# turnos-odontologia — Instrucciones para Agentes

> `AGENTS.md` y `CLAUDE.md` son copias sincronizadas. Se generan desde `knowledge-base/` y `CHANGES.md`; si se modifica uno, se debe actualizar el otro con el mismo contenido.

---

## Stack Tecnológico

> Ajustado el 2026-10-08 (antes: Node.js + TypeScript en memoria). Ver `knowledge-base/09_decisiones_y_supuestos.md` §DD-02.

| Capa | Tecnología | Versión mínima / nota |
|---|---|---|
| Backend | Python + FastAPI | Python 3.12, FastAPI 0.115 |
| ORM | SQLAlchemy | 2.0, modelos tipados con `Mapped[...]` |
| Persistencia | PostgreSQL | 17, con `btree_gist` para restricciones de exclusión |
| Autenticación | JWT | Desde C-08; secreto por variable de entorno |
| Asincronía | Redis | Desde C-16 (recordatorio simulado) |
| Contenedores | Docker / Docker Compose | `docker-compose.yml` en la raíz |
| Frontend | React + TypeScript + Vite | Desde C-15, TypeScript `strict` |
| Pruebas backend | pytest + httpx | Contra PostgreSQL real (`TEST_DATABASE_URL`) |

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md).

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. Leé el archivo relevante antes de implementar.

| Archivo | Cuándo leerlo |
|---|---|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito, alcance y objetivos |
| [02_descripcion_general.md](knowledge-base/02_descripcion_general.md) | Stack, arquitectura, integraciones y API |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores, RBAC y permisos |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, relaciones, restricciones y datos semilla |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas trazables de disponibilidad y ciclo de vida |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario y alcance por épica |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E de agenda |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura, seguridad y variables de entorno |
| [09_decisiones_y_supuestos.md](knowledge-base/09_decisiones_y_supuestos.md) | Decisiones y supuestos por validar |
| [10_preguntas_abiertas.md](knowledge-base/10_preguntas_abiertas.md) | Preguntas que requieren validación de producto |

> Antes de introducir políticas de sobreturnos, autorización, prestaciones/duraciones, escala, multi-clínica o datos personales, resolver las preguntas de prioridad Alta en `10_preguntas_abiertas.md`.

---

## Skills Disponibles

| Agente | Rol | Skills que carga |
|---|---|---|
| **Orquestación** | Fundación, coordinación OPSX y documentación | `active-orchestrator`, `agents-md-generator`, `kb-creator`, `roadmap-generator`, `skill-creator` |
| **Discovery** | Investigación y validación de requisitos | `discovery-research`, `web-scraper` |
| **Planificación OPSX** | Explorar, proponer y revisar changes | `openspec-explore`, `openspec-propose`, `openspec-update-change` |
| **Implementación OPSX** | Aplicar tasks y sincronizar especificaciones | `openspec-apply-change`, `openspec-sync-specs` |
| **Cierre OPSX** | Archivar changes completos | `openspec-archive-change` |
| **Extensión de capacidades** | Buscar o crear skills | `find-skills`, `skill-creator` |
| **Backend / API** | Endpoints, dependencias y errores FastAPI | `fastapi-templates` |
| **Base de datos** | Esquema, restricciones e índices PostgreSQL 17 | `postgresql-table-design` |
| **Calidad** | Pruebas pytest de dominio, aplicación, infraestructura y API | `python-testing-patterns` |
| **Seguridad** | Revisión/guía explícita o código secure-by-default autorizado | `security-best-practices` |
| **Asincronía (condicional)** | Solo changes que adopten una cadena async completa | `async-python-patterns` |

Cargá la skill correspondiente al contexto antes de actuar.

> El registro de skills del proyecto está versionado en [`.atl/skill-registry.md`](.atl/skill-registry.md). Las skills locales viven en [`skills/`](skills/) y se cargan según sus triggers; el backend vigente es síncrono, por lo que async exige un change que lo diseñe de punta a punta.

---

## Roadmap de Changes

El plan completo está en [CHANGES.md](CHANGES.md). Resumen:

- **MVP:** C-01b, C-02, C-03, C-04, C-05, C-08, C-15, C-16, C-17 y C-06 (sección D del Discovery).
- **Camino crítico:** `C-01b → C-08 → C-15 → C-06` (misma longitud que `C-01b → C-03 → C-04 → C-06`).
- **Primer change:** C-01 (archivado con el stack anterior) y su reimplementación C-01b en FastAPI + PostgreSQL.
- **Evolución posterior:** migraciones/respaldo, auditoría, API publicable e integraciones reales; la información clínica (C-13) requiere un marco aprobado.

Antes de cualquier `/opsx:propose`, leé [CHANGES.md](CHANGES.md), verificá dependencias y consultá los archivos indicados en “Leer antes”.

---

## Reglas Duras (específicas del proyecto)

> Reglas globales ya definidas en `~/.claude/CLAUDE.md` (orquestador, governance, TDD, engram): el proyecto las hereda. Acá viven solo las reglas específicas de este proyecto + las universales que el global no cubra.

- NUNCA almacenar, usar ni introducir datos reales de pacientes en el repositorio, los tests, las semillas ni los ejemplos → usar exclusivamente datos ficticios identificables como tales (“Paciente Demo …”). *(Regla de dominio agregada a mano por el equipo.)*
- NUNCA versionar secretos ni credenciales (`JWT_SECRET`, tokens de WhatsApp/Mercado Pago, contraseñas de producción) → leerlos de variables de entorno; `.env` está en `.gitignore` y sólo se versiona `.env.example` con valores de desarrollo.
- NUNCA poner reglas de disponibilidad en routers FastAPI, en el frontend ni en integraciones → el router traduce HTTP ↔ caso de uso; la regla vive en `backend/app/domain`, que no importa FastAPI ni SQLAlchemy.
- NUNCA quitar las restricciones `CHECK (fin > inicio)` ni `EXCLUDE USING gist` de turnos → la base es la segunda barrera contra doble reserva.
- NUNCA confirmar un turno sin su historial (ni viceversa) → ambos en la misma transacción SQLAlchemy.
- NUNCA usar `any` en el frontend ni desactivar `strict` → tipos explícitos; en Python, anotar tipos en dominio y aplicación.
- NUNCA sustituir pytest como runner del backend ni mockear PostgreSQL en tests de repositorio/API → probar contra una base real descartable.

---

## Flujo de Trabajo

```text
1. Leer la KB relevante (knowledge-base/)        → entender dominio y restricciones
2. Identificar el change en CHANGES.md           → respetar dependencias
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks con las skills adecuadas → respetar reglas duras y TDD global
5. pytest (backend) / npm test (frontend)        → todo en verde antes de archivar
6. /opsx:archive C-NN-nombre                     → sincronizar specs y cerrar el change
```

Ante conflicto entre la KB y estas reglas duras, las reglas duras prevalecen. Las decisiones de producto aún abiertas se deben escalar, no completar mediante supuestos.
