# Arquitectura Propuesta

## Patrones aplicados

| Patrón | Dónde se usa | Por qué |
|---|---|---|
| Dominio rico / reglas puras | Entidades de turno y servicio de disponibilidad | Las reglas anti-solapamiento son el núcleo y deben probarse sin UI |
| Casos de uso | Crear, consultar, bloquear, reprogramar, cancelar y confirmar | Coordina validación y persistencia sin mezclar canales |
| Puertos y adaptadores ligeros | Repositorios y futuros canales | WhatsApp, API o UI no podrán eludir las reglas |
| Repositorio en memoria | MVP local | Permite un dominio ejecutable sin infraestructura ni datos reales |
| Pruebas de unidad con `node:test` | Reglas y casos de uso | Asegura resultados deterministas y sin dependencias externas |

## Estructura de directorios

```text
turnos-odontologia/
├── src/
│   ├── domain/
│   │   ├── agenda/
│   │   ├── turnos/
│   │   └── shared/
│   ├── application/
│   │   └── use-cases/
│   ├── infrastructure/
│   │   └── in-memory/
│   └── index.ts
├── test/
│   ├── domain/
│   └── application/
├── docs/
├── knowledge-base/
└── openspec/
```

La estructura es propuesta para el primer change; aún no existe código de producción.

## Seguridad

- **Autenticación:** no definida; el MVP no expone UI ni API.
- **Autorización:** la matriz RBAC es propuesta y debe validarse antes de un adaptador multiusuario.
- **Validación de input:** validar en casos de uso y volver a imponer invariantes en dominio.
- **Datos:** usar sólo datos ficticios en desarrollo, pruebas y semillas; no incorporar PII o información clínica real.
- **Secrets management:** no hay secretos ni cuentas externas en el MVP. Si se agregan integraciones, las credenciales no se guardarán en el repositorio.
- **Privacidad y retención:** requieren revisión legal/especializada; no se infiere cumplimiento por tratarse de un dominio de salud.

## Variables de entorno

No se requieren variables de entorno en el MVP ejecutable.

| Variable futura | Descripción | Ejemplo | Sensible |
|---|---|---|---|
| `WHATSAPP_*` | Credenciales de mensajería, si se aprueba la integración | No definida | Sí |
| `MERCADOPAGO_*` | Credenciales para señas, si se aprueban | No definida | Sí |
| `GOOGLE_CALENDAR_*` | Credenciales de sincronización, si se aprueba | No definida | Sí |
