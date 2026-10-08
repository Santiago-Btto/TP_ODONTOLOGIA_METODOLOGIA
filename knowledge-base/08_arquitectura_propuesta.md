# Arquitectura Propuesta

> **Ajustar (2026-10-08).** Se reemplazó la arquitectura Node.js en memoria por el stack definido (FastAPI + SQLAlchemy + PostgreSQL + Redis + Docker; React + TypeScript + Vite). Ver [DD-02](09_decisiones_y_supuestos.md#dd-02--stack-definido-fastapi--postgresql--react).

## Patrones aplicados

| Patrón | Dónde se usa | Por qué |
|---|---|---|
| Dominio rico / reglas puras | `backend/app/domain`: entidades de turno y servicio de disponibilidad | Las reglas anti-solapamiento son el núcleo y se prueban sin HTTP ni base |
| Casos de uso | `backend/app/application`: crear, consultar, bloquear, reprogramar, cancelar y confirmar | Coordinan validación y persistencia sin mezclar canales |
| Puertos y adaptadores | Protocolos de repositorio en aplicación; SQLAlchemy y FastAPI como adaptadores | API, frontend, bots o integraciones no pueden eludir las reglas |
| Unit of Work / transacción por request | Sesión SQLAlchemy por operación | Turno e historial se confirman juntos o no se confirman |
| Restricción de exclusión en base | `EXCLUDE USING gist` sobre `tstzrange(inicio, fin, '[)')` | Defensa en profundidad ante altas concurrentes |
| Pruebas con pytest | Dominio (unidad), casos de uso y API (integración contra PostgreSQL) | Un test por escenario del spec |

## Estructura de directorios

```text
turnos-odontologia/
├── docker-compose.yml          # db (PostgreSQL) + api (FastAPI); redis desde C-10
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── app/
│   │   ├── domain/             # entidades, errores y disponibilidad (Python puro)
│   │   ├── application/        # puertos y casos de uso
│   │   ├── infrastructure/     # modelos y repositorios SQLAlchemy, sesión
│   │   └── api/                # routers y esquemas FastAPI (Pydantic)
│   └── tests/
│       ├── domain/
│       ├── application/
│       └── api/
├── frontend/                   # React + TypeScript + Vite (desde C-15)
├── docs/
├── knowledge-base/
└── openspec/
```

## Seguridad

- **Autenticación:** JWT bearer (C-08). Hasta entonces la API sólo corre en local y no se despliega.
- **Autorización:** la matriz RBAC es propuesta y debe validarse antes de exponer la API a usuarios.
- **Validación de input:** Pydantic valida forma en el borde HTTP; el dominio vuelve a imponer invariantes.
- **Datos:** sólo datos ficticios en desarrollo, pruebas y semillas; no incorporar PII o información clínica real.
- **Secrets management:** credenciales por variables de entorno; `.env` ignorado por Git y `.env.example` sin valores reales. Las credenciales de Docker Compose son sólo de desarrollo local.
- **Privacidad y retención:** requieren revisión legal/especializada; no se infiere cumplimiento por tratarse de un dominio de salud.

## Variables de entorno

| Variable | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| `DATABASE_URL` | Conexión SQLAlchemy a PostgreSQL | `postgresql+psycopg://turnos:turnos@db:5432/turnos` | Sí (fuera de desarrollo) |
| `TEST_DATABASE_URL` | Base descartable para pytest | `postgresql+psycopg://turnos:turnos@localhost:5432/turnos_test` | No (sólo local) |
| `JWT_SECRET` | Firma de tokens (C-08) | No definida | Sí |
| `REDIS_URL` | Broker de tareas asincrónicas (C-10) | `redis://redis:6379/0` | No |
| `WHATSAPP_*` | Credenciales de mensajería, si se aprueba la integración | No definida | Sí |
| `MERCADOPAGO_*` | Credenciales para señas, si se aprueban | No definida | Sí |
| `GOOGLE_CALENDAR_*` | Credenciales de sincronización, si se aprueba | No definida | Sí |
