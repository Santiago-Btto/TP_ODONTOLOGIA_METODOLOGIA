# Proposal

## Why

La sección D del Discovery exige un recordatorio manual o simulado en el MVP sin depender de cuentas externas de WhatsApp, y la arquitectura definida en `knowledge-base/02_descripcion_general.md` prevé que la API FastAPI encole tareas asincrónicas en Redis para que un worker las procese de forma desacoplada y subordinada al dominio (RN-EX-02). C-16 introduce esa tubería asincrónica con un `NotificadorSimulado` que registra los envíos sin bloquear ni comprometer la agenda si Redis no está disponible, dejando listo el camino hacia C-06 (flujo E2E en Docker Compose) y C-10 (adaptador real de WhatsApp Business).

## What Changes

- Al confirmar en base (`commit`) la creación (`CrearTurno`) o la confirmación (`ConfirmarTurno`) de un turno, el caso de uso intenta publicar en Redis una tarea de recordatorio para ese turno (`creado` o `confirmado`).
- Si la transacción falla o se revierte, no se publica ninguna tarea en Redis; si Redis está caído o inaccesible tras el `commit`, la falla de encolado se absorbe de forma segura para que el alta, la confirmación y el resto de la agenda sigan funcionando con normalidad.
- Incorporar un worker/procesador síncrono de recordatorios que consume tareas de la cola Redis, consulta el estado actual del turno en PostgreSQL y delega el envío en un `NotificadorSimulado` persistido en la tabla `recordatorios_enviados` (con clave única `(turno_id, motivo)` para garantizar idempotencia).
- Un turno inexistente o en estado `cancelado` al momento de procesar la tarea no genera recordatorio; un mismo turno y motivo procesados más de una vez registran un único envío simulado.
- Exponer `GET /api/v1/turnos/{turno_id}/recordatorios` (protegido por JWT, accesible para `recepcion` y `responsable`) para consultar los recordatorios simulados registrados de un turno (necesario para la verificación E2E por API de C-06) y proveer el comando `python -m app.infrastructure.worker_recordatorios` junto al servicio `redis` (`redis:7-alpine`) y `REDIS_URL` en `docker-compose.yml` y `.env.example`.

## Capabilities

### New Capabilities

- `recordatorio-de-turnos`: encolado pos-commit en Redis tras crear o confirmar un turno, resiliencia de la agenda con Redis caído, procesamiento idempotente con `NotificadorSimulado`, omisión de turnos cancelados y consulta de recordatorios simulados registrados.

### Modified Capabilities

Ninguna. Los contratos de `creacion-de-turnos`, `ciclo-de-vida-del-turno`, `reprogramacion-de-turnos`, `bloqueo-de-disponibilidad`, `consulta-de-agenda` y `autenticacion-y-autorizacion` conservan sus requisitos actuales.

## Impact

- Dominio: entidad de lectura/registro `RecordatorioSimulado` (`id`, `turno_id`, `motivo`, `enviado_en`), `MotivoRecordatorio` (`creado`, `confirmado`) y permiso `CONSULTAR_RECORDATORIOS` (habilitado para `recepcion` y `responsable` en `app/domain/autorizacion.py`).
- Aplicación: puertos `ColaRecordatorios` y `NotificadorRecordatorios` / `RepositorioRecordatorios`; caso de uso `ProcesarSiguienteRecordatorio` y `ConsultarRecordatoriosDeTurno`; integración pos-commit tolerante a fallos en `CrearTurno` y `ConfirmarTurno`.
- Persistencia e infraestructura: tabla `recordatorios_enviados` con restricción única `(turno_id, motivo)` y FK a `turnos.id`; adaptador `ColaRecordatoriosRedis` (`redis` sync client) con degradación silenciosa/segura ante errores de conexión; `NotificadorSimuladoSQLAlchemy`; comando `app.infrastructure.worker_recordatorios`.
- API y configuración: `GET /api/v1/turnos/{turno_id}/recordatorios` en `app/api/turnos.py`; `REDIS_URL` en `.env.example` y servicio `redis` en `docker-compose.yml`; dependencia `redis` fijada en `backend/requirements.txt`.
- Pruebas: unidad (aplicación con dobles en memoria), integración (cola Redis, idempotencia en PostgreSQL, omisión de turno cancelado y resiliencia con Redis caído) y API (`GET /api/v1/turnos/{turno_id}/recordatorios` y flujo alta/confirmación → worker → recordatorio registrado).
- Fuera de alcance: envío real por WhatsApp Business, plantillas de mensajes, consentimiento/opt-out y reintentos con backoff exponencial (pertenecen a C-10).
