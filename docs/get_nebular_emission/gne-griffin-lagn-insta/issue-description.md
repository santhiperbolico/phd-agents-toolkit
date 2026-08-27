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
| `Lagn_params` | Column paths per mode |
| `Lagn_insta` | `True`: returned `Lagn` is used by GNE; `False`: also compute and store `Lagn_noinsta` |
| `Lagn_insta_params` | Generic instantaneous params (`r_bulge`, `v_bulge`, …) or Griffin delegation |
| `redshift_previous` | Previous snapshot redshift (BOOL / duty-cycle window) |
| `tau_fold` | Folding factor for `t_Q` (Griffin) — document chosen value (1 vs 10) in PR |

### HDF5 output

| Dataset | When | Label |
| --- | --- | --- |
| `agn_data/Lagn` | Always (active AGN) | `L_bol (erg/s)` — value used by GNE for lines and `U` |
| `agn_data/L_agn_noinsta` | Only if `Lagn_insta=False` | `L_bol (erg/s)` integrated over snapshot window |

---

## Requirements

- [ ] **R1 — Instantaneous luminosity API:** Single tested entry point for `Lagn_insta` from `Lagn_noinsta`:
  - *Generic (catalog / Hirschmann):* `w = min(f_q · t_dyn / Δt, 1)` per galaxy (vectorized); `Δt` from cosmology between `redshift_previous` and `redshift` (no `age/10` heuristic).
  - *Griffin (SB):* reuse `BoolLuminosityFunction` (`compute_sb_weights` + `instantaneous_luminosity` on SB); HH without sampling.
- [ ] **R2 — Griffin+19 in `get_Lagn`:** Unify `griffin` and `Griffin+19`; `compute_Lbol_griffin` returns `(Lagn, Lagn_noinsta)` when `Lagn_insta=False`.
- [ ] **R3 — Catalog vs compute branch:** `Lagn_inputs='Lagn'` only when `L_bol` is in input data.
- [ ] **R4 — `gne()` wiring:** `Lagn_insta` delegates to unified R1 function; no duplicated logic between `gne.py` and `gne_griffin.py`.
- [ ] **R5 — HDF5 output:** Fix `write_agn_data` bug (`L_agn_noinsta` undefined → `Lagn_noinsta`); consistent labels.
- [ ] **R6 — Tutorial / run scripts:** Update `run_hdf5input_tutorial.py`, `run_gne_shark.py`, and config comments for all three modes and `Lagn_insta`.
- [ ] **R7 — Tests:** Coverage in `tests/test_Lagn.py` (and/or `test_griffin_lagn.py`) for instantaneous weights, Griffin SB/HH, and `L_agn_noinsta` write.

### Review checkpoints (from science task)

- SB and HH computed separately before summing bolometric luminosity.
- Document `f_q` / `tau_fold` value used in PR.
- `Lagn_insta=True/False` and `L_agn_noinsta` output per spec.

---

## Known issues in current code

| Piece | File | Notes |
| --- | --- | --- |
| `get_Lagn_insta` | `gne_Lagn.py` | `Δt` uses provisional `age_of_universe(z)/10`; `t_bulge` not vectorized |
| `write_agn_data` | `gne_io.py` | Bug: `L_agn_noinsta` undefined (should be `Lagn_noinsta`) |
| Mode names | `gne_Lagn.py` | `Griffin+19` branch still falls through to H14; duplicate `griffin` alias |

---

## Edge cases

- No bulge / non-finite `t_dyn` → weight 0 or `Lagn_insta = 0` (define and test).
- Missing `redshift_previous` with `Lagn_insta=False` → explicit `ValueError`.
- Griffin mode without `bh_accretion_rate_sb` / `bh_accretion_rate_hh` → clear read error.
- Bernoulli sampling reproducibility: configurable seed (default 42).

---

## Implementation phases

### Phase 1 — Instantaneous luminosity function
- Refactor `_get_Lagn_insta` / `get_Lagn_insta` (vectorize `t_bulge`, cosmological `Δt`, require `redshift_previous` when `Lagn_insta=False`).
- Add unified `compute_instantaneous_lagn(...)` routing generic vs Griffin.
- Tests R1 green.

### Phase 2 — Griffin+19 in `get_Lagn`
- Unify `griffin` → `Griffin+19` (deprecated alias + warning if needed).
- Complete `compute_Lbol_griffin`; remove dead H14 fallback.
- Tests R2.

### Phase 3 — Full GNE flow and HDF5 output
- Align `get_Lagn` with target diagram; wire `gne()`; fix `write_agn_data`.
- Tests R3, R5, R7.

### Phase 4 — Docs and run scripts
- Update tutorials, Slurm scripts, migration notes (`Mdot_hh` → `Hirschmann+14`, `griffin` → `Griffin+19`).

---

## Acceptance criteria

- [ ] `pytest tests/test_Lagn.py` passes (Griffin tests if present).
- [ ] No regression when `Lagn_insta=True`.
- [ ] `L_agn_noinsta` written correctly when `Lagn_insta=False`.
- [ ] PR opened and assigned for review.
