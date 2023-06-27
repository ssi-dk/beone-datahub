#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from os import getcwd

import scipy
import pandas as pd
import numpy as np
import scipy.spatial.distance as ssd
from scipy.cluster.hierarchy import linkage

"""The squareform function is copied from scipy.spatial.distance. For some reason
it did not work when the code was in the library, but copying it locally
fixed the problem!"""
def squareform(X, force="no", checks=True):
    """
    Convert a vector-form distance vector to a square-form distance
    matrix, and vice-versa.

    Parameters
    ----------
    X : array_like
        Either a condensed or redundant distance matrix.
    force : str, optional
        As with MATLAB(TM), if force is equal to ``'tovector'`` or
        ``'tomatrix'``, the input will be treated as a distance matrix or
        distance vector respectively.
    checks : bool, optional
        If set to False, no checks will be made for matrix
        symmetry nor zero diagonals. This is useful if it is known that
        ``X - X.T1`` is small and ``diag(X)`` is close to zero.
        These values are ignored any way so they do not disrupt the
        squareform transformation.

    Returns
    -------
    Y : ndarray
        If a condensed distance matrix is passed, a redundant one is
        returned, or if a redundant one is passed, a condensed distance
        matrix is returned.

    Notes
    -----
    1. ``v = squareform(X)``

       Given a square n-by-n symmetric distance matrix ``X``,
       ``v = squareform(X)`` returns a ``n * (n-1) / 2``
       (i.e. binomial coefficient n choose 2) sized vector `v`
       where :math:`v[{n \\choose 2} - {n-i \\choose 2} + (j-i-1)]`
       is the distance between distinct points ``i`` and ``j``.
       If ``X`` is non-square or asymmetric, an error is raised.

    2. ``X = squareform(v)``

       Given a ``n * (n-1) / 2`` sized vector ``v``
       for some integer ``n >= 1`` encoding distances as described,
       ``X = squareform(v)`` returns a n-by-n distance matrix ``X``.
       The ``X[i, j]`` and ``X[j, i]`` values are set to
       :math:`v[{n \\choose 2} - {n-i \\choose 2} + (j-i-1)]`
       and all diagonal elements are zero.

    In SciPy 0.19.0, ``squareform`` stopped casting all input types to
    float64, and started returning arrays of the same dtype as the input.

    """

    X = np.ascontiguousarray(X)

    s = X.shape

    if force.lower() == 'tomatrix':
        if len(s) != 1:
            raise ValueError("Forcing 'tomatrix' but input X is not a "
                             "distance vector.")
    elif force.lower() == 'tovector':
        if len(s) != 2:
            raise ValueError("Forcing 'tovector' but input X is not a "
                             "distance matrix.")

    # X = squareform(v)
    if len(s) == 1:
        if s[0] == 0:
            return np.zeros((1, 1), dtype=X.dtype)

        # Grab the closest value to the square root of the number
        # of elements times 2 to see if the number of elements
        # is indeed a binomial coefficient.
        d = int(np.ceil(np.sqrt(s[0] * 2)))

        # Check that v is of valid dimensions.
        if d * (d - 1) != s[0] * 2:
            raise ValueError('Incompatible vector size. It must be a binomial '
                             'coefficient n choose 2 for some integer n >= 2.')

        # Allocate memory for the distance matrix.
        M = np.zeros((d, d), dtype=X.dtype)

        # Since the C code does not support striding using strides.
        # The dimensions are used instead.
        X = ssd._copy_array_if_base_present(X)

        # Fill in the values of the distance matrix.
        ssd._distance_wrap.to_squareform_from_vector_wrap(M, X)

        # Return the distance matrix.
        return M
    elif len(s) == 2:
        if s[0] != s[1]:
            raise ValueError('The matrix argument must be square.')
        if checks:
            ssd.is_valid_dm(X, throw=True, name='X')

    elif len(s) == 2:
        if s[0] != s[1]:
            raise ValueError('The matrix argument must be square.')
        if checks:
            ssd.is_valid_dm(X, throw=True, name='X')

        # One-side of the dimensions is set here.
        d = s[0]

        if d <= 1:
            return np.array([], dtype=X.dtype)

        # Create a vector.
        v = np.zeros((d * (d - 1)) // 2, dtype=X.dtype)

        # Since the C code does not support striding using strides.
        # The dimensions are used instead.
        X = ssd._copy_array_if_base_present(X)

        # Convert the vector to squareform.
        ssd._distance_wrap.to_vector_from_squareform_wrap(X, v)
        return v
    else:
        raise ValueError(('The first argument must be one or two dimensional '
                          'array. A %d-dimensional array is not '
                          'permitted') % len(s))

# Convert single linkage matrix to newick format
def get_newick(node, parent_dist, leaf_names, newick='') -> str:
    """
    Convert sciply.cluster.hierarchy.to_tree()-output to Newick format.

    :param node: output of sciply.cluster.hierarchy.to_tree()
    :param parent_dist: output of sciply.cluster.hierarchy.to_tree().dist
    :param leaf_names: list of leaf names
    :param newick: leave empty, this variable is used in recursion.
    :returns: tree in Newick format
    """
    if node.is_leaf():
        return "%s:%.2f%s" % (leaf_names[node.id], parent_dist - node.dist, newick)
    else:
        if len(newick) > 0:
            newick = "):%.2f%s" % (parent_dist - node.dist, newick)
        else:
            newick = ");"
        newick = get_newick(node.get_left(), node.dist, leaf_names, newick=newick)
        newick = get_newick(node.get_right(), node.dist, leaf_names, newick=",%s" % (newick))
        newick = "(%s" % (newick)
        return newick

def make_tree(df: pd.DataFrame):
    print("Input dataframe (distance matrix) for tree:")
    print(df)

    m = df.values
    M = np.array(m)
    distArray = squareform(M)

    # Perform single linkage
    Z = linkage(distArray, 'single')

    # Get the list of leaf_names in the order they are in the distance matrix
    leaf_names = list(df.index)

    # Convert single linkage matrix to newick format
    tree = scipy.cluster.hierarchy.to_tree(Z, False)
    nwk_tree = get_newick(tree, tree.dist, leaf_names)
    return nwk_tree

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('source_folder', type=Path)
    args = parser.parse_args()

    source_folder = Path(args.source_folder)
    if not source_folder.is_absolute():
        source_folder =  Path(getcwd(), args.source_folder)
    print("Source folder:", source_folder)
    output_newick_file: Path = Path(source_folder.joinpath('single_linkage_tree.nwk'))

    # Read distance matrix file
    input_matrix_file = args.source_folder.joinpath('dist.tsv')
    df = pd.read_csv(input_matrix_file, index_col=0, sep="\t")
    nwk_tree = make_tree(df)

    # Save tree to output newick file
    with open(output_newick_file,"w") as outfile:
        print(nwk_tree, file=outfile)
    print(f"Output newick file was saved: {output_newick_file}")