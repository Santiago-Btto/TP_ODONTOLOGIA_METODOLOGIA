# Modelo de Datos

## Dominios

- **Agenda y disponibilidad:** reserva de tiempo, consulta de agenda y bloqueos.
- **Recursos clínicos operativos:** profesional y sillón/box requeridos para un turno.
- **Prestaciones:** duración configurada para calcular el intervalo del turno.
- **Pacientes:** identidad mínima exclusivamente ficticia para el MVP.
- **Trazabilidad:** cambios de horario y estado de un turno.

## ERD (Entity Relationship Diagram)

```text
Paciente ficticio 1 ---- * Turno * ---- 1 Profesional
                              |
                              + ---- 1 Box
                              |
                              + ---- 1 Prestación
                              |
                              + ---- * HistorialDeCambio

Profesional 1 ---- * BloqueoDeDisponibilidad
Box          1 ---- * BloqueoDeDisponibilidad
```

## Entidades

### Paciente

- Atributos: `id: string`, `nombreMostrado: string` y los datos mínimos que aún deben acordarse.
- Restricción: todo valor de desarrollo, prueba o semilla debe ser ficticio; no se admiten datos personales o clínicos reales.
- Relaciones: un paciente puede tener muchos turnos.

### Profesional

- Atributos: `id: string`, `nombreMostrado: string`, `activo: boolean`.
- Relaciones: un profesional puede tener muchos turnos y bloqueos.
- Índice lógico: por `id` y por intervalo de agenda cuando exista persistencia.

### Box

- Atributos: `id: string`, `nombre: string`, `activo: boolean`.
- Relaciones: un box puede tener muchos turnos y bloqueos.
- Índice lógico: por `id` y por intervalo de agenda cuando exista persistencia.

### Prestación

- Atributos: `id: string`, `nombre: string`, `duracionMinutos: number`.
- Constraint: la duración debe ser positiva; el catálogo de prestaciones y duraciones está pendiente.
- Relaciones: una prestación puede aparecer en muchos turnos.

### Turno

- Atributos: `id: string`, `pacienteId: string`, `profesionalId: string`, `boxId: string`, `prestacionId: string`, `inicio: DateTime`, `fin: DateTime`, `estado: EstadoTurno`.
- Estados identificados: pendiente/programado, confirmado y cancelado; la nomenclatura final debe acordarse.
- Constraints: `fin > inicio`; recursos y paciente requeridos; no puede intersectar un turno activo o bloqueo del mismo profesional o box. En PostgreSQL: `CHECK (fin > inicio)` y dos restricciones `EXCLUDE USING gist` (por `profesional_id` y por `box_id`) sobre `tstzrange(inicio, fin, '[)')` para turnos activos.
- Relaciones: pertenece a un paciente, profesional, box y prestación; tiene historial de cambios.

### BloqueoDeDisponibilidad

- Atributos: `id: string`, `recursoTipo: profesional | box`, `recursoId: string`, `inicio: DateTime`, `fin: DateTime`, `motivo?: string`.
- Constraint: `fin > inicio`; impide reservar el recurso en un intervalo intersectante.
- Relaciones: pertenece a un profesional o un box.

### HistorialDeCambio

- Atributos: `id: string`, `turnoId: string`, `tipo: creado | reprogramado | cancelado | confirmado`, `ocurridoEn: DateTime`, `antes?: ResumenTurno`, `despues?: ResumenTurno`, `actorId?: string`.
- Constraint: el detalle de identidad del actor y política de retención siguen abiertos.

## Seed data inicial

- Un conjunto mínimo de profesionales, boxes, prestaciones y pacientes con nombres evidentemente ficticios (por ejemplo, “Paciente Demo 001”).
- Datos de horarios reproducibles para pruebas: un turno válido, una reserva contigua y bloqueos de ejemplo.
- Ningún dato real de pacientes, personal, teléfonos, documentos, historias clínicas ni credenciales.
