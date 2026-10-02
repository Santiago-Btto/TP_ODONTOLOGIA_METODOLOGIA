# Reflexión sobre el trabajo de integración

**Proyecto:** turnos-odontologia  
**Integrantes:** Santiago Barretto, Mateo Algañaraz, Ezequiel Menéndez  
**Modalidad:** Grupal (3 integrantes)  
**Fecha:** 2026-10-02

El trabajo permitió recorrer un flujo completo desde una idea inicial hasta una funcionalidad especificada, probada y archivada. El producto elegido fue un sistema de turnos para consultorios odontológicos orientado al mercado argentino. La decisión de concentrar el primer change en evitar solapamientos por profesional y por box fue importante porque redujo el alcance a una regla observable y verificable. En lugar de intentar incluir historia clínica, pagos, WhatsApp, facturación u obras sociales, esos temas quedaron registrados como etapas posteriores o preguntas abiertas. Esa delimitación hizo posible que el resultado no dependiera de una interfaz ni de servicios externos.

## ¿Qué información del Discovery resultó incorrecta o no verificable?

La verificación personal de fuentes, hecha el 2026-10-02 abriendo seis URLs de tipos distintos (sitio oficial, página de producto y centro de ayuda), encontró errores concretos en el informe generado. DentalSoft y Dentios figuraban con "precios: No evidenciado" cuando ambos publican precios en su sitio (Gestión $30.000/mes y Pro $60.000/mes; 0,80 UF y 1,30 UF respectivamente). DentalSoft también tenía Mercado Pago sin registrar en caja y publicaba "sobreturnos con detección automática de solapamiento", algo que el checklist daba por no evidenciado. Denteo publicaba odontograma y respaldos diarios que el informe marcaba como ausentes, y Dentalink prometía la entrega de datos al cancelar el servicio. Detectamos los errores comparando celda por celda lo que el informe afirmaba contra lo que mostraba la URL ese día: la IA había sido conservadora con los "No evidenciado", pero la omisión también es un error, porque deforma la matriz de puntuación. Todas las correcciones se aplicaron con la decisión Ajustar y quedaron registradas en la sección "Verificación de fuentes" del informe. Además, aprendimos a distinguir "funcionalidad comprobada" (aparece en la fuente) de "afirmación comercial" (la dice el proveedor sin demostrarla): por ejemplo, el dato de "135.000 profesionales" de AgendaPro es marketing, no un hecho verificado.

## ¿En qué etapa usamos Ajustar y qué habría pasado si apretábamos Continuar?

El gate de revisión humana de Discovery quedó en **Ajustar** porque faltaba la verificación personal de fuentes y la validación con usuarios. Lo resolvimos el 2026-10-02: aplicamos las correcciones al informe y decidimos **Continuar con supuestos documentados**, dejando en claro que las entrevistas a consultorios y la política de cancelación/sobreturno siguen abiertas y viven en `knowledge-base/10_preguntas_abiertas.md`. Si hubiéramos marcado Continuar sin hacer la verificación, la Knowledge Base y el roadmap se habrían construido sobre celdas incorrectas: la matriz de puntuación habría bajado a DentalSoft y Dentios injustificadamente, y "sobreturnos: No evidenciado" podría haberse convertido en una regla de negocio del código sin evidencia. El tiempo invertido en corregir al inicio se ahorra después, cuando ya está implementado.

## ¿Qué diferencia hubo entre implementar con especificación y pedir código con un prompt?

Para el change `crear-turno-sin-solapamientos`, el spec aprobado funcionó como contrato: alta válida, conflicto por profesional, conflicto por box, caso borde de turnos contiguos y entradas inválidas. La regla de intervalos semiabiertos `[inicio, fin)` fue especialmente útil: un turno que termina a las 10:00 permite otro que empieza a las 10:00, pero rechaza cualquier intersección real. Los tests verifican esos escenarios y también confirman que, ante un rechazo, no se persiste un turno ni se agrega historial parcial. La diferencia con un prompt suelto es que el spec definió *qué* tenía que ser verdadero antes de escribir código; cuando en Apply aparecía algo que no estaba en el spec, no se improvisó: se volvió a Propose. El resultado fue un módulo de dominio pequeño, sin UI ni red, ejecutable y comprobable localmente.

## ¿Qué parte de la fundación aportó más valor y cuál menos?

La Knowledge Base y el roadmap fueron los artefactos de mayor valor: la KB conectó la investigación con modelos, reglas de negocio, flujos y riesgos; el roadmap ordenó catorce changes y permitió separar el MVP de las integraciones futuras. Las reglas de `AGENTS.md` y `CLAUDE.md` sostuvieron límites concretos: datos de prueba ficticios, ausencia de secretos, TypeScript estricto y uso de `node:test`. El registro de skills tuvo un valor más operativo que funcional, porque documenta qué habilidades había disponibles y por qué no se instalaron herramientas adicionales para un MVP pequeño. Engram mostró que la memoria persistente evita reconstruir el contexto entre sesiones (quedaron guardadas observaciones sobre el archive de C-01 y sobre la regla de no usar datos reales de pacientes), aunque la memoria no reemplaza los archivos versionados: el spec, la KB y los tests siguen siendo la evidencia principal.

## Participación de cada integrante

- **Santiago Barretto — Etapa 2 (Discovery):** condujo la investigación de mercado, el informe comparativo de 15 sistemas y el checklist de once puntos; responsable de la decisión de inspección del gate de Discovery y de la verificación personal de fuentes del 2026-10-02.
- **Mateo Algañaraz — Etapas 3 y 4 (Knowledge Base y Roadmap):** revisó los diez archivos canónicos contra el informe de Discovery (reglas de agenda, duración de prestaciones, boxes y preguntas abiertas) y validó que `CHANGES.md` estuviera alineado con el MVP recomendado en la sección D.
- **Ezequiel Menéndez — Etapa 5 (Skills y reglas) y Etapa 6 (ciclo OPSX):** evaluó las recomendaciones de `find-skill`, revisó las reglas de `AGENTS.md`/`CLAUDE.md` y condujo el change `crear-turno-sin-solapamientos` por explore → propose → apply → verify → archive.

## Uso de IA declarado

El uso de IA fue una herramienta de asistencia para investigar, organizar documentos, proponer estructura, generar pruebas y verificar el proyecto. La investigación de mercado, la corrección de fuentes, la revisión de la fundación y el ciclo OPSX fueron conducidos por el equipo con el agente como soporte; la responsabilidad de revisar fuentes, corregir supuestos y decidir qué entregar es nuestra. Para una siguiente iteración, la mejora prioritaria sería validar el Discovery con entrevistas reales o demos controladas antes de definir las políticas de agenda. El principal aprendizaje fue que una especificación trazable no elimina las decisiones humanas, pero hace visible qué se decidió, con qué evidencia y cómo se puede comprobar.
