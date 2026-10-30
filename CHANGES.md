# CHANGES — Secuencia de Implementación

> Índice canónico de todos los changes del proyecto **turnos-odontologia**.
> Cada change es atómico: un agente puede implementarlo en una sesión (~4-6 horas).
> **Leer este archivo antes de ejecutar cualquier `/opsx:propose`.**

> **Ajustar (2026-10-08).** El roadmap original asumía Node.js + TypeScript en memoria y difería la persistencia, la API y la autenticación a fases posteriores. Se corrigió para (1) adoptar el stack definido (FastAPI, SQLAlchemy, PostgreSQL, JWT, Redis, Docker Compose; React + TypeScript + Vite), (2) incorporar al MVP los ítems imprescindibles de la sección D del Discovery que no tenían change —datos mínimos de paciente (C-17) y recordatorio simulado (C-16)— y (3) corregir el camino crítico, que incluía a C-05 aunque éste sólo depende del primer change.

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
C-01  crear-turno-sin-solapamientos               ← archivado (stack anterior, Node.js)
  └── C-01b crear-turno-sin-solapamientos-fastapi ← reimplementación en el stack definido
        ├── C-02 consultar-agenda
        │     └── C-15 agenda-web-react  (también requiere C-08 y C-17)
        ├── C-03 bloquear-disponibilidad
        │     └── C-04 reprogramar-turno-atomicamente
        ├── C-05 cancelar-y-confirmar-turnos
        ├── C-08 autenticar-con-jwt
        ├── C-16 recordatorio-simulado-con-redis
        ├── C-17 registrar-paciente-minimo
        └── C-06 flujo-mvp-docker-compose   (requiere C-02, C-04, C-05, C-15, C-16, C-17)
              └── C-07 migraciones-y-respaldo
                    ├── C-14 auditoria-operativa-y-observabilidad
                    └── C-09 endurecer-api-publicable
                          ├── C-10 recordatorios-whatsapp-con-consentimiento
                          ├── C-11 cobros-y-senas-integrados
                          ├── C-12 sincronizar-calendario-externo
                          └── C-13 historia-clinica-y-odontograma
```

### Paralelismo por fase

```text
GATE 0: C-01 ✓ (archivado)
  → C-01b crear-turno-sin-solapamientos-fastapi          [Agente A]

GATE 1: C-01b ✓                                          ← FORK
  → C-02 consultar-agenda                                [Agente B]
  → C-03 bloquear-disponibilidad                         [Agente A]
  → C-05 cancelar-y-confirmar-turnos                     [Agente B]
  → C-08 autenticar-con-jwt                              [Agente C]
  → C-16 recordatorio-simulado-con-redis                 [Agente C]
  → C-17 registrar-paciente-minimo                       [Agente B]

GATE 2: C-03 ✓
  → C-04 reprogramar-turno-atomicamente                  [Agente A]

GATE 3: C-02 + C-08 + C-17 ✓
  → C-15 agenda-web-react                                [Agente C]

GATE 4: C-02 + C-04 + C-05 + C-15 + C-16 + C-17 ✓
  → C-06 flujo-mvp-docker-compose                        [Agente A]   ← MVP completo

GATE 5: C-06 ✓
  → C-07 migraciones-y-respaldo                          [Agente A]

GATE 6: C-07 ✓
  → C-09 endurecer-api-publicable                        [Agente A]
  → C-14 auditoria-operativa-y-observabilidad            [Agente B]

GATE 7: C-09 ✓                                           ← integraciones, no son fuente de verdad
  → C-10, C-11, C-12, C-13                               [según disponibilidad]
