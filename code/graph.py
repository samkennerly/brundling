from numpy import fromiter, linspace, tanh
from numpy.random import randn
from pandas import Categorical, DataFrame
from scipy.sparse import coo_matrix, diags, identity
from scipy.sparse.csgraph import laplacian


def limited(z, maxr):
    """ ndarray: Array with magnitudes smoothly compressed to <= 1. """
    rad = abs(z).clip(1e-9, None)
    rad = tanh(rad) / rad
    rad *= maxr

    return rad * z


def weighted(links):
    """ DataFrame: [source, target, weight] for each link. """
    links = DataFrame(links)

    cols = list(links.columns)
    links = links.groupby(cols[0:2], observed=True)
    links = links[cols[2]].sum() if (len(cols) > 2) else links.size().rename("_")
    links = links.loc[links.ne(0)].reset_index()
    links.columns = "source target weight".split()

    nodes = sorted(set(links["source"].unique()) | set(links["target"].unique()))
    for col in "source target".split():
        links[col] = Categorical(links[col], categories=nodes)

    return links


class Graph:
    """
    Force-directed graph layout based on Gephi's ForceAtlas2 model.

    Accepts any valid pandas.DataFrame() input with 2 or 3 columns.
    Stores graph links as DataFrame with 3 columns: source, target, weight.
    'source' and 'target' are (node, node) pairs as Categorical variables.
    'weight' sums link weights if they exist; else it counts duplicated links.
    """

    def __init__(self, graph):
        self.links = graph.links if isinstance(graph, type(self)) else weighted(graph)

    def __call__(self, nsteps, x=(), y=()):
        matrix, nodes = self.matrix, self.nodes

        dtype = "complex128"
        nrows = len(nodes)
        points = (x or randn(nrows)).astype(dtype)
        points += (y or 1j * randn(nrows)).astype(dtype)

        yield points.real.copy(), points.imag.copy()

        matrix -= diags(matrix.diagonal())
        matrix *= nrows / matrix.sum()
        matrix = laplacian(matrix, use_out_degree=True)
        matrix += identity(nrows, dtype=matrix.dtype, format=matrix.format)

        for speed in linspace(1, 0.1, nsteps - 1):
            forces = (z - points for z in points)
            forces = (z / (z * z.conj()).real.clip(1e-9, None) for z in forces)
            forces = fromiter((z.mean() for z in forces), count=nrows, dtype=dtype)
            forces -= matrix.dot(points)
            points += limited(forces, speed)

            yield points.real.copy(), points.imag.copy()

    def __iter__(self):
        return self.links.itertuples(index=False, name="Link")

    def __len__(self):
        return len(self.links)

    def __repr__(self):
        return f"{type(self).__name__} with {len(self)} links\n{self.links}"

    def frame(self, steps=120):
        """ DataFrame: [node|x,y] after n steps of evolution. """
        nodes = self.nodes
        for x, y in self(steps):
            pass

        return DataFrame({"x": x, "y": y}, index=nodes)

    @property
    def matrix(self):
        """ scipy.sparse.coo: Links as a sparse matrix. """
        links, nodes = self.links, self.nodes

        i = links["source"].cat.codes.values
        j = links["target"].cat.codes.values
        k = links["weight"].values
        n = len(nodes)

        return coo_matrix((k, (i, j)), shape=(n, n)).tocsr()

    @property
    def nodes(self):
        """ Index: Sorted union of sources and targets. """
        return self.links["source"].cat.categories
