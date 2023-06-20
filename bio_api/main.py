import subprocess
from os import getenv
import uuid
from typing import Union
from io import StringIO
from pathlib import Path

from pydantic import BaseModel
from fastapi import FastAPI
from pandas import DataFrame, read_table

from mongo import samples

app = FastAPI()
mongo_connection = getenv('MONGO_CONNECTION')
print(f"Mongo connection: {mongo_connection}")
sapi = samples.API(mongo_connection, samples.FIELD_MAPPING)

TMPDIR = getenv('TMPDIR', '/tmp')

class HCTreeCalcRequest(BaseModel):
    """Represents a REST request for a tree calculation based on hierarchical clustering.
    """
    id: Union[None, uuid.UUID]
    sample_ids: list
    timeout: int = 2

    # These attributes have identical counterparts on the HC class.
    # Some are out-commented as we may not need or want them in the REST API.
    out: Union[None, str]
    # distance_matrix:str = ''  -- Presumably not needed in the API
    # allele_profile:str = ''  -- Presumably not needed in the API
    # allele_mx:DataFrame = None  -- Unwanted as Pandas does not integrate easily with Pydantic
    method_threshold: str = 'single'
    pct_HCmethod_threshold: str = 'none'  # TODO should be changed to None (also in ReporTree)
    samples_called: float = 0.0
    loci_called: Union[str, float] = ''
    # metadata:str = ''  -- Unwanted as we don't deal with metadata this way in SOFI
    # filter_column:str = ''   -- Unwanted as we don't deal with metadata this way in SOFI
    dist: float = 1.0

class DistMatFromIdsRequest(BaseModel):
    """Represents a REST request for a distance matrix based on sequence id input.
    """
    id: Union[None, uuid.UUID]
    sequence_ids: list
    timeout: int = 2


def translate_beone_row(mongo_item):
    result_row = dict()
    for beone_dict in mongo_item['allele_profile']:
        key = beone_dict['locus']
        value = beone_dict['allele_crc32']
        result_row[key] = value
    return result_row

def allele_mx_from_beone_mongo(mongo_cursor):
    full_dict = dict()
    first_mongo_item = next(mongo_cursor)
    first_row = translate_beone_row(first_mongo_item)
    full_dict[first_mongo_item['name']] = first_row
    allele_names = set(first_row.keys())
    allele_count = len(allele_names)
    print(f"Number of alleles in first row: {allele_count}")
    for mongo_item in mongo_cursor:
        row = translate_beone_row(mongo_item)
        row_allele_names = set(row.keys())
        assert row_allele_names == allele_names
        full_dict[mongo_item['name']] = row
    return DataFrame.from_dict(full_dict, 'index', dtype=str)

def translate_bifrost_row(mongo_item):
    return mongo_item['allele_profile']  #[0]

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
    allele_count = len(allele_names)
    print(f"Number of alleles in first row: {allele_count}")
    for mongo_item in mongo_cursor:
        row = translate_bifrost_row(mongo_item)
        row_allele_names = set(row.keys())
        assert row_allele_names == allele_names
        full_dict[mongo_item['name']] = row
    return DataFrame.from_dict(full_dict, 'index', dtype=str)

def dist_mat_from_allele_profile(allele_mx:DataFrame):
		# save allele matrix to a file that cgmlst-dists can use for input
		allele_mx_path = Path(TMPDIR, 'allele_mx.tsv')  #TODO we need to put the job id into the path
		with open(allele_mx_path, 'w') as allele_mx_file_obj:
			allele_mx_file_obj.write("ID")  # Without an initial string in first line cgmlst-dists will fail!
			allele_mx.to_csv(allele_mx_file_obj, index = True, header=True, sep ="\t")

		# run cgmlst-dists
		cp1:subprocess.CompletedProcess = subprocess.run(
			["cgmlst-dists", str(allele_mx_path)], capture_output=True, text=True)
		if cp1.returncode != 0:
			errmsg = (f"Could not run cgmlst-dists on {str(allele_mx_path)}!")
			raise OSError(errmsg + "\n\n" + cp1.stderr)

		temp_df = read_table(StringIO(cp1.stdout), dtype=str)
		temp_df.rename(columns = {"cgmlst-dists": "ids"}, inplace = True)
		# TODO here we are saving a file, then reading it. Why?
		return temp_df

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/distance_matrix/from_ids")
async def dist_mat_from_ids(job: DistMatFromIdsRequest):
    job.id = uuid.uuid4()
    print(job.sequence_ids)
    """If this code is at some point going to be used in a context where the 'name' cannot be
    guaranteed to be unique, one way of getting around it would be to implement a namespace structure with
    dots as separators, like 'dk.ssi.samplelongname'.
    """
    mongo_keys = [ {'name': name} for name in job.sequence_ids]
    mongo_cursor, unmatched = sapi.get_samples_from_keys(mongo_keys)
    if len(unmatched) > 0:
        return {
            "job_id": job.id,
            "error": "Some Mongo keys were unmatched",
            "unmatched": unmatched
            }
    else:
        try:
            allele_mx_df: DataFrame = allele_mx_from_bifrost_mongo(mongo_cursor)
        except StopIteration as e:
            return {
            "job_id": job.id,
            "unmatched": unmatched,
            "error": e
        }
        dist_mx_df: DataFrame = dist_mat_from_allele_profile(allele_mx_df)
        return {
            "job_id": job.id,
            "distance_matrix": dist_mx_df.to_dict()
            }