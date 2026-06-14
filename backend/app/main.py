"""
PharmaSense Agent — FastAPI Backend
======================================
Run with:
    cd backend
    uvicorn app.main:app --reload --port 8000

Endpoints:
    GET  /api/health
    GET  /api/patients
    GET  /api/patients/{patient_id}
    GET  /api/knowledge-base
    POST /api/agent/analyze/{patient_id}
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.data_loader import load_patients, load_kb_entries, get_patient_by_id, to_summary
from app.pipeline import run_pipeline
from app.models import AnalysisResult

app = FastAPI(title="PharmaSense Agent API", version="0.1.0")

# Allow the local Vite dev server (and any origin during the hackathon demo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data once at startup (small JSON files, no DB needed for MVP)
PATIENTS = load_patients()
KB_ENTRIES = load_kb_entries()


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "patients_loaded": len(PATIENTS),
        "kb_entries_loaded": len(KB_ENTRIES),
    }


@app.get("/api/patients")
def list_patients():
    return [to_summary(p).model_dump() for p in PATIENTS]


@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    patient = get_patient_by_id(PATIENTS, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.model_dump()


@app.get("/api/knowledge-base")
def list_kb_entries():
    return [e.model_dump() for e in KB_ENTRIES]


@app.post("/api/agent/analyze/{patient_id}", response_model=AnalysisResult)
def analyze_patient(patient_id: str):
    patient = get_patient_by_id(PATIENTS, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    result = run_pipeline(patient, KB_ENTRIES)
    return result
