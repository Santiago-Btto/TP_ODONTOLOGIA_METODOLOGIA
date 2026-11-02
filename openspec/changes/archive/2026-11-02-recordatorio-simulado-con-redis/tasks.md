# Tasks

## 1. Red de seguridad y modelo de dominio de recordatorios

- [x] 1.1 Ejecutar la suite existente (`pytest backend/tests`) como red de seguridad y verificar que la línea base de tests pasa en verde antes de modificar archivos
- [x] 1.2 Crear `backend/app/domain/recordatorios.py` con `MotivoRecordatorio` (`creado`, `confirmado`), `TareaRecordatorio`, `RecordatorioEnviado` y agregar `Permiso.CONSULTAR_RECORDATORIOS` (habilitado para `recepcion` y `responsable`) en `backend/app/domain/autorizacion.py`, verificando con tests unitarios en `backend/tests/domain/test_recordatorios.py` y `backend/tests/domain/test_autorizacion.py`

## 2. Casos de uso: encolado pos-commit, resiliencia y procesamiento

- [x] 2.1 Extender `backend/app/application/puertos.py` con `ColaRecordatorios`, `ColaRecordatoriosNoOp`, `NotificadorRecordatorios`, `RepositorioRecordatorios` y el atributo `recordatorios` en `UnidadDeTrabajo`, actualizando los dobles de prueba existentes y verificando que `pytest backend/tests/domain backend/tests/application` sigue pasando
- [x] 2.2 Integrar el encolado pos-commit y la degradación segura ante fallos de Redis en `CrearTurno` (`backend/app/application/crear_turno.py`) y `ConfirmarTurno` (`backend/app/application/cambiar_estado_turno.py`), verificando con tests unitarios en `backend/tests/application/test_encolado_recordatorios.py` que se encola sólo tras `uow.commit()`, que un rollback no encola y que un fallo de la cola no aborta el caso de uso
- [x] 2.3 Implementar `ProcesarSiguienteRecordatorio` y `ConsultarRecordatoriosTurno` en `backend/app/application/procesar_recordatorio.py`, verificando con tests unitarios en `backend/tests/application/test_procesar_recordatorio.py` el envío con `NotificadorSimulado`, la idempotencia por `(turno_id, motivo)` y la omisión de turnos cancelados o inexistentes

## 3. Infraestructura: PostgreSQL, adaptador Redis y worker

- [x] 3.1 Agregar `ModeloRecordatorioEnviado` (con `UNIQUE (turno_id, motivo)` y `CHECK (motivo IN ('creado', 'confirmado'))`) en `backend/app/infrastructure/modelos.py`, `RepositorioRecordatoriosSQLAlchemy` en `backend/app/infrastructure/repositorios.py` y su cableado en `UnidadDeTrabajoSQLAlchemy`, verificando con tests de integración contra PostgreSQL real en `backend/tests/infrastructure/test_recordatorios_persistencia.py`
- [x] 3.2 Implementar `ColaRecordatoriosRedis`, `ColaRecordatoriosMemoria` y `NotificadorSimulado` en `backend/app/infrastructure/recordatorios_redis.py` junto con el entrypoint `backend/app/infrastructure/worker_recordatorios.py` (`--una-vez`), agregando `redis==5.2.0` en `backend/requirements.txt` y verificando con tests en `backend/tests/infrastructure/test_cola_y_worker_recordatorios.py` (incluyendo encolado/desencolado JSON, idempotencia y degradación cuando Redis no está disponible)

## 4. API HTTP, configuración Docker Compose y documentación

- [x] 4.1 Exponer `GET /api/v1/turnos/{turno_id}/recordatorios` en `backend/app/api/turnos.py`, cablear la cola de recordatorios en `CrearTurno` y `ConfirmarTurno` y agregar `REDIS_URL` en `backend/app/infrastructure/configuracion.py`, verificando con tests en `backend/tests/api/test_recordatorios_api.py` (`200`, `404`, `401`, `403`, ciclo completo crear/confirmar/cancelar + worker y operación normal de agenda con `REDIS_URL` caído)
- [x] 4.2 Incorporar el servicio `redis` (`redis:7-alpine`) y `REDIS_URL` en `docker-compose.yml` y `backend/.env.example`, y documentar el worker y el endpoint de recordatorios simulados en `README.md`, verificando la validez de `docker-compose.yml` y la documentación

## 5. Verificación integral del cambio

- [x] 5.1 Ejecutar la suite completa de pruebas (`pytest backend/tests`) y `openspec validate recordatorio-simulado-con-redis --strict`, verificando que todos los tests unitarios y de integración y la especificación pasan sin errores

## Workflow follow-up

- Archivar el cambio (`openspec-archive-change`) y sincronizar specs una vez completada y validada la implementación.
