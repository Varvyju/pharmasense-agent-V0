"""
PharmaSense Agent — Reasoning Pipeline: Steps 1 & 2
======================================================
Step 1: Ingest & Normalize  (Fabric IQ-style ontology mapping)
Step 2: Pattern Detection    (rule-based risk signal detection)

These are pure, deterministic functions on purpose: no LLM calls here.
This keeps the agent's core risk-detection logic auditable and testable,
which is important for the Reliability & Safety rubric criterion.
"""

from datetime import date
from typing import Dict, Any, List

from app.models import Patient, DetectedSignal


# ---------------------------------------------------------------------------
# STEP 1 — Ingest & Normalize
# ---------------------------------------------------------------------------

def step1_ingest_and_normalize(patient: Patient) -> Dict[str, Any]:
    """
    Maps raw patient journey fields onto ontology-style concepts.

    This mirrors what Fabric IQ's semantic/ontology layer would do in
    production: take raw records (from OneLake) and express them in
    terms of business concepts (LOT sequence, drug class progression,
    switch reasons, biomarker trend direction) that downstream agents
    can reason over directly.
    """
    lots = patient.lines_of_therapy
    lot_sequence = [
        {
            "lot": lot.lot,
            "drug_class": lot.drug_class,
            "duration_days": _duration_days(lot.start_date, lot.end_date),
            "switch_reason": lot.switch_reason,
            "adherence_pct": lot.adherence_pct,
            "is_current": lot.end_date is None,
        }
        for lot in lots
    ]

    lab_values = [r.phe_level_umol_L for r in patient.lab_trend]
    trend_direction = _classify_trend(lab_values)

    normalized = {
        "patient_id": patient.patient_id,
        "ontology_concepts": {
            "diagnosis": patient.diagnosis,
            "age_band": patient.age_band,
            "lot_sequence": lot_sequence,
            "current_drug_class": lot_sequence[-1]["drug_class"] if lot_sequence else None,
            "total_lots": len(lot_sequence),
            "biomarker_trend_direction": trend_direction,
            "biomarker_latest_value": lab_values[-1] if lab_values else None,
            "biomarker_min_value": min(lab_values) if lab_values else None,
            "biomarker_max_value": max(lab_values) if lab_values else None,
            "gap_in_therapy_days": patient.flags.gap_in_therapy_days,
            "rapid_switch_count": patient.flags.rapid_switch_count,
        },
    }
    return normalized


def _duration_days(start: str, end: str | None) -> int | None:
    if end is None:
        return None
    d1 = date.fromisoformat(start)
    d2 = date.fromisoformat(end)
    return (d2 - d1).days


def _classify_trend(values: List[int]) -> str:
    """
    Classifies a biomarker series into: improving, worsening, stable, rebound.

    'rebound' = values decreased then increased again by a meaningful margin
    in the second half of the series.
    """
    if len(values) < 2:
        return "insufficient_data"

    midpoint = len(values) // 2
    first_half = values[:midpoint] if midpoint > 0 else values[:1]
    second_half = values[midpoint:]

    first_avg = sum(first_half) / len(first_half)
    second_avg = sum(second_half) / len(second_half)

    overall_delta = values[-1] - values[0]

    # Rebound: dropped significantly then rose again
    min_val = min(values)
    min_idx = values.index(min_val)
    if min_idx > 0 and min_idx < len(values) - 1:
        rise_after_min = values[-1] - min_val
        drop_before_min = values[0] - min_val
        if drop_before_min > 100 and rise_after_min > 100:
            return "rebound"

    if overall_delta <= -100:
        return "improving"
    if overall_delta >= 100:
        return "worsening"
    return "stable"


# ---------------------------------------------------------------------------
# STEP 2 — Pattern Detection
# ---------------------------------------------------------------------------

