# Guía para el video de demostración (máximo 5 minutos)

La consigna pide **uso real**, no sólo mostrar archivos. Graben la pantalla con una terminal en la raíz del repositorio y una sesión nueva del agente; participen los tres integrantes. Usen únicamente datos de prueba y oculten cualquier token o ruta privada que aparezca.

| Tiempo sugerido | Responsable | Mostrar y explicar |
|---|---|---|
| 0:00–0:45 | Integrante 1 | Presentar C-02 `consultar-agenda`, US-002, dependencia C-01b y por qué se prepara ahora. Abrir `CHANGES.md` y `docs/skills-mcp/investigacion.md`. |
| 0:45–1:50 | Integrante 1 | Abrir `.agents/skills/revisar-escenarios-agenda/SKILL.md`, su entrada en `.atl/skill-registry.md` y las referencias en `AGENTS.md`/`CLAUDE.md`. En una sesión nueva, pedir una revisión de C-02 sin dar la ruta: mostrar que el agente encuentra la skill y devuelve una fila de éxito, una de error y una de borde. |
| 1:50–3:05 | Integrante 2 | Ejecutar `codex mcp list --json`; luego, en el agente, invocar Context7 `resolve-library-id` para FastAPI y `query-docs` sobre parámetros obligatorios/opcionales o para SQLAlchemy sobre `select().where()`. Mostrar identificador de biblioteca y fuente obtenida. Explicar que Context7 aporta documentación técnica y que la KB decide reglas del negocio. |
| 3:05–4:20 | Integrante 3 | Abrir `openspec/changes/consultar-agenda/` y mostrar `proposal.md`, `design.md`, `specs/consulta-de-agenda/spec.md`, `tasks.md`. Mostrar un escenario de éxito, uno de entrada inválida y el borde de intervalos contiguos, con sus pruebas previstas. Ejecutar `openspec status --change consultar-agenda --json` para evidenciar que el change está preparado, sin implementarlo ni archivarlo. |
| 4:20–4:50 | Integrante 3 | Explicar la revisión crítica: la primera pregunta al MCP suponía UUID, pero el modelo y semillas usan IDs de texto; mostrar el antes/después en `docs/skills-mcp/evidencias/context7-uso.md`. Cerrar con límites: no se hicieron tests de C-02 porque sólo se planificó. |

Antes de publicar, comprueben que el enlace del video sea accesible sin permisos especiales y que su duración no supere 5 minutos. Coloquen el enlace real y los nombres completos en `ENTREGA.md`; no sustituyan la demostración por este guion.
