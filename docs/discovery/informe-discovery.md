# Informe de Discovery - Sistema de turnos y agenda para consultorios odontológicos

**Materia:** Metodología I  
**Proyecto:** `turnos-odontologia`  
**Integrantes:** Santiago Barretto, Mateo Algañaraz, Ezequiel Menéndez  
**Fecha de consulta de fuentes:** 2026-10-01  
**Verificación personal de fuentes:** 2026-10-02  
**Versión:** 1.1 - investigación documental inicial verificada y corregida

> Alcance y criterio de evidencia. Este informe releva páginas oficiales y centros de ayuda públicos. “Comprobado” significa que la funcionalidad aparece en la fuente enlazada; no implica una prueba independiente del producto. “Afirmación comercial” identifica una declaración del proveedor aún no validada en una demo. “No evidenciado” no significa que el producto no posea la función: significa que no se localizó respaldo público en las fuentes consultadas. Los precios, planes y obligaciones regulatorias deben reconfirmarse antes de contratar.

## Resumen ejecutivo

Se investigaron quince productos que compiten directamente en gestión odontológica o resuelven una parte relevante del circuito de turnos para consultorios argentinos. El mercado ya considera básico disponer de agenda web, recordatorios y ficha clínica; varios productos locales añaden odontograma, caja, obras sociales y WhatsApp. La reserva autónoma, la reprogramación por mensajería y la protección contra solapamientos también están ampliamente presentes en las propuestas comerciales.

La oportunidad no es “hacer otra agenda”. El MVP debe resolver con fiabilidad la reserva por profesional **y por sillón/box**, los cambios y cancelaciones trazables, y una experiencia de paciente apropiada para Argentina (WhatsApp y seña opcional). Como diferenciación, se propone transparencia operativa: reglas de disponibilidad visibles, lista de espera que cubra cancelaciones y auditoría/exportación desde el inicio. No se recomienda implementar historia clínica exhaustiva, facturación electrónica, IA conversacional ni integraciones clínicas en el primer change: elevan alcance y exigen validación legal y técnica adicional.

Los cinco proveedores prioritarios para pedir demo son Dentalink, AgendaPro Dental, DentalSoft, Denteo y Dentiqa. Se seleccionan por cercanía al mercado argentino y por evidencia pública de agenda, odontología y/o integraciones locales. Simples Dental, Dentios y DentalQub sirven como referencias de experiencia de usuario y operación, no como equivalentes regulatorios argentinos.

## A. Tabla comparativa

### Lectura de la tabla

Cada vínculo de “Fuente” lleva a la página oficial concreta relevada el 2026-10-01. Las celdas condensan sólo atributos publicados allí. **FC** = funcionalidad clínica; **ADM** = administración/cobros; **SEG** = seguridad, exportación o trazabilidad. Una ausencia se escribe literalmente “No evidenciado”. El país se informa sólo si la fuente lo declara o si el proveedor se presenta expresamente como local; de otro modo se conserva “No evidenciado”.

