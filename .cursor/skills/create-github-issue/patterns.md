# Patrones — crear issue de GitHub (PhD)

## Plantilla simplificada (cuerpo)

Adaptar nombres de subsecciones al dominio (`HDF5 output`, `API response`,
`CLI flags`, etc.). **Escribir en inglés.**

```markdown
## Summary

{One or two sentences: what to integrate or change. Name key functions, flags,
or modules. Bold the central concept.}

{Optional second paragraph: partial implementation already in the codebase —
list concrete symbols/files. This issue tracks unifying those pieces and
closing the remaining gaps.}

**Related repos (separate PRs, not in scope of this issue):** `{repo_a}`,
`{repo_b}` — {short reason, e.g. config alignment after merge}.

---

## Background / motivation

{Why this matters: science context, regression, data contract, or blocker for
downstream runs. One short paragraph.}

---

## Target behaviour

### `{main_entry_point}` flow

1. {Step 1 — e.g. validate units or inputs.}
2. {Step 2 — branch on config or data presence.}
3. {Step 3 — compute or read path.}
4. {Step 4 — optional post-processing or alternate output.}

### Configuration

| Parameter | Description |
| --- | --- |
| `{param_a}` | {Allowed values and meaning} |
| `{param_b}` | {Column paths, defaults, or delegation} |

### {Output section title}

Use a title that matches the artefact: `HDF5 output`, `Output files`,
`REST response`, etc.

| {Column A} | {Column B} | {Column C} |
| --- | --- | --- |
| `{path_or_field}` | {When written or returned} | {Units, label, or semantics} |
```

### Qué no incluir por defecto

Mantener la issue legible en GitHub. Reservar para docs locales (`docs/`,
`notes/`, spec SDD):

- Checklists R1–Rn o acceptance criteria largos
- Tabla de bugs conocidos en código actual
- Edge cases exhaustivos
- Fases de implementación (Phase 1–4)
- Plan de tests detallado

Incluir esas secciones en la issue **solo** si el usuario lo pide explícitamente.

---

## Título

| Bueno | Evitar |
| --- | --- |
| `Griffin+19 AGN bolometric luminosity and instantaneous L_bol flag` | `Fix Lagn` |
| `Add batch haloscope scan pipeline for DESI mocks` | `New feature` |
| `Normalize HDF5 units in agn_data writer` | `Bug` |

- Inglés, sustantivos y verbo cuando ayude.
- Mencionar método, flag o módulo central.
- Sin punto final; ≤72 caracteres cuando sea razonable.

---

## Summary — contenido típico

1. **Qué** se hace (integrar, formalizar, exponer, corregir contrato).
2. **Estado actual** — código parcial existente (símbolos entre backticks).
3. **Límite de alcance** — repos o PRs relacionados **fuera** de esta issue.

---

## Target behaviour — tablas

### Configuration

- Una fila por parámetro de config o flag de usuario.
- Columna Description: valores permitidos, semántica True/False, rutas de columnas.

### Output (HDF5, ficheros, API)

- Tres columnas habituales: **identificador**, **cuándo**, **semántica/unidades**.
- Dejar claro qué valor usa el pipeline principal vs salidas auxiliares.

### Flujo numerado

- Orden lógico de ejecución, no orden de implementación.
- Pasos de rama (if catalog present → read; else → compute).
- Post-proceso condicional (p. ej. cuando un flag es False).

---

## Publicar con `gh`

```bash
gh issue create \
  --repo galform/get_nebular_emission \
  --title "Griffin+19 AGN bolometric luminosity and instantaneous L_bol flag" \
  --body "$(cat <<'EOF'
## Summary
...
EOF
)"
```

Sustituir `--repo` por el destino acordado. Para issues en org upstream, el
usuario debe tener permisos de escritura o usar un fork según política del repo.

---

## Publicar con MCP

`user-github` → `issue_write`:

- `method`: `create`
- `owner`, `repo`, `title`, `body`
- `labels`, `assignees` solo si el usuario los indica

Para **actualizar** una issue existente: `method: update`, `issue_number`, campos
a cambiar. Mostrar diff conceptual al usuario antes de actualizar.

---

## Relación con PRs

- Issue en **upstream** (`galform/repo`): la PR del fork referencia
  `galform/repo#N` en la descripción.
- `Closes #N` en la PR solo si `#N` existe en el **mismo repo** que la PR
  (véase `create-pull-request`).

---

## Borrador local (opcional)

Ruta habitual en repos de producto:

```
docs/{feature}/issue-description.md   # spec ampliada
```

La issue en GitHub usa la versión **recortada**; el markdown local puede
incluir Requirements, Known issues, Phases y Acceptance criteria para trabajo
con el agente.
