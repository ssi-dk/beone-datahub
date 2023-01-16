import subprocess
from typing import Union
from pydantic import BaseModel

from fastapi import FastAPI

app = FastAPI()

class Job(BaseModel):
    job_number: int
    timeout: int = 2
    columns_summary_report: list
    metadata2report: list
    frequency_matrix: list
    count_matrix: list
    matrix_4_grapetree: bool
    mx_transpose: bool
    analysis: str
    threshold: list

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/")
async def start_job(job: Job):
    
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
        '-m', f'/mnt/rt_runs/{job.job_number}/metadata.tsv',
        '-a', f'/mnt/rt_runs/{job.job_number}/allele_profiles.tsv',
        '--columns_summary_report', ','.join(job.columns_summary_report),
        '-out', f'/mnt/rt_runs/{job.job_number}/ReporTree',
        '--analysis', job.analysis,
    ]

    if len(job.threshold) > 0:
        if job.analysis == 'grapetree':
            command.extend(['--threshold', ','.join(job.threshold)])
        elif job.analysis == 'HC':
            command.extend(['--HC-threshold', ','.join(job.threshold)])

    if len(job.metadata2report) > 0:
         command.extend(['--metadata2report', ','.join(job.metadata2report)])
    
    if len(job.frequency_matrix) > 0:
         command.extend(['--frequency-matrix', ','.join(job.frequency_matrix)])
    
    if len(job.count_matrix) > 0:
        command.extend(['--count-matrix', ','.join(job.count_matrix)])
    
    if job.matrix_4_grapetree is True:
        command.append('--matrix-4-grapetree')
    
    if job.mx_transpose is True:
        command.append('--mx-transpose')
    
    print("ReporTree command:")
    print(command)
    # print(' '.join(command))
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
