# Design

## Context

La API síncrona FastAPI ya expone login OAuth2 password (`/api/v1/auth/token`), identidad (`/api/v1/auth/yo`), agenda por rango y filtros, pacientes y alta de turnos. Las rutas protegidas devuelven JSON `{codigo, detalle}` para errores de dominio y JSON `detail` para errores de esquema. No existen endpoints de catálogo de profesionales, boxes o prestaciones. CORS público pertenece a C-09; el navegador debe usar origen único. Véase `proposal.md` y `specs/agenda-web/spec.md`.

## Goals / Non-Goals

**Goals:** una interfaz operable con teclado y pantallas pequeñas, contratos HTTP tipados, manejo explícito de carga/vacío/error, datos de agenda siempre provenientes de la API y pruebas de comportamiento del cliente y componentes.

**Non-Goals:** reglas de disponibilidad en JavaScript, catálogo nuevo de recursos, persistencia del token entre recargas, portal de paciente, mensajería real y cambios al backend.

## Decisions

1. **React + TypeScript `strict` + Vite, Vitest y React Testing Library.** Separar `api/client.ts` (fetch, tipos, traducción de errores), lógica pura de períodos/fechas y componentes de autenticación, agenda, pacientes y alta. Alternativa considerada: una página monolítica, que dificulta probar estados de error y roles.
2. **Sesión en memoria.** Enviar credenciales como `application/x-www-form-urlencoded` a `/auth/token`; después consultar `/auth/yo`. Mantener sólo el token en estado React y agregar `Authorization: Bearer` en el cliente. Ante `401`, vaciar identidad y datos de agenda; ante cierre voluntario, igual. Evita versionar o persistir secretos en `localStorage`. La recarga exige nuevo login.
3. **Proxy del mismo origen.** Vite redirige `/api` a `http://localhost:8000` en desarrollo local; una imagen de frontend construye assets y los sirve con Nginx, que redirige `/api/` al servicio `api:8000` en Compose y aplica fallback SPA. Así no se agrega CORS al backend. El servicio Compose se incorpora en C-15; C-06 integra arranque completo y worker.
4. **Período civil de la máquina del usuario.** Una función pura transforma fecha local elegida en límites `[inicio, fin)` del día o de la semana lunes-domingo y envía instantes ISO con zona/offset explícito. Se muestra la zona horaria en la UI. La API conserva la autoridad sobre la intersección, orden y estados. No se adopta una política clínica de zona horaria global todavía.
5. **Roles por identidad servida.** `recepcion` y `responsable` pueden ver formulario y pacientes; `odontologo` usa siempre `profesional_id` vinculado, con ese filtro no editable. La API sigue rechazando accesos ilegales aunque el DOM se manipule. Si un odontólogo no trae `profesional_id`, se muestra error de configuración sin pedir una agenda sin filtro.
6. **Recursos sin catálogo.** Para profesional, box y prestación se admiten identificadores de texto con pistas de datos demo en documentación; no se inventa un endpoint ni se confunde un ID ingresado con disponibilidad. Pacientes sí se buscan por `GET /pacientes`, y el `id` de una selección o alta se envía a `POST /turnos`.
7. **Errores fieles al servidor.** El cliente normaliza `{codigo, detalle}` y `detail` de FastAPI en un mensaje legible, conservando estado HTTP y código; 409 y 422 no borran el formulario. Tras un `201`, se reconsulta agenda; si esa reconsulta falla, se mantiene la confirmación del alta y se informa que la vista no se actualizó.

## Risks / Trade-offs

- [El navegador se cierra o recarga] → La sesión en memoria se pierde y se vuelve a pedir login; es deliberado para este MVP interno.
- [Zona horaria local distinta de la clínica] → Mostrar zona explícita en la interfaz y enviar límites con offset; la configuración de zona clínica queda para una decisión posterior.
- [No hay catálogos de recursos] → Campos de ID con ejemplos ficticios, validación de longitud y errores `404` de la API; el catálogo corresponde a un change futuro.
- [La API o el proxy no responden] → Distinguir fallo de red de lista vacía y ofrecer reintento.

## Migration Plan

Agregar `frontend/` y su servicio Compose sin migraciones de datos. Verificar build y pruebas frontend; verificar proxy con API en Compose. Para revertir, retirar el servicio frontend y sus assets sin alterar datos del backend.
