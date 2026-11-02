# Tasks

## 1. Dominio y Autorización (TDD)

- [x] 1.1 Extender `Paciente` en `backend/app/domain/turnos.py` con `contacto: str | None = None`, normalización en `__post_init__` (`strip()` de `id`, `nombre_mostrado` y `contacto`, convirtiendo `contacto` vacío a `None`), e incorporar `DatosPacienteInvalidosError` (`codigo = "datos_paciente_invalidos"`) y `PacienteDuplicadoError` (`codigo = "paciente_duplicado"`), verificando con tests unitarios en `backend/tests/domain/test_pacientes.py`.
- [x] 1.2 Agregar `Permiso.REGISTRAR_PACIENTE` y `Permiso.CONSULTAR_PACIENTES` en `backend/app/domain/autorizacion.py` (habilitados para `recepcion` y `responsable` y denegados para `odontologo`), verificando con tests en `backend/tests/domain/test_autorizacion.py`.

## 2. Casos de Uso y Puerto de Pacientes (TDD)

- [x] 2.1 Definir el protocolo `RepositorioPacientes` (`obtener`, `obtener_por_contacto`, `agregar`, `buscar`) y exponer `pacientes: RepositorioPacientes` en `UnidadDeTrabajo` dentro de `backend/app/application/puertos.py`.
- [x] 2.2 Implementar `NuevoPaciente`, `RegistrarPaciente` (autogeneración de `id` cuando se omite, validación de duplicados por `id` y por `contacto` normalizado) y `BuscarPacientes` en `backend/app/application/pacientes.py`, verificando con tests unitarios en `backend/tests/application/test_pacientes.py`.

## 3. Persistencia SQLAlchemy y Semillas Ficticias (TDD)

- [x] 3.1 Agregar la columna anulable `contacto: Mapped[str | None] = mapped_column(String(200), nullable=True)` en `PacienteModelo` (`backend/app/infrastructure/modelos.py`) y actualizar `RecursosSQLAlchemy.paciente` para hidratar `contacto`.
- [x] 3.2 Implementar `PacientesSQLAlchemy` en `backend/app/infrastructure/unidad_de_trabajo.py` (e integrarlo en `UnidadDeTrabajoSQLAlchemy.pacientes` y `backend/app/infrastructure/repositorios.py`), incluyendo traducción de violaciones de unicidad a `PacienteDuplicadoError`, búsqueda `ILIKE` por `nombre_mostrado`, `id` y `contacto` y ordenamiento determinista, verificando contra PostgreSQL real en `backend/tests/infrastructure/test_pacientes_persistencia.py`.
- [x] 3.3 Actualizar `backend/app/infrastructure/semillas.py` con contactos manifiestamente ficticios (`+54 9 11 0000-0001`, `paciente.demo.002@example.invalid`) manteniendo compatibilidad con las pruebas existentes.

## 4. API FastAPI y Documentación (TDD)

- [x] 4.1 Definir `PacienteEntrada` (`ConfigDict(extra="forbid")`) y `PacienteSalida` en `backend/app/api/esquemas.py`, crear el router `backend/app/api/pacientes.py` (`POST /api/v1/pacientes` → `201` y `GET /api/v1/pacientes` → `200`) y registrarlo junto con el mapeo HTTP de `PacienteDuplicadoError` (`409`) y `DatosPacienteInvalidosError` (`422`) en `backend/app/api/main.py`, verificando con tests de integración en `backend/tests/api/test_pacientes_api.py` (alta válida, duplicado por id/contacto, búsqueda con y sin filtro `q`, rechazo `422` de campos clínicos/no permitidos como `historia_clinica`, `odontograma`, `dni` u `obra_social`, rechazo `401`/`403` por rol y creación posterior de un turno con el paciente dado de alta).
- [x] 4.2 Documentar los endpoints `/api/v1/pacientes` en `README.md` y verificar que la suite completa `pytest backend/tests` pase en verde contra PostgreSQL real.

## Workflow follow-up

- Archivar el change `registrar-paciente-minimo` (`openspec archive registrar-paciente-minimo --yes`), sincronizar la spec en `openspec/specs/registro-de-pacientes/spec.md` y actualizar `CHANGES.md` y `.active-orchestrator-state.json` una vez aprobada y verificada la implementación.
