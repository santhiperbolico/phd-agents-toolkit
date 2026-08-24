# MCP Slack session (solo lectura)

Servidor MCP en Python (FastMCP) para **leer** canales de Slack en workspaces
donde no puedes instalar una app (Euclid, DESI, etc.). Usa los tokens de sesión
del navegador (`xoxc` + cookie `d`), sin OAuth ni aprobación de administradores.

## Spec

**Entrada:** una o más workspaces con credenciales propias
(`alias:host:xoxc-token:xoxd-cookie`).

**Salida:** workspaces configurados, canales visibles, mensajes recientes,
búsquedas y hilos.

**Tools (solo lectura):**

1. `list_workspaces` — alias, subdominio y verificación del token.
2. `list_channels` — canales públicos/privados donde eres miembro.
3. `read_channel` — historial reciente por nombre (`#foo`) o ID.
4. `search_messages` — búsqueda con sintaxis Slack (`in:canal`, fechas, etc.).
5. `read_thread` — mensajes de un hilo por `thread_ts`.

**Errores:** variables de entorno ausentes, token caducado, canal inexistente o
sin permisos.

**Seguridad:** los tokens equivalen a tu cuenta de Slack. Guárdalos solo en
`~/.cursor/mcp.json`. No se escriben en git ni se muestran en logs. Este MCP
**no** envía mensajes ni marca canales como leídos.

## Requisitos

- Python 3.11.
- Cuenta miembro en los workspaces de Slack que quieras consultar.
- Sesión activa en el navegador (para extraer credenciales).

## Instalación

Desde la **raíz del toolkit**:

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
make install-mcp
```

Eso instala `~/.local/bin/slack-session-tools` y enlaza la skill en
`~/.cursor/skills/slack-session`.

Para **tests** de este paquete:

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/slack-session
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -U pip
python3.11 -m pip install -e ".[dev]"
pre-commit install
pytest
```

## Obtener credenciales

### Opción A — automática con Playwright (recomendada)

Tras `make install-mcp`, instala el navegador **una vez**:

```bash
~/.local/share/phd-agents-mcp/venv/bin/playwright install chromium
```

Captura credenciales por workspace (abre Chromium, inicia sesión en Slack y
espera a que cargue un canal):

```bash
slack-session-tools auth extract --alias euclid
slack-session-tools auth extract --alias desi --merge "$(jq -r '.mcpServers["slack-session"].env.SLACK_WORKSPACES' ~/.cursor/mcp.json)"
```

El comando imprime la línea lista para pegar en `~/.cursor/mcp.json` →
`slack-session` → `env` → `SLACK_WORKSPACES`.

- Cada alias usa un perfil persistente en
  `~/.local/share/slack-session-tools/profiles/<alias>/` (útil con correos distintos).
- Repite `auth extract` cuando caduque la sesión.
- `--json` devuelve JSON si el agente va a procesar la salida.
- `--headless` solo si el perfil ya está logueado.

### Opción B — manual con DevTools

1. Abre cada workspace en `app.slack.com` (Euclid, DESI, …) con tu usuario.
2. DevTools (F12) → **Red** → filtra `api/` → abre una petición → copia el
   campo `token` (`xoxc-...`). Hay un token **por workspace y por cuenta**.
3. DevTools → **Aplicación** → Cookies → `slack.com` → copia el valor de `d`
   (`xoxd-...`). Si usas **correos distintos** en Euclid y DESI, extrae una
   cookie **por cuenta** (idealmente con cada workspace abierto en su perfil o
   ventana de navegador).
4. El **team ID** está en la URL de `app.slack.com`:
   `https://app.slack.com/client/**T01234567**/C01234567`.
   También puedes usar el subdominio clásico (`https://**nombre**.slack.com`).

Si caduca la sesión (logout, SSO, cambio de contraseña), repite la extracción.

## Configuración en Cursor

1. Copia el bloque de `mcp.json.example` y **mézclalo** con tus servidores MCP.
2. Ruta habitual: `~/.cursor/mcp.json`.
3. Sustituye los placeholders. No los subas a git.

| Variable | Obligatorio | Significado |
| --- | --- | --- |
| `SLACK_WORKSPACES` | sí | Lista `alias:host:xoxc:xoxd` separada por comas |

`host` puede ser el **team ID** de la URL (`app.slack.com/client/TEAM_ID/...`) o el
subdominio clásico (`euclid-team` de `euclid-team.slack.com`).

`SLACK_SESSION_COOKIE` solo hace falta si usas entradas de tres campos con la
misma cuenta de Slack en todos los workspaces.

Ejemplo con **dos correos distintos** (recomendado para Euclid y DESI):

```json
"slack-session": {
  "command": "~/.local/bin/slack-session-tools",
  "args": ["mcp"],
  "env": {
    "PATH": "~/.local/bin:/usr/share/cursor/resources/app/resources/helpers:/usr/bin:/bin",
    "SLACK_WORKSPACES": "euclid:TYYYY:xoxc-euclid-token:xoxd-euclid-cookie,desi:TXXXX:xoxc-desi-token:xoxd-desi-cookie"
  }
}
```

Sustituye `TYYYY` y `TXXXX` por los IDs de la URL
(`https://app.slack.com/client/TYYYY/...`).

Ejemplo con **una sola cuenta** para ambos workspaces:

```json
"env": {
  "SLACK_SESSION_COOKIE": "xoxd-shared-cookie",
  "SLACK_WORKSPACES": "euclid:euclid-subdomain:xoxc-euclid-token,desi:desi-subdomain:xoxc-desi-token"
}
```

Recarga Cursor tras guardar `mcp.json`.

## Uso típico (agente)

1. `list_workspaces` — comprobar que los tokens siguen válidos.
2. `list_channels(workspace="euclid")` — localizar el canal.
3. `read_channel(workspace="euclid", channel="#data-release", limit=20)`.
4. `search_messages(workspace="desi", query="in:spectroscopy deadline after:2026-01-01")`.
5. Si un mensaje tiene `reply_count`, `read_thread` con su `ts` o `thread_ts`.

## Limitaciones

- Solo canales/DMs a los que ya tienes acceso en el navegador.
- La búsqueda usa `search.messages` en `slack.com` (comportamiento del cliente web).
- Sin descarga de ficheros adjuntos en v1.
- Sin escritura: no hay `chat.postMessage` ni marcar como leído.
- Uso no documentado por Slack; tokens de sesión personales, no compartir.

## Aviso legal

Este MCP reutiliza credenciales de tu sesión web para automatizar lecturas que ya
puedes hacer manualmente. Úsalo solo con fines personales de investigación y
renueva los tokens si Slack invalida la sesión.
