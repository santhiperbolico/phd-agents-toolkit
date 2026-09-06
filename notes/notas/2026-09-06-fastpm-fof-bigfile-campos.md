# FastPM FoF bigfile — Rdisp, Vdisp, RVdisp y Task

| Campo | Valor |
| --- | --- |
| Fecha | 2026-09-06 |
| Tipo | experimento / referencia |
| Tags | Haloscope, FastPM, FoF, bigfile |
| Tarea Notion | [Investigar Haloscope FastPM](https://app.notion.com/p/39f2070c3c2880fab66dcc655be99ee9) |
| Análisis detallado | [`notes/analisis/2026-09-06-fastpm-fof-bigfile-fields.md`](../analisis/2026-09-06-fastpm-fof-bigfile-fields.md) |

## Contenido

Documentación de los campos del catálogo FoF FastPM en formato bigfile, investigados para cerrar el punto «¿qué es Rdisp?» de la tarea Haloscope.

**Dataset de referencia:** `fastpm_N2048/fnl100/fastpm_N1/fof/fof_0.5000/LL-0.200` (a = 0.5, linking length 0.2, 30 429 030 filas).

**Fuente código:** FastPM `libfastpm/fof.c` (`_convert_extended_halo_attrs`, `_add_extended_halo_attrs`, `_reduce_extended_halo_attrs`).

---

## Resumen ejecutivo

| Campo | Qué es |
| --- | --- |
| **Task** | Rango MPI (`ThisTask`) del proceso que registró el halo. Metadato de paralelización, no físico. |
| **Rdisp** | Tensor simétrico 3×3 (6 floats) de segundos momentos espaciales ⟨r_i r_j⟩ respecto al centro del FoF. Unidades (Mpc/h)². |
| **Vdisp** | Tensor simétrico 3×3 (6 floats) de segundos momentos de velocidad ⟨v_i v_j⟩ respecto a la media del grupo. Unidades (km/s)². Usado en RFOF. |
| **RVdisp** | Matriz 3×3 (9 floats) de momentos cruzados ⟨r_i v_j⟩. Unidades (Mpc/h)×(km/s). |

No confundir **Rdisp** (dispersión espacial del grupo FoF) con metadatos MPI ni con `rdispls` de comunicaciones MPI en otros módulos de FastPM.

---

## Columnas del bigfile (este dataset)

| Columna | DTYPE | NMEMB | Descripción breve |
| --- | --- | --- | --- |
| `ID` | i8 | 1 | ID global de partícula |
| `Position` | f4 | 3 | Centro del FoF (Mpc/h) |
| `Velocity` | f4 | 3 | Velocidad media peculiar (km/s) |
| `InitialPosition` | f4 | 3 | Posición IC (`q`) |
| `Length` | i4 | 1 | Número de partículas en el grupo |
| `MinID` | i8 | 1 | ID mínimo del grupo (etiqueta única de halo) |
| `Task` | i4 | 1 | Rank MPI original |
| `Rdisp` | f4 | 6 | Dispersión espacial (tensor simétrico) |
| `Vdisp` | f4 | 6 | Dispersión de velocidades (tensor simétrico) |
| `RVdisp` | f4 | 9 | Correlación posición–velocidad |

---

## Layout de índices

### Rdisp y Vdisp (6 componentes, simétrico)

| Índice | Rdisp | Vdisp |
| --- | --- | --- |
| 0–2 | r_x², r_y², r_z² | v_x², v_y², v_z² |
| 3–5 | r_x r_y, r_y r_z, r_z r_x | v_x v_y, v_y v_z, v_z v_x |

σ_v aproximada: `sqrt(Vdisp[0] + Vdisp[1] + Vdisp[2])`.

### RVdisp (9 componentes, fila a fila)

Índices 0–2: r_x v_x, r_x v_y, r_x v_z; 3–5: r_y v_x, …; 6–8: r_z v_x, …

---

## Relación con Haloscope

- **Vdisp** y **Rdisp** entran en el refinamiento **RFOF** (`rfof.c`) para separar subestructura kinemática.
- **Task** se puede ignorar en análisis científico (solo I/O MPI).
- **RVdisp** aporta forma/movimiento interno; no aparece en el corte RFOF básico.

---

## Enlaces

- Análisis completo (tablas attr-v2, código, ejemplo Python): [`../analisis/2026-09-06-fastpm-fof-bigfile-fields.md`](../analisis/2026-09-06-fastpm-fof-bigfile-fields.md)
- **Notion (Notes PhD):** [FastPM FoF bigfile — Rdisp, Vdisp, RVdisp, Task](https://app.notion.com/p/3d32070c3c288156b8f1f569f5fbc603)
- Issue Haloscope: [#13](https://github.com/computationalAstroUAM/density_field_properties/issues/13)
- Código FastPM: `FastPM/fastpm/libfastpm/fof.c`, `store.c`, `libfastpmio/io.c`
- Dataset local: `/home/santhiperbolico/Documentos/Doctorado/fastpm_N2048/fnl100/fastpm_N1/fof/fof_0.5000/LL-0.200`
