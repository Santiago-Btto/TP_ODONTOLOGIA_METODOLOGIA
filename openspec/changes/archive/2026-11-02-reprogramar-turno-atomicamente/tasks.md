# Tasks

## 1. Red de seguridad y dominio

- [x] 1.1 Ejecutar la suite existente contra PostgreSQL de prueba y registrar el resultado (181 tests tras C-05).
- [x] 1.2 Escribir pruebas RED en `backend/tests/domain/test_turnos.py` para `Turno.reprogramar`: cambio de horario y de recursos, conservación del estado, `fin <= inicio`, sin cambios y turno cancelado; implementar `ResumenTurno`, `TipoCambio.REPROGRAMADO`, `ReprogramacionSinCambiosError` y el método; verificar GREEN.
- [x] 1.3 Escribir una prueba RED en `backend/tests/domain/test_disponibilidad.py` que exija ignorar un turno activo con el mismo `id` que el candidato; implementar la autoexclusión en `verificar_disponibilidad`.

## 2. Caso de uso

- [x] 2.1 Escribir pruebas RED en `backend/tests/application/test_reprogramar_turno.py` con unidad de trabajo en memoria: horario y recursos válidos, conservación de duración, historial con antes/después, autoexclusión, conflictos por profesional/box/bloqueo (incluido el recurso nuevo), destino contiguo, recursos inexistentes y fallo atómico al agregar historial.
- [x] 2.2 Escribir una prueba RED que exija el orden fila del turno → recursos de destino (profesional → box) antes de leer conflictos; implementar `ReprogramarTurno` y verificar GREEN.

## 3. PostgreSQL

- [x] 3.1 Escribir pruebas RED en `backend/tests/infrastructure/test_reprogramar_turno.py`: persistencia del intervalo, recursos y `antes`/`despues` en `historial_cambios`; liberación del intervalo anterior; rechazo sin cambios; fallo de historial con rollback.
- [x] 3.2 Agregar las columnas `antes` y `despues` (`JSONB`) a `HistorialModelo` y su serialización en `HistorialesSQLAlchemy`; verificar GREEN.
- [x] 3.3 Escribir pruebas de carrera entre reprogramación y alta en ambos órdenes con sesiones PostgreSQL separadas; verificar un único ganador y ausencia de interbloqueo.

## 4. API

- [x] 4.1 Escribir pruebas RED en `backend/tests/api/test_reprogramar_api.py` para `PATCH /api/v1/turnos/{id}`: `200`, `404`, `409` (conflicto y cancelado), `422` (intervalo inválido, sin cambios, cuerpo vacío, campo desconocido y fecha sin zona) y no mutación ante errores.
- [x] 4.2 Agregar `ReprogramacionEntrada`, la ruta, la dependencia y el mapeo `ReprogramacionSinCambiosError → 422`; verificar GREEN.
- [x] 4.3 Documentar la ruta y la necesidad de recrear la base local en `README.md`.

## 5. Verificación integral

- [x] 5.1 Ejecutar la suite completa, `openspec validate reprogramar-turno-atomicamente` y `git diff --check`; confirmar que no se versionaron secretos ni datos reales.

## Workflow follow-up

- Sincronizar `reprogramacion-de-turnos` en `openspec/specs/`, archivar el change, marcar C-04 en `CHANGES.md` y registrar las preguntas abiertas nuevas en la KB.
