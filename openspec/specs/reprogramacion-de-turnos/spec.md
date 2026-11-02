# reprogramacion-de-turnos Specification

## Purpose

Permite cambiar horario, profesional o box de un turno activo de forma atómica, validando el destino contra turnos y bloqueos y dejando trazabilidad del antes y el después.

## Requirements

### Requirement: Reprogramar un turno activo
El sistema SHALL permitir cambiar el inicio, el fin, el profesional y/o el box de un turno `programado` o `confirmado`. Los campos omitidos SHALL conservar su valor; si se cambia el inicio sin indicar el fin, SHALL conservarse la duración vigente. El estado del turno SHALL conservarse. El cambio SHALL registrar en la misma transacción exactamente un evento `reprogramado` con el resumen anterior y posterior (profesional, box, inicio y fin).

#### Scenario: Cambio de horario válido
- **DADO** un turno de 09:00 a 09:30 del profesional P en el box B y la agenda libre a las 11:00
- **CUANDO** se reprograma con inicio a las 11:00
- **ENTONCES** el turno queda de 11:00 a 11:30 en P y B y se registra un evento `reprogramado` con antes 09:00–09:30 y después 11:00–11:30

#### Scenario: Cambio de recursos válido
- **DADO** un turno de P en B y otro profesional y otro box libres
- **CUANDO** se reprograma al otro profesional y al otro box sin cambiar el horario
- **ENTONCES** el turno conserva el intervalo y cambia sus recursos

#### Scenario: Reprogramar conserva el estado confirmado
- **DADO** un turno `confirmado`
- **CUANDO** se reprograma a un horario libre
- **ENTONCES** el turno sigue `confirmado`

#### Scenario: El intervalo anterior queda libre
- **DADO** un turno de P en B reprogramado de 09:00 a 11:00
- **CUANDO** se solicita un nuevo turno de P en B a las 09:00
- **ENTONCES** el sistema crea el nuevo turno

### Requirement: Excluir el propio turno de la comparación
La validación de disponibilidad de una reprogramación SHALL ignorar el propio turno, de modo que el nuevo intervalo pueda solaparse con el intervalo anterior del mismo turno.

#### Scenario: Correr un turno dentro de su propio intervalo
- **DADO** un turno de 09:00 a 09:30 de P en B sin otros turnos
- **CUANDO** se reprograma con inicio a las 09:15
- **ENTONCES** el turno queda de 09:15 a 09:45 sin informar conflicto

#### Scenario: Extender el fin de un turno
- **DADO** un turno de 09:00 a 09:30
- **CUANDO** se reprograma sólo con fin a las 10:00
- **ENTONCES** el turno queda de 09:00 a 10:00

### Requirement: Validar el destino contra turnos y bloqueos
El sistema SHALL rechazar una reprogramación cuyo intervalo de destino intersecte otro turno activo del profesional o del box de destino, o un bloqueo de cualquiera de ellos. Los intervalos que sólo se tocan en un borde SHALL aceptarse.

#### Scenario: Conflicto por profesional
- **DADO** un turno T de P en B y otro turno activo de P de 11:00 a 11:30 en otro box
- **CUANDO** se reprograma T a las 11:00
- **ENTONCES** se informa un conflicto de profesional

#### Scenario: Conflicto por box
- **DADO** un turno T de P en B y otro turno activo de otro profesional de 11:00 a 11:30 en B
- **CUANDO** se reprograma T a las 11:00
- **ENTONCES** se informa un conflicto de box

#### Scenario: Conflicto por bloqueo
- **DADO** un turno T de P y un bloqueo de P de 11:00 a 12:00
- **CUANDO** se reprograma T a las 11:15
- **ENTONCES** se informa un conflicto de bloqueo de profesional

#### Scenario: Conflicto en el nuevo recurso
- **DADO** un turno T en el box B y un bloqueo del box B2 que intersecta el horario de T
- **CUANDO** se reprograma T al box B2 sin cambiar el horario
- **ENTONCES** se informa un conflicto de bloqueo de box

#### Scenario: Destino contiguo
- **DADO** un turno T y otro turno de P que termina a las 11:00
- **CUANDO** se reprograma T con inicio a las 11:00
- **ENTONCES** la reprogramación se acepta

