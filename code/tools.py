"""
Constants and utility functions.
"""
from pathlib import Path

from numpy import random
from pandas import DataFrame, Series

from ergast_api import ErgastAPI
from ergast_zip import ErgastZIP
from graph import Graph
from plot import Plot


REPO = Path(__file__).resolve().parent.parent
DATADIR = REPO / "data"
ERGAST_API = DATADIR / "cache"
ERGAST_ZIP = DATADIR / "ergast/f1.zip"
TABLEDIR = DATADIR / "tables"
PLOTDIR = DATADIR / "plots"


def afew(data, n=5):
    """ DataFrame view: Select random rows from input DataFrame. """
    return data.loc[random.choice(data.index, n)]


def savehtml(data, name, **kwargs):
    """ None: Save DataFrame to HTML file. """
    path = TABLEDIR / f"{name}.html"
    print("Save", path)
    data.to_html(path, **kwargs)


def savepng(axes, name, **kwargs):
    """ None: Save plot to PNG file. """
    path = PLOTDIR / f"{name}.png"
    print("Save", path)
    axes.figure.savefig(path, **kwargs)

# Copyright © 2020 Sam Kennerly
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
