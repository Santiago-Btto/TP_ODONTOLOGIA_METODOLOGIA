# Funcionalidades

Las historias describen el MVP de dominio ejecutable. No implican una interfaz ni una integración externa.

## Épica 1: Agenda sin solapamientos

### US-001 — Crear un turno válido

**Como** recepción
**Quiero** crear un turno para un paciente ficticio, profesional, box y prestación
**Para** reservar un horario operativo de la clínica.

**Criterios de aceptación**:
- [ ] El turno requiere los datos y recursos definidos por RN-DA-01.
- [ ] La duración o el fin producen un intervalo válido.
- [ ] Se rechaza si el profesional o box tiene un intervalo intersectante.
- [ ] Se acepta si sólo es contiguo a otra reserva.

**Reglas relacionadas**: RN-DA-01, RN-DA-02, RN-DA-03, RN-DI-01, RN-DI-02, RN-DI-03.

### US-002 — Consultar agenda

**Como** recepción u odontólogo/a
**Quiero** consultar la agenda diaria o semanal por profesional y/o box
**Para** conocer la disponibilidad y los turnos reservados.

**Criterios de aceptación**:
- [ ] La consulta permite filtrar por rango de tiempo.
- [ ] La consulta identifica el profesional y box del turno.
- [ ] La presentación concreta queda para un adaptador futuro, no para este MVP.

**Reglas relacionadas**: RN-DI-01.

### US-003 — Bloquear disponibilidad

**Como** recepción o responsable de clínica
**Quiero** registrar un bloqueo de profesional o box
**Para** impedir que se reserve un intervalo no disponible.

**Criterios de aceptación**:
- [ ] Un bloqueo tiene recurso, inicio y fin válidos.
- [ ] Un nuevo turno o reprogramación que lo intersecte es rechazado.

**Reglas relacionadas**: RN-DA-02, RN-DI-04.

## Épica 2: Cambios trazables

### US-004 — Reprogramar un turno

**Como** recepción
**Quiero** cambiar el horario o recursos de un turno
**Para** atender cambios de último momento sin perder la agenda.

**Criterios de aceptación**:
- [ ] El nuevo intervalo se valida contra profesional, box y bloqueos.
- [ ] Si la validación falla, el turno previo no se modifica.
- [ ] Si es válida, se libera el intervalo previo y se registra el cambio.

**Reglas relacionadas**: RN-DI-02, RN-DI-03, RN-DI-04, RN-TU-02, RN-TU-04.

### US-005 — Cancelar y confirmar un turno

**Como** recepción
**Quiero** cancelar o confirmar un turno
**Para** reflejar el estado operativo y liberar un horario cancelado.

**Criterios de aceptación**:
- [ ] Una cancelación libera el intervalo para nuevas reservas.
- [ ] La confirmación y cancelación se registran en el historial.
- [ ] La política de quién y hasta cuándo puede cancelar sigue pendiente.

**Reglas relacionadas**: RN-TU-01, RN-TU-03, RN-TU-04.
