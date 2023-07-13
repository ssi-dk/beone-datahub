import subprocess
from os import getenv
import uuid
from typing import Union
from io import StringIO
from pathlib import Path
import traceback

from pydantic import BaseModel
from fastapi import FastAPI
from pandas import DataFrame, read_table

from persistence import mongo
from tree_maker import make_tree

app = FastAPI()
mongo_connection = getenv('MONGO_CONNECTION')
mongo_api = mongo.MongoAPI(mongo_connection, mongo.SEQUENCE_FIELD_MAPPING)

TMPDIR = getenv('TMPDIR', '/tmp')


class ProcessingRequest(BaseModel):
    id: Union[None, uuid.UUID]
    timeout: int = 2

    def __init__(self, **kwargs):
        super().__init__( **kwargs)
        self.id = uuid.uuid4()

class DistanceMatrixRequest(ProcessingRequest):
     sequence_ids: list


class HCTreeCalcRequest(ProcessingRequest):
    """Represents a REST request for a tree calculation based on hierarchical clustering.
    """
    distances: dict
    method: str


def translate_bifrost_row(mongo_item):
    return mongo_item['categories']['cgmlst']['report']['data']['alleles']  #[0]

def allele_mx_from_bifrost_mongo(mongo_cursor):
    # Generate an allele matrix with all the allele profiles from the mongo cursor.
    full_dict = dict()
    try:
        first_mongo_item = next(mongo_cursor)
    except StopIteration:
        raise
    first_row = translate_bifrost_row(first_mongo_item)
    full_dict[first_mongo_item['name']] = first_row
    allele_names = set(first_row.keys())
    for mongo_item in mongo_cursor:
        row = translate_bifrost_row(mongo_item)
        row_allele_names = set(row.keys())
        assert row_allele_names == allele_names
        full_dict[mongo_item['name']] = row
    return DataFrame.from_dict(full_dict, 'index', dtype=str)

def dist_mat_from_allele_profile(allele_mx:DataFrame, job_id: uuid.UUID):
    # save allele matrix to a file that cgmlst-dists can use for input
    allele_mx_path = Path(TMPDIR, f'allele_matrix_{job_id.hex}.tsv')
    with open(allele_mx_path, 'w') as allele_mx_file_obj:
        allele_mx_file_obj.write("ID")  # Without an initial string in first line cgmlst-dists will fail!
        allele_mx.to_csv(allele_mx_file_obj, index = True, header=True, sep ="\t")

    # run cgmlst-dists
    cp:subprocess.CompletedProcess = subprocess.run(
        ["cgmlst-dists", str(allele_mx_path)], capture_output=True, text=True)
    if cp.returncode != 0:
        errmsg = (f"Could not run cgmlst-dists on {str(allele_mx_path)}!")
        raise OSError(errmsg + "\n\n" + cp.stderr)

    df = read_table(StringIO(cp.stdout))
    df.rename(columns = {"cgmlst-dists": "ids"}, inplace = True)
    df = df.set_index('ids')
    print("df from cgmlst-dists:")
    print(df)
    return df

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/distance_matrix/from_ids")
def dist_mat_from_ids(rq: DistanceMatrixRequest):
    """If this code is at some point going to be used in a context where the sample 'name' cannot be
    guaranteed to be unique, one way of getting around it would be to implement a namespace structure with
    dots as separators, like <sample_name>.ssi.dk
    """
    print("Requesting distance matrix with these ids:")
    print(rq.sequence_ids)
    try:
        mongo_cursor = mongo_api.get_sequences(rq.sequence_ids)
    except mongo.MongoAPIError as e:
        return {
        "job_id": rq.id,
        "error": str(e)
        }
    try:
        allele_mx_df: DataFrame = allele_mx_from_bifrost_mongo(mongo_cursor)
    except StopIteration as e:
        return {
        "job_id": rq.id,
        "error": e
        }
    dist_mx_df: DataFrame = dist_mat_from_allele_profile(allele_mx_df, rq.id)
    return {
        "job_id": rq.id,
        "distance_matrix": dist_mx_df.to_dict(orient='tight')
        }

@app.post("/tree/hc/")
def hc_tree(rq: HCTreeCalcRequest):
    response = {"job_id": rq.id, "method": rq.method}
    try:
        dist_df: DataFrame = DataFrame.from_dict(rq.distances, orient='index')
        tree = make_tree(dist_df, rq.method)
        response['tree'] = tree
    except ValueError as e:
        response['error'] = str(e)
        print(traceback.format_exc())
    return response