# Proposal

## Why

La sección D del informe de Discovery exige disponer de un registro mínimo de pacientes para que recepción pueda dar de alta y buscar destinatarios al asignar turnos desde la futura agenda web (`C-15`) y en el flujo integral del MVP (`C-06`), sin introducir historia clínica ni datos personales reales. Actualmente `Paciente` sólo existe como referencia precargada por identificador y `nombre_mostrado`, sin endpoints de alta ni búsqueda ni soporte para un dato de contacto opcional.

## What Changes

- **Extensión mínima de la entidad `Paciente`**:
  - Agregar el atributo opcional `contacto: str | None = None` a `Paciente` en el dominio (`backend/app/domain/turnos.py`) y la columna anulable `contacto: Mapped[str | None] = mapped_column(String(200), nullable=True)` en `PacienteModelo` (`backend/app/infrastructure/modelos.py`).
  - Validar en el dominio que `id` y `nombre_mostrado` (tras recortar espacios extremos) no estén vacíos (`DatosPacienteInvalidosError` → HTTP `422`), normalizando `contacto` en blanco a `None` y rechazando duplicados (`PacienteDuplicadoError` → HTTP `409`).
- **Casos de uso y puerto de pacientes (`backend/app/application/`)**:
  - Incorporar el puerto `RepositorioPacientes` (y su exposición en `UnidadDeTrabajo` y/o lector dedicado) para `obtener(id_)`, `agregar(paciente)` y `buscar(q: str | None = None) -> list[Paciente]`.
  - Implementar los casos de uso síncronos `RegistrarPaciente` (alta con `id` opcional autogenerado o explícito, `nombre_mostrado` obligatorio y `contacto` opcional) y `BuscarPacientes` (listado ordenado por `nombre_mostrado` e `id`, con filtro opcional `q` insensible a mayúsculas/minúsculas sobre `nombre_mostrado`, `id` o `contacto`).
- **Autorización RBAC y endpoints REST (`POST /api/v1/pacientes` y `GET /api/v1/pacientes`)**:
  - Añadir los permisos `Permiso.REGISTRAR_PACIENTE` y `Permiso.CONSULTAR_PACIENTES` en `backend/app/domain/autorizacion.py`, habilitados para `Rol.RECEPCION` y `Rol.RESPONSABLE` y denegados (`403`) para `Rol.ODONTOLOGO`.
  - Exponer `POST /api/v1/pacientes` (`201 Created`) y `GET /api/v1/pacientes` (`200 OK`) con validación estricta `ConfigDict(extra="forbid")` en `PacienteEntrada` para rechazar con `422` cualquier campo clínico o no permitido (`dni`, `obra_social`, `historia_clinica`, `odontograma`, `diagnostico`, etc., conforme a `DD-04`).
- **Semillas y pruebas con datos exclusivamente ficticios**:
  - Actualizar semillas y suites de pruebas por capa (`domain`, `application`, `infrastructure`, `api`) usando únicamente identidades y contactos manifiestamente ficticios (`"Paciente Demo ..."`).

## Capabilities

### New Capabilities
- `registro-de-pacientes`: Alta y búsqueda de pacientes con datos mínimos operativos (`id`, `nombre_mostrado` y `contacto` opcional), rechazo de duplicados, prohibición estricta de campos clínicos o no autorizados y control de acceso por rol.

### Modified Capabilities
<!-- No se modifican requisitos de capacidades existentes; la referencia `paciente_id` en turnos se mantiene compatible hacia atrás. -->

## Impact

- **Dominio**: `backend/app/domain/turnos.py` (`Paciente`, `DatosPacienteInvalidosError`, `PacienteDuplicadoError`), `backend/app/domain/autorizacion.py` (`Permiso.REGISTRAR_PACIENTE`, `Permiso.CONSULTAR_PACIENTES`).
- **Aplicación**: `backend/app/application/puertos.py` (`RepositorioPacientes`), `backend/app/application/pacientes.py` (`RegistrarPaciente`, `BuscarPacientes`, `NuevoPaciente`).
- **Infraestructura**: `backend/app/infrastructure/modelos.py` (`PacienteModelo.contacto`), `backend/app/infrastructure/unidad_de_trabajo.py` (`PacientesSQLAlchemy`, traducción de unicidad a `PacienteDuplicadoError`, actualización de `RecursosSQLAlchemy.paciente`), `backend/app/infrastructure/semillas.py`.
- **API**: `backend/app/api/pacientes.py` (`POST /api/v1/pacientes`, `GET /api/v1/pacientes`), `backend/app/api/esquemas.py` (`PacienteEntrada`, `PacienteSalida`), `backend/app/api/main.py` (registro de router y mapeo de errores `409`/`422`).
- **Pruebas**: Nuevas pruebas unitarias y de integración contra PostgreSQL real en `backend/tests/domain/test_pacientes.py`, `backend/tests/application/test_pacientes.py`, `backend/tests/infrastructure/test_pacientes_persistencia.py` y `backend/tests/api/test_pacientes_api.py`.
