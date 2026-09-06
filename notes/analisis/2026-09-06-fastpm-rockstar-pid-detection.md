# Análisis: fallo en detección de columna PID en catálogos Rockstar FastPM

| Campo | Valor |
| --- | --- |
| Fecha | 2026-09-06 |
| Estado | cerrado (diagnóstico + propuesta; pendiente implementación) |
| Repo / tema | `density_field_properties` — verificación ICs FastPM ↔ UNIT |
| Relacionado | commit `7bc41f6`, `scripts/verify_fastpm_unit_ics.py`, `load_catalogs.py`, plan [`2026-08-31-fastpm-unit-seed-verification-taurus.md`](../planes-cursor/2026-08-31-fastpm-unit-seed-verification-taurus.md) |
| Log del fallo | `density_field_properties/output/fastpm_unit_ics.log` |

---

## Pregunta u objetivo

¿Por qué falla el job Slurm `fastpm_unit_ics` al cargar el catálogo FastPM Rockstar, y qué cambio corrige el error **sin perder** la funcionalidad deseada (filtrar centrales cuando existe `PID`, cargar todos los halos cuando no)?

---

## Contexto

### Funcionalidad deseada (commit `7bc41f6`)

El commit *Fix Rockstar PID filter and add optional full-catalog IC check* sustituyó el filtro incorrecto `DescID == -1` por detección de columna `PID`:

- Si el catálogo **tiene** `PID` → conservar solo halos centrales (`PID == -1`).
- Si el catálogo **no tiene** `PID` → cargar todos los halos con `M200b > 0` y emitir un warning.

Esta lógica afecta a:

- `load_fastpm_central_target_catalog()` en `load_catalogs.py`
- `_resolve_halo_selection()` en `verify_fastpm_unit_ics.py` (metadatos del `summary.json`)

### Catálogos implicados

| Catálogo | Ruta | Uso |
| --- | --- | --- |
| FastPM Rockstar PM | `/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_pm/out_8.list` | Lado FastPM en verificación r(k) |
| UNIT Rockstar | `/data21/UNITSIM/fixedAmp_InvPhase_001/ROCKSTAR/out_128p.list.bz2` | Lado UNIT en verificación r(k) |

### Run previo exitoso vs fallo actual

| Artefacto | Fecha | Resultado |
| --- | --- | --- |
| `output/fastpm_unit_seed_check/summary.json` | 2026-08-31 | OK (código anterior al filtro PID) |
| `output/fastpm_unit_ics.log` | 2026-09-06 13:12 | Fallo tras commit `7bc41f6` |

---

## Síntoma

```text
ValueError: invalid literal for int() with base 10: '0.00000'
```

**Traceback:**

1. `verify_fastpm_unit_ics.py` → `_load_fastpm_halos()`
2. → `load_fastpm_central_target_catalog()`
3. → `_collect_rockstar_halos()` línea 176: `int(columns[central_id_column])`

El valor `'0.00000'` no es un ID de halo padre; es un **float de forma del halo**.

---

## Análisis

### Cadena de decisión errónea

La función `_rockstar_pid_column_index()` infiere la presencia de `PID` así:

```python
column_count = _rockstar_data_column_count(list_path)
if column_count >= EXTENDED_ROCKSTAR_MIN_COLUMNS:  # 55
    return pid_index  # 33
return None
```

Es decir: **≥ 55 columnas ⇒ PID en índice 33**. Esa suposición es incorrecta para el `out_8.list` de FastPM.

### Layout real de los catálogos (inspección en disco)

**FastPM** (`out_8.list`):

- **55 columnas** en la primera fila de datos.
- **Sin columna `PID`** en la cabecera Rockstar.
- Las columnas extra respecto al layout compacto son tensores de inercia (`Ixx`, `Iyy`, …, `Izx(500c)`), no campos de árbol de fusión.
- Columna índice 33 (0-based): `c_to_a(500c)` → valor típico `0.00000`.

Cabecera (final):

```text
... M_pe_Diemer Halfmass_Radius rvmax NFW_chi2 Ixx Iyy Izz ... Izx(500c)
```

**UNIT** (`out_128p.list.bz2`):

- **34 columnas** en la primera fila de datos.
- **Con columna `PID`** al final de la cabecera.
- Columna índice 33: `PID` → valor `-1` para halos centrales.

Cabecera (final):

```text
... M_pe_Behroozi M_pe_Diemer PID
```

### Tabla comparativa

| Propiedad | FastPM `out_8.list` | UNIT `out_128p.list.bz2` |
| --- | --- | --- |
| Nº columnas | 55 | 34 |
| ¿Tiene `PID` en header? | No | Sí |
| Columna 33 | `c_to_a(500c)` (float) | `PID` (int, `-1` = central) |
| Heurística actual (`ncol >= 55`) | Detecta PID ✗ (falso positivo) | No detecta PID (34 < 55) |
| Carga UNIT con `central_only=True` | — | Usa índice 33 **hardcodeado** en `load_unit_rockstar_target_catalog()` |

### Por qué falla solo FastPM en este flujo

- `load_fastpm_central_target_catalog()` llama a `_rockstar_pid_column_index()` → devuelve `33` para FastPM.
- `_collect_rockstar_halos()` ejecuta `int(columns[33])` → `int('0.00000')` → `ValueError`.

Para UNIT, el mismo loader de verificación IC usa `load_unit_rockstar_target_catalog()`, que **no** pasa por la heurística de 55 columnas y fija `central_id_column=33` directamente. Eso funciona porque el catálogo UNIT sí tiene `PID` en la 33.

### Tests que refuerzan la heurística incorrecta

