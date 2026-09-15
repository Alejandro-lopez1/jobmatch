# Requerimientos - JobMatch

## 1. Requerimientos Funcionales

### 1.1 Gestión de CV

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| CV-01 | Subir CV en formato PDF | Alta |
| CV-02 | Subir CV en formato DOCX | Alta |
| CV-03 | Extraer texto del CV | Alta |
| CV-04 | Detectar: nombre, email, teléfono | Alta |
| CV-05 | Detectar: habilidades técnicas | Alta |
| CV-06 | Detectar: educación (títulos, grados) | Alta |
| CV-07 | Detectar: experiencia laboral | Alta |
| CV-08 | Detectar: idiomas | Media |
| CV-09 | Normalizar habilidades a taxonomy estándar | Media |
| CV-10 | Guardar perfil parseado (JSON) | Alta |

### 1.2 Búsqueda de Empleo

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| JOB-01 | Buscar por palabra clave | Alta |
| JOB-02 | Buscar por ubicación | Alta |
| JOB-03 | Buscar por tipo (remoto, presencial, híbrido) | Alta |
| JOB-04 | Filtrar por fecha de publicación | Media |
| JOB-05 | Filtrar por salario (cuando disponible) | Baja |
| JOB-06 | Buscar en múltiples fuentes simultáneamente | Alta |
| JOB-07 | Deduplicar ofertas de múltiples fuentes | Media |
| JOB-08 | Guardar historial de búsquedas | Media |

### 1.3 Matching

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| MATCH-01 | Calcular % de match por skills | Alta |
| MATCH-02 | Calcular % de match por experiencia | Alta |
| MATCH-03 | Calcular % de match por educación | Alta |
| MATCH-04 | Score general ponderado | Alta |
| MATCH-05 | Clasificar: Bueno (80-100%), Regular (50-79%), No match (<50%) | Alta |
| MATCH-06 | Mostrar skills faltantes | Alta |
| MATCH-07 | Mostrar skills coincidentes | Alta |
| MATCH-08 | Ordenar resultados por match score | Alta |

### 1.4 Exportación

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| EXP-01 | Exportar resultados a Google Sheets | Alta |
| EXP-02 | Configurar columnas personalizadas | Media |
| EXP-03 | Exportar a CSV local | Media |
| EXP-04 | Exportar a JSON | Baja |
| EXP-05 | Actualizar hoja existente (append) | Media |

### 1.5 Interfaz

| ID | Requerimiento | Prioridad |
|----|---------------|-----------|
| UI-01 | CLI para búsquedas rápidas | Alta |
| UI-02 | Dashboard web para visualización | Media |
| UI-03 | Subir CV desde interfaz web | Media |
| UI-04 | Ver resultados con filtros | Alta |
| UI-05 | Exportar desde interfaz | Media |

---

## 2. Requerimientos No Funcionales

### 2.1 Rendimiento

| Métrica | Objetivo |
|---------|----------|
| Parseo de CV | < 5 segundos |
| Búsqueda de empleo | < 10 segundos |
| Cálculo de match | < 2 segundos por oferta |
| Exportación Sheets | < 5 segundos |

### 2.2 Usabilidad

| Requerimiento | Descripción |
|---------------|-------------|
| CLI intuitivo | Comandos claros, help incorporado |
| Errores descriptivos | Mensajes claros, no tracebacks |
| Documentación | README completo con ejemplos |

### 2.3 Seguridad

| Requerimiento | Descripción |
|---------------|-------------|
| No almacenar PII | CV parseado se procesa en memoria |
| API keys en .env | Nunca en código fuente |
| Google creds seguras | Service account.json fuera de repo |

### 2.4 Mantenibilidad

| Requerimiento | Descripción |
|---------------|-------------|
| Código modular | Separación clara de responsabilidades |
| Tests unitarios | Cobertura mínima 70% |
| Type hints | Todo el código tipado |

---

## 3. Requerimientos Técnicos

### 3.1 Stack Tecnológico

```
Backend:     Python 3.11+ / FastAPI
NLP:         spaCy (en_core_web_sm)
Scraping:    python-jobspy
APIs:        Adzuna, JSearch (RapidAPI)
Sheets:      gspread + google-auth
CLI:         typer
Frontend:    HTML + TailwindCSS + htmx
Database:    SQLite (opcional, para caché)
```

### 3.2 Dependencias Principales

```txt
# Core
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0

# NLP
spacy>=3.7.0
scikit-learn>=1.3.0
rapidfuzz>=3.0.0

# PDF/DOCX
pdfplumber>=0.10.0
python-docx>=1.0.0

# Job Sources
python-jobspy>=1.1.0
adzuna>=0.1.0
httpx>=0.25.0

# Google Sheets
gspread>=6.0.0
google-auth>=2.0.0

# CLI
typer>=0.9.0

# Utils
python-dotenv>=1.0.0
```

### 3.3 Estructura de Directorios

```
jobmatch/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── cv.py
│   │   ├── jobs.py
│   │   └── sheets.py
│   └── services/
│       ├── __init__.py
│       ├── cv_parser.py
│       ├── job_scraper.py
│       ├── job_api.py
│       ├── matcher.py
│       └── sheets_service.py
├── cli.py
├── frontend/
│   └── index.html
├── tests/
│   ├── test_cv_parser.py
│   ├── test_matcher.py
│   └── test_api.py
├── data/
│   └── skills_db.json
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. Criterios de Aceptación

### MVP (Mínimo Viable)

- [ ] Subir CV PDF y extraer skills
- [ ] Buscar empleos con JobSpy (Indeed, LinkedIn)
- [ ] Calcular match score con TF-IDF
- [ ] Clasificar en Bueno/Regular/No match
- [ ] Exportar top 10 resultados a Google Sheets
- [ ] CLI funcional con comandos básicos

### Versión Completa

- [ ] Todas las fuentes (JobSpy + Adzuna + JSearch)
- [ ] Matching multi-criterio ponderado
- [ ] Frontend web funcional
- [ ] Caché de búsquedas
- [ ] Soporte DOCX
- [ ] Exportación CSV + JSON

---

*Documento generado: Septiembre 2026*
