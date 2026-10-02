# Checklist de Discovery - turnos-odontologia

**Fecha:** 2026-10-01  
**Estado:** borrador fundamentado en investigación secundaria; requiere validación de usuarios antes de aprobarlo para la Knowledge Base.

> Convención: “decisión propuesta” no es un hecho comprobado. “No evidenciado” identifica información que no debe transformarse en requisito sin entrevista, demo o fuente adicional.

| # | Punto de Discovery | Síntesis y decisión / evidencia |
|---:|---|---|
| 1 | Problema | Los consultorios necesitan administrar disponibilidad sin duplicar tiempo de profesionales ni sillones/boxes, y manejar cambios de último momento sin perder trazabilidad. La presencia de agenda, recordatorios y confirmaciones en los productos relevados respalda que es un problema de mercado; la magnitud local y sus causas todavía deben validarse con usuarios. |
| 2 | Usuarios | **Primarios propuestos:** recepción/secretaría y odontólogo/a. **Secundarios:** responsable de clínica y paciente que reserva/confirma. **Terceros posteriores:** administrador, liquidador y laboratorio. No se asume que todos requieran la misma vista ni permiso. |
| 3 | Casos de uso | Crear turno para paciente existente/nuevo; consultar agenda diaria/semanal; reservar respetando profesional, box y duración; bloquear disponibilidad; reprogramar; cancelar y liberar recurso; registrar confirmación; listar/auditar cambios. Lista de espera y seña quedan posteriores. |
| 4 | Competidores | El informe comparativo identifica 15: Dentalink, AgendaPro, DentalSoft, Denteo, Dental-IA, Dental Manager, Hi Órbita, Dentiqa, OdontoGRAMA, Odontosys, Dentios, DentalQub, Simples Dental, Clinicorp y Odensys. Fuente: [informe de Discovery](informe-discovery.md#A-tabla-comparativa). |
| 5 | Funcionalidades necesarias | Agenda por profesional y box; duración por prestación; validación anti-solapamiento; alta/consulta/reprogramación/cancelación; bloqueos; estados del turno; datos mínimos de paciente; agenda día/semana; pruebas automatizadas de escenario feliz, conflicto y turnos contiguos. |
| 6 | Funcionalidades opcionales | Recordatorios WhatsApp, confirmación digital, lista de espera, seña, exportación, auditoría enriquecida, Google Calendar, dashboard de ocupación. Odontograma e historia clínica completa no entran al primer MVP. |
| 7 | Reglas de negocio | Un turno requiere paciente, profesional, inicio, fin y estado. Un recurso profesional o box no puede estar reservado en intervalos que se intersecten; un turno que empieza exactamente al terminar otro es válido. Cancelar/reprogramar libera el intervalo previo. Las validaciones deben ejecutarse en el dominio, no sólo en UI/bot. Política de sobreturnos: **No evidenciado**; se recomienda no permitirla en el primer change. |
| 8 | Integraciones | Prioridad posterior: WhatsApp (notificación/confirmación), Mercado Pago (seña) y Google Calendar. ARCA, obras sociales, radiología, firma y API pública quedan fuera del MVP. Credenciales reales y datos de pacientes nunca se guardan en el repositorio. |
| 9 | Restricciones | Mercado argentino; idioma español; datos ficticios en desarrollo/pruebas; interfaz no es requisito inicial; no depender de cuentas externas para ejecutar tests. La definición legal de seguridad, privacidad, consentimiento, conservación y residencia de datos requiere revisión especializada: **No evidenciado**. |
| 10 | Riesgos | (a) Asumir que WhatsApp/IA puede reservar sin controlar recursos; (b) almacenar datos sensibles sin políticas validadas; (c) intentar facturación/obras sociales antes de estabilizar agenda; (d) reglas de seña/cancelación no acordadas; (e) confundir una declaración comercial con capacidad probada. Mitigación: dominio probado primero, datos simulados, demo/documentación y decisiones registradas. |
| 11 | Preguntas abiertas | ¿Cuántos boxes, profesionales y sucursales debe soportar el alcance? ¿Qué tipos/duraciones de prestación hay? ¿Quién puede reprogramar/cancelar y hasta cuándo? ¿Se admiten sobreturnos? ¿Cómo se trata seña/reintegro? ¿Cuál es el canal de recordatorio y consentimiento? ¿Qué retención/exportación exigen las clínicas? ¿Cómo se integra cada obra social? |

## Hipótesis a validar con entrevistas

1. La prevención de solapamientos de profesional y box es más valiosa que la automatización con IA en la primera versión.
2. El canal de comunicación prioritario es WhatsApp, pero su uso debe funcionar como consecuencia de un turno válido y no como fuente de verdad de disponibilidad.
3. La agenda semana/día y una reprogramación rápida cubren el núcleo diario de recepción.
4. Señas, obras sociales, facturación y clínica completa aumentan el valor, pero no deben impedir que el primer change pueda especificarse y probarse de forma aislada.

## Gate de revisión humana

> La investigación documental puede haber sido realizada con asistencia de IA, pero la
> verificación personal de fuentes exigida por la consigna sólo cuenta cuando un integrante
> abre y contrasta las fuentes y registra el resultado.


Antes de avanzar a Knowledge Base, el equipo debe elegir **Continuar / Ajustar / Parar acá** y dejar respuesta a estas verificaciones:

- [ ] Leímos el informe y abrimos personalmente al menos cinco fuentes de tipos distintos.
- [ ] Confirmamos o corregimos los usuarios y los casos de uso con al menos una entrevista/observación de consultorio.
- [ ] Acordamos la política de cancelación, reprogramación y sobreturno para el MVP.
- [ ] No convertimos celdas “No evidenciado” en requisitos sin nueva evidencia.
- [ ] Confirmamos que el primer change será pequeño y verificable: crear turno sin solapamientos por profesional y box.

**Decisión actual:** Ajustar. Falta validación primaria y selección explícita del alcance por el equipo.
