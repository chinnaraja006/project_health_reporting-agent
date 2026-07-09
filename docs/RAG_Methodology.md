Project Health Reporting Agent

RAG (Red-Amber-Green) Methodology

Objective

The objective of this framework is to automatically determine project health using a consistent, explainable, and auditable Red-Amber-Green (RAG) model. Instead of relying entirely on AI, deterministic business rules are used to calculate the project status, while the LLM generates executive-friendly explanations and recommendations.


Evaluation Criteria 

Indicator

Green 🟢

Amber 🟠

Red   🔴

Schedule Slippage

≤ 5%  🟢

5–15% 🟠

> 15% 🔴

Budget Burn

≤ 90%  🟢

90–100% 🟠

> 100%  🔴

Milestone Health

All milestones on track  🟢

Minor milestone delays.  🟠

Critical milestone missed  🔴

Blockers

No blockers  🟢

Temporary blockers. 🟠

Critical blockers impacting delivery. 🔴

Stakeholder Sentiment

Positive  🟢

Neutral or mixed 🟠

Negative  🔴

Project Risks

Low  🟢

Medium 🟠

High. 🔴


Scoring Method

Each indicator contributes to the overall project health score.

Status   Score

Green    0

Amber    1

Red      2

The total score determines the final RAG status.

Total Score.  Final Status

0–2.           🟢 Green

3–5            🟠 Amber

6 or more      🔴 Red



AI Reasoning

After the RAG status is calculated, the Large Language Model generates:

* A plain-English explanation of the project health
* Key risks affecting delivery
* Recommended next actions for project managers and leadership

The AI does not determine the RAG status. It only explains the results produced by the deterministic scoring framework, ensuring consistency and explainability.


Assumptions

The framework assumes that project plans provide sufficient information about:

* Schedule progress
* Budget utilization
* Milestone completion
* Current blockers
* Stakeholder feedback
* Project risks

When certain information is unavailable, the system analyzes the available data and highlights any limitations in the generated report.


Handling Incomplete Data

The agent is designed to work with imperfect project plans.

Supported scenarios include:

* Missing budget information
* Missing milestone dates
* Empty stakeholder comments
* Invalid or inconsistent date formats
* Partially completed spreadsheets

Instead of failing, the system continues processing available information and generates a meaningful health assessment.
