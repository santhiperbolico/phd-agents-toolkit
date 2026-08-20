# Análisis: Haloscope SIM → FastPM (MN5 / `fastpm_tfm`)

**Repository:** [density_field_properties](https://github.com/computationalAstroUAM/density_field_properties)  
**Issue:** [#6](https://github.com/computationalAstroUAM/density_field_properties/issues/6)  
**Notebook de referencia:** `notebooks/SIM_to_FASTPM_enviarSanti.ipynb`  
**Rama de trabajo (producto):** `6-haloscope-fastpm` (desde `develop` en fork `santhiperbolico`)  
**Last updated:** 2026-07-26

---

## Qué hace el notebook (flujo Haloscope)

El notebook implementa el método **Haloscope** (ver [README del repo](https://arxiv.org/pdf/2410.07361)): transferir propiedades de halos de una simulación “verdad” (SIM) a FastPM mediante una **gaussiana multivariante condicional** `p(y|x)` (`ConditionalMultiVariateGaussian` en `notebooks/haloscope-main/haloscope.py`).

```
SIM hlist (pid=-1, Spin, cv, ca, ba, M200b)
    → env (KD-tree periódico)
    → fit CMVG por bin log M  ──predict(env)──►  FastPM enriquecido (x,y,z,M200b + cv,Spin,ca,ba)
FastPM (x,y,z,M200b)
    → env (mismo algoritmo, otro box size)
```

| Etapa | Entrada | Salida |
| --- | --- | --- |
| 1 | SIM `hlist_1.00000.list` (consistent-trees) | `halos_sim` con `cv = Rvir/Rs_Klypin`, filtros `pid==-1`, `M200b>0` |
| 2 | FastPM (hoy stub Parquet en el template) | `halos_fastpm` con `x,y,z,M200b` |
| 3 (opc.) | `CALIBRATE_MASS=True` | `M200b_cal` por abundance matching SIM↔FastPM |
| 4 | Posiciones + `BOXSIZE` por simulación | columna `env` = log10(1 + vecinos en `ENV_RADIUS` Mpc/h) |
| 5 | Bins en log10(M) | `fit(env)` → `predict` → `cv`, `Spin`, `ca`, `ba` en FastPM |
| 6 | — | `FASTPM_augmented_z0.parquet` + PDFs de validación |

**Modelo:** `x = [env]`; `y = [cv, Spin, ca, ba]`. Un modelo **por bin de masa** entrenado en SIM; se aplica a halos FastPM del mismo bin (masa SIM o `M200b_cal`).

**Haloscope:** depende de **scikit-learn** (`QuantileTransformer`). Import desde `notebooks/haloscope-main/` (p. ej. `sys.path` en la primera celda). `predict()` **muestrea** ruido gaussiano y aplica restricciones en `ca`/`ba`; no es determinista (el código imprime depuración: `"here"`, tasa de aceptación).

---

## Qué datos hay ya (MN5 / `fastpm_tfm`)

Según `config/fastpm_folders.md` y corridas ya hechas en el proyecto:

| Recurso | Ruta típica | Rol en Haloscope |
| --- | --- | --- |
| FastPM Rockstar (PM) | `/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_pm/out_0.list` | **Target** a enriquecer (posición + masa) |
| FastPM Rockstar (nbody) | `.../rockstar_out_nbody` | Alternativa de criterio de halos |
| Snap / densidad | `.../output_01/snap_1.0000` | **No** entra en el notebook actual (solo `env` por vecinos entre halos) |
| Tidal tensor / descriptors | p. ej. `output/fast_pm_bigfile/tidal_anisotropy/` | **Paralelo** al notebook: pipeline con campo de densidad; Haloscope usa proxy `env`, no `TidalForce` de la SIM |

Para FastPM hay que **sustituir** `load_fastpm()` (Parquet stub) por lectura Rockstar, alineada con la issue #5:

- `RockstarCatalogReader.read_catalog(path, n_lines=...)` → DataFrame con `halo_x/y/z`, `halo_m200b` renombrados a `x,y,z,M200b`.
- Cabecera `#Om / #Ol / #h` ya soportada en el reader.
- **Caja** para el KD-tree: el template usa **1000 Mpc/h**; hay que fijarla con el box de la corrida MN5 (Header FastPM / mismos parámetros que CIC y tidal en el repo).

---

## Qué falta (bloqueante para entrenar)

El notebook **no puede entrenar solo con FastPM**: hace falta un catálogo **SIM de entrenamiento** con columnas Rockstar/consistent-trees:

- `SIM_PATH`, `SIM_HLIST`, `SIM_HEADER`, `SIM_USECOLS`, `SIM_BOXSIZE` (ej. 205 Mpc/h en el template).
- Columnas: `Spin`, `Rvir`, `Rs_Klypin` (para `cv`), `ba`, `ca`, `M200b`, `pid`, etc.

Eso **no está** documentado en `fastpm_folders.md`. Hay que decidir qué simulación DMO/CV es la “verdad” y dónde está el `hlist_1.00000.list` en el cluster (o local). Sin SIM, solo se puede cargar FastPM; el bloque `fit` no tiene sentido.

---

## Implementación issue #6 (mapeo a tareas)

1. **Nuevo notebook** `notebooks/SIM_to_FASTPM_fastpm_mn5.ipynb`: celda **config** con rutas `/data21/...`, `FASTPM_BOXSIZE`, `SIM_*`, `ENV_RADIUS`, `N_MAX_HALOS` / `n_lines`, `CALIBRATE_MASS`, salidas bajo `output/`.
2. **Imports:** `sys.path` → `haloscope-main`; comprobar `sklearn` en `environment.yml` (añadir si falta).
3. **`load_fastpm`:** wrapper `RockstarCatalogReader` + `pandas` (subset con `n_lines`).
4. **SIM:** mantener `load_hlists` o unificar si el formato es `.list` con otra cabecera; validar `SIM_USECOLS` contra la línea `#ID ...` del hlist real.
5. **`local_environment`:** copiar del notebook original (o módulo compartido más adelante; YAGNI en v1).
6. **Runtime:** subset (p. ej. 50k halos) para prueba local; markdown con instrucciones Slurm / corrida completa.
7. **Documentación:** enlace en README y `config/fastpm_folders.md`; markdown sobre relación con pipeline tidal (mismo catálogo Rockstar; feature distinta: `env` vs tensor tidal).
8. **Validación:** al menos un corner plot SIM (hold-out) y uno SIM vs FastPM generado (criterios de la issue).

---

## Decisiones a cerrar antes de codificar

1. **Ruta y box de la SIM** de entrenamiento (¿misma cosmología que `#Om=0.3089, h=0.6774` del `out_0.list`?).
2. **`rockstar_out_pm` vs `rockstar_out_nbody`** para el catálogo FastPM a enriquecer.
3. **¿`CALIBRATE_MASS`?** Recomendable si las masas FastPM Rockstar no están en la misma escala que la SIM.
4. **¿Sustituir `env` por descriptors del repo?** La issue pide reproducir el notebook; usar `tidal_anisotropy` del pipeline sería otro experimento (`INPUT_FEATURES` distinto y alineación halo a halo).

---

## Siguiente paso SDD sugerido

1. Añadir `spec.md` en esta carpeta (requisitos R1–Rn alineados con la issue #6).
2. Notebook mínimo que: (a) cargue `out_0.list` con subset, (b) falle con mensaje claro si `SIM_PATH` no está configurado, (c) ejecute Haloscope cuando la SIM esté definida.

**Pendiente del usuario:** ruta del **hlist SIM** y **box size** MN5 acordados para rellenar la celda de config.
