import subprocess
from datetime import datetime

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/{job_number}")
async def start_job(job_number: int):
    start_time = datetime.now()
    command = [
        'python',
        '/app/ReporTree/reportree.py',
        '-a',
        f'/mnt/rt_runs/{job_number}/allele_profiles.tsv',
        '--analysis',
        'HC'
        ]
    workdir = f'/mnt/rt_runs/{job_number}'
    p = subprocess.Popen(command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        output, error = p.communicate(timeout=3)
        job_status = "finished"
    except subprocess.TimeoutExpired as e:
        output = None
        error = e
        job_status = "deferred"
    finally:
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        return {
            "job_number": job_number,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "elapsed_time": elapsed_time,
            "output": output,
            "err": error,
            "job_status": job_status
            }
