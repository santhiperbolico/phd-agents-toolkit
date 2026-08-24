---
name: slack-session
description: >-
  Lee canales de Slack (Euclid, DESI, etc.) con el MCP slack-session usando
  tokens de sesión del navegador. Solo lectura, sin instalar app en el
  workspace. Usar cuando el usuario pregunte por mensajes, hilos, búsquedas
  en Slack de consorcios científicos, o quiera extraer credenciales para
  mcp.json.
---

# Slack session (MCP, solo lectura)

## Cuándo usar

- Leer mensajes de workspaces Slack donde no hay app instalada (Euclid, DESI).
- Listar canales a los que el usuario ya tiene acceso.
- Buscar en Slack con sintaxis `in:canal`, `from:@usuario`, fechas.
- Leer hilos completos a partir de un `thread_ts`.
- **Configurar** `SLACK_WORKSPACES` en `~/.cursor/mcp.json` (extracción con
  Playwright o renovación de tokens).

## Cuándo NO usar

- Enviar mensajes, reacciones o marcar como leído (no está en este MCP).
- Workspaces con MCP oficial de Slack ya configurado y aprobado.
- El servidor `slack-session` no está conectado: indicar el README de
  `mcp/slack-session/`.
- Descargar adjuntos de Slack (no está en v1).

## Flujo

1. Comprobar que el MCP `slack-session` (o `user-slack-session`) está activo.
2. `list_workspaces` — ver alias (`euclid`, `desi`) y que el token sigue válido.
3. `list_channels(workspace=...)` si no conoces el nombre del canal.
4. `read_channel` con `limit` pequeño (10–20) para contexto reciente.
5. `search_messages` para preguntas abiertas o histórico filtrado.
6. `read_thread` cuando haya `reply_count` o necesites el hilo completo.

## Extraer credenciales para mcp.json (Playwright)

Usar cuando el usuario no tenga aún `SLACK_WORKSPACES` o pida renovar tokens.

1. Comprobar que `slack-session-tools` está instalado (`make install-mcp`).
2. Si falta Chromium: `~/.local/share/phd-agents-mcp/venv/bin/playwright install chromium`
3. Ejecutar en terminal (el usuario debe ver el navegador e iniciar sesión):

```bash
slack-session-tools auth extract --alias euclid
slack-session-tools auth extract --alias desi --merge "<valor actual de SLACK_WORKSPACES>"
```

4. Copiar la línea `SLACK_WORKSPACES` impresa a `~/.cursor/mcp.json`.
5. Recargar Cursor y probar `list_workspaces`.

Reglas:

- Un `auth extract` por alias (`euclid`, `desi`); perfiles separados si los correos son distintos.
- No mostrar tokens en chat ni commits; pegar solo en `mcp.json` local.
- Si el comando hace timeout, el usuario debe terminar el login y abrir un canal antes de que acabe el plazo (`--timeout 600` si hace falta).
- Alternativa sin CLI: MCP `user-playwright` + DevTools (más frágil); preferir `auth extract`.

## Sintaxis de búsqueda útil

- `in:channel-name` — limitar a un canal.
- `from:@usuario` — mensajes de una persona.
- `after:2026-01-01` / `before:2026-06-01` — rango de fechas.
- `"frase exacta"` — comillas para frase literal.

## Reglas críticas

- Nunca mostrar, loguear ni commitear tokens `xoxc` ni cookies `xoxd`.
- Euclid y DESI con **correos distintos** → credenciales distintas por entrada
  en `SLACK_WORKSPACES` (`alias:T_TEAM_ID:xoxc:xoxd`).
- No inventar nombres de canal; usar `list_channels` o IDs de mensajes previos.
- Preferir resúmenes a volcar historiales enteros.
- Si falla `invalid_auth` o `token_revoked`, pedir al usuario que renueve tokens
  en el navegador y actualice `~/.cursor/mcp.json`.
- No intentar escribir en Slack con este MCP.

## Relación con otras skills

| Necesidad | Skill / MCP |
| --- | --- |
| Slack Euclid/DESI (lectura) | **slack-session** (este MCP) |
| Slack con app oficial | `plugin-slack-slack` (requiere consentimiento admin) |
| Papers y bibliografía | `zotero-phd` |
| Correo UPM | `upm-mail` |

## Referencias

- [README.md](../README.md)
- Extracción de tokens: sección «Obtener credenciales» del README.
