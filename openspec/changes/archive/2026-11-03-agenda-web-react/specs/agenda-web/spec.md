# Spec Delta

## Purpose

Permite al personal autorizado operar la agenda odontológica desde un navegador usando la API existente, con vistas por período y mensajes fieles a las respuestas del servidor.

## ADDED Requirements

### Requirement: Iniciar y cerrar sesión en la agenda web
La interfaz SHALL permitir iniciar sesión con usuario y contraseña mediante la API, identificar el rol autenticado y cerrar la sesión. SHALL dejar de mostrar datos protegidos al cerrar sesión o recibir `401`, y SHALL mostrar un error comprensible ante credenciales inválidas.

#### Scenario: Inicio de sesión correcto
- **DADO** un usuario activo de recepción con credenciales válidas
- **CUANDO** inicia sesión en la web
- **ENTONCES** la web muestra la agenda y el usuario/rol obtenidos del servidor

#### Scenario: Credenciales incorrectas
- **DADO** un usuario que introduce una contraseña incorrecta
- **CUANDO** intenta iniciar sesión
- **ENTONCES** permanece en el formulario y ve un mensaje de error sin datos protegidos

#### Scenario: Sesión vencida o cierre voluntario
- **DADO** una sesión abierta
- **CUANDO** el usuario cierra sesión o la API responde `401` a una operación protegida
- **ENTONCES** desaparecen los datos de la agenda y se solicita iniciar sesión nuevamente

### Requirement: Consultar la agenda diaria y semanal
La interfaz SHALL ofrecer vistas diaria y semanal del período elegido, consultar `GET /api/v1/agenda` con fechas que incluyan zona horaria y mostrar horario, profesional, box y estado de cada turno retornado. SHALL indicar de forma explícita cuando no existan turnos o la consulta falle.

#### Scenario: Vista diaria con turnos
- **DADO** turnos del día seleccionado
- **CUANDO** el usuario abre la vista diaria
- **ENTONCES** aparecen en orden cronológico con hora, profesional, box y estado de la respuesta de la API

#### Scenario: Vista semanal sin turnos
- **DADO** una semana sin turnos para los filtros elegidos
- **CUANDO** el usuario abre la vista semanal
- **ENTONCES** ve los siete días de la semana y un estado vacío claro

#### Scenario: Error al consultar
- **DADO** que la API no puede responder la consulta
- **CUANDO** el usuario actualiza la agenda
- **ENTONCES** ve un error de carga y puede reintentar sin confundirlo con una agenda vacía

### Requirement: Filtrar la agenda según los permisos
La interfaz SHALL permitir a recepción y responsable filtrar por profesional, box o ambos. Para un odontólogo SHALL fijar el filtro al profesional vinculado a su identidad y SHALL impedir desde la interfaz solicitar la agenda de otro profesional; la API conserva la autorización definitiva.

#### Scenario: Filtro combinado de recepción
- **DADO** un usuario de recepción autenticado
- **CUANDO** ingresa un profesional y un box
- **ENTONCES** la consulta envía ambos filtros y presenta sólo los turnos retornados

#### Scenario: Agenda de odontólogo
- **DADO** un odontólogo autenticado y vinculado al profesional P
- **CUANDO** abre la agenda o cambia el filtro de box
- **ENTONCES** la consulta incluye `profesional_id=P` y la interfaz no permite cambiarlo

### Requirement: Crear un turno desde la web
La interfaz SHALL ofrecer a recepción y responsable un formulario con paciente, prestación, profesional, box e inicio, y fin opcional. SHALL enviar los valores a `POST /api/v1/turnos`, mostrar el turno creado y actualizar la agenda consultando nuevamente la API. No SHALL inferir disponibilidad localmente.

#### Scenario: Alta válida
- **DADO** recursos ficticios existentes y un intervalo disponible
- **CUANDO** recepción envía el formulario
- **ENTONCES** ve la confirmación con el turno devuelto y la agenda se actualiza desde la API

#### Scenario: Conflicto o validación rechazada
- **DADO** una solicitud que la API rechaza con `409` o `422`
- **CUANDO** se envía el formulario
- **ENTONCES** la interfaz conserva los datos ingresados y muestra la causa informada por el servidor, sin añadir el turno a la agenda

#### Scenario: Odontólogo sin permiso de alta
- **DADO** un usuario odontólogo autenticado
- **CUANDO** ve la agenda
- **ENTONCES** no dispone del formulario de creación de turnos

### Requirement: Registrar o buscar pacientes mínimos desde la web
La interfaz SHALL permitir a recepción y responsable buscar pacientes y registrar únicamente `nombre_mostrado` y `contacto` opcional mediante la API. SHALL permitir elegir el paciente devuelto para crear un turno, y SHALL mostrar los rechazos del servidor sin exponer campos clínicos.

#### Scenario: Paciente nuevo para turno
- **DADO** recepción autenticada
- **CUANDO** registra un paciente ficticio con nombre y selecciona el resultado
- **ENTONCES** el `id` devuelto queda disponible para el formulario de alta de turno

#### Scenario: Paciente duplicado
- **DADO** un contacto ya registrado
- **CUANDO** intenta registrar otro paciente con ese contacto
- **ENTONCES** ve el error `409` recibido de la API y no se selecciona un nuevo paciente

#### Scenario: Odontólogo sin acceso al padrón
- **DADO** un odontólogo autenticado
- **CUANDO** ve la agenda
- **ENTONCES** no dispone de búsqueda ni alta de pacientes