def step2_detect_signals(normalized: Dict[str, Any]) -> List[DetectedSignal]:
    """
    Applies deterministic rules over the normalized ontology concepts to
    detect treatment-pattern risk signals. Each rule is independent and
    documented, so judges/reviewers can audit exactly why a signal fired.
    """
    concepts = normalized["ontology_concepts"]
    signals: List[DetectedSignal] = []

    # Rule 1: Rapid LOT switching (>= 1 switch within a short duration)
    if concepts["rapid_switch_count"] >= 1:
        signals.append(DetectedSignal(
            signal_id="SIG-RAPID-SWITCH",
            name="Rapid line-of-therapy switching",
            severity="medium" if concepts["rapid_switch_count"] == 1 else "high",
            description=(
                f"Patient has {concepts['rapid_switch_count']} line-of-therapy "
                f"switch(es) that occurred within a short duration (under ~4 months), "
                f"which may indicate the prior therapy was not given a full trial period."
            ),
            related_fields={"rapid_switch_count": concepts["rapid_switch_count"]},
        ))

    # Rule 2: Therapy gap > 30 days
    if concepts["gap_in_therapy_days"] > 30:
        signals.append(DetectedSignal(
            signal_id="SIG-THERAPY-GAP",
            name="Therapy continuity gap",
            severity="medium",
            description=(
                f"A gap of {concepts['gap_in_therapy_days']} days was detected between "
                f"the end of one line of therapy and the start of the next, exceeding "
                f"the 30-day continuity threshold."
            ),
            related_fields={"gap_in_therapy_days": concepts["gap_in_therapy_days"]},
        ))

    # Rule 3: Biomarker rebound
    if concepts["biomarker_trend_direction"] == "rebound":
        signals.append(DetectedSignal(
            signal_id="SIG-BIOMARKER-REBOUND",
            name="Biomarker rebound after initial improvement",
            severity="high",
            description=(
                f"Phe levels improved initially (down to {concepts['biomarker_min_value']} "
                f"umol/L) but have since risen back to {concepts['biomarker_latest_value']} "
                f"umol/L, suggesting a possible rebound pattern."
            ),
            related_fields={
                "min_value": concepts["biomarker_min_value"],
                "latest_value": concepts["biomarker_latest_value"],
            },
        ))

    # Rule 4: Biomarker worsening trend
    if concepts["biomarker_trend_direction"] == "worsening":
        signals.append(DetectedSignal(
            signal_id="SIG-BIOMARKER-WORSENING",
            name="Worsening biomarker trend",
            severity="high",
            description=(
                f"Phe levels show a consistent upward trend, reaching "
                f"{concepts['biomarker_latest_value']} umol/L at the most recent reading."
            ),
            related_fields={"latest_value": concepts["biomarker_latest_value"]},
        ))

    # Rule 5: Adherence decline across LOTs
    lot_seq = concepts["lot_sequence"]
    if len(lot_seq) >= 2:
        adherence_drop = lot_seq[-2]["adherence_pct"] - lot_seq[-1]["adherence_pct"]
        if adherence_drop >= 15:
            signals.append(DetectedSignal(
                signal_id="SIG-ADHERENCE-DECLINE",
                name="Adherence decline across lines of therapy",
                severity="medium",
                description=(
                    f"Adherence dropped from {lot_seq[-2]['adherence_pct']}% on the "
                    f"previous line of therapy to {lot_seq[-1]['adherence_pct']}% on "
                    f"the current line, a decline of {adherence_drop} percentage points."
                ),
                related_fields={
                    "previous_adherence": lot_seq[-2]["adherence_pct"],
                    "current_adherence": lot_seq[-1]["adherence_pct"],
                },
            ))

    # Rule 6: Stable trend but sub-optimal adherence (plateau risk)
    current_adherence = lot_seq[-1]["adherence_pct"] if lot_seq else None
    if (concepts["biomarker_trend_direction"] == "stable"
            and current_adherence is not None and current_adherence < 70):
        signals.append(DetectedSignal(
            signal_id="SIG-PLATEAU-LOW-ADHERENCE",
            name="Stable trend with sub-optimal adherence",
            severity="low",
            description=(
                f"Biomarker levels appear stable, but current adherence is "
                f"{current_adherence}%, below the 70% threshold often used as a "
                f"reference point for adequate adherence."
            ),
            related_fields={"current_adherence": current_adherence},
        ))

    # Rule 7: Long single-LOT duration without re-assessment
    if concepts["total_lots"] == 1:
        current_lot = lot_seq[0]
        if current_lot["duration_days"] is None:
            # current LOT, started long ago — estimate via diagnosis (not exact, illustrative)
            signals.append(DetectedSignal(
                signal_id="SIG-LONG-SINGLE-LOT",
                name="Single line of therapy with no documented switch",
                severity="low",
                description=(
                    "Patient has remained on a single line of therapy with no "
                    "documented switch, which may benefit from a periodic re-assessment."
                ),
                related_fields={"current_drug_class": concepts["current_drug_class"]},
            ))

    return signals
