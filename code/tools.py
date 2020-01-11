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
