# bloqueo-de-disponibilidad Specification

## Purpose

Permite reservar intervalos no disponibles de un profesional o un box y rechazar operaciones incompatibles sin alterar los turnos existentes.

## Requirements

### Requirement: Registrar un bloqueo de un recurso
El sistema SHALL registrar cada bloqueo con identificador, inicio, fin, motivo opcional y exactamente un recurso: `profesional_id` o `box_id`. Ambos instantes SHALL tener zona horaria, el recurso SHALL existir y `fin` SHALL ser posterior a `inicio`.

#### Scenario: Bloqueo válido de profesional
- **DADO** un profesional ficticio existente sin reservas incompatibles
- **CUANDO** se registra un bloqueo de 09:00 a 10:00 para ese profesional con motivo opcional
- **ENTONCES** se conserva un bloqueo de ese profesional con el intervalo y motivo solicitados

#### Scenario: Bloqueo válido de box
- **DADO** un box ficticio existente sin reservas incompatibles
- **CUANDO** se registra un bloqueo de 09:00 a 10:00 para ese box sin motivo
- **ENTONCES** se conserva un bloqueo de ese box sin asociarlo a ningún profesional

#### Scenario: Bloqueos superpuestos del mismo recurso
- **DADO** un bloqueo de profesional P de 09:00 a 10:00 sin turnos activos en ese intervalo
- **CUANDO** se registra otro bloqueo de P de 09:30 a 10:30
- **ENTONCES** se conservan ambos bloqueos; la superposición entre bloqueos no rechaza el registro

#### Scenario: Selección inválida de recurso
- **DADO** una solicitud de bloqueo
- **CUANDO** se indican simultáneamente `profesional_id` y `box_id`, o no se indica ninguno
- **ENTONCES** la solicitud se rechaza y no se crea ningún bloqueo

#### Scenario: Recurso inexistente
- **DADO** que no existe el profesional o box indicado
- **CUANDO** se intenta registrar su bloqueo
- **ENTONCES** se informa que el recurso no existe y no se crea ningún bloqueo

#### Scenario: Intervalo inválido
- **DADO** un recurso existente
- **CUANDO** se solicita un bloqueo con `fin` igual o anterior a `inicio`
- **ENTONCES** se informa un intervalo inválido y no se crea ningún bloqueo

#### Scenario: Fecha sin zona horaria
- **DADO** un recurso existente
- **CUANDO** se solicita un bloqueo con inicio o fin sin zona horaria
- **ENTONCES** la solicitud se rechaza sin crear bloqueo

### Requirement: Rechazar bloqueos incompatibles con turnos activos
El sistema SHALL rechazar un bloqueo cuyo intervalo comparta tiempo efectivo con un turno activo del mismo recurso y SHALL conservar ese turno sin cambios. Esta política conservadora aplica mientras la resolución clínica de turnos previamente creados siga abierta.

#### Scenario: Bloqueo de profesional cruza un turno
- **DADO** un turno activo de 09:00 a 09:30 del profesional P
- **CUANDO** se solicita bloquear P de 09:15 a 10:00
- **ENTONCES** se informa un conflicto con turno existente, no se crea bloqueo y el turno y su historial permanecen iguales

#### Scenario: Bloqueo de box cruza un turno de otro profesional
- **DADO** un turno activo de 09:00 a 09:30 en el box B
- **CUANDO** se solicita bloquear B de 09:15 a 10:00
- **ENTONCES** se informa un conflicto con turno existente y no se crea bloqueo

#### Scenario: Bloqueo contiguo a un turno
- **DADO** un turno activo de 09:00 a 09:30 del recurso indicado
- **CUANDO** se solicita bloquear el recurso desde las 09:30
- **ENTONCES** el bloqueo se registra porque los intervalos semiabiertos no comparten tiempo efectivo

#### Scenario: Bloqueo que termina justo al comenzar un turno
- **DADO** un turno activo de 09:00 a 09:30 del recurso indicado
- **CUANDO** se solicita bloquear el recurso hasta las 09:00
- **ENTONCES** el bloqueo se registra porque los intervalos semiabiertos no comparten tiempo efectivo

### Requirement: Mantener consistencia entre turnos y bloqueos concurrentes
Las operaciones soportadas de creación de turno y bloqueo SHALL serializar la comprobación de disponibilidad y la escritura sobre el recurso compartido. Ante solicitudes simultáneas incompatibles, SHALL confirmarse sólo una y la otra SHALL informar un conflicto sin cambios parciales.

#### Scenario: Turno confirma antes que bloqueo del profesional
- **DADO** un profesional P libre y solicitudes concurrentes de turno y bloqueo intersectantes
- **CUANDO** el turno obtiene primero el recurso y confirma
- **ENTONCES** el bloqueo informa conflicto con turno existente y sólo el turno queda confirmado

#### Scenario: Bloqueo confirma antes que turno del profesional
- **DADO** un profesional P libre y solicitudes concurrentes de turno y bloqueo intersectantes
- **CUANDO** el bloqueo obtiene primero el recurso y confirma
- **ENTONCES** el turno informa conflicto de bloqueo y sólo el bloqueo queda confirmado

#### Scenario: Turno confirma antes que bloqueo del box
- **DADO** un box B libre y solicitudes concurrentes de turno y bloqueo intersectantes
- **CUANDO** el turno obtiene primero el recurso y confirma
- **ENTONCES** el bloqueo informa conflicto con turno existente y sólo el turno queda confirmado

#### Scenario: Bloqueo confirma antes que turno del box
- **DADO** un box B libre y solicitudes concurrentes de turno y bloqueo intersectantes
- **CUANDO** el bloqueo obtiene primero el recurso y confirma
- **ENTONCES** el turno informa conflicto de bloqueo y sólo el bloqueo queda confirmado

### Requirement: Exponer el registro de bloqueos por HTTP
El sistema SHALL exponer `POST /api/v1/bloqueos`: `201` con el bloqueo creado; `404` si el recurso no existe; `409` por turno activo incompatible; `422` por recurso mal seleccionado, intervalo inválido o fechas mal formadas o sin zona horaria.

#### Scenario: Registro de bloqueo por API
- **DADO** un profesional ficticio existente y disponible
- **CUANDO** se envía un bloqueo válido a `POST /api/v1/bloqueos`
- **ENTONCES** la respuesta es `201` con identificador, recurso, intervalo y motivo

#### Scenario: Conflicto con turno por API
- **DADO** un turno activo del recurso en el intervalo solicitado
- **CUANDO** se envía `POST /api/v1/bloqueos`
- **ENTONCES** la respuesta es `409` con código `conflicto_turno_existente` y no se crea bloqueo

#### Scenario: Fechas o recurso inválidos por API
- **DADO** una agenda de prueba
- **CUANDO** se envía una fecha mal formada, una fecha sin zona o ambos recursos a `POST /api/v1/bloqueos`
- **ENTONCES** la respuesta es `422` y no se crea bloqueo
