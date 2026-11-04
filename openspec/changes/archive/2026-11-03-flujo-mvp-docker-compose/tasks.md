# Tasks

## 1. Configuración local de demostración

- [x] 1.1 Capturar baseline de `pytest` backend y pruebas/build frontend antes de editar; registrar conteos y fallos preexistentes.
- [x] 1.2 Escribir pruebas RED para creación de `.env` con secretos aleatorios válidos, repetición sin rotación, rechazo de archivo incompleto y ausencia de secretos en salida; implementar el script de preparación y verificar GREEN con casos distintos y `git check-ignore .env`.
- [x] 1.3 Documentar el comando de preparación y lectura local de la contraseña demo sin imprimirla en ejemplos de logs; verificar que el comando documentado funciona en un checkout con archivo temporal.

## 2. Datos ficticios y usuario idempotente

- [x] 2.1 Escribir pruebas RED contra PostgreSQL real para primer bootstrap de recursos/pacientes Demo y usuario `recepcion.demo`, segunda ejecución sin duplicados y discrepancia de contraseña/rol sin sobrescritura; implementar bootstrap reutilizando esquema, semillas y Argon2id existentes hasta GREEN y triangular los bordes.
- [x] 2.2 Documentar qué datos demo se cargan, la conservación de volúmenes y cómo resolver un `.env` que no corresponde al usuario ya creado; verificar que el procedimiento no borra datos automáticamente.

## 3. Orquestación Compose del MVP

- [x] 3.1 Escribir verificación RED de `docker compose config --format json` para servicios `db`, `redis`, `bootstrap`, `api`, `frontend` y `worker`, dependencias/healthchecks y ausencia de contraseña fija en archivos versionados; integrar los servicios de C-15 y C-16 en Compose, luego verificar GREEN sin volcar el secreto en logs.
- [x] 3.2 Verificar un primer arranque y un segundo arranque con `docker compose up -d --build`: API `/health`, página web y proxy `/api`, login demo, worker activo y filas demo sin duplicados; documentar los comandos de salud y reinicio local.
- [x] 3.3 Verificar que la API todavía inicia y opera con Redis indisponible (RN-EX-02), mientras el worker espera su dependencia; añadir una prueba de integración si el nuevo cableado modifica ese comportamiento.

## 4. Prueba E2E HTTP aislada

- [x] 4.1 Escribir primero una prueba RED por HTTP del recorrido login → alta de paciente → turno → agenda → bloqueo → rechazo `409` → reprogramación → recordatorio simulado por worker → cancelación → reutilización; afirmar respuestas, IDs, estados y agenda, usando sólo identificadores Demo.
- [x] 4.2 Implementar lanzador y override de Compose con proyecto/volúmenes/red aislados y puertos de host deshabilitados, ejecución de la prueba desde un servicio interno, credenciales por entorno y limpieza garantizada aun ante fallo; verificar GREEN y que la base local cotidiana conserve sus datos.
- [x] 4.3 Ejecutar el E2E dos veces desde cero y verificar resultado reproducible, polling acotado del recordatorio antes de cancelar y ausencia de mensajes externos; documentar el comando exacto y cómo inspeccionar fallos sin mostrar secretos.

## 5. Integración final

- [x] 5.1 Ejecutar `pytest` backend completo contra PostgreSQL real, pruebas y build frontend, `docker compose config --quiet`, OpenSpec strict y E2E aislado; corregir únicamente regresiones introducidas y registrar resultados verificables en la entrega.

## Workflow follow-up

- Sincronizar `entorno-mvp-local`, archivar C-06 y actualizar `CHANGES.md` una vez completadas y verificadas las tareas.

### Evidencia de verificación (2026-11-03)

- Baseline antes de C-06: backend `409 passed` con PostgreSQL real; C-15 frontend `24 passed` y build TypeScript estricto en verde; sin fallos previos.
- TDD C-06: preparación local 4 RED → 4 GREEN; bootstrap PostgreSQL 4 RED → 4 GREEN; contrato Compose 3 RED → 3 GREEN; E2E HTTP RED por login sin bootstrap → GREEN en dos proyectos descartables.
- Arranque normal: `/health`, web y login `200`; segundo `up --build --wait` conservó filas Demo (`2` pacientes, `2` profesionales, `2` boxes, `1` prestación, `1` usuario), su id y hash. Worker activo.
- Redis caído: API reiniciada sin Redis y `/health` más pacientes autenticados respondieron `200`; Redis y worker restaurados.
- Verificación final: backend `419 passed` contra PostgreSQL real (un aviso de deprecación en Starlette), frontend `24 passed` y `npm run build` verde; `docker compose config --quiet`, check Compose `3 passed`, OpenSpec strict y `git diff --check` en verde. E2E aislado verde en dos ejecuciones completas y otra posterior al ajuste de limpieza.
- Revisión del lanzador: prueba RED de fallo en `docker compose down --volumes` (estado incorrecto `0`), corrección y GREEN `2 passed`; ahora sólo anuncia éxito si la limpieza también termina bien.
