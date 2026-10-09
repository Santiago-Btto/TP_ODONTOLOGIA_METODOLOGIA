# Decisiones y Supuestos

## Decisiones documentadas

### DD-01 — Priorizar la agenda y los recursos operativos

**Decisión**: El primer MVP se centra en turnos por profesional y box, duración, bloqueos y cambios trazables.
**Contexto**: El Discovery identifica estos controles como el núcleo confiable y deja facturación e historia clínica para más adelante.
**Alternativas consideradas**: Incluir desde el inicio odontograma, facturación, obras sociales, chatbot o integraciones.
**Justificación**: Reduce alcance y permite probar el comportamiento de disponibilidad aislado.
**Trade-offs aceptados**: El MVP no es un sistema clínico o administrativo integral ni cubre todos los diferenciadores de mercado.

### DD-02 — Stack definido: FastAPI + PostgreSQL + React

**Decisión**: Backend en Python 3.12 con FastAPI, SQLAlchemy 2.0, PostgreSQL, JWT para autenticación, Redis para funcionalidades asincrónicas y Docker / Docker Compose; frontend en React + TypeScript + Vite. Pruebas con pytest contra PostgreSQL real.
**Contexto**: La consigna permite que el equipo defina el stack a partir de la Knowledge Base; no prescribe FastAPI, PostgreSQL ni React. La versión original de esta decisión (2026-10-01) fijaba Node.js + TypeScript con `node:test` y repositorios en memoria. El equipo la revisó y aplicó **Ajustar** el 2026-10-08: eligió este stack por las necesidades de persistencia transaccional, pruebas contra una base real y una futura agenda web, documentando la decisión en esta DD-02.
**Alternativas consideradas**: Mantener el núcleo Node.js en memoria y migrar más adelante (descartada: acumula código en un stack que no se va a usar y posterga la prevención transaccional de solapamientos que el Discovery marca como imprescindible).
**Justificación**: PostgreSQL permite imponer la regla anti-solapamiento también en la base (`EXCLUDE USING gist`), cerrando la ventana de doble reserva concurrente. FastAPI expone los casos de uso sin mover reglas al controlador.
**Trade-offs aceptados**: Ejecutar los tests requiere PostgreSQL (Docker Compose o instalación local). El dominio sigue siendo Python puro y se prueba sin base.

> Historial: el change C-01 se implementó y archivó con el stack anterior (`openspec/changes/archive/2026-10-01-crear-turno-sin-solapamientos/`). El change C-01b lo reimplementa con este stack sin cambiar el comportamiento especificado.

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
