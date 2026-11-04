# Spec Delta

## Purpose

Permitir que el equipo inicie y verifique el MVP odontológico completo en un entorno local reproducible, con datos exclusivamente ficticios y sin publicar credenciales.

## ADDED Requirements

### Requirement: Preparar credenciales locales sin versionarlas
El entorno SHALL proporcionar una preparación local que genere una clave de firma JWT válida y una contraseña demo aleatoria en un archivo ignorado por Git. SHALL conservar esos valores al repetir la preparación, no SHALL imprimirlos en logs y SHALL impedir iniciar la API con un secreto ausente o inválido.

#### Scenario: Primera preparación local
- **DADO** un checkout sin configuración local
- **CUANDO** se ejecuta la preparación documentada
- **ENTONCES** quedan disponibles un `JWT_SECRET` de al menos 32 caracteres y una contraseña demo no vacía fuera de los archivos versionados

#### Scenario: Preparación repetida
- **DADO** que ya existe una configuración local válida
- **CUANDO** se repite la preparación
- **ENTONCES** se conservan las credenciales y ningún secreto aparece en los logs del comando

#### Scenario: Falta el secreto al arrancar
- **DADO** un entorno sin `JWT_SECRET` válido
- **CUANDO** se intenta iniciar el servicio de API
- **ENTONCES** el arranque falla con un error de configuración sin mostrar el secreto ni aceptar una firma débil

### Requirement: Arrancar el MVP integrado con datos demo
Tras la preparación local, `docker compose up` SHALL iniciar PostgreSQL, Redis, API, frontend web y un worker continuo de recordatorios. La API SHALL estar disponible al terminar el arranque, la web SHALL poder acceder a ella desde su mismo origen y el entorno SHALL disponer de recursos ficticios y un usuario de recepción demo sin pasos manuales de alta.

#### Scenario: Primer arranque
- **DADO** una base local nueva y configuración local válida
- **CUANDO** se levanta el stack documentado
- **ENTONCES** los servicios requeridos quedan operativos, `/health` responde correctamente, el frontend carga y el usuario demo puede autenticarse

#### Scenario: Arranque repetido
- **DADO** un stack que ya fue inicializado
- **CUANDO** se vuelve a levantar sin borrar sus datos
- **ENTONCES** los recursos y el usuario demo no se duplican y sus credenciales siguen vigentes

#### Scenario: Datos de demostración exclusivamente ficticios
- **DADO** una instalación local recién inicializada
- **CUANDO** se consultan los pacientes y recursos preparados
- **ENTONCES** los registros son los ejemplos ficticios identificados como Demo, sin información clínica real

### Requirement: Procesar recordatorios simulados en el stack
El worker del entorno SHALL consumir continuamente las tareas pendientes de Redis y registrar los recordatorios simulados de turnos activos mediante la funcionalidad vigente. No SHALL enviar mensajes externos ni registrar un recordatorio de un turno cancelado antes del procesamiento.

#### Scenario: Recordatorio de turno activo
- **DADO** un turno activo creado mediante la API integrada
- **CUANDO** el worker procesa su tarea
- **ENTONCES** la consulta autenticada de recordatorios del turno devuelve el envío simulado registrado

#### Scenario: Turno cancelado antes de procesar
- **DADO** un turno cancelado antes de que se procese su tarea
- **CUANDO** el worker consume esa tarea
- **ENTONCES** no aparece un envío simulado para ese turno

### Requirement: Verificar el recorrido completo del MVP por HTTP
El proyecto SHALL ofrecer una prueba repetible por HTTP de los servicios integrados que compruebe login, alta de paciente y turno, consulta de agenda, bloqueo, rechazo de un turno en conflicto, reprogramación, recordatorio simulado, cancelación y reutilización de un horario libre. SHALL usar sólo datos ficticios y no alterar la base local habitual del desarrollador.

#### Scenario: Flujo integrado exitoso y conflicto controlado
- **DADO** el stack de prueba aislado con recursos demo y usuario de recepción
- **CUANDO** la prueba ejecuta el recorrido completo
- **ENTONCES** cada operación obtiene su respuesta esperada, el conflicto responde `409`, el recordatorio figura antes de cancelar y el horario liberado acepta una nueva reserva

#### Scenario: Repetición de la prueba
- **DADO** una ejecución anterior del recorrido
- **CUANDO** se ejecuta nuevamente la prueba en un entorno aislado nuevo
- **ENTONCES** produce el mismo resultado sin depender de identificadores o turnos de la ejecución previa
