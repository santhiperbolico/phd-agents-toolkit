# PLAN: Secondary-property sampling of FastPM halos — Phases 1–2

**Status (2026-11-06):** Phase 1 was run (job 210, Galform LRG1 sSFR bin). Results and
required fixes are in §9; the Phase 2 sampler specification is in §10; the new tasks
(T9–T17) are in §11. Sections 1–8 describe the original Phase 1 plan and remain valid
unless §9 corrects them.

Implementation plan intended for a Cursor agent working in `fnl_matching_error_reduction`.
Phase 1 is a **diagnostic**: it decides whether secondary halo properties already
available in the FastPM FoF catalogue can lower the clustering amplitude of a halo
sample below what mass alone can reach. It does **not** build the final sampler
(Phase 2, §10).

---

## 1. Context

### 1.1 Goal

Build FastPM halo samples that match, for each SAM tracer/bin, both:

1. the abundance `N_SAM`, and
2. the power spectrum `P_gg(k)` of the SAM galaxies (Shark / Galform; LRG, ELG, QSO),

so that the halo proxy can be used in the `b_φ` / error-reduction pipeline.

### 1.2 Current method and why it fails

Current pipeline (`lower_mass_cut_matching`, `lower_mass_cut_property_pgg`):
select `{h : M_h > M_cut}` with `M_cut` optimised on `pk_chi2` or `fit_b1`, then
optionally augment with shifted duplicates to reach `N_SAM`.

Evidence (e.g. Galform LRG1 sSFR bin, z = 0.5232):

- `P_FastPM / P_gg ≈ 2.1–2.3`, roughly constant in `k` (so `b_FastPM / b_SAM ≈ 1.5`).
- The optimiser returns `M_cut ≈ 1.51e11 Msun/h`, `N = 27 736 561`, the same value
  for many different property bins. The FoF catalogue has 30 655 271 halos with minimum
  mass ≈ 1.48e11 (resolution floor, ~15 particles), so the optimiser sits at the floor,
  keeping ~90 % of the catalogue (confirmed in Phase 1, §9).
- Consequence: with a pure `M > M_cut` rule the lowest reachable bias is essentially the
  bias of the full catalogue. The optimiser saturates there. The target needs a lower
  bias.
- Synthetic augmentation changes `N`, not `b_eff`, so it cannot help.

### 1.3 Constraints

- Only the SAM `P_gg(k)` is available. **No SAM galaxy catalogues** (no host-mass
  histograms, no centrals/satellites split).
- Already explored by the user: lower bound of bias from mass only (aligned), and a
  mass window `[M_lo, M_hi]` at fixed `N` (did not work).
- FastPM FoF columns available: `InitialPosition`, `Length`, `MinID`, `Position`,
  `Rdisp`, `RVdisp`, `Task`, `Vdisp`, `Velocity`.
- Final scientific target is `b_φ`; any selection must be checked against fixed-IC
  variance reduction `R(k)` before being adopted (Phase 3).

---

## 2. Alternatives considered

| Alternative | Status | Reason |
|-------------|--------|--------|
| Synthetic halo augmentation (shifted duplicates) | **Discarded** as a bias fix | Changes number density only; `P(k)` amplitude unchanged. Kept only as a final abundance-matching step. |
| Lower mass cut (`M > M_cut`), `pk_chi2` / `fit_b1` | **Insufficient** | Bias floor = full catalogue; optimiser saturates and is degenerate across bins. |
| Mass window `[M_lo, M_hi]` at fixed `N` | **Discarded** | Explored by the user; did not reach the target. |
| `p(M)` from SAM host-mass histograms (variant A) | **Blocked** | Needs host mass of SAM centrals per bin; not available. Revisit if histograms are obtained from the `P_gg` producers. |
| Parametric `p(M)` fitted to `P_gg` (variant B) | **Deferred / likely not useful alone** | With `0 ≤ p ≤ 1` and `b(M)` increasing, the lowest bias at fixed `N` is the window of lightest halos, already tested. Only revisit if the window failure was shape-related, not amplitude. Also weakly constrained by `P_gg` alone (many equivalent `p(M)`). |
| Continuous weights `w(M, env)` | **Deferred** | Optimisation tool for Phase 2 (fit in expectation), not a new selection axis. |
| Mixing halos with random DM particles | **Discarded** (fallback only) | Can lower amplitude but breaks the interpretation of `b_φ`. |
| **Secondary property as extra selection axis** | **Selected** | Assembly bias lets samples reach a bias below the mass-only floor. Phase 1 uses FoF columns already in the catalogue. |

