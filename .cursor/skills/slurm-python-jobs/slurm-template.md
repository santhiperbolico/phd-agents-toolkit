# Plantilla Slurm

Copiar a `slurm/<nombre_descriptivo>.slurm` en el **repo de producto** y
sustituir marcadores. Antes de rellenar, leer un `.slurm` existente del mismo
repo para cuenta, partición y rutas absolutas.

```bash
#!/bin/bash
#SBATCH -A <ACCOUNT>
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --job-name=<JOB_NAME>
#SBATCH --error=output/<OUTPUT_DIR>/<JOB_NAME>.log
#SBATCH --output=output/<OUTPUT_DIR>/<JOB_NAME>.out
#SBATCH --partition=<PARTITION>
#SBATCH --exclude=<EXCLUDE_NODES>
#SBATCH --time=30-00:00:00

export OMP_NUM_THREADS=16
export PYTHONPATH=<REPO_ROOT>/src
source <REPO_ROOT>/<VENV_PATH>/bin/activate

mkdir -p output/<OUTPUT_DIR>

srun python <SCRIPT_PATH> <ARGS>
```

## Marcadores

| Marcador | Ejemplo (`fnl_matching_error_reduction`) |
| --- | --- |
| `<REPO_ROOT>` | `/home/arnes/.../fnl_matching_error_reduction` |
| `<VENV_PATH>` | `.venv` |
| `<ACCOUNT>` | `16cores` |
| `<PARTITION>` | `all` |
| `<EXCLUDE_NODES>` | `epi` |
| `<JOB_NAME>` | `fit_bphi` |
| `<OUTPUT_DIR>` | `fit_bphi_v1` |
| `<SCRIPT_PATH>` | `scripts/run_pipelines.py` |
| `<ARGS>` | `--fit-bphi --config-json configs/pipeline_run.json` |

## Variantes

- **Menos CPUs**: `--cpus-per-task=8`, `OMP_NUM_THREADS=8`.
- **Varios comandos en secuencia**: varias líneas `srun python ...`.
- **Más memoria** (descomentar si hace falta): `##SBATCH --mem=600000`.

## Envío

Tras comprobar mutex (`squeue -u "$USER" -h` sin filas):

```bash
cd <REPO_ROOT>
sbatch slurm/<nombre_descriptivo>.slurm
```
