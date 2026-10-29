# Design

## Context

Véase `proposal.md` para la motivación y `specs/consulta-de-agenda/spec.md` para el contrato. C-01b ya aporta `Turno`, PostgreSQL con `timestamptz`, SQLAlchemy, `UnidadDeTrabajoSQLAlchemy`, API FastAPI y pruebas en cuatro capas. `CHANGES.md` exige caso de uso `ConsultarAgenda`, `GET /api/v1/agenda`, rango obligatorio, filtros opcionales e inclusión por intersección. Los identificadores de profesional y box son `str`/`String(64)`; las semillas como `profesional-demo-001` confirman que no son UUID. Actualmente el único estado de dominio implementado es `programado`; C-05 definirá cancelación y confirmación.

## Goals / Non-Goals

**Goals:**
- Mantener la regla de selección comprobable en aplicación y persistencia, con una ruta HTTP delgada.
- Consultar sin alterar turnos ni historiales y conservar el formato temporal explícito que ya utiliza el alta.
- Probar la consulta de forma aislada en caso de uso, adaptador SQLAlchemy y API.

**Non-Goals:**
- Calcular huecos libres, incorporar bloqueos C-03 o crear la interfaz de C-15.
- Definir visibilidad de cancelados/confirmados antes de C-05, ni agregar autenticación antes de C-08. La API sigue circunscrita al entorno local de desarrollo hasta que esas capacidades existan.
- Cambiar esquema, semillas o contrato de `POST /api/v1/turnos`.

## Decisions

### 1. Puerto de lectura y caso de uso independientes

Agregar un puerto de consulta con operación de búsqueda por intervalo y filtros, y un caso de uso `ConsultarAgenda` que valida el rango y delega la lectura. El adaptador SQLAlchemy implementará el puerto sobre la tabla `turnos`. El caso de uso no invoca `commit`, no agrega historial y devuelve una secuencia de turnos. Es compatible con la separación actual entre aplicación, dominio e infraestructura. Alternativa descartada: consultar directamente desde el router; duplicaría reglas en la capa HTTP y dificultaría pruebas de aplicación.

### 2. Predicado temporal y filtros

Usar `TurnoModelo.inicio < fin` y `TurnoModelo.fin > inicio`, que expresa intersección de intervalos semiabiertos `[inicio, fin)` y excluye límites contiguos. Los filtros opcionales de profesional y box se agregan con conjunción `AND`, sin comprobar la existencia de recursos: un ID de texto sin turnos coincidentes produce `[]`. Ordenar por `inicio` ascendente; el orden relativo de dos turnos con el mismo inicio queda sin contrato y no se afirmará en pruebas. Alternativa descartada: seleccionar sólo turnos cuyo inicio cae dentro del rango; perdería los que empiezan antes o cubren todo el rango.

### 3. Entrada y salida HTTP

Declarar `inicio` y `fin` como parámetros obligatorios con fecha y zona horaria, y `profesional_id`/`box_id` como texto opcional, de acuerdo con el modelo existente. Normalizar instantes a UTC para comparar o serializar; rechazar fechas sin zona, formatos inválidos y `fin <= inicio` con `422` siguiendo la pauta de validación de la API de alta. Exponer una lista JSON de turnos con `id`, `profesional_id`, `box_id`, `inicio` y `fin`; evitar incluir datos del paciente que US-002 no requiere. Alternativa descartada: reutilizar íntegramente `TurnoSalida`, que añade `paciente_id` y `prestacion_id` sin necesidad para la agenda.

### 4. Guía de documentación externa y decisiones locales

Se consultó el MCP Context7: la [documentación de FastAPI](https://fastapi.tiangolo.com/tutorial/query-params/) confirma la distinción entre parámetros requeridos y opcionales y la respuesta `422` por ausencia de requeridos; la [guía ORM de SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/queryguide/select.html) documenta `select().where()`, `order_by()` y `Session.scalars()`. Estas fuentes guían sintaxis de framework. Zona horaria, intervalo válido, intersección y tipos de ID se decidieron con la KB y el código local; la evidencia está en `docs/skills-mcp/evidencias/context7-uso.md`.

## Risks / Trade-offs

- [Tiempos equivalentes con distintos desplazamientos] → comparar instantes normalizados y probar una consulta cuyo offset difiere del turno persistido.
- [Consulta amplia sin paginación] → C-02 se usa en rangos diarios/semanales; medir volumen cuando haya datos reales de escala y definir paginación en otro change si hiciera falta.
- [C-05 introduce estados adicionales] → revisar entonces la proyección y la política de inclusión; C-02 no anticipa qué estados deben mostrarse.
- [Acceso antes de C-08] → mantener el servicio sólo en desarrollo local y no tratar este change como publicación de una API con datos reales.

## Migration Plan

No se prevé migración de datos. Al implementar, incorporar el puerto, caso de uso, adaptador y router; ejecutar pruebas y validar que el alta existente sigue funcionando. Si el cambio debe revertirse, retirar la ruta y sus componentes de lectura; la base permanece intacta.

## Open Questions

- Cuando C-05 agregue cancelación y confirmación, ¿qué estados incluirá la agenda para recepción y para profesionales?
- Si varios turnos empiezan exactamente al mismo tiempo, ¿necesita la futura interfaz C-15 un criterio de desempate estable?
