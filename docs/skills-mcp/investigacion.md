# Ficha de investigación y planificación — skill propia y MCP

**TP Metodología I · Parte 1, puntos 1–4 · Consulta de fuentes: 29/10/2026**
**Proyecto:** sistema de turnos odontológicos · **Agente:** Codex · **Estado:** investigación; todavía no se instaló el MCP, creó la skill propia ni inició el nuevo change.

## 1. Necesidad real y change elegido

Elegimos **C-02 `consultar-agenda`**, pendiente en [CHANGES.md](../../CHANGES.md). Depende sólo de C-01b, ya archivado. La historia [US-002](../../knowledge-base/06_funcionalidades.md) pide consultar turnos por profesional y/o box. El alcance es `GET /api/v1/agenda`: rango obligatorio, filtros opcionales `profesional_id` y `box_id`, orden por inicio e inclusión por intersección. Sus pruebas previstas cubren consulta diaria, semanal, filtros combinados, rango vacío y exclusión.

La tarea repetible es **revisar escenarios antes de aprobar una especificación**. Pueden omitirse turnos que comienzan antes del rango y terminan dentro, límites contiguos, filtros combinados o zonas horarias. La skill contrastará esos casos con [RN-DI-01](../../knowledge-base/05_reglas_de_negocio.md). El MCP aportará documentación vigente de FastAPI y SQLAlchemy para diseñar el mismo change; las reglas del dominio siguen viniendo de la KB.

## 2. Skill creadora y diseño de la skill propia

La herramienta elegida es **`$skill-creator` de OpenAI**, compatible con Codex. Está incluida en esta instalación (`~/.codex/skills/.system/skill-creator/SKILL.md`): no requiere instalación adicional. Para comprobarla, buscarla en el selector de Codex o invocarla con `$skill-creator`; si no aparece, actualizar o reiniciar Codex. En la Parte 2 se la invocará con el diseño siguiente y se guardará la skill revisada en `.agents/skills/revisar-escenarios-agenda/SKILL.md`, con `name` y `description` YAML para que Codex la descubra. Fuentes: [guía oficial](https://learn.chatgpt.com/docs/build-skills) y [repositorio del autor](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/SKILL.md).

**Diseño previsto — `revisar-escenarios-agenda`:** se activará al explorar, proponer o revisar consultas de agenda. Recibirá C-02, US-002, RN-DI-01, modelo de Turno y borradores de proposal/spec/tasks. Extraerá reglas; contrastará intersección de intervalos semiabiertos `[inicio, fin)`, orden, filtros, rango vacío, zonas horarias y entradas inválidas; señalará contradicciones con la KB y propondrá escenarios sin editar artefactos. Entregará una matriz **regla → escenario → prueba → fuente** y preguntas pendientes. Se aceptará si cada observación es trazable y cubre funcionamiento esperado, error de negocio y borde. El equipo revisará sus sugerencias.

## 3. Comparación y elección de MCP

| Servidor existente | Capacidades y aporte a C-02 | Conexión, permisos y costo |
|---|---|---|
| **Context7 (Upstash)** | `resolve-library-id` busca la biblioteca; `query-docs` trae fragmentos de documentación. Ayuda a diseñar parámetros de FastAPI y consultas de SQLAlchemy. No necesita leer ni modificar el repositorio. | Compatible con Codex mediante MCP remoto HTTP o proceso local con Node. Cuenta/clave API para mayor límite; plan Free publicado de USD 0 y 1.000 llamadas mensuales, Pro opcional. Acceso previsto: sólo lectura de documentación pública. |
| **GitHub MCP Server (GitHub)** | Herramientas para repositorios, issues, PR y Actions; útil para inspección y colaboración, pero aporta menos a la duda técnica de C-02. | Compatible con Codex remoto por HTTP o local con Docker. La opción remota documentada requiere PAT; sus permisos pueden permitir lectura y escritura según scopes. No se encontró una tarifa del *servidor* claramente indicada en la guía consultada; confirmar costos o condiciones del servicio elegido antes de conectarlo. |

**Elegimos Context7** por su utilidad para el diseño y menor permiso. Contrastaremos los resultados con documentación oficial y la KB. Fuentes: [herramientas](https://github.com/upstash/context7), [instalación Codex](https://github.com/upstash/context7/blob/master/docs/clients/codex.mdx), [planes](https://context7.com/plans); alternativa [GitHub MCP](https://github.com/github/github-mcp-server) y [guía Codex](https://github.com/github/github-mcp-server/blob/main/docs/installation-guides/install-codex.md).

**Configuración prevista para la Parte 2:** crear una clave en el panel de Context7 y conservarla fuera del repositorio como variable `CONTEXT7_API_KEY`. Registrar el servidor remoto con `codex mcp add context7 --url https://mcp.context7.com/mcp --bearer-token-env-var CONTEXT7_API_KEY` (método de autenticación del [cliente Codex](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)). Comprobar `codex mcp list`, iniciar una sesión nueva y ejecutar `resolve-library-id` para FastAPI y `query-docs` sobre parámetros de consulta; repetir para filtros SQLAlchemy. Guardar solicitud, respuesta y aporte al diseño en la Parte 2. Límite: sólo consultas de documentación pública, sin datos reales de pacientes, credenciales en prompts ni operaciones de escritura.

## 4. Integración prevista y pendientes

En la Parte 2 se crearán la skill en `.agents/skills/`, su entrada en `.atl/skill-registry.md` y las instrucciones coherentes en `AGENTS.md`/`CLAUDE.md`. Se documentará la conexión MCP en `README.md` o un archivo enlazado; se prepararán proposal, design, specs y tasks de C-02 y se actualizará su referencia en `CHANGES.md`, sin declararlo implementado. La KB sólo cambiará si una decisión de dominio queda justificada. **Pendiente:** comprobar en una sesión nueva que Codex descubre la skill, que Context7 conecta y que una herramienta devuelve información útil; esas pruebas pertenecen a la Parte 2.
