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
        '-m',
        f'/mnt/rt_runs/{job_number}/metadata.tsv',
        '--analysis',
        'HC'
        ]
    workdir = f'/mnt/rt_runs/{job_number}'
    p = subprocess.Popen(command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        stdout, stderr = p.communicate(timeout=3)
        print(stderr)
        if stderr is None:
            status = 'RT_SUCCESSFUL'
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
        end_time = datetime.now()
        elapsed_time = end_time - start_time
        return {
            "job_number": job_number,
            "pid": p.pid,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "elapsed_time": elapsed_time,
            "status": status,
            "error": error
            }