---

## 3. Phase roadmap

| Phase | Content | Gate |
|-------|---------|------|
| **1 (done, fixes pending)** | Bias scan `b(M, q)` using FoF-only properties; extreme-sample test | Can any property reach `P/P_gg ≤ 1` at `N = N_SAM`? **Yes: `vdisp_trace` (low-q), see §9** |
| 1b (conditional) | Same scan with environment properties (`δ_R`, tidal anisotropy, neighbour density) from `density_field_properties` | Only if Phase 1 gate fails |
| 2 (next, §10) | Sampler `p = min(1, c·exp(−λ q))` on `q` = within-mass-bin percentile of `vdisp_trace`; fit in expectation using per-cell cross spectra | Matches `b₁` and `P(k)` shape per bin |
| 3 | Validation: fixed-IC `R(k)`, ensemble application without refit, `b_φ` sanity check | `N` constant across ICs; `R(k)` not degraded |

---

## 4. Phase 1 specification

### 4.1 Objective

For a given tracer/bin and one reference IC, answer:

1. Does any FoF-derived property `x` shift the clustering amplitude at fixed mass
   (within-mass-bin percentile `q`) enough to go below the mass-only floor?
2. In which direction (low or high `q`) and in which mass range?

### 4.2 Properties to scan (all at fixed mass)

`Rdisp` and `Vdisp` are stored as **6-element symmetric tensors** per halo, not scalars.
Never take the log of individual components: off-diagonal terms can be negative and
single components depend on the box axes. Build **rotation-invariant scalars** instead.
After the checks in 4.4b, assemble the 3×3 symmetric matrices `R` (from `Rdisp`) and
`V` (from `Vdisp`) and compute, per halo:

| Name | Definition | Phase 1 |
|------|------------|---------|
| `rdisp_trace` | `log10(tr R)` (total size) | yes |
| `vdisp_trace` | `log10(tr V)` (total internal kinetic energy) | yes |
| `virial_ratio` | `log10(tr V · sqrt(tr R / 3) / M)` (virialisation proxy) | yes |
| `displacement` | `|Position − InitialPosition|`, periodic minimum-image convention | yes |
| `shape_r` | `sqrt(λ_min / λ_max)` of the eigenvalues of `R` (sphericity) | only `Length ≥ length_shape_min` (default 50) |
| `anisotropy_v` | same with `V` | only `Length ≥ length_shape_min` |

The `virial_ratio` formula assumes `R` and `V` are covariance-like second moments
(so `tr V` is already a squared velocity). If the T1 check shows they are already
square-rooted dispersions, adapt the formula and document it. Eigenvalue-based shape
properties are restricted to high `Length` because the sample covariance of
~15-particle halos produces spurious anisotropy.

`RVdisp` is **not used** in Phase 1 (it is a position–velocity correlation and, if it
has 6 elements, it is not symmetric in general).

Do **not** assume the sign of the correlation with bias; the scan reveals it.
Mass proxy: `M = Length × m_particle` (use the existing helper if there is one).

### 4.3 Metric (no matter field required)

For each cell `(mass bin i, quantile bin j)`:

