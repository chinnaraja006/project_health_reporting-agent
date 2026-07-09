"""
api.py — thin FastAPI wrapper around the same core (parser -> rag_engine ->
llm_reasoning) used by agent.py. No logic is duplicated here.

Run:
    uvicorn api:app --reload --port 8000

Endpoints:
    POST /analyze-project   (multipart file upload, .xlsx)  -> full JSON report
    GET  /health
"""
import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agent import run as run_agent

app = FastAPI(title="Project Health Reporting Agent", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze-project")
async def analyze_project(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xlsm")):
        raise HTTPException(400, "Please upload a .xlsx or .xlsm project plan export.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = run_agent(tmp_path)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Failed to analyze plan: {e}") from e
    finally:
        os.unlink(tmp_path)

    return result
