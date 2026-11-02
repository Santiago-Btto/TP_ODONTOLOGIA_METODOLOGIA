# registro-de-pacientes Specification

## Purpose
Permite dar de alta y buscar pacientes con los datos mínimos operativos (`id`, `nombre_mostrado` y `contacto` opcional) exigidos por el MVP, impidiendo el ingreso de campos clínicos o no permitidos y garantizando el uso exclusivo de datos ficticios en pruebas y semillas.

## Requirements

### Requirement: Dar de alta un paciente con datos mínimos
El sistema SHALL exponer `POST /api/v1/pacientes` para registrar un paciente con `nombre_mostrado` obligatorio, `contacto` opcional e `id` opcional (autogenerado si se omite). El sistema SHALL recortar espacios extremos, normalizar un `contacto` en blanco a `null`, persistir el paciente y responder `201` con `id`, `nombre_mostrado` y `contacto`.

#### Scenario: Alta válida con nombre mostrado y contacto opcional
- **DADO** un usuario de recepción autenticado
- **CUANDO** envía `POST /api/v1/pacientes` con `nombre_mostrado` `"Paciente Demo Ficticio 010"` y `contacto` `"+54 9 11 0000-0010"`
- **ENTONCES** la respuesta es `201` con `id` generado, `nombre_mostrado` `"Paciente Demo Ficticio 010"` y `contacto` `"+54 9 11 0000-0010"`, y el paciente puede usarse para crear un turno

#### Scenario: Alta válida con identificador explícito y sin contacto
- **DADO** un usuario de recepción autenticado
- **CUANDO** envía `POST /api/v1/pacientes` con `id` `"paciente-demo-011"` y `nombre_mostrado` `"Paciente Demo Ficticia 011"` sin `contacto`
- **ENTONCES** la respuesta es `201` con `id` `"paciente-demo-011"`, `nombre_mostrado` `"Paciente Demo Ficticia 011"` y `contacto` `null`

### Requirement: Rechazar el alta de un paciente duplicado
El sistema SHALL rechazar con `409` y código `paciente_duplicado` todo intento de registrar un paciente cuyo `id` ya exista o cuyo `contacto` no nulo coincida (ignorando mayúsculas/minúsculas y espacios extremos) con el de otro paciente registrado, sin modificar los datos existentes.

#### Scenario: Rechazo por identificador duplicado
- **DADO** un paciente ya registrado con `id` `"paciente-demo-001"`
- **CUANDO** se envía `POST /api/v1/pacientes` con el mismo `id` `"paciente-demo-001"`
- **ENTONCES** la respuesta es `409` con código `paciente_duplicado` y se conserva el registro original sin cambios

#### Scenario: Rechazo por contacto duplicado
- **DADO** un paciente ya registrado con `contacto` `"paciente.demo.001@example.invalid"`
- **CUANDO** se envía `POST /api/v1/pacientes` con otro `nombre_mostrado` y `contacto` `"PACIENTE.DEMO.001@example.invalid"`
- **ENTONCES** la respuesta es `409` con código `paciente_duplicado` y no se crea un segundo paciente

### Requirement: Buscar y listar pacientes registrados
El sistema SHALL exponer `GET /api/v1/pacientes` con un parámetro opcional `q`. Sin `q` (o con `q` en blanco), SHALL devolver todos los pacientes ordenados por `nombre_mostrado` e `id` ascendentes; con `q`, SHALL devolver aquellos cuyo `nombre_mostrado`, `id` o `contacto` contengan el texto buscado sin distinguir mayúsculas de minúsculas.

#### Scenario: Búsqueda por coincidencia parcial de nombre o contacto
- **DADO** que existen los pacientes `"Paciente Demo Ana"` (contacto `"+54 9 11 0000-0101"`) y `"Paciente Demo Bruno"` (contacto `"+54 9 11 0000-0202"`)
- **CUANDO** se consulta `GET /api/v1/pacientes?q=ana` o `GET /api/v1/pacientes?q=0101`
- **ENTONCES** la respuesta es `200` y contiene únicamente a `"Paciente Demo Ana"` con su `id`, `nombre_mostrado` y `contacto`

#### Scenario: Listado sin filtro y búsqueda sin coincidencias
- **DADO** que existen pacientes registrados en la base
- **CUANDO** se consulta `GET /api/v1/pacientes` sin `q`, o con un `q` que no coincide con ningún registro
- **ENTONCES** sin `q` devuelve la lista completa ordenada por `nombre_mostrado` e `id`, y con `q` sin coincidencias devuelve `200` con `[]`

### Requirement: Rechazar campos clínicos o no permitidos y datos inválidos
El sistema SHALL limitar la entrada de `POST /api/v1/pacientes` exclusivamente a `id`, `nombre_mostrado` y `contacto`. Cualquier campo adicional (como `dni`, `obra_social`, `historia_clinica`, `odontograma` o `diagnostico`) o un `nombre_mostrado` o `id` vacío o de solo espacios SHALL rechazarse con `422` sin persistir datos.

#### Scenario: Rechazo de campos clínicos o personales no permitidos
- **DADO** un usuario autenticado con permiso para registrar pacientes
- **CUANDO** envía `POST /api/v1/pacientes` incluyendo campos como `historia_clinica`, `odontograma`, `dni` u `obra_social`
- **ENTONCES** la respuesta es `422` y no se registra el paciente

#### Scenario: Rechazo de nombre mostrado vacío o en blanco
- **DADO** un usuario autenticado con permiso para registrar pacientes
- **CUANDO** envía `POST /api/v1/pacientes` con `nombre_mostrado` `""` o `"   "`
- **ENTONCES** la respuesta es `422` y no se registra el paciente

### Requirement: Autorizar operaciones de pacientes según el rol
El sistema SHALL exigir autenticación Bearer JWT en `POST /api/v1/pacientes` y `GET /api/v1/pacientes`, permitiendo ambas operaciones a los roles `recepcion` y `responsable` y rechazando con `403` y código `acceso_denegado` al rol `odontologo`.

#### Scenario: Recepción y responsable pueden registrar y buscar pacientes
- **DADO** un usuario con rol `recepcion` o `responsable` autenticado
- **CUANDO** registra un paciente ficticio y luego consulta `GET /api/v1/pacientes`
- **ENTONCES** las respuestas son `201` y `200` respectivamente

#### Scenario: Odontólogo no puede dar de alta ni listar el padrón de pacientes
- **DADO** un usuario con rol `odontologo` autenticado
- **CUANDO** invoca `POST /api/v1/pacientes` o `GET /api/v1/pacientes`
- **ENTONCES** la respuesta es `403` con código `acceso_denegado`
