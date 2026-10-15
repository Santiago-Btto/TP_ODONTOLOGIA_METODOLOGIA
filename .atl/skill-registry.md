# Registro de skills — turnos-odontologia

Este registro indica qué skills están disponibles y cuándo corresponde cargarlas. Las
skills de `skills/` son parte del repositorio y se versionan junto con el código; no se
debe asumir que una skill recomendada en otro proyecto está instalada aquí.

## Skills locales del proyecto

| Skill y ruta | Trigger | Reglas compactas para este proyecto |
|---|---|---|
| [`fastapi-templates`](../skills/fastapi-templates/SKILL.md) | Crear o modificar endpoints FastAPI, esquemas Pydantic, dependencias o manejo de errores. | Mantener la API como adaptador HTTP: rutas y `Depends` delegan a aplicación; el dominio no importa FastAPI ni SQLAlchemy. El camino vigente es síncrono con `Session` de SQLAlchemy; no introducir `async def` ni `AsyncSession` de forma aislada. |
| [`async-python-patterns`](../skills/async-python-patterns/SKILL.md) | Solo si un change aprobado adopta explícitamente asincronía para toda una ruta de E/S. | Diseñar primero la migración completa: handlers `async`, engine/`AsyncSession`, repositorios y pruebas compatibles. No mezclar sesiones, llamadas bloqueantes ni rutas sync/async en una misma cadena. No aplica al backend síncrono actual. |
| [`postgresql-table-design`](../skills/postgresql-table-design/SKILL.md) | Diseñar o revisar tablas, tipos, claves, restricciones, índices o migraciones PostgreSQL 17. | Usar PostgreSQL real y cambios reproducibles por Docker. Conservar `CHECK (fin > inicio)`, `btree_gist` y las restricciones `EXCLUDE USING gist` que impiden solapamientos; indexar FKs y caminos de consulta reales. |
| [`python-testing-patterns`](../skills/python-testing-patterns/SKILL.md) | Agregar, modificar o diagnosticar pruebas `pytest` de dominio, aplicación, infraestructura o API. | Preferir tests deterministas con datos ficticios y fixtures aisladas. Los tests de repositorio y API se ejecutan contra `TEST_DATABASE_URL` en PostgreSQL real: no reemplazar esa garantía con mocks de PostgreSQL. Cubrir éxito y errores de negocio, incluidos `409` por solapamiento. |
| [`security-best-practices`](../skills/security-best-practices/SKILL.md) | Pedido explícito de revisión/guía de seguridad, o escritura autorizada de código secure-by-default. | Leer la guía de Python/FastAPI y, si entra frontend, la de React/TypeScript. Mantener secretos en variables de entorno y no datos reales de pacientes. La skill no inicia una auditoría automática por cualquier change de auth. |

## Skills OPSX disponibles en el entorno

| Skill | Uso |
|---|---|
| `openspec-explore` | Relevar el problema y el estado del código antes de proponer un change. |
| `openspec-propose` | Crear o revisar proposal, design, specs y tasks de un change. |
| `openspec-update-change` | Ajustar de forma controlada los artefactos de un change existente. |
| `openspec-apply-change` | Implementar las tasks contra la especificación y el diseño aprobados. |
| `openspec-sync-specs` | Sincronizar las especificaciones vigentes después de completar un change. |
| `openspec-archive-change` | Verificar y archivar un change terminado. |

## Resolución antes de aplicar un change

1. Consultar `CHANGES.md`, la knowledge base indicada y el estado del change con OpenSpec.
2. Elegir las skills por el tipo de tarea y leer sus `SKILL.md` antes de editar.
3. Mantener el backend actual íntegramente síncrono, salvo que el diseño de un change apruebe una migración async completa.
4. Cumplir siempre `AGENTS.md` / `CLAUDE.md`: datos exclusivamente ficticios, secretos fuera del repositorio, disponibilidad en dominio, `CHECK` y `EXCLUDE` en PostgreSQL, e historial de turno en la misma transacción.
5. Verificar con `pytest` contra PostgreSQL real mediante Docker Compose antes de archivar; no hay una skill local de TDD ni de Docker instalada.
