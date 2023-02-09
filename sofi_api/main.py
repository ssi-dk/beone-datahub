import subprocess
from os import getenv

from pydantic import BaseModel
from fastapi import FastAPI

import samples_api
from partitioning_HC import HC

app = FastAPI()

MONGO_FIELD_MAPPING = {
    'org': 'org',
    'name': 'name',
    'species': 'sample.metadata.Microorganism',
    'sequence_type': 'sample.summary.sequence_type',
    'metadata': 'sample.metadata',  # Used to retrieve all metadata fields.
    'sampling_year': 'sample.metadata.Date_Sampling_YYYY',
    'country_term': {'$arrayElemAt': ['$sample.metadata.Country', 0]},
    'source_type_term': {'$arrayElemAt': ['$sample.metadata.Source_Type', 0]},
    'sampling_date': 'sample.metadata.Date_Sampling',
    'allele_profile': 'pipelines.chewiesnake.allele_profile',
}

samples = samples_api.API(getenv('MONGO_CONNECTION'), MONGO_FIELD_MAPPING)

class HCRequest(BaseModel):
    ids: list
    method_threshold:str = 'single'
    timeout: int = 2


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/")
async def start_job(job: HCRequest):
    
    return {
        "OK": "Thanks."
        }