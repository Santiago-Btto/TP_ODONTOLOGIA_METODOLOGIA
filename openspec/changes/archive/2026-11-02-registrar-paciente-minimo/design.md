# Design

## Context

En el estado actual del proyecto (`C-01b` a `C-16`), la entidad `Paciente` en `backend/app/domain/turnos.py` sólo posee `id: str` y `nombre_mostrado: str`, y `PacienteModelo` en `backend/app/infrastructure/modelos.py` mapea únicamente esas dos columnas en la tabla `pacientes`. Los turnos referencian `paciente_id` y validan su existencia mediante `RepositorioRecursos.paciente(id_)`, pero la API carece de endpoints para dar de alta o buscar pacientes: dependía de semillas precargadas (`backend/app/infrastructure/semillas.py`).

Para habilitar el formulario de alta y selección de paciente en la agenda web (`C-15`) y el flujo completo en Docker Compose (`C-06`), el cambio `C-17` incorpora el alta y la búsqueda de pacientes bajo las restricciones de `04_modelo_de_datos.md` §Paciente, `09_decisiones_y_supuestos.md` §DD-04 y `10_preguntas_abiertas.md`:
- Gobernanza **ALTO (datos personales)**: minimizar los atributos persistidos a `id`, `nombre_mostrado` y `contacto` opcional; prohibir campos clínicos (`historia_clinica`, `odontograma`, `diagnostico`) o identificadores filiatorios adicionales (`dni`, `obra_social`, etc.) aún no acordados; usar exclusivamente datos manifiestamente ficticios (`"Paciente Demo ..."`).

## Goals / Non-Goals

**Goals:**
- Extender `Paciente` y `PacienteModelo` con `contacto: str | None = None` manteniendo compatibilidad total con los casos de uso y tests existentes (`C-01b`..`C-16`).
- Validar en el dominio las invariantes de `Paciente` (`id` y `nombre_mostrado` no vacíos tras `strip()`, normalización de `contacto` vacío a `None`) y tipificar errores de negocio (`DatosPacienteInvalidosError` → `422`, `PacienteDuplicadoError` → `409`).
- Proveer los casos de uso síncronos `RegistrarPaciente` y `BuscarPacientes` desacoplados mediante el puerto `RepositorioPacientes`.
- Proteger `POST /api/v1/pacientes` y `GET /api/v1/pacientes` con JWT y RBAC (`Permiso.REGISTRAR_PACIENTE` y `Permiso.CONSULTAR_PACIENTES` para `recepcion` y `responsable`) y rechazar cualquier campo extra con `ConfigDict(extra="forbid")`.

**Non-Goals:**
- Historia clínica, odontograma, evoluciones, adjuntos, DNI, fecha de nacimiento u obra social (excluidos expresamente por `DD-04` y `C-13`).
- Edición (`PATCH`/`PUT`) o baja física/lógica (`DELETE`) de pacientes en este change.
- Envío de mensajes reales al `contacto` del paciente (la integración externa real corresponde a `C-10`).

## Decisions

### 1. Modelo de dominio `Paciente` con normalización e invariantes en `__post_init__`
- **Decisión**: Extender `@dataclass(frozen=True) class Paciente` en `backend/app/domain/turnos.py` con `contacto: str | None = None`. En `__post_init__`, recortar espacios extremos (`strip()`) de `id`, `nombre_mostrado` y `contacto`; si `id` o `nombre_mostrado` quedan vacíos, lanzar `DatosPacienteInvalidosError(ErrorDeDominio)` (`codigo = "datos_paciente_invalidos"`, mapeado a HTTP `422`). Si `contacto` es cadena vacía o de solo espacios, normalizarlo a `None`.
- **Alternativa descartada**: Validar sólo en Pydantic (`PacienteEntrada`). Se descartó porque las reglas del proyecto exigen que las invariantes de entidad vivan también en la capa de dominio en Python puro.

