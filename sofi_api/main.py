import subprocess
from os import getenv
import uuid
from typing import Union

from pydantic import BaseModel
from fastapi import FastAPI
import pandas

from mongo import samples_api
from ReporTree.scripts.partitioning_HC import HC

app = FastAPI()

sapi = samples_api.API(getenv('MONGO_CONNECTION'), samples_api.FIELD_MAPPING)


class HCRequest(BaseModel):
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


def get_alleles_from_beone_mongo(mongo_cursor):
    for document in mongo_cursor:
        output = [ document['name'] ]
        for locus in document['allele_profile']:
            output.append(locus['allele_crc32'])
        yield output


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/")
async def start_job(job: HCRequest):
    job.id = uuid.uuid4()
    print(job.sample_ids)
    mongo_cursor, unmatched = sapi.get_samples_from_keys(job.sample_ids, fields={'name', 'allele_profile'})
    allele_profiles = pandas.DataFrame(mongo_cursor)
    # allele_profiles = pandas.DataFrame(get_alleles_from_beone_mongo(mongo_cursor))
    print("Allele profiles:")
    print(allele_profiles)
    hc = HC(job.id.hex[:8],
        out=job.id.hex[:8],
        allele_mx=allele_profiles,
        method_threshold=job.method_threshold,
        pct_HCmethod_threshold=job.pct_HCmethod_threshold,
        samples_called=job.samples_called,
        loci_called=job.loci_called,
        dist=job.dist
    )
    hc.run()
    return {
        "job_id": job.id
        }