# turnos-odontologia — Instrucciones para Agentes

> `AGENTS.md` y `CLAUDE.md` son copias sincronizadas. Se generan desde `knowledge-base/` y `CHANGES.md`; si se modifica uno, se debe actualizar el otro con el mismo contenido.

---

## Stack Tecnológico

| Capa | Tecnología | Versión mínima / nota |
|---|---|---|
| Runtime | Node.js | Versión LTS a fijar antes de implementar |
| Lenguaje | TypeScript | Versión a fijar por el change de implementación |
| Dominio | Módulos TypeScript sin dependencias externas | Regla de agenda ejecutable localmente |
| Pruebas | `node:test` y `node:assert` | Incluidos en Node.js; sin cuentas externas |
| Persistencia | En memoria para el MVP | No se definió base de datos |

Detalle completo: [knowledge-base/02_descripcion_general.md](knowledge-base/02_descripcion_general.md).

---

## Base de Conocimiento

La fuente de verdad del dominio vive en `knowledge-base/`. Leé el archivo relevante antes de implementar.

| Archivo | Cuándo leerlo |
|---|---|
| [01_vision_y_objetivos.md](knowledge-base/01_vision_y_objetivos.md) | Propósito, alcance y objetivos |
| [03_actores_y_roles.md](knowledge-base/03_actores_y_roles.md) | Actores, RBAC y permisos |
| [04_modelo_de_datos.md](knowledge-base/04_modelo_de_datos.md) | Entidades, relaciones y datos semilla |
| [05_reglas_de_negocio.md](knowledge-base/05_reglas_de_negocio.md) | Reglas trazables de disponibilidad y ciclo de vida |
| [06_funcionalidades.md](knowledge-base/06_funcionalidades.md) | Historias de usuario y alcance por épica |
| [07_flujos_principales.md](knowledge-base/07_flujos_principales.md) | Flujos E2E de agenda |
| [08_arquitectura_propuesta.md](knowledge-base/08_arquitectura_propuesta.md) | Patrones, estructura y límites de arquitectura |
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

Cargá la skill correspondiente al contexto antes de actuar.

> Los compact rules de cada skill los resuelve el orquestador desde `.atl/skill-registry.md` (generado por `skill-registry`; no versionado — no está en el repo). Esta tabla solo mapea skill→rol.

---

## Roadmap de Changes

El plan completo está en [CHANGES.md](CHANGES.md). Resumen:

- **Total:** 14 changes en 5 fases.
- **MVP:** `C-01` a `C-06`; el núcleo queda ejecutable localmente tras `C-06`.
- **Camino crítico declarado:** `C-01 → C-03 → C-04 → C-05 → C-06`.
- **Primer change:** `C-01` (`crear-turno-sin-solapamientos`).
- **Evolución posterior:** persistencia/concurrencia, adaptadores con autorización, auditoría, API e integraciones; la información clínica (`C-13`) requiere un marco aprobado.

Antes de cualquier `/opsx:propose`, leé [CHANGES.md](CHANGES.md), verificá dependencias y consultá los archivos indicados en “Leer antes”.

---

## Reglas Duras (específicas del proyecto)

> Reglas globales ya definidas en `~/.claude/CLAUDE.md` (orquestador, governance, TDD, engram): el proyecto las hereda. Acá viven solo las reglas específicas de este proyecto + las universales que el global no cubra.

- NUNCA almacenar, usar ni introducir datos reales de pacientes, secretos o credenciales → usar exclusivamente datos ficticios y no solicitar ni configurar cuentas externas.
- NUNCA desactivar TypeScript estricto ni usar `any` → mantener `strict` habilitado y modelar tipos explícitos.
- NUNCA hacer que el dominio dependa de UI, HTTP, red o integraciones externas → conservar reglas de agenda como módulos TypeScript puros y adaptadores posteriores separados.
- NUNCA sustituir la suite del proyecto por otro runner → escribir y ejecutar pruebas con `node:test` y `node:assert`.

---

## Flujo de Trabajo

```text
1. Leer la KB relevante (knowledge-base/)        → entender dominio y restricciones
2. Identificar el change en CHANGES.md           → respetar dependencias
3. /opsx:propose C-NN-nombre                     → proposal + design + specs + tasks
4. Implementar las tasks con las skills adecuadas → respetar reglas duras y TDD global
5. /opsx:archive C-NN-nombre                     → sincronizar specs y cerrar el change
```

Ante conflicto entre la KB y estas reglas duras, las reglas duras prevalecen. Las decisiones de producto aún abiertas se deben escalar, no completar mediante supuestos.
