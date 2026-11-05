# Turnos de odontología

Sistema de turnos y agenda para consultorios odontológicos (mercado argentino), construido con Spec-Driven Development (OpenSpec) y Active Stack.

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2.0 · PostgreSQL 17 · JWT · Redis (C-16) · Docker Compose — React + TypeScript + Vite (C-15).

**Estado actual:** están implementados el alta de turnos sin solapamientos (C-01b), la consulta de agenda (C-02), el bloqueo de disponibilidad de un profesional o un box (C-03), la reprogramación atómica (C-04), la confirmación y cancelación de turnos (C-05), la autenticación con JWT y roles (C-08), el recordatorio simulado con Redis (C-16), el alta y búsqueda de pacientes con datos mínimos (C-17), la agenda web React (C-15) y el flujo MVP integrado en Compose (C-06). Los intervalos son semiabiertos `[inicio, fin)`: dos intervalos que sólo se tocan son compatibles. PostgreSQL impone la exclusión entre turnos; los casos de uso coordinan con bloqueos de fila la creación de turnos y bloqueos.

> Todas las rutas `/api/v1` exigen un token JWT (C-08). La API sigue siendo interna: rate limiting, CORS y exposición pública llegan con C-09. Todos los datos son ficticios.

## Completo y pendiente

**Completo (MVP, 10 changes implementados, verificados y archivados en [openspec/changes/archive/](openspec/changes/archive/)):**

| Change | Qué entrega | Verificación |
|---|---|---|
| C-01b `crear-turno-sin-solapamientos-fastapi` | Alta de turnos sin solapamientos por profesional ni box, con restricción `EXCLUDE` en PostgreSQL | pytest dominio/aplicación/persistencia/API |
| C-02 `consultar-agenda` | `GET /api/v1/agenda` por rango con filtros de profesional y box | pytest |
| C-03 `bloquear-disponibilidad` | Bloqueos de profesional o box; el alta de turnos los respeta | pytest, incluida carrera turno↔bloqueo |
| C-04 `reprogramar-turno-atomicamente` | `PATCH /api/v1/turnos/{id}` atómico con historial antes/después | pytest, incluidas carreras reprogramación↔alta |
| C-05 `cancelar-y-confirmar-turnos` | Confirmar y cancelar; cancelar libera el horario | pytest |
| C-08 `autenticar-con-jwt` | Login OAuth2, JWT HS256, Argon2id, roles y actor en el historial | pytest |
| C-16 `recordatorio-simulado-con-redis` | Encolado tras commit, worker con notificador simulado e idempotencia | pytest y worker en ejecución |
| C-17 `registrar-paciente-minimo` | Alta y búsqueda de pacientes con datos mínimos, sin datos clínicos | pytest |
| C-15 `agenda-web-react` | Agenda web: login, vista diaria/semanal, filtros, pacientes y alta de turnos | vitest y build `strict` |
| C-06 `flujo-mvp-docker-compose` | Compose con datos demo, worker y E2E HTTP aislado | `check_compose_mvp.py` y `ejecutar_e2e.py` |

Evidencia de la última verificación: [docs/evidencias/verificacion-tpi.md](docs/evidencias/verificacion-tpi.md).

**Pendiente (fuera del alcance presentado, planificado en [CHANGES.md](CHANGES.md)):**

- C-07 migraciones versionadas y respaldo: hoy el esquema se crea con `create_all`; un cambio de esquema exige recrear la base demo.
- C-09 API publicable: rate limiting, CORS, idempotencia de comandos y revocación de tokens.
- C-14 auditoría operativa y observabilidad.
- C-10 a C-13 integraciones reales (WhatsApp, cobros, calendario externo) e historia clínica.
- Limitaciones conocidas del MVP: la web no tiene catálogo de profesionales, boxes ni prestaciones (se usan los IDs demo); la web no expone confirmar, cancelar, reprogramar ni bloquear (se hacen por API/Swagger); la consulta de agenda no pagina ni limita el rango; la ventana de cancelación y la política de sobreturnos siguen abiertas en [knowledge-base/10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md).

