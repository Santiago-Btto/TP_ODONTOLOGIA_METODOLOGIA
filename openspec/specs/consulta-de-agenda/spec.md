# consulta-de-agenda Specification

## Purpose

Permite consultar los turnos de una agenda odontológica en un intervalo temporal, con filtros por recursos y un contrato HTTP verificable para vistas diarias o semanales.

## Requirements

### Requirement: Consultar un rango temporal válido
El sistema SHALL aceptar un rango obligatorio `[inicio, fin)` con ambos instantes acompañados de zona horaria y `fin > inicio`. SHALL devolver los turnos registrados cuyo intervalo intersecte el rango.

#### Scenario: Turnos contenidos en una agenda diaria
- **DADO** turnos programados de 09:00 a 09:30 y de 11:00 a 11:30, con fechas y zona horaria explícitas
- **CUANDO** se consulta de 08:00 a 12:00 del mismo día
- **ENTONCES** ambos turnos aparecen en la respuesta

#### Scenario: Turno que empieza antes del rango
- **DADO** un turno de 08:30 a 09:15
- **CUANDO** se consulta de 09:00 a 10:00
- **ENTONCES** ese turno aparece porque comparte tiempo efectivo con el rango

#### Scenario: Turno que termina después del rango
- **DADO** un turno de 09:45 a 10:15
- **CUANDO** se consulta de 09:00 a 10:00
- **ENTONCES** ese turno aparece porque comparte tiempo efectivo con el rango

#### Scenario: Turno que cubre el rango completo
- **DADO** un turno de 08:30 a 10:30
- **CUANDO** se consulta de 09:00 a 10:00
- **ENTONCES** ese turno aparece exactamente una vez

### Requirement: Excluir los bordes contiguos
El sistema SHALL considerar intersección únicamente cuando `turno.inicio < fin` y `turno.fin > inicio`, conforme a RN-DI-01; un turno que sólo toca un borde del rango SHALL quedar fuera.

#### Scenario: Turno que termina justo al comenzar el rango
- **DADO** un turno de 08:30 a 09:00
- **CUANDO** se consulta de 09:00 a 10:00
- **ENTONCES** el turno no aparece

#### Scenario: Turno que empieza justo al terminar el rango
- **DADO** un turno de 10:00 a 10:30
- **CUANDO** se consulta de 09:00 a 10:00
- **ENTONCES** el turno no aparece

### Requirement: Filtrar por recursos de agenda
El sistema SHALL permitir filtros opcionales de identificadores de texto `profesional_id` y `box_id`. Si se proporcionan ambos, SHALL devolver sólo turnos que coincidan con ambos filtros.

#### Scenario: Agenda semanal de un profesional
- **DADO** turnos de dos profesionales durante una semana
- **CUANDO** se consulta el rango semanal con `profesional_id` del primero
- **ENTONCES** se devuelven sólo sus turnos intersectantes

#### Scenario: Agenda semanal de un box
- **DADO** turnos de dos boxes durante una semana
- **CUANDO** se consulta el rango semanal con `box_id` del primero
- **ENTONCES** se devuelven sólo sus turnos intersectantes

#### Scenario: Filtros combinados
- **DADO** turnos del profesional P en los boxes A y B y turnos de otros profesionales en A
- **CUANDO** se consulta con `profesional_id=P` y `box_id=A`
- **ENTONCES** sólo se devuelven los turnos de P en A que intersectan el rango

#### Scenario: Identificador sin turnos coincidentes
- **DADO** una agenda con turnos de otros profesionales y boxes
- **CUANDO** se consulta con un identificador de texto que no coincide con ningún turno
- **ENTONCES** la respuesta válida contiene una lista vacía

### Requirement: Ordenar y describir los resultados
El sistema SHALL devolver los turnos por inicio cronológico ascendente, identificando en cada elemento el profesional y el box. Si no hay coincidencias, SHALL devolver una lista vacía.

#### Scenario: Resultado ordenado
- **DADO** turnos insertados en orden distinto al cronológico
- **CUANDO** se consulta un rango que los incluye
- **ENTONCES** la respuesta contiene primero el turno con inicio anterior y cada elemento contiene `profesional_id` y `box_id`

#### Scenario: Rango sin coincidencias
- **DADO** turnos fuera del rango o que no coinciden con los filtros
- **CUANDO** se consulta ese rango
- **ENTONCES** se devuelve una lista vacía

### Requirement: Exponer la consulta por HTTP
El sistema SHALL exponer `GET /api/v1/agenda` con `inicio` y `fin` obligatorios y filtros opcionales. SHALL responder `200` con una lista ante consulta válida y `422` si faltan fechas, carecen de zona horaria, están mal formadas o `fin <= inicio`.

#### Scenario: Consulta diaria exitosa por API
- **DADO** un turno programado con identificadores de profesional y box de texto
- **CUANDO** se solicita `GET /api/v1/agenda` con `inicio` y `fin` válidos
- **ENTONCES** la respuesta es `200` y contiene una lista con el turno y sus recursos

#### Scenario: Error de regla de consulta por rango inválido
- **DADO** una agenda existente
- **CUANDO** se solicita la agenda con `fin` igual o anterior a `inicio`
- **ENTONCES** se rechaza por la regla `fin > inicio`, la respuesta es `422` y no se modifica ningún turno

#### Scenario: Fecha sin zona horaria por API
- **DADO** una agenda existente
- **CUANDO** se solicita la agenda con una fecha sin zona horaria
- **ENTONCES** la respuesta es `422` y no se modifica ningún turno

#### Scenario: Fecha obligatoria ausente por API
- **DADO** una agenda existente
- **CUANDO** se solicita la agenda omitiendo `inicio` o `fin`
- **ENTONCES** la respuesta es `422`

#### Scenario: Fecha mal formada por API
- **DADO** una agenda existente
- **CUANDO** se solicita la agenda con una fecha que no puede interpretarse
- **ENTONCES** la respuesta es `422`

#### Scenario: Desplazamientos horarios equivalentes
- **DADO** un turno guardado a las 12:00 UTC
- **CUANDO** se consulta un rango que lo incluye expresado con desplazamiento `-03:00`
- **ENTONCES** la respuesta incluye ese turno una sola vez
