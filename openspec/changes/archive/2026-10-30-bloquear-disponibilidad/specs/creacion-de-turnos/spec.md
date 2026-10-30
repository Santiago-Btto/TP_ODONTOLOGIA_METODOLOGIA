# Spec Delta

## ADDED Requirements

### Requirement: Respetar bloqueos al crear turnos
El sistema SHALL rechazar una nueva reserva que intersecte un bloqueo del mismo profesional o del mismo box, aun cuando no haya otros turnos. Un rechazo SHALL dejar intactos turnos, bloqueos e historiales; los intervalos que sólo se tocan en un borde SHALL poder reservarse.

#### Scenario: Alta rechazada por bloqueo de profesional
- **DADO** un bloqueo del profesional P de 09:00 a 10:00 y un box libre
- **CUANDO** se solicita un turno de P de 09:30 a 10:00 en ese box
- **ENTONCES** se informa un conflicto de bloqueo de profesional y no se crean turno ni historial

#### Scenario: Alta rechazada por bloqueo de box
- **DADO** un bloqueo del box B de 09:00 a 10:00 y un profesional libre
- **CUANDO** se solicita un turno de ese profesional de 09:30 a 10:00 en B
- **ENTONCES** se informa un conflicto de bloqueo de box y no se crean turno ni historial

#### Scenario: Alta contigua a un bloqueo
- **DADO** un bloqueo del profesional indicado que termina a las 09:00 y un box libre
- **CUANDO** se solicita un turno que comienza exactamente a las 09:00
- **ENTONCES** se crea el turno y su único evento de historial `creado`

#### Scenario: Alta que termina justo al comenzar un bloqueo
- **DADO** un bloqueo del box indicado que comienza a las 09:30 y un profesional libre
- **CUANDO** se solicita un turno que termina exactamente a las 09:30 en ese box
- **ENTONCES** se crea el turno y su único evento de historial `creado`

#### Scenario: Conflicto de bloqueo por API
- **DADO** un bloqueo del profesional P que intersecta el intervalo solicitado
- **CUANDO** se envía `POST /api/v1/turnos` para P
- **ENTONCES** la respuesta es `409` con código `conflicto_bloqueo_profesional` y no se crea turno ni historial
