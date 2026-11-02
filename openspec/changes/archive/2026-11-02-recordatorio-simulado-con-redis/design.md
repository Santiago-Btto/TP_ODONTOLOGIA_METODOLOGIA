# Diseño: Recordatorio simulado de turnos con Redis (`C-16`)

## Context

Los cambios `C-01b` a `C-05` y `C-08` establecieron el núcleo transaccional de turnos en PostgreSQL (`CrearTurno`, `ConfirmarTurno`, `CancelarTurno`) y la autenticación/autorización con JWT. La sección D del Discovery y el cambio `C-16` en `CHANGES.md` requieren incorporar un mecanismo asíncrono respaldado por Redis para recordar turnos al crearse o confirmarse, procesado por un worker mediante un `NotificadorSimulado` que registra el envío sin integrar WhatsApp real (diferido a `C-10`).

Además, la regla de negocio `RN-EX-02` exige que una caída o indisponibilidad de Redis nunca impida consultar la agenda ni registrar o actualizar turnos en PostgreSQL. El diseño debe mantener la arquitectura hexagonal síncrona vigente (`domain` sin dependencias de infraestructura, `application` orquestando puertos y `infrastructure` implementando adaptadores SQLAlchemy y Redis).

## Goals / Non-Goals

**Goals:**
- Definir las entidades/valores de dominio para motivos de recordatorio (`MotivoRecordatorio`: `creado`, `confirmado`), tareas de recordatorio (`TareaRecordatorio`) y registros de recordatorio enviado (`RecordatorioEnviado`).
- Encolar en Redis una `TareaRecordatorio` en `CrearTurno` (`motivo="creado"`) y `ConfirmarTurno` (`motivo="confirmado"`) **exclusivamente después** de `uow.commit()`.
- Garantizar degradación segura (`RN-EX-02`): cualquier fallo al conectar o escribir en Redis durante el encolado se captura y registra en logs sin propagar excepción al caso de uso ni a la API.
- Implementar el caso de uso `ProcesarSiguienteRecordatorio` y el worker síncrono que desapila tareas de Redis, verifica en PostgreSQL que el turno exista y no esté `cancelado`, e invoca `NotificadorSimulado`.
- Garantizar idempotencia ante reintentos o tareas duplicadas para el mismo `(turno_id, motivo)` mediante control en aplicación y restricción `UNIQUE (turno_id, motivo)` en la tabla `recordatorios_enviados`.
- Exponer `GET /api/v1/turnos/{turno_id}/recordatorios` protegido por JWT (`Permiso.CONSULTAR_RECORDATORIOS` para `recepcion` y `responsable`) para consultar los recordatorios simulados registrados y habilitar las pruebas integrales de `C-16` y `C-06`.
- Agregar el servicio `redis` (`redis:7-alpine`) y la variable `REDIS_URL` en `docker-compose.yml` y `backend/.env.example`.

**Non-Goals:**
- Integración real con WhatsApp Business API o proveedores externos de mensajería (`C-10`).
- Reemplazar el stack síncrono de FastAPI/SQLAlchemy por `asyncio`.
- Planificación temporal diferida (cron/scheduler de "24 h antes"); el alcance de `C-16` en `CHANGES.md` especifica encolar la tarea al crear/confirmar el turno y procesarla con el worker y `NotificadorSimulado`.

## Decisions

### 1. Encolado pos-commit y resiliencia ante caída de Redis (`RN-EX-02`)

- **Decisión:** `CrearTurno` y `ConfirmarTurno` aceptarán un puerto opcional `cola_recordatorios: ColaRecordatorios = ColaRecordatoriosNoOp()`. Dentro de `ejecutar(...)`, el bloque `with self._unidad_de_trabajo() as uow:` ejecutará la lógica de negocio y llamará a `uow.commit()`. Recién fuera o después de `uow.commit()`, un método auxiliar `_intentar_encolar_recordatorio(TareaRecordatorio(turno_id=turno.id, motivo=...))` invocará `self._cola_recordatorios.encolar(tarea)` dentro de un bloque `try/except Exception` que registra una advertencia (`logger.warning`) sin relanzar el error.
- **Alternativas consideradas:**
  - *Encolar antes de `uow.commit()`*: descartado porque un fallo en el commit dejaría una tarea huérfana en Redis o un fallo de Redis abortaría la transacción del turno.
  - *Outbox transaccional completo en PostgreSQL*: descartado por sobreingeniería para el alcance de `C-16`, que pide explícitamente encolar en Redis tras commit y tolerar Redis caído.

### 2. Estructura de cola en Redis y cliente síncrono

- **Decisión:** Se añade `redis==5.2.0` en `backend/requirements.txt` usando el cliente síncrono `redis.Redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=1.0, socket_timeout=1.0)`.
- `ColaRecordatoriosRedis` serializa cada `TareaRecordatorio` como JSON (`{"turno_id": int, "motivo": "creado" | "confirmado"}`) sobre una lista Redis (`RPUSH` para `encolar` y `LPOP` para `desencolar` sobre la clave configurable `turnos:recordatorios:cola`, por defecto).
- Se provee `ColaRecordatoriosMemoria` / `ColaRecordatoriosRedis` para pruebas unitarias e integración y un comando ejecutable `python -m app.infrastructure.worker_recordatorios` (con modo `--una-vez` o bucle continuo) para procesar tareas de la cola.

### 3. `NotificadorSimulado` e idempotencia en PostgreSQL

