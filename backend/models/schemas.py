from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PersonalInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class Skills(BaseModel):
    technical: list[str] = []
    soft: list[str] = []
    languages: list[str] = []


class Experience(BaseModel):
    total_years: float = 0
    positions: list[dict] = []


class Education(BaseModel):
    degree: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None


class ParsedCV(BaseModel):
    cv_id: str = ""
    parsed_at: datetime = None
    personal_info: PersonalInfo = PersonalInfo()
    skills: Skills = Skills()
    experience: Experience = Experience()
    education: list[Education] = []
    full_text: str = ""


class JobSalary(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None
    currency: str = "USD"
    period: str = "year"


class JobRequirements(BaseModel):
    skills: list[str] = []
    experience_years: float = 0
    education: Optional[str] = None


class Job(BaseModel):
    job_id: str = ""
    source: str = ""
    scraped_at: datetime = None
    title: str = ""
    company: str = ""
    location: str = ""
    url: str = ""
    description: str = ""
    salary: Optional[JobSalary] = None
    requirements: JobRequirements = JobRequirements()
    posted_date: Optional[str] = None
    is_remote: bool = False
    job_type: str = "fulltime"


class MatchResult(BaseModel):
    match_id: str = ""
    job: Job = None
    scores: dict = {}
    classification: str = ""
    matched_skills: list[str] = []
    missing_skills: list[str] = []
    recommendations: list[str] = []


class SearchQuery(BaseModel):
    query: str
    location: str = ""
    remote: bool = False
    job_type: Optional[str] = None
    results_wanted: int = 20
