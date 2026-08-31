# Plan Cursor: verificación ICs FastPM ↔ UNIT — sesión Taurus

| Campo | Valor |
| --- | --- |
| Fecha | 2026-08-31 |
| Estado | **en progreso** — r(k) calculado; pendiente param files, nota análisis y Notion |
| Entorno | Cluster Taurus (SSH interactivo; job Slurm opcional y ligero) |
| Repo de producto | `density_field_properties` |
| Repo toolkit (notas) | `phd-agents-toolkit` |
| Tarea Notion | [Matching de halos FastPM ↔ UNIT](https://app.notion.com/p/3ab2070c3c2880cca1c2c1c8a4a8190d) |
| Plan relacionado | [`2026-08-27-haloscope-taurus.md`](2026-08-27-haloscope-taurus.md) |

---

## Instrucciones para el agente

Eres un agente que trabaja **desde Taurus** (SSH interactivo o sesión en el nodo de login). El usuario abre este plan en el workspace multi-root con `phd-agents-toolkit`.

### Reglas obligatorias

1. **Lee este plan completo** antes de ejecutar nada.
2. **Un solo job Slurm activo** del usuario a la vez (`squeue -u "$USER"`). Si hay jobs en `R`/`PD`, no lances otro hasta que terminen o el usuario lo confirme.
3. **No tumbar el cluster:** no cargues catálogos `.list` completos ni hagas CIC a 512³ o más sin subset. Usa `n_lines`, filtros de masa o muestreo aleatorio.
4. **No uses el MCP `taurus` desde el portátil** si el usuario ya está en Taurus; opera con shell en la sesión actual.
5. **Commit/push solo con permiso explícito** del usuario.
6. **No implementes matching 1-1** en esta sesión; solo verificación de ICs/semilla.

### Rutas en Taurus (referencia)

| Recurso | Ruta |
| --- | --- |
| Repo Haloscope | `/home/arnes/santiago_arranz/density_field_properties` |
| Toolkit (notas) | `/home/arnes/santiago_arranz/phd-agents-toolkit` |
| FastPM Rockstar PM | `/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_pm/out_8.list` |
| FastPM Rockstar nbody | `/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_nbody/out_8.list` |
| UNIT Rockstar (Adrián, a=1) | `/data21/UNITSIM/fixedAmp_InvPhase_001/ROCKSTAR/out_128p.list.bz2` |
| UNIT hlist (legacy /data5, no usado en verificación final) | `/data5/UNITSIM/fixedAmp_InvPhase_001/ROCKSTAR/outputs/hlists/hlist_1.00000.list.bz2` |
| Script verificación | `density_field_properties/scripts/verify_fastpm_unit_ics.py` |
| Slurm verificación | `density_field_properties/slurm/verify_fastpm_unit_ics/main_verify_fastpm_unit_ics.slurm` |
| Salida numérica | `density_field_properties/output/fastpm_unit_seed_check/` |
| Tutorial FastPM (param files) | `/home/adrian/UNIT_PNG/tutorial_fastpm/` |
| Salida de esta sesión | `phd-agents-toolkit/notes/analisis/2026-08-31-fastpm-unit-seed-check.md` |

### Documentación de apoyo

- Confirmación Adrián (31 ago 2026): DM Slack Cosmology-UAM — mismas seeds; UNIT = `fixedAmp_InvPhase_001`.
- Nota calibración masas: [`notes/analisis/2026-08-27-haloscope-mass-calibration.md`](../analisis/2026-08-27-haloscope-mass-calibration.md)
- Reader Rockstar: `density_field_properties.halo_catalog.rockstar.RockstarCatalogReader`
- Pylians P(k) halos (referencia en otro repo): `fnl_matching.power_spectrum.get_pk_halos`

---

## Objetivo de la sesión

**Verificar que FastPM MN5 y UNIT `fixedAmp_InvPhase_001` comparten la misma semilla/ICs**, siguiendo el criterio de Adrián:

- Calcular **cross power spectrum** de halos (o coeficiente de correlación)
  `r(k) = xPk / sqrt(Pk_UNIT × Pk_FastPM)`
- **r(k) ≈ 1** a grandes escalas → ICs compatibles
- **r(k) ≈ 0** → seeds distintas

Complementar con comprobación de **parameter files** y cabeceras Rockstar (box, cosmología).

Estimación total: **~2 h**. Prioridad: rutas → headers → cross-P(k) en subset → nota de avance.

---

## Contexto

```mermaid
flowchart LR
    A[Param files / headers] --> B[Mismo box + cosmología?]
    B --> C[Subset halos mismo z]
    C --> D[CIC + Pk auto y cruzado]
    D --> E{r k grande escala}
    E -->|~1| F[ICs OK — desbloquea matching]
    E -->|~0| G[Seeds distintas — documentar]
```

| Fuente | Qué dice |
| --- | --- |
| Adrián (Slack, 31 ago) | FastPM en `fastpm_MN5/fastpm_tfm/` = UNIT 4096 `fixedAmp_InvPhase_001` |
| Adrián | Matching requiere mismas seeds; UNIT sin particle IDs |
| Adrián | Verificar con r(k) antes del matching 1-1 |
| Notion tarea matching | Subtarea activa: **Verificar ICs con r(k)** |

**Corrección importante (31 ago):** FastPM `out_8.list` tiene `#a = 1.000000` (z = 0), **no** z ≈ 1. El índice `out_8` no es redshift. Snapshot UNIT equivalente: **`out_128p.list.bz2`** (`#a = 1.000000`). No usar `out_8p` (a = 0.0701).

**Hipótesis revisada:** comparar ambos catálogos Rockstar a **a = 1** en caja 1000 Mpc/h.

---

## Alcance

### Incluido

- Comprobar que existen rutas FastPM y UNIT.
- Leer cabeceras Rockstar (`grep '^#'`) y anotar `Box size`, `h`, `Omega_m`, etc.
- Buscar y comparar parameter files (seed, `IC`, `box`, cosmología) en directorios FastPM y UNIT.
- Localizar snapshot UNIT al mismo redshift que `out_8`.
- Cross-P(k) en **subset** de halos (p. ej. 50k–200k por catálogo, o `M200b` mínima).
- Figura `r(k)` y tabla resumen en nota Markdown.
- Actualizar subtarea Notion «Verificar ICs» con resultado.

### Fuera de alcance

- Matching halo a halo (siguiente sesión).
- Catálogo completo o CIC a grid > 256³ sin aprobación.
- `sbatch` pesado salvo que el subset no quepa en memoria del nodo de login.
- Decidir `rockstar_out_pm` vs `nbody` (usar **PM** salvo que falle la verificación; repetir con nbody solo si hace falta).

---

## Criterios de aceptación

| Criterio | Umbral |
| --- | --- |
| Headers | Mismo `Box size` (±0.1%) y cosmología consistente |
| Param files | Misma convención de seed/phase (`fixedAmp`, `InvPhase_001`, etc.) |
| r(k) a k bajos | mediana r(k) > **0.9** en bins con k < 0.05 h/Mpc (ajustar si box distinto) |
| r(k) seeds distintas | mediana r(k) ≈ 0 en mismos bins → **ICs NO compatibles** |
| Entregable | Nota `2026-08-31-fastpm-unit-seed-check.md` + Notion actualizado |

Si headers/param files discrepan, **parar** y documentar sin forzar el cross-P(k).

---

## Plan por bloques

### Bloque 0 — Arranque (10 min)

| Paso | Acción | Criterio |
| --- | --- | --- |
| 0.1 | `squeue -u "$USER"` | Sin jobs pesados inesperados |
| 0.2 | Comprobar rutas FastPM y UNIT (`ls`, `test -f`) | Rutas existen o anotar alternativa |
| 0.3 | Activar venv y `PYTHONPATH` | Import de `density_field_properties` OK |

```bash
squeue -u "$USER" -h -o "%i %j %T %M"
REPO=/home/arnes/santiago_arranz/density_field_properties
TOOLKIT=/home/arnes/santiago_arranz/phd-agents-toolkit
cd "$REPO"
source src/.venv/bin/activate
export PYTHONPATH="${REPO}/src:${PYTHONPATH}"

FASTPM_LIST=/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_pm/out_8.list
UNIT_ROCKSTAR=/data21/UNITSIM/fixedAmp_InvPhase_001/ROCKSTAR

test -f "$FASTPM_LIST" && echo "FastPM OK" || echo "FastPM MISSING"
ls -la "$UNIT_ROCKSTAR" | head -20
```

---

### Bloque 1 — Headers y parameter files (25 min)

| Paso | Acción | Criterio |
| --- | --- | --- |
| 1.1 | `grep '^#' "$FASTPM_LIST" \| head -30` | Tabla box, h, Om |
| 1.2 | Listar snapshots UNIT: `ls "$UNIT_ROCKSTAR"` | Identificar fichero z ≈ 1 |
| 1.3 | `grep '^#'` del `.list` UNIT elegido | Mismos parámetros que FastPM |
| 1.4 | Buscar param files FastPM bajo `fastpm_MN5/` y `tutorial_fastpm/` | `grep -iE 'seed\|IC\|box\|omega'` |
| 1.5 | Buscar metadata UNIT bajo `fixedAmp_InvPhase_001/` | Misma seed/phase si está documentada |

**Preguntas resueltas / pendientes:**

- [x] ¿Qué snapshot UNIT corresponde a `out_8` FastPM a a=1? → **`out_128p.list.bz2`**
- [x] ¿Box 1 Gpc/h en ambos? → **Sí (1000 Mpc/h)**
- [ ] ¿Misma seed/phase en param files? → **Pendiente (bloque 1)**

---

### Bloque 2 — Subset de halos (20 min)

| Paso | Acción | Criterio |
| --- | --- | --- |
| 2.1 | Cargar FastPM con `RockstarCatalogReader.read_catalog(path, n_lines=...)` o script propio | DataFrame/array con x,y,z |
| 2.2 | Cargar UNIT equivalente, **mismo criterio de selección** | Mismo número de halos ±10% |
| 2.3 | Filtrar `pid == -1` si la columna está disponible | Solo halos centrales |
| 2.4 | Opcional: cortar por `M200b > 5×10¹⁰ Msun/h` | Reduce ruido de subestructura |

**Parámetros sugeridos (empezar conservador):**

| Parámetro | Valor inicial |
| --- | --- |
| `N_HALOS` | 100_000 (o `n_lines` equivalente) |
| `N_GRID` | 128 |
| `MAS` | CIC |
| `BOX_SIZE` | leer de cabecera Rockstar (Mpc/h) |

Snippet de referencia (adaptar en script/notebook):

```python
from density_field_properties.halo_catalog.rockstar import RockstarCatalogReader

fastpm = RockstarCatalogReader.read_catalog(FASTPM_LIST, n_lines=100_000)
unit = RockstarCatalogReader.read_catalog(UNIT_LIST, n_lines=100_000)

pos_fastpm = fastpm.data[:, [1, 2, 3]]  # ajustar índices si el reader devuelve otro layout
pos_unit = unit.data[:, [1, 2, 3]]
```

Verificar en Taurus el layout exacto de `HaloCatalogData` antes de indexar.

---

### Bloque 3 — Cross power spectrum y r(k) (45–60 min)

| Paso | Acción | Criterio |
| --- | --- | --- |
| 3.1 | Construir δ_halo (CIC) para FastPM y UNIT con **mismo** `N_GRID`, `BOX_SIZE`, `MAS` | Cubos float32, mean=1 tras normalizar |
| 3.2 | Calcular Pk auto: `PKL.Pk(delta, BoxSize, ...)` | k, Pk_FastPM, Pk_UNIT |
| 3.3 | Calcular cross-Pk: `PKL.XPk(delta_fastpm, delta_unit, BoxSize, ...)` | k, xPk |
| 3.4 | `r(k) = xPk / sqrt(Pk_UNIT * Pk_FastPM)` | Array r(k) |
| 3.5 | Plot r(k) vs k; línea horizontal en 1 | Guardar en `output/fastpm_unit_seed_check/` |
| 3.6 | Repetir con `N_GRID=256` si memoria permite | Robustez (opcional) |

**Dependencias Pylians** (comprobar en venv de Taurus):

```python
import MAS_library as MASL
import Pk_library as PKL
import numpy as np

# delta_fastpm, delta_unit: cubes (N_GRID, N_GRID, N_GRID)
pk_f = PKL.Pk(delta_fastpm, BOX_SIZE, 0, "CIC", 64, False)
pk_u = PKL.Pk(delta_unit, BOX_SIZE, 0, "CIC", 64, False)
xpk = PKL.XPk(delta_fastpm, delta_unit, BOX_SIZE, 0, "CIC", 64, False)

k = pk_f.k3D
r = xpk.Pk[:, 0] / np.sqrt(pk_f.Pk[:, 0] * pk_u.Pk[:, 0])
```

Si `PKL.XPk` no está disponible, alternativa mínima:

1. FFT de ambos campos → `δ̂₁`, `δ̂₂`
2. `xPk = mean(Re(δ̂₁* δ̂₂))` en bins de |k|
3. Normalizar con autospectros

**Interpretación:**

- Mismas ICs: r(k) → 1 para k ≪ k_Nyquist (modos grandes alineados).
- Seeds distintas: r(k) ≈ 0 (fases no coherentes).
- Solver PM distinto puede bajar r(k) a k altos **sin** invalidar ICs; el diagnóstico es a **grandes escalas**.

---

### Bloque 4 — Documentar y cerrar (20 min)

| Paso | Acción | Criterio |
| --- | --- | --- |
| 4.1 | Escribir `notes/analisis/2026-08-31-fastpm-unit-seed-check.md` | Tabla rutas, headers, r(k), veredicto |
| 4.2 | Guardar figura y CSV de r(k) | Ruta en la nota |
| 4.3 | Actualizar Notion tarea matching | Subtarea «Verificar ICs» marcada; veredicto en cuerpo |
| 4.4 | Si ICs OK: anotar snapshot UNIT definitivo para matching | Desbloquea siguiente sesión |

**Plantilla de veredicto (rellenar):**

```markdown
## Veredicto

- **ICs compatibles:** NO
- **Evidencia:** mediana r(k) = 0.17 en k < 0.05 h/Mpc (500k centrales, n_grid=256); headers OK
- **Snapshot UNIT usado:** out_128p.list.bz2
- **Siguiente paso:** param files + escalar a Adrián; no matching 1-1 aún
```

---

## Script implementado

Ubicación: `density_field_properties/scripts/verify_fastpm_unit_ics.py`

- Módulo P(k): `src/density_field_properties/density_field/power_spectrum.py`
- Loaders centrales (streaming): `load_fastpm_central_target_catalog`, `load_unit_rockstar_target_catalog`
- Defaults: FastPM `out_8.list`, UNIT `out_128p.list.bz2`, `--n-halos 500000`, centrales (`DescID`/`PID == -1`)

```bash
cd /home/arnes/santiago_arranz/density_field_properties
source src/.venv/bin/activate  # o: conda activate density_field_properties
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"

sbatch slurm/verify_fastpm_unit_ics/main_verify_fastpm_unit_ics.slurm
# Logs Slurm: output/fastpm_unit_ics.out / .log
```

Salida: `r_k.csv`, `r_k.png`, `summary.json` en `--output-dir`.

---

## Comandos de referencia

```bash
REPO=/home/arnes/santiago_arranz/density_field_properties
TOOLKIT=/home/arnes/santiago_arranz/phd-agents-toolkit
cd "$REPO"
source src/.venv/bin/activate
export PYTHONPATH="${REPO}/src:${PYTHONPATH}"

FASTPM_LIST=/data21/users/mruiz/fastpm_MN5/fastpm_tfm/rockstar_out_pm/out_8.list
UNIT_BASE=/data21/UNITSIM/fixedAmp_InvPhase_001/ROCKSTAR

grep '^#' "$FASTPM_LIST" | head -30
ls -lh "$UNIT_BASE"
find /data21/users/mruiz/fastpm_MN5 -iname '*.param' -o -iname '*param*' 2>/dev/null | head -10
find /data21/UNITSIM/fixedAmp_InvPhase_001 -maxdepth 2 -type f 2>/dev/null | head -20

mkdir -p output/fastpm_unit_seed_check
```

---

## Criterios de aceptación (fin de sesión)

- [x] Rutas FastPM y UNIT confirmadas; snapshot UNIT a **a = 1** identificado (`out_128p.list.bz2`).
- [x] Headers: box = 1000 Mpc/h, Om = 0.3089, Ol = 0.6911, h = 0.6774 (ambos catálogos).
- [ ] Parameter files revisados (seed/phase anotados).
- [x] r(k) calculado en subset(s) y figura guardada.
- [x] Veredicto explícito: **ICs NO compatibles** según umbral r(k) > 0.9.
- [ ] Nota `2026-08-31-fastpm-unit-seed-check.md` creada.
- [ ] Notion actualizado (subtarea verificación ICs).
- [x] Tabla «Notas de sesión» al final de este plan actualizada.

---

## Notas de sesión

| Hora | Bloque | Resumen | Bloqueos |
| --- | --- | --- | --- |
| ~15:00 | 0 | Rutas OK; venv conda `density_field_properties`; mutex Slurm respetado | Primer sbatch falló: directorio log inexistente |
| ~15:06 | 3 | Job 98398: script + r(k); logs en `output/fastpm_unit_ics.*` | — |
| ~15:30 | 1–3 | UNIT cambiado a `/data21/.../out_128p.list.bz2` (Adrián); soporte bz2 en reader | hlist `/data5` daba r(k) bajo; snapshot `out_8p` es a=0.07 |
| ~16:06 | 3 | Job 98400: n_grid=256, 100k halos asimétricos → mediana r(k)=0.24 | FastPM sin filtro central inicialmente |
| ~16:37 | 2–3 | Conteo catálogos: FastPM ~2M filas; UNIT ~174M filas | Catálogo UNIT completo inviable en memoria |
| ~17:15 | 2–3 | Job 98402: **500k centrales** simétricos, n_grid=256 → mediana r(k)=**0.17** | r(k) baja al aumentar N (descartada hipótesis “pocos halos”) |

---

## Resultado (sesión 2026-08-31)

### Snapshots y tamaños

| Catálogo | Ruta | a | Filas totales (aprox.) |
| --- | --- | --- | --- |
| FastPM | `.../rockstar_out_pm/out_8.list` | 1.000 | ~1,98 M |
| UNIT | `.../ROCKSTAR/out_128p.list.bz2` | 1.000 | ~174 M |

### Headers (coinciden)

- **Box size:** 1000 Mpc/h
- **Cosmología:** Om = 0.3089, Ol = 0.6911, h = 0.6774

### Tabla r(k) — mediana en k < 0.05 h/Mpc

| Job | N_halos | Selección | n_grid | mediana r(k) | Veredicto script |
| --- | --- | --- | --- | --- | --- |
| 98398 | 100k / 87k | UNIT centrales; FastPM sin filtro central | 128 | 0.28 | incompatible |
| 98400 | 100k / 87k | idem | 256 | 0.24 | incompatible |
| **98402** | **500k / 500k** | **Centrales simétricos (streaming)** | **256** | **0.17** | **incompatible** |

Criterio Adrián: mediana r(k) > **0.9** → ICs compatibles; ≈ 0 → seeds distintas.

**Run de referencia:** job **98402**. Artefactos en `density_field_properties/output/fastpm_unit_seed_check/`.

### Veredicto

- **ICs compatibles:** **NO** (según criterio r(k) a k bajos)
- **Evidencia:** mediana r(k) = **0.17** (500k centrales, n_grid=256); headers y cosmología OK; aumentar muestra **no** acerca r(k) a 1
- **Snapshot UNIT usado:** `out_128p.list.bz2`
- **Parameter files:** **pendiente** — no revisados en esta sesión

### Interpretación breve

- La discrepancia **no parece explicarse** solo por subset pequeño o selección asimétrica de halos.
- Posibles causas a investigar: seeds/ICs distintas pese a lo indicado por Adrián; diferencias PM vs N-body acumuladas ya a k bajos en trazador halos; convención Rockstar distinta (34 vs 55 columnas); primeros N halos del fichero no aleatorios (sesgo espacial débil pero posible).

---

## Siguientes pasos

1. **Escalar a Adrián** con tabla r(k) y rutas definitivas; confirmar emparejamiento `out_8` ↔ `out_128p` y seeds en param files.
2. **Bloque 1 pendiente:** buscar param files FastPM (`fastpm_MN5/`, `tutorial_fastpm/`) y metadata UNIT (`fixedAmp_InvPhase_001`); anotar seed / `InvPhase_001`.
3. **Diagnóstico alternativo:** r(k) sobre **campo de materia** (DM CIC) en lugar de halos, si hay snapshots DM pareados a a=1.
4. **Repetir con FastPM nbody:** `rockstar_out_nbody/out_8.list` (mismo a=1) por si el trazador PM degrada la correlación.
5. **Documentar:** crear `notes/analisis/2026-08-31-fastpm-unit-seed-check.md` y actualizar Notion «Verificar ICs».
6. **No iniciar matching 1-1** hasta resolver discrepancia r(k) o validación explícita de Adrián.

---

## Resultado (plantilla histórica — rellenada arriba)

- **Snapshot UNIT:** `out_128p.list.bz2`
- **Headers:** box = 1000 Mpc/h, h = 0.6774, Om = 0.3089
- **r(k) grandes escalas:** mediana 0.17 (500k centrales, n_grid=256)
- **Veredicto ICs:** NO compatibles
- **Siguiente sesión:** param files + consulta Adrián; opcional DM P(k) o FastPM nbody
