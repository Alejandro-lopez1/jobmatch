import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")
JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "")
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "service_account.json")
GOOGLE_SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "JobMatch Results")

MATCH_WEIGHTS = {
    "skills": 0.40,
    "experience": 0.25,
    "education": 0.15,
    "semantic": 0.20,
}

SKILL_LEVELS = {
    "phd": 5,
    "doctorate": 5,
    "master": 4,
    "mba": 4,
    "bachelor": 3,
    "grado": 3,
    "associate": 2,
    "diploma": 1,
}
