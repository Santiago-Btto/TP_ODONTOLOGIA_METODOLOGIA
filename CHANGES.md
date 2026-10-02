# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **turnos-odontologia**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

---

## Cómo usar este documento

1. Identificar el change a implementar y verificar que sus dependencias están en `openspec/changes/archive/`.
2. Leer los documentos de `knowledge-base/` indicados en “Leer antes”.
3. Ejecutar `/opsx:propose <nombre-del-change>` para crear sus artefactos.
4. Implementar, verificar y archivar el change con `/opsx:archive <nombre-del-change>`.
5. Marcar el checkbox `[x]` de este archivo al cerrar el change archivado.

---

## Árbol de dependencias

```text
C-01 crear-turno-sin-solapamientos             ← primer change MVP
  ├── C-02 consultar-agenda
  ├── C-03 bloquear-disponibilidad
  │     └── C-04 reprogramar-turno-atomicamente
  ├── C-05 cancelar-y-confirmar-turnos
  └── C-06 ejecutar-flujo-mvp-local
        └── C-07 persistir-agenda-y-controlar-concurrencia
              ├── C-08 autenticar-y-autorizar-adaptadores
              │     ├── C-09 exponer-api-de-agenda
              │     │     ├── C-10 recordatorios-con-consentimiento
              │     │     ├── C-11 cobros-y-senas-integrados
              │     │     └── C-12 sincronizar-calendario-externo
              │     └── C-13 historia-clinica-y-odontograma
              └── C-14 auditoria-operativa-y-observabilidad
```

### Paralelismo por fase

> Cada gate marca una sincronización: los changes mostrados debajo pueden proponerse y ejecutarse en paralelo una vez archivadas sus dependencias.

```text
GATE 0: ninguna
  → C-01 crear-turno-sin-solapamientos         [Agente A]

GATE 1: C-01 ✓                                 ← FORK
  → C-02 consultar-agenda                       [Agente B]
  → C-03 bloquear-disponibilidad                [Agente A]
  → C-05 cancelar-y-confirmar-turnos            [Agente C]

GATE 2: C-01 + C-03 ✓
  → C-04 reprogramar-turno-atomicamente         [Agente A]

GATE 3: C-02 + C-03 + C-04 + C-05 ✓
  → C-06 ejecutar-flujo-mvp-local               [Agente B]

GATE 4: C-06 ✓
  → C-07 persistir-agenda-y-controlar-concurrencia [Agente A]

GATE 5: C-07 ✓                                 ← FORK, sujeto a decisiones abiertas
  → C-08 autenticar-y-autorizar-adaptadores     [Agente A]
  → C-14 auditoria-operativa-y-observabilidad   [Agente B]

GATE 6: C-08 ✓                                 ← FORK; C-09 también requiere C-07
  → C-09 exponer-api-de-agenda                  [Agente C]
  → C-13 historia-clinica-y-odontograma         [Agente B]

GATE 7: C-09 ✓                                 ← FORK; integraciones no son fuente de verdad
  → C-10 recordatorios-con-consentimiento       [Agente B]
  → C-11 cobros-y-senas-integrados              [Agente A]
  → C-12 sincronizar-calendario-externo         [Agente C]
```

### Camino crítico (6 changes — mínimo irreducible)

```text
C-01 → C-03 → C-04 → C-05 → C-06
```

El MVP ejecutable queda listo tras C-06; C-02 se implementa en paralelo y es requisito de completitud del MVP, aunque no alarga la cadena de dependencias. Los changes C-07 a C-14 son evolución posterior y no deben desplazar el núcleo de agenda.

### Plan óptimo con 3 agentes

| Paso | Agente A (Backend Core) | Agente B (Backend Aux) | Agente C (Frontend) |
|---|---|---|---|
| 1 | C-01 crear-turno-sin-solapamientos | — | — |
| 2 | C-03 bloquear-disponibilidad | C-02 consultar-agenda | C-05 cancelar-y-confirmar-turnos |
| 3 | C-04 reprogramar-turno-atomicamente | — | — |
| 4 | — | C-06 ejecutar-flujo-mvp-local | — |
| 5 | C-07 persistir-agenda-y-controlar-concurrencia | — | — |
| 6 | C-08 autenticar-y-autorizar-adaptadores | C-14 auditoria-operativa-y-observabilidad | — |
| 7 | — | C-13 historia-clinica-y-odontograma | C-09 exponer-api-de-agenda |
| 8 | C-11 cobros-y-senas-integrados | C-10 recordatorios-con-consentimiento | C-12 sincronizar-calendario-externo |

