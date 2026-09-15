# JobMatch - Sistema de Busqueda de Empleo Inteligente

## Descripcion

JobMatch es una aplicacion que busca ofertas de empleo en multiples fuentes, calcula un porcentaje de compatibilidad con tu CV, y exporta los resultados a Google Sheets para llevar un registro.

---

## Funcionalidades Principales

| Funcionalidad | Descripcion |
|---------------|-------------|
| **CV Parser** | Extrae skills, experiencia y educacion de CVs (PDF/DOCX) usando NLP |
| **Multi-Fuente** | Busca en Indeed, LinkedIn, Glassdoor, Adzuna, Google for Jobs |
| **Matching Inteligente** | Calcula % de compatibilidad con TF-IDF + fuzzy matching |
| **Clasificacion** | Bueno (80-100%), Regular (50-79%), No Match (<50%) |
| **Exportacion** | Google Sheets, CSV, JSON |
| **CLI + Web** | Interfaz de linea de comandos y dashboard web |

---

## Stack Tecnologico

```
Backend:     Python 3.11+ / FastAPI
NLP:         spaCy (en_core_web_sm)
Scraping:    python-jobspy
APIs:        Adzuna, JSearch (RapidAPI)
Sheets:      gspread + google-auth
CLI:         typer
Frontend:    HTML + TailwindCSS + htmx
```

---

## Estructura del Proyecto

```
jobmatch/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuracion
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   ├── routers/
│   │   ├── cv.py            # Endpoints CV
│   │   ├── jobs.py          # Endpoints busqueda
│   │   └── sheets.py        # Endpoints Sheets
│   └── services/
│       ├── cv_parser.py     # Parseo CV (spaCy)
│       ├── job_scraper.py   # Scraping (JobSpy)
│       ├── job_api.py       # APIs: Adzuna, JSearch
│       ├── matcher.py       # Matching engine
│       └── sheets_service.py # Google Sheets
├── cli.py                   # CLI
├── frontend/
│   └── index.html           # Dashboard web
├── tests/
├── data/
│   └── skills_db.json       # Base de datos skills
├── requirements.txt
└── .env.example
```

---

## Documentacion

| Documento | Contenido |
|-----------|-----------|
| [docs/VIABILITY.md](docs/VIABILITY.md) | Analisis de viabilidad tecnica y economica |
| [docs/REQUIREMENTS.md](docs/REQUIREMENTS.md) | Requerimientos funcionales y no funcionales |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitectura del sistema y diagramas |
| [docs/USE_CASES.md](docs/USE_CASES.md) | Diagramas de casos de uso (Mermaid) |
| [docs/DATA_FLOW.md](docs/DATA_FLOW.md) | Flujo de datos detallado |
| [docs/SCREENS.md](docs/SCREENS.md) | Disenos de interfaces (CLI y Web) |
| [docs/RISK_ANALYSIS.md](docs/RISK_ANALYSIS.md) | Analisis de riesgos y mitigaciones |

---

## Diagramas

Los diagramas estan en `docs/diagrams/` en formato Mermaid:

- `use_cases.mmd` - Diagrama de casos de uso
- `sequence.mmd` - Diagrama de secuencia
- `state_diagram.mmd` - Diagrama de estados
- `flow_chart.mmd` - Flujo principal

Para renderizar: [Mermaid Live Editor](https://mermaid.live/)

---

## Fuentes de Empleo

| Fuente | Tipo | Costo | Cobertura |
|--------|------|-------|-----------|
| **JobSpy** | Scraping | Gratis | Indeed, LinkedIn, Glassdoor, ZipRecruiter |
| **Adzuna** | REST API | Gratis (2,500/mes) | Global |
| **JSearch** | RapidAPI | Freemium | Google for Jobs |

---

## Analisis de Viabilidad Resumen

| Criterio | Evaluacion |
|----------|------------|
| Viabilidad Tecnica | ✅ ALTA |
| Viabilidad Economica | ✅ ALTA ($0-15/mes) |
| Viabilidad Operativa | ✅ ALTA |
| Complejidad | ⚠️ MEDIA |

**Veredicto**: ✅ PROCEDER CON DESARROLLO

Ver [docs/VIABILITY.md](docs/VIABILITY.md) para analisis completo.

---

## Costos Estimados

| Concepto | Costo |
|----------|-------|
| Desarrollo (si contrata) | ~$5,640 |
| Desarrollo (DIY) | $0 (tiempo) |
| Operacion mensual | $0-15/mes |
| APIs | $0 (tier gratis) |

---

## Riesgos Principales

| Riesgo | Mitigacion |
|--------|------------|
| Rate limiting | Proxies, delays, caché |
| Cambios en sitios | Parsers flexibles, fallback |
| GDPR | No almacenar PII |

Ver [docs/RISK_ANALYSIS.md](docs/RISK_ANALYSIS.md) para analisis completo.

---

## Proximo Paso

Una vez revisada la documentacion, el desarrollo se realizara en fases:

1. **MVP (2-3 semanas)**: CV Parser + JobSpy + Match basico
2. **Fase 2 (+1 semana)**: APIs adicionales + Google Sheets
3. **Fase 3 (+1 semana)**: Frontend + CLI pulido

---

*Proyecto documentado: Septiembre 2026*
