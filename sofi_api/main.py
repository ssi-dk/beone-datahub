import subprocess
from os import getenv

from pydantic import BaseModel
from fastapi import FastAPI
import pandas

from mongo import samples_api
from ReporTree.scripts.partitioning_HC import HC

app = FastAPI()

sapi = samples_api.API(getenv('MONGO_CONNECTION'), samples_api.FIELD_MAPPING)


class HCRequest(BaseModel):
    ids: list
    timeout: int = 2

    # These attributes have identical counterparts on the HC class.
    # Some are out-commented as we may not need or want them in the REST API.
    out:str = None
    # distance_matrix:str = ''  -- Presumably not needed in the API
    # allele_profile:str = ''  -- Presumably not needed in the API
    # allele_mx:DataFrame = None  -- Unwanted as Pandas does not integrate easily with Pydantic
    method_threshold:str = 'single'
    pct_HCmethod_threshold: str = 'none'  # TODO should be changed to None (also in ReporTree)
    samples_called:float = 0.0
    loci_called:float = ''
    # metadata:str = ''  -- Unwanted as we don't deal with metadata this way in SOFI
    # filter_column:str = ''   -- Unwanted as we don't deal with metadata this way in SOFI
    dist:float = 1.0


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/")
async def start_job(job: HCRequest):
    print(job.ids)
    mongo_cursor, unmatched = sapi.get_samples_from_keys(job.ids, fields={'name', 'allele_profile'})
    
    # for s in mongo_cursor:
    #     print(s['name'])
    #     print(s['allele_profile'][:10])

    allele_profiles = pandas.DataFrame(mongo_cursor)
    print(allele_profiles)

    return {
        "OK": "Thanks."
        }