```

### Camino crítico del MVP (4 changes)

```text
C-01b → C-08 → C-15 → C-06
```

Tienen la misma longitud `C-01b → C-03 → C-04 → C-06` y `C-01b → C-02 → C-15 → C-06`, por lo que cualquier demora en C-02, C-03, C-04, C-08 o C-15 retrasa el MVP. C-05, C-16 y C-17 tienen holgura. Los changes C-07 en adelante son evolución posterior y no deben desplazar el núcleo de agenda.

### Plan con 3 agentes

| Paso | Agente A (Backend core) | Agente B (Backend aux) | Agente C (Plataforma / Frontend) |
|---|---|---|---|
| 1 | C-01b crear-turno-sin-solapamientos-fastapi | — | — |
| 2 | C-03 bloquear-disponibilidad | C-02 consultar-agenda | C-08 autenticar-con-jwt |
| 3 | C-04 reprogramar-turno-atomicamente | C-05 cancelar-y-confirmar / C-17 registrar-paciente-minimo | C-16 recordatorio-simulado-con-redis |
| 4 | — | — | C-15 agenda-web-react |
| 5 | C-06 flujo-mvp-docker-compose | — | — |

---

## FASE 0 — Núcleo de agenda en el stack definido

### [C-01] `crear-turno-sin-solapamientos`
- **Estado**: `[x]` archivado en `openspec/changes/archive/2026-10-01-crear-turno-sin-solapamientos/` con el stack anterior (Node.js + TypeScript en memoria). Su código fue reemplazado por C-01b; el comportamiento especificado se conserva.
- **Dependencias**: ninguna

### [C-01b] `crear-turno-sin-solapamientos-fastapi`
- **Estado**: `[x]` completado y archivado en `openspec/changes/archive/2026-10-08-crear-turno-sin-solapamientos-fastapi/` (40 tests en verde, ver `docs/evidencias/verificacion-c01b.md`)
- **Scope**: Reimplementar el alta de turnos en el stack definido, sin cambiar el contrato de C-01.
  - `backend/` con FastAPI, SQLAlchemy 2.0 y pytest; `docker-compose.yml` con `db` (PostgreSQL 17) y `api`; `.env.example` sin secretos.
  - Dominio Python puro: entidades, errores tipados e intersección semiabierta `[inicio, fin)`.
  - Modelos SQLAlchemy de paciente, profesional, box, prestación, turno e historial; `CHECK (fin > inicio)` y `EXCLUDE USING gist` por profesional y por box.
  - Caso de uso `CrearTurno` en una única transacción: turno + historial `creado`, o nada.
  - `POST /api/v1/turnos` (201/404/409/422) y `GET /health`.
  - Tests pytest por escenario del spec, incluido el rechazo de la base ante un solapamiento que elude la aplicación.
- **Dependencias**: C-01
- **Governance**: CRITICO
- **Leer antes**: `knowledge-base/02_descripcion_general.md`, `04_modelo_de_datos.md` §Turno, `05_reglas_de_negocio.md` §RN-DA y RN-DI, `08_arquitectura_propuesta.md`, `09_decisiones_y_supuestos.md` §DD-02

---

## FASE 1 — MVP (sección D del Discovery)

### [C-02] `consultar-agenda`
- **Estado**: `[x]` completado y archivado en `openspec/changes/archive/2026-10-30-consultar-agenda/` (73 tests en verde)
- **Scope**: Caso de uso `ConsultarAgenda` y `GET /api/v1/agenda` con rango obligatorio y filtros opcionales `profesional_id` / `box_id`; resultados ordenados por inicio; inclusión por intersección con el rango. Tests: agenda diaria por profesional, semanal por box, filtro combinado, rango vacío y exclusión de turnos que no intersectan.
- **Dependencias**: C-01b
- **Governance**: BAJO
- **Leer antes**: `04_modelo_de_datos.md` §Turno, `06_funcionalidades.md` §US-002, `07_flujos_principales.md` §Flujo 1

### [C-03] `bloquear-disponibilidad`
- **Estado**: `[x]` completado y archivado en `openspec/changes/archive/2026-10-30-bloquear-disponibilidad/` (148 tests en verde contra PostgreSQL real).
- **Scope**: Tabla y repositorio `bloqueo_disponibilidad` (recurso profesional o box, intervalo válido, motivo opcional); `POST /api/v1/bloqueos`; el alta de turnos rechaza intervalos que intersecten un bloqueo. La misma regla queda disponible para la reprogramación de C-04, aún pendiente. Un bloqueo que intersecta un turno existente se rechaza con error explícito, sin modificarlo; la política clínica definitiva sigue abierta. Tests: ambos recursos, bordes contiguos, alta rechazada y carreras concurrentes.
- **Dependencias**: C-01b
- **Governance**: MEDIO
- **Leer antes**: `05_reglas_de_negocio.md` §RN-DA-02 y RN-DI-04, `06_funcionalidades.md` §US-003, `10_preguntas_abiertas.md` (Media)

### [C-04] `reprogramar-turno-atomicamente`
- **Estado**: `[ ]` pendiente
- **Scope**: `ReprogramarTurno` y `PATCH /api/v1/turnos/{id}`: excluir el propio turno de la comparación, validar contra turnos y bloqueos, actualizar e insertar historial `reprogramado` en la misma transacción. Tests: cambio válido, conflictos por profesional/box/bloqueo, autoexclusión y fallo atómico.
- **Dependencias**: C-01b, C-03
- **Governance**: MEDIO
- **Leer antes**: `05_reglas_de_negocio.md` §RN-DI-02 a RN-DI-04 y RN-TU-02, `06_funcionalidades.md` §US-004

### [C-05] `cancelar-y-confirmar-turnos`
- **Estado**: `[ ]` pendiente
- **Scope**: `CancelarTurno` / `ConfirmarTurno` y sus endpoints; un turno cancelado deja de participar de la restricción de exclusión (`WHERE estado <> 'cancelado'`) y de la validación; historial `cancelado` / `confirmado`. Tests: cancelar libera el intervalo, confirmar conserva la reserva, transiciones inválidas no alteran estado.
- **Dependencias**: C-01b
- **Governance**: MEDIO
- **Leer antes**: `05_reglas_de_negocio.md` §RN-TU, `06_funcionalidades.md` §US-005, `10_preguntas_abiertas.md`

### [C-08] `autenticar-con-jwt`
- **Estado**: `[ ]` pendiente
- **Scope**: Usuarios y roles (recepción, odontólogo/a, responsable) con contraseñas hasheadas; `POST /api/v1/auth/token` (OAuth2 password flow) que emite JWT firmado con `JWT_SECRET` de entorno; dependencia FastAPI que protege todas las rutas `/api/v1`; actor trazable en el historial. Tests: token válido, expirado, firma inválida, acceso denegado por rol. Ningún secreto versionado.
- **Dependencias**: C-01b
- **Governance**: CRITICO
- **Leer antes**: `03_actores_y_roles.md` §RBAC, `08_arquitectura_propuesta.md` §Seguridad, `10_preguntas_abiertas.md` §Quién puede operar

### [C-16] `recordatorio-simulado-con-redis`
- **Estado**: `[ ]` pendiente
- **Scope**: Recordatorio manual o simulado exigido por la sección D: al crear/confirmar un turno se encola en Redis una tarea de recordatorio; un worker la procesa con un `NotificadorSimulado` que sólo registra el envío (sin WhatsApp real). Servicio `redis` en Docker Compose y `REDIS_URL`. Tests: encolado tras commit, idempotencia, turno cancelado no notifica, la agenda funciona con Redis caído.
- **Dependencias**: C-01b
- **Governance**: MEDIO
- **Leer antes**: `02_descripcion_general.md` §Integraciones, `05_reglas_de_negocio.md` §RN-EX-02

### [C-17] `registrar-paciente-minimo`
- **Estado**: `[ ]` pendiente
- **Scope**: Datos mínimos de paciente exigidos por la sección D: alta y búsqueda (`POST/GET /api/v1/pacientes`) con nombre mostrado y contacto opcional; sin datos clínicos; seeds y tests exclusivamente ficticios. Tests: alta válida, duplicado, búsqueda y rechazo de campos no permitidos.
- **Dependencias**: C-01b
- **Governance**: ALTO (datos personales)
- **Leer antes**: `04_modelo_de_datos.md` §Paciente, `09_decisiones_y_supuestos.md` §DD-04, `10_preguntas_abiertas.md` §Datos mínimos

### [C-15] `agenda-web-react`
- **Estado**: `[ ]` pendiente
- **Scope**: `frontend/` con React + TypeScript (`strict`) + Vite: login contra C-08, vista diaria/semanal por profesional y box (C-02) y formulario de alta que muestra la causa del rechazo (409/422). La UI no recalcula disponibilidad. Servicio `frontend` en Docker Compose. Tests de componentes y de cliente API.
- **Dependencias**: C-02, C-08, C-17
- **Governance**: MEDIO
- **Leer antes**: `01_vision_y_objetivos.md`, `06_funcionalidades.md`, `07_flujos_principales.md`; referencias UX del Discovery (Simples Dental, Dentios, DentalQub)

### [C-06] `flujo-mvp-docker-compose`
- **Estado**: `[ ]` pendiente
- **Scope**: `docker compose up` levanta db, redis, api y frontend con seeds ficticios; prueba E2E por API: login, alta de paciente, alta de turno, consulta, bloqueo, rechazo por conflicto, reprogramación, cancelación, reutilización del horario y recordatorio simulado registrado. Documentación de arranque.
- **Dependencias**: C-02, C-04, C-05, C-15, C-16, C-17
- **Governance**: BAJO

---

## FASE 2 — Evolución posterior al MVP

### [C-07] `migraciones-y-respaldo`
- **Estado**: `[ ]` pendiente
- **Scope**: Migraciones versionadas (Alembic), respaldo y restauración de PostgreSQL, pruebas de concurrencia con dos sesiones simultáneas sobre el mismo recurso. Decisión sobre clínica/sucursal, retención y exportación.
- **Dependencias**: C-06
- **Governance**: ALTO

### [C-14] `auditoria-operativa-y-observabilidad`
- **Estado**: `[ ]` pendiente
- **Scope**: Eventos de auditoría, logs estructurados sin PII, métricas de conflictos, runbook de doble reserva y retención de auditoría.
- **Dependencias**: C-07
- **Governance**: CRITICO

### [C-09] `endurecer-api-publicable`
- **Estado**: `[ ]` pendiente
- **Scope**: Contrato OpenAPI versionado, rate limiting, CORS, idempotencia de comandos, redacción de datos por rol y pruebas de contrato antes de exponer la API fuera de la red de la clínica.
- **Dependencias**: C-07, C-08
- **Governance**: ALTO

---

## FASE 3 — Integraciones y clínica (etapas posteriores del Discovery)

### [C-10] `recordatorios-whatsapp-con-consentimiento`
- **Estado**: `[ ]` pendiente
- **Scope**: Reemplazar el `NotificadorSimulado` de C-16 por un adaptador de WhatsApp Business con consentimiento, opt-out y reintentos sobre la cola Redis existente. Los mensajes nunca crean ni cambian turnos directamente.
- **Dependencias**: C-09, C-16
- **Governance**: ALTO

### [C-11] `cobros-y-senas-integrados`
- **Estado**: `[ ]` pendiente
- **Scope**: Seña con Mercado Pago, webhooks firmados e idempotentes procesados vía Redis, estado de pago separado del estado del turno. Requiere reglas financieras aprobadas.
- **Dependencias**: C-09
- **Governance**: CRITICO

### [C-12] `sincronizar-calendario-externo`
- **Estado**: `[ ]` pendiente
- **Scope**: Sincronización con Google Calendar subordinada al dominio; credenciales fuera del repositorio; conflictos externos nunca generan solapamientos.
- **Dependencias**: C-09
- **Governance**: ALTO

### [C-13] `historia-clinica-y-odontograma`
- **Estado**: `[ ]` pendiente
- **Scope**: Historia clínica y odontograma como dominio separado, sólo con marco legal, consentimiento, cifrado y auditoría aprobados.
- **Dependencias**: C-08, C-09
- **Governance**: CRITICO
