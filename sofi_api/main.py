import subprocess

from pydantic import BaseModel
from fastapi import FastAPI

from partitioning_HC import HC

app = FastAPI()

DM_PATH_SALMONELLA = '/data/dm/dm_salmonella.tsv'
# DM_SALMONELLA = open(DM_PATH_SALMONELLA, 'r')

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