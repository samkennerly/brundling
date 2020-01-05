"""
Data visualization toolbox.
"""
from matplotlib import style as mpstyle
from matplotlib.pyplot import figure
from pandas import DataFrame

AXES = (("frame_on", False),)
FIGURE = (
    ("clear", True),
    ("dpi", 100),
    ("edgecolor", None),
    ("facecolor", None),
    ("figsize", (9, 5)),
    ("frameon", False),
    ("tight_layout", True),
)
LEGEND = (
    ("bbox_to_anchor", (1.05, 1)),
    ("borderaxespad", 0.0),
    ("loc", "upper left"),
)


class Plot:
    """
    Plot maker for pandas.DataFrame or .Series inputs.
    """

    styles = mpstyle.available

    def __init__(self, style="bmh", **kwargs):
        mpstyle.use(style)

        self.params = dict()
        self.params["axes"] = {k: kwargs.pop(k, v) for k, v in AXES}
        self.params["figure"] = {k: kwargs.pop(k, v) for k, v in FIGURE}
        self.params["legend"] = {k: kwargs.pop(k, v) for k, v in LEGEND}

    def __call__(self, data, **kwargs):
        axes, params = self.axes, self.params

        kwargs.setdefault("grid", False)
        kwargs.setdefault("legend", False)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)

        data = DataFrame(data)
        axes = kwargs.pop("ax", None) or axes()
        axes = data.plot(ax=axes, **kwargs)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        if kwargs.get("legend"):
            axes.legend(**params["legend"])

        return axes

    def __repr__(self):
        return f"{type(self).__name__}({self.params})"

    def axes(self):
        return figure(**self.params["figure"]).add_subplot(**self.params["axes"])

    # DataFrame input

    def area(self, data, **kwargs):
        """ AxesSubplot: Area plot for each column. """
        raise NotImplementedError

    def bar(self, data, **kwargs):
        """ AxesSubplot: Bar plot for each column. """
        kwargs.setdefault("legend", True)
        kwargs.setdefault("rot", 90)
        kwargs.setdefault("stacked", True)
        kwargs.setdefault("width", 0.9)

        return self(data, kind="bar", **kwargs)

    def barh(self, data, **kwargs):
        """ AxesSubplot: Horizontal bar plot for each column. """
        kwargs.setdefault("legend", True)
        kwargs.setdefault("stacked", True)
        kwargs.setdefault("width", 0.8)

        return self(data.iloc[::-1, :], kind="barh", **kwargs)

    def box(self, data, **kwargs):
        """ AxesSubplot: Box plot for each column. """
        kwargs.setdefault("grid", True)
        kwargs.setdefault("rot", 90)

        return self(data, kind="box", **kwargs)

    def boxh(self, data, **kwargs):
        """ AxesSubplot: Horizontal box plot for each column. """
        kwargs.setdefault("grid", True)

        return self(data.iloc[:, ::-1], kind="box", vert=False, **kwargs)

    def density(self, data, **kwargs):
        """ AxesSubplot: Probability density estimate for each column. """
        kwargs.setdefault("grid", True)
        kwargs.setdefault("legend", True)

        return self(data, kind="density", **kwargs)

    def heat(self, data, **kwargs):
        """ AxesSubplot: Heatmap with same rows and columns as input. """
        axes = self.axes

        kwargs.setdefault("alpha", 0.707)
        kwargs.setdefault("cmap", "inferno")
        kwargs.setdefault("edgecolor", None)
        kwargs.setdefault("shading", "flat")

        axes = kwargs.pop("ax", None) or axes()
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        colorbar = kwargs.pop("colorbar", False)
        rotation = kwargs.pop("rot", 45)

        data = DataFrame(data).iloc[::-1, :]
        cols = data.columns
        rows = data.index
        axes.set_title(title)
        axes.set_xlabel(xlabel)
        axes.set_ylabel(ylabel)
        axes.set_xticks(range(len(cols)))
        axes.set_yticks(range(len(rows)))
        axes.set_xticklabels(cols, ha="left", rotation=rotation)
        axes.set_yticklabels(rows, verticalalignment="bottom")
        axes.tick_params(labeltop=True, labelbottom=False, length=0)
        plot = axes.pcolormesh(data, **kwargs)
        if colorbar:
            axes.figure.colorbar(plot)

        return axes

    def hexbin(self, data, **kwargs):
        """ AxesSubplot: Scatterplot with hexagonal bins. """
        kwargs.setdefault("cmap", "cubehelix")
        kwargs.setdefault("colorbar", False)

        raise NotImplementedError

    def hist(self, data, **kwargs):
        """ AxesSubplot: Histogram for each column. """
        kwargs.setdefault("bins", 33)
        kwargs.setdefault("grid", True)
        kwargs.setdefault("legend", True)
        kwargs.setdefault("stacked", True)

        return self(data, kind="hist", **kwargs)

    def line(self, data, **kwargs):
        """ AxesSubplot: Line plot for each column. """
        kwargs.setdefault("grid", True)
        kwargs.setdefault("legend", True)

        return self(data, kind="line", **kwargs)

    def scatter(self, data, **kwargs):
        """
        AxesSubplot: Scatterplot with first 2 columns as (x,y) pairs.
        If 3rd column exists, then its values are point colors.
        If 4th column exists, then its values are point sizes.
        """
        data = DataFrame(data)
        cols = data.columns
        kwargs.setdefault("alpha", 0.707)
        kwargs.setdefault("cmap", "nipy_spectral_r")
        kwargs.setdefault("colorbar", False)
        kwargs.setdefault("grid", True)
        kwargs.setdefault("legend", False)
        kwargs.setdefault("x", cols[0])
        kwargs.setdefault("y", cols[1])
        if len(cols) > 2:
            kwargs.setdefault("c", data[cols[2]])
        if len(cols) > 3:
            kwargs.setdefault("s", data[cols[3]])

        return self(data, kind="scatter", **kwargs)

    # Timeseries input

    def quant(self, ts, freq, q=(), **kwargs):
        """ AxesSubplot: Contour plot of quantiles per period. """
        kwargs.setdefault("color", list("krygbck"))
        kwargs.setdefault("grid", True)
        kwargs.setdefault("legend", True)
        kwargs.setdefault("stacked", False)

        q = list(q) or [0, 0.05, 0.25, 0.50, 0.75, 0.95, 1]
        data = ts.resample(freq).quantile(q).unstack()
        data.columns = [f"{int(100 * x)} percentile" for x in data.columns]

        return self(data, kind="line", **kwargs)
