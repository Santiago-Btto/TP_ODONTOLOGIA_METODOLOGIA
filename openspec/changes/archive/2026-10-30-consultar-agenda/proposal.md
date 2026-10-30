# Proposal

## Why

La reserva de turnos ya existe, pero recepción y profesionales todavía no pueden consultar qué turnos ocupan un rango diario o semanal. C-02 habilita esa lectura sobre la base de C-01b y permite construir después la vista de agenda C-15, conforme a `CHANGES.md` y US-002 de `knowledge-base/06_funcionalidades.md`.

## What Changes

- Incorporar una consulta de turnos por rango temporal obligatorio, con filtros opcionales por `profesional_id` y `box_id`, combinables entre sí.
- Devolver los turnos que intersectan el rango semiabierto `[inicio, fin)`, ordenados por inicio, con profesional y box identificables; un rango sin coincidencias devuelve una lista vacía.
- Exponer `GET /api/v1/agenda` con fechas que incluyen zona horaria y rechazo explícito de rangos inválidos o parámetros mal formados.
- Planificar pruebas de caso de uso, persistencia y API para consulta diaria y semanal, filtros, intervalos contiguos, rangos vacíos y errores.
- Mantener fuera de C-02 la interfaz web (C-15), la cancelación y sus estados (C-05), y la autenticación (C-08).

## Capabilities

### New Capabilities

- `consulta-de-agenda`: lectura de turnos por intervalo y recursos, con reglas de intersección, orden y contrato HTTP.

### Modified Capabilities

Ninguna. La especificación existente `creacion-de-turnos` conserva sus requisitos de alta; esta capacidad añade una lectura independiente.

## Impact

- Backend FastAPI: nuevo caso de uso y puerto de lectura, adaptador SQLAlchemy y ruta `GET /api/v1/agenda`; esquema de salida mínimo para agenda, sin datos de paciente.
- PostgreSQL: consulta de datos existentes, sin migración ni escritura nuevas previstas.
- Pruebas: ampliación de `backend/tests/application/`, `backend/tests/infrastructure/` y `backend/tests/api/`.
- Dependencia de roadmap: C-01b archivado; C-15 consumirá esta API. Referencias: `CHANGES.md` C-02, `knowledge-base/04_modelo_de_datos.md` §Turno, `knowledge-base/05_reglas_de_negocio.md` RN-DI-01 y `knowledge-base/06_funcionalidades.md` US-002.
