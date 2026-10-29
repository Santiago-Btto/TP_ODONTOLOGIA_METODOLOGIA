# Tasks

## 1. Regla de consulta y caso de uso

- [ ] 1.1 Escribir primero en `backend/tests/application/test_consultar_agenda.py` pruebas RED de rango válido y `fin <= inicio` (error de regla de consulta); implementar `ConsultarAgenda` y solicitud tipada con validación mínima; verificar GREEN con `pytest backend/tests/application/test_consultar_agenda.py`.
- [ ] 1.2 Triangular el caso de uso con rango diario/semanal, fechas con distinto desplazamiento equivalente, filtros opcionales y ausencia de escrituras o `commit`; verificar las pruebas de aplicación y que el puerto recibe el intervalo y filtros esperados.

## 2. Lectura SQLAlchemy

- [ ] 2.1 Escribir primero pruebas RED en `backend/tests/infrastructure/test_consultar_agenda.py` para turno contenido, que empieza antes, que termina después y que cubre todo el rango; implementar el puerto de lectura y el predicado `turno.inicio < fin AND turno.fin > inicio`; verificar GREEN con PostgreSQL de prueba.
- [ ] 2.2 Añadir pruebas para ambos bordes contiguos excluidos, rango vacío e ID de texto sin coincidencias; ajustar sólo la consulta necesaria y verificar `pytest backend/tests/infrastructure/test_consultar_agenda.py`.
- [ ] 2.3 Añadir pruebas para filtro de profesional, filtro de box y combinación `AND`, más orden cronológico ascendente y recursos en los resultados; implementar filtros y orden; verificar el mismo módulo de pruebas, sin exigir desempate para inicios iguales.

## 3. Contrato HTTP de agenda

- [ ] 3.1 Escribir primero pruebas RED en `backend/tests/api/test_agenda_api.py` para `GET /api/v1/agenda`: `200` con lista de consulta diaria/semanal y recursos, y `200 []` sin coincidencias; añadir esquema de salida mínimo, dependencia del caso de uso y router; verificar GREEN con `pytest backend/tests/api/test_agenda_api.py`.
- [ ] 3.2 Añadir pruebas para `422` por `inicio` o `fin` ausente, fecha mal formada, fecha sin zona y `fin <= inicio` (error de regla de consulta), y que el rechazo no modifica datos; implementar validación y traducción HTTP; verificar el mismo módulo de pruebas.
- [ ] 3.3 Documentar en `README.md` la ruta, parámetros y ejemplo con fechas y zona horaria, filtros de IDs de texto y respuesta vacía; verificar que el ejemplo coincide con OpenAPI y con una prueba de API.

## 4. Integración

- [ ] 4.1 Ejecutar la suite completa del backend y `openspec validate consultar-agenda --strict`; verificar que el alta C-01b sigue pasando, que no hubo cambio de esquema ni escritura durante la consulta y que los escenarios de `specs/consulta-de-agenda/spec.md` tienen prueba asociada.

## Workflow follow-up

- Tras revisión e implementación aprobadas, archivar el change mediante el flujo OpenSpec correspondiente. El archivado no forma parte de esta preparación de Parte 2.
