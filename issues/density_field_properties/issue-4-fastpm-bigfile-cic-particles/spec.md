# Spec: FastPM BigFile particle I/O for CIC density pipeline

**Repository:** [density_field_properties](https://github.com/computationalAstroUAM/density_field_properties)  
**Issue:** [#4](https://github.com/computationalAstroUAM/density_field_properties/issues/4)  
**Status:** Completado (Fases A–C; pre-commit hooks requieren Python ≤3.13 — validado con black/isort/flake8 en 3.10)  
**Last updated:** 2026-07-26

## Entrada

| Parámetro | Tipo | Restricciones |
| --- | --- | --- |
| `dm_particles_file` | `str` | Ruta a fichero texto (posiciones whitespace-separated, ≥3 columnas x,y,z en Mpc/h) **o** ruta FastPM BigFile (ver abajo). |
| `mass_particle` | `float` | Masa por partícula en M☉; sigue viniendo del caller (CLI / `default_params`). |
| `box_size` | `float` | Tamaño de caja en Mpc/h. |
| `n_grid` | `int` | Celdas por eje. |
| `batch_size` | `Optional[int]` | Tamaño de lote; `None` = un solo lote con todas las partículas. |

### Formato texto (comportamiento actual)

- Fichero regular legible con `np.loadtxt`.
- Extensiones habituales: `.txt`, `.dat` (y cualquier fichero que no sea directorio FastPM).

### Formato `fastpm_bigfile`

- Misma convención de ruta que `FastPMCatalogReader`: `dm_particles_file` termina en el **subdirectorio de bloque** dentro del snapshot, p. ej. `.../snap_1.0000/1`.
- El directorio padre del último segmento es la raíz BigFile (`BigFile(complete_path)`).
- Posiciones: dataset `{main_folder}/Position`, forma `(N, 3)`, unidades **Mpc/h** (como espera `mass_field_cic`).
- Cabecera: `Header/` con atributos FastPM (opcional para validación de `N`; no sustituye `mass_particle` del CLI en v1).

## Salida

- Sin cambios en la firma pública de `density_field_cic_main` → `tuple[np.ndarray, DensityFieldInfo]`.
- `DensityFieldInfo.n_particles` = suma de partículas procesadas en todos los lotes.
- Campo de densidad idéntico al actual para los mismos datos texto.

## Comportamiento (requisitos)

1. **R1 — Texto sin regresión:** `density_field_cic_main` sobre fixtures texto existentes (`batch_size=None` y `batch_size=2`) produce el mismo `density` y `n_particles` que antes.
2. **R2 — Detección de formato:** Función `detect_dm_particle_format(path: str) -> str` devuelve `"text"` o `"fastpm_bigfile"`. Criterios:
   - `"text"`: path es fichero regular (no directorio).
   - `"fastpm_bigfile"`: path es directorio, el padre es raíz BigFile con `Header/`, y existe `{basename(path)}/Position` vía `BigFile.open`.
   - Si no encaja: `ValueError` con mensaje claro (inglés).
3. **R3 — Lectura por lotes (texto):** Misma semántica que `skiprows` acumulativo + `max_rows=batch_size`; último lote vacío termina el bucle.
4. **R4 — Lectura por lotes (BigFile):** Generador o función interna que devuelve `(positions ndarray (n,3), start_idx, end_idx)` por lote; índices para logging.
5. **R5 — Integración en `density_field_cic_main`:** Un solo bucle de acumulación CIC; logging con rangos de **índice de partícula** para BigFile y de **líneas** para texto (mensaje puede unificarse como “particles start–end”).
6. **R6 — `save_density_field_cic`:** Para rutas BigFile, el nombre base del output debe ser identificable (p. ej. usar `basename` del snapshot si el último segmento es solo numérico, o `basename` completo de la ruta sin extensión ficticia).
7. **R7 — Tests:** Mock de `BigFile` al estilo `test_fastpm_reader.py`; tests de detección; test de `density_field_cic_main` con BigFile mockeado y mismas posiciones que fixture texto pequeño.

## Errores

- `ValueError`: path inexistente, formato ambiguo, o estructura BigFile incompleta (sin `Position`).
- No introducir dependencia nueva: `bigfile` ya está en `src/environment.yml`.

## Edge cases

- `batch_size` mayor que `N`: un solo lote con `N` partículas.
- Snapshot con `N=0`: bucle sin acumular; densidad cero (comportamiento coherente con texto vacío).
- Rutas con trailing slash: normalizar o aceptar de forma consistente.

## Diseño (YAGNI)

- Módulo nuevo: `src/density_field_properties/density_field/particle_io.py` con detección + generadores de lotes.
- `cic_deposit.py`: orquestación y logging; sin flag CLI de formato.
- Reutilizar patrón path `main_folder` / `complete_path` de `halo_catalog/fastpm.py`.
- Sin kwarg `reader` explícito hasta que haga falta.

## Trazabilidad requisito → test (plan)

| Requisito | Test previsto |
| --- | --- |
| R1 | `test_density_field_cic.py` (existentes) |
| R2 | `test_particle_io.py::test_detect_*` |
| R3 | `test_particle_io.py::test_text_batches_*` |
| R4–R5 | `test_particle_io.py::test_bigfile_batches_*`, `test_density_field_cic_main_fastpm_bigfile` |
| R6 | `test_save_density_field_cic_bigfile_path` (si aplica cambio mínimo en `save_density_field_cic`) |

## Fases supervisor–ejecutor

1. **Fase A (Red):** Tests nuevos + stubs mínimos que importen; pytest debe fallar por comportamiento, no por imports rotos. ✅
2. **Fase B (Green):** Implementar `particle_io.py` y cablear `density_field_cic_main` (+ ajuste naming save si tests lo exigen). ✅
3. **Fase C (Refactor):** pre-commit en ficheros tocados; pytest verde completo. ✅ (black/isort/flake8 en Python 3.10; lectura texto sin `loadtxt` vacío al final del batcheo)
