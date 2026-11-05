# Guion del video del TPI (máximo 10 minutos)

La consigna pide ver **trabajo real ejecutándose**: el sistema levantado, los tests y el uso de la skill y del MCP. Las diapositivas son opcionales. Todos los integrantes se presentan y hablan; cámara encendida al menos en la presentación personal. Usen sólo datos ficticios y no muestren el `.env`, tokens ni contraseñas.

## Preparación (antes de grabar, no entra en los 10 minutos)

1. Clon actualizado de `main` y Docker Desktop encendido.
2. `python backend/scripts/preparar_entorno.py` y `docker compose up -d --build`.
3. `docker compose ps`: `db`, `redis`, `api`, `frontend` y `worker` en ejecución; `bootstrap` terminado con código 0.
4. Abrir en pestañas: `http://localhost:5173` (agenda web), `http://localhost:8000/docs` (Swagger), el repo en GitHub y una terminal en la raíz.
5. Tener a mano la contraseña de `recepcion.demo` (está en el `.env` local; copiarla fuera de cámara).
6. Correr una vez `docker compose run --rm --no-deps api pytest -q` y `python backend/scripts/ejecutar_e2e.py` para tener los resultados en pantalla o grabar sólo el final.
7. Elegir fechas futuras para la demo (por ejemplo, la semana próxima) y verificar que la agenda esté vacía en ese rango.
8. Opcional, para mostrar el rechazo por rol: crear un usuario odontólogo con `docker compose run --rm api python -m app.infrastructure.crear_usuario --nombre odonto.demo --rol odontologo --profesional-id profesional-demo-001` (pide la contraseña por consola, mínimo 12 caracteres).
9. Ensayar una vez completo con cronómetro: cada bloque tiene un tiempo máximo.

## Distribución

| Tiempo | Quién | Qué mostrar y decir |
|---|---|---|
| 0:00–0:30 | Los tres | Presentación personal con cámara. Alcance: 10 changes del MVP completos; mínimo exigido 6. Lo pendiente (C-07, C-09 a C-14) queda fuera. |
| 0:30–1:20 | Integrante 1 | `CHANGES.md` (árbol y estados `[x]`) y `openspec/changes/archive/` con las 11 carpetas. Explicar que C-01 se reemplazó por C-01b y no se cuenta. Abrir el `tasks.md` de un change para mostrar las tareas cerradas. |
| 1:20–2:10 | Integrante 2 | Recorrido rápido: C-01b (sin solapamientos, `EXCLUDE` en PostgreSQL), C-02 (agenda), C-03 (bloqueos), C-04 (reprogramación atómica), C-05 (confirmar/cancelar). Por cada uno: problema que resuelve y cómo se verificó (tests por escenario). |
| 2:10–3:00 | Integrante 3 | C-08 (JWT y roles), C-16 (recordatorio simulado con Redis y worker), C-17 (pacientes mínimos), C-15 (agenda web) y C-06 (Compose + E2E). Mostrar una spec de `openspec/specs/` con un escenario DADO/CUANDO/ENTONCES. |
| 3:00–4:30 | Integrante 1 | **Skill propia.** Abrir `.agents/skills/revisar-escenarios-agenda/SKILL.md`, su entrada en `.atl/skill-registry.md` y la referencia en `AGENTS.md`. Explicar que se creó con `skill-creator`. Mostrar en `docs/skills-mcp/evidencias/skill-uso.md` la matriz que detectó faltantes en C-02 y la tabla de cierre que vincula cada fila con su test. Si hay tiempo, invocarla en una sesión nueva del agente. |
| 4:30–6:00 | Integrante 2 | **MCP Context7.** `codex mcp list` (o el equivalente del agente) mostrando `context7` habilitado. En el agente, ejecutar `resolve-library-id` para FastAPI y `query-docs` sobre parámetros de query obligatorios y opcionales. Contar la revisión crítica: Context7 sugirió UUID, pero el modelo usa IDs de texto; mostrar el antes/después en `docs/skills-mcp/evidencias/context7-uso.md` y que `GET /api/v1/agenda` acepta `profesional-demo-001`. |
| 6:00–7:00 | Integrante 3 | **Pruebas.** Resultado de `pytest` (422 passed), `npm test` (24 passed) y `ejecutar_e2e.py`. Explicar qué recorre el E2E: login, paciente, turno, agenda, bloqueo y rechazo 409, reprogramación, recordatorio, cancelación y reutilización del horario. |
| 7:00–8:30 | Integrante 1 | **Demo web.** Login con `recepcion.demo`; vista semanal; registrar "Paciente Demo Video"; crear un turno; intentar otro turno solapado y mostrar el mensaje del 409; crear uno contiguo y mostrar que se acepta. |
| 8:30–9:40 | Integrante 2 | **Demo en Swagger.** Authorize; confirmar el turno (200), confirmarlo otra vez (409 `transicion_invalida`); reprogramarlo (`PATCH`); consultar `/recordatorios` (registro simulado del worker); cancelarlo y mostrar que el horario se libera. Opcional: un token de `odontologo` recibe 403 al crear turnos. |
| 9:40–10:00 | Integrante 3 | Cierre: qué está completo, qué queda pendiente (sección "Completo y pendiente" del README) y qué aportaron la skill y el MCP. |

## Si algo falla durante la grabación

- La web no carga: `docker compose ps` y `docker compose logs frontend api`.
- El login falla: revisar que la contraseña sea la del `.env` actual. Si se cambió el `.env` después del primer arranque, reiniciar la demo con `docker compose down -v` y volver a levantar (borra **sólo** la base de esta demo).
- No aparece el recordatorio: esperar unos segundos (el worker consulta cada 2 s) y revisar `docker compose logs worker`.
