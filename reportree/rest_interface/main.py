import subprocess
from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()

class Job(BaseModel):
    job_number: int
    timeout: int = 2
    columns_summary_report: list

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/")
async def start_job(job: Job):
    command = [
        'python', '/app/ReporTree/reportree.py',
        '-a', f'/mnt/rt_runs/{job.job_number}/allele_profiles.tsv',
        '-m', f'/mnt/rt_runs/{job.job_number}/metadata.tsv',
        '--output', f'/mnt/rt_runs/{job.job_number}/ReporTree',
        '--analysis', 'grapetree',
        #'--columns_summary_report', ','.join(job.columns_summary_report),
        #'--metadata2report', ','.join(job.columns_summary_report),
        '-thr 4,7,14',
        #'--frequency-matrix', ','.join(job.columns_summary_report),
        '--matrix-4-grapetree',
        '--mx-transpose'
        ]
    
    print("ReporTree command:")
    print(' '.join(command))
    workdir = f'/mnt/rt_runs/{job.job_number}'
    p = subprocess.Popen(command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        stdout, stderr = p.communicate(timeout=job.timeout)
        print(stderr)
        if stderr is None:
            status = 'SUCCESS'
            error = None
        else:
            status = 'RT_ERROR'
            error = stderr
    except subprocess.TimeoutExpired as e:
        status = "RUNNING"
        error = e
    except OSError as e:
        status = "OS_ERROR"
        error = e
    finally:
        return {
            "job_number": job.job_number,
            "pid": p.pid,
            "status": status,
            "error": error
            }
