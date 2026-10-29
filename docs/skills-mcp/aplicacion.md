# Informe de aplicación — Parte 2: skill propia y MCP

**Fecha:** 29/10/2026 · **Proyecto:** turnos odontológicos · **Change preparado:** C-02 `consultar-agenda`. Esta etapa produce artefactos de planificación OPSX; la implementación, sus pruebas y el archivado quedan para otra instancia. La [ficha de la Parte 1](investigacion.md) conserva las decisiones y fuentes investigadas en clase.

## Resultado y uso comprobado

Se creó con `skill-creator` la skill local [revisar-escenarios-agenda](../../.agents/skills/revisar-escenarios-agenda/SKILL.md), adaptada a US-002, RN-DI-01 y los intervalos `[inicio, fin)`. `quick_validate.py` devolvió `Skill is valid!`. En una **sesión independiente**, el agente encontró su trigger en el [registro](../../.atl/skill-registry.md) y en [AGENTS.md](../../AGENTS.md) sin recibir la ruta directa. La invocó sobre C-02 y devolvió una matriz regla/fuente → escenario Dado/Cuando/Entonces → prueba → estado. Detectó ausencia de contrato para rangos inválidos, combinación de filtros, límites contiguos, fechas sin zona y rango vacío. [Solicitud, resultado y aporte](evidencias/skill-uso.md).

**Cambio respecto de la ficha (skill creadora):** la ficha preveía usar la copia de sistema de Codex en `~/.codex/skills/.system/skill-creator`. En la práctica se usó la `skill-creator` ya instalada en el directorio global `~/.agents/skills/skill-creator/` por Active Stack durante la Etapa 0 ([evidencia del instalador](../evidencias/etapa-0-entorno.md)), que incluye el script `quick_validate.py`. Por eso no hizo falta una instalación adicional; para reproducirlo, otro integrante necesita esa misma instalación de Active Stack o invocar `$skill-creator` desde Codex.

El servidor **Context7 MCP** ya estaba conectado globalmente en modo `stdio`; se conservó esa conexión operativa en vez de crear una nueva conexión remota con clave, prevista en la ficha. `codex mcp get context7 --json` indicó `enabled: true`. Se ejecutaron `resolve-library-id` y `query-docs` para FastAPI y SQLAlchemy 2.0. FastAPI aclaró parámetros obligatorios/opcionales y la respuesta por omisión; SQLAlchemy orientó `select().where()`, `order_by()` y `Session.scalars()`. [Solicitudes y respuestas](evidencias/context7-uso.md); [instalación reproducible y límites](context7-configuracion.md), [configuración de ejemplo sin secretos](context7.example.toml).

La exploración y ambas incorporaciones alimentaron [proposal](../../openspec/changes/consultar-agenda/proposal.md), [design](../../openspec/changes/consultar-agenda/design.md), [spec](../../openspec/changes/consultar-agenda/specs/consulta-de-agenda/spec.md) y [tasks](../../openspec/changes/consultar-agenda/tasks.md). La spec prevé consulta diaria/semanal, filtros independientes y combinados, orden, rango vacío, error de rango inválido y borde de turnos contiguos; las tasks señalan cómo probarlos al implementar. `CHANGES.md` mantiene C-02 como change por implementar.

## Revisión crítica: antes y después

La primera consulta al MCP preguntó cómo usar filtros **UUID** en FastAPI. La respuesta era válida para la sintaxis del framework, pero aplicarla literalmente habría rechazado IDs existentes como `profesional-demo-001`. Se detectó al cotejar `backend/app/domain/turnos.py` (`str`), `backend/app/infrastructure/modelos.py` (`String(64)`) y las semillas. **Antes:** propuesta de filtros UUID. **Después:** C-02 especifica filtros de texto; un ID sin turnos coincidentes produce lista vacía. También se añadió validación explícita de zona horaria y `fin > inicio`: la respuesta del MCP no prueba esas reglas. La skill expuso el caso de contigüidad y los filtros combinados antes de cerrar los artefactos. La [evidencia del MCP](evidencias/context7-uso.md#revision-de-la-propuesta-antes-y-despues) permite seguir la corrección.

## Archivos y motivo

| Archivo o grupo | Motivo |
|---|---|
| `.agents/skills/revisar-escenarios-agenda/` | Fuente versionada y descubrible de la skill, con procedimiento y salida trazable. |
| `.atl/skill-registry.md`, `AGENTS.md`, `CLAUDE.md` | Registrar cuándo usar la skill y Context7, qué entradas necesitan y cómo revisar resultados. |
| `.active-orchestrator-state.json` | Mantener el estado de la fundación coherente: agrega la skill propia a `skills.installed` y registra Context7 como integración MCP. |
| `README.md`, `docs/skills-mcp/context7-configuracion.md`, `context7.example.toml` | Reproducir la conexión MCP global sin guardar secretos. |
| `openspec/changes/consultar-agenda/`, `CHANGES.md` | Preparar el change y mantener actualizado el roadmap sin declararlo ejecutado. |
| `docs/skills-mcp/evidencias/`, este informe, `ENTREGA.md` | Documentar invocaciones, revisión crítica y datos de presentación. |

**Límites:** Context7 aporta documentación técnica, no reglas odontológicas; la KB y las specs prevalecen. El video auténtico y su enlace accesible deben incorporarlos los integrantes en `ENTREGA.md` antes de presentar. No hay pruebas de implementación de C-02 ejecutadas en esta etapa. La visibilidad por rol y los turnos cancelados dependen de changes posteriores.
