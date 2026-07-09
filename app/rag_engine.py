"""
rag_engine.py — deterministic RAG scoring, per the one-page methodology.
No LLM calls here on purpose: schedule slippage, milestone health, blockers-
from-structure, and existing-field priors are all things that should be
computed the same way every time, not vary by model sampling.
"""
from __future__ import annotations
from datetime import datetime
from dataclasses import dataclass, field

RAG_RANK = {"Green": 0, "Amber": 1, "Red": 2}
RANK_RAG = {v: k for k, v in RAG_RANK.items()}

BLOCKER_KEYWORDS = [
    "yet to receive", "pending", "awaiting", "blocked", "on hold",
    "escalat", "delay", "issue", "risk", "not received", "tbd",
    "depends on", "unresolved",
]

TODAY = datetime(2026, 7, 8)  # fixed "as of" date for reproducible sample runs


def worst(*colors: str) -> str:
    colors = [c for c in colors if c]
    if not colors:
        return "Green"
    return RANK_RAG[max(RAG_RANK.get(c, 0) for c in colors)]


def _normalize_existing(val):
    if val is None or (isinstance(val, float) and val != val):
        return None
    v = str(val).strip().capitalize()
    if v == "Yellow":
        return "Amber"
    if v in ("Green", "Amber", "Red"):
        return v
    return None


def score_schedule(row) -> tuple[str, str | None]:
    """Signal 1: schedule slippage from Variance / Critical / Total Float."""
    var = row.get("variance_days")
    critical = bool(row.get("critical"))
    float_days = row.get("total_float")

    if float_days is not None and float_days == float_days and float_days < 0:
        return "Red", f"Total float has gone negative ({float_days:.0f}d) — no schedule buffer left."

    if var is None or var != var:
        return "Green", None

    late = -var  # variance negative means finished/scheduled later than baseline
    if critical and late > 0:
        return "Red", f"Task is on the critical path and running {late:.0f}d behind baseline."
    if late > 10:
        return "Red", f"{late:.0f} days behind baseline schedule."
    if late >= 4:
        return "Amber", f"{late:.0f} days behind baseline schedule."
    return "Green", None


def score_milestone(row) -> tuple[str, str | None]:
    """Signal 2: task/milestone health from Status + % Complete vs elapsed time."""
    status = str(row.get("status") or "").strip()
    pct = row.get("pct_complete")

    if status in ("Completed", "Not Applicable"):
        return "Green", None
    if status == "On Hold":
        return "Red", "Task is on hold."
    if status == "Unknown":
        return "Green", None

    start, end = row.get("baseline_start") or row.get("start"), row.get("baseline_end") or row.get("end")
    if status == "Not Started":
        if start and (start - TODAY).days <= 5:
            return "Amber", f"Not started, planned start {start.date()} is imminent or has passed."
        return "Green", None

    # In Progress: compare % complete to expected progress for elapsed time
    if start and end and end > start and pct == pct:
        total = (end - start).days or 1
        elapsed = (TODAY - start).days
        expected = max(0.0, min(1.0, elapsed / total))
        gap = expected - float(pct)
        if gap > 0.20:
            return "Red", f"{pct*100:.0f}% complete vs ~{expected*100:.0f}% expected for elapsed time — stalled."
        if gap > 0:
            return "Amber", f"{pct*100:.0f}% complete vs ~{expected*100:.0f}% expected for elapsed time — slipping."
    return "Green", None


def score_blockers(row) -> tuple[str, str | None]:
    """Signal 3: blocker language in Status Comment / Comments."""
    text = " ".join(str(x) for x in [row.get("status_comment"), row.get("comments")] if x and x == x)
    if not text.strip():
        return "Green", None
    low = text.lower()
    hits = [k for k in BLOCKER_KEYWORDS if k in low]
    if not hits:
        return "Green", None
    strong = any(k in low for k in ["blocked", "escalat", "unresolved", "not received"])
    if strong:
        return "Red", text.strip()
    return "Amber", text.strip()


