# Tasks

## 1. Base del backend

- [ ] 1.1 Crear `backend/` con `requirements.txt`, `requirements-dev.txt`, `pyproject.toml` (configuración de pytest), `Dockerfile` y `.env.example`; agregar `docker-compose.yml` con `db` (PostgreSQL 17) y `api`.
- [ ] 1.2 Eliminar el núcleo TypeScript (`src/`, `test/`, `package.json`, `tsconfig.json`).

## 2. Dominio

- [ ] 2.1 Escribir tests de dominio: intervalo válido, fin igual/anterior al inicio, duración cero/negativa, solapamiento parcial, intervalo contenido, borde contiguo, conflicto tipado por profesional y por box.
- [ ] 2.2 Implementar `domain/turnos.py` y `domain/disponibilidad.py` hasta que 2.1 pase.

## 3. Caso de uso

- [ ] 3.1 Escribir tests de `CrearTurno` con una unidad de trabajo en memoria: alta exitosa con un único historial `creado`, conflicto por profesional, conflicto por box, reserva contigua, intervalo inválido, duración inválida y recurso inexistente; cada rechazo sin escrituras ni commit.
- [ ] 3.2 Implementar `application/puertos.py` y `application/crear_turno.py` hasta que 3.1 pase.

## 4. Persistencia PostgreSQL

- [ ] 4.1 Escribir tests de restricciones contra PostgreSQL: inserción directa solapada rechazada, inserción directa contigua aceptada, `CHECK (fin > inicio)`, y alta concurrente simulada (carrera) traducida a conflicto.
- [ ] 4.2 Implementar modelos SQLAlchemy, DDL de exclusión, `UnidadDeTrabajoSQLAlchemy` y semillas ficticias hasta que 4.1 pase.

## 5. API

- [ ] 5.1 Escribir tests de API: 201, 409 (`conflicto_profesional` y `conflicto_box`), 422 (`intervalo_invalido` y fecha sin zona), 404 (`recurso_inexistente`) y `GET /health`.
- [ ] 5.2 Implementar `api/main.py`, `api/turnos.py` y `api/esquemas.py` hasta que 5.1 pase.

## 6. Verificación y documentación

- [ ] 6.1 Ejecutar la suite completa contra PostgreSQL y registrar el resultado y la trazabilidad escenario → test.
- [ ] 6.2 Actualizar `README.md` con instalación y ejecución de tests (Docker Compose y local).
