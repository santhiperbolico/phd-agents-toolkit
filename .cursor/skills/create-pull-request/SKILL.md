---
name: create-pull-request
description: >-
  Orquesta la creación de una PR en repos PhD: code review si el diff supera
  100 líneas, pre-commit y pytest, redacción de la descripción en inglés desde
  el contexto del agente, issues de GitHub o documentación local del repo. Usar
  cuando el usuario pida crear una PR, abrir pull request, preparar merge o
  cerrar un encargo con PR en un proyecto de doctorado.
---

# Crear pull request (repos PhD)

Orquesta los pasos previos y la creación de la PR en repos de investigación.
Respeta la regla `git-conventions`: **push y PR solo con permiso explícito**
del usuario.

**Idioma de la PR:** título y descripción siempre en **inglés** (regla
`language-conventions`). Las respuestas al usuario siguen en castellano.

## Cuándo usar

- El usuario pide crear, abrir o preparar una PR.
- Hay que cerrar un encargo de implementación con PR.
- Se menciona «subir PR», «abrir pull request» o «preparar merge».

## Cuándo NO usar

- Solo commit o push sin PR → `git-workflow`.
- Solo revisar código sin crear PR → `code-review`.
- Repos sin GitHub (solo local) → orientar al usuario; no inventar remoto.

---

## Flujo operativo (orden obligatorio)

```
0. Preparación Git
        ↓
1. Code review (si diff > 100 líneas) → esperar resolución o continuar
        ↓
2. Pre-commit y pytest (si procede) → corregir fallos antes de seguir
        ↓
3. Recopilar contexto (issue GitHub, docs locales, hilo)
        ↓
4. Redactar descripción de la PR (inglés)
        ↓
5. Push (si hace falta) y crear PR en GitHub
```

No saltar pasos ni invertir el orden salvo indicación explícita del usuario.

---

### 0. Preparación Git

Ejecutar **en paralelo** en el repo activo:

```bash
git status --short
git branch -vv
git log -5 --oneline
git remote -v
```

Determinar:

| Dato | Cómo obtenerlo |
| --- | --- |
| Rama actual | `git branch --show-current` |
| Rama base (destino PR) | `main` o `master` del **fork** (`origin`) — ver abajo |
| Remoto del fork | `origin` → `github.com/{tu_usuario}/{repo}.git` |
| Remoto upstream (si existe) | `upstream` → repo principal; **no** usar como base de la PR salvo petición explícita |
| Issue GitHub | Número en rama, commit o contexto del hilo |
| Owner / repo (para PR) | Siempre desde **`origin`**, no desde `upstream` |

**Repos con fork:** la PR va de la rama de trabajo → `main` (o `master`) del
**fork** (`origin`). El merge a `upstream/main` es un paso posterior (otra PR
cross-repo o sincronización manual), no el destino por defecto.

Detectar fork:

```bash
git remote -v
# origin    git@github.com:santhiperbolico/get_nebular_emission.git
# upstream  git@github.com:galform/get_nebular_emission.git
```

Si existe `upstream`, calcular el diff y abrir la PR respecto a **`origin/${BASE}`**,
no `upstream/${BASE}`.

**Issues en el repo upstream:** referenciar como `galform/repo#37` en la
descripción. Usar `Closes #N` solo si el issue vive en el **mismo repo** que la
PR (`origin`).

Comprobar que la rama **no** es `main` ni `master`.

Calcular tamaño del diff respecto a la base:

```bash
BASE=main   # main o master del fork (origin), no upstream
git fetch origin
git diff --numstat "origin/${BASE}...HEAD" | awk '{s+=$1+$2} END {print s+0}'
```

Si `origin/${BASE}` no existe localmente, usar la rama base acordada sin
`origin/`. Registrar el total de líneas **añadidas + eliminadas**.

Buscar plantilla de PR en el repo:

```bash
ls .github/pull_request_template.md .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null
ls .github/PULL_REQUEST_TEMPLATE/*.md 2>/dev/null
```

Si existe, usarla como estructura de la descripción (paso 4).

---

### 1. Code review (condicional: diff > 100 líneas)

**Si el total es ≤ 100:** informar brevemente («diff de N líneas; se omite code
review automático») y pasar al paso 2.

**Si el total es > 100:**

1. Leer y seguir **`code-review/SKILL.md`** sobre el diff
   `origin/${BASE}...HEAD` (o equivalente).
2. Entregar el reporte con el formato de esa skill (Resumen + Hallazgos por
   severidad).
3. **Parar y esperar** al usuario:
   - Si hay hallazgos **Críticos**: recomendar corregirlos antes de la PR.
   - Preguntar explícitamente si **continuar con la PR** o **resolver primero**.
4. **Solo continuar** al paso 2 cuando el usuario confirme o indique que los
   hallazgos están resueltos.

No crear la PR en este paso.

---

### 2. Pre-commit y pytest (si procede)

Validar hooks y tests **antes** de redactar la descripción o abrir la PR.

1. Leer y seguir:
   - **`pre-commit-and-lint/SKILL.md`**
   - **`pytest-and-coverage/SKILL.md`**
2. Obtener ficheros del diff:

   ```bash
   git diff --name-only "origin/${BASE}...HEAD"
   ```

3. **Pre-commit** — si el diff incluye `.py` u otros ficheros cubiertos por
   hooks:
   - Ejecutar desde la raíz del repo o `src/` según `.pre-commit-config.yaml`.
   - Preferir alcance acotado: `pre-commit run --files <ficheros_del_diff>`.
   - Si pre-commit reformatea: re-stage y repetir hasta verde.
