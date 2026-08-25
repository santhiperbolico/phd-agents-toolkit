# Griffin+19: dos métodos para combinar HH y SB

**Repository:** [galform/get_nebular_emission](https://github.com/galform/get_nebular_emission)  
**Issue:** [galform/get_nebular_emission#37](https://github.com/galform/get_nebular_emission/issues/37)  
**PR:** [galform/get_nebular_emission#38](https://github.com/galform/get_nebular_emission/pull/38)  
**Relacionado:** [spec.md](./spec.md)  
**Last updated:** 2026-08-25

## Contexto

En el modo `Lagn_inputs='Griffin+19'`, GNE recibe dos tasas de acreción por BH:

- `mdot_hh` — canal hot / radio-related (HH)
- `mdot_sb` — canal starburst (SB)

La luminosidad bolométrica sigue Griffin+19 (con corrección super-Eddington Griffin+2020 en
`get_Lbol_from_mdot`). Como \(L(\dot{m})\) **no es lineal** en todos los regímenes (ADAF, thin
disc, super-Eddington), existen dos formas razonables de combinar HH y SB.

## Método en producción (suma de tasas de acreción)

**Implementación:** `get_Lagn_G19` en `src/gne/gne_Lagn.py`.

| Caso | Fórmula |
| --- | --- |
| Luminosidad de ventana (snapshot) | \(\dot{m}_\text{tot} = \dot{m}_\text{hh} + \dot{m}_\text{sb}\), luego \(L_\text{bol} = L(\dot{m}_\text{tot})\) |
| Luminosidad instantánea (BOOL) | Muestreo Bernoulli sobre SB: \(\dot{m} = \dot{m}_\text{hh} + \mathrm{where}(\text{on\_sb}, \dot{m}_\text{sb}, 0)\), luego \(L_\text{bol,insta} = L(\dot{m})\) |

**Motivo de la elección (discusión 2026-08-10, Miguel Viogp):**

- Consistencia con **Shark**: sumar `bh_ar_hh` + `bh_ar_sb` y después `luminosity_from_mdot`.
- Consistencia con **Galform**: cuando el starburst está activo, `L(mdot_stb + mdot_hh)`; si no,
  solo `L(mdot_hh)`.
- Para duty cycle BOOL con una sola llamada a \(L(\dot{m})\), el muestreo se aplica al
  **`mdot_sb`** (encender/apagar SB) manteniendo HH siempre.

## Método alternativo (suma de luminosidades)

**Referencia archivada:** bloque comentado encima de `get_Lagn_G19` en `src/gne/gne_Lagn.py`.

| Caso | Fórmula |
| --- | --- |
| Luminosidad de ventana | \(L_\text{bol} = L(\dot{m}_\text{hh}) + L(\dot{m}_\text{sb})\) |
| Luminosidad instantánea | \(L_\text{bol,insta} = L(\dot{m}_\text{hh}) + \mathrm{where}(\text{on\_sb}, L(\dot{m}_\text{sb}), 0)\) |

**Cuándo puede ser más físico:** si el peso BOOL / duty cycle se interpreta como probabilidad de
que la **componente SB** esté activa en el instante del snapshot, sumar luminosidades por separado
respeta mejor la no linealidad de \(L(\dot{m})\) en cada canal.

**Por qué no está en producción:** diverge del flujo de los SAM (Shark/Galform) y de la
implementación alineada por Miguel; las diferencias numéricas dependen del régimen de acreción y
conviene comparar explícitamente si se reabre el debate.

## Flag `Lagn_insta` y salida HDF5

Internamente `gne()` usa `calculate_Lagn_insta = not Lagn_insta`.

| `Lagn_insta` | Comportamiento en `gne()` | HDF5 |
| --- | --- | --- |
| `True` | GNE usa luminosidad de **ventana/catálogo** (`Lagn = Lagn_noinsta`); sin muestreo BOOL genérico | Solo `agn_data/Lagn` (no se escribe `L_agn_noinsta`, evita duplicar el mismo valor) |
| `False` | GNE usa luminosidad **instantánea** (`get_Lagn_insta` o Griffin con pesos) | `agn_data/Lagn` (instantánea) + `agn_data/L_agn_noinsta` (ventana) |

Parámetro de plegado temporal BOOL: `tau_fold` (fiducial Shark: `1.0`; si `None`, se usa `c.fq`).

## Referencias en el repo de producto

| Pieza | Fichero |
| --- | --- |
| `get_Lbol_from_mdot`, `get_Lagn_G19` | `src/gne/gne_Lagn.py` |
| Pesos BOOL, `get_Lagn_insta` | `src/gne/gne_Lagn.py` |
| Cableado `calculate_Lagn_insta = not Lagn_insta` | `src/gne/gne.py` |
| Escritura `L_agn_noinsta` | `src/gne/gne_io.py` |
| Tests | `tests/test_griffin_lagn_insta.py`, `tests/test_Lagn.py` |
