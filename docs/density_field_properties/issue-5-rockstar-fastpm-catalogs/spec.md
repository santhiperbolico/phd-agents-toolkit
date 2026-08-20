# Spec: Rockstar halo catalogs from FastPM runs

**Repository:** [density_field_properties](https://github.com/computationalAstroUAM/density_field_properties)  
**Issue:** [#5](https://github.com/computationalAstroUAM/density_field_properties/issues/5)  
**Status:** Completado (Fases A–C)  
**Last updated:** 2026-07-26

## Entrada

| Parámetro | Tipo | Restricciones |
| --- | --- | --- |
| Catálogo Rockstar | `str` (ruta fichero) | Fichero `.list` con cabecera `#` y filas whitespace-separated (columnas estándar Rockstar). |
| Reader CLI | `--halo_catalog_name` | Valor **`rockstar`** para salidas Rockstar post-FastPM (p. ej. `out_0.list`). |
| `--halo_file` | `str` | Ruta absoluta o relativa al `.list` (ej. `.../rockstar_out_pm/out_0.list`). |

## Salida

- `HaloCatalogData` con columnas id, x, y, z, m200b y opcionalmente `rg` si la cosmología del header es parseable.
- `Cosmology` desde líneas de cabecera Rockstar (formatos soportados abajo).

## Decisión de diseño (registrar en README)

- **Reutilizar `RockstarCatalogReader`** para catálogos `.list` de FastPM+Rockstar.
- **No** añadir parser duplicado en `fastpm.py` ni alias `fastpm_rockstar` salvo necesidad demostrada (YAGNI).
- `FastPMCatalogReader` sigue siendo solo para halos nativos BigFile.

## Comportamiento (requisitos)

1. **R1 — Cabecera `#Omega_M`:** Sin regresión en `read_rockstar_cosmology_header` para el formato existente (`#Omega_M = ...; Omega_L = ...; h0 = ...`).
2. **R2 — Cabecera FastPM Rockstar:** Parsear líneas con `#Om = ...; Ol = ...; h = ...` (y variantes de espacios) mapeando a `omega_matter`, `omega_lambda`, `h0` en `Cosmology`.
3. **R3 — `rg` con cosmología FastPM:** `read_catalog` y `read_catalog_batch_generator` deben incluir columna `rg` cuando R2 parsea correctamente (misma fórmula que hoy con `Cosmology`).
4. **R4 — Documentación:** README (o sección enlazada) con flujo recomendado: `--halo_catalog_name rockstar --halo_file .../out_0.list`; referencia a `config/fastpm_folders.md` (`rockstar_out_pm` vs `rockstar_out_nbody`).
5. **R5 — Fixture tipo `out_0.list`:** Test con cabecera mínima realista (`#ID ...`, `#Om`, datos con índices de columna por defecto o documentados) sin depender del cluster.
6. **R6 — Batch generator:** Test de `read_catalog_batch_generator` con cabecera `#Om` y `batch_size` pequeño (cubre reanudación por offset).

## Errores

- Líneas `#` sin parámetros reconocidos: ignorar; si no hay cosmología válida, catálogo sin `rg` (comportamiento actual).
- Cabecera parcial: no construir `Cosmology` hasta tener `omega_matter`, `omega_lambda`, `h0`.

## Edge cases

- Varias líneas `#` con cosmología: fusionar parámetros.
- `h` vs `h0` en distintas líneas: normalizar a `h0`.
- Mayúsculas/minúsculas en nombres (`Om`, `omega_m`).

## Diseño técnico

- Refactor mínimo en `rockstar.py`: helper para extraer pares `clave=valor` de líneas `#` y tabla de alias → campos `Cosmology`.
- Sin cambios en `fastpm.py` ni en `get_halo_catalog_reader` (salvo docstring breve en `utils.py` opcional si aclara el routing).

## Trazabilidad requisito → test

| Requisito | Test previsto |
| --- | --- |
| R1 | `test_read_rockstar_cosmology_header` (existente) |
| R2 | `test_read_rockstar_cosmology_header_fastpm_om_ol_h` (parametrize opcional) |
| R3 | `test_rockstar_reader_with_fastpm_cosmology_header` |
| R4 | Revisión manual README (no test automatizado obligatorio) |
| R5 | `test_rockstar_reader_fastpm_list_fixture` |
| R6 | `test_rockstar_batch_generator_fastpm_header` |

## Fases supervisor–ejecutor

1. **Fase A (Red):** Tests nuevos que fallen con el parser actual.
2. **Fase B (Green):** Implementar parser + docs.
3. **Fase C (Refactor):** pytest verde; black/isort/flake8 en ficheros tocados (Python 3.10 si hace falta).
