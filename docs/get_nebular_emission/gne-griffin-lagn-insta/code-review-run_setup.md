# Code review: `run_setup`

**Fecha:** 2026-08-25  
**Alcance:** cambios sin commitear en `run_setup/taurus/` (rama `main`)  
**Contexto:** [spec.md](./spec.md) — integración Griffin+19 / `Lagn_insta` en `get_nebular_emission`  
**Revisor:** agente (skill `code-review`)

---

## Resumen

Los scripts actualizan la firma de `gne()` (cosmología, `boxside`, `effvol`, `redshift_previous`) y configuran Griffin+19 para Shark, pero contienen **errores bloqueantes** (`tau_field` vs `tau_fold`) y **configuración invertida de `Lagn_insta`** respecto a la spec y a `gne.py`. Además hay desalineación de rutas Galform, un dataset incorrecto en `extra_params`, y un fichero duplicado sin actualizar.

---

## Hallazgos

### Crítico

1. **Kwarg incorrecto: `tau_field` en lugar de `tau_fold`**  
   - **Evidencia:** `run_gne_shark.py:325` y `run_gne_galform.py:319` pasan `tau_field=...`; `gne()` en `get_nebular_emission/src/gne/gne.py` solo acepta `tau_fold`.  
   - **Impacto:** `TypeError` en la primera llamada a `gne()`; ningún job de líneas de emisión producirá salida.  
   - **Acción:** renombrar variable y argumento a `tau_fold` en ambos scripts.

2. **`Lagn_insta` invertido respecto a la spec y a `gne.py`**  
   - **Evidencia:** en `gne.py`, `calculate_Lagn_insta = not Lagn_insta`. La [spec](./spec.md) define:
     - `Lagn_insta=True` → luminosidad de ventana/catálogo (sin BOOL).
     - `Lagn_insta=False` → luminosidad instantánea + `L_agn_noinsta` en HDF5.
   - Los comentarios en `run_gne_*.py` dicen lo contrario («instantaneous if True»).
   - **Shark** (`run_gne_shark.py:156`): `Lagn_insta = True` con `Griffin+19` → **no** aplica pesos BOOL (`weights=None` en `get_Lagn`); contradice el objetivo científico de la campaña.
   - **Galform** (`run_gne_galform.py:152`): `Lagn_insta = False` con `Lagn_inputs='Lagn'` → tras leer `L_bol` del catálogo, `gne()` llama a `get_Lagn_insta` con `Lagn_insta_params=None` → `ValueError: r_bulge must be provided` en galaxias AGN.
   - **Acción:**
     - Shark: `Lagn_insta = False`, `tau_fold = 1.0`, mantener `Lagn_insta_params`.
     - Galform (modo catálogo): `Lagn_insta = True`, `Lagn_insta_params=None`.

3. **Orden de `Lagn_params` en comentarios vs código Shark**  
   - **Evidencia:** comentarios en `run_gne_shark.py` documentan `[Mbh, Mdot_hh, Mdot_stb]`; la spec tabla dice `[m_bh, bh_accretion_rate_sb, bh_accretion_rate_hh]`. El código usa `[m_bh, bh_accretion_rate_hh, bh_accretion_rate_sb]`, coherente con `gne_Lagn.py:676-678` (`mdot_hh = vals[1]`, `mdot_sb = vals[2]`).  
   - **Impacto:** el código es correcto; la spec y los comentarios del script están desalineados y pueden inducir error al reconfigurar.  
   - **Acción:** corregir comentarios y tabla en spec (fuera de este repo).

### Importante

4. **Ruta Galform por defecto no coincide con `prep_gne_input`**  
   - **Evidencia:** `run_gne_galform.py:25` → `outpath = '.../Data/Galform/SU1'`; `prep_gne_input` escribe en `.../Galform_to_copy/`. `slurm_hdf5_run.py` usa `sam = 'Galform_to_copy'` y reescribe `simpath` vía `modify_param_file`.  
   - **Impacto:** ejecución manual del script lee árbol antiguo; Slurm sí apunta al árbol nuevo si `modify_param_file` actualiza `outpath`.  
   - **Acción:** alinear `outpath` por defecto con `Galform_to_copy` o documentar que solo Slurm reescribe rutas.

