# Casos de Uso - JobMatch

## 1. Diagrama de Casos de Uso General

```mermaid
graph TB
    subgraph "Sistema JobMatch"
        UC1[UC-01: Subir CV]
        UC2[UC-02: Buscar Empleos]
        UC3[UC-03: Calcular Match]
        UC4[UC-04: Exportar a Sheets]
        UC5[UC-05: Ver Historial]
        UC6[UC-06: Configurar Búsqueda]
    end

    subgraph "Actores"
        U[Usuario]
        S[Servidor Google Sheets]
        JS[JobSpy]
        AD[Adzuna API]
        JS2[JSearch API]
    end

    U --> UC1
    U --> UC2
    U --> UC4
    U --> UC5
    U --> UC6

    UC1 --> UC3
    UC2 --> UC3
    UC3 --> UC4

    UC2 --> JS
    UC2 --> AD
    UC2 --> JS2
    UC4 --> S
```

---

## 2. Casos de Uso Detallados

### UC-01: Subir CV

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Subir y parsear CV |
| **Actor principal** | Usuario |
| **Precondiciones** | Archivo CV disponible (PDF o DOCX) |
| **Postcondiciones** | Perfil parseado almacenado en memoria |

**Flujo Principal:**
1. Usuario selecciona archivo CV (PDF/DOCX)
2. Sistema valida formato
3. Sistema extrae texto del archivo
4. Sistema ejecuta NER (Named Entity Recognition)
5. Sistema extrae: nombre, email, teléfono, skills, educación, experiencia
6. Sistema normaliza skills a taxonomy estándar
7. Sistema retorna perfil parseado en JSON

**Flujos Alternativos:**
- 2a. Formato no válido → Error: "Formato no soportado"
- 3a. No se extrae texto → Error: "Archivo corrupto o imagen"
- 4a. NER falla parcialmente → Retorna campos disponibles + warning

**Diagrama de Flujo:**
```mermaid
flowchart TD
    A[Usuario sube CV] --> B{¿Formato válido?}
    B -->|No| C[Error: Formato no soportado]
    B -->|Si| D[Extraer texto]
    D --> E{¿Texto extraído?}
    E -->|No| F[Error: Archivo corrupto]
    E -->|Si| G[Ejecutar NER spaCy]
    G --> H[Extraer skills]
    H --> I[Extraer educación]
    I --> J[Extraer experiencia]
    J --> K[Normalizar datos]
    K --> L[Retornar PerfilCV JSON]
```

---

### UC-02: Buscar Empleos

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Buscar ofertas de empleo |
| **Actor principal** | Usuario |
| **Precondiciones** | Perfil CV parseado (opcional para búsqueda sin match) |
| **Postcondiciones** | Lista de ofertas obtenida |

**Flujo Principal:**
1. Usuario ingresa criterios de búsqueda:
   - Palabra clave (ej: "Python developer")
   - Ubicación (ej: "Madrid" o "Remoto")
   - Tipo de empleo (opcional)
2. Sistema valida criterios
3. Sistema ejecuta búsqueda en paralelo:
   - JobSpy (Indeed, LinkedIn, Glassdoor)
   - Adzuna API
   - JSearch API
4. Sistema deduplica resultados
5. Sistema retorna lista normalizada de ofertas

**Flujos Alternativos:**
- 3a. Una fuente falla → Continúa con otras fuentes
- 3a.1. Todas fallan → Error: "No se pudieron obtener resultados"
- 4a. Sin resultados → Retornar lista vacía

**Diagrama de Flujo:**
```mermaid
flowchart TD
    A[Usuario ingresa búsqueda] --> B[Validar criterios]
    B --> C{¿Criterios válidos?}
    C -->|No| D[Error: Criterios inválidos]
    C -->|Si| E[Buscar en JobSpy]
    B --> F[Buscar en Adzuna]
    B --> G[Buscar en JSearch]
    E --> H[Deduplicar resultados]
    F --> H
    G --> H
    H --> I{¿Hay resultados?}
    I -->|No| J[Retornar lista vacía]
    I -->|Si| K[Normalizar schema]
    K --> L[Retornar Lista<Job>]
```

---

### UC-03: Calcular Match

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Calcular porcentaje de compatibilidad |
| **Actor principal** | Sistema (automático) |
| **Precondiciones** | Perfil CV + Lista de ofertas |
| **Postcondiciones** | Ofertas con score de match |

**Flujo Principal:**
1. Para cada oferta en la lista:
   a. Calcular match de skills (40%)
   b. Calcular match de experiencia (25%)
   c. Calcular match de educación (15%)
   d. Calcular similaridad semántica TF-IDF (20%)
   e. Calcular score total ponderado
   f. Clasificar: Bueno/Regular/No match
   g. Identificar skills faltantes
2. Ordenar resultados por score descendente
3. Retornar resultados enriquecidos

**Clasificación:**
- **Bueno**: 80-100% → Altamente compatible
- **Regular**: 50-79% → Parcialmente compatible
- **No match**: <50% → Baja compatibilidad

**Diagrama de Flujo:**
```mermaid
flowchart TD
    A[Recibir CV + Job] --> B[Calcular Skills Match]
    B --> C[Calcular Experience Match]
    C --> D[Calcular Education Match]
    D --> E[Calcular Semantic Match TF-IDF]
    E --> F[Ponderar scores]
    F --> G[Score Total]
    G --> H{¿Score >= 80%?}
    H -->|Si| I[Clasificar: BUENO]
    H -->|No| J{¿Score >= 50%?}
    J -->|Si| K[Clasificar: REGULAR]
    J -->|No| L[Clasificar: NO MATCH]
    I --> M[Retornar MatchResult]
    K --> M
    L --> M
```

