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
        '--analysis',
        'HC'
        ]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = p.communicate()
    print('Subprocess error: ' + str(err))
    print('Subprocess stdout: ' + str(out.decode()))   

    return {
        "job: number": job_number,
        "err": err
        }
