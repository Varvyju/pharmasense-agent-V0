"""
PharmaSense Agent — Data Models
=================================
Pydantic schemas for patients, knowledge base entries, agent reasoning
steps, and the final decision-support brief.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class LineOfTherapy(BaseModel):
    lot: int
    drug: str
    drug_class: str
    start_date: str
    end_date: Optional[str] = None
    switch_reason: Optional[str] = None
    adherence_pct: int


class LabReading(BaseModel):
    date: str
    phe_level_umol_L: int


class PatientFlags(BaseModel):
    gap_in_therapy_days: int
    rapid_switch_count: int


class Patient(BaseModel):
    patient_id: str
    age_band: str
    sex: str
    diagnosis: str
    diagnosis_date: str
    lines_of_therapy: List[LineOfTherapy]
    lab_trend: List[LabReading]
    flags: PatientFlags


class PatientSummary(BaseModel):
    """Lightweight summary used for the cohort/landing view."""
    patient_id: str
    age_band: str
    diagnosis: str
    num_lots: int
    current_drug: str
    rapid_switch_count: int
    gap_in_therapy_days: int


class KBEntry(BaseModel):
    kb_id: str
    title: str
    drug_class: str
    summary: str
    source_type: str
    tags: List[str]


class DetectedSignal(BaseModel):
    signal_id: str
    name: str
    severity: str  # "low" | "medium" | "high"
    description: str
    related_fields: Dict[str, Any]


class RetrievedEvidence(BaseModel):
    signal_id: str
    kb_matches: List[Dict[str, Any]]  # [{kb_id, title, relevance_score}]


class BriefSection(BaseModel):
    heading: str
    bullets: List[str]  # each bullet should end with a [KB-xxx] citation or [data] reference


class Brief(BaseModel):
    patient_id: str
    summary: str
    sections: List[BriefSection]
    requires_human_review: bool
    disclaimer: str


class AgentStep(BaseModel):
    step: int
    name: str
    description: str
    output: Dict[str, Any]


class AnalysisResult(BaseModel):
    patient_id: str
    steps: List[AgentStep]
    brief: Brief
    requires_human_review: bool
