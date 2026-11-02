# Proposal

## Why

La API de agenda no tiene autenticación: cualquiera que alcance el puerto puede crear, reprogramar o cancelar turnos, y el historial no registra quién hizo cada cambio. La KB marca a C-08 como requisito para usar la API fuera del entorno local (`08_arquitectura_propuesta.md` §Seguridad), propone una matriz RBAC (`03_actores_y_roles.md`) y prevé `actorId` en `HistorialDeCambio`. C-15 (agenda web) depende de este change para su login.

## What Changes

- Usuarios del personal con rol `recepcion`, `odontologo` o `responsable`, contraseña con hash Argon2id y vínculo opcional a un profesional (para el odontólogo).
- `POST /api/v1/auth/token` (OAuth2 *password flow*) que emite un JWT HS256 firmado con `JWT_SECRET` de entorno, con expiración configurable; `GET /api/v1/auth/yo` devuelve el usuario autenticado sin datos sensibles.
- Una dependencia FastAPI exige `Authorization: Bearer` en **todas** las rutas `/api/v1` salvo la emisión de token: `401` si falta, está mal firmado, expiró o el usuario no existe o está inactivo; `403` si el rol no tiene permiso.
- Matriz de permisos propuesta en la KB aplicada en el dominio: recepción y responsable operan turnos, bloqueos y agenda; odontólogo/a sólo consulta su propia agenda.
- Historial con `actor_id`: crear, confirmar, cancelar y reprogramar registran al usuario autenticado.
- Comando para crear usuarios sin versionar contraseñas; `JWT_SECRET` obligatorio (mínimo 32 caracteres) y ausente del repositorio.

## Capabilities

### New Capabilities

- `autenticacion-y-autorizacion`: emisión y validación de JWT, protección de rutas, autorización por rol y trazabilidad del actor.

### Modified Capabilities

Ninguna en su comportamiento funcional: los contratos de turnos, agenda y bloqueos se conservan; ahora además exigen un token válido.

## Impact

- Dominio: `Rol`, `Permiso`, `Actor`, `Usuario`, matriz de permisos, `AccesoDenegadoError`; `actor_id` en `HistorialDeCambio`.
- Aplicación: casos de uso `Autenticar` y `ResolverActor`, puertos de usuarios, hash y tokens; `actor_id` en las solicitudes de los casos de uso que escriben historial.
- Persistencia: tabla `usuarios`; columna `historial_cambios.actor_id` con FK a `usuarios`.
- Infraestructura: `PyJWT`, `pwdlib[argon2]`, `python-multipart`; configuración por entorno; comando `crear_usuario`.
- API: router `auth`, dependencias de seguridad en todos los routers `/api/v1`, `401`/`403` con cuerpo `{codigo, detalle}`.
- Pruebas: token válido, expirado, firma inválida, algoritmo `none`, usuario inactivo, acceso denegado por rol, actor en historial y barrido de todas las rutas protegidas.
- Fuera de alcance: refresh tokens, revocación, rate limiting del login, CORS y endurecimiento para exposición pública (C-09), gestión de usuarios por API.
