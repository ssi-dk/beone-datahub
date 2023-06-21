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

def make_tree(df: pd.DataFrame):
    m = df.values
    M = np.array(m)
    distArray = ssd.squareform(M)

    # Get the list of leaf_names in the order they are in the distance matrix
    leaf_names = list(df.index)

    # Perform single linkage
    Z = linkage(distArray, 'single')

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

    # Convert single linkage matrix to newick format
    tree = scipy.cluster.hierarchy.to_tree(Z, False)
    nwk_tree = get_newick(tree, tree.dist, leaf_names)

    # Create destination folder
    destination_folder.mkdir()
    print(f"Created folder {destination_folder}")

    # Save tree to output newick file
    with open(output_newick_file,"w") as outfile:
        print(nwk_tree, file=outfile)
    print(f"Output newick file was saved: {output_newick_file}")

parser = argparse.ArgumentParser()
parser.add_argument('source_folder', type=Path)
parser.add_argument('destination_root', type=Path)
args = parser.parse_args()

source_folder = Path(args.source_folder)
if not source_folder.is_absolute():
    source_folder =  Path(getcwd(), args.source_folder)
print("Source folder:", source_folder)
destination_root = Path(args.destination_root)
if not destination_root.is_absolute():
    destination_root = Path(getcwd(), args.destination_root)
print("Destination root:", destination_root)
destination_folder: Path = destination_root.joinpath(source_folder.parts[-1])
print("Destination folder:", destination_folder)
if destination_folder.exists():
    sys.exit(f"Error: Destination folder {destination_folder} already exists. Nothing was done")
output_newick_file: Path = Path(destination_folder.joinpath('single_linkage_tree.nwk'))

# Read distance matrix file
input_matrix_file = args.source_folder.joinpath('dist.tsv')
df = pd.read_csv(input_matrix_file, index_col=0, sep="\t")
make_tree(df)