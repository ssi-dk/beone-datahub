import subprocess

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/{job_number}")
async def start_job(job_number: int):
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
            "job_number": job_number,
            "pid": p.pid,
            "status": status,
            "error": error
            }
