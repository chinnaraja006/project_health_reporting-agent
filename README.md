# Project Health Reporting Agent

AI-powered project health reporting system, built for the Zycus AI Engineer Intern Technical Assignment.

## Features

- Reads project plans from Excel (`.xlsx`/`.xlsm`), including messy real-world exports
- Determines project health using a deterministic RAG scoring framework (see `docs/RAG_Methodology.md`)
- Generates plain-English reasoning using an LLM (via OpenRouter) — the LLM explains the RAG status, it never decides it
- Handles incomplete or messy project data gracefully (`#UNPARSEABLE` cells, broken predecessor links, mislabeled columns) rather than crashing
- Produces weekly project health reports as JSON
- Synthesizes cross-project trends across multiple weekly reports (not just per-project recaps)
- Automatically generates an executive PowerPoint presentation
- Exposes a REST API via FastAPI for integration, alongside the CLI

## Project Structure

```
project_health_agent/
├── agent.py                 # CLI entry point
├── api.py                   # FastAPI wrapper (same core logic as agent.py)
├── weekly_run.py            # Runs the agent across every plan in data/
├── monthly_synthesis.py     # Cross-project trend synthesis
├── make_deck.js             # Generates the executive .pptx from synthesis.json
├── requirements.txt
├── package.json
│
├── app/
│   ├── parser.py             # Loads & normalizes messy .xlsx exports
│   ├── rag_engine.py         # Deterministic RAG scoring + rollup (no LLM calls)
│   └── llm_reasoning.py      # One OpenRouter call per project for plain-English narrative
│
├── docs/
│   └── RAG_Methodology.md    # One-page RAG methodology
│
├── data/                     # Sample project plan exports
└── outputs/                  # Weekly JSON reports (generated)
```

## Architecture

```
Project Plan (Excel)
        │
        ▼
   app/parser.py  ───────► normalizes messy export, flags data-quality issues
        │
        ▼
 app/rag_engine.py  ─────► deterministic RAG scoring + worst-signal-wins rollup
        │
        ▼
 app/llm_reasoning.py ───► one LLM call per project: explains the RAG status
        │
        ▼
   Weekly JSON Report  (outputs/*.json)
        │
        ▼
 monthly_synthesis.py ───► cross-project trend detection (synthesis.json)
        │
        ▼
   make_deck.js  ────────► Executive PowerPoint (.pptx)
```

## Installation

```bash
git clone https://github.com/chinnaraja006/project_health_reporting-agent.git
cd project_health_reporting-agent

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

npm install   # only needed for make_deck.js
```

Copy `.env.example` to `.env` and set your OpenRouter key, or export directly:

```bash
export OPENROUTER_API_KEY=your_key_here
export OPENROUTER_MODEL=openai/gpt-4o-mini
```

The agent runs without a key too — it falls back to a rule-based plain-English summary instead of the LLM narrative if `OPENROUTER_API_KEY` isn't set or the API call fails.

## Running the Project

**Analyze a single project plan (CLI):**
```bash
python3 agent.py data/Project_Plan_B.xlsx
python3 agent.py data/S2P_Project.xlsx
```

**Generate weekly reports for every plan in `data/`:**
```bash
python3 weekly_run.py
```
(This is the unit a weekly cron job would call — see the docstring in `weekly_run.py` for a sample crontab entry.)

**Start the REST API:**
```bash
uvicorn api:app --reload --port 8000
```
API docs: `http://127.0.0.1:8000/docs` — `POST /analyze-project` accepts a multipart `.xlsx` upload.

**Synthesize monthly cross-project trends:**
```bash
python3 monthly_synthesis.py
```

**Generate the executive presentation:**
```bash
node make_deck.js
```

## RAG Framework (Summary)

The RAG status is calculated using deterministic rules, not the LLM, based on:

- Schedule slippage (days behind baseline, critical-path status, total float)
- Milestone / task completion vs. expected progress for elapsed time
- Blockers (keyword detection over status comments)
- Stakeholder sentiment (inferred by the LLM from free-text comments — no structured sentiment field exists in the source data)
- Any existing Schedule Health / RAG field already present in the source export

**Budget burn is not currently scored** — neither sample export contains cost data, so this is explicitly left out rather than guessed, and flagged in the data-quality warnings. See `docs/RAG_Methodology.md` for full detail, thresholds, and assumptions.

The LLM is used only to generate the plain-English narrative and recommendations from an already-decided RAG status — it does not determine the status itself.

## Handling Incomplete Data

The system is built to survive real, messy exports, including:

- `#UNPARSEABLE` placeholder cells
- Mislabeled or shifted outline/level columns
- Broken predecessor references (`#REF`)
- Missing Status Comment / RAG / Schedule Health columns
- Excel serial dates and inconsistently formatted variance values (`"-2d"`, `"0"`, etc.)

Rather than crashing on any of these, the parser degrades gracefully — missing signals fall back to a neutral default, and every data-quality issue encountered is collected and surfaced in the final report rather than silently ignored.

## Technologies Used

- Python (pandas, FastAPI, requests)
- OpenRouter (LLM reasoning layer, model configurable via env var)
- Node.js (pptxgenjs for native, editable PowerPoint generation)

## Author

Chinnaraja S 
AI Engineer Intern Technical Assignment — Zycus
