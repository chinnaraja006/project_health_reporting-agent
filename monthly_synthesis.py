from __future__ import annotations
import argparse
import glob
import json
import os
import re
from collections import Counter, defaultdict

THEMES = {
    "Training & Enablement": ["training", "trainer", "enablement"],
    "Documentation & Sign-off": ["documentation", "sign off", "sign-off", "signoff", "iad", "review"],
    "Supplier / Integration": ["supplier", "integration", "sso", "isupplier"],
    "Configuration & Build": ["configuration", "config", "build", "staging"],
    "UAT & Testing": ["uat", "test", "acceptance"],
    "Go-Live & Migration": ["migration", "go-live", "golive", "production", "hypercare"],
}


def theme_for(text: str) -> str | None:
    low = text.lower()
    for theme, keywords in THEMES.items():
        if any(k in low for k in keywords):
            return theme
    return None


def load_latest_per_project(outputs_dir: str) -> list[dict]:
    """If the same project has multiple weekly runs, keep only the latest."""
    files = glob.glob(os.path.join(outputs_dir, "*.json"))
    by_project: dict[str, tuple[str, dict]] = {}
    for fp in files:
        with open(fp) as f:
            data = json.load(f)
        name = data.get("project_name", os.path.basename(fp))
        gen = data.get("generated_at", "")
        if name not in by_project or gen > by_project[name][0]:
            by_project[name] = (gen, data)
    return [d for _, d in by_project.values()]


def synthesize(projects: list[dict]) -> dict:
    n = len(projects)
    rag_counts = Counter(p["project_rag"] for p in projects)
    avg_pct = sum((p.get("project_pct_complete") or 0) for p in projects) / n if n else 0

    theme_counter = Counter()
    theme_examples = defaultdict(list)
    for p in projects:
        for phase in p["phases"]:
            if phase["rag"] in ("Red", "Amber"):
                t = theme_for(phase["phase"])
                if t:
                    theme_counter[t] += 1
                    short_name = p["project_name"].replace("Zycus - ", "").replace(" S2P Implementation", "")
                    theme_examples[t].append(f"{short_name}: {phase['phase']} ({phase['rag']})")
        for risk in p.get("reasoning", {}).get("top_risks", []):
            t = theme_for(risk)
            if t:
                theme_counter[t] += 1

    recurring_themes = [
        {"theme": t, "count": c, "examples": theme_examples[t][:4]}
        for t, c in theme_counter.most_common()
        if c >= 2 or n == 1  # "recurring" = shows up 2+ times, or trivially if only 1 project
    ]
    all_theme_ranked = [{"theme": t, "count": c} for t, c in theme_counter.most_common()]

    project_rows = []
    for p in projects:
        reds = [ph["phase"] for ph in p["phases"] if ph["rag"] == "Red"]
        ambers = [ph["phase"] for ph in p["phases"] if ph["rag"] == "Amber"]
        project_rows.append({
            "name": p["project_name"],
            "pm": p.get("project_manager", "Unknown"),
            "rag": p["project_rag"],
            "pct_complete": p.get("project_pct_complete"),
            "red_phase_count": len(reds),
            "amber_phase_count": len(ambers),
            "red_phases": reds,
            "top_risk": (p.get("reasoning", {}).get("top_risks") or ["None flagged"])[0],
        })

    all_actions = []
    for p in projects:
        all_actions.extend(p.get("reasoning", {}).get("recommended_actions", []))
    action_counter = Counter(all_actions)

    return {
        "generated_at": projects[0]["generated_at"] if projects else None,
        "n_projects": n,
        "rag_distribution": {"Red": rag_counts.get("Red", 0), "Amber": rag_counts.get("Amber", 0), "Green": rag_counts.get("Green", 0)},
        "avg_pct_complete": avg_pct,
        "recurring_themes": recurring_themes,
        "all_themes_ranked": all_theme_ranked,
        "projects": project_rows,
        "action_frequency": [{"action": a, "count": c} for a, c in action_counter.most_common()],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-dir", default="outputs")
    ap.add_argument("--out", default="synthesis.json")
    args = ap.parse_args()

    projects = load_latest_per_project(args.outputs_dir)
    if not projects:
        print(f"No weekly JSON outputs found in {args.outputs_dir}/. Run agent.py or weekly_run.py first.")
        return

    result = synthesize(projects)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"Synthesized {result['n_projects']} project(s) -> {args.out}")
    print(f"RAG distribution: {result['rag_distribution']}")
    print("Recurring cross-project themes:")
    for t in result["recurring_themes"]:
        print(f"  - {t['theme']} ({t['count']}x)")


if __name__ == "__main__":
    main()
