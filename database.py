import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("careerfit.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, branch TEXT NOT NULL,
            cgpa REAL NOT NULL, active_backlogs INTEGER NOT NULL,
            graduation_year INTEGER NOT NULL, skills TEXT DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, company TEXT NOT NULL, role TEXT NOT NULL,
            min_cgpa REAL NOT NULL, max_active_backlogs INTEGER NOT NULL,
            graduation_year INTEGER NOT NULL, branches TEXT NOT NULL,
            required_skills TEXT DEFAULT '', description TEXT DEFAULT ''
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS eligibility_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, job_id INTEGER,
            decision TEXT NOT NULL, report_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER NOT NULL,
            job_id INTEGER NOT NULL, applied_on TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            UNIQUE(student_id, job_id)
        )""")
        c.commit()

def save_student(name,email,branch,cgpa,backlogs,year,skills):
    with connect() as c:
        existing = c.execute("SELECT id FROM students WHERE email=?", (email,)).fetchone()
        if existing:
            c.execute("""UPDATE students SET full_name=?,branch=?,cgpa=?,active_backlogs=?,graduation_year=?,skills=? WHERE email=?""",
                      (name,branch,cgpa,backlogs,year,skills,email))
        else:
            c.execute("""INSERT INTO students(full_name,email,branch,cgpa,active_backlogs,graduation_year,skills) VALUES(?,?,?,?,?,?,?)""",
                      (name,email,branch,cgpa,backlogs,year,skills))
        c.commit()

def get_student():
    with connect() as c:
        row = c.execute("SELECT * FROM students ORDER BY id LIMIT 1").fetchone()
        return dict(row) if row else None

def add_job(company,role,min_cgpa,max_backlogs,year,branches,skills,description):
    with connect() as c:
        c.execute("""INSERT INTO jobs(company,role,min_cgpa,max_active_backlogs,graduation_year,branches,required_skills,description)
                     VALUES(?,?,?,?,?,?,?,?)""",
                  (company,role,min_cgpa,max_backlogs,year,branches,skills,description))
        c.commit()

def get_jobs():
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM jobs ORDER BY id DESC").fetchall()]

def get_job(job_id):
    with connect() as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return dict(row) if row else None

def save_check_result(student_id,job_id,result):
    import json
    with connect() as c:
        c.execute("INSERT INTO eligibility_checks(student_id,job_id,decision,report_json) VALUES(?,?,?,?)",
                  (student_id,job_id,result["decision"],json.dumps(result)))
        c.commit()

def get_check_results():
    with connect() as c:
        return [dict(r) for r in c.execute("SELECT * FROM eligibility_checks ORDER BY id DESC").fetchall()]

def add_application(student_id,job_id,applied_on):
    with connect() as c:
        c.execute("INSERT OR IGNORE INTO applications(student_id,job_id,applied_on) VALUES(?,?,?)",
                  (student_id,job_id,applied_on))
        c.commit()

def get_applications(student_id=None):
    with connect() as c:
        sql = """SELECT a.*, j.company, j.role FROM applications a JOIN jobs j ON a.job_id=j.id"""
        args = ()
        if student_id is not None:
            sql += " WHERE a.student_id=?"
            args = (student_id,)
        sql += " ORDER BY a.id DESC"
        return [dict(r) for r in c.execute(sql,args).fetchall()]

def update_application(application_id,status):
    with connect() as c:
        c.execute("UPDATE applications SET status=? WHERE id=?", (status,application_id))
        c.commit()
