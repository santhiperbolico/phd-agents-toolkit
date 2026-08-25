# Code review: `prep_gne_input`

**Fecha:** 2026-08-25  
**Alcance:** cambios sin commitear en `prep_gne_input` (rama `main`, +1 commit local)  
**Contexto:** [spec.md](./spec.md) — campaña Griffin+19 / `Lagn_insta`  
**Revisor:** agente (skill `code-review`)

---

## Resumen

Los cambios en `src/config.py` y `src/generate_input.py` alinean razonablemente la generación de entradas HDF5 con la spec Griffin+19: nuevos snapshots QSO_evo, soporte `ending_file` para layouts SAGE, campos Shark para acreción BH y bulge, y rutas de salida bajo `/data21/`. Sin embargo, hay **dos jobs de campaña que fallan en producción** (snapshots UNIT Shark 96 y 95) y una **inconsistencia en validación** respecto a `ending_file` que puede ocultar errores de ruta.

---

## Hallazgos

### Crítico

1. **Snapshot 96 en `SharkUNIT1Gpc_fnl0` no disponible para todos los subvolúmenes**  
   - **Evidencia:** `generate_input_slurm.py` incluye snap 96 con 64 subvolúmenes; `result.txt` reporta `prep_SharkUNIT1Gpc_fnl0_iz96_ivols0-63: ERROR`. Los jobs `SharkSU_*_iz96` sí terminan en SUCCESS.  
   - **Impacto:** el job Slurm se enviará y fallará; bloquea la campaña UNIT fnl0 en ese snapshot.  
   - **Acción:** eliminar snap 96 de la lista UNIT fnl0 o restringir subvolúmenes hasta confirmar disponibilidad en `/data2/users/olivia/shark_output/UNIT_1GPC/`.

2. **Snapshot 95 en `SharkUNIT1Gpc_fnl100` expandido de `[0]` a 64 subvolúmenes**  
   - **Evidencia:** diff en `generate_input_slurm.py`; `result.txt` muestra `prep_SharkUNIT1Gpc_fnl100_iz95_ivols0-63: ERROR` (antes solo ivol 0).  
   - **Impacto:** regresión operativa; el árbol Shark UNIT fnl100 no expone snap 95 completo.  
   - **Acción:** revertir a `[0]` o al subconjunto verificado.

### Importante

3. **`validate_hdf5_file` no usa `ending_file`**  
   - **Evidencia:** `src/generate_input.py:67` resuelve `except_path` con `config['ending_file']`, pero `src/validate.py:34` sigue usando `u.get_path(config['root'], ivol)` sin `ending`.  
   - **Impacto:** con `validate_files=True` (p. ej. snap 97 GP20UNIT1Gpc / SAGE_comparison), la validación puede comprobar un fichero distinto al que usa la generación, o fallar cuando la generación sería correcta.  
   - **Acción:** propagar `ending=config.get('ending_file')` en `validate.py`, igual que en `generate_input.py`.

4. **Rutas de salida renombradas a `Galform_to_copy`**  
   - **Evidencia:** `get_GP20SU_config`, `get_GP20UNIT1Gpc_config` y Shark usan `/data21/users/vgonzalez/Data/Galform_to_copy/...` y `/data21/.../Shark/...`.  
   - **Impacto:** coherente con `run_setup` (`sam = 'Galform_to_copy'`), pero hay que asegurar que los scripts de ejecución manual no apunten al árbol antiguo `/home2/vgonzalez/Data/Galform/`.  
   - **Acción:** documentar el cambio de ruta en README o comentario de campaña.

5. **`result.txt` en raíz del repo (untracked)**  
   - **Evidencia:** fichero de resumen de jobs Slurm con trazas de error.  
   - **Impacto:** no debe commitearse; contiene rutas de cluster.  
   - **Acción:** añadir a `.gitignore` o borrar tras revisión.

### Opcional

6. **`generate_input_files.py` y `generate_input_slurm.py` mezclan config de campaña con código**  
   - Cambios de sim/snap/listas de jobs son operativos (GP20UNIT1Gpc_fnl0 iz90, listas QSO_evo). Aceptable para ejecución local, pero conviene no commitear listas de campaña en `main` sin PR dedicado.

7. **Comentarios obsoletos en `generate_input_slurm.py`**  
   - Bloques comentados extensos dificultan lectura; podrían eliminarse tras estabilizar la campaña.

---

## Alineación con la spec Griffin+19

| Requisito spec | Estado en `prep_gne_input` |
| --- | --- |
| Shark: `m_bh`, `bh_accretion_rate_hh/sb` | ✅ en `get_SharkSU_config` y `get_SharkUNIT1Gpc_config` |
| Shark: `rgas_bulge`, `mgas_bulge`, `mstars_bulge` | ✅ ya presentes; añadidos `rstar_bulge`, `rstar_disk` |
| Galform: `Lbol_AGN` en catálogo | ✅ en configs GP20 |
| Snapshots QSO_evo (65, 74, 81, 86) | ✅ rutas `QSO_evo/` en GP20SU y GP20UNIT fnl0/fnl100 |
| `ending_file` para HDF5 con sufijo `iz*` | ✅ snap 97 SAGE; falta en validación (hallazgo 3) |
| Alineación datasets ↔ units tras `rstar_*` | ✅ 28 datasets / 28 unidades en Shark SU y UNIT |

---

## Checklist

| Ítem | Estado |
| --- | --- |
| **Corrección** — lógica y edge cases | ⚠️ jobs UNIT iz96/iz95 fallan; validación desalineada |
| **Diseño** — coherencia con repo y spec | ✅ campos Shark/Galform cubren API GNE |
| **Secretos** — sin credenciales en diff | ✅ solo rutas de cluster públicas en el equipo |

---

## Acciones recomendadas (orden)

1. Quitar snap 96 de `SharkUNIT1Gpc_fnl0` y revertir iz95 fnl100 a subvolúmenes válidos.
2. Corregir `validate.py` para `ending_file`.
3. No commitear `result.txt`.
4. Verificar en cluster que las rutas `Galform_to_copy` existen y son escribibles antes de relanzar campaña completa.
