# Tasks

## 1. Red de seguridad y dominio

- [ ] 1.1 Ejecutar la suite existente contra PostgreSQL de prueba y registrar el resultado (234 tests tras C-04).
- [ ] 1.2 Escribir pruebas RED en `backend/tests/domain/test_autorizacion.py` para la matriz de permisos por rol y el alcance de agenda del odontólogo/a; implementar `app/domain/autorizacion.py`; verificar GREEN.

## 2. Casos de uso

- [ ] 2.1 Escribir pruebas RED en `backend/tests/application/test_autenticacion.py` con dobles en memoria: login válido, contraseña incorrecta, usuario inexistente (verificación contra hash ficticio) e inactivo; resolución de actor con token válido, expirado, inválido, usuario borrado o desactivado.
- [ ] 2.2 Implementar `Autenticar`, `ResolverActor` y sus puertos; verificar GREEN.
- [ ] 2.3 Escribir pruebas RED que exijan `actor_id` en el historial de crear, confirmar, cancelar y reprogramar; agregar el campo y propagarlo en las solicitudes; verificar GREEN sin romper las pruebas previas.

## 3. Infraestructura

- [ ] 3.1 Escribir pruebas RED en `backend/tests/infrastructure/test_seguridad.py`: hash Argon2id verificable, configuración rechaza secreto ausente o corto, JWT con `exp`/`iat`/`sub`, rechazo de otra firma y de `alg: none`.
- [ ] 3.2 Implementar `HasherArgon2`, `EmisorJWT` y `ConfiguracionSeguridad`; agregar dependencias fijadas a `requirements.txt`; verificar GREEN.
- [ ] 3.3 Escribir pruebas RED en `backend/tests/infrastructure/test_usuarios.py`: tabla `usuarios` (único, `CHECK` de rol, FK), repositorio, comando de alta (contraseña corta, duplicado) y FK de `historial_cambios.actor_id`; implementar; verificar GREEN.

## 4. API

- [ ] 4.1 Mover la fixture `cliente` de las pruebas de API a `backend/tests/api/conftest.py` con secreto aleatorio, usuarios por rol y token de recepción; adaptar los módulos existentes sin cambiar sus aserciones.
- [ ] 4.2 Escribir pruebas RED en `backend/tests/api/test_auth_api.py`: login, `yo`, `401` (sin token, expirado, firma inválida, `none`, usuario desactivado), `403` por rol, odontólogo/a con su agenda, actor en historial y barrido de todas las rutas `/api/v1`.
- [ ] 4.3 Implementar router `auth`, dependencias `actor_actual` / `requiere`, protección a nivel router, propagación del actor y mapeo `401`/`403` con `WWW-Authenticate`; verificar GREEN.
- [ ] 4.4 Actualizar `.env.example`, `docker-compose.yml` y `README.md` (generar secreto, crear usuario, obtener y usar token).

## 5. Verificación integral

- [ ] 5.1 Ejecutar la suite completa, `openspec validate autenticar-con-jwt`, `git diff --check` y una búsqueda de secretos en el diff; revisar el cambio con `security-best-practices` (FastAPI) y registrar hallazgos.

## Workflow follow-up

- Sincronizar `autenticacion-y-autorizacion` en `openspec/specs/`, archivar el change, marcar C-08 en `CHANGES.md` y actualizar la KB (actores, arquitectura).