- **Decisión:** El `NotificadorSimulado` registra cada envío simulado en la tabla `recordatorios_enviados` de PostgreSQL a través de la unidad de trabajo:
  - Columnas: `id` (`SERIAL PRIMARY KEY`), `turno_id` (`INTEGER NOT NULL REFERENCES turnos(id)`), `motivo` (`VARCHAR(20) NOT NULL`, `CHECK (motivo IN ('creado', 'confirmado'))`), `destinatario` (`VARCHAR(120) NOT NULL`, nombre ficticio o teléfono ficticio del paciente para trazabilidad de la simulación) y `enviado_en` (`TIMESTAMPTZ NOT NULL`).
  - Restricción: `UNIQUE (turno_id, motivo)` (`uq_recordatorios_enviados_turno_motivo`).
- **Flujo del worker (`ProcesarSiguienteRecordatorio.ejecutar()`):**
  1. Obtiene la siguiente `TareaRecordatorio` de `ColaRecordatorios.desencolar()`. Si la cola está vacía, devuelve `None`.
  2. Abre `with self._unidad_de_trabajo() as uow:`.
  3. Busca el turno con `uow.turnos.obtener_por_id(tarea.turno_id)`. Si no existe o `turno.estado == EstadoTurno.CANCELADO`, sale sin registrar envío y retorna un resultado indicando omisión.
  4. Verifica con `uow.recordatorios.existe_envio(tarea.turno_id, tarea.motivo)`. Si ya existe, retorna el registro existente sin duplicar (y si ocurre condición de carrera, la restricción `UNIQUE (turno_id, motivo)` actúa como segunda barrera).
  5. Invoca `self._notificador.enviar_recordatorio(...)`, persiste el `RecordatorioEnviado` en `uow.recordatorios` y ejecuta `uow.commit()`.

### 4. Contrato HTTP y autorización RBAC

- **Decisión:** Agregar `Permiso.CONSULTAR_RECORDATORIOS = "consultar_recordatorios"` en `backend/app/domain/autorizacion.py`, habilitado para `Rol.RECEPCION` y `Rol.RESPONSABLE` (los mismos roles que operan recordatorios y comunicación con pacientes; `Rol.ODONTOLOGO` recibe `403 acceso_denegado`).
- Exponer `GET /api/v1/turnos/{turno_id}/recordatorios` en `backend/app/api/turnos.py`:
  - Verifica que el turno exista (`404 recurso_inexistente` si no existe).
  - Devuelve `200 OK` con `list[RecordatorioSimuladoSalida]` (`id`, `turno_id`, `motivo`, `destinatario`, `enviado_en`) ordenada por `enviado_en ASC, id ASC`.

### 5. Configuración Docker Compose y estrategia de pruebas

- **Decisión:** En `docker-compose.yml` se incorpora el servicio `redis` (`image: redis:7-alpine`, puerto `6379:6379`, healthcheck `redis-cli ping`) y en el servicio `api` se agrega `REDIS_URL: redis://redis:6379/0` en `environment`. La dependencia de `api` sobre `redis` no bloquea el arranque si Redis falla en tiempo de ejecución.
- **Pruebas:**
  - *Unitarias (dominio y aplicación)*: encolado sólo tras `uow.commit()`, no encolado si falla validación o commit, resiliencia cuando `cola.encolar` lanza excepción, procesamiento con `NotificadorSimulado`, idempotencia ante tarea duplicada y omisión cuando el turno fue cancelado o no existe.
  - *Integración y API (PostgreSQL real + Redis/adaptador)*: `ColaRecordatoriosRedis`, persistencia única en `recordatorios_enviados`, endpoint `GET /api/v1/turnos/{turno_id}/recordatorios` con RBAC, y creación/confirmación/consulta de agenda funcionando normalmente cuando `REDIS_URL` apunta a un Redis inaccesible.

## Risks / Trade-offs

- **[Riesgo] Pérdida de recordatorio si Redis está caído en el instante del commit** → **Mitigación:** Aceptado por diseño en `RN-EX-02` (priorizar disponibilidad de la agenda clínica por sobre el recordatorio). El fallo queda registrado en logs y la operación puede reencolarse al confirmar el turno.
- **[Riesgo] Entorno local de tests sin servidor Redis levantado** → **Mitigación:** Los tests de integración de casos de uso, persistencia e idempotencia usan PostgreSQL real + cola Redis cuando `REDIS_URL` está disponible o un cliente Redis con transporte inyectable (`fakeredis` / socket cerrado para simular caída real de red), garantizando que toda la suite `pytest` sea determinística y reproducible.

## Migration Plan

1. Incorporar modelos de dominio (`MotivoRecordatorio`, `TareaRecordatorio`, `RecordatorioEnviado`) y permiso `CONSULTAR_RECORDATORIOS`.
2. Extender puertos de aplicación (`ColaRecordatorios`, `NotificadorRecordatorios`, `RepositorioRecordatorios`, `UnidadDeTrabajo.recordatorios`) y casos de uso (`CrearTurno`, `ConfirmarTurno`, `ProcesarSiguienteRecordatorio`, `ConsultarRecordatoriosTurno`).
3. Añadir `ModeloRecordatorioEnviado` en `backend/app/infrastructure/modelos.py`, `RepositorioRecordatoriosSQLAlchemy`, `NotificadorSimulado`, `ColaRecordatoriosRedis` y `worker_recordatorios.py`.
4. Exponer `GET /api/v1/turnos/{turno_id}/recordatorios` e inyectar `ColaRecordatoriosRedis` en las dependencias de `CrearTurno` y `ConfirmarTurno`.
5. Actualizar `docker-compose.yml`, `backend/requirements.txt` y `backend/.env.example`.

## Open Questions

- Ninguna pregunta bloqueante para `C-16`. El formato de plantilla y credenciales reales de WhatsApp pertenecen a `C-10` (`OP-06`).
