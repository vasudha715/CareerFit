import re

def normalize_skills(raw):
    if isinstance(raw, set):
        return {normalize_skill(x) for x in raw if normalize_skill(x)}
    return {normalize_skill(x) for x in (raw or "").split(",") if normalize_skill(x)}

def normalize_skill(value):
    return re.sub(r"\s+", " ", str(value).strip().lower())

def evaluate_eligibility(student, job):
    checks = []
    def add(label, actual, required, passed, detail):
        checks.append({"Criterion": label, "Student value": actual, "Company requirement": required,
                       "Result": "Matched" if passed is True else ("Not matched" if passed is False else "Missing information"),
                       "Explanation": detail, "_passed": passed})

    cgpa = student.get("cgpa")
    add("CGPA", cgpa, f">= {job['min_cgpa']}", None if cgpa is None else cgpa >= job["min_cgpa"],
        "Student CGPA meets the minimum." if cgpa is not None and cgpa >= job["min_cgpa"] else
        ("Student CGPA is below the minimum." if cgpa is not None else "CGPA is not available."))

    backlogs = student.get("active_backlogs")
    add("Active backlogs", backlogs, f"<= {job['max_active_backlogs']}", None if backlogs is None else backlogs <= job["max_active_backlogs"],
        "Backlog count is within the allowed limit." if backlogs is not None and backlogs <= job["max_active_backlogs"] else
        ("Backlog count exceeds the allowed limit." if backlogs is not None else "Backlog information is not available."))

    year = student.get("graduation_year")
    add("Graduation year", year, str(job["graduation_year"]), None if year is None else year == job["graduation_year"],
        "Graduation year matches." if year is not None and year == job["graduation_year"] else
        ("Graduation year does not match." if year is not None else "Graduation year is not available."))

    branch = (student.get("branch") or "").strip().upper()
    allowed = {x.strip().upper() for x in job["branches"].split(",")}
    branch_pass = None if not branch else ("ALL" in allowed or branch in allowed)
    add("Branch", branch or "Not provided", job["branches"], branch_pass,
        "Branch is eligible." if branch_pass is True else ("Branch is not listed as eligible." if branch_pass is False else "Branch is not available."))

    required = normalize_skills(job.get("required_skills",""))
    owned = normalize_skills(student.get("skills",""))
    missing = sorted(required - owned)
    if any(c["_passed"] is False for c in checks):
        decision = "Not eligible"
    elif any(c["_passed"] is None for c in checks):
        decision = "Needs profile information"
    else:
        decision = "Eligible"
    public_checks = [{k:v for k,v in c.items() if k != "_passed"} for c in checks]
    return {"decision": decision, "checks": public_checks, "missing_skills": missing,
            "matched_skills": sorted(required & owned), "required_skills": sorted(required)}

def skill_recommendations(missing):
    suggestions = {
        "python": "Study variables, conditions, loops, functions and basic problem solving; build small scripts.",
        "sql": "Practice SELECT, WHERE, JOIN, GROUP BY and aggregate queries using a sample database.",
        "dbms": "Revise keys, normalization, relationships, transactions and indexing.",
        "excel": "Practice formulas, sorting, filtering, lookup functions and pivot tables.",
        "data analysis": "Learn data cleaning, exploratory analysis and clear chart interpretation.",
        "communication": "Practice structured explanations, presentations and mock interviews.",
        "problem solving": "Solve beginner programming problems and explain your approach before coding.",
    }
    return [(skill, suggestions.get(skill, f"Learn the fundamentals of {skill} and complete a small practical exercise.")) for skill in missing]