- compute `P_cell(k)` with the existing `get_pk_halos` (same `n_grid`, `boxsize`);
- apply the **same shot-noise convention as the reference `P_gg`** (check how `P_gg`
  and `get_pk_halos` treat `1/N`; document the choice);
- report `r_cell = mean_k[P_cell(k) / P_gg(k)]` over `k ∈ [fit_k_min, fit_k_max]`
  (default `0.003–0.08 h/Mpc`) and a large-scale version `k < 0.05`;
- report `b_rel = sqrt(P_cell / P_ref)` at large scales, with `P_ref` = full catalogue.

Because all cells share the same IC, cosmic variance largely cancels in ratios.

### 4.4 Extreme-sample test (the gate)

For each property and each direction (`low q` / `high q`):

1. Compute `f = N_SAM / N_catalogue`.
2. In **every** mass bin, keep the fraction `f` of halos with the lowest (or highest)
   `q`, by rank. Total is `N_SAM` by construction.
3. Compute `P_extreme(k) / P_gg(k)` as in 4.3.

Decision rule (configurable thresholds):

- `r_extreme ≤ 1 + tol` (default `tol = 0.1`) → property is **viable**: go to Phase 2.
- `r_extreme > 1 + tol` for all properties → go to Phase 1b (environment).

Also repeat the test restricted to `Length` ranges (e.g. `Length < 50` vs `≥ 50`),
because FoF-internal properties are noisy for ~15-particle halos and the effect must
appear where the sample is dominated (low masses).

### 4.4b Sanity checks

- `q` must be (approximately) independent of mass: check the correlation of `q` with
  `log M` and the uniformity of `q` within each mass bin.
- Verify the semantics of `Rdisp`, `Vdisp`, `RVdisp` in the FastPM source/docs before
  interpreting. Do not assume. Establish and document:
  1. the **order of the 6 components** (e.g. `xx, xy, xz, yy, yz, zz` or another);
  2. whether they are covariances (centred second moments) or square-rooted values;
  3. units (comoving vs physical; velocity units).
- Positive semi-definiteness test: after assembling the 3×3 matrices, the eigenvalues
  must be ≥ 0 (up to numerical tolerance) for essentially all halos. A significant
  fraction of negative eigenvalues indicates a wrong component order. Log the fraction
  and fail loudly above a configurable threshold.
- Consistency of scale: `tr V` should scale roughly as `M^(2/3)`; check it on the
  catalogue before using `virial_ratio`.

---

## 5. Tasks for the agent

Follow the repository conventions of `fnl_matching_error_reduction`: inspect the
existing modules first and reuse helpers. Suggested names below are proposals.

**T1 — Catalogue inspection and loader.**
Reuse the existing FoF loader (see `src/fnl_matching/matching/selection.py` and the
callers of `get_pk_halos`). Expose `Length`, `Position`, `InitialPosition`, `Rdisp`,
`Vdisp`, `RVdisp`. Log catalogue size, minimum `Length`, and whether
`M_cut ≈ 1.51e11` corresponds to the full catalogue. Document column semantics
(component order, covariance vs square root, units) and run the checks in 4.4b.

**T2 — Property builders.**
New module `src/fnl_matching/matching/secondary_properties.py` with small pure
functions: `assemble_symmetric_tensors(components)` (N×6 → N×3×3, with the component
order as a documented constant), `compute_trace`, `compute_shape_ratio` (eigenvalues
via `np.linalg.eigvalsh`), `compute_virial_ratio`, `compute_periodic_displacement`,
`percentile_within_mass_bins(values, log_mass, mass_edges)`.

**T3 — Cell and extreme-sample selection.**
Same module or `matching/selection.py`: functions returning boolean masks for
`(mass bin, quantile bin)` cells and for the extreme sample with fraction `f` per
mass bin (rank-based, deterministic, no random seed needed).

