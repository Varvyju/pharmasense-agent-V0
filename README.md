# PharmaSense Agent

> An explainable, multi-step reasoning agent for pharma treatment journey
> analysis — built for the **Microsoft Agents League Hackathon 2026**
> (Reasoning Agents track).

---

## Important disclaimers

- **All data in this project is SYNTHETIC.** No real patient data is used,
  stored, or referenced anywhere in this repository.
- This tool **does not diagnose, prescribe, or recommend treatment
  changes.**
- Every output is tagged `requires_human_review: true` and carries a
  mandatory disclaimer. This is **decision-support for care teams**, not
  a clinical decision-maker.

---

## The problem

Care teams managing complex, multi-year pharma treatment journeys —
multiple lines of therapy, switch reasons, adherence records, biomarker
trends — face a real burden in spotting subtle but important patterns:
rapid therapy switches, gaps in continuity, biomarker rebounds that look
like "improvement" until you check the second half of the trend. Today
this review is largely manual.

## The solution

**PharmaSense Agent** is a 5-step explainable reasoning agent that:

1. Normalizes a patient's raw treatment journey into ontology-style
   concepts
2. Detects treatment-pattern risk signals using transparent, auditable
   rules
3. Retrieves cited supporting evidence from a curated knowledge base for
   each signal
4. Synthesizes everything into a structured, citation-backed brief
5. Runs a safety pass that strips any diagnostic/prescriptive language
   and enforces human review

Every step of the reasoning process is visible in the UI — nothing is a
black box.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React + Vite)                        │
│  Cohort view → Patient journey → Reasoning trace → Brief          │
└───────────────────────────────┬───────────────────────────────────┘
                                  │ REST (JSON)
┌───────────────────────────────▼───────────────────────────────────┐
│                  BACKEND (FastAPI, Python)                         │
│                                                                      │
│  Step 1: Ingest & Normalize   (Fabric IQ-style ontology mapping)    │
│  Step 2: Pattern Detection    (deterministic risk-signal rules)     │
│  Step 3: Evidence Retrieval   (Foundry IQ-style cited RAG)          │
│  Step 4: Synthesis            (structured, cited brief)             │
│  Step 5: Safety & Compliance  (guardrails + human-review flag)      │
│                                                                      │
│  Data: synthetic patient journeys + curated knowledge base (JSON)   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## How this maps to Microsoft's IQ stack

This MVP runs entirely locally with static JSON data — **deliberately,**
to keep it runnable by anyone without Azure credentials. But every
component is architected to map directly onto Microsoft Foundry, Foundry
IQ, and Fabric IQ:

| MVP component | Maps to | Production equivalent |
|---|---|---|
| Synthetic patient journeys, normalized into ontology concepts (LOT sequence, drug class, switch reason, biomarker trend) in Step 1 | **Fabric IQ** | Fabric OneLake + Fabric IQ ontology / semantic model over real treatment data |
| Curated knowledge base + cited TF-IDF retrieval in Step 3 | **Foundry IQ** | Foundry IQ knowledge base backed by Azure AI Search, with identity-based access controls |
| 5-step sequential agent orchestration (`pipeline.py`) | **Microsoft Foundry Agent Service** | Foundry Agent Service / Semantic Kernel multi-agent orchestration |
| Step 5 safety/guardrail layer | **Responsible AI in Foundry** | Foundry Content Safety + agent evaluation pipelines |

---

## Agent reasoning flow

| Step | Name | What it does |
|---|---|---|
| 1 | Ingest & Normalize | Maps raw journey fields to ontology concepts: LOT sequence, drug classes, switch reasons, biomarker trend direction |
| 2 | Pattern Detection | Applies 7 deterministic rules to detect risk signals (rapid switching, therapy gaps, biomarker rebound/worsening, adherence decline, etc.) |
| 3 | Evidence Retrieval | For each signal, retrieves top-matching entries from a 13-entry curated knowledge base via TF-IDF cosine similarity |
| 4 | Synthesis | Builds a structured brief (Summary, Detected Signals, Supporting Evidence, Discussion Points) — every sentence carries a `[KB-xxx]`, `[SIG-xxx]`, or `[data]` citation |
| 5 | Safety & Compliance | Regex-scans every sentence for diagnostic/prescriptive language, strips violations, forces `requires_human_review: true` and attaches the disclaimer |

---

## Tech stack

- **Backend:** Python 3.11, FastAPI, Pydantic, pure-Python TF-IDF retrieval
- **Frontend:** React + Vite, React Router, Recharts
- **Data:** static JSON (28 synthetic patients, 13 knowledge-base entries) — no database required
- **Optional LLM enhancement:** Step 4 supports an optional phrasing-only
  LLM rewrite pass (`PHARMASENSE_LLM_REWRITE=1` + `OPENAI_API_KEY`). The
  pipeline works fully offline without it — the LLM is an enhancement,
  never a dependency, and the safety layer (Step 5) re-validates its
  output regardless.

---

## Setup & run

### Backend
```bash
cd backend
pip install -r requirements.txt --break-system-packages
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Then open the frontend URL (default `http://localhost:5173`).

### Regenerating synthetic data (optional)
```bash
cd data
python3 synthetic_data_generator.py
```

---

## Demo video

[Link to demo video — add after recording]

---

## Responsible AI / safety design

- **Step 5 is a first-class pipeline stage**, not a post-hoc filter —
  it runs on every analysis and is shown in the UI trace.
- Every brief carries `requires_human_review: true` and a disclaimer
  banner, both enforced server-side (cannot be bypassed by the client).
- A regex-based prohibited-language filter blocks diagnostic/prescriptive
  phrasing (`diagnose`, `prescribe`, `should start/stop/switch`, etc.).
  Any match is stripped and logged in a visible audit trail.
- Steps 1–3 are fully deterministic (no LLM) by default, eliminating
  hallucination risk in the core reasoning chain. The optional LLM pass
  in Step 4 only rephrases already-cited content and is re-checked by
  Step 5.

---

## Roadmap (production path)

- Replace synthetic JSON → Fabric IQ ontology over real OneLake data,
  with identity-based access controls
- Replace curated KB → Foundry IQ knowledge base backed by Azure AI Search
- Replace single-process pipeline → Foundry Agent Service multi-agent
  deployment with full OpenTelemetry tracing
- Add Foundry evaluation suites for the safety/guardrail layer
- Expand the rule set in Step 2 with clinician-reviewed thresholds per
  therapeutic area

---

## Team

Varun Namavali ([github.com/Varvyju](https://github.com/Varvyju))
Built for the Microsoft Agents League Hackathon — Reasoning Agents track.
