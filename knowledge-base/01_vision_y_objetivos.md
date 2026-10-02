# Visión y Objetivos

## Propósito del sistema

El MVP resuelve la asignación confiable de turnos odontológicos sin solapar a un mismo profesional ni a un mismo sillón/box, y conserva trazabilidad básica cuando un turno cambia de horario o estado.

La prioridad es el núcleo de agenda para consultorios del mercado argentino: reglas de disponibilidad deterministas antes que automatizaciones, cobros o historia clínica. Todo ejemplo, dato de prueba y semilla debe ser ficticio; no se almacenan datos reales de pacientes.

## Objetivos por actor

| Actor | Objetivo principal | Objetivos secundarios |
|---|---|---|
| Recepción / secretaría | Crear y gestionar turnos válidos rápidamente | Consultar agenda, bloquear horarios, reprogramar y cancelar |
| Odontólogo/a | Conocer su agenda sin conflictos | Distinguir el box asignado y los estados de sus turnos |
| Responsable de clínica | Operar recursos escasos con trazabilidad | Revisar cambios y bloqueos; definir la política pendiente |
| Paciente | Obtener o confirmar un turno a través de canales futuros | Recibir recordatorios; no es una interfaz incluida en este MVP |

## Alcance v0.1 — MVP de dominio ejecutable

- Modelar pacientes ficticios, profesionales, boxes, prestaciones, bloqueos y turnos.
- Crear un turno con paciente, profesional, box, inicio, fin/duración y estado.
- Consultar agenda diaria o semanal por profesional y/o box.
- Impedir intervalos que se intersecten para el mismo profesional o para el mismo box.
- Aceptar turnos contiguos: el inicio de uno puede coincidir exactamente con el fin de otro.
- Reprogramar o cancelar un turno y liberar su intervalo anterior.
- Registrar historial básico de cambios y confirmación.
- Ejecutar reglas y pruebas localmente sin cuentas ni servicios externos.

## Fuera de alcance

- Interfaz web, móvil o portal de paciente.
- Integraciones reales con WhatsApp, Mercado Pago o Google Calendar.
- Odontograma, historia clínica, imágenes, recetas, firma o tratamientos clínicos completos.
- Facturación ARCA, obras sociales, liquidaciones, conciliación de cobros y seña.
- Chatbot/IA, lista de espera, campañas, API pública y multi-sucursal avanzada.
- Datos reales de pacientes, credenciales reales o una política legal de salud no validada.

## Métricas de éxito

- Las pruebas cubren al menos un turno válido, un conflicto por profesional, un conflicto por box y un caso de turnos contiguos.
- Ninguna operación de alta o reprogramación crea reservas superpuestas para recursos activos.
- Los cambios de horario y estado quedan representados en el historial básico definido para el MVP.
- La suite se ejecuta localmente con datos completamente ficticios y sin dependencias externas.
