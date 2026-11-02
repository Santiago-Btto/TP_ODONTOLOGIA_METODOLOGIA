# Design

## Context

Véanse `proposal.md` y el delta spec. Hoy hay cinco rutas `/api/v1` (alta, confirmación, cancelación y reprogramación de turnos; agenda; bloqueos) sin autenticación. Los routers ya delegan en casos de uso con `Depends`, y `ErrorDeDominio` se traduce a `{codigo, detalle}` con un mapa de estados. La KB propone la matriz RBAC (`03_actores_y_roles.md`), exige secretos por entorno (`08_arquitectura_propuesta.md`) y prevé `actorId` en el historial (`04_modelo_de_datos.md`). La pregunta Alta “¿Quién puede crear, reprogramar, cancelar o confirmar?” sigue abierta: se implementa la matriz **propuesta**, centralizada para poder ajustarla sin tocar rutas. Governance: CRÍTICO; se aplicó la guía `security-best-practices` (FastAPI) en el diseño y la revisión.

## Goals / Non-Goals

**Goals:**

- Ninguna ruta `/api/v1` de agenda accesible sin token válido; prueba que barre todas las rutas registradas para que una ruta futura no quede abierta por omisión.
- Autorización expresada en el dominio, sin repartir `if rol == ...` por los routers.
- Ningún secreto en el repositorio; la app no arranca sin `JWT_SECRET` suficiente.
- Actor de cada cambio de turno persistido en el historial.

**Non-Goals:**

- Refresh tokens, revocación o lista negra de tokens; cierre de sesión del lado del servidor.
- Rate limiting y bloqueo por intentos fallidos del login, CORS y cabeceras para exposición pública (C-09).
- Alta, baja o cambio de contraseña de usuarios por API.
- Restringir datos de la agenda por rol más allá del alcance del odontólogo (pregunta Media abierta).

## Decisions

### 1. Autorización en el dominio

`app/domain/autorizacion.py` (Python puro) define `Rol`, `Permiso`, `Actor(id, rol, profesional_id)` y la matriz:

| Permiso | recepción | responsable | odontólogo/a |
|---|---|---|---|
| `crear_turno`, `reprogramar_turno`, `confirmar_turno`, `cancelar_turno` | ✓ | ✓ | — |
| `crear_bloqueo` | ✓ | ✓ | — |
| `consultar_agenda` | ✓ | ✓ | sólo la propia |

`verificar_permiso(actor, permiso)` lanza `AccesoDenegadoError` (`acceso_denegado`). `verificar_alcance_agenda(actor, profesional_id)` exige al odontólogo/a filtrar por su `profesional_id` vinculado; sin vínculo no puede consultar. La KB dice “Agenda propia: consultar; cambios pendientes de definición”, por eso no recibe permisos de escritura.

### 2. Usuarios y contraseñas

Tabla `usuarios`: `id` (texto ≤64), `nombre_usuario` único (≤64), `hash_contrasena`, `rol` con `CHECK` sobre los tres valores, `profesional_id` opcional con FK, `activo`. El hash usa `pwdlib` con Argon2id (`PasswordHash.recommended()`), la recomendación vigente de la documentación de FastAPI; se descarta `passlib` por estar sin mantenimiento. Nunca se devuelve el hash: las respuestas usan esquemas propios.

Los usuarios se crean con `python -m app.infrastructure.crear_usuario` (contraseña por `getpass` o `CONTRASENA_NUEVO_USUARIO`, mínimo 12 caracteres). No se agregan usuarios a las semillas: una contraseña de semilla versionada sería una credencial en el repositorio.

### 3. Tokens

`POST /api/v1/auth/token` recibe `username` y `password` como formulario (`OAuth2PasswordRequestForm`, por eso `python-multipart`) y devuelve `{access_token, token_type: "bearer", expires_in}`. El JWT (PyJWT) firma con HS256 y lleva sólo `sub` (id de usuario), `iat` y `exp`; el rol **no** viaja en el token, se lee de la base en cada request, así un cambio de rol o una desactivación aplican de inmediato. La decodificación fija `algorithms=["HS256"]` (rechaza `none` y confusiones de algoritmo) y exige `sub`, `iat` y `exp`.

