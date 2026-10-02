# Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — Priorizar la agenda y los recursos operativos

**Decisión**: El primer MVP se centra en turnos por profesional y box, duración, bloqueos y cambios trazables.
**Contexto**: El Discovery identifica estos controles como el núcleo confiable y deja facturación e historia clínica para más adelante.
**Alternativas consideradas**: Incluir desde el inicio odontograma, facturación, obras sociales, chatbot o integraciones.
**Justificación**: Reduce alcance y permite probar el comportamiento de disponibilidad aislado.
**Trade-offs aceptados**: El MVP no es un sistema clínico o administrativo integral ni cubre todos los diferenciadores de mercado.

### DD-02 — Ejecutar el dominio localmente, sin UI ni infraestructura

**Decisión**: Usar Node.js y TypeScript sin dependencias externas, con `node:test` y repositorios en memoria.
**Contexto**: El alcance indicado es un MVP de dominio ejecutable y reproducible sin servicios externos.
**Alternativas consideradas**: Aplicación web, API REST o persistencia en base de datos desde el inicio.
**Justificación**: Facilita TDD de invariantes y elimina necesidad de cuentas o infraestructura.
**Trade-offs aceptados**: No existe interfaz, persistencia durable ni acceso multiusuario en esta etapa.

### DD-03 — El dominio es la autoridad de disponibilidad

**Decisión**: Toda creación o modificación se valida dentro del dominio.
**Contexto**: Futuras UI, bots o integraciones podrían intentar reservar por canales distintos.
**Alternativas consideradas**: Validar sólo en el canal que inicia la operación.
**Justificación**: Evita que una integración eluda conflictos de profesional o box.
**Trade-offs aceptados**: Los adaptadores futuros deben depender de los casos de uso y no implementar reglas divergentes.

### DD-04 — Datos exclusivamente ficticios

**Decisión**: No se usarán datos reales de pacientes en repositorio, pruebas, semillas o ejemplos.
**Contexto**: El Discovery declara datos ficticios y reconoce que las políticas de datos de salud no están acordadas.
**Alternativas consideradas**: Usar datos reales anonimizados o importar agenda existente.
**Justificación**: Protege la privacidad y evita asumir requisitos legales no validados.
**Trade-offs aceptados**: No se valida migración ni calidad de datos reales en el MVP.

## Supuestos inferidos

### SU-01 — El turno consume un profesional y un box

**Supuesto**: Cada turno del MVP reserva simultáneamente un profesional y un box.
**Origen**: Checklist e informe de Discovery enfatizan la prevención de doble uso de ambos recursos.
**Riesgo si es falso**: No se podrían modelar servicios que no requieren box, recursos alternativos o varios profesionales.
**Cómo validar**: Confirmar el flujo y tipos de prestación con consultorios entrevistados.

### SU-02 — La operación inicial es de equipo

**Supuesto**: El sistema inicia para una clínica/equipo, no como producto público multi-tenant.
**Origen**: Actores identificados incluyen recepción, odontólogos y responsable de clínica.
**Riesgo si es falso**: Multi-sucursal, aislamiento por clínica y autenticación requieren diseño diferente.
**Cómo validar**: Definir número de clínicas, sucursales, boxes y profesionales del alcance.

### SU-03 — La política por defecto no admite sobreturnos

**Supuesto**: El primer change rechaza sobreturnos.
**Origen**: Checklist: política no evidenciada y recomendación explícita de no permitirlos inicialmente.
**Riesgo si es falso**: El modelo de disponibilidad debe incorporar excepciones, prioridades y capacidad adicional.
**Cómo validar**: Acordar política operativa con el responsable de clínica.
