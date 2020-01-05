"""
Ergast API tools. https://ergast.gom/api/
"""
from collections import namedtuple
from itertools import chain
from json import dump, load, loads
from operator import itemgetter
from pathlib import Path
from sys import stderr as STDERR
from time import sleep
from urllib.request import urlopen

BASE = "https://ergast.com/api"
LIMIT = 100
RETRIES = 2
TIMEOUT = 8


def tupled(rows, name, *cols):
    """ Iterator[namedtuple]: Rows extracted from dictionaries. """
    Row = namedtuple(name, cols, defaults=[None for _ in cols])

    return (Row(**x) for x in rows)


def unpacked(rows, *keys):
    """ Iterator[dict]: Dictionaries extracted from query replies. """
    for key in keys:
        rows = map(itemgetter(key), rows)

    return chain.from_iterable(rows)


def warn(*args, file=STDERR):
    """ None: Print error message to standard error stream. """
    print("ERROR", __name__, *args, file=file)


class ErgastAPI:
    """
    Get data from https://ergast.com/api/ politely.

    No external dependencies. Tested with Python 3.7.5.
    Init with a path-like object to choose a cache folder.
    Call to generate paged query replies with automatic retries.
    Slows down after failed requests to avoid overloading the server.

    For bigger queries, download a database image: https://ergast.com/mrd/db/

    Inputs
        folder      Path, str or None: Cache folder. Input None to disable cache.
        limit       int: Maximum results per page.
        retries     int: Maximum retries per query.
        timeout     float: Max seconds to wait for each response.

    Create an ErgastAPI which caches replies to local disk.
    >>> api = ErgastAPI('path/to/cache/folder')

    Call with query parameters to generate paged replies.
    >>> pages = [ x for x in api('f1', 1990, 6, 'pitstops') ]

    Erase cached results (if any) for a specific query.
    >>> api.erase('f1', 1990, 6, 'pitstops')

    Send pre-formatted queries. Each of these returns a list of namedtuples:
    >>> api.f1circuits
    >>> api.f1constructors
    >>> api.f1drivers
    >>> api.f1seasons
    >>> api.f1status
    """

    def __init__(self, folder=None, limit=LIMIT, retries=RETRIES, timeout=TIMEOUT):
        self.folder = Path(folder) if folder else None
        self.limit = int(limit)
        self.retries = int(retries)
        self.timeout = float(timeout)

    def __call__(self, *args):
        """ Iterator[dict]: Paginated replies. Set folder=None to disable cache. """
        return self.cached(*args) if self.folder else self.batches(*args)

    def __repr__(self):
        name = type(self).__name__
        params = ", ".join(f"{k}={v}" for k, v in vars(self).items())

        return f"{name}({params})"

    # Tables

    @property
    def f1circuits(self):
        """ List[namedtuple]: All tracks. """
        rows = self("f1", "circuits")
        keys = "MRData CircuitTable Circuits".split()
        cols = "circuitId circuitName country lat long locality url".split()
        rows = unpacked(rows, *keys)
        rows = ({**x, **x.pop("Location")} for x in rows)
        rows = tupled(rows, "Circuit", *cols)

        return list(rows)

    @property
    def f1constructors(self):
        """ List[namedtuple]: All constructors. """
        rows = self("f1", "constructors")
        keys = "MRData ConstructorTable Constructors".split()
        cols = "constructorId name nationality url".split()
        rows = unpacked(rows, *keys)
        rows = tupled(rows, "Constructor", *cols)

        return list(rows)

    @property
    def f1drivers(self):
        """ List[namedtuple]: All drivers. """
        rows = self("f1", "drivers")
        keys = "MRData DriverTable Drivers".split()
        cols = "driverId code dateOfBirth familyName givenName nationality".split()
        cols += "permanentNumber url".split()
        rows = unpacked(rows, *keys)
        rows = tupled(rows, "Driver", *cols)

        return list(rows)

    @property
    def f1seasons(self):
        """ List[namedtuple]: All seasons. """
        rows = self("f1", "seasons")
        keys = "MRData SeasonTable Seasons".split()
        cols = "season url".split()
        rows = unpacked(rows, *keys)
        rows = tupled(rows, "Season", *cols)

        return list(rows)

    @property
    def f1status(self):
        """ List[namedtuple]: Status codes for race results. """
        rows = self("f1", "status")
        keys = "MRData StatusTable Status".split()
        cols = "statusId count status".split()
        rows = unpacked(rows, *keys)
        rows = tupled(rows, "Status", *cols)

        return list(rows)

    # Manual query methods

    def batches(self, *args):
        """ Iterator[dict]: Replies with automatic pagination. """
        limit, reply = self.limit, self.reply

        offset, total = 0, 1
        while offset < total:
            page = reply(*args, offset=offset)
            total = int(page["MRData"]["total"])
            offset += limit
            yield page

    def cached(self, *args):
        """ Iterator[dict]: Cached pages. Downloads pages if none exist. """
        download, querypath = self.download, self.querypath

        folder = querypath(*args)
        if not any(folder.glob("*.json")):
            download(*args)

        for path in sorted(folder.glob("*.json")):
            with open(path) as file:
                yield load(file)

    def download(self, *args):
        """ None: Delete any old pages. Get and save new pages. """
        batches, erase, querypath = self.batches, self.erase, self.querypath

        folder = querypath(*args)
        if folder.exists():
            erase(*args)
        else:
            print(f"mkdir {folder}")
            folder.mkdir(parents=True)

        for i, data in enumerate(batches(*args)):
            path = (folder / str(i)).with_suffix(".json")
            with open(path, "w") as file:
                print(f"save {path}")
                dump(data, file, allow_nan=False, indent=2)

    def erase(self, *args):
        """ None: Delete any cached pages. """
        querypath = self.querypath

        for path in querypath(*args).glob("*.json"):
            print(f"rm {path}")
            path.unlink()

    # Helpers

    def querypath(self, *args):
        """ Path: Path to cache folder. """
        return self.folder.joinpath(*map(str, args))

    def reply(self, *args, offset=0):
        """ dict: Data extracted from query reply. """
        limit, retries, timeout = self.limit, self.retries, self.timeout

        path = "/".join(map(str, args)) + ".json"
        url = f"{BASE}/{path}?limit={limit}&offset={offset}"
        print(f"GET {url}")

        for itry in reversed(range(1 + retries)):
            try:
                with urlopen(url, timeout=timeout) as file:
                    return loads(file.read())

            except Exception as err:
                if itry:
                    warn(f"Retry in {timeout} seconds because {err}")
                    sleep(timeout)
                    timeout *= 2
                else:
                    warn(f"Gave up after {retries} retries.")
                    raise err


"""
Copyright © 2019 Sam Kennerly

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
