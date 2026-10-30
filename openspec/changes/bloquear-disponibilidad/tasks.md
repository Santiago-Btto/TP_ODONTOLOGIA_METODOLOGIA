# Tasks

## 1. Base de pruebas y dominio

- [x] 1.1 Ejecutar primero la suite existente para establecer la red de seguridad de `CrearTurno`, persistencia y API con PostgreSQL de prueba. En PowerShell: `$backendPath=(Resolve-Path backend).Path`; luego `docker run --rm --network turnos-odontologia_default --mount "type=bind,source=$backendPath,target=/app" --workdir /app -e "TEST_DATABASE_URL=postgresql+psycopg://turnos:turnos@db:5432/turnos_test" tp-odontologia-verification-20261010-api:latest pytest -q -p no:cacheprovider`. Registrar cantidad de pruebas verdes y detener la implementación si aparece una falla preexistente.
- [x] 1.2 Escribir pruebas RED en `backend/tests/domain/test_bloqueos.py` para bloqueos válidos de profesional y box y selección inválida de recurso; crear la entidad y error mínimos, pasar GREEN, añadir un segundo caso distinto por comportamiento y refactorizar con el módulo en verde (`pytest backend/tests/domain/test_bloqueos.py`).
- [x] 1.3 Añadir pruebas RED para `fin <= inicio`, instantes sin zona y solapamiento semiabierto frente a contigüidad; implementar sólo la validación y regla de dominio necesarias, triangular inicio/fin en ambos bordes y verificar nuevamente el módulo de dominio.

## 2. Casos de uso y disponibilidad

- [x] 2.1 Escribir pruebas RED de `CrearBloqueo` con unidad de trabajo en memoria: profesional y box válidos, recurso inexistente y motivo opcional; implementar el caso de uso y puerto mínimos con un único commit en éxito y cero commits en error; triangular cada conducta y verificar `pytest backend/tests/application/test_crear_bloqueo.py`.
- [x] 2.2 Añadir pruebas RED de bloqueo que intersecta turno activo del mismo profesional y del mismo box, frente a bloqueo contiguo permitido; implementar el rechazo conservador `conflicto_turno_existente` sin alterar turno/historial y pasar las pruebas de aplicación.
- [x] 2.3 Añadir pruebas RED para registrar dos bloqueos superpuestos del mismo recurso y dos contiguos, sin turnos existentes; comprobar que el caso de uso acepta ambos pares y conserva los cuatro registros, sin introducir un conflicto bloqueo-vs-bloqueo (`pytest backend/tests/application/test_crear_bloqueo.py`).
- [x] 2.4 Ejecutar la red de seguridad de `CrearTurno` y escribir pruebas RED para alta intersectante con bloqueo de profesional, alta intersectante con bloqueo de box y alta contigua; extender el caso de uso y la regla de dominio sin poner disponibilidad en el router; triangular las tres rutas, verificar `pytest backend/tests/application/test_crear_turno.py` y conservar turno+historial atómicos.
- [x] 2.5 Escribir pruebas RED que exijan adquirir el recurso antes de leer conflictos en ambos casos de uso, con orden profesional→box para turnos; añadir el puerto de bloqueo transaccional y sus dobles, pasar GREEN y verificar que un rechazo no llama a `commit`.

## 3. PostgreSQL y concurrencia

- [x] 3.1 Escribir pruebas RED en `backend/tests/infrastructure/test_bloqueos.py` de `CHECK` XOR, `CHECK (fin > inicio)`, FKs y aceptación de escrituras directas de bloqueos superpuestos/contiguos; añadir `BloqueoModelo` e índices de búsqueda por recurso e intervalo sin `EXCLUDE` entre bloqueos, triangular profesional y box y verificar contra PostgreSQL real.
- [x] 3.2 Añadir pruebas RED de repositorio SQLAlchemy para buscar bloqueos y turnos activos por recurso e intersección e insertar bloqueo; implementar adaptador/UoW, verificar éxito, error de turno existente y ambos bordes contiguos en `backend/tests/infrastructure/test_bloqueos.py`, sin traducción de un conflicto inexistente entre bloqueos.
- [x] 3.3 Escribir pruebas RED con dos sesiones PostgreSQL y sincronización controlada para turno y bloqueo concurrentes del mismo profesional y del mismo box; implementar `SELECT ... FOR UPDATE` compartido, con lectura de conflictos **después** del lock bajo `READ COMMITTED`, y verificar los cuatro casos: turno primero/bloqueo primero por profesional y por box. En cada caso confirmar sólo una operación, conflicto para la otra y ausencia de deadlock.
- [x] 3.4 Ejecutar pruebas de persistencia existentes y nuevas, incluidas las restricciones `CHECK`/`EXCLUDE` de turnos, para comprobar que la extensión conserva C-01b/C-02 (`pytest backend/tests/infrastructure -q`).

## 4. API y documentación de uso

- [x] 4.1 Escribir pruebas RED en `backend/tests/api/test_bloqueos_api.py` para `POST /api/v1/bloqueos`: `201` de profesional y box con respuesta completa, `201` para bloqueos superpuestos, `404` por recurso inexistente y `409` sólo por turno activo incompatible; añadir esquemas, router, dependencia y mapa de errores mínimos; triangular cada respuesta y verificar el módulo API.
- [x] 4.2 Añadir pruebas RED de `422` por ambos/ningún recurso, fecha ausente o mal formada/sin zona y `fin <= inicio`, y de no mutación; implementar validación Pydantic/HTTP sin reglas de disponibilidad en el router y verificar el módulo API.
- [x] 4.3 Añadir pruebas API RED de `POST /api/v1/turnos` contra bloqueo de profesional y box con códigos `conflicto_bloqueo_profesional`/`conflicto_bloqueo_box`, y altas contiguas `201` en ambos sentidos (turno empieza al acabar el bloqueo y termina al iniciarlo); implementar sólo la traducción necesaria y verificar `pytest backend/tests/api -q`.
- [x] 4.4 Documentar en `README.md` el nuevo endpoint, ejemplos con IDs y fechas ficticios, respuestas y limitación de uso local; comprobar que el ejemplo coincide con OpenAPI y con una prueba de API.

## 5. Verificación integral

- [x] 5.1 Con `$backendPath=(Resolve-Path backend).Path`, ejecutar `docker run --rm --network turnos-odontologia_default --mount "type=bind,source=$backendPath,target=/app" --workdir /app -e "TEST_DATABASE_URL=postgresql+psycopg://turnos:turnos@db:5432/turnos_test" tp-odontologia-verification-20261010-api:latest pytest -q -p no:cacheprovider` y `openspec validate bloquear-disponibilidad --strict`; registrar resultados y matriz escenario→prueba, comprobar `git diff --check` y confirmar que no se implementó C-04 ni se versionaron secretos o datos reales.

## Workflow follow-up

- Tras pruebas verdes y revisión del cambio, sincronizar las specs vigentes y archivar C-03 con el flujo OpenSpec; actualizar `CHANGES.md` según la convención del proyecto.