---

### UC-04: Exportar a Google Sheets

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Exportar resultados a hoja de cálculo |
| **Actor principal** | Usuario |
| **Precondiciones** | Resultados de búsqueda disponibles + Credenciales Google |
| **Postcondiciones** | Datos escritos en Google Sheets |

**Flujo Principal:**
1. Usuario solicita exportar resultados
2. Sistema verifica credenciales Google
3. Sistema crea/abre hoja de cálculo
4. Sistema escribe encabezados
5. Sistema escribe filas con datos:
   - Fecha
   - Empresa
   - Puesto
   - Match %
   - Skills faltantes
   - URL oferta
   - Fuente
   - Estado (Pendiente)
6. Sistema retorna URL de la hoja

**Flujos Alternativos:**
- 2a. Sin credenciales → Error: "Configurar service account"
- 4a. Hoja existe → Append a hoja existente
- 5a. Error de escritura → Reintentar 3 veces

**Diagrama de Flujo:**
```mermaid
flowchart TD
    A[Usuario solicita exportar] --> B[Verificar credenciales Google]
    B --> C{¿Credenciales válidas?}
    C -->|No| D[Error: Configurar service account]
    C -->|Si| E{¿Hoja existe?}
    E -->|Si| F[Abrir hoja existente]
    E -->|No| G[Crear nueva hoja]
    F --> H[Escribir encabezados]
    G --> H
    H --> I[Escribir filas de datos]
    I --> J{¿Escritura exitosa?}
    J -->|No| K[Reintentar]
    K --> I
    J -->|Si| L[Retornar URL hoja]
```

---

### UC-05: Ver Historial de Búsquedas

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Consultar búsquedas anteriores |
| **Actor principal** | Usuario |
| **Precondiciones** | Búsquedas previas guardadas |
| **Postcondiciones** | Historial mostrado |

**Flujo Principal:**
1. Usuario solicita ver historial
2. Sistema lee caché de búsquedas
3. Sistema retorna lista de búsquedas con:
   - Fecha
   - Criterios
   - Cantidad de resultados
   - Mejor match score

---

### UC-06: Configurar Búsqueda

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Guardar configuración de búsqueda |
| **Actor principal** | Usuario |
| **Precondiciones** | Ninguna |
| **Postcondiciones** | Configuración guardada |

**Flujo Principal:**
1. Usuario define configuración:
   - Fuentes a usar
   - Filtros por defecto
   - Ubicación por defecto
2. Sistema guarda en .env o config.json
3. Sistema confirma guardado

---

## 3. Diagrama de Estados

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> UploadingCV : Subir CV
    UploadingCV --> ParsingCV : Archivo recibido
    ParsingCV --> CVReady : Parseo exitoso
    ParsingCV --> Error : Parseo fallido
    Error --> Idle : Corregir
    CVReady --> Searching : Buscar empleos
    Searching --> ResultsReady : Búsqueda completa
    ResultsReady --> Matching : Calcular match
    Matching --> MatchReady : Match calculado
    MatchReady --> Exporting : Exportar a Sheets
    Exporting --> Exported : Exportación exitosa
    Exporting --> ExportError : Error exportación
    ExportError --> ResultsReady : Reintentar
    Exported --> Idle : Completado
    MatchReady --> Idle : Nueva búsqueda
```

---

## 4. Matriz de Requerimientos vs Casos de Uso

| Requerimiento | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 |
|---------------|-------|-------|-------|-------|-------|-------|
| CV-01: Subir PDF | X | | | | | |
| CV-02: Subir DOCX | X | | | | | |
| CV-03: Extraer texto | X | | | | | |
| CV-04: Detectar datos | X | | | | | |
| CV-05: Detectar skills | X | | X | | | |
| JOB-01: Buscar keyword | | X | | | | |
| JOB-02: Buscar ubicación | | X | | | | |
| JOB-06: Multi-fuente | | X | | | | |
| MATCH-01: Skills match | | | X | | | |
| MATCH-05: Clasificar | | | X | | | |
| EXP-01: Google Sheets | | | | X | | |
| EXP-05: Append | | | | X | | |

---

## 5. Diagrama de Secuencia - Flujo Completo

```mermaid
sequenceDiagram
    actor User
    participant CLI
    participant API
    participant CVParser
    participant JobScraper
    participant Matcher
    participant Sheets

    User->>CLI: jobmatch search "Python developer" Madrid
    CLI->>API: POST /cv/upload (CV file)
    API->>CVParser: parse_resume(file)
    CVParser-->>API: ParsedCV
    API-->>CLI: CV parseado ✓

    CLI->>API: GET /jobs/search?q=Python+developer&loc=Madrid
    API->>JobScraper: search_all(query, location)
    
    par Múltiples fuentes
        JobScraper->>JobScraper: search_jobspy()
        JobScraper->>JobScraper: search_adzuna()
        JobScraper->>JobScraper: search_jsearch()
    end
    
    JobScraper-->>API: List[Job]
    
    API->>Matcher: calculate_match(cv, jobs)
    Matcher-->>API: List[MatchResult]
    API-->>CLI: Resultados con scores

    CLI-->>User: Top 10 resultados mostrados

    User->>CLI: jobmatch export --to-sheets
    CLI->>API: POST /sheets/export(results)
    API->>Sheets: append_results(sheet, results)
    Sheets-->>API: URL hoja
    API-->>CLI: Exportado ✓
    CLI-->>User: https://docs.google.com/sheets/...
```

---

*Documento generado: Septiembre 2026*
