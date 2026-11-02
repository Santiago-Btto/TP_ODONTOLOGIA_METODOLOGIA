# Design

## Context

Véanse `proposal.md` y los delta specs. C-01b persiste `turnos.estado` como texto y declara las exclusiones GiST con `WHERE (estado <> 'cancelado')`; las consultas de disponibilidad de turnos (`activos_que_se_solapan`, `activos_del_recurso_que_se_solapan`) ya filtran `estado != 'cancelado'`. El dominio sólo conoce `programado` y el historial sólo `creado`. La KB fija RN-TU-01, RN-TU-03, RN-TU-04 y US-005; deja abiertas la ventana de cancelación, quién puede cancelar y qué ocurre al confirmar un turno vencido.

## Goals / Non-Goals

**Goals:**

- Expresar las transiciones permitidas en el dominio puro, sin FastAPI ni SQLAlchemy.
- Cambiar estado e insertar historial en una única transacción.
- Serializar transiciones concurrentes sobre el mismo turno.
- Reutilizar la exclusión en base existente para que el intervalo cancelado quede libre también para escrituras directas.

**Non-Goals:**

- Ventana temporal de cancelación, reglas por rol o actor del cambio (C-08).
- Avisar al paciente, lista de espera o recordatorios (C-16 / C-10).
- Revertir una cancelación o un “des-confirmar”: no están en la KB.
- Reprogramación (C-04).

## Decisions

### 1. Máquina de estados en el dominio

`EstadoTurno` suma `confirmado` y `cancelado`; `TipoCambio` suma `confirmado` y `cancelado`. `Turno` (inmutable) expone `confirmar()` y `cancelar()`, que devuelven una copia con el nuevo estado mediante `dataclasses.replace`, y la propiedad `activo` (`estado != cancelado`).

| Desde \ Acción | confirmar | cancelar |
|---|---|---|
| programado | confirmado | cancelado |
| confirmado | `transicion_invalida` | cancelado |
| cancelado | `transicion_invalida` | `transicion_invalida` |

Confirmar dos veces se rechaza en lugar de ser idempotente: así cada evento del historial corresponde a un cambio real y el cliente detecta un doble clic. Cancelar es terminal porque la KB no define una reactivación. RN-TU-03 pide no omitir validaciones de horario o recurso al confirmar; confirmar no cambia ninguno de los dos y el turno ya ocupa el intervalo, por lo que no se revalida disponibilidad.

Alternativa descartada: un único `CambiarEstado(estado_destino)`, que trasladaría al cliente la responsabilidad de conocer la máquina de estados.

### 2. Casos de uso y bloqueo de fila

`CancelarTurno` y `ConfirmarTurno` comparten la estructura: dentro de la unidad de trabajo leen el turno con `SELECT ... FOR UPDATE` (`obtener_para_actualizar`), aplican la transición del dominio, actualizan la fila (`actualizar`), agregan `HistorialDeCambio(tipo)` y confirman una sola vez. Bajo `READ COMMITTED`, una segunda transición concurrente espera el bloqueo y relee la versión confirmada, por lo que dos cancelaciones simultáneas producen una cancelación y un `transicion_invalida`, nunca dos eventos. Sólo se bloquea la fila del turno: ninguna de las dos operaciones lee disponibilidad, así que no toma filas de profesional ni de box y no puede formar ciclos con el protocolo profesional → box de C-03.

Un turno inexistente se informa con `RecursoInexistenteError("turno", id)` (`recurso_inexistente`, `404`), coherente con los demás recursos.

### 3. Liberación del intervalo

No hay cambio de esquema. Al pasar a `cancelado`, la fila sale del predicado parcial de ambas exclusiones GiST y de las consultas de disponibilidad, de modo que un alta o un bloqueo posteriores sobre ese intervalo se aceptan si no hay otro conflicto. Un turno `confirmado` sigue dentro del predicado y conserva su reserva.

### 4. Contrato HTTP

`POST /api/v1/turnos/{turno_id}/cancelar` y `POST /api/v1/turnos/{turno_id}/confirmar`, sin cuerpo, responden `200` con `TurnoSalida` (incluye `estado`). Se eligen subrecursos de acción con `POST` porque son comandos con efectos (historial) y no ediciones parciales del recurso; `PATCH` queda para la reprogramación de C-04. `409 transicion_invalida` y `404 recurso_inexistente` usan el cuerpo `{codigo, detalle}` existente. `turno_id` se valida con longitud `1..64`, igual que el resto de los identificadores.

La agenda agrega `estado` a `TurnoAgendaSalida` y sigue listando los turnos cancelados: la vista los necesita para mostrar la cancelación, y filtrarlos cambiaría el contrato de C-02 sin una decisión de producto.

## Risks / Trade-offs

- [Confirmar un turno vencido] → se permite; la KB lo marca como pregunta abierta. Se documenta para revisarlo con el Product Owner.
- [Cancelar sin ventana ni rol] → cualquier llamada a la API local puede cancelar hasta que C-08 agregue autenticación; la ventana sigue abierta (RN-EX-03).
- [Agenda con cancelados] → los clientes deben usar `estado` para no mostrar un cancelado como ocupado.

## Migration Plan

Sin migración: los valores nuevos caben en `turnos.estado` (`VARCHAR(20)`) y `historial_cambios.tipo` (`VARCHAR(20)`). Revertir implica retirar rutas y casos de uso; los turnos ya cancelados deben conservarse porque la exclusión parcial los ignora correctamente.

## Open Questions

- ¿Puede confirmarse un turno cuyo inicio ya pasó?
- ¿Cuál es la ventana de cancelación y quién puede cancelar?
- ¿La agenda debería ocultar turnos cancelados por defecto?