## Estructura

```text
backend/            API FastAPI, dominio, casos de uso, persistencia y tests (pytest)
frontend/           React + TypeScript strict + Vite; tests y build Nginx
docker-compose.yml  PostgreSQL + Redis + bootstrap Demo + API + frontend + worker
docker-compose.e2e.yml  Override sin puertos para el E2E aislado
knowledge-base/     Base de conocimiento del proyecto
.agents/skills/     Skills locales versionadas y skills OPSX del proyecto
openspec/           Specs vigentes y changes archivados
docs/               Discovery, exploraciones OPSX y evidencias
CHANGES.md          Roadmap de changes
```

## Correr los tests

Los tests de dominio y de casos de uso no necesitan base de datos. Los de persistencia y API corren contra un PostgreSQL real indicado en `TEST_DATABASE_URL`; **su esquema se borra y se recrea**, así que tiene que ser una base descartable.

### Opción A — Docker Compose

Requisitos: Docker con Docker Compose v2.

```bash
python backend/scripts/preparar_entorno.py
docker compose up -d --build
```

```bash
docker compose run --rm --no-deps api pytest
```

El servicio `db` crea la base `turnos` y la base descartable `turnos_test` (credenciales de desarrollo `turnos` / `turnos`, sólo válidas en este compose). La suite usa exclusivamente `turnos_test` y borra su esquema. `preparar_entorno.py` genera secretos aleatorios en `.env` local ignorado por Git y conserva los mismos valores al repetirse.

### Opción B — Python y PostgreSQL locales

Requisitos: Python 3.12 y PostgreSQL 15 o posterior con la extensión `btree_gist` (viene con el paquete estándar/contrib).

1. Crear una base vacía para los tests, por ejemplo `turnos_test`.
2. Instalar dependencias:

```bash
cd backend
python -m venv .venv
.venv/Scripts/pip install -r requirements-dev.txt   # Windows (Git Bash)
# .venv/bin/pip install -r requirements-dev.txt     # Linux / macOS
```

3. Ejecutar la suite, indicando la base descartable:

```bash
TEST_DATABASE_URL="postgresql+psycopg://USUARIO:CLAVE@localhost:5432/turnos_test" .venv/Scripts/python -m pytest -v
```

En PowerShell: `$env:TEST_DATABASE_URL = "postgresql+psycopg://..."; .venv\Scripts\python -m pytest -v`.

Resultado esperado: la suite completa en verde. Para C-03 se verificó además la carrera concurrente entre turno y bloqueo contra PostgreSQL real.

### Frontend C-15

Requisitos para desarrollo sin contenedores: Node.js 22 o posterior y la API levantada en `localhost:8000`. El servidor Vite redirige `/api` a la API; no requiere CORS. La imagen de Compose sirve los archivos compilados con Nginx y redirige `/api/` por el mismo origen.

```bash
cd frontend
npm ci
npm test -- --run
npm run build
npm run dev
```

En desarrollo, abrir `http://localhost:5173`; con Compose, ejecutar primero `python backend/scripts/preparar_entorno.py`, luego `docker compose up -d --build` y abrir la misma URL. El bootstrap crea `recepcion.demo` automáticamente con la contraseña aleatoria `DEMO_PASSWORD` guardada sólo en el `.env` local; **no hay contraseña predeterminada**. El token JWT sólo permanece en memoria: al recargar o cerrar la página hay que ingresar de nuevo.

La agenda permite ver un día o una semana, filtrar por profesional y box, buscar o registrar pacientes mínimos y crear turnos. El rol `odontologo` sólo ve su profesional vinculado y no presenta controles de pacientes ni de alta. Los errores `409` y `422` muestran el mensaje de la API y conservan el formulario. La zona horaria visible es la del dispositivo; los límites de consulta y horarios enviados llevan zona explícita. Actualmente no hay catálogo de profesionales, boxes o prestaciones: usar los IDs demo `profesional-demo-001`, `box-demo-001` y `prestacion-demo-001` tras cargar las semillas. La API verifica toda disponibilidad y autorización.

