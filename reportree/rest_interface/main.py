import subprocess
from typing import Union
from argparse import ArgumentParser

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

def run_subprocess(job_number, timeout=5):
    # Original command from
    # https://github.com/insapathogenomics/ReporTree/wiki/4.-Examples#outbreak-detection---bacterial-foodborne-pathogen-eg-listeria-monocytogenes
    """
    command = ['python', 'reportree.py',
        '-m', 'Listeria_input_metadata.tsv',
        '-a', 'Listeria_input_alleles.tsv',
        '--columns_summary_report', 'n_sample,source,n_country,country,n_region,region,first_seq_date,last_seq_date,timespan_days,ST',
        '--metadata2report', 'ST,source,iso_year',
        '-thr', '4,7,14',
        '--frequency-matrix', 'ST,iso_year',
        '--count-matrix', 'ST,iso_year',
        '--matrix-4-grapetree',
        '--mx-transpose',
        '-out', 'Listeria_outbreak_level_example',
        '--analysis', 'grapetree'
    ]
    """
    
    command = [
        'python', '/app/ReporTree/reportree.py',
        '-m', f'/mnt/rt_runs/{job_number}/metadata.tsv',
        '-a', f'/mnt/rt_runs/{job_number}/allele_profiles.tsv',
        '--columns_summary_report', 'country_code,source_type',
        '--metadata2report', 'country_code,source_type',
        '-thr', '4,7,14',
        '--frequency-matrix', 'country_code,source_type',
        '--matrix-4-grapetree',
        '--mx-transpose',
        '-out', f'/mnt/rt_runs/{job_number}/ReporTree',
        '--analysis', 'grapetree',
        '--partitions2report', 'country_code,source_type'
    ]
    
    print("ReporTree command:")
    print(' '.join(command))
    status = "UNKNOWN"
    error = None
    workdir = f'/mnt/rt_runs/{job_number}'
    # p = subprocess.Popen(command, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p = subprocess.Popen(command)
    try:
        stdout, stderr = p.communicate(timeout=timeout)
        print(stderr)
        if stderr is None:
            status = "SUCCESS"
            error = None
        else:
            status = "RT_ERROR"
            error = stderr
    except subprocess.TimeoutExpired as e:
        status = "RUNNING"
        error = e
    except OSError as e:
        status = "OS_ERROR"
        error = e
    
    return {
        "job_number": job_number,
        "pid": p.pid,
        "status": status,
        "error": error
        }

@app.post("/reportree/start_job/")
async def start_job(job: Job):
    result = run_subprocess(job.job_number)
    print(result)
    return result


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('job_number')
    parser.add_argument('timeout')
    args = parser.parse_args()
    result = run_subprocess(args.job_number, int(args.timeout))
    print(result)