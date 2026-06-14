"""
PharmaSense Agent — Synthetic Data Generator
==============================================
Generates a cohort of fully synthetic PKU (Phenylketonuria) patient
treatment journeys. NO REAL PATIENT DATA IS USED ANYWHERE.

Run:
    python synthetic_data_generator.py

Output:
    patients.json  -- written to the same folder
"""

import json
import random
from datetime import date, timedelta

random.seed(42)  # reproducible output

DRUG_CLASSES = {
    "Sapropterin (Kuvan-class)": "BH4 cofactor therapy",
    "Pegvaliase (PAL-class)": "Enzyme substitution therapy",
    "Large Neutral Amino Acids (LNAA)": "Amino acid supplementation",
    "Dietary Phe restriction only": "Diet-based management",
}

SWITCH_REASONS = [
    "inadequate_response",
    "tolerability_issue",
    "adherence_decline",
    "guideline_update",
    None,  # patient still on current LOT, no switch yet
]

AGE_BANDS = ["6-12", "13-17", "18-25", "26-40", "41-60"]


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 1)))


def generate_lab_trend(start_date: date, months: int, base_level: int, pattern: str):
    """
    pattern: 'improving', 'rebound', 'stable', 'worsening'
    Generates Phe level (umol/L) readings every ~3 months.
    """
    trend = []
    current = base_level
    d = start_date
    for i in range(months // 3):
        if pattern == "improving":
            current = max(120, current - random.randint(60, 150))
        elif pattern == "rebound":
            if i < months // 6:
                current = max(120, current - random.randint(80, 150))
            else:
                current = current + random.randint(80, 200)
        elif pattern == "worsening":
            current = current + random.randint(40, 120)
        else:  # stable
            current = current + random.randint(-40, 40)
        trend.append({
            "date": d.isoformat(),
            "phe_level_umol_L": max(60, current)
        })
        d = d + timedelta(days=90)
    return trend


def generate_patient(idx: int) -> dict:
    pid = f"SYN-{idx:04d}"
    age_band = random.choice(AGE_BANDS)
    diagnosis_date = random_date(date(2010, 1, 1), date(2020, 1, 1))

    # Decide how many lines of therapy (1-3)
    num_lots = random.choices([1, 2, 3], weights=[0.35, 0.45, 0.20])[0]
    drug_names = list(DRUG_CLASSES.keys())
    random.shuffle(drug_names)
    chosen_drugs = drug_names[:num_lots]

    lots = []
    cursor = diagnosis_date + timedelta(days=random.randint(10, 60))
    gap_days_total = 0
    rapid_switch_count = 0
    prev_end = None

    for i, drug in enumerate(chosen_drugs):
        is_last = (i == num_lots - 1)
        lot_start = cursor
        if prev_end is not None:
            gap = (lot_start - prev_end).days
            gap_days_total += max(0, gap)

        if is_last:
            lot_end = None
            switch_reason = None
            duration_days = random.randint(180, 720)
        else:
            duration_days = random.randint(60, 540)
            lot_end = lot_start + timedelta(days=duration_days)
            switch_reason = random.choice(
                [r for r in SWITCH_REASONS if r is not None]
            )
            if duration_days < 120:
                rapid_switch_count += 1

        adherence = random.randint(55, 97)

        lots.append({
            "lot": i + 1,
            "drug": drug,
            "drug_class": DRUG_CLASSES[drug],
            "start_date": lot_start.isoformat(),
            "end_date": lot_end.isoformat() if lot_end else None,
            "switch_reason": switch_reason,
            "adherence_pct": adherence,
        })

        if lot_end:
            cursor = lot_end + timedelta(days=random.randint(0, 45))
            prev_end = lot_end
        else:
            prev_end = lot_start + timedelta(days=duration_days)

    # Lab trend pattern depends on last LOT characteristics
    last_lot = lots[-1]
    if last_lot["adherence_pct"] < 70:
        pattern = "rebound"
    elif last_lot["drug_class"] == "Enzyme substitution therapy":
        pattern = random.choice(["improving", "rebound"])
    elif last_lot["drug_class"] == "Diet-based management":
        pattern = random.choice(["stable", "worsening"])
    else:
        pattern = random.choice(["improving", "stable"])

    lab_trend = generate_lab_trend(
        start_date=date.fromisoformat(last_lot["start_date"]),
        months=24,
        base_level=random.randint(900, 1400),
        pattern=pattern,
    )

    patient = {
        "patient_id": pid,
        "age_band": age_band,
        "sex": random.choice(["F", "M"]),
        "diagnosis": "Phenylketonuria (PKU)",
        "diagnosis_date": diagnosis_date.isoformat(),
        "lines_of_therapy": lots,
        "lab_trend": lab_trend,
        "flags": {
            "gap_in_therapy_days": gap_days_total,
            "rapid_switch_count": rapid_switch_count,
        },
    }
    return patient


def main():
    cohort = [generate_patient(i + 1) for i in range(28)]
    with open("patients.json", "w") as f:
        json.dump(cohort, f, indent=2)
    print(f"Generated {len(cohort)} synthetic patients -> patients.json")


if __name__ == "__main__":
    main()
