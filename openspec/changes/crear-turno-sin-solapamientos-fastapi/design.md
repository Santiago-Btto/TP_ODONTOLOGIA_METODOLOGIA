# Design

## Context

C-01 dejó un núcleo Node.js en memoria con el contrato `creacion-de-turnos`. La KB ajustada (DD-02) fija Python/FastAPI/SQLAlchemy/PostgreSQL. Este change reimplementa el contrato en ese stack y agrega la protección en la base. El relevamiento previo está en `docs/opsx/explore-crear-turno-fastapi.md`.

## Goals / Non-Goals

**Goals:**

- Dominio Python puro (sin FastAPI ni SQLAlchemy) con las mismas reglas de C-01.
- Turno + historial confirmados en una única transacción.
- Defensa en profundidad: PostgreSQL rechaza solapamientos aunque se eluda el caso de uso.
- Contrato HTTP estable para el alta, con códigos de error de dominio.

**Non-Goals:**

- Autenticación JWT (C-08), Redis (C-16), frontend (C-15), migraciones Alembic (C-07).
- Bloqueos, cancelación/confirmación, consulta de agenda.
- Recursos inactivos: el modelo guarda `activo`, pero la regla de rechazo no está especificada y queda como pregunta abierta.

## Decisions

### Capas

```text
backend/app/
  domain/          turnos.py (entidades + errores), disponibilidad.py (regla pura)
  application/     puertos.py (Protocols), crear_turno.py (caso de uso)
  infrastructure/  db.py, modelos.py (ORM + DDL), unidad_de_trabajo.py, semillas.py
  api/             main.py (app, /health, manejadores de error), turnos.py (router), esquemas.py
```

`domain` no importa nada de `application`, `infrastructure` ni `api`. El caso de uso depende de un puerto `UnidadDeTrabajo` (repositorios + `commit`), no de SQLAlchemy.

### Intersección semiabierta

`se_solapan(a, b) = a.inicio < b.fin and b.inicio < a.fin`. Igual que C-01. Las fechas son `datetime` con zona horaria (`timestamptz` en la base); la API exige fechas con zona (`AwareDatetime`) y responde 422 si faltan.

### Restricción de exclusión en PostgreSQL

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE turnos ADD CONSTRAINT turnos_sin_solapamiento_profesional
  EXCLUDE USING gist (profesional_id WITH =, tstzrange(inicio, fin, '[)') WITH &&)
  WHERE (estado <> 'cancelado');
ALTER TABLE turnos ADD CONSTRAINT turnos_sin_solapamiento_box
  EXCLUDE USING gist (box_id WITH =, tstzrange(inicio, fin, '[)') WITH &&)
  WHERE (estado <> 'cancelado');
```

El rango `'[)'` reproduce la regla del dominio: los turnos contiguos no colisionan. El `WHERE` deja preparado C-05 (cancelar libera el intervalo). Se agrega con un `DDL` asociado a `after_create` de la tabla.

Alternativa considerada: sólo `SELECT ... FOR UPDATE` antes de insertar. Descartada: no bloquea filas inexistentes y deja la ventana de doble reserva.

### Transacción y traducción de errores

`CrearTurno.ejecutar` abre la unidad de trabajo, busca los cuatro recursos (`RecursoInexistenteError` si falta alguno), construye el candidato, consulta turnos activos que se solapen por profesional y por box, llama a `verificar_disponibilidad`, agrega turno e historial y hace `commit`. Si el `commit` viola una restricción de exclusión (carrera entre dos requests), la unidad de trabajo traduce `IntegrityError` según el nombre de la restricción a `ConflictoProfesionalError` o `ConflictoBoxError` y hace rollback. Ante cualquier error, nada queda persistido.

### Mapeo HTTP

| Error de dominio | HTTP | `codigo` |
|---|---|---|
| `RecursoInexistenteError` | 404 | `recurso_inexistente` |
| `ConflictoProfesionalError` | 409 | `conflicto_profesional` |
| `ConflictoBoxError` | 409 | `conflicto_box` |
| `IntervaloInvalidoError` | 422 | `intervalo_invalido` |
| `DuracionInvalidaError` | 422 | `duracion_invalida` |

El cuerpo es `{"codigo": ..., "detalle": ...}`. El router no recalcula disponibilidad.

### Identificadores y tiempo

Los IDs son texto. El router genera el ID del turno (`uuid4`); el caso de uso lo recibe para seguir siendo determinista en tests. El instante del historial viene de un reloj inyectado.

### Pruebas

- `tests/domain`: reglas puras.
- `tests/application`: caso de uso con una unidad de trabajo en memoria (doble de prueba del puerto), para comprobar la ausencia de escrituras ante cada rechazo.
- `tests/infrastructure` y `tests/api`: contra PostgreSQL real (`TEST_DATABASE_URL`); el esquema se recrea por sesión y las tablas se vacían por test.

### Entorno

`docker-compose.yml`: `db` (`postgres:17`, con healthcheck) y `api` (build de `backend/`, `uvicorn`). Las credenciales del compose son sólo de desarrollo local. El esquema se crea al iniciar la API; las semillas ficticias se cargan con `python -m app.infrastructure.semillas`.

## Risks / Trade-offs

- [`create_all` no migra esquemas existentes] → Aceptable sin datos reales; Alembic entra en C-07.
- [API sin autenticación] → Sólo uso local hasta C-08; documentado en README y KB.
- [Los tests requieren PostgreSQL] → Dos caminos documentados (Docker Compose o local).

## Migration Plan

No hay datos que migrar. Se elimina el núcleo TypeScript (`src/`, `test/`, `package.json`, `tsconfig.json`); el archive de C-01 conserva su historia. Rollback: revertir los commits de este change.
