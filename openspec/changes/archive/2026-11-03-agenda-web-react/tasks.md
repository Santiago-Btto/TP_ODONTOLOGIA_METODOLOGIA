# Tasks

## 1. Base del frontend

- [x] 1.1 Crear `frontend/` con React, TypeScript `strict`, Vite, scripts `dev`, `build`, `test` y dependencias fijadas en lockfile; verificar `npm ci` y `npm run build` sin `any`.
- [x] 1.2 Preparar Vitest y React Testing Library con entorno DOM y primera prueba de render; verificar `npm test -- --run` en verde.

## 2. Contratos HTTP y sesión

- [x] 2.1 Escribir primero pruebas RED del cliente para login form-encoded, `/auth/yo`, Bearer, errores de dominio/validación/red y `401`; implementar lo mínimo hasta GREEN, triangular con al menos dos casos por comportamiento y verificar la suite del cliente.
- [x] 2.2 Escribir primero pruebas RED del flujo de login, credenciales inválidas, cierre y expiración; implementar sesión en memoria e identidad por rol, verificar pruebas de componente y que no queden datos protegidos tras `401`.

## 3. Consulta de agenda

- [x] 3.1 Escribir pruebas RED de límites `[inicio, fin)` diarios y semanales con fechas ISO y zona explícita (incluido cambio de mes); implementar funciones puras y verificar casos múltiples.
- [x] 3.2 Escribir pruebas RED de agenda diaria/semanal, orden recibido, columnas de estado, vacío, error y reintento; implementar vistas y verificar pruebas de componente.
- [x] 3.3 Escribir pruebas RED para filtros profesional/box combinados y odontólogo restringido a su `profesional_id`; implementar controles por rol y verificar que todas las consultas del odontólogo incluyan su filtro.

## 4. Pacientes y alta de turno

- [x] 4.1 Escribir pruebas RED de búsqueda y alta mínima de pacientes, selección del `id` devuelto, rechazo `409` y ausencia de controles para odontólogo; implementar UI y verificar pruebas de componente y cliente.
- [x] 4.2 Escribir pruebas RED del formulario de alta para `201`, `409`, `422`, retención de campos y reconsulta de agenda; implementar sin calcular disponibilidad y verificar pruebas de componente y cliente.

## 5. Distribución y documentación

- [x] 5.1 Crear build de frontend servida por Nginx con proxy `/api/` hacia `api:8000`, fallback SPA y servicio `frontend` en Compose; verificar `docker compose config` y que la UI y `/api/v1/auth/token` compartan origen.
- [x] 5.2 Documentar en `README.md` instalación, arranque, login ficticio, IDs demo de recursos, zona horaria visible, pruebas y limitación de catálogos; verificar manualmente los comandos escritos.
- [x] 5.3 Ejecutar suite frontend completa, build con `strict`, y suite backend existente para comprobar integración sin regresiones; registrar resultados y corregir cualquier fallo introducido.

### Verificación C-15

- `npm ci --no-audit --no-fund`: instalación reproducible desde lockfile.
- `npm test -- --run`: 24 pruebas frontend aprobadas (cliente, períodos y componentes).
- `npm run build`: TypeScript `strict` y Vite aprobados.
- `docker compose config --quiet` y `docker compose build frontend --quiet`: aprobados.
- Proxy del mismo origen en Compose: `GET /` respondió `200` y `GET /api/v1/auth/token` respondió `405` (ruta POST alcanzada a través de Nginx).
- `docker compose run --rm --no-deps -e TEST_DATABASE_URL=postgresql+psycopg://turnos:turnos@db:5432/turnos_test api pytest -q`: 409 aprobadas, 1 warning deprecación Starlette/anyio.

## Workflow follow-up

- Sincronizar la especificación `agenda-web`, archivar C-15 y actualizar `CHANGES.md` después de las verificaciones.
