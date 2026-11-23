# CareerFit — Placement Readiness & Job Eligibility Intelligence Platform

A working individual project prototype using Python, Streamlit, SQLite and Pandas.

## Run on Windows
Open this folder in VS Code. In the terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

If PowerShell blocks activation:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

If `python` is not recognized, try replacing `python` with `py`.

## Features
- Create and update one student profile
- Store academic details and comma-separated skills
- Browse preloaded sample jobs and add new opportunities
- Compare CGPA, active backlogs, graduation year and branch
- Explain each eligibility criterion as Matched, Not matched or Missing information
- Compare required skills with student skills
- Generate a learning-priority suggestion list
- Track applications and update their statuses
- Persist information in SQLite

## Demo scenario
The app starts with three sample opportunities. Create a student profile with:
- Branch: IT
- CGPA: 8.16
- Active backlogs: 0
- Graduation year: 2028
- Skills: Python, Excel, DBMS

Check the Junior Software Engineer sample job. The expected result is academically eligible, with SQL listed as a missing skill. Then open Skill Gap & Learning Plan, add the job to Application Tracker and change its status.

## Architecture
- `app.py`: Streamlit screens and user interactions.
- `database.py`: SQLite schema and database operations.
- `eligibility.py`: eligibility rules, skill comparison and recommendations.
- `test_eligibility.py`: automated tests for core rules.

## Core logic
Academic eligibility is determined by explicit comparisons:
- CGPA >= minimum CGPA
- Active backlogs <= maximum allowed
- Graduation year equals the specified year
- Branch belongs to the allowed branch list, unless `ALL` is specified

The system returns `Eligible`, `Not eligible`, or `Needs profile information`. Missing information is not silently treated as a pass.

Skills are normalized to lowercase and compared as sets. The missing skills are the required skills not present in the student's profile.

## Honest limitations
This prototype uses manually entered job requirements and deterministic rules. It does not parse PDFs, use an LLM, verify student claims, or predict hiring outcomes. It has no authentication or role-based access control and is intended for a local demonstration with sample data, not real sensitive student records.

## Future improvements
PDF job-description extraction, secure authentication, placement-officer roles, audit history, REST API, Flutter client, skill ontology and explainable AI-assisted recommendations.
