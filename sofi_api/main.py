import subprocess
from os import getenv

from pydantic import BaseModel
from fastapi import FastAPI

from mongo import samples_api
from partitioning_HC import HC

app = FastAPI()

sapi = samples_api.API(getenv('MONGO_CONNECTION'), samples_api.FIELD_MAPPING)


class HCRequest(BaseModel):
    ids: list
    method_threshold:str = 'single'
    timeout: int = 2


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/")
async def start_job(job: HCRequest):

    mongo_cursor, unmatched = sapi.get_samples_from_keys(job.ids)

    for s in mongo_cursor:
        print(s)
    
    return {
        "OK": "Thanks."
        }