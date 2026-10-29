# Turnos de odontología

Sistema de turnos y agenda para consultorios odontológicos (mercado argentino), construido con Spec-Driven Development (OpenSpec) y Active Stack.

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 · PostgreSQL 17 · JWT (C-08) · Redis (C-16) · Docker Compose — React + TypeScript + Vite (C-15).

**Estado actual:** está implementado el alta de turnos sin solapamientos por profesional ni por box (change C-01b). Los intervalos son semiabiertos `[inicio, fin)`: un turno que empieza exactamente cuando termina otro se admite. PostgreSQL impone la misma regla con restricciones `EXCLUDE USING gist`, así que ni siquiera una escritura que eluda la aplicación puede generar una doble reserva.

> La API todavía no tiene autenticación (llega con C-08): es sólo para desarrollo local. Todos los datos son ficticios.

## Estructura

```text
backend/            API FastAPI, dominio, casos de uso, persistencia y tests (pytest)
docker-compose.yml  PostgreSQL + API para desarrollo local
knowledge-base/     Base de conocimiento del proyecto
.agents/skills/     Skills locales versionadas y skills OPSX del proyecto
openspec/           Specs vigentes y changes archivados
docs/               Discovery, exploraciones OPSX y evidencias
CHANGES.md          Roadmap de changes
```

## Correr los tests

Los tests de dominio y de casos de uso no necesitan base de datos. Los de persistencia y API corren contra un PostgreSQL real indicado en `TEST_DATABASE_URL`; **su esquema se borra y se recrea**, así que tiene que ser una base descartable.

### Opción A — Docker Compose

Requisitos: Docker con Docker Compose v2.

```bash
docker compose up -d db
```

```bash
docker compose run --rm api pytest
```

El servicio `db` crea la base `turnos` y la base descartable `turnos_test` (credenciales de desarrollo `turnos` / `turnos`, sólo válidas en este compose).

### Opción B — Python y PostgreSQL locales

Requisitos: Python 3.12 y PostgreSQL 15 o posterior con la extensión `btree_gist` (viene con el paquete estándar/contrib).

1. Crear una base vacía para los tests, por ejemplo `turnos_test`.
2. Instalar dependencias:

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt   # Windows (Git Bash)
# .venv/bin/pip install -r requirements-dev.txt     # Linux / macOS
```

3. Ejecutar la suite, indicando la base descartable:

```bash
TEST_DATABASE_URL="postgresql+psycopg://USUARIO:CLAVE@localhost:5432/turnos_test" .venv/Scripts/python -m pytest -v
```

En PowerShell: `$env:TEST_DATABASE_URL = "postgresql+psycopg://..."; .venv\Scripts\python -m pytest -v`.

Resultado esperado: `40 passed`.

## Levantar la API

```bash
docker compose up -d
```

```bash
docker compose run --rm api python -m app.infrastructure.semillas
```

- Documentación interactiva: http://localhost:8000/docs
- Salud: `GET http://localhost:8000/health`
- Alta de turno:

```bash
curl -X POST http://localhost:8000/api/v1/turnos -H "content-type: application/json" -d '{"paciente_id":"paciente-demo-001","profesional_id":"profesional-demo-001","box_id":"box-demo-001","prestacion_id":"prestacion-demo-001","inicio":"2030-01-10T09:00:00-03:00"}'
```

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `201` | Turno creado | — |
| `404` | Paciente, profesional, box o prestación inexistente | `recurso_inexistente` |
| `409` | El profesional o el box ya tienen un turno activo que se solapa | `conflicto_profesional` / `conflicto_box` |
| `422` | Fin no posterior al inicio, prestación con duración no positiva, fecha sin zona horaria o datos mal formados | `intervalo_invalido` / `duracion_invalida` |

Sin Docker: definir `DATABASE_URL` (ver `backend/.env.example`), ejecutar `python -m app.infrastructure.semillas` y `uvicorn app.api.main:app --reload` desde `backend/`.

## Proceso (SDD / OPSX)

- Discovery: [docs/discovery/informe-discovery.md](docs/discovery/informe-discovery.md) (y su PDF).
- Spec vigente: [openspec/specs/creacion-de-turnos/spec.md](openspec/specs/creacion-de-turnos/spec.md).
- Changes archivados: [openspec/changes/archive/](openspec/changes/archive/).
- Evidencias de entrega: [docs/evidencias/](docs/evidencias/).

## Skill propia y Context7 para C-02

La [ficha de investigación](docs/skills-mcp/investigacion.md) explica la elección de una skill de revisión de escenarios y del MCP Context7 para preparar la consulta de agenda. La [guía de Context7](docs/skills-mcp/context7-configuracion.md) detalla requisitos, configuración reproducible sin secretos, comprobación y límites; el [registro de uso](docs/skills-mcp/evidencias/context7-uso.md) muestra herramientas reales y su aporte. Context7 se configura en el `~/.codex/config.toml` personal, no dentro del repositorio.

La [skill de revisión de agenda](.agents/skills/revisar-escenarios-agenda/SKILL.md) está versionada en el proyecto y [su evidencia de uso](docs/skills-mcp/evidencias/skill-uso.md) muestra el hallazgo de escenarios faltantes. El [informe de aplicación](docs/skills-mcp/aplicacion.md) resume cambios, revisión crítica y límites. La [guía de video](docs/skills-mcp/guion-video.md) y [ENTREGA.md](ENTREGA.md) ayudan a completar la presentación del equipo.
