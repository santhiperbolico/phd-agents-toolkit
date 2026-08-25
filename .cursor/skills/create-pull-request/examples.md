# Ejemplos — crear pull request (PhD)

## Ejemplo 1 — PR con code review e issue GitHub

**Contexto:** rama `feature/42-haloscope-scan` en `gne-haloscope`, diff 215 líneas,
issue GitHub #42 «Add batch haloscope scan pipeline».

**Paso 1:** code review → 0 críticos, 1 importante (falta test de borde).
Usuario: «añade el test y continúa».

**Paso 2:** pre-commit en ficheros del diff → pass. Pytest:

```bash
pytest tests/pipeline/test_haloscope_scan.py --no-cov
```

**Paso 3:** `issue_read` #42 → título y criterios de aceptación.

**Paso 4 — descripción (inglés):**

```markdown
## Objective

Implement a batch haloscope scan pipeline for GNE data products, as described
in GitHub issue #42. The pipeline must read preprocessed spectra, run the
haloscope detection pass, and write summary tables for downstream analysis.

## Changes

- New `HaloscopeScanRunner` in `src/pipeline/haloscope_scan.py`
- CLI entry point `scripts/run_haloscope_scan.py`
- Unit tests for runner edge cases (empty input, single-bin spectrum)

## Outcome

Running `python scripts/run_haloscope_scan.py --config configs/scan.yaml`
produces per-run CSV summaries under `output/haloscope/` ready for the
comparison notebook. Empty input directories fail fast with a clear error.

## References

- **GitHub issue:** [#42](https://github.com/org/gne-haloscope/issues/42)

## Test plan

- [ ] `pytest tests/pipeline/test_haloscope_scan.py`
- [ ] Manual run on sample data in `data/fixtures/spectra_small/`

Closes #42
```

**Título:** `[#42] Add batch haloscope scan pipeline`

---

## Ejemplo 2 — PR pequeña sin issue ni code review

**Contexto:** diff 38 líneas, fix de timeout en consulta Gaia, sin issue.

- Paso 1: omitido (38 ≤ 100).
- Paso 2: pre-commit en el `.py` tocado; pytest del módulo relacionado.
- Paso 3: contexto solo del hilo del agente.
- Paso 4: descripción en inglés sin sección References de issue.

**Título:** `Fix timeout when querying large Gaia catalogs`

---

## Ejemplo 3 — PR de documentación

**Contexto:** rama `docs/research-plan`, solo Markdown en `docs/`, diff 95 líneas.

- Paso 1: omitido (95 ≤ 100).
- Paso 2: pre-commit si hay hooks de Markdown; **omitir pytest** (sin `.py`).
- Paso 3: leer `docs/research-plan.md` y hilo.
- Paso 4: objective = qué sección se actualiza y por qué; outcome = qué lee
  el revisor tras el merge.

**Título:** `Update methodology section in research plan`

---

## Ejemplo 4 — Usuario pide continuar tras hallazgo crítico

Tras code review con hallazgo crítico (credencial en diff):

1. Reportar como **Crítico** y recomendar no abrir PR.
2. Esperar respuesta.
3. Si el usuario dice «continúa igualmente», documentar en la descripción que
   el hallazgo queda pendiente **solo** si lo acepta explícitamente; por
   defecto, **no** crear la PR con secretos en el diff.
