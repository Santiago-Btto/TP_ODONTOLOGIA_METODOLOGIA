# Proposal

## Why

La API ya permite autenticar personal, registrar pacientes y turnos, y consultar agenda, pero recepción y profesionales sólo pueden operarla con clientes HTTP. El MVP necesita una interfaz web usable que muestre el resultado real de la API y explique por qué una reserva fue rechazada.

## What Changes

- Crear `frontend/` con React, TypeScript estricto y Vite para iniciar sesión y consultar agenda diaria o semanal, filtrada por profesional y/o box.
- Permitir al personal autorizado buscar o registrar un paciente ficticio y crear un turno; mostrar los errores `409` y `422` recibidos de la API sin calcular disponibilidad en el navegador.
- Ajustar la interfaz al rol devuelto por `/api/v1/auth/yo`: un odontólogo consulta exclusivamente su propia agenda; recepción y responsable pueden operar turnos y pacientes.
- Servir el frontend como servicio de Docker Compose con proxy same-origin hacia la API; documentar ejecución y pruebas de componentes y cliente HTTP.

## Capabilities

### New Capabilities

- `agenda-web`: interacción web autenticada para consulta diaria/semanal, alta de turnos y visualización de errores del servidor.

### Modified Capabilities

Ninguna. Los contratos de la API existente permanecen vigentes.

## Impact

Nuevo `frontend/`, pruebas y dependencias npm; servicio y configuración de proxy en `docker-compose.yml`; instrucciones de uso en `README.md`. La API FastAPI, la persistencia y las reglas de dominio no cambian.
