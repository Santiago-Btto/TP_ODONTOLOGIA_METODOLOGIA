# Proposal

## Why

La agenda requiere un núcleo confiable que impida reservar simultáneamente un profesional o un box. Este primer cambio hace verificable la regla central de disponibilidad antes de sumar adaptadores, consultas, bloqueos o persistencia.

## What Changes

- Agregar un módulo TypeScript de dominio y aplicación para crear turnos en memoria con paciente, profesional, box, prestación e intervalo válidos.
- Validar disponibilidad para ambos recursos usando intervalos semiabiertos `[inicio, fin)`, de modo que turnos contiguos sean válidos.
- Rechazar conflictos de profesional o box e intervalos/duraciones inválidos sin persistir un turno ni un historial parcial.
- Registrar el evento de historial `creado` únicamente después de una reserva válida.
- Incorporar repositorios en memoria, fixtures exclusivamente ficticios y pruebas automatizadas del núcleo. No se añadirán UI, HTTP, persistencia, autenticación ni integraciones externas.

## Capabilities

### New Capabilities
- `creacion-de-turnos`: Crear una reserva de agenda válida y proteger la disponibilidad del profesional y del box frente a solapamientos.

### Modified Capabilities

- Ninguna.

## Impact

- Código nuevo: configuración Node.js/TypeScript, dominio, caso de uso, repositorios en memoria y pruebas bajo el proyecto.
- Sin cambios de API, bases de datos, credenciales, dependencias externas ni datos reales.
- Esta capacidad será la base de los changes de consulta, bloqueos, reprogramación y ciclo de vida del turno.
