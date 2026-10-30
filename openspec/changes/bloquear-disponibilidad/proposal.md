# Proposal

## Why

La agenda permite crear y consultar turnos, pero todavía no puede reservar intervalos no clínicos de un profesional o un box. C-03 agrega bloqueos persistentes para que nuevas reservas respeten esa indisponibilidad y prepara la validación que C-04 necesitará al reprogramar.

## What Changes

- Registrar bloqueos de **un profesional o un box**, con intervalo válido y motivo opcional, mediante `POST /api/v1/bloqueos`.
- Rechazar un bloqueo que intersecte un turno activo existente del mismo recurso, con error explícito y sin alterar ese turno. Es una política conservadora provisional: la KB deja abierta la resolución clínica de estos casos.
- Rechazar altas de turnos que intersecten bloqueos del profesional o box; admitir intervalos que sólo se tocan en el borde.
- Serializar las operaciones de turno y bloqueo sobre recursos compartidos para evitar carreras entre tablas. Los bloqueos del mismo recurso pueden solaparse; la KB no los prohíbe.
- Añadir pruebas de dominio, aplicación, PostgreSQL y API, incluida una carrera concurrente. C-04 consumirá esta regla al implementar reprogramaciones; este change no agrega `PATCH`.

## Capabilities

### New Capabilities

- `bloqueo-de-disponibilidad`: registrar y persistir intervalos no disponibles de un profesional o box, con validaciones y contrato HTTP.

### Modified Capabilities

- `creacion-de-turnos`: impedir nuevas reservas que intersecten bloqueos del profesional o box, manteniendo turno e historial en una sola transacción.

## Impact

- Dominio y aplicación: entidad de bloqueo, errores y regla de intersección; caso de uso `CrearBloqueo`, puerto de bloqueos y extensión de `CrearTurno`.
- Persistencia: tabla `bloqueos_disponibilidad` con claves foráneas, `CHECK` e índices de consulta; adaptador SQLAlchemy y bloqueo transaccional compartido de recursos.
- API: `POST /api/v1/bloqueos` y traducción de errores a `404`, `409` o `422`; `POST /api/v1/turnos` añade conflicto por bloqueo.
- Pruebas: casos de éxito, error, borde y concurrencia contra PostgreSQL real. Dependencia C-01b completada; C-04 permanece pendiente.