**T4 — Scan pipeline.**
New `src/fnl_matching/pipelines/secondary_property_bias_scan.py`: loads one IC,
loads the target `P_gg` (reuse the manifest/path logic of
`lower_mass_cut_property_pgg`), computes the cell metrics and the extreme-sample test,
writes outputs. Compute `P(k)` per cell only once per property.

**T5 — Config, CLI, Slurm.**
Add a `secondary_property_bias_scan` block to the pipeline config (new JSON under
`configs/`), a CLI in `scripts/pipelines/`, and a Slurm template mirroring the
existing ones. Config keys: `fastpm_path`, `fastpm_i_sim`, `manifest_csv`, `n_grid`,
`mass_bins` (number or edges), `n_quantiles`, `properties`, `fit_k_min`, `fit_k_max`,
`large_scale_k_max`, `tolerance`, `length_splits`, `output_dir`.

**T6 — Outputs and figures.**
Under `output/secondary_property_bias_scan/<object>/<SAM>/<property_slug>/`:

- `scan_cells.csv`: one row per cell with `N`, `r_cell`, `b_rel`.
- `scan_extreme.json`: extreme-sample results per property and direction, plus the
  gate decision.
- Figures: `b_rel` vs mass for each quantile bin; `P_extreme / P_gg` vs `k`;
  `q`-vs-mass independence check.

**T7 — Tests.**
`src/tests/matching/test_secondary_properties.py` and
`src/tests/pipelines/test_secondary_property_bias_scan.py`: pytest functions only,
parametrised, with small synthetic catalogues (periodic wrap in displacement, `q`
uniformity within bins, extreme-sample size equals `N_SAM`, rank determinism, tensor
assembly from the 6 components, trace and eigenvalues invariant under a random
rotation, positive semi-definiteness check flags a wrong component order).

**T8 — Run and report.**
Run on the Galform LRG1 sSFR case from the figure and on one ELG case from
`configs/manifests/pgg_mstar_oii_selected.csv`. Summarise the gate decision in a short
note (`docs/conclusions/`), no scientific claims beyond the numbers produced.

---

## 6. Coding and workflow rules

- Python identifiers, NumPy-style docstrings, comments, logs and exceptions in English.
- No `from __future__ import annotations`; no imports inside functions.
- pytest functions (no test classes), `parametrize` where useful.
- KISS, DRY, YAGNI; small single-purpose functions; reuse existing helpers.
- pre-commit: black, isort, flake8; no `# noqa: E501` in docstrings.
- Commits and PRs in English; do not push unless explicitly asked.
- Local run: activate the venv, `export PYTHONPATH=src`, then `pytest <path> -v`.

---

## 7. Risks and caveats

- FoF-internal properties of ~15-particle halos are noisy; effects may vanish exactly
  where the sample is dominated. Hence the `Length` split in 4.4.
- Selecting on halo properties changes the response to primordial non-Gaussianity:
  a matching `P(k)` does not guarantee a matching `b_φ` (check in Phase 3).
- Property thresholds must be rank/quantile based within each IC so that `N` stays
  constant across the ensemble (needed for `R(k)`).
- `P_gg` alone constrains mostly the large-scale amplitude; do not interpret fitted
  parameters as galaxy–halo physics.

## 8. Open questions (to resolve before or during T1)

1. Is the particle snapshot (or the ICs) stored for the reference realisation? That
   decides how Phase 1b computes `δ_R` and tidal anisotropy.
2. Does the stored `P_gg` include shot noise, and does `get_pk_halos` subtract it?
3. In which direction did the mass-window attempt fail (FastPM above or below the SAM,
   amplitude or shape)? It decides whether Phase 2 can reuse any `p(M)` variant.
4. What is the exact layout of the 6-component `Rdisp` / `Vdisp` / `RVdisp` fields
   (component order, covariance vs square root, units)? Resolve in T1 from the FastPM
   source before building any property.

---

