# Descripción General

## Stack tecnológico

| Capa | Tecnología | Versión mínima / nota |
|---|---|---|
| Runtime | Node.js | Versión LTS a fijar antes de implementar |
| Lenguaje | TypeScript | Versión a fijar por el change de implementación |
| Dominio | Módulos TypeScript sin dependencias externas | Regla de agenda ejecutable localmente |
| Pruebas | `node:test` y `node:assert` | Incluidos en Node.js; sin cuentas externas |
| Persistencia | En memoria para el MVP | No se definió base de datos |

## Arquitectura general

El sistema será un núcleo de dominio ejecutable, sin UI ni infraestructura. Una capa de aplicación recibe comandos (crear, reprogramar, cancelar, confirmar y bloquear), consulta repositorios en memoria y delega la decisión de disponibilidad a reglas de dominio. Las validaciones no viven exclusivamente en un canal futuro como UI, bot o API.

```text
Comando/ejecutable local
          |
          v
Casos de uso (aplicación)
          |
          v
Dominio: turnos, disponibilidad y reglas anti-solapamiento
          |
          v
Repositorios en memoria + datos ficticios
```

Esta arquitectura deja canales e integraciones como adaptadores posteriores, para que todos deban pasar por el mismo control de recursos.

## Integraciones externas

| Servicio | Propósito potencial | Estado en MVP |
|---|---|---|
| WhatsApp | Recordatorios, confirmación o cambio de turnos | Posterior; se puede simular/documentar sin API |
| Mercado Pago | Seña | Posterior; reglas de seña/reintegro sin acordar |
| Google Calendar | Sincronización de agenda | Posterior |

No se usan cuentas, credenciales ni llamadas externas durante pruebas.

## API REST

No aplica al MVP: no se definió una API HTTP. Si se expone una más adelante, sus endpoints deberán invocar los mismos casos de uso y reglas de dominio.
