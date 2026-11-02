# autenticacion-y-autorizacion Specification

## Purpose

Protege la API interna de agenda con tokens JWT, aplica la matriz de permisos por rol y registra qué usuario realizó cada cambio de turno.

## Requirements

### Requirement: Emitir un token de acceso
El sistema SHALL exponer `POST /api/v1/auth/token` (OAuth2 password flow) que, ante nombre de usuario y contraseña válidos de un usuario activo, devuelve `200` con un JWT firmado con `JWT_SECRET`, `token_type` `bearer` y su vida en segundos. Ante credenciales inválidas, usuario inexistente o inactivo SHALL responder `401` con código `credenciales_invalidas`, sin revelar cuál de los casos ocurrió.

#### Scenario: Login válido
- **DADO** un usuario activo de recepción con contraseña conocida
- **CUANDO** envía sus credenciales a `POST /api/v1/auth/token`
- **ENTONCES** la respuesta es `200` con `access_token`, `token_type` `bearer` y `expires_in`

#### Scenario: Contraseña incorrecta
- **DADO** un usuario activo
- **CUANDO** envía una contraseña incorrecta
- **ENTONCES** la respuesta es `401` con código `credenciales_invalidas`

#### Scenario: Usuario inexistente o inactivo
- **DADO** un nombre de usuario que no existe, o un usuario inactivo con su contraseña correcta
- **CUANDO** solicita un token
- **ENTONCES** la respuesta es `401` con el mismo código `credenciales_invalidas`

### Requirement: Proteger todas las rutas de agenda
Toda ruta bajo `/api/v1`, salvo la emisión de token, SHALL exigir `Authorization: Bearer <token>`. SHALL responder `401` con `WWW-Authenticate: Bearer` y código `no_autenticado` si falta el token, `token_invalido` si la firma, el algoritmo o los reclamos no son válidos o el usuario ya no existe o está inactivo, y `token_expirado` si venció.

#### Scenario: Token válido
- **DADO** un token vigente de un usuario de recepción
- **CUANDO** consulta la agenda
- **ENTONCES** la respuesta es `200`

#### Scenario: Sin token
- **DADO** cualquier ruta `/api/v1` distinta de la emisión de token
- **CUANDO** se la invoca sin `Authorization`
- **ENTONCES** la respuesta es `401` con código `no_autenticado` y no se modifica ningún dato

#### Scenario: Token expirado
- **DADO** un token cuyo `exp` ya pasó
- **CUANDO** se lo usa en una ruta protegida
- **ENTONCES** la respuesta es `401` con código `token_expirado`

#### Scenario: Firma inválida
- **DADO** un token firmado con otro secreto o con algoritmo `none`
- **CUANDO** se lo usa en una ruta protegida
- **ENTONCES** la respuesta es `401` con código `token_invalido`

#### Scenario: Usuario desactivado después de emitir el token
- **DADO** un token vigente de un usuario que luego se desactiva
- **CUANDO** se lo usa en una ruta protegida
- **ENTONCES** la respuesta es `401` con código `token_invalido`

### Requirement: Autorizar por rol
El sistema SHALL aplicar la matriz propuesta: recepción y responsable de clínica pueden crear, reprogramar, confirmar y cancelar turnos, crear bloqueos y consultar la agenda; odontólogo/a sólo puede consultar la agenda filtrada por el profesional vinculado a su usuario. Una operación no permitida SHALL responder `403` con código `acceso_denegado` sin modificar datos.

#### Scenario: Odontólogo intenta crear un turno
- **DADO** un usuario odontólogo/a autenticado
- **CUANDO** envía `POST /api/v1/turnos`
- **ENTONCES** la respuesta es `403` con código `acceso_denegado` y no se crea turno ni historial

#### Scenario: Odontólogo consulta su propia agenda
- **DADO** un odontólogo/a vinculado al profesional P
- **CUANDO** consulta la agenda con `profesional_id=P`
- **ENTONCES** la respuesta es `200`

#### Scenario: Odontólogo consulta otra agenda
- **DADO** un odontólogo/a vinculado al profesional P
- **CUANDO** consulta la agenda sin filtro de profesional o con otro profesional
- **ENTONCES** la respuesta es `403` con código `acceso_denegado`

#### Scenario: Recepción opera turnos y bloqueos
- **DADO** un usuario de recepción autenticado
- **CUANDO** crea, confirma, reprograma y cancela un turno y registra un bloqueo
- **ENTONCES** todas las operaciones se aceptan

### Requirement: Registrar el actor de cada cambio de turno
Los eventos de historial `creado`, `confirmado`, `cancelado` y `reprogramado` generados por la API SHALL registrar el identificador del usuario autenticado que realizó la operación.

#### Scenario: Actor en el historial
- **DADO** un usuario de recepción autenticado
- **CUANDO** crea un turno y luego lo cancela
- **ENTONCES** ambos eventos del historial registran el identificador de ese usuario

### Requirement: Gestionar secretos y contraseñas de forma segura
El sistema SHALL leer `JWT_SECRET` del entorno y negarse a iniciar si falta o tiene menos de 32 caracteres. Las contraseñas SHALL almacenarse sólo como hash Argon2id y ninguna respuesta SHALL incluir el hash. El repositorio no SHALL contener secretos ni contraseñas.

#### Scenario: Secreto ausente
- **DADO** un entorno sin `JWT_SECRET`
- **CUANDO** se intenta construir la configuración de seguridad
- **ENTONCES** se informa un error de configuración y la API no inicia

#### Scenario: Contraseña almacenada como hash
- **DADO** un usuario creado con el comando de alta
- **CUANDO** se lee su fila en la base
- **ENTONCES** el campo almacenado es un hash Argon2id distinto de la contraseña

#### Scenario: Identidad del usuario autenticado
- **DADO** un token vigente
- **CUANDO** se consulta `GET /api/v1/auth/yo`
- **ENTONCES** la respuesta incluye id, nombre de usuario, rol y profesional vinculado, sin el hash
