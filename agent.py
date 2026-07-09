from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from app.parser import load_plan
from app.rag_engine import build_tree, summarize
from app.llm_reasoning import generate_reasoning

RAG_EMOJI = {"Green": "\U0001F7E2", "Amber": "\U0001F7E1", "Red": "\U0001F534"}


def run(path: str) -> dict:
    df, meta = load_plan(path)
    root, project_row = build_tree(df)
    summary = summarize(project_row, root)
    reasoning = generate_reasoning(meta["project_name"], summary)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": os.path.basename(path),
        "project_name": meta["project_name"],
        "project_manager": meta["project_manager"],
        "data_quality_warnings": meta["warnings"],
        "project_rag": summary["project_rag"],
        "project_pct_complete": summary["project_pct_complete"],
        "phases": summary["phases"],
        "reasoning": reasoning,
        "tree": root.to_dict(),
    }


def print_report(result: dict):
    rag = result["project_rag"]
    print(f"\n{RAG_EMOJI.get(rag, '')}  {result['project_name']}  —  {rag.upper()}")
    print(f"PM: {result['project_manager']}  |  Generated: {result['generated_at']}")
    if result["data_quality_warnings"]:
        print("\nData quality notes:")
        for w in result["data_quality_warnings"]:
            print(f"  - {w}")
    print(f"\n{result['reasoning'].get('overall_summary', '')}")
    print("\nPhases:")
    for p in result["phases"]:
        print(f"  {RAG_EMOJI.get(p['rag'], '')} {p['phase']} — {p['rag']}")
    if result["reasoning"].get("top_risks"):
        print("\nTop risks:")
        for r in result["reasoning"]["top_risks"]:
            print(f"  - {r}")
    if result["reasoning"].get("recommended_actions"):
        print("\nRecommended actions:")
        for a in result["reasoning"]["recommended_actions"]:
            print(f"  - {a}")
    print()


def main():
    ap = argparse.ArgumentParser(description="Project Health Reporting Agent")
    ap.add_argument("plan_file", help="Path to project plan .xlsx export")
    ap.add_argument("--out", help="Path to write JSON output (default: outputs/<name>_<date>.json)")
    ap.add_argument("--quiet", action="store_true", help="Skip printed report, only write JSON")
    args = ap.parse_args()

    result = run(args.plan_file)

    out_path = args.out
    if not out_path:
        os.makedirs("outputs", exist_ok=True)
        stem = os.path.splitext(os.path.basename(args.plan_file))[0]
        date_tag = datetime.now().strftime("%Y%m%d")
        out_path = f"outputs/{stem}_{date_tag}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    if not args.quiet:
        print_report(result)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
