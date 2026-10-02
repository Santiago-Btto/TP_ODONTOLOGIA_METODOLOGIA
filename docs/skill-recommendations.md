# Recomendación de skills para el MVP

Fecha de verificación: 2026-10-01.

## Contexto evaluado

El MVP es un CLI de agenda odontológica en Node.js + TypeScript. La base de
conocimiento prescribe `node:test` y ninguna dependencia externa. La calidad
se rige además por TDD estricto ya configurado en las instrucciones del
proyecto. Por lo tanto, una skill adicional solo se justifica si aporta una
capacidad que el flujo actual no cubre y que esté dentro del alcance presente.

## Opciones verificadas

| Opción | Fuente y señal de calidad | Aporte potencial | Decisión para el MVP |
| --- | --- | --- | --- |
| `obra/superpowers` — `test-driven-development` | [Repositorio público de obra/superpowers](https://github.com/obra/superpowers), ~287 mil estrellas al verificarlo; documenta el ciclo RED → GREEN → REFACTOR. | Disciplina de TDD agnóstica del framework. | **No instalar.** Duplica el módulo de TDD estricto ya obligatorio para este proyecto; añadirlo haría coexistir dos autoridades sobre el mismo ciclo. |
| `anthropics/skills` — `webapp-testing` | [Skill oficial](https://github.com/anthropics/skills/tree/main/skills/webapp-testing); el repositorio contaba con ~176 mil estrellas. Es una herramienta Playwright para verificar aplicaciones web locales. | E2E de una futura interfaz web. | **Diferir.** El alcance actual es un CLI y no hay UI. Además requiere Playwright y sus dependencias, en contra de la decisión del MVP de no sumar dependencias externas. |
| `vercel-labs/agent-skills` — `vercel-optimize` | [Skill oficial](https://github.com/vercel-labs/agent-skills/tree/main/skills/vercel-optimize); el repositorio contaba con ~31 mil estrellas. Su propia documentación exige Node.js 20+, Vercel CLI autenticado y un proyecto Vercel vinculado. | Auditoría de costo/rendimiento de un servicio ya desplegado en Vercel. | **No instalar.** No existe despliegue ni cuenta Vercel dentro del alcance; la skill sería inejecutable y no mejora el dominio de turnos. |

## Decisión

No se instala ninguna skill adicional en este MVP. El conjunto actual cubre lo
necesario:

- OpenSpec/OPSX gobierna propuesta, aplicación y archivo de cambios.
- El módulo de TDD estricto exige pruebas primero, ejecución de la suite y
  evidencia de RED/GREEN/TRIANGULATE/REFACTOR.
- `node:test`, junto con TypeScript, permite probar la lógica de solapamiento,
  disponibilidad y estados sin framework ni dependencia extra.

La recomendación se revisará únicamente si el alcance suma una interfaz web
(evaluar `webapp-testing`) o un despliegue en Vercel (evaluar
`vercel-optimize`). Para TDD se mantiene la política actual para evitar reglas
duplicadas.

## Fuentes consultadas

- [obra/superpowers — test-driven-development](https://github.com/obra/superpowers)
- [anthropics/skills — webapp-testing](https://github.com/anthropics/skills/tree/main/skills/webapp-testing)
- [vercel-labs/agent-skills — vercel-optimize](https://github.com/vercel-labs/agent-skills/tree/main/skills/vercel-optimize)
- [Node.js test runner](https://nodejs.org/api/test.html)
