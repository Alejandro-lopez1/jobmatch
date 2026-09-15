import re
import uuid
from datetime import datetime, timezone

from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.models.schemas import ParsedCV, Job, MatchResult
from backend.config import MATCH_WEIGHTS, SKILL_LEVELS


class MatchService:
    def __init__(self):
        self.weights = MATCH_WEIGHTS
        self.edu_levels = SKILL_LEVELS

    def _skill_similarity(self, skill1: str, skill2: str) -> float:
        s1, s2 = skill1.lower().strip(), skill2.lower().strip()
        if s1 == s2:
            return 1.0
        if s1 in s2 or s2 in s1:
            return 0.9
        ratio = fuzz.ratio(s1, s2)
        if ratio >= 85:
            return ratio / 100.0
        tokens1 = set(s1.split())
        tokens2 = set(s2.split())
        if tokens1 and tokens2:
            intersection = tokens1.intersection(tokens2)
            if intersection:
                return len(intersection) / max(len(tokens1), len(tokens2))
        return 0.0

    def calculate_skills_match(self, cv_skills: list[str], job_skills: list[str]) -> tuple[float, list[str], list[str]]:
        if not job_skills:
            return 1.0, cv_skills.copy(), []

        matched = []
        missing = []
        for job_skill in job_skills:
            found = False
            for cv_skill in cv_skills:
                if self._skill_similarity(job_skill, cv_skill) >= 0.8:
                    matched.append(job_skill)
                    found = True
                    break
            if not found:
                missing.append(job_skill)

        score = len(matched) / len(job_skills) if job_skills else 0.0
        return score, matched, missing

    def calculate_experience_match(self, cv_years: float, required_years: float) -> float:
        if required_years <= 0:
            return 1.0
        if cv_years >= required_years:
            return 1.0
        return cv_years / required_years

    def calculate_education_match(self, cv_education: list[dict], job_education: str | None) -> float:
        if not job_education:
            return 1.0
        if not cv_education:
            return 0.0

        job_level = 0
        job_edu_lower = job_education.lower()
        for level_name, level_value in self.edu_levels.items():
            if level_name in job_edu_lower:
                job_level = level_value
                break

        cv_max_level = 0
        for edu in cv_education:
            degree = edu.get("degree", "").lower() if isinstance(edu, dict) else str(edu).lower()
            for level_name, level_value in self.edu_levels.items():
                if level_name in degree:
                    cv_max_level = max(cv_max_level, level_value)
                    break

        if cv_max_level >= job_level:
            return 1.0
        elif job_level > 0:
            return cv_max_level / job_level
        return 0.5

    def calculate_semantic_match(self, cv_text: str, job_text: str) -> float:
        if not cv_text or not job_text:
            return 0.0
        try:
            vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
            tfidf_matrix = vectorizer.fit_transform([cv_text, job_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(sim)
        except Exception:
            return 0.0

    def classify_match(self, score: float) -> str:
        if score >= 0.80:
            return "bueno"
        elif score >= 0.50:
            return "regular"
        return "no_match"

    def calculate_match(self, cv: ParsedCV, job: Job) -> MatchResult:
        cv_skills = cv.skills.technical
        job_skills = job.requirements.skills if job.requirements.skills else []

        if not job_skills and job.description:
            job_skills = self._extract_skills_from_description(job.description)

        skill_score, matched, missing = self.calculate_skills_match(cv_skills, job_skills)
        exp_score = self.calculate_experience_match(
            cv.experience.total_years, job.requirements.experience_years
        )
        edu_score = self.calculate_education_match(
            [e.dict() if hasattr(e, "dict") else e for e in cv.education],
            job.requirements.education,
        )
        semantic_score = self.calculate_semantic_match(cv.full_text, job.description)

        total = (
            skill_score * self.weights["skills"]
            + exp_score * self.weights["experience"]
            + edu_score * self.weights["education"]
            + semantic_score * self.weights["semantic"]
        )

        classification = self.classify_match(total)
        recommendations = self._generate_recommendations(missing, cv.experience.total_years, job.requirements.experience_years)

        return MatchResult(
            match_id=str(uuid.uuid4()),
            job=job,
            scores={
                "skills": round(skill_score, 3),
                "experience": round(exp_score, 3),
                "education": round(edu_score, 3),
                "semantic": round(semantic_score, 3),
                "total": round(total, 3),
            },
            classification=classification,
            matched_skills=matched,
            missing_skills=missing,
            recommendations=recommendations,
        )

    def _extract_skills_from_description(self, description: str) -> list[str]:
        skill_keywords = [
            "python", "javascript", "java", "sql", "aws", "docker", "kubernetes",
            "react", "node.js", "django", "fastapi", "flask", "git", "linux",
            "postgresql", "mysql", "mongodb", "redis", "html", "css", "typescript",
            "golang", "rust", "c++", "c#", "php", "ruby", "swift", "kotlin",
        ]
        found = []
        desc_lower = description.lower()
        for skill in skill_keywords:
            if skill in desc_lower:
                found.append(skill.title())
        return list(set(found))

    def _generate_recommendations(self, missing: list[str], cv_years: float, req_years: float) -> list[str]:
        recs = []
        if missing:
            recs.append(f"Considerar aprender: {', '.join(missing[:3])}")
        if cv_years < req_years:
            diff = req_years - cv_years
            recs.append(f"Te faltan {diff:.0f} años de experiencia requeridos")
        if not recs:
            recs.append("Excelente compatibilidad con la oferta")
        return recs

    def rank_jobs(self, cv: ParsedCV, jobs: list[Job]) -> list[MatchResult]:
        results = [self.calculate_match(cv, job) for job in jobs]
        results.sort(key=lambda x: x.scores["total"], reverse=True)
        return results