> **Actualización 2026-10-02.** Seis fuentes fueron abiertas y contrastadas personalmente por el equipo (filas 1, 2, 3, 4, 11 y 13). Las correcciones resultantes ya están incorporadas en las tablas A y B y en el análisis C; el detalle está en [Verificación de fuentes](#verificación-de-fuentes).

| # | Producto / proveedor / país declarado | Segmento y modalidad | Agenda y capacidad | Turnos digitales y automatización | FC | ADM e integraciones | Operación, SEG y comercial | Fuente y fecha |
|---:|---|---|---|---|---|---|---|---|
| 1 | Dentalink / Engenis SpA / Chile (operación AR publicada) | Consultorio y clínica; web/SaaS | Vistas diaria, semanal y por profesional; ocupación de sillones | Reserva 24/7 por enlace, WhatsApp, redes y web; recordatorios | Expediente, odontograma y periodontograma | Financiamiento/pagos: comprobado para México; Mercado Pago y ARCA: No evidenciado | Entrega de toda la información almacenada al cancelar el servicio: afirmación comercial; cumplimiento argentino, API pública y precios publicados: No evidenciado | [Agenda AR](https://www.softwaredentalink.com/ar/atrae-mas-pacientes/agendamiento-online) y [producto](https://web-mx.softwaredentalink.com/) - 2026-10-01, verificada 2026-10-02 |
| 2 | AgendaPro / AgendaPro Inc. / No evidenciado | Clínicas y salud; SaaS/web y app | Turnos configurables por práctica/profesional; uno o varios sillones | Reserva 24/7, sitio/enlace, WhatsApp, SMS y email | Historia clínica dental, tratamientos e imágenes | Pagos/señas, comisiones, caja y reportes; pago online disponible en AR | Seguridad, auditoría, exportación y precio publicado: No evidenciado; prueba gratuita: afirmación comercial | [Dental AR](https://agendapro.com/ar/dental/software-odontologico) y [sitio de reservas](https://ayuda.agendapro.com/es/articles/6126081-como-configuro-mi-sitio-web) - 2026-10-01, verificada 2026-10-02 |
| 3 | DentalSoft / DentalSoft / Argentina (equipo argentino declarado) | Clínicas y profesionales; nube/SaaS | Día, semana y mes; bloqueos, urgencias, multi-sucursal y sobreturnos con detección de solapamiento | Turnos online/web (plan Pro), chatbot; recordatorios por WhatsApp/email y actualización por confirmación/cancelación | Ficha, odontograma FDI e historial | Caja/cobros (efectivo, tarjeta, transferencia, Mercado Pago y obra social), presupuestos, liquidaciones de profesionales/obras sociales, reportes; Google Calendar | Precios publicados: gratis 6 meses (hasta 50 turnos), Gestión $30.000/mes y Pro $60.000/mes (+$10.000 por profesional adicional); seguridad, exportación, API y ARCA: No evidenciado | [Producto](https://www.dentalsoft.com.ar/) - 2026-10-01, verificada 2026-10-02 |
| 4 | Denteo Clínica / Denteo / Argentina (“Hecho en Argentina”) | Consultorios, clínicas y laboratorios; nube | Agenda visual; sillones, prevención de solapamientos y duración variable: No evidenciado | WhatsApp con plantillas aprobadas; turnos online, cancelación y reprogramación: No evidenciado | Historia clínica con odontograma y presupuestos: comprobado en la página; periodontograma: No evidenciado | Facturación electrónica ARCA, Mercado Pago, Google Calendar y WhatsApp Business declarados | Servidor propio en Argentina y respaldo diario fuera del servidor declarados; Ley 25.326 citada; exportación, auditoría, roles de la clínica y API: No evidenciado; prueba 15 días | [Producto](https://denteo.com.ar/) - 2026-10-01, verificada 2026-10-02 |
| 5 | Dental-IA / Dental-IA / Argentina (presentación pública) | Consultorios odontológicos; plataforma web | Agenda y disponibilidad por profesional/box: No evidenciado | Asistente oficial WhatsApp: confirma, cancela, reprograma y cobra seña por Mercado Pago | Odontograma digital multicapa FDI; ficha/anamnesis e imágenes: No evidenciado | Mercado Pago comprobado; caja, ARCA, obras sociales y reportes: No evidenciado | Integración oficial con Meta: afirmación comercial; roles, auditoría, exportación, precios y seguridad: No evidenciado | [Producto](https://www.dentalia.com.ar/) - 2026-10-01 |
| 6 | Dental Manager / Dental Manager / Argentina (declarado) | Clínica; SaaS/nube | Día, semana o mes; multi-profesional, horarios y sin solapamientos (afirmación comercial) | Bot WhatsApp 24/7 para alta, cambio y cancelación de turnos | Historial, odontograma, prestaciones y evolución | Obra social en ficha; caja, pagos, ARCA, Mercado Pago y reportes: No evidenciado | Nube y prueba de 30 días; roles, auditoría, exportación, seguridad y precio: No evidenciado | [Producto](https://dentalmanager.com.ar/) - 2026-10-01 |
| 7 | Hi Órbita / Órbita Gestión / Argentina (declarado) | Clínicas y consultorios; sistema de gestión + asistente | Agenda por sillón y por profesional | Asistente de WhatsApp que gestiona turnos: afirmación comercial; reserva web, confirmación y cancelación: No evidenciado | Ficha con odontograma | Obras sociales y caja; facturación, MP, ARCA y reportes: No evidenciado | Seguridad, auditoría, exportación, roles y precios: No evidenciado | [Producto](https://hiorbita.com/) - 2026-10-01 |
| 8 | Dentiqa / Dentiqa / Argentina (mercado AR declarado) | Clínicas; SaaS, disponible en LatAm | Multi-dentista, día/semana, bloqueos por profesional y validación de horario | Chatbot IA WhatsApp 24/7, recordatorios, campañas; reserva web/enlace: No evidenciado | Odontograma y periodontograma, imágenes, plan/presupuesto, firma y consentimientos | Estadísticas e ingresos facturados; Mercado Pago, ARCA y obras sociales: No evidenciado | Meta Business API oficial: afirmación comercial; multi-clínica; auditoría/exportación/seguridad/precios: No evidenciado | [Producto](https://dentiqa.app/ar) - 2026-10-01 |
| 9 | OdontoGRAMA / proveedor no identificado públicamente / Argentina (dominio local; origen legal no evidenciado) | Consultorio; nube, PC/tablet/celular | Agendas personalizables y control de asistencia; recursos/sillones y prevención de solapamientos: No evidenciado | Reserva online, WhatsApp, confirmación, cancelación y reprogramación: No evidenciado | Ficha, imágenes, tratamientos y diagnósticos; odontograma/periodontograma: No evidenciado | Caja, cuentas corrientes, facturación a prepagas/obras sociales, gastos y estadísticas | Respaldo/protección 24x7: afirmación comercial; roles, auditoría, exportación y API: No evidenciado; cuenta gratis | [Producto](https://www.odontograma.com.ar/) - 2026-10-01 |
| 10 | Odontosys / Odontosys / No evidenciado | Clínicas dentales; acceso desde dispositivos/nube (declarado) | Agenda; recursos/sillones, reserva online, cancelación y reprogramación: No evidenciado | Confirmación automática por WhatsApp y email | Historia, imágenes/RX, odontograma y periodontograma | Cuentas y pago registrado; facturación, integraciones locales y obras sociales: No evidenciado | Datos cifrados en AWS declarados; exportación, auditoría, roles, precios y API: No evidenciado | [Producto](https://odontosys.com/) - 2026-10-01 |
| 11 | Dentios / Dentios / Chile (diseñado en Chile declarado) | Clínicas dentales; SaaS | Agenda en tiempo real por doctor/box y reservas online | Estados por WhatsApp y recordatorios automáticos (automáticos en plan Premium; manuales en Base) | Ficha, odontograma y diagnóstico; RX IA: afirmación comercial | Cobros POS TUU y boletas chilenas; integraciones AR/ARCA/MP: No evidenciado | Precios publicados: plan gratuito $0 CLP, Base 0,80 UF ($30.600/mes IVA inc.) y Premium 1,30 UF ($49.725/mes IVA inc.); seguridad declarada: SSL grado bancario y respaldo horario (FAQ); prueba 30 días; roles, auditoría y exportación: No evidenciado | [Producto](https://dentios.cl/) - 2026-10-01, verificada 2026-10-02 |
| 12 | DentalQub / DentalQub / Chile (normativa chilena declarada) | Dentistas y clínicas; SaaS | Día/semana/mes; agenda, profesionales y recursos: No evidenciado | WhatsApp y agenda; reserva online, recordatorios, cancelación y reprogramación: No evidenciado | Fichas y odontograma | Pagos, seguros y SII electrónico; ARCA/MP: No evidenciado | Alineación con normativa chilena declarada; prueba 7 días y precio desde 0,67 UF/mes; exportación/auditoría/API: No evidenciado | [Producto](https://dentalqub.cl/) - 2026-10-01 |
| 13 | Simples Dental / Simples Dental / Brasil (mercado BR declarado) | Clínicas odontológicas; agenda online, web/app | Día/semana/profesional/silla, control de sillas y panel de encajes | Enlace 24h, confirmaciones y recordatorios WhatsApp/SMS/app; Copiloto WhatsApp; Secretária IA en pre-lanzamiento | Prontuario/historial; odontograma, imágenes y presupuestos: No evidenciado en fuente principal | Gestión financiera y reportes; integraciones argentinas/MP/ARCA: No evidenciado | Permisos de agenda; LGPD: afirmación comercial; prueba 7 días sin tarjeta; el envío automático requiere saldo de WhatsApp (costo por mensaje); exportación/auditoría/API: No evidenciado | [Agenda](https://www.simplesdental.com/agenda-online) y [ayuda WhatsApp](https://ajuda.simplesdental.com/pt-BR/articles/3659017-como-ativar-a-confirmacao-de-consulta-automatica-por-whatsapp) - 2026-10-01, verificada 2026-10-02 |
| 14 | Clinicorp / Clinicorp / Brasil (operación brasileña; origen legal no evidenciado) | Clínicas odontológicas; SaaS | Agenda inteligente; recursos/sillones y prevención de solapamiento: No evidenciado | Confirmación automática por WhatsApp; SMS, email y app Clini.me publicados | Prontuario digital; odontograma/periodontograma e imágenes: No evidenciado en fuente revisada | Informes sobre faltas/desmarcaciones; cobros/facturación/integraciones AR: No evidenciado | Seguridad, exportación, auditoría, roles, precios y API: No evidenciado | [Producto](https://www.clinicorp.com/) y [material oficial](https://conteudos.clinicorp.com/hubfs/Materiais%20Ricos/Checklist%20Guia%20de%20atividades%20para%20a%20secret%C3%A1ria%20de%20odontologia.pdf) - 2026-10-01 |
| 15 | Odensys / Odensys / México y Perú (mercados declarados; origen legal no evidenciado) | Odontólogos y clínicas; nube | Agenda y recordatorios; recursos/sillones, reserva, cancelación y reprogramación: No evidenciado | Recordatorios; WhatsApp, enlace, chatbot y campañas: No evidenciado | Historia clínica y odontograma | Facturación y pagos; integraciones locales AR/MP/ARCA: No evidenciado | Acceso desde cualquier dispositivo; seguridad, exportación, auditoría, roles, precios y API: No evidenciado | [Producto](https://odensys.com/software-dental) - 2026-10-01 |

### Observaciones de evidencia

- La presencia de una interfaz de demostración o una frase de marketing no se trató como prueba de performance, cobertura legal ni disponibilidad en todos los planes.
- Las afirmaciones de automatización con IA, reducción de ausencias, protección de datos y cantidad de clientes deben verificarse en demo, contrato y política de privacidad. No se usaron como hechos para el MVP.
- Los productos de Brasil, Chile, México y Perú son referencias funcionales; no prueban compatibilidad con ARCA, Mercado Pago, obras sociales ni normativa argentina.

## B. Matriz ponderada de 0 a 5

**Pesos exigidos:** gestión de turnos y automatización 25%; funcionalidad clínica odontológica 20%; integraciones locales y WhatsApp 15%; administración, cobros y facturación 15%; experiencia del paciente 10%; seguridad, exportación y trazabilidad 10%; precio y facilidad de adopción 5%.

**Nota metodológica.** 0 = No evidenciado en las fuentes seleccionadas; 1 = mención muy limitada o genérica; 2 = evidencia parcial de una parte de la categoría; 3 = cobertura funcional comprobada pero incompleta o sin evidencia local; 4 = cobertura amplia en la fuente oficial; 5 = cobertura amplia con demostración, ayuda pública o evidencia específica para el caso. No se premió una afirmación comercial sin detalle operativo. El total es `Σ(nota × peso)` y ordena evidencia pública, no calidad real ni recomendación de compra.

| Producto | Turnos 25% | Clínica 20% | Local/WhatsApp 15% | ADM 15% | Paciente 10% | SEG/export. 10% | Precio/adopción 5% | Total / 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Dentalink | 5 | 5 | 3 | 4 | 4 | 2 | 1 | **3,95** |
| DentalSoft | 4 | 4 | 4 | 4 | 4 | 1 | 4 | **3,70** |
| Simples Dental | 5 | 2 | 4 | 4 | 5 | 1 | 4 | **3,65** |
| AgendaPro Dental | 4 | 4 | 4 | 4 | 4 | 1 | 3 | **3,65** |
| Dentios | 4 | 4 | 3 | 4 | 3 | 2 | 4 | **3,55** |
| Dentiqa | 4 | 5 | 4 | 2 | 4 | 1 | 2 | **3,50** |
| Odontosys | 3 | 5 | 2 | 2 | 2 | 3 | 1 | **2,90** |
| Denteo | 3 | 2 | 4 | 4 | 2 | 2 | 3 | **2,90** |
| DentalQub | 2 | 3 | 2 | 4 | 2 | 3 | 5 | **2,75** |
| Dental Manager | 4 | 3 | 3 | 1 | 3 | 0 | 4 | **2,70** |
| Dental-IA | 3 | 3 | 4 | 1 | 4 | 0 | 2 | **2,60** |
| Hi Órbita | 3 | 3 | 3 | 2 | 2 | 0 | 1 | **2,35** |
| Clinicorp | 3 | 2 | 3 | 2 | 3 | 0 | 1 | **2,25** |
| Odensys | 2 | 4 | 1 | 3 | 1 | 0 | 3 | **2,15** |
| OdontoGRAMA | 2 | 2 | 1 | 4 | 1 | 1 | 5 | **2,10** |

**Correcciones de la verificación personal (2026-10-02).** DentalSoft pasó de 2 a 4 en precio/publicación de planes (antes “No evidenciado”, ahora con montos publicados en la fuente oficial); Dentios de 1 a 2 en SEG y Denteo de 1 a 2 en SEG (respaldos y seguridad declarados con detalle en la fuente). El resto de las notas no cambió. La selección de demos de la sección D no sigue el orden exacto de esta matriz: además de la puntuación considera cercanía al mercado argentino.

## C. Análisis competitivo

### Estándar de mercado

La agenda digital, recordatorios por WhatsApp/SMS/email, ficha clínica y reportes aparecen repetidamente. En los productos odontológicos maduros también son frecuentes el odontograma, presupuestos, pagos/caja y vistas por profesional. La reserva desde enlace, web o redes está explícita en Dentalink, AgendaPro, Simples Dental y DentalSoft. Por lo tanto, un MVP que sólo permita crear un turno manual no sería competitivo, aunque sí puede ser el primer change del proyecto.

### Diferenciadores reales observables

- Gestión explícita de sillones/boxes: Dentalink, Dentios, Simples Dental y Hi Órbita la publican; su importancia es mayor que una agenda genérica para una clínica dental.
- Automatización conversacional: Dental-IA, Dental Manager, Dentiqa, Hi Órbita y Simples Dental publican bots o asistentes por WhatsApp. Debe probarse si efectivamente respetan restricciones de agenda.
- Integración local visible: Denteo publica ARCA, Mercado Pago, Google Calendar y WhatsApp Business. DentalSoft publica tratamiento de obras sociales y Google Calendar. Esa cercanía local es más relevante para Argentina que funciones fiscales de Chile o Brasil.
- Clínica documentada: Dentalink y Dentiqa publican odontograma/periodontograma; el segundo además menciona firma, consentimientos e imágenes. Esto es un diferenciador frente a agendas generalistas, pero no corresponde al primer alcance.

### Vacíos frecuentes para Argentina

1. En la evidencia revisada es escasa la documentación pública de reglas formales contra el doble uso simultáneo de profesional **y** sillón/box, incluyendo el caso de borde de dos turnos contiguos. La única mención pública encontrada en la verificación personal (2026-10-02) es la de DentalSoft, que publica “sobreturnos con detección automática de solapamiento”, sin documentar la regla de turnos contiguos ni la doble restricción de profesional y box a la vez.
2. Pocos sitios documentan exportación de datos, log de auditoría, políticas de retención, roles detallados o API pública. Para datos de salud no se debe inferir cumplimiento legal a partir de iconos de seguridad.
3. Se publicitan WhatsApp y cobros, pero suelen faltar condiciones de los planes, costos por mensajes, alcances de cancelación, reversas de seña y comportamiento cuando una conversación automatizada falla.
4. No se encontró evidencia pública suficiente sobre interoperabilidad con radiología, firma digital, ARCA/obras sociales y Mercado Pago en la mayoría de los competidores. La ausencia documental debe convertirse en preguntas de demo, no en una conclusión de inexistencia.

### Oportunidades de innovación

- Modelar disponibilidad como recursos combinados (profesional, sillón/box, prestación y duración), impedir solapamientos de forma determinista y explicar al usuario la causa del rechazo.
- Diseñar una lista de espera accionable: ante cancelación, ofrecer sólo horarios compatibles, registrar la respuesta y evitar duplicaciones.
- Hacer trazable cada cambio: quién creó, reprogramó, canceló o confirmó, qué horario se liberó y qué notificación se envió.
- Priorizar una integración de WhatsApp que nunca reserve fuera de las reglas del calendario; la IA debe proponer, no eludir validaciones de dominio.
- Ofrecer exportación legible de datos y configuración de consentimiento/retención desde el inicio. La adecuación jurídica requiere revisión profesional independiente.

## D. Recomendación final

### Cinco competidores para demo

1. **Dentalink:** confirmar reglas de recursos, disponibilidad de módulos/planes argentinos, exportación y evidencia de auditoría.
2. **AgendaPro Dental:** evaluar reserva 24/7, seña/pago en Argentina, el uso real de sillones y la historia clínica dental.
3. **DentalSoft:** validar agenda con bloqueos, sincronización con Google Calendar, liquidaciones/obras sociales y límites del chatbot.
4. **Denteo:** revisar integración efectiva con ARCA, Mercado Pago y WhatsApp Business, más residencia/seguridad de datos y trazabilidad.
5. **Dentiqa:** probar bloqueo por profesional, flujo del bot de WhatsApp y la relación entre agenda, odontograma y campañas.

### Tres referencias para experiencia de usuario

- **Simples Dental:** jerarquía visual de agenda por día/semana/profesional/silla y confirmaciones.
- **Dentios:** panel de agenda por box y estados de turno visibles.
- **DentalQub:** presentación de agenda, cobros y precio/prueba claramente comunicados.

### MVP sugerido

**Imprescindible**

- Alta, consulta, reprogramación y cancelación de turnos.
- Disponibilidad por profesional y sillón/box, duración por prestación y bloqueo de horarios.
- Prevención transaccional de solapamientos; se permiten turnos contiguos, no superpuestos.
- Datos mínimos de paciente y estado del turno; historial de cambios básico.
- Agenda diaria/semanal y recordatorio manual o integración de mensajería simulada/documentada para no depender de una API real en el primer change.

**Diferenciadores que siguen al MVP**

- Lista de espera con ofertas compatibles al liberarse un horario.
- Registro de auditoría de cambios y exportación CSV/JSON para el dueño de la clínica.
- Confirmación/cancelación por WhatsApp que pasa por las mismas reglas de dominio que la UI.
- Seña opcional con estado de pago separado del estado del turno; integración real sólo tras validar proveedor y requisitos.

**Etapas posteriores**

- Odontograma, periodontograma, imágenes, anamnesis, recetas, firma y tratamiento clínico completo.
- Facturación ARCA, obras sociales, liquidaciones y conciliación de cobros.
- Chatbot/IA, campañas de marketing, radiología, APIs públicas y multi-sucursal avanzada.
- Evaluación legal de privacidad, consentimiento, retención, seguridad y contratación de servicios externos.

## Verificación de fuentes

### Verificación documental de las fuentes

La siguiente comprobación documental fue realizada contra la página enlazada el **2026-10-01**.
Sirve para auditar y corregir el informe. La **verificación personal** exigida por la consigna
se hizo el **2026-10-02** y está registrada más abajo, en “Verificación personal de las fuentes”.

| Tipo / fuente comprobada | Afirmación usada en el informe | Hallazgo en la URL | Resultado / corrección |
|---|---|---|---|
| Sitio oficial de producto: [Dentalink AR](https://www.softwaredentalink.com/ar/atrae-mas-pacientes/agendamiento-online) | Vistas diaria/semanal/profesional, control de sillones y reserva 24/7 en WhatsApp/redes/web | La página enumera las tres vistas, ocupación de sillones y enlace de reserva 24/7. | Confirmada. No se afirmó Mercado Pago ni ARCA porque no aparecen en esa fuente. |
| Página de producto: [AgendaPro Dental AR](https://agendapro.com/ar/dental/software-odontologico) | Turnos por práctica/profesional, reserva sin registro, sillones, seña y clínica dental | El contenido publica esas capacidades y pagos/señas. | Confirmada. Seguridad, auditoría y exportación quedaron “No evidenciado”. |
| Sitio oficial: [DentalSoft](https://www.dentalsoft.com.ar/) | Agenda con bloqueos/multi-sucursal, WhatsApp/email, odontograma y Google Calendar | La página describe esos módulos y aclara que los recordatorios actualizan la agenda ante confirmación/cancelación. | Confirmada. No se dedujo integración oficial de Meta ni cumplimiento ARCA. |
| Centro de ayuda: [Simples Dental - confirmación automática](https://ajuda.simplesdental.com/pt-BR/articles/3659017-como-ativar-a-confirmacao-de-consulta-automatica-por-whatsapp) | Confirmación automática por WhatsApp configurable desde agenda | La guía indica activar WhatsApp en Comunicación y crear el turno; contempla decisión individual de envío. | Confirmada. Las capacidades de IA permanecen como pre-lanzamiento o afirmación comercial según la fuente. |
| Sitio oficial: [Dentios](https://dentios.cl/) | Agenda por doctor/box, reservas, WhatsApp, ficha, odontograma y POS | La página muestra calendario por box, estados WhatsApp, reserva online, ficha/odontograma y alianza POS TUU. | Confirmada para Chile. No se extrapoló la integración fiscal/POS a Argentina. |
| Sitio oficial: [Denteo](https://denteo.com.ar/) | Producto argentino con ARCA, Google Calendar, WhatsApp Business y Mercado Pago | La página nombra esas integraciones y su prueba de 15 días. | Confirmada como declaración del proveedor. Se mantuvo “No evidenciado” para auditoría, exportación y detalle de seguridad. |

### Verificación personal de las fuentes (2026-10-02)

Cada integrante del equipo abrió las siguientes fuentes en un navegador y contrastó lo que el informe afirmaba con lo que la URL mostraba ese día. Las discrepancias detectadas se corrigieron en las secciones A, B y C con la decisión **Ajustar**; ninguna corrección se hizo por deducción.

| Tipo y fuente | Qué afirmaba el informe | Qué se encontró (2026-10-02) | Resultado / corrección |
|---|---|---|---|
| Sitio oficial: [Dentalink AR](https://www.softwaredentalink.com/ar/atrae-mas-pacientes/agendamiento-online) | Vistas diaria/semanal/profesional, ocupación de sillones y reserva 24/7 por link/WhatsApp/redes/web | La página publica las tres vistas, “control total de la ocupación de tus sillones”, turnos online 24/7 y link de reserva en WhatsApp/Instagram/web. Además declara entrega rápida de toda la información al cancelar el servicio. | **Confirmada y ampliada.** Se pasó “exportación: No evidenciado” a “entrega de la información al cancelar: afirmación comercial”. Precios siguen sin montos publicados (sólo nombres de planes). |
| Página de producto: [AgendaPro Dental AR](https://agendapro.com/ar/dental/software-odontologico) | Turnos por práctica/profesional, reserva sin registro, sillones, seña, comisiones, WhatsApp/SMS/email, historia clínica con imágenes | Todo eso aparece publicado, más “más de 135.000 profesionales” como frase de marketing. | **Confirmada sin cambios.** El dato de 135.000 profesionales queda como afirmación comercial, no como hecho. |
| Sitio oficial: [DentalSoft](https://www.dentalsoft.com.ar/) | Agenda día/semana/mes con bloqueos y multi-sucursal; recordatorios WhatsApp/email; caja, liquidaciones, reportes; precios: No evidenciado | Precios publicados: gratis 6 meses (hasta 50 turnos, 1 odontólogo), Gestión $30.000/mes, Pro $60.000/mes (+$10.000 por profesional). Caja con Mercado Pago. Publica “urgencias y sobreturnos con detección automática de solapamiento”. Turnos online y chatbot figuran en el plan Pro. | **Corregida en tres celdas:** precios publicados, Mercado Pago en ADM y sobreturnos en agenda. Recalculada la matriz B (precio 2 → 4). |
| Centro de ayuda: [Simples Dental - confirmación automática](https://ajuda.simplesdental.com/pt-BR/articles/3659017-como-ativar-a-confirmacao-de-consulta-automatica-por-whatsapp) | Confirmación automática configurable, con envío y decisión individual por turno | La guía confirma mensaje 24 h antes + recordatorio 2 h antes, toggle por consulta y estados verde/rojo en agenda; exige saldo de WhatsApp Utilities para enviar. | **Confirmada con matiz de costo:** se agregó “el envío automático requiere saldo de WhatsApp (costo por mensaje)”. |
| Sitio oficial: [Dentios](https://dentios.cl/) | Agenda por doctor/box, reservas online, estados por WhatsApp, ficha/odontograma, POS TUU; precios y seguridad: No evidenciado | Precios publicados: plan gratuito $0 CLP, Base 0,80 UF ($30.600/mes IVA inc.), Premium 1,30 UF ($49.725/mes IVA inc.); FAQ declara SSL grado bancario y respaldos automáticos cada hora; recordatorios automáticos sólo en Premium. | **Corregida en dos celdas:** precios publicados y seguridad con detalle. Recalculada la matriz B (SEG 1 → 2). |
| Sitio oficial: [Denteo](https://denteo.com.ar/) | ARCA, Mercado Pago, Google Calendar, WhatsApp Business, servidor argentino, prueba 15 días; odontograma y seguridad: No evidenciado | Todo eso aparece; además “Historia clínica con odontograma”, “Backup diario” fuera del servidor y cita a la Ley 25.326. Los roles publicados son de Denteo Lab, no de la clínica. | **Corregida en dos celdas:** odontograma comprobado y seguridad con respaldos declarados. Recalculada la matriz B (SEG 1 → 2). Roles de clínica siguen “No evidenciado”. |

**Resultado agregado:** 6 de 6 fuentes abiertas; 4 requirieron corrección del informe (Dentalink, DentalSoft, Dentios, Denteo), 1 se confirmó con matiz (Simples Dental) y 1 se confirmó sin cambios (AgendaPro). Todas las correcciones fueron aplicadas con la decisión **Ajustar** antes de dar por cerrada la etapa.

## Referencias completas

Todas las referencias fueron consultadas el **2026-10-01**. Se privilegian fuentes primarias.

1. Dentalink. “Software de agenda odontológica para gestionar turnos online, Argentina”. https://www.softwaredentalink.com/ar/atrae-mas-pacientes/agendamiento-online
2. Dentalink. “Software para dentistas, México”. https://web-mx.softwaredentalink.com/
3. AgendaPro. “Mejor Software para Dentistas en Argentina”. https://agendapro.com/ar/dental/software-odontologico
4. AgendaPro. “¿Cómo configuro mi sitio web?”. Centro de ayuda. https://ayuda.agendapro.com/es/articles/6126081-como-configuro-mi-sitio-web
5. DentalSoft. “Software dental para clínicas y profesionales”. https://www.dentalsoft.com.ar/
6. Denteo. “Software de gestión odontológica”. https://denteo.com.ar/
7. Dental-IA. “Software clínico e inteligencia artificial para consultorios odontológicos”. https://www.dentalia.com.ar/
8. Dental Manager. “Software de gestión para clínicas dentales en Argentina”. https://dentalmanager.com.ar/
9. Hi Órbita. “Software de gestión odontológica con IA”. https://hiorbita.com/
10. Dentiqa. “Software dental para clínicas en Argentina con IA y WhatsApp”. https://dentiqa.app/ar
11. OdontoGRAMA. “El consultorio en la nube”. https://www.odontograma.com.ar/
12. Odontosys. “Software de gestión para clínicas dentales”. https://odontosys.com/
13. Dentios. “Software de gestión para clínicas dentales”. https://dentios.cl/
14. DentalQub. “Software dental moderno para clínicas en Chile”. https://dentalqub.cl/
15. Simples Dental. “Agenda online para dentistas”. https://www.simplesdental.com/agenda-online
16. Simples Dental. “Cómo activar la confirmación de consulta automática por WhatsApp”. Centro de ayuda. https://ajuda.simplesdental.com/pt-BR/articles/3659017-como-ativar-a-confirmacao-de-consulta-automatica-por-whatsapp
17. Clinicorp. “O software odontológico para clínicas e consultórios”. https://www.clinicorp.com/
18. Clinicorp. “Checklist: guia de actividades para la secretaria de odontología”. Material oficial. https://conteudos.clinicorp.com/hubfs/Materiais%20Ricos/Checklist%20Guia%20de%20atividades%20para%20a%20secret%C3%A1ria%20de%20odontologia.pdf
19. Odensys. “Software dental para consultorios odontológicos”. https://odensys.com/software-dental

## Decisión de inspección

**2026-10-02 — Continuar con supuestos documentados (Ajustar aplicado).**

La verificación personal de seis fuentes de tipos distintos se completó y sus correcciones se incorporaron a las secciones A, B y C: precios publicados de DentalSoft y Dentios, Mercado Pago y sobreturnos en DentalSoft, odontograma y respaldos de Denteo, exportación declarada de Dentalink y el matiz de costo de WhatsApp en Simples Dental.

Quedan dos verificaciones abiertas y se declaran como tales, sin darse por cumplidas:

1. Entrevista u observación en al menos un consultorio para confirmar usuarios y casos de uso.
2. Política de cancelación, reprogramación y sobreturno acordada con el producto.

Se decide **Continuar** porque la knowledge-base y el roadmap ya construyeron sobre esos puntos con supuestos explícitos en `knowledge-base/10_preguntas_abiertas.md`, y porque el primer change (crear turno sin solapamientos) no depende de esas políticas. Si se hubiera marcado “Continuar” sin dejar registrados los supuestos, el riesgo habría sido convertir huecos de información en reglas de negocio del código.