---

## FASE 0 — Núcleo determinista del MVP

### [C-01] `crear-turno-sin-solapamientos`
- **Estado**: `[x]` completado y archivado en `openspec/changes/archive/2026-10-01-crear-turno-sin-solapamientos/`
- **Scope**: Entregar el primer vertical slice del MVP como módulo Node.js/TypeScript, sin UI, HTTP, cuentas externas ni dependencias de terceros.
  - Configurar `package.json`, `tsconfig.json`, scripts de compilación y `node:test`; crear la estructura `src/domain`, `src/application`, `src/infrastructure/in-memory` y `test/`.
  - Modelos: `Paciente`, `Profesional`, `Box`, `Prestacion`, `Turno`, `HistorialDeCambio` y `EstadoTurno`; rechazar duraciones no positivas, recursos ausentes y datos de prueba no ficticios.
  - Implementar repositorios en memoria y el servicio puro de disponibilidad con la intersección semiabierta `[inicio, fin)`, para admitir turnos contiguos.
  - Caso de uso `CrearTurno`: calcular `fin` desde la prestación o validar el fin recibido, reservar simultáneamente profesional y box y persistir el historial `creado` sólo tras validar ambos recursos.
  - Tests TDD: alta válida, conflicto por profesional, conflicto por box, turnos contiguos, intervalo inválido y duración inválida; comprobar que un rechazo no deja reservas ni historial parcial.
- **Dependencias**: ninguna
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance v0.1 — MVP de dominio ejecutable
  - `knowledge-base/02_descripcion_general.md` §Stack tecnológico y Arquitectura general
  - `knowledge-base/04_modelo_de_datos.md` §Entidades y Seed data inicial
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DA y RN-DI
  - `knowledge-base/08_arquitectura_propuesta.md` §Patrones aplicados

---

## FASE 1 — Operación local de la agenda

### [C-02] `consultar-agenda`
- **Estado**: `[ ]` pendiente
- **Scope**: Incorporar consulta determinista de agenda sobre el núcleo en memoria.
  - Caso de uso `ConsultarAgenda` con filtros obligatorios de rango y filtros opcionales por `profesionalId` y `boxId`.
  - Definir DTO de salida que identifique turno, profesional, box, prestación, intervalo y estado, sin presentar UI ni exponer datos personales reales.
  - Ordenar resultados por inicio y documentar el criterio de inclusión de intervalos que intersectan el rango consultado.
  - Tests: agenda diaria por profesional, agenda semanal por box, filtro combinado, rango vacío y exclusión de datos que no intersectan.
- **Dependencias**: C-01
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Alcance v0.1
  - `knowledge-base/04_modelo_de_datos.md` §Turno
  - `knowledge-base/06_funcionalidades.md` §US-002 — Consultar agenda
  - `knowledge-base/07_flujos_principales.md` §Flujo 1

### [C-03] `bloquear-disponibilidad`
- **Estado**: `[ ]` pendiente
- **Scope**: Añadir bloqueos de profesional o box que participen de la misma validación de disponibilidad.
  - Modelo y repositorio en memoria `BloqueoDeDisponibilidad` con `recursoTipo`, `recursoId`, intervalo válido y motivo opcional.
  - Caso de uso `BloquearDisponibilidad` que valide recurso e intervalo y persista el bloqueo sin reinterpretar los turnos existentes.
  - Extender el servicio de disponibilidad para rechazar altas y reprogramaciones que intersecten un bloqueo de cualquiera de los dos recursos.
  - Definir error explícito para el caso pendiente de bloqueo que se solapa con un turno existente; no inventar política de resolución.
  - Tests: bloqueo de profesional, bloqueo de box, bordes contiguos válidos, alta/reprogramación rechazada por bloqueo y persistencia inalterada ante un bloqueo inválido.
- **Dependencias**: C-01
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §BloqueoDeDisponibilidad
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DA-02 y RN-DI-04
  - `knowledge-base/06_funcionalidades.md` §US-003 — Bloquear disponibilidad
  - `knowledge-base/07_flujos_principales.md` §Flujo 4
  - `knowledge-base/10_preguntas_abiertas.md` §Preguntas abiertas (Media)

