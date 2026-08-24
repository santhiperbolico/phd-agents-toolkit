# MCP correo UPM

Servidor MCP en Python (FastMCP) para **leer y enviar** correo de la
Universidad Politécnica de Madrid desde Cursor, usando IMAP SSL y SMTP
STARTTLS según la [guía oficial de clientes](https://www.upm.es/UPM/ServiciosTecnologicos/email/Alumnos/Ayuda/ConfiguracionClientes/DatosConfiguracion).

## Spec

**Entrada:** dirección UPM (`@alumnos.upm.es` o `@upm.es`) y contraseña, más
carpeta IMAP, UID, filtros o destinatarios.

**Salida:** nombres de carpetas, resúmenes de mensajes, cuerpo de un mensaje
(truncado) o confirmación de envío.

**Tools:**

1. `list_folders` — carpetas IMAP seleccionables.
2. `list_messages` — mensajes recientes (los más nuevos primero); filtros
   opcionales de no leídos, From, Subject y texto.
3. `get_message` — un mensaje por UID (cuerpo truncado a 20 000 caracteres).
4. `send_message` — envío de texto plano.

**Errores:** variables de entorno ausentes, dominio no UPM, autenticación
IMAP/SMTP, carpeta o UID inexistentes, destinatarios inválidos.

**Seguridad:** la contraseña solo vive en el entorno de Cursor (`mcp.json`).
No se escribe en git ni se muestra en logs. Confirma con el usuario antes de
enviar.

## Requisitos

- Python 3.11.
- Cuenta de correo UPM activa.
- IMAP SSL (993) y SMTP STARTTLS (587) alcanzables desde el portátil.

| Tipo | Dirección | IMAP | Usuario IMAP | SMTP |
| --- | --- | --- | --- | --- |
| Alumnos | `nombre.apellido@alumnos.upm.es` | `correo.alumnos.upm.es:993` | `nombre.apellido` | `smtp.upm.es:587` (usuario = dirección completa) |
| Personal | `nombre.apellido@upm.es` | `correo.upm.es:993` | `nombre.apellido` | igual |

SSL es obligatorio. El puerto 25 no es válido.

## Instalación

Desde la **raíz del toolkit** (el agente no ejecuta `make`/`pip`; hazlo tú):

```bash
sudo apt install python3.11-venv   # una vez, si ensurepip falla
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
make install-mcp
```

Eso instala `~/.local/bin/upm-mail-tools` (junto a Overleaf y Taurus) y enlaza
la skill `upm-mail` en `~/.cursor/skills/`.

Para **tests** de este paquete:

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/upm-mail
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
python3.11 -m pip install -U pip
python3.11 -m pip install -e ".[dev]"
pre-commit install
```

## Configuración en Cursor

1. Copia el bloque de `mcp.json.example` (o el combinado `mcp/mcp.json.example`)
   y **mézclalo** con tus servidores MCP. No sustituyas el fichero entero.
2. Ruta habitual: `~/.cursor/mcp.json`.
3. Pon tu dirección y contraseña. No las subas a git.

| Variable | Obligatorio | Significado |
| --- | --- | --- |
| `UPM_MAIL_ADDRESS` | sí | Dirección completa UPM |
| `UPM_MAIL_PASSWORD` | sí | Contraseña de la cuenta |

Ejemplo mínimo:

```json
{
  "mcpServers": {
    "upm-mail": {
      "command": "~/.local/bin/upm-mail-tools",
      "args": ["mcp"],
      "env": {
        "PATH": "~/.local/bin:/usr/share/cursor/resources/app/resources/helpers:/usr/bin:/bin",
        "UPM_MAIL_ADDRESS": "nombre.apellido@alumnos.upm.es",
        "UPM_MAIL_PASSWORD": "replace_me"
      }
    }
  }
}
```

Tras guardar `mcp.json`, recarga Cursor (**Developer: Reload Window**) y
comprueba que el servidor `upm-mail` aparece en MCP.

## Tests y pre-commit

```bash
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit/mcp/upm-mail
source .venv/bin/activate
pytest
cd /home/santhiperbolico/Documentos/Doctorado/repositorios/phd-agents-toolkit
pre-commit run --config mcp/upm-mail/.pre-commit-config.yaml --all-files
```

Los tests usan clientes IMAP/SMTP falsos; no conectan a los servidores de la UPM.

## Limitaciones (v1)

- Sin adjuntos en el envío; el cuerpo es texto plano.
- Sin borrar, mover ni marcar mensajes.
- El cuerpo leído se trunca a 20 000 caracteres; se listan nombres de adjuntos
  sin descargarlos.
- Como máximo 50 mensajes por listado.
- La conexión IMAP es de solo lectura (`BODY.PEEK` / `SELECT` readonly).
