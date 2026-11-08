# Generating Dark Matter Subhalo Populations Using Normalizing Flows

| Campo | Valor |
| --- | --- |
| Fecha nota | 2026-10-09 |
| Autores | Lonergan, Benson, Gilman |
| Publicación | The Open Journal of Astrophysics 8 (2025) |
| DOI | [10.33232/001c.142569](https://doi.org/10.33232/001c.142569) |
| arXiv | [2504.15468](https://arxiv.org/abs/2504.15468) |
| Zotero | `QJFUGXM5` |
| Tags | lensing, subhalos, Galacticus, normalizing flows, pyHalo, emulación |

## Resumen en una frase

Entrenan un **normalizing flow** sobre poblaciones de subhalos de **Galacticus** para muestrear en ~2 s lo que un árbol SAM cuesta ~3 días de CPU, y muestran que el forward model de lensing (estilo Gilman et al.) con esos subhalos reproduce estadísticas similares al **modelo empírico** ya usado en el campo.

## Problema que aborda

- La lensing fuerte de cuásares es sensible a la **subestructura** de materia oscura en la galaxia lente.
- Los análisis bayesianos / ABC necesitan **O(10⁶)** realizaciones de poblaciones de subhalos por sistema (Gilman et al. 2020).
- El modelo **empírico** (analítico, calibrado contra Galacticus) es barato pero simplifica correlaciones (stripping vs órbita, crecimiento del host, etc.).
- Correr **Galacticus** por realización (~2,6×10⁵ s ≈ 3 días CPU por árbol) no escala a millones de draws.
- Objetivo: emular la distribución joint de parámetros de subhalos de Galacticus con ML generativo, manteniendo el coste del empírico.

## Métodos (núcleo)

### Dos generadores de subhalos

1. **Modelo empírico** (Gilman et al. 2020; stripping Keeley et al. 2024): perfiles NFW truncados, SMF con pivot 10⁸ M⊙, distribución espacial 3D con núcleo uniforme (Jiang & van den Bosch 2017), CDM en este paper.
2. **Galacticus** (SAM): árboles de merger EPS/Parkinson para host **M = 10¹³·³ M⊙**, **z_lens = 0,5**, resolución **10⁶ M⊙** en masa ligada; subhalos en anillo **r_2D ≤ 20 kpc**; 300 árboles para entrenamiento (~6–8 CPU-h cada uno).

### Normalizing flow

- Cada subhalo: **6 parámetros** — M_infall, c, M_bound, z_infall, r_t (vía fit χ² al perfil vs NFW), r_2D.
- Preprocesado: logs/adimensionales respecto a M_host y R_vir; mapeo a hipercubo [-1, 1]³.
- Red: **12 capas de acoplamiento afín**, coeficientes s,t de red densa (5 capas, ReLU + tanh), Adam lr=10⁻⁴, L2=0,01.
- Train/val 80/20 sobre subhalos de los 300 árboles (~49k subhalos en figuras de validación).
- Post-muestreo: **recorte** a restricciones físicas (masa mínima 2×10⁶ M⊙, M_bound ∈ [10⁶, 10¹⁰] M⊙, z_infall ≥ z_lens, r_2D ≤ 20 kpc, etc.).

### Pipeline de lensing (demostración)

- Subhalos → **pyHalo** (rev. citada) → **Samana** para imágenes y ratios de flujo.
- Mock liso: perfil power-law elíptico (θ_E = 1″, eje 0,73, γ = 2,05, shear externa 0,057).
- Estadístico **S_lens**: RMS de desviaciones en los **tres ratios de flujo** respecto al mock (cuásar cuádruple).
- 10⁰⁰⁰ realizaciones por modelo (empírico vs emulador) para CDF de S_lens.

## Resultados clave

| Aspecto | Dato |
| --- | --- |
| Tiempo 1 población | Empírico ~2 s; Galacticus ~2,6×10⁵ s; emulador (entrenado) ~2 s |
| Entrenamiento emulador | ~1,1×10⁵ s; dataset = 300 árboles Galacticus (~2 100 CPU-h total vs ~22 000 CPU-h para 10⁶ valores S_lens) |
| Samana por S_lens | ~80 s → el cuello de botella sigue siendo el lensing forward, no el generador |
| Acuerdo empírico–emulador | Histogramas de f₂/f₁, f₃/f₁, f₄/f₁ y CDF de S_lens muy parecidos; mejor que modelo sin subestructura |
| Conteo subhalos/realización | ~23 000 (empírico) vs ~1 200 (emulador/Galacticus): distinto criterio de resolución (M_infall vs M_bound); recortar subhalos con M_bound < 10⁶ M⊙ en el empírico **no cambia** la CDF de S_lens |

## Limitaciones (autores)

- Flujos invertibles mal adaptados a bordes afilados / multimodalidad (Ap. A).
- Sin **sub-subhalos** en el entrenamiento.
- Un solo (M_host, z_lens); solo **CDM**.
- Futuro: **conditional NF** en masa de host, z, o masa de partícula WDM para un solo emulador multi-modelo.

## Código y dependencias citadas

- [Galacticus](https://github.com/galacticusorg/galacticus) — rev. `4313a4e2`
- [pyHalo](https://github.com/dangilman/pyHalo) — rev. `9a5d619`
- [Samana](https://github.com/dangilman/samana) — rev. `30cdf83`

## Opinión / lectura crítica (Roger)

**Fortalezas.** El paper cierra el argumento práctico que faltaba entre «física SAM» y «análisis de lensing a escala estadística»: el NF no sustituye Galacticus en la física, pero **amortiza** el coste del SAM en una fase de entrenamiento y luego iguala el throughput del modelo empírico. La validación no se queda en marginales 2D: conectan con **S_lens**, que es lo que importa en el pipeline de Gilman. El experimento de recorte de subhalos de baja M_bound refuerza que las diferencias de conteo entre empírico y Galacticus son en gran parte cosméticas para lensing — coherente con la literatura que ya usabas.

**Debilidades.** La comparación «Galacticus vía NF» vs «empírico» es en parte **circular**: el empírico se diseñó para parecerse a Galacticus, así que el acuerdo en S_lens es esperable y no demuestra por sí solo superioridad física del SAM emulado. Solo un mock y 10⁴ realizaciones en las figuras principales de S_lens: es prueba de concepto, no inferencia sobre datos reales ni sobre WDM. El NF opera en un hipercubo con clipping: hay riesgo de sesgo cerca de límites si el volumen de rechazo es alto (no cuantifican fracción de muestras descartadas). No discuten incertidumbre del emulador en el posterior (error de discretización del generador).

**Relevancia para tu tesis.**

- **Artículo III (catálogos rápidos / SBI):** arquetipo de «simulador caro → generador barato» con garantía de densidad (NF) frente a GANs o copulas simples.
- **Artículo I (Haloscope / emulación):** misma lógica de amortización: entrenar una vez, muestrear muchas veces en un forward model costoso.
- **No es substituto directo de HOD/FOF:** dominio lensing + subhalos en el centro de la lente; útil como referencia metodológica y como puente hacia trabajos de Gilman/Benson.

## Seguimiento sugerido

- Gilman et al. (2020, 2021, 2024) y Keeley et al. (2024) para el empírico actualizado.
- Papamakarios et al. (2021) — review de NF.
- Papers de **conditional NF** citados (Winkler 2019; Abbasi 2023) si planteas emular catálogos condicionados en cosmología o masa de halo.

## Enlaces

- [Zotero item key QJFUGXM5](zotero://select/library/items/QJFUGXM5)
