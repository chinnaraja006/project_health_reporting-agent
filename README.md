Project Health Reporting Agent

AI-powered project health reporting system developed for the Zycus AI Engineer Intern Technical Assignment.


Features

* Reads project plans from Excel (.xlsx/.xlsm)
* Determines project health using a deterministic RAG scoring framework
* Generates plain-English reasoning using an LLM
* Handles incomplete or messy project data gracefully
* Produces weekly project health reports
* Generates monthly portfolio insights across multiple projects
* Automatically creates an executive PowerPoint presentation
* Exposes REST APIs using FastAPI for easy integration



Project Structure

project_health_agent/
├── api.py
├── agent.py
├── weekly_run.py
├── monthly_synthesis.py
├── make_deck.js
├── requirements.txt
├── package.json
│
├── app/
│   ├── parser.py
│   ├── rag_engine.py
│   ├── llm_reasoning.py
│   └── report_generator.py
│
├── docs/
│   └── RAG_Methodology.md
│
├── data/
│
└── outputs/

Architecture

Project Plan (Excel)
          │
          ▼
   Project Parser
          │
          ▼
 Structured Project Data
          │
 ┌────────┴────────┐
 ▼                 ▼
RAG Engine     LLM Reasoning
 │                 │
 └────────┬────────┘
          ▼
 Weekly Project Report
          │
          ▼
 Monthly Portfolio Analysis
          │
          ▼
 Executive Presentation

 Installation

Clone the repository:
git clone <repository-url>
cd project_health_agent
Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate
Install dependencies:
pip install -r requirements.txt

Running the Project

Analyze a Project Plan (CLI)
python agent.py data/Project_Plan_B.xlsx
python agent.py data/S2P_Project.xlsx

Start the REST API
uvicorn api:app --reload

API documentation:
http://127.0.0.1:8000/docs

Generate Weekly Reports
python weekly_run.py

Generate Monthly Portfolio Summary
python monthly_synthesis.py

Generate Executive Presentation
node make_deck.js

RAG Framework

The project health score is calculated using deterministic business rules based on:

* Schedule slippage
* Budget utilization
* Milestone completion
* Project blockers
* Stakeholder sentiment
* Overall project risks

The LLM is used only to generate executive-friendly explanations and recommendations.
 It does not determine the project status.

 Handling Incomplete Data

The system is designed to handle imperfect project plans, including:

* Missing values
* Empty fields
* Invalid dates
* Inconsistent formatting
* Partial project information

When important information is unavailable, 
the agent still produces a report while indicating reduced confidence where appropriate.


Technologies Used

* Python
* FastAPI
* Pandas
* OpenAI / OpenRouter
* JavaScript
* PowerPoint generation libraries


Author

Chinnaraja S

AI Engineer Intern Technical Assignment – Zycus