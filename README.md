# Turnos de odontología — núcleo local

Núcleo TypeScript en memoria para crear turnos sin solapar un profesional ni un box. Los intervalos son semiabiertos (`[inicio, fin)`), por lo que una reserva que comienza exactamente al finalizar otra se admite.

## Requisitos

- Node.js 22.6.0 o posterior.
- No se instalan dependencias, servicios, variables de entorno ni cuentas externas.

## Comandos reproducibles

```sh
npm test
npm run build
```

`npm test` ejecuta la suite con `node:test` y `node:assert`. `npm run build` carga el punto de entrada con el soporte nativo de TypeScript de Node para verificar que todos los módulos del núcleo se transforman y resuelven. `tsconfig.json` conserva `strict: true` como contrato del proyecto.

## Alcance

Incluye entidades de agenda, validación de intervalos y duración, disponibilidad por profesional y box, repositorios en memoria, historial `creado` y el caso de uso `CrearTurno`.

No incluye UI, HTTP, red, persistencia durable, autenticación, integraciones ni datos personales. Las fixtures son manifiestamente ficticias.