## 9. Phase 1 results (job 210, Galform LRG1 sSFR bin `ssfr_m0p27832_m0p18112`)

Setup: `N_SAM = 10 683 288`, catalogue `N = 30 655 271` (`Length < 50`: 23 995 952;
`Length ≥ 50`: 6 659 319), tolerance 0.1, 8 mass bins × 4 quantile bins.

### 9.1 Extreme-sample test (`all` split)

`r_extreme = mean_k[P_extreme / P_gg]` for the `N_SAM` halos with lowest / highest `q`
in every mass bin (keep fraction 0.348).

| Property | `r_low` | `r_high` | Gate | Status |
|----------|---------|----------|------|--------|
| `vdisp_trace` | **0.82** | 5.74 | **pass** | valid; only property with a real signal |
| `rdisp_trace` | 1.74 | 2.79 | fail | valid; weak effect |
| `virial_ratio` | 2.53 | 2.60 | fail | **suspect (see 9.3)** |
| `shape_r` | 2.48 | 2.63 | fail | **suspect (see 9.3)** |
| `anisotropy_v` | 2.57 | 2.61 | fail | **suspect (see 9.3)** |
| `displacement` | 25.7 | 37.1 | fail | **bug suspected (see 9.3)** |

`length_lt_50` split: `vdisp_trace` low-q gives `r = 0.64` (gate passes); the
`rdisp_trace` low-q gives 1.54 (fails).

### 9.2 `vdisp_trace` in detail

- At fixed mass the dependence on `q` is large for low-mass halos: in the lowest mass
  bin (1.5–4.5e11) `b_rel` goes from 0.51 (lowest quartile) to 1.91 (highest), a factor
  ≈ 3.7. The `b_rel(q3)/b_rel(q0)` ratio per mass bin is
  `[3.72, 2.69, 1.89, 1.59, 1.31, 1.28, 1.24, 1.13]`: the effect fades above ~1e13.
- The ratio `P_extreme_low / P_gg` is ≈ 1 for `0.1 ≲ k ≲ 0.6 h/Mpc` and somewhat below
  1 (~0.6–0.9) at the lowest `k`. The rise at `k > 0.8` is beyond the Nyquist of
  `n_grid = 256` (≈ 0.80 h/Mpc) and must not be interpreted.
- Interpretation caveat: at fixed `Length`, `tr(V)` is likely an **environment proxy**
  (halos next to massive structures have inflated dispersions; isolated relaxed halos
  have low ones), not an internal halo property. This is a hypothesis to test (T13).
  It matters for `b_φ`: selection on environment changes the response to fNL.
- The target is reachable and bracketed: random subsampling gives `r ≈ 2.2`, the
  extreme low-q sample gives `r ≈ 0.64–0.82`, so an intermediate selection strength
  gives `r = 1`.

### 9.3 Suspected implementation problems (must be fixed before trusting those properties)

1. **`virial_ratio`, `shape_r`, `anisotropy_v` are identical in `length_lt_50`**: same
   `q_mass_correlation` (−0.1292) and same `r_extreme` (9.72 / 9.48); in `all` they also
   coincide cell by cell in the first mass bin. Different properties cannot give
   identical numbers. Hypothesis: for `Length < 50` they are NaN (the plan restricts
   shape properties to `Length ≥ length_shape_min`) and the percentile falls back to the
   catalogue order, which selects spatially coherent chunks of the box (hence `r` from
   10 to 430, erratic). Open point: `virial_ratio` was **not** supposed to be restricted;
   find out why it is degenerate too.
2. **`displacement` gives `r` between 5.9 and 58 in every mass bin**, almost independent
   of mass and U-shaped in `q`. No halo property should do that. Hypothesis:
   `InitialPosition` and `Position` do not share units/convention (e.g. grid units,
   different wrap), so the "displacement" depends on position and the extreme sample is a
   spatial region of the box. A sane displacement histogram is a few Mpc/h with a tail up
   to ~20–30 Mpc/h.
