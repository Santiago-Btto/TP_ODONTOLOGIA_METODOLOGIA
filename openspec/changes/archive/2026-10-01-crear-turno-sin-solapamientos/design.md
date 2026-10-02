# Design

## Context

El repositorio contiene la definición del MVP y sus reglas de negocio, pero aún no tiene código de aplicación. Este change implementará el primer núcleo ejecutable; la motivación y el contrato observable están en `proposal.md` y en la delta `specs/creacion-de-turnos/spec.md`.

## Goals / Non-Goals

**Goals:**

- Separar entidades de dominio, caso de uso y adaptadores en memoria para que la regla de disponibilidad no dependa de una interfaz.
- Hacer atómica, dentro de la ejecución local, la creación del turno y de su historial: ambos sólo se escriben tras validar los dos recursos.
- Fijar contratos de error distinguibles para conflicto por profesional, conflicto por box, intervalo inválido y duración inválida.

**Non-Goals:**

- Bloqueos de disponibilidad, reprogramación, cancelación, confirmación y consulta de agenda.
- Persistencia, transacciones entre procesos, red, UI, autenticación, auditoría operativa o integraciones.
- Datos reales de pacientes o reglas clínicas/financieras adicionales.

## Decisions

### Capas y dependencias dirigidas hacia el dominio

Se organizarán tipos y reglas puras bajo `src/domain`, el caso de uso y puertos bajo `src/application`, y repositorios en `src/infrastructure/in-memory`. El caso de uso dependerá de interfaces de repositorio, no de colecciones ni de adaptadores concretos. Esto permite sustituir la persistencia posterior sin reescribir la validación.

Alternativa considerada: implementar el flujo directamente en un repositorio en memoria. Se descarta porque mezclaría la regla de negocio con almacenamiento y haría más riesgosa la evolución hacia persistencia.

### Intervalos semiabiertos y servicio puro de disponibilidad

La intersección se determinará con `inicioCandidato < finExistente && inicioExistente < finCandidato`. La igualdad en un borde no es intersección. Un servicio puro recibirá un candidato y los turnos activos relevantes y devolverá disponibilidad o un error de conflicto tipado.

Alternativa considerada: comparar por inclusión de extremos. Se descarta porque falla con un turno que cubre completamente al candidato y suele rechazar erróneamente turnos contiguos.

### Validar antes de cualquier escritura

`CrearTurno` construirá y validará el intervalo (usando la duración de la prestación cuando corresponda) y consultará ambos recursos antes de escribir. Sólo al final guardará el turno y, de inmediato, el historial `creado`. Los repositorios en memoria deben exponer lecturas y escrituras que permitan comprobar que un error no dejó estado parcial.

Alternativa considerada: persistir primero y compensar ante el segundo conflicto. Se descarta: añade una ventana de estado parcial y complejidad de rollback que el núcleo en memoria no necesita.

### Tiempo explícito y datos de prueba ficticios

El núcleo recibirá fechas/horas como datos de entrada, sin depender del reloj del sistema, para volver las pruebas reproducibles. Fixtures y nombres de pacientes deben indicar explícitamente que son ficticios.

Alternativa considerada: generar horarios con la fecha actual. Se descarta porque produciría pruebas no deterministas.

### Toolchain de prueba mínimo

Se configurará TypeScript con el runner nativo `node:test` y scripts para compilar y ejecutar pruebas. Las pruebas se escribirán antes del código productivo y cubrirán el flujo del caso de uso y las reglas puras donde resulte útil.

Alternativa considerada: incorporar un framework externo. Se descarta para mantener el primer vertical slice sin dependencias de terceros.

## Risks / Trade-offs

- [No hay aislamiento entre procesos] → El alcance se limita a una ejecución local en memoria; la concurrencia se resolverá en el change de persistencia.
- [Los repositorios en memoria pueden ocultar fallas de infraestructura] → Los puertos de aplicación mantendrán separada la futura implementación persistente y sus pruebas de integración.
- [La política de turnos activos evoluciona con cancelación] → Este change define un estado inicial mínimo y el change de ciclo de vida ajustará la selección de activos sin duplicar la fórmula de solapamiento.

## Migration Plan

No hay datos ni despliegue previo que migrar. La implementación se añade como núcleo local autocontenido. El rollback consiste en retirar los archivos del change antes de que exista un consumidor externo.
