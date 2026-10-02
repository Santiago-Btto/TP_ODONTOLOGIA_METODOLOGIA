# Reglas de Negocio

Cada regla tiene un código único para trazabilidad. Las reglas marcadas como propuestas proceden del Discovery y requieren validación de clínica antes de declararse política final.

## Dominio: Datos y recursos (RN-DA)

- **RN-DA-01**: Un turno requiere paciente, profesional, box, inicio, fin o una prestación de duración definida y estado.
- **RN-DA-02**: Todo intervalo de turno o bloqueo debe tener un fin estrictamente posterior al inicio.
- **RN-DA-03**: Los datos de pacientes usados en desarrollo, pruebas y semillas son exclusivamente ficticios. No se almacenan datos reales de pacientes en el repositorio.
- **RN-DA-04**: Una prestación debe tener una duración positiva antes de poder calcular un turno.

## Dominio: Disponibilidad (RN-DI)

- **RN-DI-01**: Dos intervalos se solapan si comparten tiempo efectivo; dos turnos son contiguos y válidos cuando el fin del primero es exactamente el inicio del segundo.
- **RN-DI-02**: No puede crearse ni reprogramarse un turno que se solape con un turno activo del mismo profesional.
- **RN-DI-03**: No puede crearse ni reprogramarse un turno que se solape con un turno activo del mismo box.
- **RN-DI-04**: Un bloqueo de disponibilidad impide crear o reprogramar un turno que se solape para el profesional o box bloqueado.
- **RN-DI-05**: Las validaciones de disponibilidad se ejecutan en el dominio, nunca sólo en UI, bot, API o integración.

## Dominio: Ciclo de vida del turno (RN-TU)

- **RN-TU-01**: Cancelar un turno libera su intervalo para nuevas reservas.
- **RN-TU-02**: Reprogramar un turno valida el nuevo intervalo contra ambos recursos y libera el intervalo anterior únicamente al confirmar el cambio válido.
- **RN-TU-03**: Confirmar cambia el estado del turno sin omitir las validaciones que correspondan a cambios de horario o recurso.
- **RN-TU-04**: Crear, reprogramar, cancelar y confirmar deben dejar un historial básico de cambio.

## Dominio: Excepciones globales

- **RN-EX-01**: No se permiten sobreturnos en el primer change; esta es una recomendación de alcance ante la ausencia de una política validada, no una política clínica definitiva.
- **RN-EX-02**: Ninguna integración externa es fuente de verdad de disponibilidad; sólo puede proponer o solicitar una operación que el dominio valide.
- **RN-EX-03**: La seña, el reintegro, la ventana de cancelación, la retención y exportación de datos requieren decisión explícita antes de implementarse.
