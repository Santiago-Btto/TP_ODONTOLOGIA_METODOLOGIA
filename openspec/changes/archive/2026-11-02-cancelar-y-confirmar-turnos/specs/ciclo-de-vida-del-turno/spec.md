# Spec Delta

## ADDED Requirements

### Requirement: Confirmar un turno programado
El sistema SHALL permitir confirmar un turno en estado `programado`. La confirmación SHALL cambiar su estado a `confirmado`, conservar intervalo y recursos, y registrar en la misma transacción exactamente un evento de historial `confirmado`.

#### Scenario: Confirmación exitosa
- **DADO** un turno `programado` de 09:00 a 09:30
- **CUANDO** se confirma
- **ENTONCES** el turno queda `confirmado` con el mismo intervalo y recursos y se registra un evento `confirmado`

#### Scenario: Confirmar conserva la reserva
- **DADO** un turno `confirmado` de 09:00 a 09:30 de un profesional y un box
- **CUANDO** se solicita otro turno intersectante del mismo profesional
- **ENTONCES** el sistema informa un conflicto de profesional

### Requirement: Cancelar un turno activo
El sistema SHALL permitir cancelar un turno `programado` o `confirmado`. La cancelación SHALL cambiar su estado a `cancelado` y registrar en la misma transacción exactamente un evento de historial `cancelado`.

#### Scenario: Cancelación de un turno programado
- **DADO** un turno `programado`
- **CUANDO** se cancela
- **ENTONCES** el turno queda `cancelado` y se registra un evento `cancelado`

#### Scenario: Cancelación de un turno confirmado
- **DADO** un turno `confirmado`
- **CUANDO** se cancela
- **ENTONCES** el turno queda `cancelado` y el historial contiene `creado`, `confirmado` y `cancelado` en ese orden

### Requirement: Liberar el intervalo de un turno cancelado
Un turno `cancelado` SHALL dejar de participar en la validación de disponibilidad del dominio, en la restricción de exclusión de la base y en el rechazo de bloqueos, de modo que su intervalo pueda reservarse o bloquearse de nuevo.

#### Scenario: Cancelar libera el intervalo para un nuevo turno
- **DADO** un turno de 09:00 a 09:30 del profesional P en el box B, luego cancelado
- **CUANDO** se solicita un nuevo turno de P en B de 09:00 a 09:30
- **ENTONCES** el sistema crea el nuevo turno

#### Scenario: Cancelar libera el intervalo para un bloqueo
- **DADO** un turno cancelado de 09:00 a 09:30 del profesional P
- **CUANDO** se registra un bloqueo de P de 09:00 a 10:00
- **ENTONCES** el bloqueo se registra

### Requirement: Rechazar transiciones inválidas sin cambios
El sistema SHALL rechazar confirmar un turno `confirmado` o `cancelado` y cancelar un turno `cancelado`, informando una transición inválida, sin modificar el estado ni agregar historial.

#### Scenario: Confirmar un turno cancelado
- **DADO** un turno `cancelado`
- **CUANDO** se intenta confirmarlo
- **ENTONCES** se informa una transición inválida y el turno sigue `cancelado` sin historial nuevo

#### Scenario: Cancelar dos veces
- **DADO** un turno `cancelado`
- **CUANDO** se intenta cancelarlo de nuevo
- **ENTONCES** se informa una transición inválida y el historial conserva un único `cancelado`

#### Scenario: Confirmar dos veces
- **DADO** un turno `confirmado`
- **CUANDO** se intenta confirmarlo de nuevo
- **ENTONCES** se informa una transición inválida y el historial conserva un único `confirmado`

#### Scenario: Turno inexistente
- **DADO** que no existe un turno con el identificador indicado
- **CUANDO** se intenta cancelarlo o confirmarlo
- **ENTONCES** se informa que el recurso no existe y no se escribe historial

### Requirement: Serializar transiciones concurrentes
Dos transiciones simultáneas sobre el mismo turno SHALL ejecutarse en serie: la segunda SHALL evaluarse contra el estado confirmado por la primera.

#### Scenario: Dos cancelaciones simultáneas
- **DADO** un turno `programado` y dos solicitudes concurrentes de cancelación
- **CUANDO** la primera confirma su transacción
- **ENTONCES** la segunda informa una transición inválida y existe un único evento `cancelado`

### Requirement: Exponer cancelación y confirmación por HTTP
El sistema SHALL exponer `POST /api/v1/turnos/{turno_id}/cancelar` y `POST /api/v1/turnos/{turno_id}/confirmar`, que responden `200` con el turno actualizado, `404` con `recurso_inexistente` si el turno no existe y `409` con `transicion_invalida` ante una transición no permitida.

#### Scenario: Confirmación por API
- **DADO** un turno `programado` creado por API
- **CUANDO** se envía `POST /api/v1/turnos/{id}/confirmar`
- **ENTONCES** la respuesta es `200` con estado `confirmado`

#### Scenario: Cancelación por API y reutilización del horario
- **DADO** un turno creado por API de 09:00 a 09:30
- **CUANDO** se envía `POST /api/v1/turnos/{id}/cancelar` y luego `POST /api/v1/turnos` con el mismo intervalo y recursos
- **ENTONCES** la cancelación responde `200` con estado `cancelado` y el nuevo alta responde `201`

#### Scenario: Transición inválida por API
- **DADO** un turno cancelado
- **CUANDO** se envía `POST /api/v1/turnos/{id}/confirmar`
- **ENTONCES** la respuesta es `409` con código `transicion_invalida`

#### Scenario: Turno inexistente por API
- **DADO** que no existe el turno indicado
- **CUANDO** se envía `POST /api/v1/turnos/{id}/cancelar`
- **ENTONCES** la respuesta es `404` con código `recurso_inexistente`