4. **Pytest** — si procede:
   - **Sí:** cambios en `tests/` o en código Python bajo test.
   - **No:** solo documentación, config sin tests, o repo sin suite.
   - Ejecutar tests relacionados con el diff; usar `--no-cov` en ejecuciones
     acotadas salvo que el encargo exija cobertura.
5. **Si algo falla:** corregir y **no pasar al paso 3** hasta verde (o el
   usuario indique continuar con fallos conocidos).

Informar al usuario: comandos ejecutados, alcance y resultado (pass/fail).

---

### 3. Recopilar contexto

En repos PhD no hay Jira ni Confluence. Usar estas fuentes **en orden de
prioridad**:

| Prioridad | Fuente | Qué extraer |
| --- | --- | --- |
| 1 | **Issue GitHub** | Título, cuerpo, criterios de aceptación, comentarios |
| 2 | **Documentación del repo** | `README.md`, `docs/`, `specs/`, `notes/` si existen |
| 3 | **Hilo del agente** | Objetivo, decisiones técnicas, resultado alcanzado |
| 4 | **Notion PhD** (opcional) | Solo si el usuario enlazó una tarea concreta |

**Issue GitHub:**

- Detectar número desde rama (`feature/42-*`, `fix/42-*`), mensajes de commit
  (`Fixes #42`) o el hilo.
- MCP `user-github` → `issue_read` con `method: get` (y `get_comments` si hace
  falta contexto).
- Si no hay issue: continuar con docs locales y hilo; no inventar ticket.

**Docs locales:**

- Buscar en el repo activo: `README.md`, `docs/`, `specs/`, `notes/`.
- Para contexto en repos hermanos → skill `phd-local-docs` (solo si aporta al
  encargo).

---

### 4. Redactar descripción de la PR (inglés)

Usar la plantilla de [patterns.md](patterns.md#pr-description-template). Las
secciones **Objective** y **Outcome** deben ser **detalladas**, no una línea
genérica.

**Título** (inglés):

- Con issue: `[#42] Short imperative summary` o `Short summary (#42)`.
- Sin issue: imperativo conciso, ≤72 caracteres, sin punto final.

Si el repo tiene plantilla en `.github/`, adaptarla manteniendo inglés.

Incluir en **References** (si aplica):

- Enlace al issue: `https://github.com/{owner}/{repo}/issues/{N}`
- Enlaces a docs locales del repo (rutas relativas en la descripción).

**Cerrar issue:** si el PR resuelve un issue, añadir en el cuerpo
`Closes #42` (o `Fixes #42`) para el autocierre de GitHub.

---

### 5. Push y crear PR

**Push:** solo con permiso explícito del usuario.

```bash
git push -u origin "$(git branch --show-current)"
```

**Crear PR** en GitHub (preferir `gh`; alternativa MCP). **Owner/repo = fork
(`origin`)**, base = `main` del fork:

```bash
gh pr create \
  --repo "$(git remote get-url origin | sed -E 's#.*github.com[:/]([^/]+/[^/.]+).*#\1#')" \
  --base main \
  --head "$(git branch --show-current)" \
  --title "Add haloscope scan pipeline" \
  --body "$(cat <<'EOF'
## Objective
...
EOF
)"
```

Si `gh` no está instalado, usar MCP `user-github` → `create_pull_request` con
`owner` y `repo` del **fork** (`origin`).

Detalle de `gh` y MCP en [patterns.md](patterns.md#create-pr-on-github).

Tras crear la PR, devolver al usuario:

1. **URL de la PR**.
2. Resumen de pasos (code review, pre-commit, pytest, líneas de diff).
3. Descripción enviada (o enlace).

---

## Reglas críticas

- **Orden fijo:** code review (si aplica) → pre-commit/pytest → contexto →
  descripción → PR.
- **Umbral 100 líneas:** inserciones + eliminaciones del `git diff --numstat`.
- **Espera obligatoria** tras code review con hallazgos.
- **Permisos Git:** push y PR solo con permiso explícito; nunca push a
  `main`/`master`.
- **Inglés** en título y descripción de la PR.
- **Sin secretos** en la descripción ni en commits de la PR.

---

## Integración con otras skills

| Necesidad | Skill / herramienta |
| --- | --- |
| Ramas, commits, push | `git-workflow` |
| Code review (>100 líneas) | `code-review` |
| Pre-commit | `pre-commit-and-lint` |
| Pytest | `pytest-and-coverage` |
| Docs en repos hermanos | `phd-local-docs` |
| Contexto issue GitHub | MCP `user-github` → `issue_read` |
| Redactar issue nueva | `create-github-issue` |
| Crear PR GitHub | `gh pr create` o MCP `create_pull_request` |
| Tarea Notion (opcional) | `notion-phd-tasks` |

---

## Salida esperada

- Diff medido (líneas) y si hubo code review.
- Resultado de pre-commit y pytest (o motivo de omisión).
- Issue GitHub usado (o motivo de omisión).
- URL de la PR creada.
- Descripción redactada en inglés (objective y outcome detallados).

---

## Checklist

- [ ] Rama válida (no `main`/`master`) y base = `main`/`master` del **fork** (`origin`)
- [ ] Tamaño del diff calculado
- [ ] Code review ejecutado y resuelto si diff > 100
- [ ] Pre-commit en verde en ficheros del diff (si aplica)
- [ ] Pytest ejecutado en tests relacionados (si procede)
- [ ] Contexto recopilado (issue, docs locales o hilo)
- [ ] Descripción en **inglés** con objective, changes, outcome
- [ ] Permiso explícito para push y crear PR
- [ ] URL de la PR devuelta al usuario

## Referencias

- [Plantilla y comandos GitHub](patterns.md)
- [Ejemplos PhD](examples.md)
