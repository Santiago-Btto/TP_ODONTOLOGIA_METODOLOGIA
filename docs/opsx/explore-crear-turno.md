# Exploración — crear turno sin solapamientos

## Problema y objetivo

El MVP necesita una operación de dominio determinista para crear turnos sin
reservar dos veces el mismo profesional ni el mismo box. Es el primer change
del roadmap y establece el núcleo sobre el que se apoyarán consulta, bloqueos,
reprogramación y cambios de estado.

## Decisiones confirmadas para el change

- El alcance es un núcleo Node.js/TypeScript en memoria: no hay UI, HTTP,
  persistencia, autenticación ni integraciones externas.
- Un turno candidato lleva paciente, profesional, box, prestación e intervalo;
  el fin puede calcularse con la duración positiva de la prestación o
  validarse si se recibe explícitamente.
- Todo dato de desarrollo, fixtures y pruebas es manifiestamente ficticio.
- Los intervalos usan la convención semiabierta `[inicio, fin)`. Dos turnos se
  solapan cuando `inicioA < finB && inicioB < finA`; por ello el fin de uno
  igual al inicio de otro es válido.
- La creación debe verificar ambos recursos antes de persistir el turno y el
  historial `creado`. Un rechazo no deja reservas ni historial parcial.
- Las validaciones viven en el dominio/caso de uso, no en un adaptador.

## Comportamientos de aceptación

1. Crea y registra un turno válido con recursos disponibles.
2. Rechaza un candidato que intersecta un turno activo del mismo profesional.
3. Rechaza un candidato que intersecta un turno activo del mismo box.
4. Acepta un turno exactamente contiguo a una reserva existente.
5. Rechaza un intervalo cuyo fin no es posterior a su inicio y una prestación
   con duración no positiva.

## Diseño candidato

```text
CrearTurno
  --> construye intervalo válido
  --> Disponibilidad valida profesional y box contra turnos activos
  --> Repositorio en memoria guarda Turno
  --> Historial en memoria guarda evento creado
```

El servicio de disponibilidad es puro y recibe los turnos relevantes; los
repositorios en memoria implementan puertos definidos por el dominio o la
aplicación. En este change no se modelan bloqueos ni concurrencia persistente:
ambos pertenecen a changes posteriores del roadmap.

## Riesgos y límites

- La consistencia se limita a una ejecución local y secuencial; la exclusión
  entre procesos se abordará con persistencia y control de concurrencia.
- La política de estados se mantiene mínima: los conflictos se calculan contra
  turnos activos, dejando la cancelación para el change correspondiente.
- No se introducen datos personales, historias clínicas ni credenciales.

## Criterio de preparación para implementar

La propuesta debe especificar los escenarios anteriores, el diseño debe
definir contratos, errores y la fórmula de solapamiento, y las tareas deben
seguir TDD: seguridad previa, RED, GREEN, triangulación y refactorización.
