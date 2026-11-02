# Proposal

## Why

La agenda crea, consulta y bloquea turnos, pero un turno nace `programado` y no puede cambiar de estado. Recepción necesita reflejar que el paciente confirmó o canceló (US-005), y una cancelación debe liberar el intervalo para nuevas reservas (RN-TU-01). La restricción de exclusión de C-01b ya ignora los turnos `cancelado`, pero ningún caso de uso los produce.

## What Changes

- Incorporar los estados `confirmado` y `cancelado` y una máquina de estados explícita en el dominio: `programado → confirmado`, `programado → cancelado`, `confirmado → cancelado`. Cualquier otra transición se rechaza con `transicion_invalida` sin alterar el turno.
- Casos de uso `CancelarTurno` y `ConfirmarTurno`: bloquean la fila del turno, aplican la transición y registran el historial `cancelado` / `confirmado` en la misma transacción.
- Endpoints `POST /api/v1/turnos/{turno_id}/cancelar` y `POST /api/v1/turnos/{turno_id}/confirmar`: `200` con el turno, `404` si no existe, `409` por transición inválida.
- Un turno cancelado deja de participar en la validación de disponibilidad del dominio, en la restricción `EXCLUDE` y en el rechazo de bloqueos; un turno confirmado conserva su reserva.
- La agenda (`GET /api/v1/agenda`) informa el `estado` de cada turno para distinguir reservas activas de cancelaciones.

## Capabilities

### New Capabilities

- `ciclo-de-vida-del-turno`: confirmar y cancelar turnos con transiciones válidas, historial y liberación del intervalo cancelado.

### Modified Capabilities

- `consulta-de-agenda`: cada elemento de la respuesta incluye el estado del turno.

## Impact

- Dominio: `EstadoTurno`, `TipoCambio`, error `TransicionInvalidaError` y métodos de transición de `Turno`.
- Aplicación: puertos `obtener_para_actualizar` / `actualizar` del repositorio de turnos; casos de uso nuevos.
- Persistencia: sin cambios de esquema; la columna `estado` y la exclusión `WHERE (estado <> 'cancelado')` ya existen.
- API: dos rutas nuevas y el campo `estado` en la agenda.
- Fuera de alcance: ventana de cancelación, quién puede cancelar (C-08 / pregunta Alta abierta), avisos al paciente, lista de espera y confirmación de turnos vencidos (pregunta Media abierta).
