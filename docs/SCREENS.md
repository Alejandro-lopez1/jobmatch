# Interfaces de Usuario - JobMatch

## 1. CLI (Command Line Interface)

### 1.1 Comandos Principales

```bash
# Subir CV
jobmatch cv upload ./mi_cv.pdf

# Buscar empleos
jobmatch search "Python developer" --location Madrid --remote

# Ver resultados de la última búsqueda
jobmatch results

# Exportar a Google Sheets
jobmatch export --to-sheets

# Exportar a CSV
jobmatch export --to-csv results.csv

# Ver historial
jobmatch history

# Configurar
jobmatch config set --default-location Madrid
jobmatch config show
```

### 1.2 Ejemplo de Salida CLI

```
$ jobmatch search "Python developer" --location Madrid

🔍 Buscando empleos...
   ├─ JobSpy (Indeed, LinkedIn, Glassdoor): 45 resultados
   ├─ Adzuna API: 12 resultados
   └─ JSearch API: 23 resultados
   
   Total: 80 resultados (62 duplicados eliminados)
   
📊 Calculando matches con tu CV...
   
✅ Búsqueda completada!

┌────┬────────────────────┬─────────────────┬────────┬─────────────────┐
│ #  │ Empresa            │ Puesto          │ Match  │ Clasificación   │
├────┼────────────────────┼─────────────────┼────────┼─────────────────┤
│  1 │ Tech Corp          │ Python Developer│ 87.2%  │ 🟢 BUENO        │
│  2 │ Startup XYZ        │ Backend Dev     │ 76.5%  │ 🟡 REGULAR      │
│  3 │ Big Tech Inc       │ Senior Python   │ 72.1%  │ 🟡 REGULAR      │
│  4 │ Consultora ABC     │ Full Stack      │ 58.3%  │ 🟡 REGULAR      │
│  5 │ Empresa random     │ Java Developer  │ 34.2%  │ 🔴 NO MATCH     │
└────┴────────────────────┴─────────────────┴────────┴─────────────────┘

📋 Top match: Tech Corp - Python Developer (87.2%)
   Skills faltantes: Django, Celery
   Ver detalles: jobmatch show 1

💡 Para exportar a Google Sheets: jobmatch export --to-sheets
```

---

## 2. Web Dashboard

