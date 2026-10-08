# Exploración — crear turno sin solapamientos en FastAPI + PostgreSQL (C-01b)

Fecha: 2026-10-08

## Estado del código antes del change

- `src/` y `test/` contienen el núcleo de C-01 en Node.js + TypeScript: dominio (`turnos.ts`, `disponibilidad.ts`), caso de uso `CrearTurno` y repositorios en memoria. `npm test` pasa 20/20.
- `npm run build` sólo quita tipos (`--experimental-strip-types`); `tsc --noEmit` **falla** (TS5097 por imports `.ts` sin `allowImportingTsExtensions` y TS2307 por falta de `@types/node`). La regla “TypeScript estricto” nunca se verificó.
- No hay persistencia, API, contenedores ni autenticación.
- La knowledge-base, `AGENTS.md` y `CHANGES.md` ya fueron ajustados al stack definido (commits `bc96daf` y `c5bab36`).

## Problema

El comportamiento de C-01 es correcto y está especificado, pero está implementado en un stack que el proyecto no va a usar. Además, la sección D del Discovery pide **prevención transaccional** de solapamientos, imposible de garantizar con repositorios en memoria: dos procesos podrían validar a la vez y reservar el mismo recurso.

## Qué se conserva y qué cambia

| Aspecto | C-01 (Node) | C-01b (FastAPI) |
|---|---|---|
| Intersección `[inicio, fin)` y turnos contiguos válidos | Sí | Igual, en Python puro |
| Errores distinguibles (profesional, box, intervalo, duración) | Clases `Error` | Excepciones de dominio |
| Turno + historial `creado` sin estado parcial | Orden de escrituras en memoria | Una transacción SQLAlchemy |
| Recursos referenciados | Objetos completos en la entrada | IDs que deben existir en la base |
| Protección ante concurrencia | No | `EXCLUDE USING gist` en PostgreSQL |
| Canal | Ninguno | `POST /api/v1/turnos` |

## Comportamientos de aceptación

1. Alta válida: turno + un historial `creado`.
2. Conflicto por profesional (con otro box) y por box (con otro profesional): rechazo sin escrituras.
3. Turno contiguo (empieza cuando termina otro): aceptado, también por la restricción de la base.
4. Intervalo con fin ≤ inicio y prestación con duración ≤ 0: rechazo sin escrituras.
5. Nuevo: recurso inexistente (paciente, profesional, box o prestación) → rechazo.
6. Nuevo: un solapamiento que elude la validación de aplicación es rechazado por PostgreSQL.
7. Nuevo: la API traduce cada resultado a 201 / 404 / 409 / 422.

## Riesgos y límites

- Los tests de integración necesitan PostgreSQL: se documentan dos caminos (Docker Compose o instalación local con `TEST_DATABASE_URL`).
- Sin Alembic todavía: el esquema se crea con `metadata.create_all` + DDL de la restricción; las migraciones versionadas quedan para C-07.
- Sin JWT todavía (C-08): la API no se despliega; sólo uso local.
- Fuera de alcance: bloqueos, cancelación, consulta de agenda, Redis y frontend (changes propios).

## Criterio de preparación

El proposal debe justificar la elección, el spec debe expresar cada escenario como DADO / CUANDO / ENTONCES y el design debe fijar la restricción de exclusión, el manejo transaccional y el mapeo de errores HTTP.
