# Entrega — TPI Metodología I

**Proyecto:** sistema de turnos y agenda para consultorios odontológicos.

**Repositorio:** https://github.com/Santiago-Btto/TP_ODONTOLOGIA_METODOLOGIA

**Equipo (3 integrantes):**

1. Santiago Barretto
2. Mateo Algañaraz
3. Ezequiel Menéndez

**Video (hasta 10 minutos, accesible):** se informa en el `.txt` que se sube al campus.

**Commit de entrega:** el último commit de `main` al momento de subir el `.txt`.

## Alcance presentado

Mínimo exigido por la consigna: 2 changes × 3 integrantes = **6**. Se presentan **10 changes del MVP** completos: propuestos, aplicados, verificados y archivados en [openspec/changes/archive/](openspec/changes/archive/).

| Change | Resultado | Archivado |
|---|---|---|
| C-01b `crear-turno-sin-solapamientos-fastapi` | Alta de turnos sin solapamientos (dominio + `EXCLUDE USING gist`) | 2026-10-08 |
| C-02 `consultar-agenda` | Consulta de agenda por rango, profesional y box | 2026-10-30 |
| C-03 `bloquear-disponibilidad` | Bloqueos de profesional o box | 2026-10-30 |
| C-05 `cancelar-y-confirmar-turnos` | Confirmación y cancelación con historial | 2026-11-02 |
| C-04 `reprogramar-turno-atomicamente` | Reprogramación atómica con historial antes/después | 2026-11-02 |
| C-08 `autenticar-con-jwt` | Login JWT, roles y actor trazable | 2026-11-02 |
| C-16 `recordatorio-simulado-con-redis` | Recordatorio simulado con Redis y worker | 2026-11-02 |
| C-17 `registrar-paciente-minimo` | Alta y búsqueda de pacientes con datos mínimos | 2026-11-02 |
| C-15 `agenda-web-react` | Agenda web React conectada a la API | 2026-11-03 |
| C-06 `flujo-mvp-docker-compose` | MVP integrado en Docker Compose con E2E | 2026-11-03 |

C-01 (stack Node.js en memoria) también está archivado, pero su código fue reemplazado por C-01b y **no se cuenta** para el mínimo. Lo pendiente (C-07, C-09 a C-14) está en [CHANGES.md](CHANGES.md) y en la sección "Completo y pendiente" del [README](README.md).

## Skill propia y MCP

- **Skill propia:** [`revisar-escenarios-agenda`](.agents/skills/revisar-escenarios-agenda/SKILL.md), creada con `skill-creator` y registrada en [`.atl/skill-registry.md`](.atl/skill-registry.md) y [AGENTS.md](AGENTS.md). Aplicada a C-02 antes de aprobar la spec: [evidencia y cierre](docs/skills-mcp/evidencias/skill-uso.md).
- **MCP:** Context7 (`resolve-library-id`, `query-docs`) para FastAPI y SQLAlchemy durante el diseño de C-02: [configuración sin secretos](docs/skills-mcp/context7-configuracion.md) y [registro de uso](docs/skills-mcp/evidencias/context7-uso.md).
- **Informe de aplicación:** [docs/skills-mcp/aplicacion.md](docs/skills-mcp/aplicacion.md).

## Verificación

Resultados y comandos de la última corrida: [docs/evidencias/verificacion-tpi.md](docs/evidencias/verificacion-tpi.md).

## Antes de subir el `.txt`

- [ ] Video grabado (máximo 10 minutos, los tres hablan, cámara encendida en la presentación personal).
- [ ] Enlace del video abierto sin permisos especiales (probado en ventana privada).
- [ ] Repositorio público o con acceso para el docente.
- [ ] `.txt` con comisión, enlace al video, enlace al repositorio, cantidad de integrantes y nombres completos.
