---
name: overleaf-ols
description: >-
  Sincroniza proyectos Overleaf (cuenta gratuita) con carpetas locales en
  phd-papers usando overleaf-sync (ols). Usar cuando el usuario trabaje con
  Overleaf sin Git premium, pida pull/push con ols, o edite papers en
  repositorios/phd-papers.
---

# Overleaf-sync (ols)

## Cuándo usar

- Cuenta Overleaf **gratuita** (sin `git.overleaf.com`).
- Sincronizar `papers/<slug>/` en `phd-papers` con un proyecto en overleaf.com.
- Antes o después de editar `.tex` en Cursor cuando la copia canónica compartida está en Overleaf.

## Cuándo NO usar

- Overleaf con **Git oficial** (premium, Commons, institucional) → skill **`overleaf-mcp`**.
- El LaTeX solo vive en otro repo (p. ej. `plan_innovacion/plan_latex/`) sin proyecto Overleaf enlazado.
- Commits o push git del repo `phd-papers` → skill **`git-workflow`** (permiso explícito).

## Repositorio

Raíz: `/home/santhiperbolico/Documentos/Doctorado/repositorios/phd-papers`

- Venv: `phd-papers/.venv` → `source .venv/bin/activate`, comando `ols`.
- Cookie: `~/.config/phd-ols/.olauth.json` (overleaf-sync 2.x; nunca en git). Login:
  `ols login --auth-file ~/.config/phd-ols/.olauth.json`. Migración desde pickle:
  `phd-papers/scripts/migrate_olauth.py`.
- Metadatos por paper: `papers/<slug>/paper.yaml` (`overleaf_project_name`).

## Flujo

1. Leer `paper.yaml` del slug; el nombre en Overleaf debe coincidir **exactamente** con `overleaf_project_name`.
2. `git checkout paper/<slug>` (rama del artículo; ver `paper.yaml` → `git_branch`).
3. **Inicio de edición:** `git pull` → `ols --auth-file ~/.config/phd-ols/.olauth.json -r -p papers/<slug> -n "<overleaf_project_name>"`.
4. Editar en `papers/<slug>/`; compilar con `latexmk` si hace falta.
5. **Cierre:** `git commit` (si el usuario lo pide) → `ols --auth-file ~/.config/phd-ols/.olauth.json -l -p papers/<slug> -n "<overleaf_project_name>"`.
6. Bidireccional interactivo: `ols` sin `-l`/`-r` (puede preguntar en conflictos; no usar en cron sin supervisión).

Variables útiles en shell:

```bash
export OLS_AUTH=~/.config/phd-ols/.olauth.json
ols --auth-file "$OLS_AUTH" -r -p papers/<slug> -n "<name>"
```

## Reglas críticas

- No commitear `.olauth`, `.olsync-state.json` ni cookies.
- No editar el mismo fichero en Overleaf y en local sin sincronizar antes.
- Tras cambios en la web de Overleaf, esperar **1–2 minutos** antes de `ols -r`.
- `paper.yaml` y `.olignore` están en `.olignore` del paper: no suben a Overleaf.
- API no oficial: si `ols` falla tras actualización de Overleaf, revisar [issues del proyecto](https://github.com/moritzgloeckl/overleaf-sync/issues).

## Salida esperada

- Comandos `ols` ejecutados (o preparados para el usuario) con rutas y nombre de proyecto correctos.
- Recordatorio de `git commit` si hubo cambios locales importantes.
- Sin exponer la cookie de sesión.

## Referencias

- `/home/santhiperbolico/Documentos/Doctorado/repositorios/phd-papers/README.md`
- Skill **`phd-paper-new`** para crear `papers/<slug>/`.
