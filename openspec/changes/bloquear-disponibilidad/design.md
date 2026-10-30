# Design

## Context

Véanse `proposal.md` y los dos delta specs de este change para el contrato. C-01b ya tiene `Turno`, `verificar_disponibilidad`, `CrearTurno`, unidad de trabajo SQLAlchemy, `CHECK (fin > inicio)` y exclusiones GiST para turno contra turno. C-02 agregó lectura de agenda, pero no bloqueos. La KB define RN-DA-02, RN-DI-01, RN-DI-04 y US-003; `knowledge-base/10_preguntas_abiertas.md` deja sin acuerdo la resolución de bloqueos que cruzan turnos existentes. La reprogramación se implementará en C-04 y la autenticación en C-08.

## Goals / Non-Goals

**Goals:**

- Mantener las reglas de disponibilidad en dominio/aplicación y la API como traductor HTTP.
- Conservar la atomicidad de turno más historial; persistir un bloqueo entero o nada.
- Evitar carreras turno contra bloqueo entre los dos casos de uso soportados, sin imponer una política de conflicto entre bloqueos que la KB no define.
- Mantener la implementación íntegramente síncrona y compatible con las fixtures PostgreSQL existentes.

**Non-Goals:**

- Resolver clínicamente un turno previo mediante cancelación, reubicación o aviso; la política provisional es rechazar el bloqueo.
- Implementar `PATCH` de reprogramación, control de roles, historial de bloqueos o consulta de bloqueos por un endpoint nuevo.
- Garantizar la relación cruzada turno-bloqueo frente a escrituras SQL directas que eviten los casos de uso; los controles entre tablas se ejercen en las operaciones soportadas.

## Decisions

### 1. Modelo de dominio y error conservador

Agregar `BloqueoDeDisponibilidad` en Python puro con `id`, `profesional_id: str | None`, `box_id: str | None`, `inicio`, `fin` y `motivo: str | None`. Su construcción comprueba exactamente un recurso, instantes con zona y `fin > inicio`. Una función de dominio compara intervalos semiabiertos y distingue conflicto por bloqueo del profesional y del box para el alta de turno. `CrearBloqueo` rechaza un turno activo intersectante con `conflicto_turno_existente`, sin cancelarlo ni tocar su historial. Esto adopta la opción conservadora para C-03 porque la política clínica está abierta en la KB; deberá revisarse con el responsable antes de admitir otra conducta. Alternativa descartada: cancelar automáticamente el turno, que introduce una transición y consentimiento no definidos por C-03.

### 2. Tabla y repositorio de bloqueos

Agregar `bloqueos_disponibilidad` con ID de texto de hasta 64 caracteres, `profesional_id` y `box_id` anulables con FKs a sus tablas, `inicio`/`fin` `TIMESTAMPTZ` obligatorios y `motivo` opcional. Un `CHECK` XOR exige exactamente una FK y otro exige `fin > inicio`. Crear índices útiles para buscar por recurso e intervalo; conservar `btree_gist` y las exclusiones GiST existentes de `turnos`, sin agregar una exclusión entre bloqueos. El adaptador SQLAlchemy consulta turnos activos intersectantes antes de insertar un bloqueo; varios bloqueos del mismo recurso pueden superponerse. Traducir únicamente nombres de constraints conocidos a errores de dominio, conservando otros errores de integridad como fallos inesperados. Alternativa descartada: `tipo_recurso`/`recurso_id` polimórficos, que perderían FKs reales hacia profesionales y boxes.

### 3. Serialización transaccional de recursos compartidos

