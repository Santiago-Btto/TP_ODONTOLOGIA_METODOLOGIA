# Context7 MCP para preparar C-02

Context7 aporta **documentación actual de bibliotecas** al agente. En este trabajo se usa para contrastar decisiones técnicas de `consultar-agenda` con las guías de FastAPI y SQLAlchemy 2.0. Su uso previsto es de lectura: no consulta la base de turnos ni modifica GitHub, los archivos del proyecto o datos de pacientes.

## Estado y requisitos

En la máquina de trabajo ya existía una conexión global `context7` de tipo `stdio`, habilitada y operativa. Por eso se conservó ese modo en vez de instalar de nuevo el servidor remoto con clave previsto en la [ficha de investigación](investigacion.md). El servidor es el mismo; cambió sólo la forma de conectarse. Se verificó con `codex mcp get context7 --json` y con llamadas reales a `resolve-library-id` y `query-docs` ([registro de uso](evidencias/context7-uso.md)).

Para reproducir esta conexión se necesitan Codex con soporte MCP, Node.js con `npx`, permiso para descargar el paquete `@upstash/context7-mcp@2.2.5` y acceso a Internet tanto para la descarga inicial como para las consultas posteriores al servicio Context7. La configuración vive en `~/.codex/config.toml` del usuario (en Windows, normalmente `%USERPROFILE%\.codex\config.toml`) y se comparte entre Codex CLI y la app de escritorio. El archivo de ejemplo [context7.example.toml](context7.example.toml) **no está activo** y no contiene credenciales.

Si `context7` todavía no aparece en `codex mcp list`, registrarlo con:

```text
codex mcp add context7 -- npx -y --package=@upstash/context7-mcp@2.2.5 -- context7-mcp
```

También se puede copiar **sólo la tabla** de `context7.example.toml` al `config.toml` global, sin sobrescribir las otras entradas. En modo local `stdio` y para la consulta pública realizada no se necesitó variable de entorno ni credencial. Si el equipo necesita límites mayores, Context7 documenta la clave opcional `CONTEXT7_API_KEY`; debe definirse en el entorno personal, nunca en Git. La alternativa remota estudiada en la Parte 1 usa `--bearer-token-env-var CONTEXT7_API_KEY`.

## Comprobación y uso

1. Ejecutar `codex mcp list --json` y comprobar que `context7` figure con `enabled: true`.
2. Abrir una sesión nueva de Codex en este repositorio y comprobar que ofrece `resolve-library-id` y `query-docs` (los nombres internos pueden mostrarse como `resolve_library_id` y `query_docs`).
3. Solicitar: «Usá Context7: resolvé FastAPI y consultá cómo declarar parámetros de query obligatorios y opcionales para `GET /api/v1/agenda`». Repetir con SQLAlchemy 2.0 para `select().where()`, `order_by()` y `Session.scalars()`.
4. Comprobar que la respuesta incluya un identificador de biblioteca y un enlace a documentación de FastAPI o SQLAlchemy. El [registro](evidencias/context7-uso.md) contiene la solicitud y el resultado observado en este proyecto.

El agente debe enviar a Context7 **solamente preguntas técnicas públicas**. No incluir pacientes reales, secretos, código privado ni datos de producción. Las respuestas son referencias técnicas y no deciden reglas odontológicas: cualquier propuesta de dominio se verifica contra `knowledge-base/`. Context7 se documenta como **MCP**, no se registra como una skill.

## Si algo falla

No apareció un problema de instalación en esta sesión: la entrada global ya existía y las herramientas respondieron. Si no se ven herramientas, revisar `codex mcp list --json`, reiniciar la sesión tras cambiar la configuración y comprobar que `npx` está disponible. Si no descarga el paquete, revisar conectividad o restricciones de red. Si la consulta queda limitada por cuota, consultar los límites del plan y configurar una clave propia fuera del repositorio; no copiar tokens en evidencias.

Fuentes: [Context7 para Codex](https://github.com/upstash/context7/blob/master/docs/clients/codex.mdx), [servidor y herramientas](https://github.com/upstash/context7), [configuración MCP de Codex](https://learn.chatgpt.com/docs/extend/mcp?surface=cli). Consultadas el 29/10/2026.
