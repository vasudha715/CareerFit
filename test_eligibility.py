import unittest
from eligibility import evaluate_eligibility, normalize_skills

STUDENT = {"branch":"IT","cgpa":8.16,"active_backlogs":0,"graduation_year":2028,"skills":"Python, Excel, DBMS"}
JOB = {"min_cgpa":7.5,"max_active_backlogs":0,"graduation_year":2028,"branches":"IT,CSE","required_skills":"Python,SQL,DBMS"}

class EligibilityTests(unittest.TestCase):
    def test_eligible_academic_profile(self):
        result = evaluate_eligibility(STUDENT, JOB)
        self.assertEqual(result["decision"], "Eligible")
        self.assertEqual(result["missing_skills"], ["sql"])

    def test_low_cgpa_is_not_eligible(self):
        student = dict(STUDENT, cgpa=6.5)
        self.assertEqual(evaluate_eligibility(student, JOB)["decision"], "Not eligible")

    def test_missing_information_is_not_a_pass(self):
        student = dict(STUDENT, graduation_year=None)
        self.assertEqual(evaluate_eligibility(student, JOB)["decision"], "Needs profile information")

    def test_skill_normalization(self):
        self.assertEqual(normalize_skills("Python, SQL, python"), {"python","sql"})

if __name__ == "__main__":
    unittest.main()