`CrearTurno` puede consultar primero la existencia de paciente, profesional, box y prestación; antes de leer conflictos de disponibilidad o insertar, `CrearTurno` y `CrearBloqueo` adquieren bloqueos de fila `SELECT ... FOR UPDATE` sobre los recursos afectados dentro de la misma unidad de trabajo. Para un turno se toma primero la fila de profesional y después la de box; un bloqueo toma la fila de su único recurso. Ese orden fijo evita ciclos de espera entre altas que comparten ambos recursos. Usar el aislamiento PostgreSQL `READ COMMITTED`: tras esperar el bloqueo de fila, cada sentencia posterior obtiene una vista nueva y lee el turno o bloqueo que la primera transacción confirmó. La lectura de conflictos ocurre **después** de adquirir el bloqueo, nunca antes. El puerto de recursos expone una operación explícita de bloqueo; los dobles de pruebas registran esa llamada. Se comprueba con sesiones PostgreSQL separadas y coordinación determinista de hilos, tanto por profesional como por box y con ambos órdenes de llegada. [PostgreSQL 17](https://www.postgresql.org/docs/17/explicit-locking.html) documenta la espera de `FOR UPDATE` hasta el fin de la transacción. La regla de negocio proviene de la KB.

Las exclusiones existentes sólo comparan filas de `turnos` entre sí. La garantía cruzada turno-bloqueo depende de que ambas escrituras pasen por los casos de uso y su protocolo de bloqueo. Una inserción SQL directa de bloqueo contra turno queda fuera del contrato de integridad cruzada de C-03, y se documenta expresamente.

### 4. Puertos, caso de uso y transacciones

Extender `UnidadDeTrabajo` con repositorio de bloqueos y método de bloqueo de recursos. `CrearTurno` mantiene su validación de recursos, cálculo de duración, comprobación de turnos y escritura atómica, añadiendo el bloqueo de filas antes de leer conflictos y la comprobación de bloqueos de ambos recursos. `CrearBloqueo` verifica el recurso, bloquea su fila, consulta turnos activos de ese recurso, inserta y confirma una única vez. No rechaza por otros bloqueos, aunque sus intervalos se superpongan. Un error antes del commit revierte automáticamente y no crea historial. El puerto queda disponible para C-04, que deberá usar el mismo orden de bloqueo al reprogramar. Alternativa descartada: comprobar sólo desde el router, que no protege otros canales ni una carrera entre requests.

### 5. Contrato HTTP

El router síncrono `POST /api/v1/bloqueos` usa esquemas Pydantic separados del modelo SQLAlchemy; `AwareDatetime` impide fechas sin zona, `extra="forbid"` evita parámetros inesperados y una validación de modelo exige exactamente uno entre `profesional_id` y `box_id`. La respuesta `201` incluye ID generado, recurso, intervalo normalizado a UTC y motivo. Un recurso inexistente devuelve `404`; sólo el conflicto con turno activo devuelve `409`; recurso mal seleccionado, intervalo inválido o fecha mal formada devuelve `422`. Los conflictos de un nuevo turno por bloqueo usan códigos `conflicto_bloqueo_profesional` o `conflicto_bloqueo_box`, coherentes con la prioridad profesional → box de las validaciones actuales. No se envían datos reales de pacientes ni secretos en ejemplos. La ruta permanece de uso local hasta C-08.

## Risks / Trade-offs

- [Carrera entre tablas sin constraint cruzado] → bloqueo de filas compartido en ambos casos de uso y prueba concurrente real; documentar la limitación de SQL directo.
- [Interbloqueo por varios recursos] → orden profesional antes de box en todas las operaciones que tomen ambos.
- [Bloqueo que cruza un turno existente] → `409`, sin mutación; la política clínica definitiva sigue abierta y puede requerir otro change.
- [Esquema existente en desarrollo] → `create_all` agrega la tabla; no sustituye una migración versionada, prevista en C-07.
- [Pruebas de integración sin PostgreSQL] → usar Docker Compose y `TEST_DATABASE_URL` de la base descartable antes de archivar.

## Migration Plan

Agregar tabla y constraints al esquema creado por `Base.metadata.create_all`; en el entorno local ya existente, `create_all` añade la tabla sin alterar `turnos`. Ejecutar la suite completa contra PostgreSQL 17 antes de desplegar. Revertir la ruta y componentes de aplicación si hubiera que deshabilitar la función; cualquier bloqueo ya registrado debe conservarse/exportarse antes de retirar la tabla. Una migración de producción versionada se tratará en C-07.

## Open Questions

- ¿Qué acción clínica debería permitir en el futuro un bloqueo que cruce un turno previamente confirmado? C-03 conserva el rechazo provisional sin modificar reservas.
- ¿Necesitará recepción consultar o listar bloqueos desde una vista futura de agenda? C-03 sólo publica el alta.
