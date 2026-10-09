# Descripción General

## Stack tecnológico

> **Ajustar (2026-10-08).** La versión inicial de esta KB fijaba Node.js + TypeScript con repositorios en memoria. La consigna permite definir el stack desde la KB; el equipo revisó esa decisión y adoptó FastAPI + PostgreSQL + React, con su justificación en [DD-02](09_decisiones_y_supuestos.md#dd-02--stack-definido-fastapi--postgresql--react).

### Backend

| Capa | Tecnología | Versión mínima / nota |
|---|---|---|
| Lenguaje | Python | 3.12 |
| Framework HTTP | FastAPI | 0.115 |
| ORM | SQLAlchemy | 2.0 (API tipada `Mapped[...]`) |
| Persistencia | PostgreSQL | 17; extensión `btree_gist` para restricciones de exclusión |
| Autenticación | JWT (OAuth2 password flow + bearer token) | Se incorpora en C-08; nunca con secretos versionados |
| Tareas asincrónicas | Redis | Cola/broker para recordatorios y tareas diferidas (C-16 simulado, C-10 WhatsApp); el alta de turnos no lo necesita |
| Pruebas | pytest + httpx (`TestClient`) | Contra PostgreSQL real, sin cuentas externas |
| Contenedores | Docker / Docker Compose | `db` (PostgreSQL) y `api` (FastAPI) desde C-01b; `redis` se agrega con C-16 |

### Frontend

| Capa | Tecnología | Nota |
|---|---|---|
| Librería UI | React | Se incorpora en C-15 (agenda web), después de la API autenticada |
| Lenguaje | TypeScript | Modo `strict` |
| Build | Vite | Servidor de desarrollo y build de producción |

## Arquitectura general

El dominio sigue siendo la autoridad de disponibilidad. Los canales (API, frontend, bots futuros) invocan casos de uso; nunca recalculan reglas por su cuenta. PostgreSQL agrega una segunda barrera: una restricción de exclusión impide persistir dos turnos activos solapados del mismo profesional o box aunque un adaptador eluda la validación de aplicación.

```text
Frontend React + TS + Vite (C-15)
          |
          v  HTTP/JSON (JWT desde C-08)
API FastAPI  ----------------->  Redis (tareas asincrónicas, C-16)
          |
          v
Casos de uso (aplicación)
          |
          v
Dominio: turnos, disponibilidad y reglas anti-solapamiento (Python puro)
          |
          v
Repositorios SQLAlchemy  ----->  PostgreSQL (EXCLUDE USING gist)
```

## Integraciones externas

| Servicio | Propósito potencial | Estado en MVP |
|---|---|---|
| WhatsApp | Recordatorios, confirmación o cambio de turnos | Posterior; en el MVP el recordatorio es simulado y registrado (C-16) |
| Mercado Pago | Seña | Posterior; reglas de seña/reintegro sin acordar |
| Google Calendar | Sincronización de agenda | Posterior |

No se usan cuentas, credenciales ni llamadas externas durante pruebas.

## API REST

Versionada bajo `/api/v1`. Los endpoints delegan en los casos de uso y traducen errores de dominio a respuestas HTTP:

| Método | Ruta | Change | Respuestas |
|---|---|---|---|
| `GET` | `/health` | C-01b | `200` con estado de la API y de la base |
| `POST` | `/api/v1/turnos` | C-01b | `201` creado, `404` recurso inexistente, `409` conflicto de profesional/box, `422` intervalo o duración inválidos |

Hasta que exista C-08 (JWT), la API sólo se ejecuta en entorno local de desarrollo y no debe desplegarse.
