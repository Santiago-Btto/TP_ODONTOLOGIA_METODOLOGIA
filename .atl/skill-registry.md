# Registro de skills — turnos-odontologia

**Uso del delegador.** Antes de asignar una tarea, resolver la skill aplicable en este
registro e inyectar sus reglas compactas al agente executor. Las skills locales están
versionadas en [`.agents/skills/`](../.agents/skills/) junto con las skills OPSX; no se
debe declarar disponible una skill que no tenga su `SKILL.md` en el repositorio.

## Skills locales del proyecto

| Trigger | Skill | Ruta |
|---|---|---|
| Endpoints, esquemas Pydantic, dependencias, errores o estructura FastAPI. | `fastapi-templates` | [`.agents/skills/fastapi-templates/SKILL.md`](../.agents/skills/fastapi-templates/SKILL.md) |
| API async, concurrencia de E/S, tiempo real, colas o una migración async completa. | `async-python-patterns` | [`.agents/skills/async-python-patterns/SKILL.md`](../.agents/skills/async-python-patterns/SKILL.md) |
| Tests Python/pytest, TDD, fixtures, integración, API, base de datos o CI. | `python-testing-patterns` | [`.agents/skills/python-testing-patterns/SKILL.md`](../.agents/skills/python-testing-patterns/SKILL.md) |
| Tablas, tipos, constraints, índices, migraciones, JSON o particiones PostgreSQL. | `postgresql-table-design` | [`.agents/skills/postgresql-table-design/SKILL.md`](../.agents/skills/postgresql-table-design/SKILL.md) |
| Pedido explícito de guía/revisión de seguridad o código secure-by-default autorizado. | `security-best-practices` | [`.agents/skills/security-best-practices/SKILL.md`](../.agents/skills/security-best-practices/SKILL.md) |
| Planificación o revisión de escenarios de consulta de agenda, especialmente C-02: rangos, filtros, orden, errores y trazabilidad. | `revisar-escenarios-agenda` | [`.agents/skills/revisar-escenarios-agenda/SKILL.md`](../.agents/skills/revisar-escenarios-agenda/SKILL.md) |

## Reglas compactas

Las siguientes reglas combinan los `SKILL.md` versionados con las restricciones
específicas de `AGENTS.md`/`CLAUDE.md`. Si una regla genérica entra en conflicto con el
proyecto, prevalece la regla específica del proyecto.

### fastapi-templates

- Mantener la separación API, servicios/casos de uso, repositorios y modelos/esquemas; el dominio no importa FastAPI ni SQLAlchemy.
- Versionar rutas bajo `api/v1` y centralizar su composición; el router sólo traduce HTTP hacia la aplicación.
- Usar `Depends` para sesión, autorización, configuración y lógica transversal; no duplicar esas responsabilidades en endpoints.
- Separar esquemas Pydantic de modelos de persistencia y devolver errores HTTP con contratos claros.
- Aislar la lógica de negocio en servicios y el acceso a datos en repositorios.
- El backend actual es síncrono: mantener `Session` y handlers sync; no introducir `async def` ni `AsyncSession` de forma aislada.
- Si un change aprueba una ruta async integral, probar dependencias con una sesión de prueba y `httpx.AsyncClient` según el diseño.

### async-python-patterns

- Usar asyncio para E/S concurrente; para CPU-bound, descargar el trabajo a proceso o hilo (`asyncio.to_thread`).
- Mantener cada ruta de ejecución totalmente sync o totalmente async; no mezclar `Session` bloqueante y `AsyncSession` en la misma cadena.
- Esperar coroutines con `await`; gestionar explícitamente resultados y errores de `create_task()` y `gather()`.
- Aplicar límites de tiempo con `asyncio.wait_for()` y manejar `asyncio.TimeoutError`.
- No bloquear el event loop con `time.sleep` o I/O síncrona; usar alternativas async.
- Ante cancelación, limpiar recursos, capturar `asyncio.CancelledError` y relanzarla.
- Cubrir timeout y cancelación con `pytest.mark.asyncio` sólo si el change aprobó la migración async completa.

