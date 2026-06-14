"""
PharmaSense Agent — Pipeline Orchestrator
============================================
Runs the full 5-step reasoning pipeline for a given patient and packages
the result (step-by-step trace + final brief) for the API response.

This is the "Foundry Agent Service"-equivalent orchestration layer in
the MVP: a single coordinator invoking each reasoning step in sequence,
analogous to how a multi-step agent plan would be executed in production.
"""

from typing import List

from app.models import Patient, KBEntry, AgentStep, AnalysisResult
from app.reasoning_steps_1_2 import step1_ingest_and_normalize, step2_detect_signals
from app.reasoning_step_3 import step3_retrieve_evidence
from app.reasoning_steps_4_5 import step4_synthesize_brief, step5_safety_check


def run_pipeline(patient: Patient, kb_entries: List[KBEntry]) -> AnalysisResult:
    steps: List[AgentStep] = []

    # --- Step 1 ---
    normalized = step1_ingest_and_normalize(patient)
    steps.append(AgentStep(
        step=1,
        name="Ingest & Normalize",
        description=(
            "Maps the patient's raw treatment journey onto ontology-style "
            "concepts (LOT sequence, drug classes, biomarker trend direction). "
            "This mirrors Fabric IQ's semantic data modeling layer."
        ),
        output=normalized,
    ))

    # --- Step 2 ---
    signals = step2_detect_signals(normalized)
    steps.append(AgentStep(
        step=2,
        name="Pattern Detection",
        description=(
            "Applies deterministic rules over the normalized concepts to "
            "detect treatment-pattern risk signals (rapid switching, therapy "
            "gaps, biomarker rebound/worsening, adherence decline)."
        ),
        output={
            "signals_detected": len(signals),
            "signals": [s.model_dump() for s in signals],
        },
    ))

    # --- Step 3 ---
    current_drug_class = normalized["ontology_concepts"]["current_drug_class"]
    evidence = step3_retrieve_evidence(signals, kb_entries, current_drug_class)
    steps.append(AgentStep(
        step=3,
        name="Evidence Retrieval",
        description=(
            "For each detected signal, retrieves the most relevant entries "
            "from the curated knowledge base via TF-IDF similarity. This "
            "mirrors Foundry IQ's role of grounding agent outputs in cited, "
            "governed knowledge sources."
        ),
        output={
            "evidence": [e.model_dump() for e in evidence],
        },
    ))

    # --- Step 4 ---
    brief = step4_synthesize_brief(patient, normalized, signals, evidence, kb_entries)
    steps.append(AgentStep(
        step=4,
        name="Synthesis",
        description=(
            "Synthesizes the normalized data, detected signals, and retrieved "
            "evidence into a structured, citation-backed decision-support brief."
        ),
        output={"brief_preview": brief.model_dump()},
    ))

    # --- Step 5 ---
    safety_result = step5_safety_check(brief)
    steps.append(AgentStep(
        step=5,
        name="Safety & Compliance Check",
        description=(
            "Scans every statement in the brief for diagnostic or prescriptive "
            "language, strips any violations, and enforces the mandatory "
            "human-review flag and disclaimer."
        ),
        output=safety_result,
    ))

    return AnalysisResult(
        patient_id=patient.patient_id,
        steps=steps,
        brief=brief,
        requires_human_review=True,
    )
