# Análisis: ¿NFW + Rdisp permiten estimar R200c y M200c?

| Campo | Valor |
| --- | --- |
| Fecha | 2026-09-08 |
| Estado | borrador — criterio de diseño |
| Repo / tema | FastPM FoF, Rdisp, perfiles de densidad |
| Relacionado | [`2026-09-06-fastpm-fof-bigfile-fields.md`](2026-09-06-fastpm-fof-bigfile-fields.md), [`2026-09-08-rdisp-forma-masa-m200b.md`](2026-09-08-rdisp-forma-masa-m200b.md) |

---

## Pregunta

Si asumimos un perfil de densidad (p. ej. NFW), ¿podemos usar `Rdisp` para estimar **R200c** y **M200c**? ¿La no esfericidad del grupo FoF lo invalida?

---

## Respuesta corta

| Enfoque | ¿Tiene sentido? |
| --- | --- |
| Identificación física directa: `Rdisp` = R200c | **No** |
| Modelo inverso NFW + c(M) + factor FoF calibrado | **Sí, con supuestos fuertes** |
| Sustituto de Rockstar cuando ya existe catálogo SO | **No recomendado** |

La **no esfericidad** añade scatter, pero el obstáculo principal es que FoF y R200c son **definiciones distintas**, no que el halo sea triaxial.

---

## Qué aporta asumir NFW

Perfil esférico NFW con dos parámetros libres: **M200c** (o R200c) y **concentración** c = R200c / r_s.

`Rdisp` aporta una restricción de tamaño vía la traza:

\[
R_\text{rms}^2 = \frac{1}{3}\mathrm{Tr}(\mathbf{S}) = \langle r^2 \rangle
\]

Para partículas que siguen ρ(r) dentro de una esfera de radio R, el momento de segundo orden es calculable:

\[
\langle r^2 \rangle_R = \frac{1}{M(<R)} \int_0^R r^4 \rho_\text{NFW}(r)\, dr = g(c)\, R^2
\]

Con R = R200c y **c fijada** (p. ej. relación c–M cosmológica):

\[
R_{200c} \approx \frac{R_\text{rms}}{\sqrt{\eta(c)\, g(c)}}
\qquad
M_{200c} = \frac{4\pi}{3}\, R_{200c}^3\, 200\,\rho_{\mathrm{crit},c}(z)
\]

donde η(c) es un factor de corrección **FoF** (el grupo FoF no muestrea exactamente la esfera NFW hasta R200c).

---

## Limitaciones (por orden de importancia)

### 1. FoF ≠ contorno de sobredensidad esférica

Incluso con NFW esférico:

- El FoF selecciona partículas por **linking length**, no por ρ = 200 ρ_crit.
- Puede incluir material fuera de R200c o perder material interior.
- El centro FoF puede diferir del centro de densidad de Rockstar.

NFW ayuda a **modelar** la relación, no a identificarla físicamente.

### 2. Sistema subdeterminado (M, c) con un solo escalar

`Rdisp` (traza) da **una** ecuación; NFW tiene **dos** grados de libertad.

| Cierre | Incertidumbre típica |
| --- | --- |
| c(M) cosmológica fija | ~10–20 % en R propagado a M |
| Segunda observable (`Vdisp`, `Length`) | Mejor; modelo 2×2 |
| Calibración empírica FoF ↔ Rockstar | Más honesto |

### 3. No esfericidad

NFW es esférico; `Rdisp` es un **tensor**. Colapsar a \(R_\text{rms} = \sqrt{\mathrm{Tr}/3}\) asume isotropía. Los autovalores de `S` dan forma triaxial, pero el FoF sigue sin ser un contorno de sobredensidad.

### 4. FastPM PM

El suavizado PM altera el perfil interior y la membresía FoF respecto a N-body de alta resolución (UNIT).

---

## Pipeline de inversión (si no hay Rockstar)

```text
1. R_rms = sqrt( (Rdisp[0] + Rdisp[1] + Rdisp[2]) / 3 )

2. Iterar: asumir c = c(M, z)  →  calcular g(c)

3. R200c = R_rms / sqrt( η × g(c) )
   η calibrado en subset FoF ↔ Rockstar (misma sim)

4. M200c = (4π/3) R200c³ × 200 ρ_crit,c(z)
```

**Mejora:** añadir `Vdisp` → σ_NFW(R200c, c) y resolver (M, c) con dos ecuaciones.

---

## Comparación con alternativas

| Método | Fiabilidad vs Rockstar M200c |
| --- | --- |
| M_FoF = N × m_p + abundance matching | Buena para HMF global |
| NFW + `Rdisp` + c(M) sin calibración η | Scatter halo a halo grande |
| NFW + `Rdisp` + `Vdisp` + c(M) | Mejor, mucho más trabajo |
| Rockstar M200c directo | Referencia estándar |

---

## Conclusión

- **Teóricamente:** NFW cierra el problema si fijas c(M) y calibras η(FoF).
- **Prácticamente:** con Rockstar disponible en FastPM, no compensa frente a M200c/R200c directos.
- **Uso razonable:** catálogo solo FoF, sin Rockstar, aceptando ~0.1–0.3 dex de incertidumbre en masa; siempre validar en pares emparejados.

---

## Referencias

- Tensor de segundos momentos: [`2026-09-06-fastpm-fof-bigfile-fields.md`](2026-09-06-fastpm-fof-bigfile-fields.md)
- Rdisp vs M200b (sin NFW): [`2026-09-08-rdisp-forma-masa-m200b.md`](2026-09-08-rdisp-forma-masa-m200b.md)
- Calibración FoF con Ap. C Ramakrishnan: [`2026-09-08-fof-masa-calibracion-ramakrishnan-apc.md`](2026-09-08-fof-masa-calibracion-ramakrishnan-apc.md)
