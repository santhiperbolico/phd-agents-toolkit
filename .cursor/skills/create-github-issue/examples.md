# Ejemplos — crear issue de GitHub

## Ejemplo 1 — GNE Griffin+19 (#37)

**Contexto:** integrar método Griffin+19 en `get_Lagn`, flag instantáneo, salida
HDF5. Spec ampliada en `docs/get_nebular_emission/gne-griffin-lagn-insta/`;
issue publicada en versión simplificada.

**Título:**

```
Griffin+19 AGN bolometric luminosity and instantaneous L_bol flag
```

**Cuerpo (extracto — estructura publicada):**

```markdown
## Summary

Integrate the **Griffin+19** AGN bolometric luminosity method (with the Griffin+2020 super-Eddington correction already in `luminosity_from_mdot`) into `get_Lagn`, and formalize **instantaneous** vs **time-window** bolometric luminosity (`Lagn_insta` vs `Lagn_noinsta`) with clear HDF5 output labels.

Partial implementation already exists in the codebase (`BoolLuminosityFunction.instantaneous_luminosity`, `get_Lagn_insta`, `Lagn_insta` flag in `gne.py`, `griffin` mode in `compute_Lbol_griffin`). This issue tracks unifying those pieces and closing the remaining gaps.

**Related repos (separate PRs, not in scope of this issue):** `prep_gne_input`, `run_setup` — config alignment after merge.

---

## Background / motivation

Shark vs Galform Hα flux cuts show ~3 magnitude differences, partly driven by AGN temporal treatment (Griffin+19 duty cycle, `f_q`, instantaneous bolometric luminosity). GNE must expose a consistent Griffin+19 path and a well-defined instantaneous luminosity flag before downstream science runs.

---

## Target behaviour

### `get_Lagn` flow

1. Check units (`units_h0`, `units_Gyr`, `units_L`).
2. If `L_bol` is present in input data → read catalog value (`Lagn_inputs='Lagn'`).
3. Otherwise compute `L_bol` via:
   - `Hirschmann+14` (`Mdot`, `M_bh`), or
   - `Griffin+19` (`luminosity_from_mdot` on SB + HH components; BOOL weights when applicable).
4. Apply instantaneous treatment when `Lagn_insta=False`: compute instantaneous `Lagn` and retain `Lagn_noinsta`.

### Configuration

| Parameter | Description |
| --- | --- |
| `Lagn_inputs` | `Lagn`, `Hirschmann+14`, or `Griffin+19` |
| `Lagn_insta` | `True`: returned `Lagn` is used by GNE; `False`: also compute and store `Lagn_noinsta` |

### HDF5 output

| Dataset | When | Label |
| --- | --- | --- |
| `agn_data/Lagn` | Always (active AGN) | `L_bol (erg/s)` — value used by GNE for lines and `U` |
| `agn_data/L_agn_noinsta` | Only if `Lagn_insta=False` | `L_bol (erg/s)` integrated over snapshot window |
```

**Issue publicada:** [galform/get_nebular_emission#37](https://github.com/galform/get_nebular_emission/issues/37)

**Nota:** la copia local `issue-description.md` añade Requirements (R1–R7), Known
issues, Edge cases, Phases y Acceptance criteria — **no** van en la issue de
GitHub salvo que el usuario quiera ampliarla.

---

## Ejemplo 2 — Issue mínima sin tablas de salida

**Contexto:** refactor interno sin cambio de contrato HDF5.

```markdown
## Summary

Refactor `compute_weights` to remove duplicated BOOL logic shared with
`BoolLuminosityFunction`. No change to public config or HDF5 datasets.

---

## Background / motivation

Duplicate duty-cycle math diverged in two modules; a single implementation
reduces risk before the Griffin+19 integration issue.

---

## Target behaviour

### `compute_weights` flow

1. Accept the same arguments as today.
2. Delegate BOOL sampling to `BoolLuminosityFunction.compute_sb_weights`.
3. Return identical arrays as the current function for all existing tests.
```

Sin tablas Configuration/Output cuando no hay parámetros nuevos ni artefactos
nuevos.

---

## Ejemplo 3 — Borrador sin publicar

**Flujo agente:**

1. Redactar título y cuerpo en inglés.
2. Mostrar al usuario el markdown completo.
3. Esperar «créala» o «publica en galform/repo».
4. Ejecutar `gh issue create` y devolver URL.

No llamar a `issue_write` ni `gh issue create` en el paso 1.
