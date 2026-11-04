# Proposal

## Why

Las funciones del MVP ya existen por separado, pero el entorno local todavía exige crear el usuario demo y cargar semillas a mano, no arranca un worker continuo y carece de una prueba que demuestre el recorrido integrado. C-06 convierte esas piezas en un sistema reproducible y verificable desde Docker Compose.

## What Changes

- Incorporar una preparación local que genere `JWT_SECRET` y contraseña demo aleatorios en un `.env` ignorado por Git, con instrucciones de uso y sin registrar secretos en logs.
- Hacer que `docker compose up` levante PostgreSQL, Redis, API, frontend y worker continuo, espere la disponibilidad de sus dependencias y cargue datos y usuario de recepción ficticios de forma idempotente.
- Añadir una prueba E2E de la API integrada: autenticación, paciente, turno, agenda, bloqueo y rechazo, reprogramación, recordatorio simulado registrado, cancelación y reutilización del horario.
- Documentar arranque, credenciales locales, comprobaciones, pruebas y reinicio del entorno de demostración.

## Capabilities

### New Capabilities

- `entorno-mvp-local`: arranque reproducible del MVP completo con datos ficticios, configuración local fuera del repositorio y verificación integrada por HTTP.

### Modified Capabilities

Ninguna. Los contratos funcionales de autenticación, turnos, agenda, bloqueos, pacientes y recordatorios se conservan.

## Impact

- `docker-compose.yml`, script local de configuración, bootstrap de infraestructura, prueba E2E y `README.md`.
- Reutiliza el servicio `frontend` incorporado por C-15, las semillas de `backend/app/infrastructure/semillas.py` y el worker de C-16; no modifica reglas de disponibilidad ni introduce migraciones de C-07.
- Requiere Docker Compose y una configuración local inicial; el repositorio nunca almacena contraseñas ni secretos.
