# Actores y Roles

## Actores del sistema

| Actor | Descripción | Cómo interactúa en el alcance actual |
|---|---|---|
| Recepción / secretaría | Opera el calendario cotidiano del consultorio | Ejecuta casos de uso de agenda en el futuro adaptador o ejecutable |
| Odontólogo/a | Profesional que requiere tiempo y, habitualmente, un box | Consulta agenda; sus permisos definitivos están por validar |
| Responsable de clínica | Responsable operativo del consultorio | Define políticas y supervisa cambios; permisos detallados pendientes |
| Paciente | Persona para quien se registra el turno | Es una entidad con datos mínimos ficticios; no posee canal directo en el MVP |

## RBAC — Matriz de permisos propuesta

La autorización es una proyección propuesta, no un requisito validado con clínicas. El núcleo de dominio no debe asumir que un canal externo ya autorizó una operación.

| Rol | Recurso | Permisos propuestos |
|---|---|---|
| Recepción | Turno | Crear, consultar, reprogramar, cancelar y confirmar |
| Recepción | Bloqueo | Crear, consultar y quitar según política futura |
| Odontólogo/a | Agenda propia | Consultar; cambios pendientes de definición |
| Responsable de clínica | Agenda, turnos y bloqueos | Consultar y administrar; auditoría enriquecida posterior |
| Paciente | Turno propio | Sin permiso directo en MVP; futuro canal de reserva/confirmación |

## Rutas públicas

No hay rutas públicas: el MVP no incluye UI ni API HTTP. Las futuras reservas por web, enlace, WhatsApp o bot deberán diseñarse con autenticación/autorización y pasar por las reglas del dominio.
