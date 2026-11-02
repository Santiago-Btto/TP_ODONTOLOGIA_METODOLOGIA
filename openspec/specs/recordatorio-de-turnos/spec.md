# recordatorio-de-turnos Specification

## Purpose

Definir las reglas y escenarios verificables para el encolado en Redis tras commit, el procesamiento idempotente mediante un notificador simulado, la omisión de turnos cancelados, la resiliencia de la agenda cuando Redis no está disponible y la consulta HTTP de recordatorios simulados por turno.

## Requirements

### Requirement: Encolar recordatorio tras confirmar la transacción

El sistema SHALL encolar en Redis una tarea de recordatorio simulado con el identificador del turno y el motivo (`creado` o `confirmado`) únicamente después de que la transacción de base de datos que crea o confirma el turno haya sido confirmada (`commit`). Si la transacción falla o revierte (`rollback`), el sistema SHALL NOT encolar ninguna tarea en Redis.

#### Scenario: Encolar recordatorio al crear un turno válido

- **DADO** un paciente activo, un odontólogo activo y una franja libre dentro de su horario laboral
- **CUANDO** el caso de uso `CrearTurno` confirma la creación del turno en la base de datos
- **ENTONCES** se encola exactamente una tarea de recordatorio para ese `turno_id` con motivo `creado` después del `commit`

#### Scenario: Encolar recordatorio al confirmar un turno programado

- **DADO** un turno existente en estado `programado`
- **CUANDO** el caso de uso `ConfirmarTurno` confirma la transición a `confirmado` en la base de datos
- **ENTONCES** se encola exactamente una tarea de recordatorio para ese `turno_id` con motivo `confirmado` después del `commit`

#### Scenario: No encolar recordatorio si la creación o confirmación falla

- **DADO** un intento de crear o confirmar un turno que falla por validación de dominio o restricción de persistencia
- **CUANDO** la transacción revierte sin confirmar cambios
- **ENTONCES** no se encola ninguna tarea de recordatorio en Redis

### Requirement: Preservar la operatoria de agenda cuando Redis no está disponible

El sistema SHALL preservar el funcionamiento normal de la creación, confirmación, cancelación y consulta de turnos aunque Redis no esté disponible o falle la operación de encolado (RN-EX-02). Un fallo de conexión o escritura en Redis tras el `commit` de PostgreSQL SHALL registrarse sin abortar ni revertir la operación sobre el turno.

#### Scenario: Crear turno con Redis caído

- **DADO** un paciente activo, un odontólogo activo, una franja libre y el servicio Redis inaccesible
- **CUANDO** se solicita crear el turno mediante `POST /api/v1/turnos` o el caso de uso `CrearTurno`
- **ENTONCES** el turno y su historial inicial quedan persistidos en PostgreSQL y la operación responde exitosamente (`201`)

#### Scenario: Confirmar turno y consultar agenda con Redis caído

- **DADO** un turno en estado `programado` y el servicio Redis inaccesible
- **CUANDO** se confirma el turno (`POST /api/v1/turnos/{turno_id}/confirmar`) y luego se consulta la agenda (`GET /api/v1/agenda`)
- **ENTONCES** la confirmación responde `200` con estado `confirmado` y la agenda devuelve el turno actualizado sin error

### Requirement: Procesar recordatorios con notificador simulado e idempotencia

El sistema SHALL procesar las tareas encoladas mediante un worker que invoque un `NotificadorSimulado` (sin envío externo real por WhatsApp) y registre el envío simulado asociado al `(turno_id, motivo)`. El procesamiento SHALL ser idempotente: si una tarea con el mismo `turno_id` y `motivo` se procesa más de una vez, el sistema SHALL registrar un único envío simulado sin duplicados ni error.

#### Scenario: Procesar tarea de recordatorio para un turno activo

- **DADO** un turno existente en estado `programado` o `confirmado` y una tarea encolada con motivo `creado` o `confirmado`
- **CUANDO** el worker procesa la tarea de la cola
- **ENTONCES** el `NotificadorSimulado` registra un envío simulado con el `turno_id`, el `motivo` y la marca temporal de envío

#### Scenario: Reintento idempotente de la misma tarea de recordatorio

- **DADO** un turno activo cuyo recordatorio para el par `(turno_id, motivo)` ya fue registrado por el `NotificadorSimulado`
- **CUANDO** el worker procesa nuevamente una tarea duplicada con el mismo `turno_id` y `motivo`
- **ENTONCES** no se crea un segundo registro ni falla el procesamiento, conservándose exactamente un envío simulado para ese `(turno_id, motivo)`

### Requirement: Omitir recordatorios de turnos cancelados o inexistentes

El sistema SHALL verificar el estado actual del turno en PostgreSQL al momento de procesar una tarea de recordatorio y SHALL NOT enviar ni registrar recordatorio alguno si el turno se encuentra en estado `cancelado` o no existe.

#### Scenario: Turno cancelado antes de que el worker procese su recordatorio

- **DADO** un turno que fue creado (encolando una tarea `creado`) y posteriormente cancelado antes de ejecutarse el worker
- **CUANDO** el worker procesa la tarea pendiente de la cola
- **ENTONCES** el `NotificadorSimulado` no registra ningún envío para ese turno y la tarea se descarta limpiamente

#### Scenario: Tarea de recordatorio para un turno inexistente

- **DADO** una tarea en la cola cuyo `turno_id` no existe en la base de datos
- **CUANDO** el worker procesa la tarea
- **ENTONCES** no se registra ningún envío simulado y el worker continúa sin error fatal

### Requirement: Consultar recordatorios simulados de un turno por HTTP

El sistema SHALL exponer el endpoint autenticado `GET /api/v1/turnos/{turno_id}/recordatorios` para los roles `recepcion` y `responsable`, devolviendo la lista ordenada cronológicamente de los recordatorios simulados registrados para ese turno (`turno_id`, `motivo`, `enviado_en`). Si el turno no existe, SHALL responder `404`; sin token válido, `401`; y para un actor con rol `odontologo`, `403`.

#### Scenario: Consulta exitosa de recordatorios simulados de un turno

- **DADO** un turno existente cuyos recordatorios `creado` y `confirmado` fueron procesados por el worker
- **CUANDO** un actor con rol `recepcion` o `responsable` consulta `GET /api/v1/turnos/{turno_id}/recordatorios`
- **ENTONCES** el sistema responde `200` con los dos recordatorios simulados ordenados por `enviado_en` ascendente

#### Scenario: Consulta de recordatorios para un turno inexistente o sin permisos

- **DADO** un identificador de turno inexistente o un actor con rol `odontologo`
- **CUANDO** se invoca `GET /api/v1/turnos/{turno_id}/recordatorios`
- **ENTONCES** el sistema responde `404` (`recurso_inexistente`) si el turno no existe para un rol autorizado, o `403` (`acceso_denegado`) si el actor tiene rol `odontologo`