3. **`length_ge_50` is incomplete by construction**: with 6.66 M halos an extreme sample of
   10.68 M cannot be built, so no `scan_extreme.json` is produced. It must be reported
   explicitly as `not_applicable` instead of silently missing. In that split
   `rdisp_trace` gives `b_rel` from 0.84 to 1.24 at low mass (modest).

Decision: Phase 2 proceeds with `vdisp_trace`. The other properties are neither adopted
nor discarded until the checks in T9–T11 are done.

---

## 10. Phase 2 specification: sampler on `vdisp_trace`

### 10.1 Objective

Build a FastPM halo sample with exactly `N_SAM` halos whose `P(k)` matches the target
`P_gg` in amplitude (`b₁` at large scales) and shape over `[fit_k_min, fit_k_max]`, using
the within-mass-bin percentile `q` of `vdisp_trace` as selection axis. One free parameter
(optionally two), no knowledge of the SAM catalogues.

### 10.2 Selection rule

- Mass bins: fixed log-spaced edges from the config (same in every IC). Merge bins with
  fewer than `min_halos_per_bin` halos (default 1000) with their neighbour.
- `q ∈ [0, 1]`: percentile of `vdisp_trace` within each mass bin of the current IC
  (rank-based). Ties are broken with a **global, order-independent random key**:
  `key_h = hash(MinID_h, tie_break_seed)` (`MinID` is unique per FoF group), with a
  single `tie_break_seed` in the config, shared by all ICs and independent of the draw
  seeds. Never break ties by catalogue order (spatially correlated) and never use a
  per-IC seed for `q`: the same halo must get the same `q` regardless of file ordering or
  MPI task layout. Log the fraction of tied values per property; if it is negligible the
  tie-break is only defensive. Draw seeds are a separate function of
  `(random_seed, ic_id, draw_id)`.
- Selection probability per halo:

  `p(M, q) = min(1, c · exp(−λ q))`, with `c` solved numerically (root finding) so that
  `Σ_h p_h = N_SAM`.

- `λ = 0` is a random subsample (reference level, `r ≈ 2.2`); `λ → ∞` tends to the
  extreme low-q sample of Phase 1 (`r ≈ 0.64–0.82`).
- Optional second parameter `γ` for a mass tilt `p ∝ (M/M_ref)^(−γ)`, enabled only if the
  one-parameter fit leaves a clear shape residual. Keep `γ` off by default (YAGNI).
- Realisation: `n_draws` independent draws with fixed seeds. Per mass bin and `q` bin,
  draw exactly `round(Σ p)` halos without replacement so that `N` is constant across
  draws and ICs (needed for `R(k)`).

### 10.3 Fit in expectation (no FFT inside the optimiser)

1. Define cells `(mass bin j, quantile bin l)`, with finer `q` resolution than Phase 1
   (default 10 quantile bins).
2. Once per IC, compute the halo count field `n_c(x)` of each cell (same grid and mass
   assignment as `get_pk_halos`) and the cross spectra `P_{cc'}(k)`.
