# Spec Delta

## MODIFIED Requirements

### Requirement: Ordenar y describir los resultados
El sistema SHALL devolver los turnos por inicio cronológico ascendente, identificando en cada elemento el profesional, el box y el estado del turno (`programado`, `confirmado` o `cancelado`). Si no hay coincidencias, SHALL devolver una lista vacía.

#### Scenario: Resultado ordenado
- **DADO** turnos insertados en orden distinto al cronológico
- **CUANDO** se consulta un rango que los incluye
- **ENTONCES** la respuesta contiene primero el turno con inicio anterior y cada elemento contiene `profesional_id`, `box_id` y `estado`

#### Scenario: Rango sin coincidencias
- **DADO** turnos fuera del rango o que no coinciden con los filtros
- **CUANDO** se consulta ese rango
- **ENTONCES** se devuelve una lista vacía

#### Scenario: Turno cancelado identificado en la agenda
- **DADO** un turno cancelado y otro confirmado dentro del rango
- **CUANDO** se consulta la agenda
- **ENTONCES** ambos aparecen y cada uno informa su estado `cancelado` o `confirmado`
