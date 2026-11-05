# Verificación del TPI

**Fecha:** 2026-11-05 · **Commit verificado:** `a690d8b` (rama `tpi/preparar-entrega`) · **Alcance:** los 10 changes del MVP (C-01b, C-02, C-03, C-04, C-05, C-08, C-16, C-17, C-15, C-06).

Esta verificación separa lo **ejecutado** de lo que el equipo debe **completar con Docker** antes de grabar. Todos los datos son ficticios; ningún comando imprime el `.env`.

## 1. Ejecutado desde un clon limpio, sin Docker (Opción B del README)

Entorno: Linux, Python 3.12.3, Node 22, PostgreSQL 16.15 y Redis 7.0.15 locales y descartables. Dependencias: FastAPI 0.115.6, SQLAlchemy 2.0.36, psycopg 3.2.3, redis-py 5.2.0.

| Paso | Comando | Resultado |
|---|---|---|
| Configuración local | `python backend/scripts/preparar_entorno.py` | `.env` generado, ignorado por Git, idéntico al repetir |
| Dependencias backend | `pip install -r requirements-dev.txt` | OK |
| Suite backend contra PostgreSQL real | `TEST_DATABASE_URL=…/turnos_test python -m pytest -q` | **422 passed**, 1 warning (deprecación de Starlette `TestClient`) |
| Tests de C-02 (skill y MCP aplicados) | `pytest tests/application/test_consultar_agenda.py tests/infrastructure/test_consultar_agenda.py tests/api/test_agenda_api.py` | 33 passed |
| Frontend | `npm ci` · `npm test -- --run` · `npm run build` | 24 passed · build TypeScript `strict` OK |
| Configuración Compose | `docker compose config --quiet` (normal y con `docker-compose.e2e.yml`) | OK |
| Comprobación Compose | `python backend/scripts/check_compose_mvp.py` | 4 tests OK (incluye `restart: unless-stopped` del worker) |
| Datos demo | `python -m app.infrastructure.bootstrap_demo` dos veces | "Datos Demo y usuario de recepción listos." ambas veces (idempotente) |
| API | `uvicorn app.api.main:app` | `/health` → `{"estado":"ok","base_de_datos":"ok"}`; `/docs` → 200 |
| E2E HTTP del MVP (corrida 1, base nueva) | `pytest scripts/test_mvp_http.py` con `MVP_API_URL` y `MVP_WEB_URL` | 1 passed |
| E2E HTTP del MVP (corrida 2, base nueva) | ídem | 1 passed |
| Resiliencia del worker | Redis detenido 6 s y reiniciado con el worker en marcha; luego E2E | Worker siguió activo, registró 2 avisos de reconexión y el E2E (que espera el recordatorio) pasó |

El E2E recorre login, paciente, turno, agenda, bloqueo y rechazo `409`, reprogramación, recordatorio simulado, cancelación y reutilización del horario. En esta corrida el proxy web fue el servidor de desarrollo de Vite (`/api` → API); en Compose lo hace Nginx.

Comprobaciones manuales por HTTP (auditoría del 2026-11-05): 401 sin token, con firma alterada y con `alg:none`; 403 para `odontologo` en agenda ajena, alta de turnos y pacientes; 409 por solapamiento, bloqueo sobre turno, reconfirmación y reprogramación de un cancelado; 201 en turno contiguo; 422 sin zona horaria, rango inválido, campo clínico (`dni`) y reprogramación sin cambios; 404 por recurso inexistente; alta y agenda siguen respondiendo con Redis detenido (RN-EX-02).

## 2. Pendiente de ejecutar con Docker (antes de grabar)

En el entorno de esta verificación no había acceso a Docker Hub, así que no se pudieron descargar las imágenes. Un integrante debe correr, desde un clon limpio de `main` ya actualizado:

```bash
python backend/scripts/preparar_entorno.py
docker compose up -d --build
docker compose ps
docker compose run --rm --no-deps api pytest -q
python backend/scripts/ejecutar_e2e.py
```

y completar esta tabla con la salida real:

| Comando | Resultado esperado | Resultado obtenido |
|---|---|---|
| `docker compose ps` | `db`, `redis`, `api` healthy; `frontend` y `worker` running; `bootstrap` exited (0) | |
| `docker compose run --rm --no-deps api pytest -q` | `422 passed` | |
| `python backend/scripts/ejecutar_e2e.py` | `1 passed` y desmontaje del entorno aislado | |
| `http://localhost:5173` | Login de `recepcion.demo` y agenda visible | |