3. Expected spectrum of a Bernoulli sample with per-cell probabilities `p_c`.
   Notation: `ñ_c(k)` = FFT of the MAS-assigned count field of cell `c`, window
   treatment exactly as in `get_pk_halos`; `𝒞_{cc'}(k)` = shell average of
   `Re[ñ_c(k) ñ_{c'}*(k)]` (same binning as `get_pk_halos`); `𝒩` = the normalisation
   factor that `get_pk_halos` applies (read it from the code; do not re-derive it);
   `N_s = Σ_c p_c N_c`; `S_c(k)` = self-pair term of cell `c`, i.e. `Σ_{h∈c} |W_h(k)|²`,
   equal to `N_c` under the code's flat shot-noise convention (use the code's convention).

   For `b_h ~ Bernoulli(p_h)`:
   `⟨|n_s(k)|²⟩ = |Σ_c p_c ñ_c(k)|² + Σ_c p_c (1 − p_c) S_c(k)`.

   Hence, shot noise subtracted (code convention if it subtracts `1/N`):

   `P_exp(k) = 𝒩 / N_s² · [ Σ_{c,c'} p_c p_{c'} 𝒞_{cc'}(k) − Σ_c p_c² S_c(k) ]`

   and, if the code does **not** subtract shot noise, add `𝒩 / N_s`. The diagonal term
   `−Σ_c p_c² S_c` removes the self-pairs that the cross spectra contain with weight `p²`
   instead of `p`; omitting it biases `P_exp` high by a shot-noise-sized amount (order
   10 % at `k ≈ 0.2` for `N ~ 10⁷`). The convention must match the one used for `P_gg`
   (see open question 2 in §8).
   **Arbiter for all factors:** a test on a toy catalogue that averages `get_pk_halos`
   over many Bernoulli draws and compares with `P_exp` (see T17).
4. Optimise `λ` (and `γ` if enabled) with `scipy.optimize` on the reduced χ² against
   `P_gg` in `[fit_k_min, fit_k_max]` (default 0.003–0.08 h/Mpc), using the `P_gg`
   uncertainties. Report also the large-scale amplitude ratio (`k < 0.05`).
5. Validate with real draws (10.2) and compare `P_draw(k)` with `P_exp(k)`.

### 10.4 Acceptance criteria (configurable)

- `|mean_k(P_sample / P_gg) − 1| ≤ 0.05` over the fit range.
- RMS of `P_sample / P_gg − 1` over the fit range `≤ 0.10`.
- `N_selected = N_SAM` exactly in every draw.
- Spatial uniformity guard: counts of selected / catalogue halos in coarse spatial cells
  are consistent with a constant fraction (chi² test), to catch coherent-region selections.
- Outputs per bin: JSON with `lambda`, `c`, chi², ratios, draws summary; figures with
  `P/P_gg` in **log-k** restricted to the fit range plus an extended panel up to the
  Nyquist (marked), and `p(q)` curves per mass bin.

### 10.5 Robustness and scope

- Repeat on at least two more sSFR/SFR bins of Galform LRG1, and on one ELG case.
- Calibrate `λ` on the reference IC and apply it, unchanged, to the other ICs with `q`
  recomputed inside each IC (no refit).
- Out of scope in Phase 2: `b_φ` evaluation and `R(k)` (Phase 3), environment properties
  (Phase 1b), satellite modelling.

---

## 11. New tasks (T9–T17)

**T9 — Fix degenerate properties (`virial_ratio`, `shape_r`, `anisotropy_v`).**
Log the NaN/non-finite fraction of every property per split. Fail loudly if `q` contains
NaN instead of ranking them. Make the `Length ≥ length_shape_min` restriction explicit
(shape properties are only evaluated in that range and skipped otherwise, with a
`not_applicable` entry). Find out why `virial_ratio` was affected. Add a test that two
different properties never return identical `q` arrays on a synthetic catalogue.

**T10 — Debug `displacement`.**
Check units and coordinate convention of `Position` and `InitialPosition` in the FastPM
source and on the data. Apply the periodic minimum-image convention. Save a histogram of
the displacement (expected: a few Mpc/h with a tail up to ~20–30 Mpc/h). Add a unit test
with synthetic periodic positions.

**T11 — Spatial-uniformity guard and `not_applicable` handling.**
For every extreme or Phase 2 sample, compare the selected fraction in coarse spatial
cells (e.g. 8³) with the global fraction and flag samples that are spatially coherent.
Report splits where `N_split < N_SAM` as `not_applicable` in `scan_extreme.json`.

**T12 — Plot fixes.**
`P/P_gg` plots in log-k, restricted to the fit range plus an extended panel; draw the
Nyquist `k` of `n_grid` as a vertical line and do not plot beyond it.