## Levantar el MVP completo

Requisitos: Python 3.12 y Docker con Compose v2. Desde la raíz del repositorio:

```bash
python backend/scripts/preparar_entorno.py
docker compose up -d --build
```

Abrir `http://localhost:5173`. El usuario es `recepcion.demo`; abrir el `.env` local en un editor para consultar `DEMO_PASSWORD`. No compartir ni versionar ese archivo. La API responde en `http://localhost:8000/health` y la documentación en `http://localhost:8000/docs`. El frontend usa `/api` por el mismo origen mediante Nginx. El worker consume Redis y sólo registra recordatorios **simulados**: no envía mensajes externos.

El bootstrap carga automáticamente los pacientes `paciente-demo-001/002`, profesionales `profesional-demo-001/002`, boxes `box-demo-001/002`, prestación `prestacion-demo-001` y el usuario `recepcion.demo`. Todos son ficticios. El primer arranque crea esquema y semillas; los arranques siguientes conservan los datos, el identificador y el hash del usuario sin duplicarlos. No se cargan datos clínicos.

Para comprobar el arranque y la configuración:

```bash
python backend/scripts/check_compose_mvp.py
docker compose config --quiet
docker compose ps
```

Si `api` queda en `Created` o termina con `Temporary failure in name resolution`, revisar que ningún otro proceso (por ejemplo, un `uvicorn` local) ocupe el puerto 8000 y ejecutar `docker compose down` seguido de `docker compose up -d`.

Para detener sin borrar datos: `docker compose down`. Sólo si querés reiniciar intencionalmente **esta instalación de demostración** desde cero, ejecutá `docker compose down -v`: elimina su volumen de PostgreSQL. Si cambiás `DEMO_PASSWORD` en un `.env` que ya tiene usuario creado, el bootstrap falla para evitar modificar su hash silenciosamente; restaurá el valor anterior o reiniciá de manera deliberada el volumen demo. Una base vieja sin las columnas actuales también requiere recreación local hasta C-07, que incorporará migraciones.

Para obtener un token (OAuth2 password flow), usar la contraseña del `.env` local sin registrarla en logs ni en el repositorio:

```bash
curl -X POST http://localhost:8000/api/v1/auth/token -d "username=recepcion.demo" -d "password=CONTRASEÑA_LOCAL"
# → {"access_token":"…","token_type":"bearer","expires_in":1800}
export TOKEN="…"
```

Para comprobar **todo el recorrido integrado** dos veces en entornos descartables independientes, sin tocar el volumen habitual ni publicar puertos de prueba:

```bash
python backend/scripts/ejecutar_e2e.py
python backend/scripts/ejecutar_e2e.py
```

La prueba usa API HTTP real y el proxy web: login, paciente, turno, agenda, bloqueo y rechazo `409`, reprogramación, recordatorio simulado, cancelación y reutilización del horario. Calcula fechas futuras en cada ejecución, espera el worker con plazo acotado y desmonta sus contenedores y volumen aunque falle. Si falla, revisar el mensaje de la prueba y `docker compose ps` del entorno habitual; el lanzador nunca imprime el `.env`. `python backend/scripts/check_compose_mvp.py` comprueba también dependencias y variables obligatorias sin revelar sus valores.

Todos los ejemplos de abajo llevan `-H "Authorization: Bearer $TOKEN"`. En http://localhost:8000/docs el botón **Authorize** hace el login.

| Rol | Puede |
|---|---|
| `recepcion`, `responsable` | Registrar y buscar pacientes; crear, reprogramar, confirmar y cancelar turnos; crear bloqueos; consultar cualquier agenda y consultar recordatorios simulados |
| `odontologo` | Sólo consultar su propia agenda (`profesional_id` = el profesional vinculado a su usuario) |

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `401` | Sin token, token mal firmado o con algoritmo no permitido, usuario borrado o desactivado | `no_autenticado` / `token_invalido` |
| `401` | Token vencido (pedir otro) | `token_expirado` |
| `401` | Login con usuario o contraseña incorrectos (o usuario inactivo) | `credenciales_invalidas` |
| `403` | El rol no permite la operación | `acceso_denegado` |