### 2.1 Layout Principal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🔧 JobMatch                          [Mi CV] [Config] [Historial]         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    BUSCAR EMPLEOS                                    │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────┐  ┌─────────────────────┐         │   │
│  │  │ 🔍 Python developer...      │  │ 📍 Madrid, España   │         │   │
│  │  └─────────────────────────────┘  └─────────────────────┘         │   │
│  │                                                                     │   │
│  │  ☑️ Remoto  ☑️ Híbrido  ☐ Presencial                              │   │
│  │                                                                     │   │
│  │  [🔍 Buscar]  [📥 Exportar]  [📊 Ver Hoja]                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RESULTADOS (18 de 62)                            │   │
│  │                                                                     │   │
│  │  Filtrar: [🟢 Bueno ✓] [🟡 Regular ✓] [🔴 No Match]              │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 🟢 87.2% - Python Developer                                  │   │   │
│  │  │    Tech Corp | Madrid (Híbrido) | €45k-55k                   │   │   │
│  │  │    Skills: Python ✓ | Django ✗ | PostgreSQL ✗ | AWS ✓       │   │   │
│  │  │    [Ver Oferta] [Aplicar] [Descartar]                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 🟡 76.5% - Backend Developer                                 │   │   │
│  │  │    Startup XYZ | Remoto | €40k-50k                           │   │   │
│  │  │    Skills: Python ✓ | FastAPI ✗ | Docker ✓ | SQL ✓          │   │   │
│  │  │    [Ver Oferta] [Aplicar] [Descartar]                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │ 🟡 72.1% - Senior Python Engineer                           │   │   │
│  │  │    Big Tech Inc | Madrid (Presencial) | €55k-65k             │   │   │
│  │  │    Skills: Python ✓ | Java ✗ | AWS ✓ | K8s ✗               │   │   │
│  │  │    [Ver Oferta] [Aplicar] [Descartar]                        │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  │                                                                     │   │
│  │  [← Anterior]  Página 1 de 4  [Siguiente →]                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Modal: Detalle de Oferta

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ✕ Python Developer - Tech Corp                                      [X]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SCORE DE MATCH                                    │   │
│  │                                                                     │   │
│  │         ┌─────────────────────────────────────┐                    │   │
│  │         │                                     │                    │   │
│  │         │          87.2%                      │                    │   │
│  │         │          BUENO                      │                    │   │
│  │         │                                     │                    │   │
│  │         └─────────────────────────────────────┘                    │   │
│  │                                                                     │   │
│  │  Skills (40%)      ████████████░░░░  75%                          │   │
│  │  Experiencia (25%) ████████████████  100%                         │   │
│  │  Educación (15%)   ████████████████  100%                         │   │
│  │  Semántico (20%)   █████████████░░░  78%                          │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    ANÁLISIS DE SKILLS                               │   │
│  │                                                                     │   │
│  │  ✅ Coincidentes:                                                  │   │
│  │     • Python (experiencia comprobada)                              │   │
│  │     • AWS (mencionado en CV)                                       │   │
│  │                                                                     │   │
│  │  ❌ Faltantes:                                                     │   │
│  │     • Django (recomendado: tomar curso básico)                     │   │
│  │     • PostgreSQL (recomendado: práctica en proyectos)              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    DETALLES DE LA OFERTA                            │   │
│  │                                                                     │   │
│  │  Empresa: Tech Corp                                                 │   │
│  │  Ubicación: Madrid (Híbrido)                                       │   │
│  │  Salario: €45,000 - €55,000 / año                                  │   │
│  │  Tipo: Tiempo completo                                             │   │
│  │  Publicado: hace 2 días                                             │   │
│  │                                                                     │   │
│  │  Descripción:                                                      │   │
│  │  Buscamos desarrollador Python con experiencia en cloud...         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [🔗 Ver Oferta Original]  [📤 Exportar]  [❌ Descartar]  [✅ Aplicar]   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Página: Mi CV

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  👤 Mi CV                                                     [Editar]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    INFORMACIÓN PERSONAL                             │   │
│  │                                                                     │   │
│  │  Nombre:    Juan Pérez                                             │   │
│  │  Email:     juan@email.com                                         │   │
│  │  Teléfono:  +34 612 345 678                                        │   │
│  │  Ubicación: Madrid, España                                         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    HABILIDADES                                      │   │
│  │                                                                     │   │
│  │  Técnicas:                                                         │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │   │
│  │  │ Python  │ │  SQL    │ │  AWS    │ │ Docker  │ │   Git   │     │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │   │
│  │                                                                     │   │
│  │  Blandas:                                                          │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐           │   │
│  │  │  Liderazgo    │ │ Comunicación  │ │  Trabajo      │           │   │
│  │  │               │ │               │ │  en equipo    │           │   │
│  │  └───────────────┘ └───────────────┘ └───────────────┘           │   │
│  │                                                                     │   │
│  │  Idiomas:                                                          │   │
│  │  • Español (nativo)                                                │   │
│  │  • Inglés (B2)                                                     │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EXPERIENCIA                                      │   │
│  │                                                                     │   │
│  │  📅 2021 - 2024 | Software Developer | Tech Corp                   │   │
│  │     • Desarrollo de APIs REST con Python                           │   │
│  │     • Implementación de microservicios en AWS                      │   │
│  │                                                                     │   │
│  │  📅 2019 - 2021 | Junior Developer | Startup XYZ                   │   │
│  │     • Desarrollo web fullstack                                     │   │
│  │     • Mantenimiento de bases de datos                              │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    EDUCACIÓN                                        │   │
│  │                                                                     │   │
│  │  🎓 Grado en Ingeniería Informática                                │   │
│  │     Universidad Politécnica de Madrid | 2015-2019                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  [📤 Subir nuevo CV]  [💾 Guardar]  [🔄 Re-parsear]                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Página: Configuración

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚙️ Configuración                                          [Guardar]     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FUENTES DE EMPLEO                                │   │
│  │                                                                     │   │
│  │  ☑️ JobSpy (Indeed, LinkedIn, Glassdoor, ZipRecruiter)            │   │
│  │  ☑️ Adzuna API                                                     │   │
│  │  ☑️ JSearch (Google for Jobs)                                      │   │
│  │                                                                     │   │
│  │  API Keys:                                                         │   │
│  │  ┌─────────────────────────────────────────────────────────┐       │   │
│  │  │ Adzuna App ID:    [adzuna_app_id          ]             │       │   │
│  │  │ Adzuna App Key:   [********************** ]             │       │   │
│  │  │ RapidAPI Key:     [********************** ]             │       │   │
│  │  └─────────────────────────────────────────────────────────┘       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PREFERENCIAS DE BÚSQUEDA                         │   │
│  │                                                                     │   │
│  │  Ubicación por defecto: [Madrid, España        ]                   │   │
│  │  Tipo de empleo:        [☑️ Remoto] [☑️ Híbrido] [☐ Presencial]   │   │
│  │  Rango salarial mín:    [€30,000   ]                               │   │
│  │  Publicado en últimas:  [7 días     ]                               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    GOOGLE SHEETS                                    │   │
│  │                                                                     │   │
│  │  Estado: ✅ Conectado                                              │   │
│  │  Hoja por defecto: JobMatch Results                                 │   │
│  │                                                                     │   │
│  │  [🔑 Regenerar credenciales]  [📋 Ver hoja actual]                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    PESOS DE MATCHING                                │   │
│  │                                                                     │   │
│  │  Skills:        [====40%====]  (30-60%)                            │   │
│  │  Experiencia:   [==25%=====]  (15-40%)                            │   │
│  │  Educación:     [=15%======]  (5-25%)                             │   │
│  │  Semántico:     [==20%=====]  (10-30%)                            │   │
│  │                                                                     │   │
│  │  [🔄 Restaurar valores por defecto]                                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Wireframes Móvil

```
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│               │  │               │  │               │
│  🔧 JobMatch  │  │  🔍 Buscar    │  │  📊 Resultados│
│               │  │               │  │               │
│  ┌─────────┐  │  │ ┌───────────┐ │  │ ┌───────────┐ │
│  │  Mi CV  │  │  │ │ Python... │ │  │ │ 🟢 87%    │ │
│  └─────────┘  │  │ └───────────┘ │  │ │ Tech Corp │ │
│               │  │               │  │ │ [Ver]     │ │
│  ┌─────────┐  │  │ ┌───────────┐ │  │ └───────────┘ │
│  │ Buscar  │  │  │ │ Madrid... │ │  │               │
│  └─────────┘  │  │ └───────────┘ │  │ ┌───────────┐ │
│               │  │               │  │ │ 🟡 72%    │ │
│  ┌─────────┐  │  │ ☑️ Remoto    │  │ │ Startup X │ │
│  │Results  │  │  │ ☑️ Híbrido   │  │ │ [Ver]     │ │
│  └─────────┘  │  │               │  │ └───────────┘ │
│               │  │ [🔍 Buscar]  │  │               │
│  ┌─────────┐  │  │               │  │ [📥 Exportar] │
│  │ Config  │  │  │               │  │               │
│  └─────────┘  │  │               │  │               │
│               │  │               │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

*Documento generado: Septiembre 2026*
