# Checklist de Discovery - turnos-odontologia

**Fecha:** 2026-10-01  
**Última actualización:** 2026-10-02 (tras la verificación personal de fuentes)  
**Estado:** investigación documental verificada por el equipo; validación primaria con usuarios sigue abierta y queda registrada como supuesto en la Knowledge Base.

> Convención: “decisión propuesta” no es un hecho comprobado. “No evidenciado” identifica información que no debe transformarse en requisito sin entrevista, demo o fuente adicional.

| # | Punto de Discovery | Síntesis y decisión / evidencia |
|---:|---|---|
| 1 | Problema | Los consultorios necesitan administrar disponibilidad sin duplicar tiempo de profesionales ni sillones/boxes, y manejar cambios de último momento sin perder trazabilidad. La presencia de agenda, recordatorios y confirmaciones en los productos relevados respalda que es un problema de mercado; la magnitud local y sus causas todavía deben validarse con usuarios. |
| 2 | Usuarios | **Primarios propuestos:** recepción/secretaría y odontólogo/a. **Secundarios:** responsable de clínica y paciente que reserva/confirma. **Terceros posteriores:** administrador, liquidador y laboratorio. No se asume que todos requieran la misma vista ni permiso. |
| 3 | Casos de uso | Crear turno para paciente existente/nuevo; consultar agenda diaria/semanal; reservar respetando profesional, box y duración; bloquear disponibilidad; reprogramar; cancelar y liberar recurso; registrar confirmación; listar/auditar cambios. Lista de espera y seña quedan posteriores. |
| 4 | Competidores | El informe comparativo identifica 15: Dentalink, AgendaPro, DentalSoft, Denteo, Dental-IA, Dental Manager, Hi Órbita, Dentiqa, OdontoGRAMA, Odontosys, Dentios, DentalQub, Simples Dental, Clinicorp y Odensys. Fuente: [informe de Discovery](informe-discovery.md#A-tabla-comparativa). |
| 5 | Funcionalidades necesarias | Agenda por profesional y box; duración por prestación; validación anti-solapamiento; alta/consulta/reprogramación/cancelación; bloqueos; estados del turno; datos mínimos de paciente; agenda día/semana; pruebas automatizadas de escenario feliz, conflicto y turnos contiguos. |
| 6 | Funcionalidades opcionales | Recordatorios WhatsApp, confirmación digital, lista de espera, seña, exportación, auditoría enriquecida, Google Calendar, dashboard de ocupación. Odontograma e historia clínica completa no entran al primer MVP. |
| 7 | Reglas de negocio | Un turno requiere paciente, profesional, inicio, fin y estado. Un recurso profesional o box no puede estar reservado en intervalos que se intersecten; un turno que empieza exactamente al terminar otro es válido. Cancelar/reprogramar libera el intervalo previo. Las validaciones deben ejecutarse en el dominio, no sólo en UI/bot. Política de sobreturnos: **No evidenciado en nuestras fuentes al 2026-10-01**; la verificación personal del 2026-10-02 encontró que DentalSoft publica “sobreturnos con detección automática de solapamiento”, pero sin documentar la regla de turnos contiguos ni la doble restricción de profesional y box. Se mantiene la recomendación de no admitir sobreturnos en el primer change. |
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

- [x] Leímos el informe y abrimos personalmente al menos cinco fuentes de tipos distintos. *(2026-10-02: seis fuentes abiertas por el equipo — Dentalink, AgendaPro, DentalSoft, Simples Dental, Dentios y Denteo — con cuatro correcciones aplicadas al informe.)*
- [ ] Confirmamos o corregimos los usuarios y los casos de uso con al menos una entrevista/observación de consultorio. **Abierto:** no se hizo; queda como supuesto en `knowledge-base/10_preguntas_abiertas.md`.
- [ ] Acordamos la política de cancelación, reprogramación y sobreturno para el MVP. **Abierto:** el primer change no incluye sobreturnos ni política de cancelación; queda como pregunta abierta.
- [x] No convertimos celdas “No evidenciado” en requisitos sin nueva evidencia.
- [x] Confirmamos que el primer change será pequeño y verificable: crear turno sin solapamientos por profesional y box. *(C-01, archivado.)*

**Decisión: Continuar con supuestos documentados (2026-10-02).** Se aplicó **Ajustar** a las cuatro celdas que la verificación personal encontró incorrectas (precios de DentalSoft y Dentios, Mercado Pago de DentalSoft, odontograma/respaldos de Denteo, exportación de Dentalink y costo de WhatsApp de Simples Dental) y las correcciones quedaron en el informe. Las dos verificaciones sin resolver se declaran abiertas en lugar de marcarse como cumplidas; por eso la Knowledge Base debe conservar esos puntos en `10_preguntas_abiertas.md`. La alternativa “Continuar sin registrar los supuestos” se descartó porque habría hecho pasar huecos de información por requisitos confirmados.
