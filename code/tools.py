"""
Constants and utility functions.
"""
from pathlib import Path

from pandas import DataFrame, Series

from ergast_api import ErgastAPI
from ergast_zip import ErgastZIP
from graph import Graph
from plot import Plot


REPO = Path(__file__).resolve().parent.parent
DATADIR = REPO / "data"
ERGAST_API = DATADIR / "ergast/api"
ERGAST_ZIP = DATADIR / "ergast/f1.zip"
TABLEDIR = DATADIR / "tables"
PLOTDIR = DATADIR / "plots"


def afew(data, n=5):
    """ DataFrame: Print DataFrame metadata and return a few rows. """
    schema = DataFrame({"dtype": data.dtypes, "nulls": data.isnull().sum()})
    print(f"[{len(data)} rows x {len(schema)} columns]", schema, sep="\n")

    return data.tail(n)

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
