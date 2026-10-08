# Verificacion de entrega - turnos-odontologia

**Fecha de verificacion:** 2026-10-08 (actualiza la del 2026-10-02)  
**Proyecto:** `turnos-odontologia`  
**Integrante/s:** Santiago Barretto / Mateo Algañaraz / Ezequiel Menéndez

Este documento separa evidencia verificable de lo que cada integrante todavía debe producir personalmente. No sustituye la verificación humana de fuentes ni la revisión final de la reflexión.

## Resultado ejecutivo

El 2026-10-08 se aplicó **Ajustar** sobre la fundación porque el stack fijado (Node.js + TypeScript en memoria) contradecía el definido para el Sistema Odontológico (FastAPI, SQLAlchemy, PostgreSQL, JWT, Redis, Docker Compose; React + TypeScript + Vite). Se corrigieron knowledge-base, `AGENTS.md`/`CLAUDE.md` y `CHANGES.md`, y el change de alta de turnos se reimplementó y archivó como **C-01b** con 40 tests en verde contra PostgreSQL. También se agregó la evidencia de la Etapa 0 y se completó el informe de Discovery (v1.2).

## Checklist de la consigna y evidencia concreta

| Requisito | Estado | Evidencia verificable / acción pendiente |
|---|---|---|
| Etapa 0: captura del instalador | Verificado | `docs/evidencias/etapa0-instalador-active-stack.jpg` y `etapa-0-entorno.md`. |
| Etapa 0: captura de la lista de harnesses | **Pendiente** | Falta una captura propia de la lista de harnesses instalados. |
| Repositorio con instrucciones, estado de fundación y registro de skills | Verificado | `AGENTS.md`, `CLAUDE.md` (sincronizados), `.active-orchestrator-state.json` (`step: "done"`, stack y `opsx` actualizados), `.atl/skill-registry.md`. |
| Discovery en Markdown y PDF | Verificado | `docs/discovery/informe-discovery.md` v1.2 y PDF regenerado con portada; checklist en `docs/discovery/checklist-discovery.md`. |
| Knowledge base con los 10 documentos canónicos | Verificado | Ajustada al stack definido (DD-02) el 2026-10-08. |
| Roadmap alineado con la sección D | Verificado | `CHANGES.md`: se agregaron C-16 (recordatorio simulado), C-17 (datos mínimos de paciente) y C-15 (agenda web); camino crítico corregido. |
| Reglas del proyecto | Verificado | Reglas duras nuevas (secretos, reglas sólo en dominio, restricciones de base, transacción, pytest contra PostgreSQL) + regla propia de datos ficticios. |
| Change OPSX justificado y completo | Verificado | C-01 (stack anterior) y C-01b en `openspec/changes/archive/`; exploración en `docs/opsx/explore-crear-turno-fastapi.md`; justificación escrita en el `proposal.md` de C-01b. |
| Spec con escenarios DADO / CUANDO / ENTONCES (feliz, error, borde) | Verificado | `openspec/specs/creacion-de-turnos/spec.md`: 8 requisitos y 13 escenarios. |
| Tests por escenario en verde | Verificado por ejecución | `docs/evidencias/verificacion-c01b.md`: 40 passed desde un clon limpio; trazabilidad escenario → test. |
| README reproducible | Verificado (opción B) | Opción local (Python + PostgreSQL) ejecutada desde un clon limpio. La opción Docker Compose **no se pudo ejecutar** (sin Docker en la máquina de verificación): probarla antes de entregar. |
| Cinco fuentes comprobadas personalmente | Verificado | 6 fuentes del 2026-10-02. La revisión complementaria del 2026-10-08 es automatizada: un integrante debe confirmar la corrección de Dental-IA abriendo la URL. |
| Momento de inspección “Ajustar” | Verificado | Discovery (2026-10-02) y fundación/stack (2026-10-08, commits `bc96daf`, `c5bab36`). |
| Engram: guardado y recuperación real | **Pendiente** | Se mencionan las observaciones #95 y #96; mostrarlas desde la sesión original. No inventar su contenido. |
| Video de defensa | No requerido | Según indicación de la cátedra. |
| Reflexión escrita | **Requiere actualización del equipo** | `docs/evidencias/reflexion.md` menciona TypeScript y `node:test`. La reflexión debe redactarla el equipo: agregar con voz propia el Ajustar de stack del 2026-10-08 y qué habría pasado sin él. |
| Historial de commits con el proceso | Verificado | Commits del 2026-10-08 con autoría de Mateo Algañaraz: evidencia, Ajustar de KB/roadmap/reglas y ciclo OPSX completo de C-01b (explore → propose → apply → verify → archive). Santiago y Ezequiel deberían sumar commits propios de lo que condujeron. |
| Sin secretos ni datos reales | Verificado | Fixtures y semillas “Demo Ficticio”; `.env` ignorado; `.env.example` y `docker-compose.yml` sólo con credenciales de desarrollo local. |

## Comandos ejecutados (2026-10-08)

```text
cd backend
python -m venv .venv && .venv/Scripts/pip install -r requirements-dev.txt
TEST_DATABASE_URL=postgresql+psycopg://...@localhost:55432/turnos_test .venv/Scripts/python -m pytest -v
# 40 passed
```

## Pendientes que no se pueden simular

1. Captura de la lista de harnesses instalados (Etapa 0).
2. Probar `docker compose up -d db` + `docker compose run --rm api pytest` en una máquina con Docker.
3. Confirmar personalmente la corrección de precios de Dental-IA (revisión complementaria del informe).
4. Actualizar la reflexión con el Ajustar de stack, redactado por el equipo.
5. Mostrar la recuperación real de Engram (#95, #96).
