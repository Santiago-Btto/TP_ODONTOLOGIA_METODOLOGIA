# Design

## Context

Véanse `proposal.md` y el delta spec. Ya existen: `Turno` con su máquina de estados (C-05), `verificar_disponibilidad` y `verificar_bloqueos_de_turno` en el dominio, `obtener_para_actualizar` (`SELECT ... FOR UPDATE` sobre el turno) y `actualizar` en el repositorio, el bloqueo de filas de recursos en orden profesional → box (C-03) y las exclusiones GiST de `turnos` con predicado `estado <> 'cancelado'`. La KB (Flujo 2) pide obtener el turno, excluirlo de la comparación, validar contra turnos y bloqueos de ambos recursos y, si falla, conservar el original sin liberar ni reservar nada.

## Goals / Non-Goals

**Goals:**

- Validación en el dominio y en la aplicación; la API sólo traduce HTTP.
- Atomicidad: turno actualizado + historial `reprogramado`, o nada.
- Ausencia de doble reserva frente a altas, bloqueos y otras reprogramaciones concurrentes, sin introducir interbloqueos.

**Non-Goals:**

- Cambiar paciente o prestación del turno: la KB sólo menciona horario y recursos.
- Recalcular el fin por un cambio de prestación.
- Decidir si reprogramar un turno confirmado exige reconfirmarlo (pregunta abierta; se conserva el estado).
- Autorización por rol y actor del cambio (C-08).

## Decisions

### 1. Regla en el dominio

`Turno.reprogramar(inicio, fin, profesional_id, box_id)` devuelve una copia con los nuevos valores, valida `fin > inicio` mediante el constructor y rechaza:

- un turno `cancelado` con `TransicionInvalidaError` (`transicion_invalida`, acción “reprogramar”), porque cancelar es terminal en C-05 y la KB deja abierta la reprogramación de cancelados;
- un candidato idéntico al original con `ReprogramacionSinCambiosError` (`reprogramacion_sin_cambios`), para no registrar eventos sin cambio real.

El estado se conserva: un turno `confirmado` sigue `confirmado`. Pasarlo a `programado` sería una regla de producto no definida en la KB.

`verificar_disponibilidad` ignora los turnos activos con el mismo `id` que el candidato. La autoexclusión queda en la regla y no depende de cada consulta. Para altas no cambia nada, porque un turno nuevo no puede estar persistido.

`ResumenTurno` (profesional, box, inicio, fin) es un valor de dominio. `HistorialDeCambio` suma `antes` y `despues` opcionales con valor por defecto `None`, sin alterar los eventos existentes.

### 2. Cálculo del intervalo candidato

Los campos omitidos conservan su valor actual. Si se informa `inicio` sin `fin`, se conserva la duración vigente del turno (`fin - inicio`); no se recalcula desde la prestación, porque el turno pudo haberse creado con un `fin` explícito. Si se informa `fin`, se usa tal cual.

### 3. Orden de bloqueos y transacción

Dentro de una unidad de trabajo:

1. `obtener_para_actualizar(turno_id)`: bloquea la fila del turno. Una cancelación, confirmación o reprogramación concurrente del mismo turno queda en serie.
2. Validar existencia del profesional y box de destino (`404`).
3. Construir el candidato con la regla del dominio.
4. `recursos.bloquear(profesional_destino, box_destino)`: el mismo orden profesional → box de `CrearTurno` y `CrearBloqueo`.
5. Leer turnos activos y bloqueos intersectantes de los recursos de destino **después** del bloqueo (`READ COMMITTED` ve lo confirmado por quien liberó el lock), excluir el propio turno y aplicar las reglas del dominio.
6. `actualizar` + historial `reprogramado` + un único `commit`.

Orden global: fila de turno → filas de recursos (profesional, luego box). `CrearTurno` y `CrearBloqueo` nunca bloquean filas de turnos, y confirmar/cancelar sólo bloquean la fila del turno, así que no hay ciclos de espera. No se bloquean los recursos de origen: liberar un intervalo no exige exclusión mutua y, mientras no se confirma, el resto de las transacciones sigue viendo el intervalo anterior ocupado (RN-TU-02).

La exclusión GiST evalúa la nueva versión de la fila contra las demás; la versión anterior del mismo turno no cuenta. Es la segunda barrera si una escritura eludiera la aplicación.

### 4. Persistencia del historial

`historial_cambios` suma `antes` y `despues` como `JSONB` anulables, con instantes ISO 8601 en UTC. Se elige `JSONB` en lugar de columnas tipadas porque el resumen es un registro de auditoría inmutable que no se consulta por campo. Sin migraciones versionadas (llegan con C-07): `create_all` no agrega columnas a una tabla existente, por lo que una base local creada antes de este change debe recrearse (`docker compose down -v`).

### 5. Contrato HTTP

`PATCH /api/v1/turnos/{turno_id}` con `ReprogramacionEntrada` (`extra="forbid"`): `inicio`, `fin` (`AwareDatetime`), `profesional_id`, `box_id` (`1..64`), todos opcionales y al menos uno presente. Respuestas: `200` con `TurnoSalida`; `404 recurso_inexistente` (turno, profesional o box); `409 conflicto_profesional` / `conflicto_box` / `conflicto_bloqueo_profesional` / `conflicto_bloqueo_box` / `transicion_invalida`; `422 intervalo_invalido` / `reprogramacion_sin_cambios`, o `detail` de FastAPI para cuerpo vacío, campos desconocidos o fechas sin zona.

## Risks / Trade-offs

- [Conflicto falso durante una reprogramación en curso] → un alta concurrente sobre el intervalo de origen puede ver todavía el turno anterior y rechazarse. Es conservador y consistente con RN-TU-02.
- [Esquema local preexistente] → recrear la base de desarrollo; documentado en el README hasta C-07.
- [Reprogramar un confirmado] → conserva `confirmado`; registrar la duda en las preguntas abiertas.

## Migration Plan

`create_all` crea las columnas nuevas en bases vacías y en la base de pruebas. Una base local previa se recrea. Revertir implica retirar la ruta y el caso de uso; las columnas anulables pueden quedar sin efecto sobre los demás casos de uso.

## Open Questions

- ¿Reprogramar un turno confirmado debe volverlo a `programado`?
- ¿Se podrá cambiar la prestación o el paciente de un turno existente?