En `test_load_catalogs_rockstar.py`, el helper `_extended_row()` construye filas de **55 columnas** con `pid` en el índice 33, pero **sin cabecera Rockstar real**. Ese fixture modela un layout que **no coincide** con ninguno de los catálogos de producción:

- FastPM real: 55 cols, **sin** PID.
- UNIT real: 34 cols, **con** PID al final.

El test `test_rockstar_pid_column_index_requires_extended_layout` valida la heurística errónea en lugar del criterio correcto (presencia de `PID` en el header).

---

## Propuesta de corrección

### Principio

Detectar `PID` leyendo la **cabecera Rockstar** (primera línea `#ID DescID ...`), no por el número de columnas.

### Cambios concretos

#### 1. Nueva función de parseo de header

```python
def _rockstar_header_column_names(list_path: Path) -> list[str] | None:
    """Return column names from the first Rockstar header line starting with #ID."""
    opener = bz2.open if list_path.suffix == ".bz2" else open
    mode = "rt" if list_path.suffix == ".bz2" else "r"
    with opener(list_path, mode) as handle:
        for line in handle:
            if not line.startswith("#"):
                break
            tokens = line[1:].strip().split()
            if tokens and tokens[0] == "ID":
                return tokens
    return None
```

#### 2. Reemplazar `_rockstar_pid_column_index`

```python
def _rockstar_pid_column_index(list_path: Path) -> int | None:
    header = _rockstar_header_column_names(list_path)
    if header is None:
        return None
    try:
        return header.index("PID")
    except ValueError:
        return None
```

- Eliminar el argumento `pid_index` (el índice se obtiene del header).
- Eliminar `EXTENDED_ROCKSTAR_MIN_COLUMNS` de `config.py` si deja de usarse.

#### 3. Actualizar call sites

| Fichero | Cambio |
| --- | --- |
| `load_catalogs.py` → `load_fastpm_central_target_catalog` | `pid_column = _rockstar_pid_column_index(list_path)` |
| `verify_fastpm_unit_ics.py` → `_resolve_halo_selection` | Igual |
| `load_catalogs.py` → `load_unit_rockstar_target_catalog` | **Opcional pero recomendable:** usar la misma función cuando `central_only=True` en lugar del índice fijo 33 |

#### 4. Comportamiento esperado tras el fix

| Catálogo | `_rockstar_pid_column_index` | Acción |
| --- | --- | --- |
| FastPM `out_8.list` | `None` | Todos los halos con `M200b > 0` + warning |
| UNIT `out_128p.list.bz2` | `33` (desde header) | Solo `PID == -1` |

La funcionalidad deseada del commit `7bc41f6` se mantiene; solo cambia el criterio de detección.

#### 5. Actualizar tests

- Fixture **tipo FastPM**: cabecera real de 55 columnas sin `PID` + fila de datos coherente → índice `None`.
- Fixture **tipo UNIT**: cabecera con `... PID` + fila de 34 columnas → índice correcto de `PID`.
- Sustituir o complementar `_extended_row()` para que refleje layouts reales.
- Añadir test de integración que simule el header de `out_8.list` (55 cols, sin PID) y verifique que no lanza `ValueError`.

### Alternativas descartadas

| Alternativa | Motivo de descarte |
| --- | --- |
| Afinar umbral (`ncol == 34` vs `ncol == 55`) | Frágil ante otras variantes de Rockstar |
| Asumir PID siempre en índice 33 | Falso para FastPM de 55 columnas |
| Volver a `DescID == -1` | Incorrecto semánticamente (`DescID` ≠ host/subhalo) |

---

## Verificación propuesta

Tras implementar:

```bash
cd /home/arnes/santiago_arranz/density_field_properties
source src/.venv/bin/activate  # o .venv según entorno
pytest src/tests/haloscope/test_load_catalogs_rockstar.py -v
pre-commit run --all-files
```

Re-lanzar el job Slurm:

```bash
sbatch slurm/verify_fastpm_unit_ics/main_verify_fastpm_unit_ics.slurm
```

Comprobar que `output/fastpm_unit_ics.log` no contiene el `ValueError` y que `summary.json` refleja `central_halos_only: false` (FastPM sin PID) o el filtro acordado para ambos lados.

---

## Conclusiones y siguientes pasos

**Conclusión:** el fallo no es del catálogo ni de Slurm. Es un **falso positivo** en la detección de `PID`: el código confunde «catálogo con 55 columnas» con «catálogo con PID en la columna 33». El `out_8.list` de FastPM tiene 55 columnas por tensores de inercia, pero **no incluye `PID`**.

- [ ] Implementar detección de `PID` por cabecera Rockstar
- [ ] Actualizar tests con fixtures realistas (FastPM 55 cols / UNIT 34 cols + PID)
- [ ] Eliminar `EXTENDED_ROCKSTAR_MIN_COLUMNS` si queda obsoleto
- [ ] Re-ejecutar verificación ICs en Slurm y documentar resultado en `summary.json`
- [ ] Valorar alinear `load_unit_rockstar_target_catalog` con la misma función de detección

---

## Referencias

- Código: `density_field_properties/src/density_field_properties/haloscope/sim_to_fastpm/load_catalogs.py`
- Script: `density_field_properties/scripts/verify_fastpm_unit_ics.py`
- Tests: `density_field_properties/src/tests/haloscope/test_load_catalogs_rockstar.py`
- Plan sesión Taurus: [`notes/planes-cursor/2026-08-31-fastpm-unit-seed-verification-taurus.md`](../planes-cursor/2026-08-31-fastpm-unit-seed-verification-taurus.md)
- Resultado previo (31 ago): `density_field_properties/output/fastpm_unit_seed_check/summary.json`
