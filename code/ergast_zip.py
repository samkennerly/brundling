"""
Ergast database image readers. https://ergast.com/mrd/db/
"""
from pathlib import Path
from zipfile import ZipFile

from pandas import read_csv, to_timedelta


def to_seconds(s):
    """ Series[float64]: Converted Series of minute:seconds.fraction strings. """
    s = s.str.partition(":")

    return 60 * s[0].astype(float) + s[2].astype(float)


class ErgastZIP:
    """
    Read Formula 1 data from an https://ergast.com/mrd/db database dump.

    Returns pandas.Series or pandas.DataFrame objects.
    Reads CSV files inside a ZIP file. Does not save or modify files.
    Converts to pandas-friendly datatypes. Renames or drops some columns.

    Inputs
        path    Path or str: Path to ZIP file containing CSVs.

    Create an ErgastF1 which reads from a specific ZIP file.
    >>> tables = ErgastF1('path/to/ergast/data.zip')

    DataFrames are available as read-only attributes.
    >>> tables.circuits
    >>> tables.drivers

    For smaller queries, use the Ergast API: https://ergast.com/mrd
    """

    def __init__(self, path):
        self.path = Path(path).resolve()

    def __repr__(self):
        name = type(self).__name__
        params = ", ".join(f"{k}={v}" for k, v in vars(self).items())

        return f"{name}({params})"

    def get(self, name, **kwargs):
        """ DataFrame: Read CSV file inside ZIP file. """
        path = self.path
        kwargs.setdefault("header", None)
        kwargs.setdefault("index_col", "id")
        kwargs.setdefault("na_values", ["\\N"])
        name = Path(name).with_suffix(".csv").name

        with ZipFile(path) as zed:
            with zed.open(name) as file:
                data = read_csv(file, **kwargs)

        return data.rename_axis(None)

    @property
    def tables(self):
        """ List[str]: Table names. """
        path = self.path
        with ZipFile(path) as zf:
            return zf.namelist()

    # Series

    @property
    def seasons(self):
        get, kw = self.get, {}
        kw["index_col"] = None
        kw["names"] = "year url".split()

        return get("seasons.csv", **kw).pop("year")

    @property
    def status(self):
        get, kw = self.get, {}
        kw["names"] = "id status".split()

        return get("status.csv", **kw).pop("status")

    # DataFrames

    @property
    def circuits(self):
        get, kw = self.get, {}
        kw["names"] = "id ref circuit city country latitude longitude alt url".split()
        kw["usecols"] = set(kw["names"]) - {"alt"}
        data = get("circuits.csv", **kw)

        return data.sort_index(axis=1)

    @property
    def drivers(self):
        get, kw = self.get, {}
        kw["names"] = "id ref number code first last birthday nation url".split()
        kw["parse_dates"] = ["birthday"]
        data = get("driver.csv", **kw)
        data["number"] = data["number"].fillna(0).astype(int)
        data["driver"] = data.pop("first").str.cat(data.pop("last"), sep=" ")

        return data.sort_index(axis=1)

    @property
    def driver_standings(self):
        get, kw = self.get, {}
        kw["names"] = "id id_race id_driver points pos pos_str wins".split()
        kw["usecols"] = set(kw["names"]) - {"pos_str"}
        data = get("driver_standings.csv", **kw)

        return data.sort_index(axis=1)

    @property
    def lap_times(self):
        get, kw = self.get, {}
        kw["index_col"] = None
        kw["names"] = "id_race id_driver lap pos time msec".split()
        kw["usecols"] = set(kw["names"]) - {"time"}
        data = get("lap_times.csv", **kw)
        data["seconds"] = data.pop("msec") / 1000

        return data.sort_index(axis=1)

    @property
    def pit_stops(self):
        get, kw = self.get, {}
        kw["index_col"] = None
        kw["names"] = "id_race id_driver stop lap time duration_str duration".split()
        kw["usecols"] = set(kw["names"]) - {"duration_str"}
        data = get("pit_stops.csv", **kw)
        data["duration"] /= 1000
        data["time"] = to_timedelta(data.pop("time"))

        return data.sort_index(axis=1)

    @property
    def qualifying(self):
        get, kw, qcols = self.get, {}, "q1 q2 q3".split()
        kw["names"] = "id id_race id_driver id_team number pos q1 q2 q3".split()
        data = get("qualifying.csv", **kw)
        for col in qcols:
            data[col] = to_seconds(data[col])

        return data.sort_index(axis=1)

    @property
    def races(self):
        get, kw = self.get, {}
        kw["names"] = "id season round id_circuit race date time url".split()
        kw["parse_dates"] = ["date", "time"]
        data = get("races.csv", **kw)
        data["time"] -= data["time"].dt.normalize()

        return data.sort_index(axis=1)

    @property
    def results(self):
        get, kw = self.get, {}
        kw["names"] = "id id_race id_driver id_team number grid pos pos_text".split()
        kw["names"] += "order points laps time msec fastlap rank".split()
        kw["names"] += "fastlap_sec fastlap_kph id_status".split()
        kw["usecols"] = set(kw["names"]) - {"pos_text", "time"}
        data = get("results.csv", **kw)

        data["sec"] = data.pop("msec") / 1000
        data["fastlap_sec"] = to_seconds(data["fastlap_sec"])
        for col in "number fastlap rank pos".split():
            data[col] = data[col].fillna(0).astype(int)

        return data.sort_index(axis=1)

    @property
    def teams(self):
        get, kw = self.get, {}
        kw["names"] = "id ref team nation url".split()
        data = get("constructors.csv", **kw)

        return data.sort_index(axis=1)

    @property
    def team_results(self):
        get, kw = self.get, {}
        kw["names"] = "id id_race id_team points status".split()
        data = get("constructor_results.csv", **kw)
        data["dsq"] = data.pop("status") == "D"

        return data.sort_index(axis=1)

    @property
    def team_standings(self):
        get, kw = self.get, {}
        kw["names"] = "id id_race id_team points pos pos_str wins".split()
        kw["usecols"] = set(kw["names"]) - {"pos_str"}
        data = get("constructor_standings.csv", **kw)

        return data.sort_index(axis=1)


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
