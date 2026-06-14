"""
PharmaSense Agent — Reasoning Pipeline: Step 3
=================================================
Step 3: Evidence Retrieval (Foundry IQ-style grounded retrieval)

For each detected signal, retrieve the most relevant knowledge-base
entries using TF-IDF cosine similarity over signal text + tags vs.
KB summaries + tags. This mirrors Foundry IQ's role of grounding agent
outputs in cited, governed knowledge sources.

Deliberately lightweight: no vector DB, no embedding model download —
keeps the MVP runnable anywhere with just the Python standard library.
"""

from typing import List, Dict, Any

from app.models import DetectedSignal, KBEntry, RetrievedEvidence
from app.text_similarity import fit_tfidf, transform, cosine_similarity


# Maps signal_id -> extra tag keywords that boost retrieval relevance
SIGNAL_TAG_HINTS = {
    "SIG-RAPID-SWITCH": ["rapid_switch", "LOT", "switch_reason"],
    "SIG-THERAPY-GAP": ["gap_in_therapy", "continuity_of_care"],
    "SIG-BIOMARKER-REBOUND": ["rebound", "adherence", "enzyme_substitution"],
    "SIG-BIOMARKER-WORSENING": ["worsening_trend", "diet_management"],
    "SIG-ADHERENCE-DECLINE": ["adherence", "confounder"],
    "SIG-PLATEAU-LOW-ADHERENCE": ["stable_trend", "adherence", "plateau"],
    "SIG-LONG-SINGLE-LOT": ["long_duration", "re_assessment", "single_LOT"],
}


def _kb_document_text(entry: KBEntry) -> str:
    return f"{entry.title} {entry.summary} {' '.join(entry.tags)} {entry.drug_class}"


def _signal_query_text(signal: DetectedSignal, current_drug_class: str | None) -> str:
    hints = SIGNAL_TAG_HINTS.get(signal.signal_id, [])
    drug_class_text = current_drug_class or ""
    return f"{signal.name} {signal.description} {' '.join(hints)} {drug_class_text}"


def step3_retrieve_evidence(
    signals: List[DetectedSignal],
    kb_entries: List[KBEntry],
    current_drug_class: str | None,
    top_k: int = 2,
) -> List[RetrievedEvidence]:
    """
    For each detected signal, retrieve the top_k most relevant KB entries
    via TF-IDF cosine similarity. Returns relevance scores so the UI can
    show *why* each citation was selected.
    """
    if not signals:
        return []

    kb_docs = [_kb_document_text(e) for e in kb_entries]
    query_docs = [_signal_query_text(s, current_drug_class) for s in signals]

    # Fit TF-IDF over KB docs + queries together so vocab is shared.
    model = fit_tfidf(kb_docs + query_docs)
    kb_matrix = model.doc_vectors[: len(kb_docs)]

    results: List[RetrievedEvidence] = []
    for i, signal in enumerate(signals):
        query_vector = transform(query_docs[i], model)
        sims = cosine_similarity(query_vector, kb_matrix)
        ranked_idx = sorted(range(len(sims)), key=lambda idx: sims[idx], reverse=True)[:top_k]

        matches = []
        for idx in ranked_idx:
            score = float(sims[idx])
            if score <= 0:
                continue
            entry = kb_entries[idx]
            matches.append({
                "kb_id": entry.kb_id,
                "title": entry.title,
                "relevance_score": round(score, 3),
            })

        results.append(RetrievedEvidence(
            signal_id=signal.signal_id,
            kb_matches=matches,
        ))

    return results


def get_kb_entry_by_id(kb_entries: List[KBEntry], kb_id: str) -> KBEntry | None:
    for entry in kb_entries:
        if entry.kb_id == kb_id:
            return entry
    return None