### python-testing-patterns

- Elegir capa de prueba: unitaria para comportamiento aislado, integración para componentes y funcional/E2E para un flujo completo.
- Escribir cada prueba con Arrange–Act–Assert y nombre `test_<unidad>_<escenario>_<resultado_esperado>`.
- Mantener tests independientes, datos ficticios, fixtures aisladas y limpieza propia; centralizar fixtures compartidas en `tests/conftest.py`.
- Cubrir caminos significativos, incluido éxito y error de negocio; no optimizar sólo por porcentaje de cobertura.
- Usar mocks únicamente para dependencias externas; los tests de repositorio y API usan PostgreSQL real mediante `TEST_DATABASE_URL`.
- Controlar el tiempo para lógica temporal y usar markers para suites lentas o de integración cuando sea necesario.
- En cambios async aprobados, usar `pytest.mark.asyncio` y probar timeout; no adoptar async sólo por la prueba.

### postgresql-table-design

- Modelar primero en 3NF y desnormalizar sólo con evidencia de beneficio de lectura.
- Definir `NOT NULL`, `DEFAULT`, `CHECK` y claves foráneas con una política explícita de `ON DELETE/UPDATE`.
- Usar tipos adecuados: `TIMESTAMPTZ` para eventos, `NUMERIC` para dinero, `TEXT` para cadenas y `BIGINT`/`DOUBLE PRECISION` según el dato.
- Mantener identificadores `snake_case` sin comillas; indexar las FKs y los filtros, joins u ordenamientos reales.
- Elegir el índice por patrón: B-tree común, GIN para JSONB/arrays/FTS y GiST para rangos o exclusiones.
- Conservar obligatoriamente `CHECK (fin > inicio)`, `btree_gist` y `EXCLUDE USING gist` para las reservas.
- Probar constraints e índices contra PostgreSQL real en Docker Compose; no confiar sólo en validaciones de aplicación.

### security-best-practices

- Activar esta skill sólo ante solicitud explícita de seguridad o escritura secure-by-default autorizada; no convertir cada change en una auditoría.
- Identificar lenguajes y frameworks dentro del alcance y leer las referencias de cada uno; para web, cubrir frontend y backend.
- Aplicar secure-by-default al código nuevo y señalar pasivamente sólo riesgos críticos o de alto impacto fuera del alcance.
- No versionar secretos ni datos reales de pacientes; usar variables de entorno y datos demo ficticios.
- Para informes, escribir Markdown con resumen ejecutivo, hallazgos numerados por severidad e impacto; citar archivo y línea.
- Presentar hallazgos y pedir autorización antes de iniciar fixes; corregir uno por vez y ejecutar los tests configurados.
- Para IDs expuestos públicamente, evitar secuencias pequeñas previsibles y evaluar UUID4/hex aleatorio según el diseño.

### revisar-escenarios-agenda

- Auditar el borrador sin editar especificaciones, tareas, código ni pruebas; separar reglas confirmadas de decisiones abiertas.
- Leer `CHANGES.md`, la KB y las specs aplicables; consultar `openspec status --change <cambio> --json` antes de atribuir artefactos.
- Revisar US-002, RN-DI-01 y el modelo de `Turno` cuando estén disponibles; declarar fuentes ausentes o contradictorias.
- Comprobar `inicio`, `fin` y el caso `inicio < fin`; tratar la respuesta a rango inválido como decisión pendiente si no está definida.
- Verificar intersección de intervalos `[inicio, fin)`: `turno.inicio < rango.fin` y `turno.fin > rango.inicio`; un turno sólo contiguo queda fuera.
- Cubrir turno contenido, que empieza antes, que termina después y que abarca todo el rango.
- Revisar filtros de profesional y box: ninguno, cada uno y ambos; señalar combinación no definida.
- Revisar ausencia de resultados y orden por inicio; no inventar desempate.
- Plantear preguntas verificables sobre entradas inválidas, zonas horarias y cambios de horario si faltan políticas.
- Vincular escenarios con pruebas previstas o existentes, distinguiendo las previstas de las ejecutadas.
- Entregar matriz «Regla y fuente / Escenario Dado-Cuando-Entonces / Prueba / Estado», con éxito, borde, entrada inválida o error, y hallazgos priorizados.

