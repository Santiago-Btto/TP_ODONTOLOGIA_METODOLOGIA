# Proposal

## Why

**Justificación de la elección.** Elegimos reimplementar “crear turno evitando solapamientos por profesional y por box” porque es el primer ítem imprescindible del MVP de la sección D del Discovery (disponibilidad por profesional y sillón/box con **prevención transaccional** de solapamientos), tiene reglas verificables (intersección semiabierta, turnos contiguos válidos) y es una sola funcionalidad que se puede terminar. Es además la base de la que dependen todos los demás changes del MVP en `CHANGES.md`.

C-01 ya especificó y probó este comportamiento, pero en Node.js + TypeScript con repositorios en memoria. El proyecto ajustó su stack a FastAPI + SQLAlchemy + PostgreSQL (KB §DD-02), y los repositorios en memoria no pueden impedir dos reservas concurrentes del mismo recurso. Este change traslada el contrato al stack definido y agrega la barrera de la base de datos.

## What Changes

- Crear `backend/` (Python 3.12, FastAPI, SQLAlchemy 2.0, pytest) y `docker-compose.yml` con PostgreSQL 17 y la API.
- Portar el dominio a Python puro: entidades, errores y la intersección `[inicio, fin)`.
- Modelos SQLAlchemy de paciente, profesional, box, prestación, turno e historial, con `CHECK (fin > inicio)` y restricciones `EXCLUDE USING gist` por profesional y por box.
- Caso de uso `CrearTurno` que valida recursos, intervalo y disponibilidad y confirma turno + historial `creado` en una única transacción.
- `POST /api/v1/turnos` (201/404/409/422) y `GET /health`.
- Tests pytest por escenario del spec (dominio y caso de uso con dobles de los puertos; restricciones y API contra PostgreSQL real).
- **BREAKING (interno):** se eliminan `src/`, `test/`, `package.json` y `tsconfig.json` del núcleo Node.js. El archive de C-01 se conserva como historial.
- Fuera de alcance: JWT (C-08), Redis (C-16), frontend (C-15), bloqueos, cancelación, consulta de agenda y migraciones Alembic (C-07).

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `creacion-de-turnos`: los escenarios pasan a formato DADO / CUANDO / ENTONCES; se agregan el rechazo de recursos inexistentes, la protección en la persistencia y el contrato HTTP del alta.

## Impact

- Código nuevo en `backend/`; se retira el núcleo TypeScript.
- Nueva dependencia de infraestructura: PostgreSQL (Docker Compose o instalación local) para ejecutar los tests de integración.
- Sin credenciales reales: `.env.example` sólo trae valores de desarrollo local.
- `README.md` documenta la nueva forma de instalar y correr los tests.
