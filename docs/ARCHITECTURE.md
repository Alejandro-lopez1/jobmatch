# Arquitectura del Sistema - JobMatch

## 1. Diagrama de Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              JOBMATCH                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │              │    │              │    │              │                   │
│  │   CLI        │    │   Web UI     │    │   API        │                   │
│  │   (typer)    │    │   (HTML)     │    │   (FastAPI)  │                   │
│  │              │    │              │    │              │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                           │
│         └───────────────────┼───────────────────┘                           │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     CORE SERVICES                                     │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │ CV Parser  │  │ Job Scraper│  │ Matcher    │  │ Sheets Svc │     │  │
│  │  │ (spaCy)    │  │ (JobSpy)   │  │ (TF-IDF)   │  │ (gspread)  │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                             │                                               │
│                             ▼                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                     DATA LAYER                                        │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │ CV Cache   │  │ Jobs Cache │  │ Skills DB  │  │ Config     │     │  │
│  │  │ (JSON)     │  │ (SQLite)   │  │ (JSON)     │  │ (.env)     │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SERVICES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │   Indeed   │  │  LinkedIn  │  │  Glassdoor │  │  ZipRecruiter│          │
│  │  (JobSpy)  │  │  (JobSpy)  │  │  (JobSpy)  │  │  (JobSpy)  │           │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘           │
│                                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                            │
│  │  Adzuna    │  │  JSearch   │  │  Google    │                            │
│  │   API      │  │ (RapidAPI) │  │  Sheets    │                            │
│  └────────────┘  └────────────┘  └────────────┘                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI APPLICATION                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ROUTERS                                      │   │
│  │                                                                     │   │
│  │  POST /cv/upload          → Parsea CV y retorna perfil             │   │
│  │  GET  /jobs/search        → Busca empleos y retorna con match      │   │
│  │  POST /sheets/export      → Exporta resultados a Google Sheets     │   │
│  │  GET  /health             → Health check                           │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                       SERVICES                                      │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ CVParserService                                             │   │   │
│  │  │   - extract_text(file) → str                                │   │   │
│  │  │   - parse_resume(text) → ParsedCV                          │   │   │
│  │  │   - extract_skills(text) → List[str]                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ JobSearchService                                           │   │   │
│  │  │   - search_jobspy(query, location) → List[Job]             │   │   │
│  │  │   - search_adzuna(query, location) → List[Job]             │   │   │
│  │  │   - search_jsearch(query, location) → List[Job]            │   │   │
│  │  │   - search_all(query, location) → List[Job]                │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ MatchService                                               │   │   │
│  │  │   - calculate_match(cv, job) → MatchResult                 │   │   │
│  │  │   - skill_match(cv_skills, job_skills) → float             │   │   │
│  │  │   - experience_match(cv_exp, job_exp) → float              │   │   │
│  │  │   - classify_match(score) → str                            │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ SheetsService                                              │   │   │
│  │  │   - connect() → gspread.Client                              │   │   │
│  │  │   - create_sheet(name) → Worksheet                         │   │   │
│  │  │   - append_results(sheet, jobs) → None                     │   │   │
│  │  │   - export_csv(jobs) → str                                 │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Modelo de Datos

### 3.1 Perfil CV (Parsed)

```json
{
  "cv_id": "uuid",
  "parsed_at": "2026-09-14T22:30:00Z",
  "personal_info": {
    "name": "Juan Pérez",
    "email": "juan@email.com",
    "phone": "+34 612 345 678",
    "location": "Madrid, España"
  },
  "skills": {
    "technical": ["Python", "JavaScript", "SQL", "Docker"],
    "soft": ["Liderazgo", "Comunicación"],
    "languages": ["Español (nativo)", "Inglés (B2)"]
  },
  "experience": {
    "total_years": 5,
    "positions": [
      {
        "title": "Software Developer",
        "company": "Tech Corp",
        "duration": "2021-2024",
        "years": 3
      }
    ]
  },
  "education": [
    {
      "degree": "Grado en Ingeniería Informática",
      "institution": "Universidad Politécnica",
      "year": 2019
    }
  ]
}
```

### 3.2 Oferta de Empleo

```json
{
  "job_id": "uuid",
  "source": "indeed|linkedin|adzuna|jsearch",
  "scraped_at": "2026-09-14T22:30:00Z",
  "title": "Senior Python Developer",
  "company": "Startup XYZ",
  "location": "Madrid (Híbrido)",
  "url": "https://...",
  "description": "Buscamos desarrollador Python...",
  "salary": {
    "min": 45000,
    "max": 55000,
    "currency": "EUR",
    "period": "year"
  },
  "requirements": {
    "skills": ["Python", "Django", "PostgreSQL", "AWS"],
    "experience_years": 3,
    "education": "Grado en Informática"
  },
  "posted_date": "2026-09-10",
  "is_remote": true,
  "job_type": "fulltime"
}
```

### 3.3 Resultado de Match

```json
{
  "match_id": "uuid",
  "job_id": "uuid",
  "cv_id": "uuid",
  "calculated_at": "2026-09-14T22:30:00Z",
  "scores": {
    "skills": 0.85,
    "experience": 0.90,
    "education": 1.0,
    "semantic": 0.78,
    "total": 0.87
  },
  "classification": "bueno|regular|no_match",
  "matched_skills": ["Python", "SQL", "AWS"],
  "missing_skills": ["Django", "PostgreSQL"],
  "recommendations": [
    "Considerar aprender Django para mejorar match",
    "Experiencia cumple con requisitos mínimos"
  ]
}
```

