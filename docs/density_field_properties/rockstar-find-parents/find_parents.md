# ROCKSTAR `find_parents`: host halos (PID)

**Contexto:** post-proceso sobre catálogos Rockstar `.list` para asignar el **halo anfitrión** (host) de cada subestructura. La utilidad añade la columna **PID** (*parent ID*): identificador del halo principal que contiene al halo dado según la jerarquía espacial (vecinos en volumen, ordenados por `vmax` / radio de virial).

**Código:** utilidad C en el árbol Rockstar (`util/find_parents.c`), que incluye la lógica de `parents.c` y un árbol espacial `fast3tree`. No forma parte del merger Rockstar en sí; se ejecuta **después** de tener el catálogo.

**Relación con catálogos podados:** si corres Rockstar en varios snapshots, suele generarse una versión podada `out_AAA.list` (Rockstar comprueba en el snapshot siguiente si el halo sigue existiendo y no es espurio). Para esos ficheros conviene pasar `find_parents` para disponer de PIDs coherentes con la lista podada.

## Ejecutable (Taurus, UNIT)

```text
/home/adrian/UNIT_PNG/rockstar_old/rockstar/util/find_parents
```

En `util/` no hay fichero de configuración: solo fuentes, el binario y `to_run_find_parents` (comentario de uso). La configuración del **run Rockstar** (box, snapshots, etc.) vive en `.cfg` en la raíz del repo Rockstar (`parallel.cfg`, `quickstart.cfg`, …), no en esta utilidad.

## Uso

```text
find_parents <hlist> <box_size>
```

| Argumento | Descripción |
| --- | --- |
| `hlist` | Catálogo de entrada (p. ej. `out_87.list` o `halos_0.0.ascii`). |
| `box_size` | Tamaño de la caja en las mismas unidades que las posiciones del catálogo (p. ej. `250` Mpc/h). Si se omite en código antiguo, el default compilado es `250`. |

La salida va a **stdout**: mismas columnas que la entrada más **PID** al final. Las líneas de cabecera `#` se reemiten; en la primera se añade el nombre de columna `PID`.

### Ejemplos

Síncrono, redirigiendo solo stdout:

```bash
./find_parents out_AAA.list BoxSize > /ruta/outp_AAA.list
```

En segundo plano, resistente al cierre de SSH (`nohup`), stdout y stderr al mismo fichero (sobrescribe si existe):

```bash
nohup ./find_parents halos_0.0.ascii BoxSize >& halosp_0.0.ascii &
```

**MN5 (snapshot 87, box 250):**

```bash
nohup /home/adrian/UNIT_PNG/rockstar_old/rockstar/util/find_parents \
  /data8/adrian/MN5/SEP_UNI/N2048_L250_fid/ROCKSTAR/outputs/out_87.list \
  250 \
  >& /data21/users/vgonzalez/Data/Rockstar/SU1/outp_87.list &
```

Comprobar que el proceso sigue vivo: `ps -p <PID>` (sustituir por el PID que imprime el shell al lanzar con `&`).

## Notas sobre la línea de comandos

- **`nohup`:** el proceso no recibe SIGHUP al cerrar la terminal; útil en jobs largos por SSH. No sustituye a Slurm.
- **`&`:** ejecución en background.
- **`>& archivo`:** redirige stdout y stderr al fichero en modo **sobrescritura**. Para acumular logs: `>>& archivo` o `>> archivo 2>&1`.

## Slurm (density_field_properties)

Job listo para FastPM MN5 `out_8.list` (box 1000 Mpc/h):

```bash
cd /home/arnes/santiago_arranz/density_field_properties
sbatch slurm/rockstar/find_parents_fastpm_mn5_out8.slurm
```

Escribe `output/rockstar_find_parents/fastpm_mn5_tfm/out_8_with_pid.list` (el directorio de mruiz no es escribible).

## Enlace con lectura de catálogos en Python

En [density_field_properties](https://github.com/computationalAstroUAM/density_field_properties), `RockstarCatalogReader` espera la columna estándar **pid** (índice 5 en el layout por defecto) cuando el fichero ya incluye padres. Si solo tienes `out_*.list` sin post-proceso, genera primero el catálogo con PID vía `find_parents` o usa un reader que no dependa de la jerarquía de subhalos.

**Origen de la nota operativa:** `notes/notas/example_find_parents.txt` (toolkit PhD).