5. **`extra_params` Shark: `data/r_bulge` inexistente en HDF5 de entrada**  
   - **Evidencia:** `run_gne_shark.py:241` pide `data/r_bulge`; `prep_gne_input` escribe `data/rgas_bulge` (`config.py` Shark). `extra_params_names` usa `rgas_bulge`.  
   - **Impacto:** fallo al leer parámetros extra o columna vacía/ausente en salida.  
   - **Acción:** cambiar a `data/rgas_bulge`.

6. **`redshift_previous` solo advierte, no aborta**  
   - **Evidencia:** `run_gne_shark.py:304-305` imprime warning si `read_previous_redshift` devuelve `None`. Con `Lagn_insta=False` (modo instantáneo Griffin), la spec exige `ValueError` explícito.  
   - **Impacto:** ejecución con ventana temporal heurística (`delta_t_window = t_snapshot/10` en `gne_Lagn.py`) si falta snapshot anterior.  
   - **Acción:** validar `redshift_previous` antes de `gne()` cuando `Lagn_insta=False`; asegurar que `redshift_path` cubre todos los snaps de campaña.

7. **`redshift_list` cargado pero no usado**  
   - **Evidencia:** `np.loadtxt(redshift_path)` en ambos scripts; solo se usa `read_previous_redshift(redshift_path, snapshot)` en el bucle.  
   - **Impacto:** código muerto; confusión.  
   - **Acción:** eliminar `redshift_list` o usarlo en `read_previous_redshift`.

8. **Fichero duplicado `taurus/run_gne_galform copy.py` (untracked)**  
   - **Evidencia:** copia con API antigua de `gne()` (`vol, mp` posicional, sin `Lagn_insta`, `tau_fold`, `redshift_previous`).  
   - **Impacto:** riesgo de ejecución accidental del script obsoleto.  
   - **Acción:** borrar; no commitear.

### Opcional

9. **`plot_tests = False`** — razonable para campaña masiva Slurm.

10. **`check_all_jobs` en `slurm_hdf5_run.py`** — el bucle por `(sim, snap)` llama a `check_all_jobs(sam, snap, ...)` sin filtrar por simulación; puede mezclar logs de distintos modelos si comparten prefijo. Revisar si `generate_job_name` distingue suficientemente.

11. **`create_slurm_script(..., sam, snap, str(nvol))`** — firma alineada con `gne_slurm.create_slurm_script(hpc, param_file, simpath, model, snap, subvols, ...)` ✅.

12. **Galform `Lagn_params=['data/Lbol_AGN','data/mstars_bulge']`** — en modo `Lagn`, `get_Lagn` solo usa `vals[0]`; el segundo elemento es redundante (no rompe, pero confunde).

---

## Matriz de configuración objetivo (post-corrección)

| Script | `Lagn_inputs` | `Lagn_insta` | `tau_fold` | Notas |
| --- | --- | --- | --- | --- |
| `run_gne_shark.py` | `Griffin+19` | `False` | `1.0` | BOOL sobre componente SB; escribe `L_agn_noinsta` |
| `run_gne_galform.py` | `Lagn` | `True` | `None` | Usa `L_bol` del catálogo sin remuestreo |

---

## Checklist

| Ítem | Estado |
| --- | --- |
| **Corrección** — firma `gne()` y parámetros AGN | ❌ `tau_field`; `Lagn_insta` invertido |
| **Diseño** — Shark vs Galform según spec | ⚠️ intención correcta en Shark (Griffin+19) pero flag mal puesto |
| **Secretos** — sin credenciales | ✅ |
| **Coherencia rutas con `prep_gne_input`** | ⚠️ Slurm OK; manual Galform no |

---

## Acciones recomendadas (orden)

1. Renombrar `tau_field` → `tau_fold` en `run_gne_galform.py` y `run_gne_shark.py`.
2. Corregir `Lagn_insta` (Shark `False`, Galform `True`) y actualizar comentarios al significado de la spec.
3. Sustituir `data/r_bulge` por `data/rgas_bulge` en `extra_params`.
4. Eliminar `run_gne_galform copy.py` y la variable `redshift_list` no usada.
5. Alinear `outpath` Galform con `Galform_to_copy` o verificar que `modify_param_file` siempre lo sobrescribe.
6. Relanzar un subvolumen de prueba (`testing=True`) antes de campaña completa.
