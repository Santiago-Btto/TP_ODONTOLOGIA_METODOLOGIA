# Design

## Context

`docker-compose.yml` tiene `db`, `redis` y `api`; C-15 añade `frontend` con proxy de mismo origen. `semillas.py` inserta recursos y pacientes ficticios mediante `merge`, `crear_usuario.py` exige contraseña externa y el worker de C-16 ya admite modo continuo. La API exige `JWT_SECRET` de al menos 32 caracteres y crea el esquema al iniciar, mientras que las rutas HTTP existentes ya cubren el flujo de C-06. Véase `proposal.md` y `specs/entorno-mvp-local/spec.md`.

## Goals / Non-Goals

**Goals:** un único comando de arranque después de preparar secretos locales, dependencia ordenada de servicios, bootstrap repetible, worker continuo, prueba HTTP contra servicios reales en un proyecto Compose aislado y documentación que permita reproducir las comprobaciones.

**Non-Goals:** migraciones/versionado de esquema (C-07), nuevos endpoints, envío de recordatorios reales, CORS público, credenciales de producción, datos clínicos y reglas de disponibilidad nuevas.

## Decisions

1. **Preparación local separada y explícita.** Un script multiplataforma de biblioteca estándar genera un `.env` raíz ignorado por Git con `JWT_SECRET` y `DEMO_PASSWORD` aleatorios, protege permisos cuando el sistema lo permite y no sobrescribe una configuración válida en ejecuciones repetidas. Si el archivo es incompleto o inválido, falla con instrucciones de reparación sin imprimir valores. El usuario puede leer su `.env` local para el login. Alternativa descartada: contraseña o secreto fijo en Compose, porque el repositorio prohíbe versionarlos. La API conserva su validación actual del secreto.
2. **Bootstrap como servicio one-shot de Compose.** Un proceso basado en la imagen backend espera `db` saludable, crea esquema y semillas ficticias con la infraestructura existente y crea una cuenta `recepcion.demo` usando el hash Argon2id actual y la contraseña local. El alta de usuario se hace sólo si falta; si ya existe, se verifica que rol y contraseña correspondan, y se falla claramente ante discrepancias en vez de sobrescribir un usuario. API y worker dependen de `service_completed_successfully`. Alternativa descartada: ejecución manual documentada, que deja el arranque no reproducible; también se descarta hacer la inserción en cada request.
3. **Salud y orden de servicios.** Redis y PostgreSQL mantienen healthchecks; `api` espera el bootstrap (que depende de PostgreSQL saludable) y expone `/health` para healthcheck HTTP, pero no espera Redis: RN-EX-02 permite operar aun si Redis falla. `frontend` espera la API saludable y mantiene el proxy `/api/` de C-15; `worker` espera bootstrap y Redis saludables y ejecuta su bucle continuo existente. Alternativa descartada: `service_started` como prueba de disponibilidad para los servicios que sí requieren Redis.
4. **E2E de caja negra aislado.** Un servicio de prueba ejecuta peticiones HTTP reales a `api:8000` y consulta la web por su mismo origen; un lanzador inicia una instancia Compose con nombre de proyecto único y volúmenes/red independientes, sin puertos de host publicados mediante un override de prueba, y la destruye con volúmenes al finalizar aun si el test falla. Recibe las credenciales demo por variables de entorno desde el `.env` local, sin imprimirlas. Alternativa descartada: usar la base cotidiana o `TestClient` solamente, porque no probarían el cableado real del stack.
5. **Secuencia temporal determinista y espera acotada.** La prueba utiliza recursos demo y franjas futuras calculadas desde la fecha actual en cada ejecución dentro del entorno aislado: crea turno A; comprueba agenda; bloquea una franja distinta e intenta alta B intersectante (`409`); reprograma A a otra franja; consulta `recordatorios` con polling acotado hasta ver el registro simulado; cancela A y reserva C en el horario liberado. La espera precede a cancelar porque el worker omite correctamente tareas de turnos cancelados. Se afirman códigos HTTP, IDs, estados y ausencia/presencia en agenda, no sólo ausencia de excepciones.
6. **TDD en la integración.** Primero pruebas de preparación y bootstrap (configuración ausente/repetida, usuario y semillas idempotentes), luego configuración Compose y E2E con RED/GREEN. Se ejecutan `docker compose config`, `pytest` backend con PostgreSQL real, pruebas/build frontend, E2E aislado y smoke de arranque. No se cambian contratos funcionales ya cubiertos por sus propios specs.

## Risks / Trade-offs

- [Un `.env` viejo trae contraseña distinta de la del usuario ya creado] → bootstrap falla con diagnóstico, sin cambiar el hash; documentar limpieza deliberada de volúmenes sólo para el demo.
- [El proceso inicial de bootstrap crea esquema sin migraciones] → aceptable en base nueva de MVP; una base antigua requiere recreación local hasta C-07. No borrar datos automáticamente.
- [El worker procesa antes de que el test consulte] → el test espera el registro en PostgreSQL por la API, sin depender del instante preciso de ejecución.
- [El proxy o un servicio tarda en iniciar] → healthchecks y timeouts acotados; el lanzador informa qué servicio falló y siempre desmonta el proyecto aislado.
- [Secretos en salida de comandos o trazas] → no usar `docker compose config` como salida pública de logs; pruebas y scripts nunca imprimen variables sensibles. El archivo local permanece fuera de Git.

## Migration Plan

1. Preparar `.env` local con el script y comprobar que está ignorado por Git.
2. Construir y levantar Compose. En una base nueva, bootstrap crea esquema y datos demo; API, worker y frontend arrancan después.
3. Ejecutar verificación integrada en un proyecto Compose aislado y comprobar suites backend/frontend.
4. Para revertir, restaurar el Compose anterior y retirar bootstrap/worker; conservar la base local salvo que el usuario ejecute explícitamente un reinicio con volúmenes. No hay migración de datos en C-06.