`JWT_SECRET` se lee del entorno al iniciar la app; si falta o tiene menos de 32 caracteres, la app no arranca. `JWT_EXPIRA_MINUTOS` (por defecto 30) acota la vida del token, a falta de revocación. Para no revelar qué usuarios existen, el login verifica contra un hash ficticio cuando el usuario no existe y responde siempre `401 credenciales_invalidas`; un usuario inactivo recibe la misma respuesta.

### 4. Protección de rutas

`OAuth2PasswordBearer(auto_error=False)` extrae el token y la dependencia `actor_actual` lo resuelve con el caso de uso `ResolverActor`. Cada router `/api/v1` (turnos, agenda, bloqueos) declara `dependencies=[Depends(actor_actual)]`, y cada ruta pide además `requiere(Permiso.X)`, que devuelve el `Actor`. FastAPI cachea la dependencia por request, así que el token se valida una vez. Una prueba recorre `app.routes` y exige `401` sin token en toda ruta `/api/v1` salvo `/api/v1/auth/token`. `/health` y la documentación OpenAPI siguen públicas para desarrollo; su exposición se revisa en C-09.

Errores: `no_autenticado`, `token_invalido`, `token_expirado`, `credenciales_invalidas` → `401` con `WWW-Authenticate: Bearer`; `acceso_denegado` → `403`. Mismo cuerpo `{codigo, detalle}` que el resto de la API.

### 5. Actor en el historial

`HistorialDeCambio` suma `actor_id: str | None = None` (último campo, sin romper eventos existentes). Las solicitudes de `CrearTurno`, `ConfirmarTurno`, `CancelarTurno` y `ReprogramarTurno` reciben `actor_id` y lo propagan. La columna `historial_cambios.actor_id` es anulable (eventos previos a C-08 o escritos fuera de la API) con FK `RESTRICT` a `usuarios`, para que no se borre un usuario con historial. Los bloqueos no tienen historial en la KB; no se agrega auditoría de bloqueos.

### 6. Configuración y pruebas

`crear_app(fabrica, seguridad)` acepta una `ConfiguracionSeguridad` inyectada; sin ella la toma del entorno. Las pruebas generan un secreto aleatorio por sesión (`secrets.token_urlsafe`), crean usuarios con hashes calculados una vez por sesión y emiten tokens directamente con el emisor; el login real se prueba aparte. `.env.example` deja `JWT_SECRET` vacío con la instrucción para generarlo; `docker-compose.yml` lo toma de `${JWT_SECRET:-}`.

## Risks / Trade-offs

- [Token robado válido hasta su expiración] → vida corta por defecto y desactivación del usuario efectiva en el siguiente request; revocación queda para un change posterior.
- [Fuerza bruta sobre el login] → Argon2id encarece cada intento; rate limiting en C-09.
- [Matriz RBAC no validada] → centralizada en un único módulo de dominio con pruebas por rol; se ajusta cuando se responda la pregunta Alta.
- [Esquema local previo] → `usuarios` se crea con `create_all`, pero `historial_cambios.actor_id` requiere recrear la base local hasta C-07.
- [OpenAPI pública] → aceptable en local; C-09 decide su exposición.

## Migration Plan

Generar `JWT_SECRET` y exportarlo antes de levantar la API; recrear la base local (`docker compose down -v`) por la columna nueva; crear al menos un usuario con el comando. Los clientes deben obtener un token y enviarlo en `Authorization: Bearer`. Revertir implica retirar las dependencias de seguridad; `usuarios` y `actor_id` pueden quedar sin efecto.

## Open Questions

- ¿Quién puede crear, reprogramar, cancelar o confirmar y hasta cuándo? (Alta, sigue abierta; se aplica la matriz propuesta.)
- ¿El odontólogo/a puede ver la agenda de otros profesionales o del box?
- ¿Hace falta revocar sesiones (por ejemplo, al despedir personal) antes de que expire el token?
