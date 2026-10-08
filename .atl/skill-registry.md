# Skill Registry — turnos-odontologia

Generado para el proyecto `turnos-odontologia`.

## Skills disponibles en el repositorio

| Skill | Uso |
|---|---|
| `openspec-explore` | Relevamiento del estado del código y del problema antes de proponer un change. |
| `openspec-propose` | Generación y revisión de proposal, design, specs y tasks. |
| `openspec-update-change` | Ajustes controlados de los artefactos de un change. |
| `openspec-apply-change` | Implementación de las tasks contra la especificación aprobada. |
| `openspec-sync-specs` | Sincronización de especificaciones vigentes después de un change. |
| `openspec-archive-change` | Verificación y archivo de un change terminado. |

## Skills recomendadas y decisión para el MVP

No se instaló ninguna skill adicional. `docs/skill-recommendations.md` documenta las
opciones evaluadas y sus motivos.

- TDD adicional: diferido porque el proyecto ya exige un flujo TDD explícito.
- `webapp-testing`: diferido. Con el ajuste de stack (2026-10-08) el MVP sí incluye una agenda web React (C-15); se reevalúa al proponer ese change.
- `vercel-optimize`: no aplicable porque no hay despliegue en Vercel.

## Regla de uso

Antes de actuar sobre un change, el agente debe cargar la skill correspondiente y
respetar las reglas de `AGENTS.md` / `CLAUDE.md` y la knowledge-base.