### [C-04] `reprogramar-turno-atomicamente`
- **Estado**: `[ ]` pendiente
- **Scope**: Implementar cambio de horario y/o recursos como operación atómica.
  - Caso de uso `ReprogramarTurno` que recupere el turno, construya el candidato y lo excluya de su propia comparación.
  - Validar el candidato contra turnos activos y bloqueos del profesional y box nuevos antes de modificar cualquier repositorio.
  - Reemplazar intervalo, profesional o box sólo si pasa la validación; registrar `HistorialDeCambio` con resúmenes antes y después.
  - Devolver errores de turno inexistente y turno cancelado como comportamiento explícito, dejando señalada la política pendiente cuando corresponda.
  - Tests: cambio válido, conflicto por profesional, conflicto por box, bloqueo, autoexclusión, y fallo atómico que conserva el turno e historial previos.
- **Dependencias**: C-01, C-03
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Turno y HistorialDeCambio
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DI-02 a RN-DI-04 y RN-TU-02
  - `knowledge-base/06_funcionalidades.md` §US-004 — Reprogramar un turno
  - `knowledge-base/07_flujos_principales.md` §Flujo 2
  - `knowledge-base/10_preguntas_abiertas.md` §Preguntas abiertas (Media)

### [C-05] `cancelar-y-confirmar-turnos`
- **Estado**: `[ ]` pendiente
- **Scope**: Completar los cambios básicos de estado sin ampliar la política de autorización.
  - Casos de uso `CancelarTurno` y `ConfirmarTurno` con transiciones explícitas para los estados acordados del MVP.
  - Hacer que la disponibilidad ignore un turno cancelado, conservando el turno y agregando historial `cancelado` o `confirmado`.
  - Mantener la confirmación como cambio de estado; cualquier cambio simultáneo de horario o recurso debe delegar en la validación de reprogramación.
  - Exponer errores para turno inexistente y transición no permitida, sin asumir ventana de cancelación ni actor autorizado.
  - Tests: cancelar libera el intervalo, confirmar conserva la reserva, ambos eventos escriben historial y las transiciones inválidas no alteran estado.
- **Dependencias**: C-01
- **Governance**: MEDIO
- **Leer antes**:
  - `knowledge-base/04_modelo_de_datos.md` §Turno y HistorialDeCambio
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU
  - `knowledge-base/06_funcionalidades.md` §US-005 — Cancelar y confirmar
  - `knowledge-base/07_flujos_principales.md` §Flujo 3
  - `knowledge-base/10_preguntas_abiertas.md` §Quién puede cancelar o confirmar

### [C-06] `ejecutar-flujo-mvp-local`
- **Estado**: `[ ]` pendiente
- **Scope**: Ensamblar el MVP local verificable sin añadir UI ni integración externa.
  - Crear composición en `src/index.ts` y un adaptador de línea de comandos mínimo para ejecutar comandos ficticios de crear, consultar, bloquear, reprogramar, cancelar y confirmar.
  - Inyectar repositorios en memoria y exponer contratos de casos de uso sin duplicar reglas de disponibilidad en el adaptador.
  - Incorporar fixtures reproducibles con pacientes, profesionales, boxes y prestaciones manifiestamente ficticios.
  - Añadir prueba de aceptación de flujo E2E local: alta, consulta, bloqueo, rechazo por conflicto, reprogramación, cancelación y reutilización del horario.
  - Documentar comandos locales, versión LTS de Node fijada y la garantía de no requerir `.env`, UI, API ni cuentas externas.
- **Dependencias**: C-02, C-03, C-04, C-05
- **Governance**: BAJO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Métricas de éxito y Fuera de alcance
  - `knowledge-base/02_descripcion_general.md` §Arquitectura general
  - `knowledge-base/07_flujos_principales.md` §Flujos 1 a 4
  - `knowledge-base/08_arquitectura_propuesta.md` §Estructura de directorios y Seguridad
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-02 y DD-04

---

## FASE 2 — Evolución segura antes de exponer canales

### [C-07] `persistir-agenda-y-controlar-concurrencia`
- **Estado**: `[ ]` pendiente
- **Scope**: Sustituir la persistencia en memoria sólo tras definir escala y privacidad, manteniendo la autoridad del dominio.
  - Acordar y versionar decisión de clínica/sucursal, esquema de datos mínimos ficticios o política aprobada para datos reales, retención y exportación.
  - Implementar adaptadores de repositorio persistente y migraciones para agenda, bloqueos e historial, sin modificar los contratos de casos de uso.
  - Garantizar exclusión de concurrencia para profesional y box mediante transacciones y restricciones compatibles con el motor seleccionado.
  - Diseñar migración y respaldo reversible; verificar que una falla no genere doble reserva ni historial parcial.
  - Tests de integración: dos altas concurrentes al mismo recurso, reinicio/persistencia, aislamiento definido y rollback ante conflicto.
