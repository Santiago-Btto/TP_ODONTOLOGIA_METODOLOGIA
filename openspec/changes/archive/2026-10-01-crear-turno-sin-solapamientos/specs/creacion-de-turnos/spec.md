# Spec Delta

## Purpose

Define una reserva de agenda confiable que protege simultáneamente la disponibilidad de un profesional y un box en el núcleo local del sistema.

## ADDED Requirements

### Requirement: Crear una reserva válida
El sistema SHALL crear un turno cuando paciente ficticio, profesional, box y prestación están identificados, el intervalo es válido y ambos recursos están disponibles. El turno creado SHALL conservar su intervalo y recursos, y generar un evento de historial de tipo `creado`.

#### Scenario: Alta exitosa
- **WHEN** se solicita un turno de intervalo válido para un profesional y un box sin reservas activas conflictivas
- **THEN** el sistema crea el turno y registra exactamente un evento `creado` asociado

### Requirement: Proteger la disponibilidad del profesional
El sistema SHALL rechazar la creación de un turno cuyo intervalo comparta tiempo efectivo con un turno activo del mismo profesional, aun si los boxes son distintos.

#### Scenario: Conflicto por profesional
- **WHEN** se solicita un turno que intersecta una reserva activa del mismo profesional con otro box
- **THEN** el sistema informa un conflicto de profesional y no crea turno ni historial nuevos

### Requirement: Proteger la disponibilidad del box
El sistema SHALL rechazar la creación de un turno cuyo intervalo comparta tiempo efectivo con un turno activo del mismo box, aun si los profesionales son distintos.

#### Scenario: Conflicto por box
- **WHEN** se solicita un turno que intersecta una reserva activa del mismo box con otro profesional
- **THEN** el sistema informa un conflicto de box y no crea turno ni historial nuevos

### Requirement: Admitir límites contiguos
El sistema SHALL tratar los intervalos de los turnos como semiabiertos `[inicio, fin)`. Un turno que inicia exactamente cuando termina otro turno activo del mismo recurso SHALL poder crearse.

#### Scenario: Reserva contigua
- **WHEN** se solicita un turno cuyo inicio coincide exactamente con el fin de una reserva activa del mismo profesional y box
- **THEN** el sistema crea el nuevo turno sin informar conflicto

### Requirement: Rechazar datos temporales inválidos
El sistema SHALL rechazar la creación cuando el fin no sea estrictamente posterior al inicio o cuando la duración de la prestación no sea positiva. Un rechazo SHALL conservar sin cambios las reservas y el historial existentes.

#### Scenario: Intervalo sin duración positiva
- **WHEN** se solicita un turno cuyo fin es igual o anterior a su inicio
- **THEN** el sistema informa un error de intervalo inválido y no persiste cambios

#### Scenario: Prestación con duración inválida
- **WHEN** se solicita calcular un turno con una prestación de duración cero o negativa
- **THEN** el sistema informa un error de duración inválida y no persiste cambios