#### Scenario: Turno cancelado en el destino
- **DADO** un turno cancelado de P de 11:00 a 11:30
- **CUANDO** se reprograma otro turno de P a las 11:00
- **ENTONCES** la reprogramación se acepta

### Requirement: Reprogramar de forma atómica
Ante cualquier rechazo o fallo antes de confirmar la transacción, el turno SHALL conservar intervalo, recursos y estado, y no SHALL registrarse historial; el intervalo anterior sólo SHALL liberarse al confirmar un cambio válido.

#### Scenario: Rechazo sin cambios
- **DADO** un turno T de 09:00 a 09:30 y una reprogramación rechazada por conflicto
- **CUANDO** se consulta T
- **ENTONCES** T sigue de 09:00 a 09:30 con sus recursos y su historial sólo contiene `creado`

#### Scenario: Fallo al registrar el historial
- **DADO** una reprogramación válida cuyo registro de historial falla
- **CUANDO** se ejecuta
- **ENTONCES** el turno conserva su intervalo y recursos originales y no hay evento `reprogramado`

### Requirement: Rechazar reprogramaciones inválidas
El sistema SHALL rechazar reprogramar un turno `cancelado` (transición inválida), un turno, profesional o box inexistente (recurso inexistente), un intervalo con `fin <= inicio` (intervalo inválido) y una solicitud que no cambia ningún valor (reprogramación sin cambios), sin persistir cambios.

#### Scenario: Turno cancelado
- **DADO** un turno cancelado
- **CUANDO** se intenta reprogramarlo
- **ENTONCES** se informa una transición inválida

#### Scenario: Box de destino inexistente
- **DADO** un turno existente
- **CUANDO** se reprograma a un box que no existe
- **ENTONCES** se informa que el recurso no existe

#### Scenario: Intervalo inválido
- **DADO** un turno de 09:00 a 09:30
- **CUANDO** se reprograma con fin a las 09:00
- **ENTONCES** se informa un intervalo inválido

#### Scenario: Sin cambios
- **DADO** un turno de 09:00 a 09:30 de P en B
- **CUANDO** se reprograma con los mismos valores
- **ENTONCES** se informa una reprogramación sin cambios y no se registra historial

### Requirement: Serializar reprogramaciones concurrentes
Una reprogramación SHALL bloquear el turno y luego los recursos de destino en el orden profesional → box antes de leer conflictos. Ante una reprogramación y un alta concurrentes sobre el mismo intervalo de destino, SHALL confirmarse sólo una.

#### Scenario: Reprogramación confirma antes que un alta
- **DADO** un turno T y una solicitud concurrente de alta en el horario de destino de T
- **CUANDO** la reprogramación obtiene primero los recursos y confirma
- **ENTONCES** el alta informa conflicto y sólo existe la reprogramación

#### Scenario: Alta confirma antes que una reprogramación
- **DADO** un turno T y una solicitud concurrente de alta en el horario de destino de T
- **CUANDO** el alta obtiene primero los recursos y confirma
- **ENTONCES** la reprogramación informa conflicto y T conserva su intervalo

### Requirement: Exponer la reprogramación por HTTP
El sistema SHALL exponer `PATCH /api/v1/turnos/{turno_id}` con `inicio`, `fin`, `profesional_id` y `box_id` opcionales (al menos uno). SHALL responder `200` con el turno, `404` con `recurso_inexistente`, `409` por conflicto o `transicion_invalida`, y `422` por intervalo inválido, sin cambios, cuerpo vacío, campos desconocidos o fechas sin zona horaria.

#### Scenario: Reprogramación por API
- **DADO** un turno creado por API a las 09:00 (-03:00)
- **CUANDO** se envía `PATCH /api/v1/turnos/{id}` con inicio a las 11:00 (-03:00)
- **ENTONCES** la respuesta es `200` con el turno de 14:00 a 14:30 UTC

#### Scenario: Conflicto por API
- **DADO** dos turnos del mismo profesional
- **CUANDO** se reprograma uno sobre el otro
- **ENTONCES** la respuesta es `409` con código `conflicto_profesional`

#### Scenario: Cuerpo vacío por API
- **DADO** un turno existente
- **CUANDO** se envía `PATCH` con un cuerpo `{}`
- **ENTONCES** la respuesta es `422`
