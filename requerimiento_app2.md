# IQ TEST – ESPECIFICACIÓN FINAL (ANVIL-ONLY, SIMPLE, CACHE SERVER-SIDE)

## 1. Objetivo del sistema
Aplicación web en **Anvil** para realizar un **test de IQ estimado (80–200)**, de carácter recreativo, viral y de bajo costo operativo, con:
- backend 100% Anvil (Server Modules),
- persistencia mínima en Data Tables,
- **cache server-side en JSON usando Data Tables**,
- frontend nativo Anvil + librerías por CDN,
- sin APIs externas, sin workers, sin procesos complejos.

---

## 2. Restricciones explícitas
**Permitido**
- Anvil Forms
- Anvil Server Modules
- Anvil Data Tables
- Native Libraries (CDN)
- Python estándar

**No permitido**
- FastAPI / Flask / ASGI
- Bases externas (Postgres, MySQL, etc.)
- Redis / Memcached
- ORMs
- Cron jobs / background tasks
- Uplink
- CDN externo

---

## 3. Arquitectura general

[ Browser ]
|
| (Anvil internal calls)
v
[ Anvil Forms ]
|
v
[ Server Modules ]
|
v
[ Data Tables ]

yaml
Copiar código

El **cache JSON** se resuelve íntegramente en Data Tables.

---

## 4. Estructura del proyecto Anvil

### 4.1 Forms (UI)
- `LandingForm`
- `TestForm`
- `ResultForm`
- `AdminForm`

### 4.2 Server Modules
- `svc_tests`
- `svc_sessions`
- `svc_scoring`
- `svc_cache`
- `svc_analytics`
- `svc_admin`

---

## 5. Data Tables (esquema final)

### 5.1 `tests`
| campo | tipo |
|------|------|
| slug | text (unique) |
| title | text |
| lang | text |
| is_active | bool |
| published_version | number |

---

### 5.2 `test_versions`
| campo | tipo |
|------|------|
| test_slug | text |
| version | number |
| status | text (`draft` / `published`) |
| config | simpleObject |

`config`:
```json
{
  "n_items": 15,
  "show_percentile": true
}
5.3 item_bank
campo	tipo
test_slug	text
version	number
item_id	text
domain	text (`matrix
difficulty	number (1–5)
prompt	text
options	simpleObject
correct	text
explanation	text (opcional)

5.4 sessions
campo	tipo
session_id	text (unique)
test_slug	text
version	number
status	text (`started
started_at	datetime
finished_at	datetime
current_index	number
current_difficulty	number
score_raw	number
answers_count	number
result_iq	number
result_percentile	number
share_token	text

5.5 analytics_daily
campo	tipo
date	date
test_slug	text
version	number
starts	number
finishes	number
avg_time_sec	number

5.6 cache_kv (CACHE SERVER-SIDE)
campo	tipo
key	text (unique)
value	simpleObject
expires_at	datetime

6. Cache server-side (JSON)
6.1 Principio
Todo JSON reutilizable se cachea en cache_kv.

6.2 Funciones estándar (svc_cache)
python
Copiar código
def cache_get(key):
    row = app_tables.cache_kv.get(key=key)
    if row and row['expires_at'] > anvil.server.now():
        return row['value']
    return None

def cache_set(key, value, ttl_seconds):
    expires = anvil.server.now() + datetime.timedelta(seconds=ttl_seconds)
    app_tables.cache_kv.add_row(
        key=key,
        value=value,
        expires_at=expires
    )
6.3 Claves cacheadas
key	contenido	TTL
catalog	tests activos	300s
test:{slug}	metadata + versión	300s
items:{slug}:{version}:{difficulty}	pool ítems	600s

7. Lógica del test
7.1 Inicio
difficulty inicial = 3

score_raw = 0

answers_count = 0

7.2 Selección de ítems (semi-adaptativo)
Correcto → difficulty +1 (máx 5)

Incorrecto → difficulty -1 (mín 1)

Se elige ítem no usado de ese nivel

8. Scoring (simple y estable)
8.1 Score crudo
ini
Copiar código
score_raw = cantidad de respuestas correctas
8.2 Conversión IQ
ini
Copiar código
p = score_raw / n_items
iq = round(80 + p * 120)
Rango garantizado: 80 – 200

8.3 Percentil interno
ini
Copiar código
percentile = round(p * 100)
Mostrar siempre como “percentil interno (no clínico)”

9. Server Functions (contrato interno)
svc_tests
get_catalog()

get_test(slug)

svc_sessions
start_session(slug)

submit_answer(session_id, item_id, answer)

finish_session(session_id)

svc_scoring
evaluate_answer(session, item, answer)

compute_iq(session)

svc_analytics
track_start(slug, version)

track_finish(slug, version, duration)

svc_admin
CRUD ítems

Publicar versión

10. UI (Forms)
LandingForm
Título + CTA

Botón iniciar test

TestForm
Pregunta actual

Opciones

Progreso X / N

ResultForm
IQ estimado

Percentil

Botón copiar link

Disclaimer

AdminForm
Selector test / versión

CRUD ítems

Publicar

11. Librerías por CDN (Native Libraries)
html
Copiar código
<!-- Bootstrap -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<!-- SweetAlert2 (opcional) -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<!-- Bootstrap Icons (opcional) -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
12. Seguridad y anti-abuso (mínimo)
Máx 3 sesiones activas por usuario

Duración mínima válida: 45s

Sesiones sospechosas excluidas de analytics

13. Disclaimer obligatorio
“Este test ofrece una estimación recreativa de inteligencia.
No constituye un test clínico ni diagnóstico profesional.”

14. Resultado final
100% desplegable en Anvil

DB pequeña

Cache JSON server-side

Código simple y mantenible

Listo para tráfico moderado y viralidad controlada
