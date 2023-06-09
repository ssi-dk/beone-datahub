import sys
import os
import argparse
import textwrap
import pandas
from datetime import date
import logging
import subprocess
from io import StringIO
from pathlib import Path
from pandas import DataFrame

TMPDIR = os.getenv('TMPDIR', '/tmp')


def create_logger(folder: Path, out: str):
    fh = logging.FileHandler(Path(folder).joinpath(out + '.log'), mode='a')
    fh.setLevel(logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(fh)
    return logger


class HCTreeCalc:
    """
    Instantiate this class when importing partitioning_HC into another code module;
    then use the 'run' method to run the calculation.
    """
    out: str = ''
    folder: str = 'test'
    distance_matrix: str = ''
    allele_profile: str = ''
    allele_mx: DataFrame = None
    method_threshold: str = 'single'
    pct_HCmethod_threshold: str = 'none'
    samples_called: float = 0.0
    loci_called: float = ''
    metadata: str = ''
    filter_column: str = ''
    dist: float = 1.0

    def __init__(self, job_folder_name, **kwargs):
        self.folder = Path(TMPDIR).joinpath(job_folder_name)
        self.__dict__.update(kwargs)

    def allele_df_provided(self):
        return "Not provided" if self.allele_mx is None else "Provided"

    def __str__(self):
        return \
            f"Folder: {self.folder}\n" + \
            f"Output filename prefix: {self.out}\n" + \
            f"Allele profile filename: {self.allele_profile}\n" + \
            f"Allele profile dataframe: {self.allele_df_provided()}\n" + \
            f"Distance matrix filename: {self.distance_matrix}\n" + \
            f"Metadata filename: {self.metadata}\n" + \
            f"Method threshold: {self.method_threshold}\n" + \
            f"Percentage method threshold: {self.pct_HCmethod_threshold}\n" + \
            f"Samples called: {self.samples_called}\n" + \
            f"Loci called: {self.loci_called}\n" + \
            f"Filter column: {self.filter_column}\n" + \
            f"Distances: {self.dist}"

    def run(self):
        self.folder.mkdir()
        self.logger = create_logger(self.folder, self.out)
        self.logger.info(
            "Running hierarchical clustering with these parameters:")
        self.logger.info(self.__str__())
        self.logger.info("")

        if self.allele_profile:
            self.logger.info(
                "Profile matrix provided as file path; pairwise distance will be calculated.")
            self.df_dist = from_allele_profile(self, self.logger)
        elif self.allele_mx is not None:
            self.logger.info(
                "Profile matrix provided as DataFrame; pairwise distance will be calculated.")
            self.df_dist = from_allele_profile(
                self, self.logger, allele_mx=self.allele_mx)
        elif self.distance_matrix:
            self.logger.info(
                "Distance matrix provided; pairwise distance will NOT be calculated.")
            self.df_dist = from_distance_matrix(self, self.logger)
        else:
            msg = "Either distance matrix or allele profile must be specified!"
            self.logger.error(msg)
            raise ValueError(msg)


def get_newick(node, parent_dist, leaf_names, newick='') -> str:
    """
    This function was retrieved from: https://stackoverflow.com/questions/28222179/save-dendrogram-to-newick-format
    We thank STACKOVERFLOW and @MrTomRod and @jfn

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
        newick = get_newick(node.get_left(), node.dist,
                            leaf_names, newick=newick)
        newick = get_newick(node.get_right(), node.dist,
                            leaf_names, newick=",%s" % (newick))
        newick = "(%s" % (newick)

        return newick


def from_allele_profile(hc=None, logger=None, allele_mx: DataFrame = None):
    global args
    if hc:
        args = hc
    if allele_mx is None:
        allele_mx = pandas.read_table(args.allele_profile, dtype=str)
    # implemented because of chewie-ns profiles
    allele_mx = allele_mx.replace("INF-", "", regex=True)
    # implemented because of chewie-ns profiles
    allele_mx = allele_mx.replace("\*", "", regex=True)
    allele_mx = allele_mx.replace(
        {"N": "0", "a": "A", "c": "C", "t": "T", "g": "G"})

    # filtering allele matrix	----------

    if args.metadata and args.filter_column:
        logger.info("Filtering the distance matrix...")

        filters = args.filter_column
        mx = pandas.read_table(args.metadata, dtype=str)
        sample_column = mx.columns[0]
        initial_samples = len(allele_mx[allele_mx.columns[0]].values.tolist())
        final_samples = len(allele_mx[allele_mx.columns[0]].values.tolist())
        logger.info("\tFrom the " + str(initial_samples) + " samples, " +
                    str(final_samples) + " were kept in the matrix...")
        allele_mx.to_csv(Path(args.folder).joinpath(
            args.out + "_subset_matrix.tsv"), sep="\t", index=None)

    # cleaning allele matrix (columns)	----------

    if args.samples_called and float(args.samples_called) != 1.0 and float(args.samples_called) != 0.0:
        logger.info("Keeping only sites/loci with information in >= " +
                    str(float(args.samples_called) * 100) + "% of the samples...")

        pos_t0 = len(allele_mx.columns[1:])
        for col in allele_mx.columns[1:]:
            values = allele_mx[col].values.tolist()
            if (len(values)-values.count("0"))/len(values) < float(args.samples_called):
                allele_mx = allele_mx.drop(columns=col)
        allele_mx.to_csv(Path(args.folder).joinpath(
            args.out + "_flt_matrix.tsv"), index=False, header=True, sep="\t")
        pos_t1 = len(allele_mx.columns[1:])
        logger.info("\tFrom the " + str(pos_t0) + " loci/positions, " +
                    str(pos_t1) + " were kept in the matrix.")

    # cleaning allele matrix (rows)	----------

    if args.loci_called:
        logger.info("Cleaning the profile matrix using a threshold of >" +
                    str(args.loci_called) + " alleles/positions called per sample...")

        report_allele_mx = {}

        len_schema = len(allele_mx.columns) - 1

        report_allele_mx["samples"] = allele_mx[allele_mx.columns[0]]
        report_allele_mx["missing"] = allele_mx.isin(["0"]).sum(axis=1)
        report_allele_mx["called"] = len_schema - \
            allele_mx.isin(["0"]).sum(axis=1)
        report_allele_mx["pct_called"] = (
            len_schema - allele_mx.isin(["0"]).sum(axis=1)) / len_schema

        report_allele_df = pandas.DataFrame(data=report_allele_mx)
        if float(args.loci_called) != 1.0:
            flt_report = report_allele_df[report_allele_df["pct_called"] > float(
                args.loci_called)]
        else:
            flt_report = report_allele_df[report_allele_df["pct_called"] == float(
                args.loci_called)]
        pass_samples = flt_report["samples"].values.tolist()

        if len(pass_samples) == 0:
            logger.info("Cannot proceed because " + str(len(pass_samples)
                                                        ) + " samples were kept in the matrix!")
            sys.exit()

        logger.info("\tFrom the " + str(len(allele_mx[allele_mx.columns[0]].values.tolist(
        ))) + " samples, " + str(len(pass_samples)) + " were kept in the profile matrix.")

        allele_mx = allele_mx[allele_mx[allele_mx.columns[0]].isin(
            pass_samples)]
        allele_mx.to_csv(Path(args.folder).joinpath(
            args.out + "_flt_matrix.tsv"), index=False, header=True, sep="\t")
        report_allele_df.to_csv(Path(args.folder).joinpath(
            args.out + "_loci_report.tsv"), index=False, header=True, sep="\t")

    # getting distance matrix	----------

    logger.info("Getting the pairwise distance matrix with cgmlst-dists...")

    # save allele matrix to a file that cgmlst-dists can use for input
    allele_mx_path = Path(TMPDIR, hc.out, hc.out + '_allele_mx.tsv')
    with open(allele_mx_path, 'w') as allele_mx_file_obj:
        # Without an initial string cgmlst-dists will fail!
        allele_mx_file_obj.write("ID")
        allele_mx.to_csv(allele_mx_file_obj, index=True, header=True, sep="\t")

    # run cgmlst-dists
    cp1: subprocess.CompletedProcess = subprocess.run(
        ["cgmlst-dists", str(allele_mx_path)], capture_output=True, text=True)
    if cp1.returncode != 0:
        errmsg = (f"Could not run cgmlst-dists on {str(allele_mx_path)}!")
        logger.error(errmsg)
        logger.error(cp1.stderr)
        raise OSError(errmsg + "\n\n" + cp1.stderr)

    temp_df = pandas.read_table(StringIO(cp1.stdout), dtype=str)
    temp_df.rename(columns={"cgmlst-dists": "dists"}, inplace=True)
    # TODO here we are saving a file, then reading it. Why?
    temp_df.to_csv(Path(args.folder).joinpath(
        args.out + "_dist.tsv"), sep="\t", index=None)
    dist = pandas.read_table(
        Path(args.folder).joinpath(args.out + "_dist.tsv"))
    return dist


def from_distance_matrix(hc=None, logger=None):
    global args
    if hc:
        args = hc
    dist = pandas.read_table(args.distance_matrix)

    # filtering the pairwise distance matrix	----------

    if args.metadata and args.filter_column:
        logger.info("Filtering the distance matrix...")

        filters = args.filter_column
        mx = pandas.read_table(args.metadata, dtype=str)
        sample_column = mx.columns[0]
        dist.to_csv(args.folder + "_flt_dist.tsv", sep="\t", index=None)

    elif args.metadata and args.filter_column == "":
        logger.info(
            "Metadata file was provided but no filter was found... I am confused :-(")
        sys.exit()

    elif (not args.metadata) and args.filter_column:
        logger.info(
            "Metadata file was not provided but a filter was found... I am confused :-(")
        sys.exit()

    else:
        sample_column = "sequence"

    return dist