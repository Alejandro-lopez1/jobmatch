import re
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone

import spacy
import pdfplumber
from docx import Document
from rapidfuzz import fuzz

from backend.models.schemas import ParsedCV, PersonalInfo, Skills, Experience, Education
from backend.config import DATA_DIR


SKILLS_DB_PATH = DATA_DIR / "skills_db.json"


def load_skills_db() -> dict:
    if SKILLS_DB_PATH.exists():
        return json.loads(SKILLS_DB_PATH.read_text(encoding="utf-8"))
    return {}


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix == ".docx":
        return extract_text_from_docx(file_path)
    elif suffix == ".txt":
        return path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Formato no soportado: {suffix}")


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s@.\-+áéíóúñü]", " ", text, flags=re.IGNORECASE)
    return text.strip()


class CVParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        self.skills_db = load_skills_db()
        self.all_skills = self._flatten_skills()
        self._add_custom_entities()

    def _flatten_skills(self) -> list[str]:
        skills = []
        for category in self.skills_db.values():
            skills.extend(category)
        return list(set(skills))

    def _add_custom_entities(self):
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="ner")
            patterns = [
                *[{"label": "SKILL", "pattern": [{"LOWER": s.lower()}]} for s in self.all_skills],
                {"label": "DEGREE", "pattern": [{"LOWER": "bachelor"}]},
                {"label": "DEGREE", "pattern": [{"LOWER": "master"}]},
                {"label": "DEGREE", "pattern": [{"LOWER": "phd"}]},
                {"label": "DEGREE", "pattern": [{"LOWER": "mba"}]},
                {"label": "DEGREE", "pattern": [{"LOWER": "grado"}]},
                {"label": "DEGREE", "pattern": [{"LOWER": "licenciatura"}]},
            ]
            ruler.add_patterns(patterns)

    def extract_email(self, text: str) -> str | None:
        match = re.search(r"[\w.\-+]+@[\w\-]+\.[\w.\-]+", text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> str | None:
        patterns = [
            r"\+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}",
            r"\d{3}[\s\-]\d{3}[\s\-]\d{3,4}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        return None

    def extract_skills_from_text(self, text: str) -> list[str]:
        found = []
        text_lower = text.lower()
        for skill in self.all_skills:
            if skill.lower() in text_lower:
                found.append(skill)
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "SKILL" and ent.text not in found:
                found.append(ent.text)
        return list(set(found))

    def extract_experience_years(self, text: str) -> float:
        patterns = [
            r"(\d{1,2})\+?\s*(?:years?|años?)\s*(?:of\s+)?(?:experience|experiencia)",
            r"experience:?\s*(\d{1,2})\+?\s*(?:years?|años?)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        dates = re.findall(
            r"(?:20\d{2}|19\d{2})\s*[-–]\s*(?:20\d{2}|19\d{2}|present|actual|current)",
            text,
            re.IGNORECASE,
        )
        if dates:
            years = set()
            for date_range in dates:
                nums = re.findall(r"\d{4}", date_range)
                if len(nums) == 2:
                    start, end = int(nums[0]), int(nums[1])
                    years.add(end - start)
                elif len(nums) == 1:
                    years.add(datetime.now().year - int(nums[0]))
            if years:
                return float(sum(years))
        return 0

    def extract_education(self, doc) -> list[Education]:
        education = []
        degrees = [ent for ent in doc.ents if ent.label_ == "DEGREE"]
        for degree in degrees:
            edu = Education(degree=degree.text)
            sent = degree.sent
            for ent in sent.ents:
                if ent.label_ == "ORG" and not edu.institution:
                    edu.institution = ent.text
                if ent.label_ == "DATE" and not edu.year:
                    nums = re.findall(r"\d{4}", ent.text)
                    if nums:
                        edu.year = int(nums[-1])
            education.append(edu)
        return education

    def parse(self, file_path: str) -> ParsedCV:
        raw_text = extract_text(file_path)
        clean = clean_text(raw_text)
        doc = self.nlp(clean)

        name = None
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break

        education = self.extract_education(doc)

        skills_found = self.extract_skills_from_text(clean)
        technical = [s for s in skills_found if s in self.all_skills]

        return ParsedCV(
            cv_id=str(uuid.uuid4()),
            parsed_at=datetime.now(timezone.utc),
            personal_info=PersonalInfo(
                name=name,
                email=self.extract_email(raw_text),
                phone=self.extract_phone(raw_text),
            ),
            skills=Skills(technical=technical),
            experience=Experience(total_years=self.extract_experience_years(clean)),
            education=education,
            full_text=clean,
        )
