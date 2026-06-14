"""
PharmaSense Agent — Data Loader
==================================
Loads synthetic patients and the curated knowledge base from the /data
folder (JSON files). No database required for the MVP.
"""

import json
import os
from typing import List

from app.models import Patient, KBEntry, PatientSummary

# Resolve path to the shared /data folder at the project root
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(_THIS_DIR, "..", "..", "data"))

PATIENTS_PATH = os.path.join(DATA_DIR, "patients.json")
KB_PATH = os.path.join(DATA_DIR, "knowledge_base.json")


def load_patients() -> List[Patient]:
    with open(PATIENTS_PATH) as f:
        raw = json.load(f)
    return [Patient(**p) for p in raw]


def load_kb_entries() -> List[KBEntry]:
    with open(KB_PATH) as f:
        raw = json.load(f)
    return [KBEntry(**e) for e in raw]


def get_patient_by_id(patients: List[Patient], patient_id: str) -> Patient | None:
    for p in patients:
        if p.patient_id == patient_id:
            return p
    return None


def to_summary(patient: Patient) -> PatientSummary:
    current_lot = patient.lines_of_therapy[-1]
    return PatientSummary(
        patient_id=patient.patient_id,
        age_band=patient.age_band,
        diagnosis=patient.diagnosis,
        num_lots=len(patient.lines_of_therapy),
        current_drug=current_lot.drug,
        rapid_switch_count=patient.flags.rapid_switch_count,
        gap_in_therapy_days=patient.flags.gap_in_therapy_days,
    )
