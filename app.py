import streamlit as st
import pandas as pd
from database import (
    init_db, save_student, get_student, add_job, get_jobs, get_job,
    save_check_result, get_check_results, add_application,
    get_applications, update_application
)
from eligibility import evaluate_eligibility, normalize_skills, skill_recommendations

st.set_page_config(page_title="CareerFit | Placement Readiness", page_icon="🎯", layout="wide")
init_db()

st.markdown("""
<style>
.block-container {padding-top:1.5rem; padding-bottom:2rem;}
.hero {padding:1.35rem 1.5rem; border-radius:16px; background:linear-gradient(115deg,#142d4e,#286b91); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e7f2fb; margin:.35rem 0 0;}
div[data-testid="stMetric"] {background:white; border:1px solid #e7edf4; padding:12px; border-radius:12px;}
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🎯 CareerFit</h1><p>Placement Readiness & Job Eligibility Intelligence Platform</p></div>', unsafe_allow_html=True)

# Seed realistic sample jobs once, so the application can be demonstrated immediately.
if not get_jobs():
    add_job("Junior Software Engineer", "TechNova", 7.0, 0, 2028, "IT,CSE,ECE", "Python,SQL,DBMS,Problem Solving", "Knowledge of programming fundamentals and databases.")
    add_job("Data Analyst Intern", "DataBridge", 7.5, 0, 2028, "IT,CSE,ECE,EEE", "Python,SQL,Excel,Data Analysis", "Basic data cleaning, analysis and reporting skills.")
    add_job("Graduate Engineer Trainee", "CoreSystems", 6.5, 1, 2028, "ALL", "Communication,Python,SQL", "Open to eligible engineering branches.")

page = st.sidebar.radio("Navigation", [
    "Dashboard", "My Student Profile", "Explore Jobs & Check Eligibility",
    "Skill Gap & Learning Plan", "Application Tracker", "Project Guide"
])
st.sidebar.caption("CareerFit • Local working prototype")

student = get_student()
jobs = get_jobs()

if page == "Dashboard":
    st.subheader("Placement readiness dashboard")
    if student:
        st.write(f"Welcome, **{student['full_name']}**")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("CGPA", f"{student['cgpa']:.2f}")
        c2.metric("Graduation year", student["graduation_year"])
        c3.metric("Skills listed", len(normalize_skills(student["skills"])))
        c4.metric("Jobs available", len(jobs))
        st.markdown("### Your profile snapshot")
        st.write(f"**Branch:** {student['branch']}  ·  **Active backlogs:** {student['active_backlogs']}")
        st.write(f"**Skills:** {student['skills'] or 'No skills added'}")
    else:
        st.info("Create your student profile first from **My Student Profile**.")
        st.write("CareerFit helps students compare their academic and technical profiles with company placement requirements.")
    apps = get_applications()
    checks = get_check_results()
    a,b = st.columns(2)
    a.metric("Eligibility checks performed", len(checks))
    b.metric("Applications tracked", len(apps))
    if jobs:
        st.markdown("### Available sample opportunities")
        st.dataframe(pd.DataFrame(jobs)[["company","role","min_cgpa","max_active_backlogs","graduation_year","branches"]], use_container_width=True, hide_index=True)

elif page == "My Student Profile":
    st.subheader("Student profile")
    st.write("Enter accurate information. The eligibility checker uses these details.")
    defaults = student or {}
    with st.form("profile_form"):
        name = st.text_input("Full name *", value=defaults.get("full_name",""))
        email = st.text_input("Email *", value=defaults.get("email",""))
        x1,x2,x3 = st.columns(3)
        with x1: branch = st.selectbox("Branch", ["IT","CSE","ECE","EEE","MECH","CIVIL","Other"], index=(["IT","CSE","ECE","EEE","MECH","CIVIL","Other"].index(defaults.get("branch","IT")) if defaults.get("branch","IT") in ["IT","CSE","ECE","EEE","MECH","CIVIL","Other"] else 0))
        with x2: cgpa = st.number_input("CGPA (0–10)", min_value=0.0, max_value=10.0, value=float(defaults.get("cgpa",8.0)), step=0.01)
        with x3: year = st.number_input("Graduation year", min_value=2025, max_value=2035, value=int(defaults.get("graduation_year",2028)), step=1)
        backlogs = st.number_input("Current active backlogs", min_value=0, max_value=30, value=int(defaults.get("active_backlogs",0)), step=1)
        skills = st.text_area("Technical and professional skills (comma-separated)", value=defaults.get("skills","Python, Excel, DBMS"), placeholder="Python, SQL, Communication, Excel")
        submitted = st.form_submit_button("Save student profile", type="primary")
    if submitted:
        if not name.strip() or not email.strip() or "@" not in email:
            st.error("Enter your name and a valid email address.")
        else:
            save_student(name.strip(), email.strip().lower(), branch, float(cgpa), int(backlogs), int(year), skills.strip())
            st.success("Profile saved successfully.")
            st.rerun()

elif page == "Explore Jobs & Check Eligibility":
    st.subheader("Explore opportunities")
    if not student:
        st.warning("Save your student profile before checking eligibility.")
    else:
        st.markdown("### Available jobs")
        if jobs:
            job_df = pd.DataFrame(jobs)
            st.dataframe(job_df[["id","company","role","min_cgpa","max_active_backlogs","graduation_year","branches","required_skills"]], use_container_width=True, hide_index=True)
            selected_id = st.selectbox("Choose a job to evaluate", [j["id"] for j in jobs], format_func=lambda i: f"{next(j['company']+' — '+j['role'] for j in jobs if j['id']==i)} (Job #{i})")
            job = get_job(selected_id)
            result = evaluate_eligibility(student, job)
            if st.button("Check my eligibility", type="primary", use_container_width=True):
                save_check_result(student["id"], job["id"], result)
                st.session_state["last_result"] = {"job_id": job["id"], "result": result}
            last = st.session_state.get("last_result")
            if last and last["job_id"] == job["id"]:
                result = last["result"]
                st.markdown("### Eligibility report")
                if result["decision"] == "Eligible":
                    st.success("You meet all specified mandatory eligibility criteria.")
                elif result["decision"] == "Not eligible":
                    st.error("One or more mandatory criteria are not satisfied.")
                else:
                    st.warning("Eligibility cannot be confirmed because some required profile information is missing.")
                st.write(f"**Decision:** {result['decision']}")
                report = pd.DataFrame(result["checks"])
                st.dataframe(report, use_container_width=True, hide_index=True)
                st.caption("The system distinguishes a failed criterion from information that has not been provided.")
                st.markdown("### Skill comparison")
                st.write("**Missing skills:** " + (", ".join(result["missing_skills"]) if result["missing_skills"] else "None identified"))
        st.divider()
        st.markdown("### Add a placement opportunity")
        with st.form("job_form"):
            j1,j2 = st.columns(2)
            with j1:
                company = st.text_input("Company name")
                role = st.text_input("Job role")
                min_cgpa = st.number_input("Minimum CGPA", min_value=0.0, max_value=10.0, value=7.0, step=0.1)
            with j2:
                max_backlogs = st.number_input("Maximum active backlogs allowed", min_value=0, max_value=20, value=0)
                grad_year = st.number_input("Eligible graduation year", min_value=2025, max_value=2035, value=2028)
                branches = st.text_input("Eligible branches (comma-separated; ALL for all)", value="IT,CSE")
            required_skills = st.text_input("Required skills (comma-separated)", value="Python,SQL,DBMS")
            description = st.text_area("Additional description")
            add = st.form_submit_button("Add job")
        if add:
            if company.strip() and role.strip():
                add_job(company.strip(), role.strip(), float(min_cgpa), int(max_backlogs), int(grad_year), branches.strip(), required_skills.strip(), description.strip())
                st.success("Job opportunity added.")
                st.rerun()
            else:
                st.error("Company and role are required.")

elif page == "Skill Gap & Learning Plan":
    st.subheader("Skill gap analysis")
    if not student:
        st.warning("Create your student profile first.")
    elif not jobs:
        st.info("No jobs available.")
    else:
        selected_id = st.selectbox("Choose a target job", [j["id"] for j in jobs], format_func=lambda i: f"{next(j['company']+' — '+j['role'] for j in jobs if j['id']==i)}")
        job = get_job(selected_id)
        student_skills = normalize_skills(student["skills"])
        required = normalize_skills(job["required_skills"])
        missing = sorted(required - student_skills)
        matched = sorted(required & student_skills)
        x,y,z = st.columns(3)
        x.metric("Required skills", len(required))
        y.metric("Skills matched", len(matched))
        z.metric("Skills to develop", len(missing))
        st.write("**Already listed:** " + (", ".join(matched) if matched else "None"))
        st.write("**Skills to develop:** " + (", ".join(missing) if missing else "No skill gaps found for this job."))
        recommendations = skill_recommendations(missing)
        if recommendations:
            st.markdown("### Suggested learning priorities")
            for skill, suggestion in recommendations:
                st.markdown(f"- **{skill.title()}** — {suggestion}")
        st.caption("Recommendations are general starting points. They are not a guarantee of job selection.")

elif page == "Application Tracker":
    st.subheader("Placement application tracker")
    if not student:
        st.warning("Create your student profile first.")
    else:
        with st.form("application_form"):
            job_ids = [j["id"] for j in jobs]
            chosen = st.selectbox("Job opportunity", job_ids, format_func=lambda i: f"{next(j['company']+' — '+j['role'] for j in jobs if j['id']==i)}")
            applied_on = st.date_input("Application date")
            add_app = st.form_submit_button("Add application")
        if add_app:
            add_application(student["id"], chosen, str(applied_on))
            st.success("Application added to your tracker.")
            st.rerun()
        apps = get_applications(student["id"])
        if apps:
            st.markdown("### Your applications")
            for app in apps:
                with st.expander(f"{app['company']} — {app['role']} | {app['status']}"):
                    st.write(f"Applied on: {app['applied_on']}")
                    new_status = st.selectbox("Update status", ["Applied","Assessment","Interview","Selected","Rejected","Withdrawn"], index=["Applied","Assessment","Interview","Selected","Rejected","Withdrawn"].index(app["status"]), key=f"status_{app['id']}")
                    if st.button("Save status", key=f"save_{app['id']}"):
                        update_application(app["id"], new_status)
                        st.success("Application status updated.")
                        st.rerun()
        else:
            st.info("No applications tracked yet.")

elif page == "Project Guide":
    st.subheader("How CareerFit works")
    st.markdown("""
    **System workflow**
    1. Student creates a profile with branch, CGPA, backlogs, graduation year and skills.
    2. Placement opportunities are entered with company requirements.
    3. The eligibility engine compares each mandatory criterion independently.
    4. The report shows Matched, Not matched or Missing information.
    5. Required skills are compared with the student's listed skills.
    6. A learning plan suggests what to work on, and students can track applications.

    **Eligibility logic**
    - CGPA must be greater than or equal to the company's minimum.
    - Active backlogs must be less than or equal to the allowed maximum.
    - Graduation year must match the specified year.
    - Branch must be included in the eligible branches, unless the company specifies ALL.
    - A missing profile value is not automatically treated as a pass.

    **Technology**
    - Python: business rules and data processing.
    - Streamlit: interactive web interface.
    - SQLite: persistent relational database.
    - Pandas: displaying and filtering structured reports.

    **Limitations**
    - Job requirements are entered manually in this version.
    - Skills are compared by normalized text labels, not semantic AI.
    - The prototype does not verify claims in a student's profile.
    - It has no authentication or multi-user access control yet.
    - It does not guarantee recruitment or selection.
    """)
    st.markdown("### Suggested demonstration")
    st.code("1. Create a student profile.\n2. Open Explore Jobs and select a sample company.\n3. Run the eligibility check and explain each criterion.\n4. Open Skill Gap and Learning Plan.\n5. Add an application and update its status in Application Tracker.")
