# Evidencia de uso real de Context7 para C-02

**Fecha:** 29/10/2026. **Servidor:** Context7 MCP, conexión global `stdio` habilitada. `codex mcp get context7 --json` informó `enabled: true`, `command: npx` y el paquete `@upstash/context7-mcp@2.2.5`. No había credenciales en la entrada.

| Herramienta y solicitud realizada | Resultado obtenido | Aporte a C-02 |
|---|---|---|
| `resolve-library-id`: `libraryName="FastAPI"`, consulta sobre parámetros de rango obligatorios y filtros UUID opcionales para `GET /api/v1/agenda`. | Identificador `/websites/fastapi_tiangolo`; biblioteca FastAPI con reputación alta. | Selección explícita de la documentación del framework usado por la API. |
| `query-docs` con ese identificador: «How does FastAPI declare required datetime query parameters and optional UUID query parameters with type hints? Does FastAPI validate and return 422 for invalid values?» | [FastAPI Query Parameters](https://fastapi.tiangolo.com/tutorial/query-params/): un parámetro sin valor predeterminado es obligatorio; `None` lo vuelve opcional; omitir uno obligatorio produce `422`. | El diseño puede distinguir rango obligatorio de filtros opcionales y prever pruebas de parámetros ausentes. |
| `resolve-library-id`: `libraryName="SQLAlchemy"`, consulta sobre `SELECT`, filtros, orden y rangos. | Identificador `/websites/sqlalchemy_en_20_orm`; documentación ORM 2.0, reputación alta. | Selección de la versión de ORM compatible con el backend. |
| `query-docs` con ese identificador: «How to compose select(Turno).where(...) with optional filters, interval intersection, order_by inicio, and execute via Session.scalars?» | [SQLAlchemy ORM Querying Guide](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html): `select(...).where(...)`, `order_by(...)` y `Session.scalars(...)`. | Orienta la consulta de turnos ordenada por inicio, sin trasladar reglas de dominio al router. |

**Revisión crítica:** la respuesta sobre parámetros de FastAPI acredita obligatoriedad y validación de tipo, pero no acredita que una fecha tenga zona horaria ni que `fin > inicio`. Esas condiciones requieren validación explícita apoyada en la KB y escenarios de C-02. La documentación consultada se toma como guía de API/ORM, no como fuente de decisiones de negocio. No se enviaron datos reales de pacientes ni secretos.

## Revisión de la propuesta: antes y después

**Antes:** la solicitud real a Context7 preguntó por filtros UUID opcionales. Esa formulación servía para consultar la sintaxis de FastAPI, pero no describía los identificadores que ya usa este proyecto.

**Detección:** el modelo de dominio declara `profesional_id` y `box_id` como `str` en [`backend/app/domain/turnos.py`](../../../backend/app/domain/turnos.py); las columnas correspondientes son `String(64)` en [`backend/app/infrastructure/modelos.py`](../../../backend/app/infrastructure/modelos.py). Las [semillas](../../../backend/app/infrastructure/semillas.py) incluyen valores como `profesional-demo-001`, que no son UUID. Por eso, aplicar literalmente la respuesta de Context7 cambiaría el contrato existente y rechazaría identificadores válidos.

**Después:** la propuesta para C-02 conserva los identificadores existentes: filtros opcionales `profesional_id: str | None = None` y `box_id: str | None = None`. Un identificador sin turnos coincidentes devuelve una lista vacía; la consulta no necesita comprobar la existencia del profesional o box. El rango de fechas sigue siendo obligatorio. La presencia de zona horaria y la condición `fin > inicio` necesitan validación explícita; FastAPI no las garantiza por declarar parámetros `datetime`. Context7 aportó la forma de expresar parámetros y consultas, mientras que el modelo y la KB determinaron los tipos y reglas finales.
