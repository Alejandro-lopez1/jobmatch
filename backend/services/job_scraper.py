import uuid
from datetime import datetime, timezone

import httpx
from jobspy import scrape_jobs

from backend.models.schemas import Job, JobSalary, JobRequirements
from backend.config import ADZUNA_APP_ID, ADZUNA_APP_KEY, JSEARCH_API_KEY


class JobSearchService:
    def search_jobspy(
        self,
        query: str,
        location: str = "",
        results_wanted: int = 20,
        country: str = "USA",
    ) -> list[Job]:
        try:
            kwargs = {
                "site_name": ["indeed", "linkedin", "glassdoor", "google"],
                "search_term": query,
                "results_wanted": results_wanted,
                "country_indeed": country,
            }
            if location:
                kwargs["location"] = location

            df = scrape_jobs(**kwargs)
            if df is None or df.empty:
                return []

            jobs = []
            for _, row in df.iterrows():
                salary = None
                if row.get("min_amount") or row.get("max_amount"):
                    salary = JobSalary(
                        min=row.get("min_amount"),
                        max=row.get("max_amount"),
                        currency=row.get("currency", "USD"),
                        period=row.get("interval", "year"),
                    )

                jobs.append(
                    Job(
                        job_id=str(uuid.uuid4()),
                        source=row.get("site", "jobspy"),
                        scraped_at=datetime.now(timezone.utc),
                        title=row.get("title", ""),
                        company=row.get("company", ""),
                        location=row.get("location", ""),
                        url=row.get("job_url", ""),
                        description=row.get("description", "")[:2000] if row.get("description") else "",
                        salary=salary,
                        is_remote="remote" in str(row.get("location", "")).lower(),
                        job_type=row.get("job_type", "fulltime"),
                    )
                )
            return jobs
        except Exception as e:
            print(f"[JobSpy] Error: {e}")
            return []

    def search_adzuna(
        self,
        query: str,
        location: str = "",
        results_wanted: int = 20,
        country: str = "us",
    ) -> list[Job]:
        if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
            return []

        try:
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": min(results_wanted, 50),
                "what": query,
                "content-type": "application/json",
            }
            if location:
                params["where"] = location

            response = httpx.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for item in data.get("results", []):
                salary = None
                if item.get("salary_min") or item.get("salary_max"):
                    salary = JobSalary(
                        min=item.get("salary_min"),
                        max=item.get("salary_max"),
                        currency="USD",
                    )

                jobs.append(
                    Job(
                        job_id=str(uuid.uuid4()),
                        source="adzuna",
                        scraped_at=datetime.now(timezone.utc),
                        title=item.get("title", ""),
                        company=item.get("company", {}).get("display_name", ""),
                        location=item.get("location", {}).get("display_name", ""),
                        url=item.get("redirect_url", ""),
                        description=item.get("description", "")[:2000],
                        salary=salary,
                    )
                )
            return jobs
        except Exception as e:
            print(f"[Adzuna] Error: {e}")
            return []

    def search_jsearch(
        self,
        query: str,
        location: str = "",
        results_wanted: int = 20,
    ) -> list[Job]:
        if not JSEARCH_API_KEY:
            return []

        try:
            url = "https://jsearch.p.rapidapi.com/search"
            params = {
                "query": f"{query} in {location}" if location else query,
                "page": "1",
                "num_pages": "1",
                "results_wanted": str(min(results_wanted, 50)),
            }
            headers = {
                "X-RapidAPI-Key": JSEARCH_API_KEY,
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            }

            response = httpx.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            jobs = []
            for item in data.get("data", []):
                salary = None
                if item.get("job_min_salary") or item.get("job_max_salary"):
                    salary = JobSalary(
                        min=item.get("job_min_salary"),
                        max=item.get("job_max_salary"),
                        currency=item.get("job_salary_currency", "USD"),
                        period=item.get("job_salary_period", "YEAR").lower(),
                    )

                jobs.append(
                    Job(
                        job_id=str(uuid.uuid4()),
                        source="jsearch",
                        scraped_at=datetime.now(timezone.utc),
                        title=item.get("job_title", ""),
                        company=item.get("employer_name", ""),
                        location=item.get("job_city", "") + ", " + item.get("job_country", ""),
                        url=item.get("job_apply_link", ""),
                        description=item.get("job_description", "")[:2000] if item.get("job_description") else "",
                        salary=salary,
                        is_remote=item.get("job_is_remote", False),
                    )
                )
            return jobs
        except Exception as e:
            print(f"[JSearch] Error: {e}")
            return []

    def search_all(
        self,
        query: str,
        location: str = "",
        results_wanted: int = 20,
    ) -> list[Job]:
        all_jobs = []
        all_jobs.extend(self.search_jobspy(query, location, results_wanted))
        all_jobs.extend(self.search_adzuna(query, location, results_wanted))
        all_jobs.extend(self.search_jsearch(query, location, results_wanted))

        unique_jobs = self._deduplicate(all_jobs)
        return unique_jobs

    def _deduplicate(self, jobs: list[Job]) -> list[Job]:
        seen = set()
        unique = []
        for job in jobs:
            key = (job.title.lower().strip(), job.company.lower().strip())
            if key not in seen:
                seen.add(key)
                unique.append(job)
        return unique