## MCP de documentación: Context7

Context7 es un **servidor MCP**, no una skill del proyecto. Durante el diseño de C-02 permite consultar documentación pública actual de FastAPI y SQLAlchemy: `resolve-library-id` identifica la biblioteca y `query-docs` responde una pregunta técnica sobre ella. Usarlo para contrastar decisiones de API y consultas antes de cerrar el diseño; validar toda regla odontológica contra `knowledge-base/`. Enviar sólo preguntas técnicas públicas, sin datos reales de pacientes, secretos ni código privado. Las herramientas de consulta son de lectura y no modifican el repositorio ni servicios externos. Configuración, comprobación y evidencia: [Context7 para C-02](../docs/skills-mcp/context7-configuracion.md).

## Skills OPSX presentes en el proyecto

| Skill | Ruta | Uso |
|---|---|---|
| `openspec-explore` | [`.agents/skills/openspec-explore/SKILL.md`](../.agents/skills/openspec-explore/SKILL.md) | Relevar el problema y el estado antes de proponer. |
| `openspec-propose` | [`.agents/skills/openspec-propose/SKILL.md`](../.agents/skills/openspec-propose/SKILL.md) | Crear o revisar proposal, design, specs y tasks. |
| `openspec-update-change` | [`.agents/skills/openspec-update-change/SKILL.md`](../.agents/skills/openspec-update-change/SKILL.md) | Ajustar artefactos de un change existente. |
| `openspec-apply-change` | [`.agents/skills/openspec-apply-change/SKILL.md`](../.agents/skills/openspec-apply-change/SKILL.md) | Implementar tasks contra la especificación y el diseño. |
| `openspec-sync-specs` | [`.agents/skills/openspec-sync-specs/SKILL.md`](../.agents/skills/openspec-sync-specs/SKILL.md) | Sincronizar specs vigentes tras completar un change. |
| `openspec-archive-change` | [`.agents/skills/openspec-archive-change/SKILL.md`](../.agents/skills/openspec-archive-change/SKILL.md) | Verificar y archivar un change terminado. |

## Convenciones del proyecto

| Archivo | Rol |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | Índice de reglas, stack, skills, KB y flujo de trabajo para agentes. |
| [`CLAUDE.md`](../CLAUDE.md) | Copia sincronizada de `AGENTS.md` para Claude Code. |
| [`CHANGES.md`](../CHANGES.md) | Roadmap y dependencias de los changes. |
| [`knowledge-base/`](../knowledge-base/) | Fuente de verdad del dominio; leer el archivo referido por el change. |
| [`openspec/`](../openspec/) | Specs vigentes y changes; OpenSpec es la fuente de estado del ciclo. |

## Resolución antes de aplicar un change

1. Consultar `CHANGES.md`, la knowledge base indicada y el estado del change con OpenSpec.
2. Elegir las skills por el tipo de tarea y leer sus `SKILL.md` antes de editar.
3. Mantener el backend íntegramente síncrono, salvo que el diseño de un change apruebe una migración async completa.
4. Cumplir `AGENTS.md` / `CLAUDE.md`: datos ficticios, secretos fuera del repositorio, disponibilidad en dominio, `CHECK`/`EXCLUDE` y turno más historial en la misma transacción.
5. Verificar con `pytest` contra PostgreSQL real mediante Docker Compose antes de archivar; no hay una skill local de TDD ni de Docker instalada.
