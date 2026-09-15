import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.matcher import MatchService
from backend.models.schemas import ParsedCV, PersonalInfo, Skills, Experience, Education, Job, JobSalary, JobRequirements


class TestMatcher:
    def setup_method(self):
        self.matcher = MatchService()

    def test_skill_exact_match(self):
        cv_skills = ["Python", "SQL", "AWS"]
        job_skills = ["Python", "SQL"]
        score, matched, missing = self.matcher.calculate_skills_match(cv_skills, job_skills)
        assert score == 1.0
        assert matched == ["Python", "SQL"]
        assert missing == []

    def test_skill_partial_match(self):
        cv_skills = ["Python", "AWS"]
        job_skills = ["Python", "Django", "PostgreSQL"]
        score, matched, missing = self.matcher.calculate_skills_match(cv_skills, job_skills)
        assert score == 1/3
        assert matched == ["Python"]
        assert set(missing) == {"Django", "PostgreSQL"}

    def test_skill_no_job_skills(self):
        cv_skills = ["Python"]
        job_skills = []
        score, matched, missing = self.matcher.calculate_skills_match(cv_skills, job_skills)
        assert score == 1.0

    def test_skill_fuzzy_match(self):
        cv_skills = ["JavaScript", "PostgreSQL"]
        job_skills = ["JS", "Postgres"]
        score, matched, missing = self.matcher.calculate_skills_match(cv_skills, job_skills)
        # JS -> JavaScript = 0.67, Postgres -> PostgreSQL = 0.82
        # Ambos deberían matchar con threshold 0.8
        assert score >= 0.5

    def test_experience_match_sufficient(self):
        assert self.matcher.calculate_experience_match(5, 3) == 1.0
        assert self.matcher.calculate_experience_match(3, 3) == 1.0

    def test_experience_match_insufficient(self):
        assert self.matcher.calculate_experience_match(2, 4) == 0.5
        assert self.matcher.calculate_experience_match(0, 5) == 0.0

    def test_experience_match_zero_required(self):
        assert self.matcher.calculate_experience_match(0, 0) == 1.0
        assert self.matcher.calculate_experience_match(5, 0) == 1.0

    def test_education_match_same(self):
        cv_edu = [{"degree": "bachelor"}]
        assert self.matcher.calculate_education_match(cv_edu, "bachelor") == 1.0

    def test_education_match_higher(self):
        cv_edu = [{"degree": "master"}]
        assert self.matcher.calculate_education_match(cv_edu, "bachelor") == 1.0

    def test_education_match_lower(self):
        cv_edu = [{"degree": "bachelor"}]
        assert self.matcher.calculate_education_match(cv_edu, "master") == 0.75

    def test_education_no_cv(self):
        assert self.matcher.calculate_education_match([], "bachelor") == 0.0

    def test_education_no_job_req(self):
        cv_edu = [{"degree": "bachelor"}]
        assert self.matcher.calculate_education_match(cv_edu, None) == 1.0

    def test_classify_bueno(self):
        assert self.matcher.classify_match(0.80) == "bueno"
        assert self.matcher.classify_match(1.0) == "bueno"
        assert self.matcher.classify_match(0.95) == "bueno"

    def test_classify_regular(self):
        assert self.matcher.classify_match(0.50) == "regular"
        assert self.matcher.classify_match(0.75) == "regular"
        assert self.matcher.classify_match(0.79) == "regular"

    def test_classify_no_match(self):
        assert self.matcher.classify_match(0.49) == "no_match"
        assert self.matcher.classify_match(0.0) == "no_match"

    def test_full_match_integration(self):
        cv = ParsedCV(
            cv_id="test",
            personal_info=PersonalInfo(name="Test"),
            skills=Skills(technical=["Python", "SQL", "AWS", "Docker"]),
            experience=Experience(total_years=5),
            education=[Education(degree="bachelor")],
            full_text="Python developer with 5 years experience in AWS and Docker"
        )

        job = Job(
            job_id="test",
            title="Python Developer",
            company="Test Corp",
            location="Madrid",
            description="We need Python developer with AWS and Docker experience",
            requirements=JobRequirements(
                skills=["Python", "AWS", "Docker", "Kubernetes"],
                experience_years=3,
                education="bachelor"
            )
        )

        result = self.matcher.calculate_match(cv, job)

        assert result.scores["total"] > 0.7
        assert result.classification == "bueno"
        assert "Python" in result.matched_skills
        assert "AWS" in result.matched_skills
        assert "Docker" in result.matched_skills
        assert "Kubernetes" in result.missing_skills


class TestCVSchemas:
    def test_parsed_cv_creation(self):
        cv = ParsedCV(
            cv_id="test",
            personal_info=PersonalInfo(name="Juan", email="juan@test.com"),
            skills=Skills(technical=["Python", "JavaScript"]),
            experience=Experience(total_years=3),
            education=[Education(degree="bachelor", institution="Uni")],
            full_text="test"
        )
        assert cv.personal_info.name == "Juan"
        assert "Python" in cv.skills.technical

    def test_job_creation(self):
        job = Job(
            job_id="test",
            title="Python Dev",
            company="Acme",
            location="Madrid",
            requirements=JobRequirements(skills=["Python"], experience_years=2)
        )
        assert job.title == "Python Dev"
        assert job.requirements.experience_years == 2


class TestCache:
    def test_cache_init(self):
        from backend.services.cache_service import init_db, get_connection
        init_db()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "cv_cache" in tables
        assert "job_cache" in tables
        assert "search_history" in tables
        conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])