### 2. Detección de duplicados por `id` y por `contacto` normalizado (`409 Conflict`)
- **Decisión**: Definir `PacienteDuplicadoError(ErrorDeDominio)` (`codigo = "paciente_duplicado"`, mapeado a HTTP `409`). Un paciente se considera duplicado si:
  1. Se indica un `id` que ya existe en `pacientes`, o
  2. Se indica un `contacto` no nulo cuyo valor normalizado (`lower().strip()`) ya está asociado a otro paciente registrado.
  Además de la verificación en el caso de uso `RegistrarPaciente`, `PacientesSQLAlchemy` traducirá cualquier `IntegrityError` de clave primaria o índice único funcional/columna sobre `pacientes` a `PacienteDuplicadoError`. Cuando `id` se omita en el alta, el caso de uso generará un identificador único (`f"paciente-{uuid4().hex[:12]}"` o `uuid4()`).
- **Alternativa descartada**: Hacer único a `nombre_mostrado`. Dos pacientes distintos pueden compartir nombre mostrado en una clínica, mientras que `id` y un `contacto` explícito actúan como claves naturales de desambiguación en recepción.

### 3. Puerto `RepositorioPacientes` en `UnidadDeTrabajo` y búsqueda insensible a mayúsculas
- **Decisión**: Definir `RepositorioPacientes(Protocol)` en `backend/app/application/puertos.py` con:
  - `obtener(id_: str) -> Paciente | None`
  - `obtener_por_contacto(contacto: str) -> Paciente | None`
  - `agregar(paciente: Paciente) -> None`
  - `buscar(consulta: str | None = None) -> list[Paciente]`
  Exponer `pacientes: RepositorioPacientes` dentro de `UnidadDeTrabajo` (y mantener `RecursosSQLAlchemy.paciente(id_)` devolviendo `Paciente(fila.id, fila.nombre_mostrado, fila.contacto)` para no romper ningún caso de uso previo). En `PacientesSQLAlchemy.buscar`, aplicar `ILIKE` sobre `nombre_mostrado`, `id` y `contacto` cuando `consulta` no esté vacía, ordenando siempre por `PacienteModelo.nombre_mostrado.asc(), PacienteModelo.id.asc()`.
- **Alternativa descartada**: Crear una sesión suelta fuera de `UnidadDeTrabajo` sólo para el alta. Integrarlo en `UnidadDeTrabajo` mantiene el mismo patrón transaccional que `turnos`, `bloqueos` y `recordatorios`.

### 4. Rechazo estricto de campos clínicos o no permitidos (`extra="forbid"`) y RBAC
- **Decisión**: Definir `PacienteEntrada(BaseModel)` con `model_config = ConfigDict(extra="forbid")`, aceptando únicamente `id: str | None = Field(default=None, min_length=1, max_length=64)`, `nombre_mostrado: str = Field(min_length=1, max_length=200)` y `contacto: str | None = Field(default=None, max_length=200)`. Cualquier payload con `dni`, `obra_social`, `historia_clinica`, `odontograma`, etc. es rechazado automáticamente con HTTP `422 Unprocessable Entity` antes de tocar la base.
- En `backend/app/domain/autorizacion.py`, agregar `Permiso.REGISTRAR_PACIENTE = "registrar_paciente"` y `Permiso.CONSULTAR_PACIENTES = "consultar_pacientes"`. Como `PERMISOS_POR_ROL[Rol.RECEPCION]` y `PERMISOS_POR_ROL[Rol.RESPONSABLE]` contienen `frozenset(Permiso)` y `Rol.ODONTOLOGO` sólo contiene `{Permiso.CONSULTAR_AGENDA}`, recepción y responsable quedan habilitados y odontólogo/a recibe `403` (`acceso_denegado`), alineado con `03_actores_y_roles.md` (odontólogo/a sólo consulta su propia agenda).

## Risks / Trade-offs

- **[Riesgo] Ingreso accidental de datos reales en pruebas o semillas** → **Mitigación**: Todas las pruebas y `semillas.py` usarán nombres con el prefijo `"Paciente Demo ..."` y dominios `.invalid` o teléfonos ficticios `+54 9 11 0000-XXXX`.
- **[Riesgo] Ruptura de constructores posicionales `Paciente("id", "Nombre")` en los 363 tests existentes** → **Mitigación**: El nuevo campo `contacto: str | None = None` tiene valor por defecto `None` al final del dataclass `Paciente`, preservando el 100% de las llamadas posicionales y por palabra clave existentes.
