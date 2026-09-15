from fastapi import APIRouter, HTTPException

from backend.models.schemas import SearchQuery, MatchResult, ParsedCV
from backend.services.job_scraper import JobSearchService
from backend.services.matcher import MatchService

router = APIRouter(prefix="/jobs", tags=["Jobs"])
_scraper = JobSearchService()
_matcher = MatchService()

_current_cv: ParsedCV | None = None


@router.post("/set-cv")
async def set_cv(cv: ParsedCV):
    global _current_cv
    _current_cv = cv
    return {"status": "ok", "skills": cv.skills.technical}


@router.post("/search", response_model=list[MatchResult])
async def search_jobs(query: SearchQuery):
    if not _current_cv:
        raise HTTPException(400, "Primero sube un CV con POST /cv/upload")

    try:
        jobs = _scraper.search_all(
            query=query.query,
            location=query.location,
            results_wanted=query.results_wanted,
        )
        if not jobs:
            return []

        results = _matcher.rank_jobs(_current_cv, jobs)
        return results
    except Exception as e:
        raise HTTPException(500, f"Error en la búsqueda: {str(e)}")


@router.get("/sources")
async def get_sources():
    return {
        "jobspy": "Indeed, LinkedIn, Glassdoor, Google",
        "adzuna": "API global (requiere API key)",
        "jsearch": "Google for Jobs (requiere RapidAPI key)",
    }
