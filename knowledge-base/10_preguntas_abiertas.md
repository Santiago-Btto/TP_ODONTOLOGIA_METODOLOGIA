# Preguntas Abiertas

## Inconsistencias detectadas

No se detectaron contradicciones materiales entre el checklist y el informe. Ambos distinguen hechos investigados de propuestas y remarcan que la validación primaria todavía no ocurrió.

## Preguntas abiertas (priorizadas)

| Prioridad | Pregunta | Bloquea | Decisor |
|---|---|---|---|
| Alta | ¿Cuál es la política de sobreturnos y existen excepciones por urgencia? | Regla definitiva de disponibilidad | Responsable de clínica / Product Owner |
| Alta | ¿Quién puede crear, reprogramar, cancelar o confirmar y hasta qué momento? | RBAC y ciclo de vida del turno | Responsable de clínica / Product Owner |
| Alta | ¿Qué prestaciones existen, qué duración tienen y un turno siempre requiere un único box y profesional? | Modelo de datos y cálculo de intervalos | Clínica / Product Owner |
| Alta | ¿Cuántos profesionales, boxes y sucursales debe soportar la primera versión? | Escala y modelo de aislamiento | Product Owner |
| Alta | [DISCOVERY] `scale` sólo se infirió como equipo desde los actores de los documentos. ¿El alcance es una clínica, varias sucursales o un producto multi-clínica? | Arquitectura y autorización futuras | Product Owner |
| Alta | ¿Qué datos mínimos de paciente son necesarios y qué consentimiento, retención, exportación y seguridad aplican? | Modelo de datos si se agregan datos personales | Responsable legal / clínica |
| Media | ¿Cómo se resuelven bloqueos que se solapan con turnos ya creados? | Operación de bloqueos | Responsable de clínica |
| Media | ¿Qué ocurre si se intenta reprogramar un turno cancelado o confirmar uno vencido? | Máquina de estados | Product Owner |
| Media | ¿La agenda diaria/semanal debe ocultar, anonimizar o limitar datos según el rol? | Autorización y privacidad | Clínica / Product Owner |
| Media | ¿Cuál es la ventana de cancelación, y cómo se aplican señas y reintegros? | Integración de pagos posterior | Responsable de clínica / Finanzas |
| Media | ¿Qué canal de recordatorio y consentimiento se requiere para WhatsApp u otros medios? | Integración de mensajería posterior | Product Owner / legal |
| Baja | ¿Se necesita lista de espera, exportación de agenda o auditoría enriquecida después del MVP? | Roadmap posterior | Product Owner |
| Baja | ¿Se integrará Google Calendar y bajo qué regla se resuelven conflictos de sincronización? | Adaptador de calendario posterior | Tech Lead / Product Owner |

## Validación pendiente del Discovery

El informe vigente es investigación documental, no validación primaria. Antes de elevar estas propuestas a requisitos de producto se recomienda entrevistar al menos tres consultorios argentinos y ejecutar demos de los cinco productos priorizados: Dentalink, AgendaPro Dental, DentalSoft, Denteo y Dentiqa.
