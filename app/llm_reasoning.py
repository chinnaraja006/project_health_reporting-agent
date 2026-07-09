from __future__ import annotations
import json
import os
import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

SYSTEM_PROMPT = """You are a Professional Services project health analyst. \
You are given a project's deterministically-computed RAG status per phase, \
plus the specific Red/Amber tasks and their raw status comments. \
Write plain-English reasoning a VP could read in 30 seconds. \
Do not change or contradict the given RAG colors — only explain and \
contextualize them. Output ONLY valid JSON, no markdown fences, no preamble, \
matching this schema exactly:
{
  "overall_summary": "2-3 sentences on overall project health",
  "phase_reasoning": [{"phase": "...", "reasoning": "1-2 plain-English sentences"}],
  "top_risks": ["risk 1", "risk 2", ...],
  "recommended_actions": ["action 1", "action 2", ...]
}"""


def _call_openrouter(payload: dict) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    resp = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _fallback_reasoning(summary: dict) -> dict:
    """No API key / call failed — deterministic plain-English fallback so the
    agent never hard-fails just because the reasoning layer is unavailable."""
    phases = summary["phases"]
    reds = [p["phase"] for p in phases if p["rag"] == "Red"]
    ambers = [p["phase"] for p in phases if p["rag"] == "Amber"]
    overall = summary["project_rag"]
    parts = []
    if overall == "Red":
        parts.append(f"Project is RED. {len(reds)} phase(s) at risk: {', '.join(reds) or 'see detail'}.")
    elif overall == "Amber":
        parts.append(f"Project is AMBER. Watch phases: {', '.join(ambers) or 'see detail'}.")
    else:
        parts.append("Project is GREEN with no material schedule or milestone risk detected.")
    risks = []
    for p in phases:
        for t in p["red_tasks"] + p["amber_tasks"]:
            risks.append(f"{p['phase']} / {t['task']}: {t['reasons'][0] if t['reasons'] else 'flagged'}")
    return {
        "overall_summary": " ".join(parts),
        "phase_reasoning": [
            {"phase": p["phase"], "reasoning": f"{p['rag']} — {p['pct_complete']*100:.0f}% complete." if p["pct_complete"] == p["pct_complete"] else f"{p['rag']}."}
            for p in phases
        ],
        "top_risks": risks[:6] or ["No material risks detected in current data."],
        "recommended_actions": ["Review flagged tasks above with the assigned owners."] if risks else ["Continue current cadence; no action required."],
    }


def generate_reasoning(project_name: str, summary: dict) -> dict:
    user_prompt = (
        f"Project: {project_name}\n"
        f"Overall RAG (already computed, do not change): {summary['project_rag']}\n\n"
        f"Phase detail:\n{json.dumps(summary['phases'], indent=2, default=str)}"
    )
    try:
        content = _call_openrouter({
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 1200,
            "temperature": 0.3,
        })
        content = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(content)
    except Exception as e:  # noqa: BLE001 — deliberate broad catch for graceful degradation
        fallback = _fallback_reasoning(summary)
        fallback["_llm_error"] = str(e)
        return fallback