**T13 — Environment diagnostic for `vdisp_trace`.**
Using only halo positions (no snapshot needed), build a smoothed density field of all
halos at `R = 3, 5, 10 Mpc/h`, interpolate it at each halo, and report within-mass-bin
correlations between `q(vdisp_trace)` and the local density. High correlation supports
the "environment proxy" interpretation. Output a short table and one figure.

**T14 — Cell fields and cross spectra.**
New module (proposal) `src/fnl_matching/matching/cell_spectra.py`: functions to build the
count field of each `(mass bin, quantile bin)` cell and the cross-spectrum matrix
`P_{cc'}(k)`, reusing the grid/mass-assignment code of `get_pk_halos`. Cache the matrix
on disk (NPZ) per IC and config hash.

**T15 — Expected spectrum and fit.**
Functions (proposal, in `src/fnl_matching/matching/property_sampling.py`):
`probabilities_from_lambda(q, mass_bin, lam, n_target)` (solves `c`),
`expected_pk(p_cells, cross_spectra, ...)` (implements the §10.3 equation; reuse the
normalisation/MAS/FFT code path of `get_pk_halos` for `ñ_c` and `𝒩` instead of
re-implementing them), `fit_lambda(...)`. Pure functions, no I/O.

**T16 — Sampler and pipeline.**
`draw_sample(...)` with exact-N draws per cell and fixed seeds; new pipeline
`src/fnl_matching/pipelines/property_sampling_pgg.py`, CLI in `scripts/pipelines/`, config
block `property_sampling` (keys: `property`, `mass_bin_edges`, `n_quantiles`,
`min_halos_per_bin`, `fit_k_min`, `fit_k_max`, `n_draws`, `random_seed`, `tolerances`,
`manifest_csv`, `output_dir`) and Slurm template. Reuse the manifest/`P_gg` loading of
`lower_mass_cut_property_pgg`.

**T17 — Tests and report.**
pytest functions, parametrised: `c` solves `Σp = N_SAM` for several `λ`; `λ = 0` gives a
uniform probability; large `λ` tends to the rank-based extreme sample; exact `N` in every
draw; expected spectrum equals the mean of `get_pk_halos` over ≥ 200 Bernoulli draws on a toy
catalogue within the standard error (this test settles volume / `n̄` / shot-noise
factors, including the `−Σ p_c² S_c` term and both shot-noise conventions); `q` is
invariant to a random permutation of the catalogue order; tie-break keys depend only on
`MinID` and the seed;
spatial-uniformity guard flags a spatial slab. Then run on the Galform LRG1 sSFR bin and
write a short note in `docs/conclusions/`.

### 11.1 Order of work

T9–T12 (fixes) in parallel with T13 → T14 → T15 → T16 → T17. Phase 2 uses only
`vdisp_trace`, so the property-specific fixes (T9 for `virial_ratio`/`shape_r`/
`anisotropy_v`, T10) do not block it. Dependencies that **do** apply to Phase 2:
- first step of T9, for `vdisp_trace` only: log NaN/non-finite and tie fractions before
  building anything on it;
- T11 (spatial-uniformity guard) must exist before the T16 acceptance criteria are used;
- T12 (plots) before any figure is shared.
Until T9/T10 are done, results for the other properties are **quarantined**: they must
not be quoted in conclusions or docs, except as "inconclusive, under review".

### 11.2 Additional risks

- Selecting on `vdisp_trace` may change the response to primordial non-Gaussianity:
  matching `P(k)` does not guarantee matching `b_φ` (Phase 3).
- If `q` is mostly an environment proxy, a property computed on the same IC modes may
  interact with the fixed-IC variance reduction: check `R(k)` in Phase 3.
- Noise in `Vdisp` for ~15-particle halos: the fitted `λ` is specific to this
  catalogue resolution and mass floor.