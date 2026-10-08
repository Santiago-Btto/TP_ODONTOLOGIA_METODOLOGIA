# turnos-odontologia — Base de Conocimiento

Base de conocimiento generada desde `docs/discovery/informe-discovery.md`, `docs/discovery/checklist-discovery.md` y el contexto de Discovery registrado por el orquestador. Distingue evidencia documental, decisiones de alcance y preguntas aún no validadas.

## Índice de Archivos

| Archivo | Contenido |
|---|---|
| [01_vision_y_objetivos.md](01_vision_y_objetivos.md) | Propósito, alcance y objetivos por actor |
| [02_descripcion_general.md](02_descripcion_general.md) | Stack, arquitectura e integraciones |
| [03_actores_y_roles.md](03_actores_y_roles.md) | Actores, RBAC propuesto y rutas |
| [04_modelo_de_datos.md](04_modelo_de_datos.md) | Dominios, entidades y datos semilla |
| [05_reglas_de_negocio.md](05_reglas_de_negocio.md) | Reglas trazables de disponibilidad y ciclo de vida |
| [06_funcionalidades.md](06_funcionalidades.md) | Épicas e historias de usuario del MVP |
| [07_flujos_principales.md](07_flujos_principales.md) | Flujos de alta, cambio, cancelación y bloqueo |
| [08_arquitectura_propuesta.md](08_arquitectura_propuesta.md) | Patrones, estructura, seguridad y variables |
| [09_decisiones_y_supuestos.md](09_decisiones_y_supuestos.md) | Decisiones y supuestos para validar |
| [10_preguntas_abiertas.md](10_preguntas_abiertas.md) | Preguntas priorizadas y validación pendiente |

## Quick Start para Desarrolladores

1. Entender el problema y alcance -> [01](01_vision_y_objetivos.md), [03](03_actores_y_roles.md).
2. Entender entidades y restricciones -> [04](04_modelo_de_datos.md), [05](05_reglas_de_negocio.md).
3. Entender los comportamientos a implementar -> [06](06_funcionalidades.md), [07](07_flujos_principales.md).
4. Preparar el change técnico -> [02](02_descripcion_general.md), [08](08_arquitectura_propuesta.md), [09](09_decisiones_y_supuestos.md).
5. Antes de codificar decisiones de producto -> [10](10_preguntas_abiertas.md).

## Resumen Ejecutivo

El MVP es un sistema de turnos odontológicos con backend Python/FastAPI, SQLAlchemy y PostgreSQL (Redis para tareas asincrónicas, Docker Compose para el entorno) y frontend React + TypeScript + Vite, sin datos reales de pacientes. El stack se ajustó el 2026-10-08 (ver DD-02); la versión inicial era un núcleo Node.js en memoria. Su comportamiento crítico es impedir solapamientos de profesional y box, aceptar turnos contiguos y conservar trazabilidad básica al cambiar estados u horarios. Las decisiones clínicas, legales y operativas no validadas permanecen registradas como preguntas abiertas.
