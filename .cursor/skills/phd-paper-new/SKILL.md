---
name: phd-paper-new
description: >-
  Arranca un artículo en phd-papers: comprobaciones git (main), rama paper/<slug>,
  descarga desde Overleaf, limpieza plantilla A&A, push ols y metadatos. Usar al
  crear un paper nuevo con proyecto Overleaf ya existente o plantilla A&A.
---

# Nuevo artículo (phd-papers)

## Cuándo usar

- Alta de un **nuevo** artículo con proyecto ya creado en Overleaf (plantilla A&A por defecto).
- URL tipo `https://www.overleaf.com/project/<id>`.

## Cuándo NO usar

- Editar un paper existente → `papers/<slug>/` y **`overleaf-ols`**.
- Plan CAPD → `plan_innovacion/`.
- Overleaf Git premium → **`overleaf-mcp`**.

## Preflight git (obligatorio, antes de cualquier acción)

Repo: `/home/santhiperbolico/Documentos/Doctorado/repositorios/phd-papers`

1. Ejecutar (o equivalente mental):

```bash
python3.11 scripts/git_paper_preflight.py <slug>
```

2. Si falla:
   - Estás en **`paper/<otro-artículo>`** → **parar**. Indica la rama actual, pide revisar/commit, `git checkout main`, y solo entonces continuar.
   - No estás en **`main`** → **parar**. Mismo mensaje: revisar cambios, volver a `main`.
   - **`main` sucio** → **parar**. Pedir commit o stash en `main` antes de crear la rama del nuevo artículo.

3. No crear carpeta ni llamar a Overleaf hasta que el preflight pase (salvo `--allow-dirty-main` solo si el usuario lo pide explícitamente).

## Datos necesarios

| Campo | Uso |
| --- | --- |
| `slug` | `papers/<slug>/`, rama `paper/<slug>` |
| `--overleaf-name` | Nombre **exacto** en Overleaf (`ols list`) |
| `--overleaf-id` | Id de la URL del proyecto |
| `--title` | `\title{...}` tras limpiar la demo |
| `--subtitle` | Opcional (default `Article I`) |

Auth: `~/.config/phd-ols/.olauth.json` (overleaf-sync 2.x). Si solo hay pickle legacy: `python3.11 scripts/migrate_olauth.py`.

## Flujo (bootstrap)

Desde la raíz de `phd-papers`, venv activado:

```bash
source .venv/bin/activate
python3.11 scripts/bootstrap_paper.py <slug> \
  --overleaf-name "<Exact Overleaf name>" \
  --overleaf-id "<project-id>" \
  --title "<LaTeX title>" \
  --subtitle "Article I"
```

El script:

1. Preflight git y `git checkout -b paper/<slug>`.
2. Descarga zip del proyecto Overleaf.
3. Escribe `paper.yaml`, `.olignore`.
4. **`clean_aa_article.py`** — sustituye la demo `aa_example.tex`, crea `references.bib`, quita `figure.eps`.
5. **`ols -l`** — sube la versión limpia a Overleaf.

Después: `git add papers/<slug>` y commit en la rama `paper/<slug>` (solo con permiso explícito del usuario).

## Plantilla Overleaf por defecto

[Astronomy and Astrophysics](https://www.overleaf.com/latex/templates/astronomy-and-astrophysics-template/ngdddtchkbcg). Esqueleto local: `templates/astronomy-and-astrophysics/aa_article_clean.tex`.

## Reglas críticas

- Una rama git **`paper/<slug>`** por artículo; `main` solo infra compartida y merges cuando toque.
- No commitear `.olauth`, `.olauth.json` en el repo (están en `~/.config/phd-ols/`).
- Tras limpiar, el main en Overleaf sigue siendo **`aa_example.tex`** (no renombrar sin cambiar el compiler en Overleaf).
- `overleaf-sync` **2.0.0rc1** en `requirements.txt`; 1.2.x no lista proyectos en overleaf.com actual.

## Salida esperada

- `papers/<slug>/` con fuentes sincronizables.
- Overleaf actualizado con la plantilla limpia.
- Usuario informado de la rama `paper/<slug>` y del siguiente paso (`overleaf-ols`).

## Referencias

- `/home/santhiperbolico/Documentos/Doctorado/repositorios/phd-papers/README.md`
- Skill **`overleaf-ols`**
