# Decisión de skills para el proyecto

Fecha de actualización: 2026-10-15.

## Contexto actual

El proyecto es una API de turnos odontológicos en Python 3.12, FastAPI,
SQLAlchemy 2.0 y PostgreSQL 17. Docker Compose reproduce la API y la base de
datos, y `pytest` verifica dominio, aplicación, infraestructura y API contra
PostgreSQL real. Las reglas de disponibilidad requieren `CHECK`, `btree_gist`
y restricciones `EXCLUDE`; por eso se incorporaron skills específicas al
repositorio, sin reemplazar OPSX ni las reglas de `AGENTS.md`.

## Skills instaladas y decisión

| Skill | Fuente | Aporte al proyecto | Decisión |
|---|---|---|---|
| `fastapi-templates` | [`wshobson/agents`](https://github.com/wshobson/agents) | Endpoints, dependencias, esquemas y errores de FastAPI. | **Instalada** en `.agents/skills/fastapi-templates`. Se adapta a la arquitectura por capas y al camino síncrono vigente. |
| `async-python-patterns` | [`wshobson/agents`](https://github.com/wshobson/agents) | Criterios para elegir asincronía y evitar bloquear el event loop. | **Instalada, uso condicional** en `.agents/skills/async-python-patterns`. Solo se carga si un change aprueba migrar una ruta completa a async; no se mezcla con `Session` síncrona. |
| `python-testing-patterns` | [`wshobson/agents`](https://github.com/wshobson/agents) | Fixtures, aislamiento y cobertura de pruebas pytest. | **Instalada** en `.agents/skills/python-testing-patterns`. Los tests de repositorio y API siguen usando PostgreSQL real, no mocks de la base. |
| `postgresql-table-design` | [`wshobson/agents`](https://github.com/wshobson/agents) | Tipos, índices y restricciones propios de PostgreSQL. | **Instalada** en `.agents/skills/postgresql-table-design`. Refuerza el uso de `CHECK` y `EXCLUDE` para evitar solapamientos. |
| `security-best-practices` | [`openai/skills`](https://github.com/openai/skills) | Guía secure-by-default y revisión de seguridad para FastAPI y React. | **Instalada** en `.agents/skills/security-best-practices`. Se carga ante pedido explícito de revisión/guía de seguridad o para escribir código secure-by-default autorizado; no inicia auditorías automáticas. |

## Decisiones de alcance

- No se instala una skill de TDD: el proyecto ya define su disciplina de pruebas en
  las instrucciones y una segunda autoridad duplicaría reglas.
- No se instala una skill de patrones Docker: cambios de imágenes, volúmenes y
  entornos pueden tener impacto alto; se revisan con Docker Compose, la
  knowledge base y las reglas específicas del repositorio.
- Las skills se mantienen versionadas en `.agents/skills/`; al cambiarlas se actualizan
  `.atl/skill-registry.md`, `AGENTS.md` y `CLAUDE.md`.

La selección no reemplaza el flujo OpenSpec/OPSX: cada cambio sigue requiriendo
proposal, diseño, pruebas contra PostgreSQL real y archivo al completarse.
