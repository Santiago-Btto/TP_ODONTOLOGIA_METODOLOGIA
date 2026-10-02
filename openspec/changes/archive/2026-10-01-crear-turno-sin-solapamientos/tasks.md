# Tasks

## 1. Base ejecutable y contrato de dominio

- [x] 1.1 Configurar `package.json`, `tsconfig.json`, scripts de compilación y `node:test`; verificar que el comando de pruebas y la compilación se ejecutan sin dependencias de terceros.
- [x] 1.2 Escribir primero pruebas RED para entidades de turno y prestación que cubran intervalo válido, fin no posterior al inicio y duración cero/negativa; verificar que fallan antes de incorporar la lógica de dominio.
- [x] 1.3 Implementar el mínimo de tipos, entidades y errores de dominio para satisfacer las pruebas de 1.2; verificar GREEN con el runner y añadir al menos un segundo caso límite por cada validación antes de refactorizar con la suite verde.
- [x] 1.4 Crear fixtures reproducibles de paciente, profesional, box y prestación con nombres evidentemente ficticios; verificar en sus pruebas que ninguna fixture usa datos personales reales.

## 2. Disponibilidad de recursos

- [x] 2.1 Escribir primero pruebas RED para la función pura de intersección semiabierta: solapamiento parcial, un intervalo contenido y borde exactamente contiguo; verificar que fallan antes de implementar la regla.
- [x] 2.2 Implementar el mínimo servicio puro de disponibilidad que use `inicioCandidato < finExistente && inicioExistente < finCandidato`; verificar GREEN para los casos de 2.1 y refactorizar manteniendo la suite verde.
- [x] 2.3 Escribir primero pruebas RED que distingan conflicto por profesional de conflicto por box a partir de turnos activos en memoria; verificar que ambos casos fallan antes de agregar la selección por recurso.
- [x] 2.4 Implementar puertos y repositorios en memoria de turnos para consultar las reservas de cada recurso y devolver errores tipados; verificar GREEN de 2.3 y triangulación con recursos no compartidos sin conflicto.

## 3. Caso de uso CrearTurno y atomicidad local

- [x] 3.1 Escribir primero la prueba RED de alta exitosa que espere turno persistido e historial `creado` único tras validar ambos recursos; verificar que falla sin caso de uso.
- [x] 3.2 Implementar el mínimo `CrearTurno` que construya el candidato, valide ambos recursos y sólo entonces guarde turno e historial; verificar GREEN de 3.1 y refactorizar sin cambiar comportamiento.
- [x] 3.3 Escribir primero pruebas RED de rechazo por conflicto de profesional y por conflicto de box que además esperen repositorios e historial sin cambios; verificar ambas fallas antes de modificar el caso de uso.
- [x] 3.4 Completar la integración del caso de uso con la disponibilidad y repositorios para pasar 3.3; verificar GREEN y triangular con una reserva contigua que comparta profesional y box y se acepte.
- [x] 3.5 Escribir primero pruebas RED de intervalo inválido y prestación de duración inválida que comprueben ausencia de estado parcial; verificar que fallan antes de integrar las validaciones de entrada.
- [x] 3.6 Integrar las validaciones de entrada al caso de uso y errores explícitos; verificar GREEN de 3.5 y ejecutar el refactor final con todas las pruebas del change verdes.

## 4. Verificación de integración del núcleo

- [x] 4.1 Ejecutar compilación y la suite completa; verificar escenarios de alta válida, conflicto por profesional, conflicto por box, borde contiguo e intervalos/duraciones inválidos sin fallas.
- [x] 4.2 Revisar que el cambio no añade UI, HTTP, persistencia, autenticación, integraciones ni datos reales; verificar el alcance mediante revisión de archivos y de las fixtures.
