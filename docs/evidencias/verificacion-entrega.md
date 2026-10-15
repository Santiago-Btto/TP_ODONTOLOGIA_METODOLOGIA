# Verificacion de entrega - turnos-odontologia

**Fecha de verificacion:** 2026-10-10 (actualiza la del 2026-10-09)
**Proyecto:** `turnos-odontologia`  
**Integrante/s:** Santiago Barretto / Mateo Algañaraz / Ezequiel Menéndez

Este documento separa evidencia verificable de lo que cada integrante todavía debe producir personalmente. No sustituye la verificación humana de fuentes ni la revisión final y autoría personal de la reflexión. Por indicación actual del equipo, el video queda fuera del alcance de esta verificación; este documento no afirma que la consigna original lo dispense.

## Resultado ejecutivo

El 2026-10-08 se aplicó **Ajustar** sobre la fundación porque el stack fijado inicialmente (Node.js + TypeScript en memoria) no tenía una decisión del equipo suficientemente justificada. La consigna permite definirlo desde la KB, por lo que DD-02 registra la elección del equipo: FastAPI, SQLAlchemy, PostgreSQL, JWT, Redis, Docker Compose y React + TypeScript + Vite. Se corrigieron knowledge-base, `AGENTS.md`/`CLAUDE.md` y `CHANGES.md`, y el change de alta de turnos se reimplementó y archivó como **C-01b** con 40 tests en verde contra PostgreSQL. También se agregó evidencia documental de la Etapa 0, evidencia recuperable de Engram y se completó el informe de Discovery (v1.2).

## Checklist de la consigna y evidencia concreta

| Requisito | Estado | Evidencia verificable / acción pendiente |
|---|---|---|
| Etapa 0: captura del instalador | Verificado | `docs/evidencias/capturas/active-stack-instalacion-completa.png` y `etapa-0-entorno.md`. |
| Etapa 0: harnesses instalados | Verificado | `docs/evidencias/capturas/active-stack-plan-instalacion.png` conserva la lista de 15 componentes seleccionados y la captura de finalización confirma “All steps succeeded”. |
| Repositorio con instrucciones, estado de fundación y registro de skills | Verificado | `AGENTS.md`, `CLAUDE.md` (sincronizados), `.active-orchestrator-state.json` (`step: "done"`, stack, `opsx` y cinco skills versionadas actualizados), `.atl/skill-registry.md` y `.agents/skills/`. |
| Discovery en Markdown y PDF | Verificado | `docs/discovery/informe-discovery.md` v1.2 y PDF regenerado con portada; checklist en `docs/discovery/checklist-discovery.md`. |
| Knowledge base con los 10 documentos canónicos | Verificado | DD-02 registra que el equipo eligió el stack tras Ajustar, conforme a la posibilidad de definirlo desde la KB; no lo atribuye a una imposición de la cátedra. |
| Roadmap alineado con la sección D | Verificado | `CHANGES.md`: se agregaron C-16 (recordatorio simulado), C-17 (datos mínimos de paciente) y C-15 (agenda web); camino crítico corregido. |
| Reglas del proyecto | Verificado | Reglas duras nuevas (secretos, reglas sólo en dominio, restricciones de base, transacción, pytest contra PostgreSQL) + regla propia de datos ficticios. |
| Change OPSX justificado y completo | Verificado | C-01 (stack anterior) y C-01b en `openspec/changes/archive/`; exploración en `docs/opsx/explore-crear-turno-fastapi.md`; justificación escrita en el `proposal.md` de C-01b. |
| Spec con escenarios DADO / CUANDO / ENTONCES (feliz, error, borde) | Verificado | `openspec/specs/creacion-de-turnos/spec.md`: 8 requisitos y 13 escenarios. |
| Tests por escenario en verde | Verificado por ejecución | `docs/evidencias/verificacion-c01b.md`: 40 passed desde un clon limpio; trazabilidad escenario → test. |
| README reproducible | Verificado (opciones A y B) | La opción local (Python + PostgreSQL) y la opción Docker Compose se ejecutaron desde clones limpios. El 2026-10-10, Docker construyó `api`, PostgreSQL alcanzó estado `healthy` y `docker compose run --rm api pytest` finalizó con `40 passed, 1 warning in 1.47s`. |
| Cinco fuentes comprobadas personalmente | Verificado con salvedad | Hay 6 fuentes verificadas el 2026-10-02. La corrección de Dental-IA de 2026-10-08 es documental/complementaria y sigue requiriendo confirmación humana; no se cuenta como una séptima verificación personal. |
| Momento de inspección “Ajustar” | Verificado | Discovery (2026-10-02) y fundación/stack (2026-10-08, commits `bc96daf`, `c5bab36`). |
| Engram: guardado y recuperación real | Verificado por salida de CLI | `engram-evidencia.md` conserva las salidas de `engram context` y `engram search`; recupera la observación #95 del antecedente y #113 de C-01b. No hay captura de la sesión original ni se declara una inexistente. |
| Video de defensa | Fuera de alcance en esta revisión | Se ignora por indicación actual del equipo. Verificar con la cátedra si la consigna lo exige para la entrega. |
| Reflexión escrita | Consistencia de contenido validada; autoría personal pendiente | `docs/evidencias/reflexion.md` fue contrastada con Discovery, KB, OPSX y evidencias en `validacion-reflexion.md`; describe DD-02 como decisión del equipo, no requisito externo. Cada integrante debe confirmar que representa su experiencia y ajustar lo que no sea propio. |
| Historial de commits con el proceso | Verificado | Commits del 2026-10-08 con autoría de Mateo Algañaraz: evidencia, Ajustar de KB/roadmap/reglas y ciclo OPSX completo de C-01b (explore → propose → apply → verify → archive). Santiago y Ezequiel deberían sumar commits propios de lo que condujeron. |
| Sin secretos ni datos reales | Verificado | Fixtures y semillas “Demo Ficticio”; `.env` ignorado; `.env.example` y `docker-compose.yml` sólo con credenciales de desarrollo local. |

## Comandos ejecutados

```text
cd backend
python -m venv .venv && .venv/Scripts/pip install -r requirements-dev.txt
TEST_DATABASE_URL=postgresql+psycopg://...@localhost:55432/turnos_test .venv/Scripts/python -m pytest -v
# 40 passed
```

El 2026-10-10, desde el clon limpio
`C:\Users\esteb\AppData\Local\Temp\tp-odontologia-verification-20261010`, se
ejecutó la opción Docker del README con el ejecutable de Docker Desktop:

```text
& 'C:\Program Files\Docker\Docker\resources\bin\docker.exe' compose run --rm api pytest
```

Docker descargó `postgres:17`, construyó la imagen `api` y esperó a que el
contenedor `db` estuviera `Healthy`. La suite recogió 40 casos y terminó así:

```text
======================== 40 passed, 1 warning in 1.47s =========================
```

El único warning fue una deprecación de Starlette `TestClient`: el alias
`anyio.abc.BlockingPortal` está deprecado.

## Pendientes que no se pueden simular

1. Confirmar personalmente la corrección de precios de Dental-IA (revisión documental/complementaria del informe).
2. Cada integrante debe revisar y confirmar como propia la reflexión antes de presentarla; la validación de contenido no certifica autoría humana individual.
3. Consultar a la cátedra si el video continúa siendo obligatorio; se excluyó de esta revisión sólo por indicación actual del equipo.