def score_existing_field(row) -> tuple[str, str | None]:
    """Signal 5: prior from Zycus's own Schedule Health / RAG column."""
    v = _normalize_existing(row.get("existing_rag"))
    if v is None:
        return "Green", None
    return v, None


def score_row(row) -> dict:
    s_sched, r_sched = score_schedule(row)
    s_mile, r_mile = score_milestone(row)
    s_block, r_block = score_blockers(row)
    s_exist, _ = score_existing_field(row)

    final = worst(s_sched, s_mile, s_block, s_exist)
    reasons = [r for r in [r_sched, r_mile, r_block] if r]
    if not reasons and s_exist in ("Amber", "Red"):
        reasons.append(f"Flagged {s_exist} in source Schedule Health/RAG field.")
    return {
        "rag": final,
        "signals": {"schedule": s_sched, "milestone": s_mile, "blockers": s_block, "existing_field": s_exist},
        "reasons": reasons,
    }


@dataclass
class Node:
    task: str
    level: int
    rag: str = "Green"
    reasons: list = field(default_factory=list)
    children: list = field(default_factory=list)
    status: str = ""
    pct_complete: float = None

    def rollup(self):
        """Worst-signal-wins: a node's RAG = worst of its own + all children."""
        child_colors = [c.rollup() for c in self.children]
        self.rag = worst(self.rag, *child_colors)
        return self.rag

    def to_dict(self):
        return {
            "task": self.task,
            "level": self.level,
            "status": self.status,
            "pct_complete": self.pct_complete,
            "rag": self.rag,
            "reasons": self.reasons,
            "children": [c.to_dict() for c in self.children],
        }


def build_tree(df) -> tuple[Node, Node]:
    """Outline (level column) -> tree, using row order + a level stack.

    Row 0 of a Zycus export is the overall project summary line (same level
    as, or one above, the actual phases) — it's returned separately as
    `project_row` so it doesn't get counted as a phase itself.
    """
    if len(df) == 0:
        empty = Node(task="(empty plan)", level=0)
        return empty, empty

    project_row_data = df.iloc[0]
    project_scored = score_row(project_row_data)
    project_row = Node(
        task=project_row_data["task"],
        level=int(project_row_data["level"]),
        status=str(project_row_data.get("status") or ""),
        pct_complete=project_row_data.get("pct_complete"),
        rag=project_scored["rag"],
        reasons=project_scored["reasons"],
    )

    root = Node(task="PROJECT ROOT", level=int(project_row_data["level"]) - 1)
    stack = [root]

    for _, row in df.iloc[1:].iterrows():
        scored = score_row(row)
        status = str(row.get("status") or "")
        node = Node(
            task=row["task"],
            level=int(row["level"]),
            status=status,
            pct_complete=row.get("pct_complete"),
        )
        if status in ("Completed", "Not Applicable"):
            node.rag = "Green"
        else:
            node.rag = scored["rag"]
            node.reasons = scored["reasons"]

        while stack and stack[-1].level >= node.level:
            stack.pop()
        if not stack:
            stack = [root]
        stack[-1].children.append(node)
        stack.append(node)

    root.rollup()
    project_row.rag = worst(project_row.rag, root.rag)
    return root, project_row


def summarize(project_row: Node, root: Node) -> dict:
    """Flatten to project + top-level phase summary for the reasoning layer."""
    phases = []
    for phase in root.children:
        red_tasks = _collect(phase, "Red")
        amber_tasks = _collect(phase, "Amber")
        phases.append({
            "phase": phase.task,
            "rag": phase.rag,
            "status": phase.status,
            "pct_complete": phase.pct_complete,
            "red_tasks": red_tasks[:8],
            "amber_tasks": amber_tasks[:8],
        })
    overall = worst(project_row.rag, root.rag)
    return {
        "project_rag": overall,
        "project_pct_complete": project_row.pct_complete,
        "phases": phases,
    }


def _collect(node: Node, color: str) -> list[dict]:
    out = []
    if node.rag == color and node.reasons:
        out.append({"task": node.task, "reasons": node.reasons})
    for c in node.children:
        out.extend(_collect(c, color))
    return out
