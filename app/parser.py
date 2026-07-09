"""
parser.py — loads a Zycus-style project plan export (.xlsx) and normalizes it
into a flat DataFrame the rag_engine can score, regardless of which of the
two known export layouts (Project_Plan_B style / S2P_Project style) it is.

Handles messiness observed in real exports:
- #UNPARSEABLE placeholder cells
- Mislabeled/shifted header for the outline "level" (sometimes under 'Level',
  sometimes functionally stored in 'Ancestors')
- Variance stored as strings like "-2d" / "0" / "15d"
- Critical? stored as 1.0/NaN instead of booleans
- Excel serial date columns
- Missing Status Comment / Comments / RAG / Schedule Health columns
"""
from __future__ import annotations
import re
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

EXCEL_EPOCH = datetime(1899, 12, 30)


def _excel_to_date(val):
    try:
        if pd.isna(val):
            return None
        return EXCEL_EPOCH + timedelta(days=float(val))
    except (ValueError, TypeError):
        return None


def _parse_variance_days(val):
    """'-2d' -> -2, '0' -> 0, 15 -> 15, NaN -> None"""
    if pd.isna(val):
        return None
    s = str(val).strip()
    m = re.match(r"^(-?\d+(?:\.\d+)?)d?$", s)
    if m:
        return float(m.group(1))
    return None


def _detect_level_column(df: pd.DataFrame) -> str | None:
    if "Level" in df.columns and df["Level"].notna().any():
        return "Level"
    # Fallback: some exports mislabel the outline depth under 'Ancestors'
    if "Ancestors" in df.columns:
        vals = pd.to_numeric(df["Ancestors"], errors="coerce").dropna()
        if len(vals) > 0 and vals.between(0, 15).all():
            return "Ancestors"
    return None


def _first_present(df, *names):
    for n in names:
        if n in df.columns:
            return n
    return None


def load_plan(path: str) -> tuple[pd.DataFrame, dict]:
    """Returns (normalized_df, meta) where meta carries data-quality warnings."""
    raw = pd.read_excel(path)
    warnings = []

    level_col = _detect_level_column(raw)
    if level_col is None:
        warnings.append("No usable hierarchy/level column found — treating all rows as flat (level 1).")
        level = pd.Series([1] * len(raw))
    else:
        level = pd.to_numeric(raw[level_col], errors="coerce").ffill().fillna(0).astype(int)

    rag_col = _first_present(raw, "RAG")
    health_col = _first_present(raw, "Schedule Health")
    comment_col = _first_present(raw, "Status Comment")
    comments_col = _first_present(raw, "Comments")
    baseline_start_col = _first_present(raw, "Baseline Start Date", "Baseline Start")
    baseline_end_col = _first_present(raw, "Baseline End Date", "Baseline Finish")

    n_unparseable = 0
    for col in raw.columns:
        n_unparseable += (raw[col].astype(str) == "#UNPARSEABLE").sum()
    if n_unparseable:
        warnings.append(f"{n_unparseable} '#UNPARSEABLE' cells found in source export — ignored, not treated as errors.")

    n_ref = 0
    if "Predecessors" in raw.columns:
        n_ref = raw["Predecessors"].astype(str).str.contains("#REF", na=False).sum()
    if n_ref:
        warnings.append(f"{n_ref} broken predecessor links (#REF) found — dependency chain may be unreliable for those tasks.")

    out = pd.DataFrame({
        "level": level,
        "task": raw.get("Task Name", pd.Series([""] * len(raw))).fillna("(unnamed task)"),
        "status": raw.get("Status", pd.Series([np.nan] * len(raw))).fillna("Unknown"),
        "pct_complete": pd.to_numeric(raw.get("% Complete"), errors="coerce"),
        "start": raw.get("Start Date", raw.get("Start")).apply(_excel_to_date) if _first_present(raw, "Start Date", "Start") else None,
        "end": raw.get("End Date", raw.get("Finish")).apply(_excel_to_date) if _first_present(raw, "End Date", "Finish") else None,
        "baseline_start": raw[baseline_start_col].apply(_excel_to_date) if baseline_start_col else None,
        "baseline_end": raw[baseline_end_col].apply(_excel_to_date) if baseline_end_col else None,
        "variance_days": raw.get("Variance").apply(_parse_variance_days) if "Variance" in raw.columns else None,
        "total_float": pd.to_numeric(raw.get("Total Float"), errors="coerce"),
        "critical": raw.get("Critical ?").notna() if "Critical ?" in raw.columns else False,
        "on_hold": raw.get("On Hold?").fillna(False).astype(bool) if "On Hold?" in raw.columns else False,
        "priority": raw.get("Priority"),
        "owner": raw.get("Owner"),
        "assigned_to": raw.get("Assigned To"),
        "status_comment": raw[comment_col] if comment_col else None,
        "comments": raw[comments_col] if comments_col else None,
        "existing_rag": (raw[rag_col] if rag_col else raw[health_col] if health_col else pd.Series([None] * len(raw))),
    })

    meta = {
        "n_rows": len(out),
        "level_source_column": level_col or "(none — flat fallback)",
        "warnings": warnings,
        "project_name": str(raw.get("Project Name", pd.Series([""])).dropna().iloc[0]) if "Project Name" in raw.columns and raw["Project Name"].notna().any() else (out["task"].iloc[0] if len(out) else "Unknown Project"),
        "project_manager": str(raw.get("Project Manager", pd.Series(["Unknown"])).dropna().iloc[0]) if "Project Manager" in raw.columns and raw["Project Manager"].notna().any() else "Unknown",
    }
    return out, meta
