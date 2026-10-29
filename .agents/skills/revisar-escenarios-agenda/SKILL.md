---
name: revisar-escenarios-agenda
description: Revisa escenarios de consulta de agenda odontológica antes de aprobar una especificación o sus pruebas. Úsala para cambios como C-02 consultar-agenda cuando se necesite detectar omisiones en rangos, filtros, orden, errores y trazabilidad sin modificar artefactos.
---

# Revisar escenarios de agenda

Audita el borrador y devuelve hallazgos concretos. No edites especificaciones, tareas, código ni pruebas. No inventes reglas de negocio: separa lo confirmado por las fuentes de las decisiones todavía abiertas.

## Entradas

1. Lee el alcance del cambio en `CHANGES.md` y los borradores pertinentes en `openspec/changes/<cambio>/`. Consulta el estado con `openspec status --change <cambio> --json` antes de atribuirle artefactos.
2. Lee las reglas y casos de uso de `knowledge-base/`, en especial US-002, RN-DI-01 y el modelo de `Turno` si están disponibles. Revisa también las especificaciones principales aplicables.
3. Si una fuente falta o contradice otra, registra esa limitación; no la completes por inferencia silenciosa.

## Auditoría

- Comprueba que el rango consultado tenga `inicio` y `fin`, y que se cubra el caso `inicio < fin`. Si la fuente no define el comportamiento para un rango inválido, preséntalo como decisión pendiente y no asignes un código HTTP inventado.
- Revisa la intersección de intervalos semiabiertos `[inicio, fin)`: un turno intersecta el rango si `turno.inicio < rango.fin` y `turno.fin > rango.inicio`. Un turno contiguo al límite queda fuera. Incluye escenarios de turno contenido, turno que comienza antes, turno que termina después y turno que cubre todo el rango.
- Comprueba filtros opcionales por profesional y box: ninguno, cada uno por separado y ambos juntos. Señala si la semántica de combinación no está expresada.
- Comprueba rango sin resultados, orden cronológico por inicio y el tratamiento de empates solo si alguna fuente lo especifica. No impongas un desempate nuevo.
- Revisa entradas inválidas, zonas horarias y cambios de horario. Si faltan formato, zona de referencia, conversión o respuesta de error, formula preguntas verificables en vez de inventar políticas.
- Contrasta cada escenario con las pruebas previstas en `tasks.md` o código de pruebas existente. Distingue prueba prevista de prueba ejecutada.

## Salida

Devuelve una matriz con columnas **Regla y fuente**, **Escenario (Dado/Cuando/Entonces)**, **Prueba asociada o propuesta** y **Estado** (`cubierto`, `falta`, `ambiguo`). Cita rutas y nombres de regla o criterio de aceptación. Incluye al menos un caso exitoso, uno de borde y uno de entrada inválida o error, marcando claramente lo que requiera decisión. Cierra con correcciones sugeridas y preguntas abiertas, priorizadas por impacto.
