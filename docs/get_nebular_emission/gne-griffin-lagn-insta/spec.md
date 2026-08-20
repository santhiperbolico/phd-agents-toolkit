# Spec: Griffin+19 en `get_Lagn` y luminosidad bolométrica instantánea

**Repository:** [get_nebular_emission](https://github.com/computationalAstroUAM/get_nebular_emission)  
**Issue:** _(pendiente de enlazar)_  
**Status:** En planificación  
**Last updated:** 2026-07-30

## Resumen

Integrar de forma coherente el método **Griffin+19** (con corrección super-Eddington Griffin+2020 ya en `luminosity_from_mdot`) en el cálculo de la luminosidad bolométrica del AGN (`Lagn` / `L_bol`), y formalizar el tratamiento de la **luminosidad instantánea** frente a la luminosidad de ventana temporal (`Lagn_noinsta`), con etiquetas HDF5 claras en la salida de GNE.

El código de producto ya contiene piezas parciales (`BoolLuminosityFunction.instantaneous_luminosity`, `get_Lagn_insta`, flag `Lagn_insta` en `gne.py`, modo `griffin` en `compute_Lbol_griffin`). Esta spec define el plan para unificarlas y cerrar huecos.

## Flujo lógico objetivo (`get_Lagn` + post-proceso en `gne`)

```mermaid
flowchart TD
    START([get_Lagn]) --> UNITS[Comprobar unidades<br/>units_h0, units_Gyr, units_L]
    UNITS --> Q_LBOL{¿Hay L_bol<br/>en los datos?}

    Q_LBOL -->|Sí| READ["Usar L_bol de entrada<br/>(modo Lagn)<br/>+ conversión units_L"]
    Q_LBOL -->|No| MODEL{Lagn_inputs}

    MODEL -->|Hirschmann+14| H14[get_Lagn_H14<br/>Mdot, M_bh]
    MODEL -->|Griffin+19| G19["luminosity_from_mdot<br/>componentes SB + HH<br/>+ pesos BOOL si aplica"]

    READ --> Q_INSTA
    H14 --> Q_INSTA
    G19 --> Q_INSTA

    Q_INSTA{Lagn_insta?}

    Q_INSTA -->|True| OUT_GNE["Salida GNE: Lagn<br/>(label L_bol instantánea<br/>si procede)"]
    Q_INSTA -->|False| CALC_BOTH["Calcular Lagn instantánea<br/>y conservar Lagn_noinsta"]

    CALC_BOTH --> OUT_GNE
    OUT_GNE --> FIN([write_agn_data / fin])
```

### Convenciones de modos

| Rama | `Lagn_inputs` | `Lagn_params` |
| --- | --- | --- |
| **Sí** — `L_bol` en catálogo | `Lagn` | `[columna L_bol]` (+ `units_L`) |
| **No** — calcular `L_bol` | `Hirschmann+14` | `[Mdot, M_bh]` |
| **No** — calcular `L_bol` | `Griffin+19` | `[m_bh, bh_accretion_rate_sb, bh_accretion_rate_hh, …]` + cosmología (`h0`, `omega0`, `z`, `z_prev`, `Lbox`, `tau_fold`) |

## Entrada (configuración GNE)

| Parámetro | Tipo | Descripción |
| --- | --- | --- |
| `Lagn_inputs` | `str` | `Lagn`, `Hirschmann+14` o `Griffin+19` |
| `Lagn_params` | `list` | Columnas/rutas según modo (tabla anterior) |
| `Lagn_insta` | `bool` | `True`: `Lagn` devuelto es el que usa GNE. `False`: calcular versión instantánea y guardar también `Lagn_noinsta` |
| `Lagn_insta_params` | `list` | Parámetros para el cálculo instantáneo genérico (`r_bulge`, `v_bulge`, …) o delegación a Griffin |
| `redshift_previous` | `float` | Redshift del snapshot anterior (ventana temporal BOOL / duty cycle) |
| `tau_fold` | `float` | Factor de plegado para `t_Q` (Griffin) |

## Salida

| Dataset HDF5 | Cuándo | Label objetivo |
| --- | --- | --- |
| `agn_data/Lagn` | Siempre (AGN activo) | `L_bol (erg/s)` — valor usado por GNE para líneas y `U` |
| `agn_data/L_agn_noinsta` | Solo si `Lagn_insta=False` | `L_bol (erg/s)` integrada en la ventana entre snapshots (sin muestreo instantáneo) |

## Estado actual en el repo de producto

| Pieza | Fichero | Notas |
| --- | --- | --- |
| `BoolLuminosityFunction.instantaneous_luminosity` | `gne_griffin.py` | Muestreo Bernoulli SB; `rng` fijo (42) |
| `compute_Lbol_griffin` | `gne_griffin.py` | Aplica instantáneo solo a SB; HH sin muestreo |
| `get_Lagn_insta` / `_get_Lagn_insta` | `gne_Lagn.py` | Fórmula `min(fq·t_bulge/Δt, 1)·Lagn`; `Δt` provisional (`age_of_universe(z)/10`); `t_bulge` no vectorizado por galaxia |
| Flag `Lagn_insta` | `gne.py` | Post-`get_Lagn`; copia `Lagn_noinsta` si `False` |
| `write_agn_data(..., Lagn_noinsta=...)` | `gne_io.py` | Bug: variable `L_agn_noinsta` sin definir (debe ser `Lagn_noinsta`) |
| Modos `Hirschmann+14`, `Griffin+19`, `griffin` | `gne_Lagn.py` | Nombres duplicados / ramas incompletas (`Griffin+19` aún deriva a H14 sin spin) |

## Requisitos

1. **R1 — Función de luminosidad instantánea (prioridad 1):** API única y testeada para obtener `Lagn_insta` a partir de `Lagn_noinsta`, con dos vías documentadas:
   - **Genérica (catálogo / Hirschmann):** peso `w = min(fq · t_dyn / Δt, 1)` por galaxia (vectorizado); `Δt` = edad cósmica entre `redshift_previous` y `redshift` (astropy / `gne_cosmology`), no heurística fija.
   - **Griffin (SB):** reutilizar `BoolLuminosityFunction` (`compute_sb_weights` + `instantaneous_luminosity` sobre `luminosity_from_mdot` de la componente SB); HH sin muestreo.
2. **R2 — Integración Griffin+19 en `get_Lagn`:** Unificar `griffin` y `Griffin+19` en un solo modo; `compute_Lbol_griffin` debe poder devolver `(Lagn, Lagn_noinsta)` cuando `Lagn_insta=False`.
3. **R3 — Flujo «¿Hay L_bol?»:** Rama `Lagn_inputs='Lagn'` solo cuando `L_bol` viene en datos; ramas de cálculo solo en el caso contrario.
4. **R4 — Cableado en `gne()`:** `Lagn_insta` delega en la función unificada (R1); no duplicar lógica entre `gne.py` y `gne_griffin.py`.
5. **R5 — Salida HDF5:** Corregir bug en `write_agn_data`; labels coherentes; documentar semántica de `Lagn` vs `L_agn_noinsta`.
6. **R6 — Scripts tutorial / run:** Actualizar `run_hdf5input_tutorial.py`, `run_gne_shark.py` y comentarios de configuración con los tres modos y el flag `Lagn_insta`.
7. **R7 — Tests:** Cobertura mínima en `tests/test_Lagn.py` (y/o nuevo `test_griffin_lagn.py`) para pesos instantáneos, Griffin SB/HH y escritura de `L_agn_noinsta`.

## Errores y edge cases

- Galaxias sin bulge / `t_dyn` no finito → peso 0 o `Lagn_insta = 0` (definir y testear).
- `redshift_previous` ausente con `Lagn_insta=False` → `ValueError` explícito.
- Modo Griffin sin columnas `bh_accretion_rate_sb` / `bh_accretion_rate_hh` → error claro en lectura.
- Reproducibilidad del muestreo Bernoulli: semilla configurable (opcional, default 42).

## Diseño técnico (orientativo)

- Extraer en `gne_Lagn.py` (o módulo compartido si crece) algo como `compute_instantaneous_lagn(Lagn_noinsta, method, ...)` que enrute a `_get_Lagn_insta` o a `BoolLuminosityFunction`.
- `get_Lagn` devuelve `Lagn` (siempre la luminosidad «base» de la rama); la conversión instantánea puede quedarse en `gne()` o moverse dentro de `get_Lagn` según se mantenga separación lectura/cálculo vs. post-proceso temporal (preferir un solo sitio — R4).
- Reutilizar `FlatLambdaCDM` ya usado en `BoolLuminosityFunction` para `Δt` en la vía genérica.

## Trazabilidad requisito → test

| Requisito | Test previsto |
| --- | --- |
| R1 genérica | `test_get_lagn_insta_weights_vectorized` — pesos acotados a 1, forma del array |
| R1 Griffin | `test_instantaneous_luminosity_sb_bernoulli` — media ≈ `w·L_sb` con muchas realizaciones o mock RNG |
| R2 | `test_compute_lbol_griffin_returns_noinsta` |
| R3 | `test_get_lagn_reads_catalog_vs_calculates` (parametrize `Lagn_inputs`) |
| R5 | `test_write_agn_data_lagn_noinsta` |
| R7 | Integración mínima `gne(..., Lagn_insta=False)` con fixture HDF5 pequeño |

## Plan de implementación (fases)

### Fase 1 — Función de luminosidad instantánea _(primer punto)_

1. Refactorizar `_get_Lagn_insta` / `get_Lagn_insta`:
   - Vectorizar `t_bulge(r_bulge, v_bulge)` por galaxia.
   - Calcular `delta_t_window` con cosmología (`z_prev`, `z`).
   - Aceptar `redshift_previous` como argumento obligatorio cuando `Lagn_insta=False`.
2. Revisar `BoolLuminosityFunction.instantaneous_luminosity`:
   - Documentar contrato (entrada `L_sb` en erg/s, salida instantánea).
   - Opcional: exponer también `Lagn_noinsta = L_hh + L_sb` sin muestreo.
3. Crear función unificada `compute_instantaneous_lagn(...)` que seleccione vía genérica vs Griffin según `Lagn_inputs` / contexto.
4. Tests unitarios R1 (red phase → green).

**Criterio de cierre Fase 1:** tests R1 verdes; `get_Lagn_insta` sin heurística `age/10`; sin regresión en modos con `Lagn_insta=True`.

### Fase 2 — Griffin+19 en `get_Lagn`

1. Unificar alias `griffin` → `Griffin+19` (mantener alias deprecado con warning si hace falta).
2. Completar `compute_Lbol_griffin`: spin opcional, retorno `(Lagn_insta, Lagn_noinsta)` cuando proceda.
3. Eliminar o aislar código muerto de la rama antigua `Griffin+19` → H14 en `get_Lagn`.
4. Tests R2.

### Fase 3 — Flujo completo y salida GNE

1. Alinear `get_Lagn` con el diagrama (rama `Lagn` solo si hay `L_bol` en datos).
2. Cablear `gne()` con la función unificada de Fase 1; eliminar duplicación.
3. Corregir `write_agn_data` (`Lagn_noinsta`); revisar labels HDF5.
4. Tests R3, R5, R7.

### Fase 4 — Documentación y scripts de run

1. Actualizar tutoriales y scripts Slurm (`run_gne_shark.py`, etc.).
2. Notas de migración: renombres `Mdot_hh` → `Hirschmann+14`, `griffin` → `Griffin+19`.
3. Revisión manual README / docstrings en ficheros tocados.

## Notas de implementación en producto

_(Actualizar al cerrar cada fase con commit/PR enlazado.)_

| Fase | Estado | PR / commit |
| --- | --- | --- |
| 1 | Pendiente | |
| 2 | Pendiente | |
| 3 | Pendiente | |
| 4 | Pendiente | |