- **Dependencias**: C-06
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Persistencia
  - `knowledge-base/04_modelo_de_datos.md` §Entidades e Índice lógico
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DI-01 a RN-DI-05
  - `knowledge-base/09_decisiones_y_supuestos.md` §SU-02
  - `knowledge-base/10_preguntas_abiertas.md` §Prioridad Alta

### [C-08] `autenticar-y-autorizar-adaptadores`
- **Estado**: `[ ]` pendiente
- **Scope**: Incorporar identidad y autorización a adaptadores futuros sólo después de validar la matriz operativa.
  - Validar quién puede crear, reprogramar, cancelar, confirmar, bloquear y consultar antes de codificar una política de permisos.
  - Modelos y almacenamiento: `Usuario`, `Rol`, asignaciones y sesiones/credenciales según el mecanismo elegido, sin secretos embebidos.
  - Implementar middleware o puerto de identidad para que los adaptadores soliciten autorización y los casos de uso reciban actor trazable.
  - Ampliar `HistorialDeCambio.actorId` sólo bajo la política de datos aprobada.
  - Tests: permisos por rol, acceso denegado, revocación de sesión y trazabilidad del actor sin filtrar datos sensibles.
- **Dependencias**: C-07
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/03_actores_y_roles.md` §RBAC — Matriz de permisos propuesta
  - `knowledge-base/04_modelo_de_datos.md` §HistorialDeCambio
  - `knowledge-base/05_reglas_de_negocio.md` §RN-TU y RN-EX-03
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad
  - `knowledge-base/10_preguntas_abiertas.md` §Quién puede operar y privacidad

### [C-14] `auditoria-operativa-y-observabilidad`
- **Estado**: `[ ]` pendiente
- **Scope**: Preparar trazabilidad y operación de producción sin convertir los logs en una historia clínica paralela.
  - Definir eventos de auditoría mínimos para cambios de agenda, bloqueos y accesos, con correlación y actor autorizado.
  - Implementar logs estructurados, métricas de conflicto y alertas de errores de disponibilidad sin incluir PII ni contenido clínico.
  - Establecer retención, acceso y exportación de auditoría conforme a la política aprobada; separar historial funcional de telemetría.
  - Crear runbook de restauración, incidentes de doble reserva y revisión de accesos.
  - Tests: redacción de datos sensibles, correlación de un cambio y ausencia de duplicación de eventos ante reintentos.
- **Dependencias**: C-07
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Métricas de éxito
  - `knowledge-base/04_modelo_de_datos.md` §HistorialDeCambio
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-04
  - `knowledge-base/10_preguntas_abiertas.md` §Retención y exportación

---

## FASE 3 — Canales e integraciones posteriores al MVP

### [C-09] `exponer-api-de-agenda`
- **Estado**: `[ ]` pendiente
- **Scope**: Publicar un adaptador HTTP versionado que delegue exclusivamente en los casos de uso existentes.
  - Definir contrato OpenAPI y endpoints autenticados para turnos, agenda y bloqueos; no exponer una ruta pública de reserva sin diseño específico.
  - Mapear validaciones y errores de dominio a respuestas consistentes sin recalcular disponibilidad en controladores.
  - Aplicar autorización, rate limiting, validación de entrada y redacción de datos según el rol.
  - Crear pruebas de contrato, integración de autorización y regresión de conflictos de profesional/box a través del adaptador.
  - Documentar versionado, idempotencia de comandos y estrategia de errores/reintentos.
- **Dependencias**: C-07, C-08
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §API REST
  - `knowledge-base/03_actores_y_roles.md` §Rutas públicas
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DI-05 y RN-EX-02
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad
  - `knowledge-base/09_decisiones_y_supuestos.md` §DD-03

### [C-10] `recordatorios-con-consentimiento`
- **Estado**: `[ ]` pendiente
- **Scope**: Agregar recordatorios como adaptador saliente, no como fuente de verdad de la agenda.
  - Definir canal, consentimiento, contenido, opt-out y retención antes de incorporar credenciales de mensajería.
  - Crear puerto `NotificadorDeTurnos`, cola/reintentos idempotentes y adaptador de proveedor aislado por configuración segura.
  - Emitir solicitudes de notificación sólo después de una transición persistida; los mensajes nunca crean ni cambian turnos directamente.
  - Registrar estado técnico mínimo de entrega sin incluir información clínica ni secretos.
  - Tests: consentimiento ausente, idempotencia, reintento, fallo del proveedor y operación de agenda independiente del proveedor.
- **Dependencias**: C-07, C-08, C-09
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Integraciones externas
  - `knowledge-base/05_reglas_de_negocio.md` §RN-EX-02 y RN-EX-03
  - `knowledge-base/08_arquitectura_propuesta.md` §Variables de entorno y Seguridad
  - `knowledge-base/10_preguntas_abiertas.md` §Canal de recordatorio y consentimiento

### [C-11] `cobros-y-senas-integrados`
- **Estado**: `[ ]` pendiente
- **Scope**: Diseñar y conectar señas/pagos sólo con reglas financieras y legales aprobadas.
  - Acordar importes, reintegros, ventana de cancelación, conciliación y efectos de un pago fallido antes de escribir flujo de cobro.
  - Crear agregado/puerto de pago, estados de seña y webhooks autenticados con verificación de firma e idempotencia.
  - Mantener la disponibilidad y el ciclo de vida de turno en el dominio; un webhook sólo solicita una transición definida y auditada.
  - Gestionar secretos mediante proveedor seguro y separar tokens/identificadores de datos de pacientes.
  - Tests: firma inválida, webhook duplicado, pago rechazado, reintegro y conservación de la agenda ante falla del proveedor.
- **Dependencias**: C-07, C-08, C-09
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Mercado Pago
  - `knowledge-base/05_reglas_de_negocio.md` §RN-EX-03
  - `knowledge-base/08_arquitectura_propuesta.md` §Variables de entorno
  - `knowledge-base/10_preguntas_abiertas.md` §Señas y reintegros

### [C-12] `sincronizar-calendario-externo`
- **Estado**: `[ ]` pendiente
- **Scope**: Añadir sincronización externa subordinada al dominio de agenda.
  - Acordar dirección de sincronización, propiedad de eventos y resolución de conflictos antes de conectar un proveedor.
  - Crear puerto de calendario, mapeo de eventos y cola idempotente para altas, cambios y cancelaciones confirmadas localmente.
  - Guardar credenciales cifradas o delegadas a un gestor de secretos; nunca en repositorio ni en fixtures.
  - Reconciliar fallas sin aceptar cambios externos que el dominio no haya validado para profesional y box.
  - Tests: evento duplicado, conflicto externo, fallo de red, cancelación y no creación de solapamientos desde el adaptador.
- **Dependencias**: C-07, C-08, C-09
- **Governance**: ALTO
- **Leer antes**:
  - `knowledge-base/02_descripcion_general.md` §Google Calendar
  - `knowledge-base/05_reglas_de_negocio.md` §RN-DI-05 y RN-EX-02
  - `knowledge-base/08_arquitectura_propuesta.md` §Variables de entorno
  - `knowledge-base/10_preguntas_abiertas.md` §Google Calendar y conflictos de sincronización

---

## FASE 4 — Información clínica, sólo con marco aprobado

### [C-13] `historia-clinica-y-odontograma`
- **Estado**: `[ ]` pendiente
- **Scope**: Incorporar historia clínica y odontograma como dominio separado, una vez validadas obligaciones legales, seguridad y consentimiento.
  - Definir datos clínicos mínimos, consentimiento, roles, retención, exportación, borrado y respuesta a incidentes con responsables habilitados.
  - Modelos y migraciones: `HistoriaClinica`, entradas clínicas y estructura de odontograma con separación estricta de la agenda.
  - Aplicar control de acceso por rol, cifrado en tránsito/en reposo según la decisión técnica, y auditoría inmutable de lectura/escritura.
  - Vincular el paciente sólo mediante identificadores necesarios; no introducir datos reales en repositorio, pruebas o semillas.
  - Tests de seguridad y privacidad: denegación por rol, trazabilidad, retención, redacción de logs y aislamiento entre clínicas si aplica.
- **Dependencias**: C-07, C-08
- **Governance**: CRITICO
- **Leer antes**:
  - `knowledge-base/01_vision_y_objetivos.md` §Fuera de alcance
  - `knowledge-base/03_actores_y_roles.md` §Actores del sistema
  - `knowledge-base/04_modelo_de_datos.md` §Paciente
  - `knowledge-base/08_arquitectura_propuesta.md` §Seguridad
  - `knowledge-base/10_preguntas_abiertas.md` §Datos de paciente, consentimiento y retención
