---
name: git-workflow
description: >-
  Flujo Git: crear ramas, add selectivo, commit en inglés y push seguro. Usar
  cuando el usuario pida rama nueva, commit, push, gestión Git o preparar
  cambios (commit/push solo con permiso explícito; ver regla git-conventions).
---

# Flujo Git — ramas, commit y push

Cumple siempre la regla `git-conventions` (permisos, ramas protegidas, inglés en commits). Esta skill es el procedimiento operativo.

## Cuándo usar

- Crear una rama de trabajo para una feature o fix.
- Commit, push o preparar cambios para commit.
- Cerrar un encargo con commit/push.
- Convenciones de mensaje de commit o nombre de rama.

## Cuándo NO usar

- Revisar PRs → skill `code-review`.
- Resolver conflictos de merge complejos (orientar al usuario).

---

## Metodología de branching

Flujo simple orientado a GitHub:

| Tipo | Rama base | Merge destino (PR) |
| --- | --- | --- |
| **Feature** | `main` | `main` |
| **Fix** | `main` | `main` |
| **Docs** | `main` | `main` |

```
main ──●──●──●──────────────────────────────► integración
        \
         └── feature/electoral-simulation ──► PR ──► main
```

### Crear rama (comandos)

Feature desde `main`:

```bash
git fetch origin && git checkout main && git pull --ff-only origin main
git checkout -b feature/electoral-simulation
```

Fix:

```bash
git fetch origin && git checkout main && git pull --ff-only origin main
git checkout -b fix/gaia-query-timeout
```

### Reglas para el agente

- Merge a `main`/`master`: **solo vía PR**; el agente no hace merge local ni push a esas ramas.
- No trabajar directamente en `main`/`master` sin rama intermedia.

---

## Convención de nombre de rama

```
[feature|fix|docs]/slug-en-kebab-case
```

| Parte | Formato | Ejemplo |
| --- | --- | --- |
| prefijo | `feature/`, `fix/`, `docs/` (opcional) | `feature/` |
| slug | Minúsculas, guiones, sin espacios | `electoral-simulation`, `gaia-pipeline` |

Ejemplos válidos: `feature/electoral-simulation`, `fix/catalog-timeout`, `docs/research-plan`.

Sin prefijo también válido: `electoral-analysis`, `gaia-pipeline`.

### Flujo

1. **Slug** acordado con el usuario si hace falta.
2. **Rama base:** `main` (o `master` si el repo lo usa).

```bash
git branch -a
git remote show origin | sed -n '/HEAD branch/s/.*: //p'
```

3. **Actualizar referencias** y ramificar:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
git checkout -b feature/my-feature
git branch --show-current
```

4. Si ya hay cambios locales sin commitear, valorar `git stash` antes del checkout; explicar al usuario qué opción aplicas.

### Permisos (ramas)

- **Crear y cambiar ramas locales:** permitido sin permiso explícito.
- **Push de la rama nueva:** requiere permiso explícito:

```bash
git push -u origin feature/my-feature
```

---

## Commit y push

### Permiso y ramas protegidas

- No ejecutar `git commit` ni `git push` sin permiso explícito en el hilo (regla `git-conventions`).
- **Prohibido** commit o push en `main` o `master` — **incluso si el usuario lo pide**. Explicar que el merge va por PR.

Antes de commit o push:

```bash
git branch --show-current
```

Si la salida es `main` o `master`, **parar**.

### 1. Inspección inicial (en paralelo)

```bash
git status --short
git diff && git diff --staged
git log -5 --oneline
```

### 2. Revisar `.gitignore` (antes del stage)

Con `git status`, identificar **untracked** (`??`) que no deban versionarse. Patrones habituales:

- `.venv/`, `__pycache__/`, `.ipynb_checkpoints/`
- `.env`, credenciales, tokens
- `data/`, `models/`, artefactos pesados
- `.coverage`, `htmlcov/`, cachés de IDE

```bash
git check-ignore -v path/to/file || echo "NOT ignored"
```

Si **debe** ignorarse y no lo está: actualizar `.gitignore` antes del stage.

### 3. Stage selectivo

```bash
git add <paths_for_task>
```

- Rutas explícitas; evitar `git add .` si hay ruido.
- No incluir secretos.

### 4. Commit

**Solo con permiso explícito** y **nunca** en `main`/`master`. **Inglés** (regla `language-conventions`).

```bash
git commit -m "$(cat <<'EOF'
Add Monte Carlo simulation for seat allocation

Optional body: what and why in one or two sentences.
EOF
)"
```

### 5. Push

**Solo con permiso explícito** y **nunca** a `main` ni `master`.

```bash
BRANCH=$(git branch --show-current)
# abort if BRANCH is main or master
git push -u origin "$BRANCH"
```

- Sin `--force` salvo petición explícita en rama de feature (nunca en ramas protegidas).

---

## Checklist rápido

- [ ] Rama actual **no** es `main` ni `master`.
- [ ] Rama creada desde `main` (o `master`).
- [ ] Untracked revisados; `.gitignore` actualizado si hace falta.
- [ ] Permiso explícito para commit; para push, permiso explícito o «commit y push».
- [ ] Solo archivos del encargo en stage.
- [ ] Mensaje de commit en **inglés**.
- [ ] Pre-commit pasado si aplica.
