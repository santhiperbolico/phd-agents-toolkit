# FastPM FoF bigfile — descripción de campos

| Campo | Valor |
| --- | --- |
| Fecha | 2026-09-06 |
| Dataset | FoF catalog, linking length 0.2, scale factor 0.5 |
| Ruta local | `/home/santhiperbolico/Documentos/Doctorado/fastpm_N2048/fnl100/fastpm_N1/fof/fof_0.5000/LL-0.200` |
| Formato | [bigfile](https://github.com/rainwoodman/bigfile) |
| Fuente código | FastPM `libfastpm/fof.c`, `libfastpm/store.c`, `libfastpmio/io.c` |
| Simulación | N2048, fnl100, `fastpm_N1` |
| Nota vinculada | [`notes/notas/2026-09-06-fastpm-fof-bigfile-campos.md`](../notas/2026-09-06-fastpm-fof-bigfile-campos.md) · [Notion Notes](https://app.notion.com/p/3d32070c3c288156b8f1f569f5fbc603) |
| Análisis Rdisp vs M200b | [`2026-09-08-rdisp-forma-masa-m200b.md`](2026-09-08-rdisp-forma-masa-m200b.md) |

---

## Contexto del dataset

| Elemento | Significado |
| --- | --- |
| `fof_0.5000/` | Catálogo FoF escrito en **a = 0.5** (z = 1). |
| `LL-0.200/` | Bloque bigfile con **linking length = 0.2** (en unidades de separación media entre partículas; parámetro `fof_linkinglength` en el paramfile). |
| `N` filas | **30 429 030** entradas (todas las columnas comparten este tamaño). |

El catálogo FoF de FastPM guarda, por cada partícula del subconjunto escrito, las propiedades del **grupo FoF** al que pertenece. Tras el post-procesado MPI, partículas del mismo halo comparten los mismos atributos de grupo (posición media, dispersiones, etc.), salvo `ID`, `Task` y metadatos de identificación.

---

## Atributos del bloque (`attr-v2`)

Metadatos comunes del bloque `LL-0.200` (no son columnas por halo):

| Atributo | Tipo | Valor (este dataset) | Descripción |
| --- | --- | --- | --- |
| `M0` | f8 | 0.997747 | Masa de partícula de referencia (10¹⁰ M☉/h por partícula CDM en la convención FastPM). |
| `a.x` | f8 | 0.5 | Factor de escala en el que se evalúan posiciones comóvingas. |
| `a.v` | f8 | 0.5 | Factor de escala asociado a velocidades. |
| `q.scale` | f8[3] | 0.488281 × 3 | Escala para decodificar `InitialPosition` desde el índice de partícula. |
| `q.shift` | f8[3] | 0 × 3 | Desplazamiento para decodificar posiciones iniciales. |
| `q.size` | i8 | 8589934592 | Tamaño de la malla de partículas (N³ con N = 2048). |
| `q.strides` | i8[3] | (4194304, 2048, 1) | Strides C-order para reconstruir índices 3D de `InitialPosition`. |

Metadatos globales de la simulación (fichero `attrv2_dump/fastpm_N1.human.txt` del snapshot asociado):

| Atributo | Valor |
| --- | --- |
| `BoxSize` | 1000 Mpc/h |
| `ScalingFactor` / `Time` | 0.5 |
| `NC` | 2048 |
| `ParticleFraction` | 0.01 |
| `UsePeculiarVelocity` | 1 |
| `UnitLength_in_cm` | 3.08568×10²⁴ (Mpc) |
| `UnitVelocity_in_cm_per_s` | 10⁵ (km/s) |

---

## Tabla de columnas del bigfile

Todas las columnas tienen **30 429 030** filas y **NFILE = 1** (un solo fichero de datos por columna).

| Columna | DTYPE | NMEMB | Unidades / tipo | Descripción breve |
| --- | --- | --- | --- | --- |
| `ID` | i8 | 1 | entero | Identificador global de la partícula (índice lineal en la malla IC, o ID de partícula según configuración). |
| `Position` | f4 | 3 | Mpc/h | Centro del grupo FoF (media comóvinga de las posiciones de miembros, con convención periódica). |
| `Velocity` | f4 | 3 | km/s (peculiar) | Velocidad media del grupo: v_p = a·ẋ. |
| `InitialPosition` | f4 | 3 | Mpc/h | Posición comóvinga en condiciones iniciales (columna `q`; decodificable con `q.*` del bloque). |
| `Length` | i4 | 1 | adimensional | Número de partículas en el grupo FoF. |
| `MinID` | i8 | 1 | entero | Etiqueta global mínima del grupo tras el merge MPI; identificador único del halo. |
| `Task` | i4 | 1 | entero | **Rango MPI original** (0 … NTask−1) del proceso que “posee” el halo tras el FoF. |
| `Rdisp` | f4 | 6 | (Mpc/h)² y (Mpc/h)² mezclados | Tensor simétrico 3×3 de **segundos momentos espaciales** respecto al centro del halo (ver abajo). |
| `Vdisp` | f4 | 6 | (km/s)² y (km/s)² mezclados | Tensor simétrico 3×3 de **segundos momentos de velocidad** respecto a la velocidad media del halo. |
| `RVdisp` | f4 | 9 | Mpc/h × km/s | Matriz 3×3 de **momentos cruzados** posición–velocidad (ver abajo). |

---

## `Task` — rango MPI del halo

**Qué es:** índice del proceso MPI (`ThisTask`) en el que se originó el segmento principal del halo durante el algoritmo FoF distribuido.

**Para qué sirve en FastPM:**

- Descomponer y reensamblar halos tras el merge global (`fastpm_store_decompose` con `FastPMTargetTask`).
- Saber en qué rank residía el halo cuando se calculó (útil para depuración y para entender la distribución del catálogo).

**Qué no es:** no es un identificador de halo ni un flag físico; es **metadato de paralelización**.

Referencia: `fof.c` — «`fof.task` is the original mpi rank of the halo»; se asigna en `fastpm_fof_remove_empty_halos` con `halos->task[i] = finder->priv->ThisTask`.

---

## `Rdisp`, `Vdisp`, `RVdisp` — dispersiones del grupo FoF

Estos campos se calculan en `_convert_extended_halo_attrs`, se acumulan sobre miembros del halo en `_add_extended_halo_attrs` y se normalizan en `_reduce_extended_halo_attrs` (`FastPM/fastpm/libfastpm/fof.c`).

Para cada partícula miembro se define, respecto al centro ya promediado del halo:

- **r_rel** = x_partícula − x_halo (con envoltura periódica en caja comóvinga).
- **v_rel** = v_partícula − v_halo (sin término de expansión de Hubble en el código actual; hay un `FIXME` en fuente).

---

## Tensor de segundos momentos espaciales (fundamento de `Rdisp`)

### Definición intuitiva

Imagina un grupo de partículas (un halo FoF) y su centro de masa **x**_halo. Para cada partícula mides el desplazamiento relativo **r**_i = **x**_i − **x**_halo. El **tensor de segundos momentos espaciales** resume todas esas desviaciones respondiendo a:

- ¿Cuánto se alejan en promedio en x, y y z?
- ¿Hay correlación entre desplazamientos en distintas direcciones? (p. ej. el halo es más alargado en una dirección)

En lugar de un solo número (como un radio), obtienes una **matriz 3×3** que codifica tamaño **y forma**.

### Definición matemática

Para N partículas con desplazamientos **r**_i = (r_ix, r_iy, r_iz), el tensor es el **promedio de productos externos**:

\[
\mathbf{S} = \langle \mathbf{r}\mathbf{r}^T \rangle = \frac{1}{N}\sum_{i=1}^{N} \mathbf{r}_i \mathbf{r}_i^T
\]

En componentes: S_ij = ⟨r_i r_j⟩ = (1/N) Σ_k r_{k,i} r_{k,j}.

La matriz es **simétrica** (S_ij = S_ji), así que solo hacen falta **6 números independientes** (xx, yy, zz, xy, yz, zx). En FastPM (`Rdisp`) se guardan exactamente esas 6 componentes, con unidades (Mpc/h)².

### Interpretación física

**Tamaño.** La **traza** Tr(**S**) = ⟨r_x²⟩ + ⟨r_y²⟩ + ⟨r_z²⟩ mide la extensión media cuadrática del grupo. Es proporcional al **radio cuadrático medio**:

\[
R_\text{rms} = \sqrt{\langle |\mathbf{r}|^2 \rangle} = \sqrt{\text{Tr}(\mathbf{S})}
\]

**Forma.** Los **autovalores** λ₁ ≥ λ₂ ≥ λ₃ ≥ 0 de **S** son varianzas en los ejes principales del halo:

| Caso | Interpretación |
| --- | --- |
| λ₁ ≈ λ₂ ≈ λ₃ | Halo más **esférico** |
| λ₁ ≫ λ₂ ≈ λ₃ | Halo **alargado** (cigarro) |
| λ₁ ≈ λ₂ ≫ λ₃ | Halo **aplanado** (disco) |

Los **autovectores** dan la orientación del halo en la caja. Ratios de autovalores (p. ej. λ₃/λ₁, √(λ₂/λ₁)) son análogos a los axis ratios **c/a**, **b/a** de Rockstar.

**Qué mide y qué no.** Sí describe la geometría del conjunto de partículas FoF; no mide masa (usar `Length` × m_p), densidad real ni relajación dinámica (para eso está `Vdisp`).

### Analogía

- **Primer momento** (centro): ⟨**r**⟩ = 0 si el centro es la media → *dónde* está el halo.
- **Segundo momento** (tensor **S**): *cómo de extendida y orientada* está la nube de partículas.

Es el mismo concepto que la **matriz de covarianza** en estadística, pero aplicada a desplazamientos espaciales respecto al centro del grupo.

### Ejemplo mínimo

Tres partículas en 1D con desplazamientos r = −1, 0, +1 respecto al centro: ⟨r²⟩ = (1 + 0 + 1)/3 = 2/3.

En 3D, si las partículas solo se extienden en x (±a, 0, 0), **S** ≈ diag(a², 0, 0) → alargado a lo largo de x.

### Extracción de forma en Python

```python
import numpy as np

def rdisp_to_tensor(rdisp_row):
    """Build 3x3 symmetric tensor from FastPM Rdisp (6 floats)."""
    sxx, syy, szz, sxy, syz, szx = rdisp_row
    return np.array([
        [sxx, sxy, szx],
        [sxy, syy, syz],
        [szx, syz, szz],
    ])

def axis_ratios_from_rdisp(rdisp_row):
    """Eigenvalue-based shape proxies (sorted λ1 >= λ2 >= λ3)."""
    eigenvalues = np.linalg.eigvalsh(rdisp_to_tensor(rdisp_row))
    lam1, lam2, lam3 = np.sort(eigenvalues)[::-1]
    if lam1 <= 0:
        return np.nan, np.nan
    return np.sqrt(lam3 / lam1), np.sqrt(lam2 / lam1)  # c/a, b/a proxies
```

**Nota:** las componentes off-diagonal de `Rdisp` en FastPM pueden no estar normalizadas por `Length` en el reduce (ver abajo); usar solo la diagonal o verificar antes de análisis cuantitativo con forma.

---

### `Rdisp` — dispersión espacial (6 componentes)

Almacena la parte independiente del tensor simétrico ⟨r_i r_j⟩ (promedio sobre miembros del halo):

| Índice | Componente | Fórmula por partícula (antes de promediar) |
| --- | --- | --- |
| 0 | xx | r_x² |
| 1 | yy | r_y² |
| 2 | zz | r_z² |
| 3 | xy | r_x r_y |
| 4 | yz | r_y r_z |
| 5 | zx | r_z r_x |

**Unidades:** (Mpc/h)² en diagonal; (Mpc/h)² en off-diagonal.

**Interpretación física:** tamaño y forma del grupo FoF en espacio comóvingo. La traza (Rdisp[0]+Rdisp[1]+Rdisp[2]) es proporcional al radio cuadrático medio del halo. Usado implícitamente en el pipeline **RFOF** (FoF refinado) junto con `Vdisp`.

**Nota de implementación:** en `_reduce_extended_halo_attrs` solo se dividen por `Length` los índices 0–2 (diagonal); los índices 3–5 se acumulan pero **no se dividen** en el reduce final. Comprobar este detalle si se usan las componentes off-diagonal de `Rdisp` para análisis cuantitativo.

### `Vdisp` — dispersión de velocidades (6 componentes)

Tensor simétrico ⟨v_i v_j⟩ con la misma convención de índices que `Rdisp`:

| Índice | Componente |
| --- | --- |
| 0–2 | v_x², v_y², v_z² |
| 3–5 | v_x v_y, v_y v_z, v_z v_x |

**Unidades:** (km/s)².

**Interpretación física:** dispersión interna de velocidades peculiares del grupo. En **RFOF** (`rfof.c`) se usa la traza de `Vdisp` (suma de componentes diagonales, luego raíz cuadrada) comparada con un umbral σ(M, z) para subdividir halos kinemáticamente activos.

Todas las 6 componentes se dividen por `Length` al finalizar el reduce.

### `RVdisp` — correlación posición–velocidad (9 componentes)

Matriz 3×3 completa ⟨r_i v_j⟩ almacenada en orden fila:

| Índice | Componente |
| --- | --- |
| 0, 1, 2 | r_x v_x, r_x v_y, r_x v_z |
| 3, 4, 5 | r_y v_x, r_y v_y, r_y v_z |
| 6, 7, 8 | r_z v_x, r_z v_y, r_z v_z |

**Unidades:** (Mpc/h) × (km/s).

**Interpretación física:** acoplamiento entre extensión espacial y movimiento interno (p. ej. rotación, contorno en diagrama r–v, elongación kinemática). No es un escalar “dispersión” único; hay que construir invariantes (traza, autovalores) si se necesita un número resumido.

Las 9 componentes se dividen por `Length` al finalizar el reduce.

---

## Resto de columnas (referencia rápida)

### `ID`

Identificador de partícula en la convención FastPM. Permite enlazar con snapshots de partículas y reconstruir `InitialPosition` cuando procede. **No se replica** al fusionar segmentos de halo (conserva el ID de la partícula de lookup).

### `Position` / `Velocity`

Medias aritméticas de las coordenadas comóvingas y velocidades peculiares de los miembros del FoF. Unidades: **Mpc/h** y **km/s** (FastPM README).

### `InitialPosition`

Posición comóvinga en el instante inicial (Lagrangian). Se escribe como `q` en el I/O (`InitialPosition` en bigfile). Decodificación con atributos `q.scale`, `q.shift`, `q.size`, `q.strides` del bloque.

### `Length`

Número entero de partículas en el grupo FoF (incluye umbral mínimo `fof_nmin` aplicado en el finder).

### `MinID`

Identificador global mínimo entre las partículas del grupo tras el merge FoF en MPI. Sirve como **ID único de halo** para agrupar segmentos repartidos entre ranks (`fastpm_fof_reduce_halo_attrs` agrupa por `MinID`).

---

## Lectura en Python (ejemplo)

```python
from bigfile import BigFile
import numpy

path = (
    "/home/santhiperbolico/Documentos/Doctorado/fastpm_N2048/fnl100/"
    "fastpm_N1/fof/fof_0.5000/LL-0.200"
)
bf = BigFile(path)
bb = bf["LL-0.200"]

pos = bb["Position"][:]          # (N, 3) float32, Mpc/h
vdisp = bb["Vdisp"][:]          # (N, 6) float32
sigma_v = numpy.sqrt(vdisp[:, 0] + vdisp[:, 1] + vdisp[:, 2])
task = bb["Task"][:]            # (N,) int32
minid = bb["MinID"][:]          # (N,) int64
length = bb["Length"][:]        # (N,) int32
```

---

## Relación con Haloscope / RFOF

| Campo | Uso downstream |
| --- | --- |
| `Vdisp` | Criterio kinemático en **RFOF** para separar subestructura (σ_v vs umbral dependiente de M y z). |
| `Rdisp` | Tamaño espacial del candidato a halo; entra en criterios de refinamiento RFOF junto con `Vdisp`. |
| `RVdisp` | Información de forma/movimiento interno; no aparece en el corte RFOF básico de `rfof.c`, pero puede ser útil para estudios de dinámica interna. |
| `Task` | Solo paralelización; ignorar en análisis científico salvo depuración de I/O. |

---

## Referencias en el código FastPM

| Tema | Fichero | Funciones / líneas relevantes |
| --- | --- | --- |
| Cálculo Rdisp/Vdisp/RVdisp | `libfastpm/fof.c` | `_convert_extended_halo_attrs`, `_add_extended_halo_attrs`, `_reduce_extended_halo_attrs` |
| Activación de columnas FoF | `libfastpm/fof.c` | `fastpm_fof_allocate_halos` (`COLUMN_RDISP \| COLUMN_VDISP \| COLUMN_RVDISP`) |
| Definición de columnas | `libfastpm/store.c` | `DEFINE_COLUMN(rdisp, …, 6)`, `vdisp`, `rvdisp`, `task` |
| I/O bigfile | `libfastpmio/io.c` | `DEFINE_COLUMN_IO("Rdisp", …)`, etc. |
| Uso de Vdisp en RFOF | `libfastpm/rfof.c` | `_std_vdisp`, bucle sobre `candidates->vdisp` |
| Unidades snapshot | `README.rst` | Position Mpc/h; Velocity km/s peculiar |

---

## Resumen ejecutivo (Rdisp / RVdisp / Vdisp / Task)

| Campo | Una frase |
| --- | --- |
| **Task** | Rank MPI donde se registró el halo (metadato de paralelización, no físico). |
| **Rdisp** | Segundos momentos espaciales del grupo FoF respecto a su centro (tensor 3×3 simétrico, 6 floats). |
| **Vdisp** | Segundos momentos de velocidad peculiars respecto a la media del grupo (tensor 3×3 simétrico, 6 floats). |
| **RVdisp** | Momentos cruzados ⟨r_i v_j⟩ (matriz 3×3, 9 floats) entre extensión espacial y movimiento interno. |
