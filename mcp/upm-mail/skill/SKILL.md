---
name: upm-mail
description: >-
  Lee y envía correo de la Universidad Politécnica de Madrid (IMAP/SMTP)
  con el MCP upm-mail. Usar cuando el usuario hable de correo UPM,
  alumnos.upm.es, bandeja de entrada, mensajes de la universidad o
  enviar un email desde la cuenta institucional.
---

# Correo UPM (MCP)

## Cuándo usar

- Listar carpetas o mensajes de la cuenta `@alumnos.upm.es` o `@upm.es`.
- Buscar correos por remitente, asunto, texto o no leídos.
- Leer el cuerpo de un mensaje concreto.
- Enviar un correo de texto plano desde la cuenta UPM.

## Cuándo NO usar

- Gmail, Outlook personal u otras cuentas que no sean UPM.
- Overleaf, Zotero, Taurus o tareas de Notion.
- El servidor MCP `upm-mail` no está conectado: indicar el README de
  `mcp/upm-mail/`.
- Adjuntos, HTML rico, borrar o mover mensajes (no está en v1).

## Flujo

1. Comprobar que el MCP `upm-mail` (o `user-upm-mail`) está activo.
2. `list_folders` si hace falta una carpeta distinta de `INBOX`.
3. `list_messages` con filtros (`unread_only`, `from_address`, `subject`,
   `text`) y un `limit` pequeño.
4. `get_message(uid, folder)` para el cuerpo. El campo `truncated` indica
   si el texto se cortó.
5. `send_message` solo tras **confirmar destinatarios, asunto y cuerpo**
   con el usuario.

## Reglas críticas

- Nunca mostrar, loguear ni commitear `UPM_MAIL_PASSWORD`.
- No enviar correo sin confirmación explícita del usuario.
- No inventar UIDs; usar los de `list_messages`.
- Preferir resúmenes a volcar bandejas enteras.
- Si falla la autenticación, pedir al usuario que revise `UPM_MAIL_ADDRESS`
  y `UPM_MAIL_PASSWORD` en `~/.cursor/mcp.json`; no probar contraseñas.

## Relación con otras skills

| Necesidad | Skill |
| --- | --- |
| Correo institucional UPM | **upm-mail** (este MCP) |
| Papers y bibliografía | `zotero-phd` |
| LaTeX en Overleaf | `overleaf-mcp` |
| Cluster Taurus | `taurus-cluster` |

## Referencias

- [README.md](../README.md)
- [Datos de configuración UPM](https://www.upm.es/UPM/ServiciosTecnologicos/email/Alumnos/Ayuda/ConfiguracionClientes/DatosConfiguracion)
