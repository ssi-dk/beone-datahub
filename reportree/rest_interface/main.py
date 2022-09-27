from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/reportree/start_job/{job_number}")
async def start_job(job_number: int):
    return {
        "job: number": job_number,
        "status": "OK"
        }