---

## 4. Flujo de Datos

### 4.1 Flujo Principal: Búsqueda + Match

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Usuario    │     │  Sistema    │     │  Fuentes    │     │  Sheets     │
│  (CLI/Web)  │     │  (JobMatch) │     │  Externas   │     │  (Google)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  1. Sube CV       │                   │                   │
       │──────────────────>│                   │                   │
       │                   │                   │                   │
       │  2. CV Parseado   │                   │                   │
       │<──────────────────│                   │                   │
       │                   │                   │                   │
       │  3. Búsqueda      │                   │                   │
       │──────────────────>│                   │                   │
       │                   │                   │                   │
       │                   │  4. Scraping/API  │                   │
       │                   │──────────────────>│                   │
       │                   │                   │                   │
       │                   │  5. Ofertas       │                   │
       │                   │<──────────────────│                   │
       │                   │                   │                   │
       │                   │  6. Matching      │                   │
       │                   │  (en memoria)     │                   │
       │                   │                   │                   │
       │  7. Resultados    │                   │                   │
       │<──────────────────│                   │                   │
       │                   │                   │                   │
       │  8. Exportar      │                   │                   │
       │──────────────────>│                   │                   │
       │                   │                   │                   │
       │                   │  9. Write Sheet   │                   │
       │                   │──────────────────────────────────────>│
       │                   │                   │                   │
       │  10. Confirmado   │                   │                   │
       │<──────────────────│                   │                   │
       │                   │                   │                   │
```

### 4.2 Flujo de Cálculo de Match

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MATCHING PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT: ParsedCV + Job                                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 1. SKILLS MATCH (40%)                                               │   │
│  │                                                                     │   │
│  │   cv_skills = ["Python", "SQL", "AWS", "Docker"]                   │   │
│  │   job_skills = ["Python", "Django", "PostgreSQL", "AWS"]           │   │
│  │                                                                     │   │
│  │   matched = ["Python", "AWS"]  → 2/4 = 0.50                       │   │
│  │   fuzzy_matches = ["SQL" ≈ "PostgreSQL"] (0.82)                   │   │
│  │   final_skill_score = 0.75                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 2. EXPERIENCE MATCH (25%)                                           │   │
│  │                                                                     │   │
│  │   cv_years = 5                                                      │   │
│  │   job_required = 3                                                  │   │
│  │   score = min(1.0, 5/3) = 1.0                                      │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 3. EDUCATION MATCH (15%)                                            │   │
│  │                                                                     │   │
│  │   cv_education = "Grado en Informática"                             │   │
│  │   job_education = "Grado en Informática"                            │   │
│  │   score = 1.0 (match exacto)                                       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 4. SEMANTIC MATCH (20%)                                             │   │
│  │                                                                     │   │
│  │   cv_text = "Desarrollador Python con experiencia en cloud..."      │   │
│  │   job_text = "Buscamos senior Python developer, AWS..."            │   │
│  │                                                                     │   │
│  │   tfidf_vectorize → cosine_similarity → 0.78                       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                      │                                      │
│                                      ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ 5. SCORE FINAL                                                      │   │
│  │                                                                     │   │
│  │   total = (0.75 × 0.40) + (1.0 × 0.25) +                         │   │
│  │           (1.0 × 0.15) + (0.78 × 0.20)                            │   │
│  │                                                                     │   │
│  │   total = 0.30 + 0.25 + 0.15 + 0.156 = 0.856                      │   │
│  │                                                                     │   │
│  │   classification = "BUENO" (80-100%)                                │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  OUTPUT: MatchResult(score=0.856, classification="bueno", ...)              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Tecnologías por Capa

| Capa | Tecnología | Justificación |
|------|------------|---------------|
| **Presentación** | CLI (typer) + Web (HTML/htmx) | Simple, sin framework JS pesado |
| **API** | FastAPI | Async, rápido, auto-docs |
| **NLP** | spaCy + scikit-Industry standard, rápido |
| **Scraping** | python-jobspy | Agrega múltiples sitios |
| **APIs externas** | httpx (async) | Mejor que requests para FastAPI |
| **Almacenamiento** | JSON + SQLite caché | Simple para uso personal |
| **Exportación** | gspread | API oficial no oficial de Sheets |

---

## 6. Decisiones de Diseño

### 6.1 ¿Por qué no MongoDB/PostgreSQL?
- **Uso personal**: No se necesitan queries complejas
- **Simplicidad**: JSON files son suficientes
- **Portabilidad**: Sin dependencia de DB server

### 6.2 ¿Por qué spaCy y no NLTK?
- **Velocidad**: spaCy es 10x más rápido
- **Production-ready**: NLTK es más académico
- **NER integrado**: spaCy trae NER pre-entrenado

### 6.3 ¿Por qué JobSpy y no Beautiful Soup?
- **Mantenimiento**: JobSpy actualiza cuando cambian los sitios
- **Multi-fuente**: Un solo library para Indeed, LinkedIn, etc.
- **Proxies**: Soporte integrado

---

*Documento generado: Septiembre 2026*
