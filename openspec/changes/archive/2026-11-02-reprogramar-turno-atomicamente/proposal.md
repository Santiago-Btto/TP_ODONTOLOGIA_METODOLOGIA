# Proposal

## Why

Recepción necesita mover un turno de horario, de profesional o de box sin cancelarlo y crearlo de nuevo (US-004). La KB exige que el nuevo intervalo se valide contra ambos recursos y contra los bloqueos (RN-DI-02 a RN-DI-04) y que el intervalo anterior se libere únicamente si el cambio es válido (RN-TU-02), dejando historial (RN-TU-04). C-03 ya dejó disponible la regla de bloqueos y el protocolo de bloqueo de recursos; C-05 aportó la máquina de estados.

## What Changes

- Caso de uso `ReprogramarTurno`: cambia `inicio`, `fin`, `profesional_id` y/o `box_id` de un turno existente en una sola transacción.
- El propio turno se excluye de la comparación de disponibilidad: moverlo dentro de su mismo intervalo o solaparlo con su versión anterior es válido.
- El candidato se valida contra turnos activos y bloqueos del profesional y del box de destino; ante cualquier rechazo el turno conserva intervalo, recursos y estado, y no se escribe historial.
- El historial registra `reprogramado` con el resumen anterior y posterior (profesional, box, inicio y fin), como prevé `HistorialDeCambio` en la KB.
- `PATCH /api/v1/turnos/{turno_id}`: `200`, `404`, `409` (conflicto o turno cancelado) y `422`.

## Capabilities

### New Capabilities

- `reprogramacion-de-turnos`: reprogramar un turno activo de forma atómica, con autoexclusión, validación contra turnos y bloqueos, historial con antes/después y contrato HTTP.

### Modified Capabilities

Ninguna: altas, bloqueos y transiciones de estado conservan su contrato.

## Impact

- Dominio: `ResumenTurno`, `TipoCambio.REPROGRAMADO`, `ReprogramacionSinCambiosError`, `Turno.reprogramar(...)` y autoexclusión en `verificar_disponibilidad`.
- Aplicación: `ReprogramarTurno`, reutilizando los puertos existentes (`obtener_para_actualizar`, `actualizar`, `recursos.bloquear`, `bloqueos.que_se_solapan`).
- Persistencia: columnas `antes` y `despues` (`JSONB`, opcionales) en `historial_cambios`.
- API: `PATCH /api/v1/turnos/{turno_id}` con `ReprogramacionEntrada`.
- Pruebas: cambio válido, conflictos por profesional/box/bloqueo, autoexclusión, fallo atómico y concurrencia contra PostgreSQL real.
