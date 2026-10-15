# Skills versionadas del proyecto

Esta carpeta (`.agents/skills/`) conserva las skills que complementan el flujo OPSX del entorno. Se leen
desde el repositorio para que cualquier integrante o agente trabaje con las mismas
guías, incluso al clonar el proyecto en otra máquina.

| Skill | Propósito | Fuente |
|---|---|---|
| `fastapi-templates` | Endpoints, dependencias y estructura de FastAPI. | `wshobson/agents` |
| `async-python-patterns` | Decidir y aplicar asincronía de forma coherente. | `wshobson/agents` |
| `python-testing-patterns` | Estrategias y organización de pruebas con pytest. | `wshobson/agents` |
| `postgresql-table-design` | Diseño PostgreSQL, restricciones e índices. | `wshobson/agents` |
| `security-best-practices` | Revisión y guía de desarrollo seguro para FastAPI y React. | `openai/skills` |

## Criterio de selección

No se agregó una skill de TDD porque el proyecto ya tiene ese flujo definido en sus
instrucciones y duplicarlo no aporta una regla nueva. Tampoco se agregó una skill de
Docker: los cambios de contenedores, volúmenes o entornos pueden afectar datos y se
revisan con las reglas del proyecto y Docker Compose existente, en lugar de incorporar
automatizaciones de mayor riesgo.

`async-python-patterns` es condicional: el backend actual usa FastAPI y SQLAlchemy de
forma síncrona. Solo se carga al diseñar un change que adopte una ruta totalmente async;
nunca para mezclar `Session` y `AsyncSession` en una misma cadena.

## Mantenimiento

Las skills de `.agents/skills/` deben mantenerse versionadas. Al agregar, actualizar o quitar
una, actualizar también `.atl/skill-registry.md` y las tablas de skills de `AGENTS.md`
y `CLAUDE.md`; no declarar una skill como disponible hasta que sus archivos estén en el
repositorio.