`GET /api/v1/auth/yo` devuelve id, usuario, rol y profesional vinculado del token. `/health` y la documentación OpenAPI siguen públicas para desarrollo local. Cada evento del historial de turnos registra el usuario que hizo el cambio.

- Documentación interactiva: http://localhost:8000/docs
- Salud: `GET http://localhost:8000/health`
- Alta y búsqueda de pacientes con datos mínimos (`C-17`, `POST /api/v1/pacientes` y `GET /api/v1/pacientes`, roles `recepcion` y `responsable`):

  Registra únicamente datos mínimos operativos (`id` opcional, `nombre_mostrado` obligatorio y `contacto` opcional) y rechaza con `422` cualquier campo clínico o personal no permitido (`historia_clinica`, `odontograma`, `dni`, `obra_social`, etc., conforme a `DD-04`). Todos los datos en semillas y pruebas son manifiestamente ficticios (`"Paciente Demo ..."`).

```bash
curl -X POST http://localhost:8000/api/v1/pacientes -H "Authorization: Bearer $TOKEN" -H "content-type: application/json" -d '{"nombre_mostrado":"Paciente Demo Ficticio 010","contacto":"+54 9 11 0000-0010"}'
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/pacientes?q=Demo"
```

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `201` / `200` | Paciente dado de alta (`POST`) o listado ordenado por `nombre_mostrado` e `id` (`GET`) | — |
| `401` | Sin token o token inválido/expirado | `no_autenticado` / `token_invalido` / `token_expirado` |
| `403` | Rol sin permiso (`odontologo`) | `acceso_denegado` |
| `409` | `id` o `contacto` ya registrado | `paciente_duplicado` |
| `422` | `nombre_mostrado` o `id` vacío/en blanco, o presencia de campos clínicos/no permitidos | `datos_paciente_invalidos` / `detail` de FastAPI |

- Alta de turno:

```bash
curl -X POST http://localhost:8000/api/v1/turnos -H "Authorization: Bearer $TOKEN" -H "content-type: application/json" -d '{"paciente_id":"paciente-demo-001","profesional_id":"profesional-demo-001","box_id":"box-demo-001","prestacion_id":"prestacion-demo-001","inicio":"2030-01-10T09:00:00-03:00"}'
```

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `201` | Turno creado | — |
| `404` | Paciente, profesional, box o prestación inexistente | `recurso_inexistente` |
| `409` | Un turno o bloqueo ocupa el profesional o el box | `conflicto_profesional` / `conflicto_box` / `conflicto_bloqueo_profesional` / `conflicto_bloqueo_box` |
| `422` | Fin no posterior al inicio, prestación con duración no positiva, fecha sin zona horaria o datos mal formados | `intervalo_invalido` / `duracion_invalida` |

