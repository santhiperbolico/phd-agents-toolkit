# PhD Agents Toolkit

Repositorio compartido de **reglas** y **skills** para Vibecoding con Cursor en **proyectos de doctorado** (investigación, análisis de datos, simulaciones, pipelines científicos).

No contiene código de investigación: centraliza convenciones Python, calidad (pre-commit), pytest, Git y flujo con agentes.

## Idioma

| Qué | Idioma |
| --- | --- |
| Respuestas del agente | Castellano |
| Código, docstrings, commits | Inglés |

## Workspace en Cursor (multi-root)

Las reglas y skills de este repo **solo se cargan** si `phd-agents-toolkit` está en el workspace de Cursor. No hace falta copiar `.cursor/` a cada repo de investigación.

### Pasos

1. Clona este repo junto a tus proyectos (p. ej. `~/Documentos/Doctorado/reposotorios/phd-agents-toolkit`).
2. **File → Add Folder to Workspace** → selecciona `phd-agents-toolkit`.
3. Añade los repos en los que trabajes (`plan_investigacion`, análisis electorales, pipelines Gaia, …).
4. **File → Save Workspace As…** → guarda un `.code-workspace` reutilizable.

Pon **`phd-agents-toolkit` como primera carpeta** para que el agente localice rápido [.cursor/AGENTS.md](.cursor/AGENTS.md).

### Ejemplo `phd-research.code-workspace`

Ajusta rutas según tu máquina:

```json
{
  "folders": [
    {
      "path": "../reposotorios/phd-agents-toolkit",
      "name": "phd-agents-toolkit"
    },
    {
      "path": "../plan_investigacion/plan_investigacion",
      "name": "plan-investigacion"
    }
  ],
  "settings": {}
}
```

Si abres **un solo repo** sin `phd-agents-toolkit`, no tendrás reglas ni skills comunes. Añade temporalmente esta carpeta al workspace o abre el `.code-workspace` completo.

### Actualizar el toolkit

```bash
cd ~/Documentos/Doctorado/reposotorios/phd-agents-toolkit && git pull
```

Si no aparecen reglas nuevas: **Developer: Reload Window** en Cursor.

---

## Qué va aquí vs en cada repo

- **Aquí:** reglas y skills reutilizables entre proyectos de doctorado.
- **En cada repo:** contexto de la investigación — metodología, datasets, convenciones de dominio.

Con el workspace multi-root, Cursor combina ambos. Para el detalle, mirar `.cursor/rules/` y `.cursor/skills/` en este repo y en el de investigación.

## Contribuir

- Convenciones **compartidas** entre proyectos PhD → PR hacia `main` en este repo.
- No duplicar reglas que solo aplican a un proyecto concreto.
- Commits en **inglés**; respuestas del agente en **castellano** (ver regla `language-conventions`).

## Repositorio

[github.com/santhiperbolico/phd-agents-toolkit](https://github.com/santhiperbolico/phd-agents-toolkit)
