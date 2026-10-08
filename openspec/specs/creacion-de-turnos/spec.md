# creacion-de-turnos Specification

## Purpose

Define una reserva de agenda confiable que protege simultáneamente la disponibilidad de un profesional y un box, tanto en el dominio como en la persistencia PostgreSQL, y la expone por API HTTP.

## Requirements

### Requirement: Crear una reserva válida
El sistema SHALL crear un turno cuando paciente ficticio, profesional, box y prestación existen, el intervalo es válido y ambos recursos están disponibles. El turno creado SHALL conservar su intervalo y recursos, y generar en la misma transacción un evento de historial de tipo `creado`.

#### Scenario: Alta exitosa
- **DADO** un profesional y un box sin turnos activos y una prestación de 30 minutos
- **CUANDO** se solicita un turno que empieza a las 09:00 con esa prestación
- **ENTONCES** el sistema crea el turno de 09:00 a 09:30 y registra exactamente un evento `creado` asociado

### Requirement: Proteger la disponibilidad del profesional
El sistema SHALL rechazar la creación de un turno cuyo intervalo comparta tiempo efectivo con un turno activo del mismo profesional, aun si los boxes son distintos.

#### Scenario: Conflicto por profesional
- **DADO** un turno activo del profesional de 09:00 a 09:30 en el box 2
- **CUANDO** se solicita para ese profesional un turno de 09:00 a 09:30 en el box 1
- **ENTONCES** el sistema informa un conflicto de profesional y no crea turno ni historial nuevos

### Requirement: Proteger la disponibilidad del box
El sistema SHALL rechazar la creación de un turno cuyo intervalo comparta tiempo efectivo con un turno activo del mismo box, aun si los profesionales son distintos.

#### Scenario: Conflicto por box
- **DADO** un turno activo del box de 09:00 a 09:30 con otro profesional
- **CUANDO** se solicita un turno de 09:00 a 09:30 en ese box
- **ENTONCES** el sistema informa un conflicto de box y no crea turno ni historial nuevos

### Requirement: Admitir límites contiguos
El sistema SHALL tratar los intervalos de los turnos como semiabiertos `[inicio, fin)`. Un turno que inicia exactamente cuando termina otro turno activo del mismo recurso SHALL poder crearse.

#### Scenario: Reserva contigua
- **DADO** un turno activo del mismo profesional y del mismo box de 08:30 a 09:00
- **CUANDO** se solicita un turno que empieza exactamente a las 09:00
- **ENTONCES** el sistema crea el nuevo turno sin informar conflicto

### Requirement: Rechazar datos temporales inválidos
El sistema SHALL rechazar la creación cuando el fin no sea estrictamente posterior al inicio o cuando la duración de la prestación no sea positiva. Un rechazo SHALL conservar sin cambios las reservas y el historial existentes.

#### Scenario: Intervalo sin duración positiva
- **DADO** una agenda sin turnos
- **CUANDO** se solicita un turno cuyo fin es igual o anterior a su inicio
- **ENTONCES** el sistema informa un error de intervalo inválido y no persiste cambios

#### Scenario: Prestación con duración inválida
- **DADO** una prestación cuya duración es cero o negativa
- **CUANDO** se solicita calcular un turno con esa prestación
- **ENTONCES** el sistema informa un error de duración inválida y no persiste cambios

### Requirement: Rechazar recursos inexistentes
El sistema SHALL rechazar la creación cuando el paciente, el profesional, el box o la prestación indicados no existen, sin persistir cambios.

#### Scenario: Profesional inexistente
- **DADO** que no existe un profesional con el identificador indicado
- **CUANDO** se solicita un turno para ese identificador
- **ENTONCES** el sistema informa que el recurso no existe y no crea turno ni historial

### Requirement: Impedir solapamientos en la persistencia
La base de datos SHALL rechazar por restricción la escritura de un turno activo que se solape con otro turno activo del mismo profesional o del mismo box, aun si la escritura no pasó por el caso de uso. Los turnos contiguos SHALL ser aceptados también por la base.

#### Scenario: Escritura solapada que elude la aplicación
- **DADO** un turno activo persistido de 09:00 a 09:30 para un profesional
- **CUANDO** se inserta directamente en la base otro turno de 09:15 a 09:45 para el mismo profesional
- **ENTONCES** PostgreSQL rechaza la escritura y la tabla conserva un único turno

#### Scenario: Escritura contigua directa
- **DADO** un turno activo persistido de 09:00 a 09:30 para un profesional y un box
- **CUANDO** se inserta directamente otro turno de 09:30 a 10:00 con el mismo profesional y box
- **ENTONCES** PostgreSQL acepta la escritura

### Requirement: Exponer el alta por API HTTP
El sistema SHALL exponer `POST /api/v1/turnos`, que delega en el caso de uso y traduce su resultado a HTTP: `201` con el turno creado, `404` si un recurso no existe, `409` ante conflicto de profesional o box y `422` ante intervalo o duración inválidos o datos mal formados.

#### Scenario: Alta por API
- **DADO** recursos ficticios existentes y sin turnos
- **CUANDO** se envía `POST /api/v1/turnos` con un inicio a las 09:00
- **ENTONCES** la respuesta es `201` con el turno de 09:00 a 09:30 en estado `programado`

#### Scenario: Conflicto por API
- **DADO** un turno activo del profesional de 09:00 a 09:30
- **CUANDO** se envía `POST /api/v1/turnos` para el mismo profesional a las 09:15
- **ENTONCES** la respuesta es `409` con el código `conflicto_profesional`

#### Scenario: Intervalo inválido por API
- **DADO** recursos ficticios existentes
- **CUANDO** se envía `POST /api/v1/turnos` con un fin igual al inicio
- **ENTONCES** la respuesta es `422` con el código `intervalo_invalido`

#### Scenario: Recurso inexistente por API
- **DADO** que no existe el box indicado
- **CUANDO** se envía `POST /api/v1/turnos` con ese box
- **ENTONCES** la respuesta es `404` con el código `recurso_inexistente`
