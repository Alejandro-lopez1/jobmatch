# Análisis de Riesgos - JobMatch

## 1. Matriz de Riesgos

| ID | Riesgo | Probabilidad | Impacto | Severidad | Mitigación |
|----|--------|--------------|---------|-----------|------------|
| R01 | Rate limiting en scraping | Alta | Medio | 🟡 | Proxies, delays, caché |
| R02 | Cambios en estructura de sitios | Media | Alto | 🟠 | Parsers flexibles, monitoreo |
| R03 | API keys revocadas | Baja | Medio | 🟡 | Múltiples fuentes fallback |
| R04 | CVs con formatos raros | Alta | Bajo | 🟡 | Múltiples extractores |
| R05 | Datos personales (GDPR) | Media | Alto | 🟠 | No almacenar PII |
| R06 | SpaCy model download falla | Baja | Bajo | 🟢 | Bundled model |
| R07 | Google Sheets quota exceeded | Baja | Bajo | 🟢 | Caché local |
| R08 | Scraping ilegal | Baja | Alto | 🟠 | Solo sitios públicos, TOS check |

---

## 2. Detalle de Riesgos

### R01: Rate Limiting en Scraping

**Descripción**: Sitios como LinkedIn limitan requests por IP (aprox. 10 páginas).

**Probabilidad**: Alta (especialmente en LinkedIn)

**Impacto**: Medio (resultados incompletos, no total failure)

**Mitigación**:
```python
# 1. Delays entre requests
import time
time.sleep(random.uniform(2, 5))

# 2. Rotación de proxies (opcional)
proxies = [
    "user:pass@proxy1:port",
    "user:pass@proxy2:port"
]

# 3. Caché de resultados
if cached_result and not expired:
    return cached_result

# 4. Fallback a fuentes alternativas
if jobspy_fails:
    return adzuna_results
```

**Plan de Contingencia**: Usar solo APIs (Adzuna + JSearch) si scraping falla.

---

### R02: Cambios en Estructura de Sitios

**Descripción**: Indeed, LinkedIn, etc. cambian su HTML/APIs periódicamente.

**Probabilidad**: Media (1-2 veces al año)

**Impacto**: Alto (parser deja de funcionar)

**Mitigación**:
```python
# 1. Usar librería mantenida (JobSpy se actualiza)
# 2. Parseo flexible con múltiples patrones
patterns = [
    r'<div class="job-title">(.*?)</div>',
    r'<h2[^>]*>(.*?)</h2>',
    r'data-title="([^"]*)"'
]

# 3. Monitoreo automático
def check_parser_health():
    test_result = parse_sample_job()
    if not test_result:
        alert("Parser needs update")
```

**Plan de Contingencia**: Parche rápido o fallback a otras fuentes.

---

### R05: Datos Personales (GDPR)

**Descripción**: Almacenar nombre, email, teléfono del CV puede violar GDPR.

**Probabilidad**: Media

**Impacto**: Alto (multas)

**Mitigación**:
```python
# 1. NO almacenar PII en disco
# Solo procesar en memoria, no guardar nombre/email

# 2. Si se cachea, anonimizar
anonymized_cv = {
    "skills": cv["skills"],
    "experience_years": cv["experience"]["total_years"],
    "education_level": cv["education"][0]["degree"],
    # NO incluir: name, email, phone
}

# 3. Política de privacidad clara
# "JobMatch no almacena información personal. 
#  Los CVs se procesan en memoria y se descartan."
```

**Plan de Contingencia**: Eliminar cualquier PII almacenado si se detecta.

---

### R08: Scraping Ilegal

**Descripción**: Algunos sitios prohíben scraping en sus TOS.

**Probabilidad**: Baja (para uso personal)

**Impacto**: Alto (demandas, bans)

**Mitigación**:
```
1. Solo sitios que permiten scraping:
   - Indeed: Permitido para uso personal (no comercial)
   - LinkedIn: Prohibido explícitamente → No usar scraping directo
   - Glassdoor: Términos ambiguos → Usar con precaución

2. Alternativas legales:
   - Usar APIs oficiales cuando existan (Adzuna, JSearch)
   - Google for Jobs (vía JSearch) es legal

3. Límites éticos:
   - No hacer más de 100 requests/día por sitio
   - No re-vender datos
   - Respetar robots.txt
```

**Plan de Contingencia**: Eliminar scraping de sitios problemáticos, usar solo APIs.

---

## 3. Plan de Respuesta a Incidentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE RESPUESTA A INCIDENTES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│  │  Incidente  │────>│  Diagnóstico│────>│  Acción     │                  │
│  │  Detectado  │     │  (5 min)    │     │  Correctiva │                  │
│  └─────────────┘     └─────────────┘     └─────────────┘                  │
│         │                   │                   │                          │
│         ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                                                                     │  │
│  │  TIPO 1: Rate Limit (429)                                          │  │
│  │  → Acción: Esperar 60s, reintentar con otro proxy                  │  │
│  │  → Si persiste: Cambiar a fuente alternativa                       │  │
│  │                                                                     │  │
│  │  TIPO 2: Parser Error (KeyError, IndexError)                       │  │
│  │  → Acción: Log del error, usar fallback parser                     │  │
│  │  → Si persiste: Desactivar fuente, alertar usuario                 │  │
│  │                                                                     │  │
│  │  TIPO 3: API Error (401, 403)                                      │  │
│  │  → Acción: Verificar API key, intentar refresh                     │  │
│  │  → Si persiste: Desactivar API, usar otras fuentes                 │  │
│  │                                                                     │  │
│  │  TIPO 4: Google Sheets Error                                       │  │
│  │  → Acción: Verificar credenciales, reintentar                      │  │
│  │  → Si persiste: Exportar a CSV local como fallback                 │  │
│  │                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Monitoreo y Alertas

| Métrica | Umbral | Acción |
|---------|--------|--------|
| Tasa de éxito scraping | < 80% | Alerta, revisar parsers |
| Tiempo de respuesta API | > 10s | Revisar conectividad |
| Errores de match | > 5% | Revisar lógica de matching |
| Google Sheets writes | > 100/día | Revisar quota |

---

## 5. Backups y Recuperación

| Componente | Backup | Frecuencia |
|------------|--------|------------|
| Configuración (.env) | Git (privado) | Manual |
| CV parseado | No necesario (regenerable) | - |
| Historial de búsquedas | JSON export | Semanal |
| Google Sheets | Copia CSV local | Automático |

---

*Documento generado: Septiembre 2026*
