# Project Health Reporting Agent

## RAG (Red-Amber-Green) Methodology

### Objective

The objective of this framework is to automatically determine project health using a consistent, explainable, and auditable Red-Amber-Green (RAG) model. Deterministic business rules — not the LLM — calculate the RAG status. The LLM is used only to generate executive-friendly explanations of a status that has already been decided.

### Evaluation Criteria

| Signal | Green 🟢 | Amber 🟠 | Red 🔴 |
|---|---|---|---|
| **Schedule Slippage** (days behind baseline, from the Variance column) | ≤ 3 days late, or ahead of baseline | 4–10 days late | > 10 days late, OR a Critical-path task is late, OR Total Float has gone negative |
| **Milestone / Task Health** (% Complete vs. expected progress for elapsed time) | On track | Trailing expected progress by up to ~20 points | Trailing by > 20 points, task is On Hold, or Not Started past its planned start date |
| **Blockers** (Status Comment / Comments) | No blocker language detected | Comment flags a pending dependency with no stated deadline risk | Comment explicitly names a stuck dependency or unresolved external ask |
| **Stakeholder Sentiment** (inferred by the LLM from free-text comments) | Neutral-to-positive | Mild friction, unclear ownership | Explicit escalation or withheld sign-off |
| **Existing Zycus RAG / Schedule Health field** (if present in source data) | Green | Yellow | Red |

**Roll-up rule:** a phase or project is never healthier than its worst active (non-completed) child — worst-signal-wins, not an average.

### A Note on Budget

**Budget burn is not currently scored.** Neither sample project export (`Project_Plan_B.xlsx`, `S2P_Project.xlsx`) contains a cost or budget column, so rather than fabricate a threshold, this framework explicitly leaves budget out of v1 and flags its absence in each report's data-quality warnings. Once a Budget/Actual Cost field is available, it should be added as a sixth signal with equal weight to schedule and milestone health.

### Assumptions

- Dates are stored as Excel serial numbers and converted to real dates before scoring.
- Where an existing Schedule Health/RAG column already exists in the source file, it's treated as a strong prior — but can be overridden if the other signals disagree strongly (e.g. a Red status comment shouldn't be masked by a stale Green field).
- Malformed predecessor references (`#REF`) and `#UNPARSEABLE` cells are treated as data-quality warnings, not fatal errors.
- Stakeholder sentiment has no structured field in the source data, so it's inferred by the LLM from free-text comments rather than scored deterministically.

---
*This methodology is implemented in `app/rag_engine.py`. See `README.md` for how to run the agent.*
