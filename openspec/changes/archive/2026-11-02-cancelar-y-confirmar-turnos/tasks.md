# Tasks

## 1. Red de seguridad y dominio

- [x] 1.1 Ejecutar la suite existente contra PostgreSQL de prueba (`TEST_DATABASE_URL=... pytest -q -p no:cacheprovider` desde `backend/`) y registrar el resultado antes de tocar código.
- [x] 1.2 Escribir pruebas RED en `backend/tests/domain/test_turnos.py` para la tabla de transiciones (dos válidas desde `programado`, una desde `confirmado`, tres inválidas) y la propiedad `activo`; agregar estados, tipos de cambio, `TransicionInvalidaError` y métodos `confirmar()` / `cancelar()`; verificar GREEN.

## 2. Casos de uso

- [x] 2.1 Escribir pruebas RED en `backend/tests/application/test_cambiar_estado_turno.py` con unidad de trabajo en memoria: confirmación y cancelación exitosas con un único historial y un commit; transiciones inválidas y turno inexistente sin historial ni commit; lectura con bloqueo de fila antes de transicionar.
- [x] 2.2 Agregar al puerto `RepositorioTurnos` `obtener_para_actualizar` y `actualizar`; implementar `CancelarTurno` y `ConfirmarTurno`; verificar GREEN.

## 3. PostgreSQL

- [x] 3.1 Escribir pruebas RED en `backend/tests/infrastructure/test_ciclo_de_vida.py`: estado e historial persistidos; cancelar libera el intervalo para un alta y para un bloqueo; confirmar conserva la reserva; la base acepta por escritura directa un turno sobre un intervalo cancelado.
- [x] 3.2 Implementar `obtener_para_actualizar` (`SELECT ... FOR UPDATE`) y `actualizar` en `TurnosSQLAlchemy`; verificar GREEN.
- [x] 3.3 Escribir una prueba de dos cancelaciones concurrentes con sesiones separadas y pausa controlada del primer commit; verificar un único `cancelado` y `transicion_invalida` para la segunda.

## 4. API

- [x] 4.1 Escribir pruebas RED en `backend/tests/api/test_ciclo_de_vida_api.py`: `200` al confirmar y cancelar, reutilización del horario (`201`), `409 transicion_invalida`, `404 recurso_inexistente` y `422` por identificador demasiado largo.
- [x] 4.2 Agregar rutas, dependencias y mapeo `TransicionInvalidaError → 409`; agregar `estado` a `TurnoAgendaSalida` y actualizar la prueba de OpenAPI de la agenda; verificar GREEN.
- [x] 4.3 Documentar las rutas en `README.md` con ejemplos ficticios.

## 5. Verificación integral

- [x] 5.1 Ejecutar la suite completa, `openspec validate cancelar-y-confirmar-turnos` y `git diff --check`; confirmar que no se versionaron secretos ni datos reales.

## Workflow follow-up

- Sincronizar `ciclo-de-vida-del-turno` y `consulta-de-agenda` en `openspec/specs/`, archivar el change y marcar C-05 en `CHANGES.md`.