- Consulta de agenda (`GET /api/v1/agenda`):

  Parámetros de consulta (`query`):
  - `inicio` (obligatorio): fecha y hora con zona horaria explícita (ej. `2030-01-10T08:00:00-03:00`).
  - `fin` (obligatorio): fecha y hora con zona horaria explícita, estrictamente posterior a `inicio` (ej. `2030-01-10T12:00:00-03:00`).
  - `profesional_id` (opcional): identificador de texto del profesional (`1..64` caracteres, ej. `profesional-demo-001`).
  - `box_id` (opcional): identificador de texto del box (`1..64` caracteres, ej. `box-demo-001`).

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/agenda?inicio=2030-01-10T08:00:00-03:00&fin=2030-01-10T12:00:00-03:00&profesional_id=profesional-demo-001&box_id=box-demo-001"
```

  Respuesta `200` con coincidencias (ordenada por `inicio` ascendente, normalizada en UTC):

```json
[
  {
    "id": "turno-demo-001",
    "profesional_id": "profesional-demo-001",
    "box_id": "box-demo-001",
    "inicio": "2030-01-10T12:00:00Z",
    "fin": "2030-01-10T12:30:00Z"
  }
]
```

  Respuesta `200` sin coincidencias (rango vacío o filtro de ID de texto sin turnos):

```json
[]
```

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `200` | Lista de turnos que intersectan `[inicio, fin)` (o `[]` si no hay coincidencias) | — |
| `422` | Falta `inicio` o `fin`, fecha mal formada, fecha sin zona horaria o `fin <= inicio` | `intervalo_invalido` (cuando `fin <= inicio`) |

- Bloquear disponibilidad (`POST /api/v1/bloqueos`): indicar **exactamente uno** entre `profesional_id` y `box_id`. El motivo es opcional; las fechas deben incluir zona horaria y `fin > inicio`.

```bash
curl -X POST http://localhost:8000/api/v1/bloqueos -H "Authorization: Bearer $TOKEN" -H "content-type: application/json" -d '{"profesional_id":"profesional-demo-001","inicio":"2030-01-10T09:00:00-03:00","fin":"2030-01-10T10:00:00-03:00","motivo":"Reunión Demo"}'
```

El resultado `201` incluye el ID del bloqueo, el recurso, el intervalo en UTC y el motivo. Se acepta un segundo bloqueo que se superponga al primero: la KB no define un conflicto entre bloqueos. Un bloqueo que cruce un turno activo del mismo recurso se rechaza sin cambiar el turno ni su historial.

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `201` | Bloqueo registrado | — |
| `404` | Profesional o box inexistente | `recurso_inexistente` |
| `409` | Un turno activo cruza el bloqueo | `conflicto_turno_existente` |
| `422` | Recurso omitido o doble, fecha inválida/sin zona, o `fin <= inicio` | `detail` de validación de FastAPI |

La garantía cruzada turno-bloqueo cubre las operaciones de esta API; escrituras SQL directas que eludan los casos de uso no participan de su protocolo de bloqueo. La política clínica para un bloqueo que afecta un turno anterior queda abierta: C-03 lo rechaza conservadoramente y no cancela turnos. Los bloqueos exigen el rol `recepcion` o `responsable`.

- Confirmar o cancelar un turno (`POST /api/v1/turnos/{turno_id}/confirmar` y `POST /api/v1/turnos/{turno_id}/cancelar`, sin cuerpo):

```bash
curl -X POST http://localhost:8000/api/v1/turnos/ID-DEL-TURNO/confirmar -H "Authorization: Bearer $TOKEN"
curl -X POST http://localhost:8000/api/v1/turnos/ID-DEL-TURNO/cancelar -H "Authorization: Bearer $TOKEN"
```

Transiciones permitidas: `programado → confirmado`, `programado → cancelado` y `confirmado → cancelado`. Cada una registra su evento (`confirmado` / `cancelado`) en el historial dentro de la misma transacción. Un turno cancelado libera su intervalo: se puede volver a reservar o bloquear. Un turno confirmado sigue ocupándolo. La agenda informa el `estado` de cada turno y sigue mostrando los cancelados.

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `200` | Turno actualizado (incluye `estado`) | — |
| `404` | El turno no existe | `recurso_inexistente` |
| `409` | Confirmar un confirmado o cancelado, o cancelar un cancelado | `transicion_invalida` |
| `422` | Identificador de más de 64 caracteres | `detail` de validación de FastAPI |

La ventana de cancelación y la confirmación de turnos vencidos siguen como preguntas abiertas (ver `knowledge-base/10_preguntas_abiertas.md`).

- Reprogramar un turno (`PATCH /api/v1/turnos/{turno_id}`): indicar al menos uno entre `inicio`, `fin`, `profesional_id` y `box_id`. Lo omitido se conserva; un `inicio` sin `fin` conserva la duración del turno.

```bash
curl -X PATCH http://localhost:8000/api/v1/turnos/ID-DEL-TURNO -H "Authorization: Bearer $TOKEN" -H "content-type: application/json" -d '{"inicio":"2030-01-10T11:00:00-03:00","box_id":"box-demo-002"}'
```

El nuevo intervalo se valida contra los demás turnos activos y los bloqueos del profesional y box de destino; el propio turno no cuenta como conflicto. Si algo falla, el turno queda exactamente como estaba. Si es válido, el intervalo anterior se libera y el historial registra `reprogramado` con el resumen anterior y posterior. El estado (`programado` / `confirmado`) se conserva.

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `200` | Turno reprogramado | — |
| `404` | Turno, profesional o box inexistente | `recurso_inexistente` |
| `409` | Conflicto en el destino o turno cancelado | `conflicto_profesional` / `conflicto_box` / `conflicto_bloqueo_profesional` / `conflicto_bloqueo_box` / `transicion_invalida` |
| `422` | `fin <= inicio`, ningún valor cambia, cuerpo vacío, campo desconocido o fecha sin zona | `intervalo_invalido` / `reprogramacion_sin_cambios` / `detail` de FastAPI |

- Recordatorios simulados con Redis (`C-16`, `GET /api/v1/turnos/{turno_id}/recordatorios`):

  Al crear o confirmar un turno, se encola en Redis (`REDIS_URL`) una tarea de recordatorio (`creado` / `confirmado`) exclusivamente tras confirmar la transacción en PostgreSQL. Si Redis no está disponible, el alta, la confirmación y la consulta de agenda siguen operando con normalidad (`RN-EX-02`).

  El servicio `worker` de Compose procesa continuamente las tareas con `NotificadorSimulado` (idempotente por `(turno_id, motivo)` y que omite turnos cancelados). Para comprobar su estado:

```bash
docker compose ps worker
```

  Consultar los recordatorios simulados registrados de un turno (`recepcion` o `responsable`):

```bash
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/turnos/ID-DEL-TURNO/recordatorios"
```

| Respuesta | Cuándo | `codigo` |
|---|---|---|
| `200` | Lista de recordatorios simulados enviados del turno (ordenada por `enviado_en` ascendente) | — |
| `401` | Sin token o token inválido/expirado | `no_autenticado` / `token_invalido` / `token_expirado` |
| `403` | Rol sin permiso (`odontologo`) | `acceso_denegado` |
| `404` | El turno no existe | `recurso_inexistente` |

Sin Docker: definir `DATABASE_URL`, `REDIS_URL` (opcional; si se omite usa cola nula) y `JWT_SECRET` (ver `backend/.env.example`), ejecutar `python -m app.infrastructure.semillas`, crear un usuario con `python -m app.infrastructure.crear_usuario …` y `uvicorn app.api.main:app --reload` desde `backend/`.

## Proceso (SDD / OPSX)

- Discovery: [docs/discovery/informe-discovery.md](docs/discovery/informe-discovery.md) (y su PDF).
- Specs vigentes: [openspec/specs/](openspec/specs/) (creación, agenda, bloqueos, ciclo de vida, reprogramación, autenticación, recordatorios, pacientes, agenda web y entorno MVP local).
- Changes archivados: [openspec/changes/archive/](openspec/changes/archive/).
- Evidencias de entrega: [docs/evidencias/](docs/evidencias/).

## Skill propia y Context7 para C-02

La [ficha de investigación](docs/skills-mcp/investigacion.md) explica la elección de una skill de revisión de escenarios y del MCP Context7 para preparar la consulta de agenda. La [guía de Context7](docs/skills-mcp/context7-configuracion.md) detalla requisitos, configuración reproducible sin secretos, comprobación y límites; el [registro de uso](docs/skills-mcp/evidencias/context7-uso.md) muestra herramientas reales y su aporte. Context7 se configura en el `~/.codex/config.toml` personal, no dentro del repositorio.

La [skill de revisión de agenda](.agents/skills/revisar-escenarios-agenda/SKILL.md) está versionada en el proyecto y [su evidencia de uso](docs/skills-mcp/evidencias/skill-uso.md) muestra el hallazgo de escenarios faltantes. El [informe de aplicación](docs/skills-mcp/aplicacion.md) resume cambios, revisión crítica y límites. [ENTREGA.md](ENTREGA.md) resume el alcance presentado en el TPI.
