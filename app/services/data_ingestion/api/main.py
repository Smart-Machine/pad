import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from utils.processes import run_crawling_process

app = FastAPI()

@app.get("/health")
def is_service_healthy():
    return "healthy" 

@app.get("/update")
def update_data(): 
    run_crawling_process()
    return {
        "msg": "success"
    }