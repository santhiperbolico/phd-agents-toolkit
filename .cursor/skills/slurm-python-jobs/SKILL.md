---
name: slurm-python-jobs
description: >-
  Ejecuta scripts Python pesados en Slurm siguiendo slurm/*.slurm del repo de
  producto activo, con un solo job activo por usuario y ejecución local para
  tareas ligeras (<3 min). Usar al lanzar pipelines, fits, plots masivos,
  sbatch, squeue o cuando el usuario pida correr algo en el cluster.
---

# Slurm — scripts Python

## Reglas críticas

1. **Un solo job Slurm a la vez.** Antes de `sbatch`, comprobar que el usuario
   no tiene jobs en cola o en ejecución. Si hay alguno, **no enviar** otro job:
   informar al usuario y esperar a que termine o cancelar explícitamente a
   petición suya.
2. **Solo Slurm para procesos pesados** (duración estimada **> 3 minutos**).
   Scripts rápidos (tests, plots pequeños, dry-runs) se ejecutan en local con
   el `.venv` del repo, nunca con `sbatch`.
3. **Reutilizar** un fichero existente en `slurm/` del repo activo cuando cubra
   el caso. Crear uno nuevo solo si no hay equivalente.

---

## Cuándo usar Slurm vs local

| Criterio | Acción |
| --- | --- |
| Estimación ≤ 3 min o tarea trivial | Local: activar venv + `python ...` |
| Pipeline completo, matching, fits, muchos subvolúmenes, etc. | Slurm vía `sbatch slurm/<job>.slurm` |
| Incertidumbre sobre duración | Preguntar al usuario o hacer un dry-run local breve |

---

## Preparación (repo activo)

1. Identificar la **raíz del repo de producto** (no `phd-agents-toolkit`).
2. Listar `slurm/*.slurm` y leer el más parecido al trabajo solicitado.
3. Detectar venv (`src/.venv` o `.venv` en raíz) → skill `venv-and-deps`.
4. Copiar del `.slurm` de referencia: cuenta, partición, `PYTHONPATH`, rutas
   de log y patrón `srun python ...`.

---

## Flujo antes de enviar

### 1. Comprobar mutex (obligatorio)

Desde la raíz del repo de producto:

```bash
cd <REPO_ROOT>
squeue -u "$USER" -h -o "%i %j %T"
```

- **Salida vacía** → se puede enviar un job.
- **Cualquier línea** (RUNNING, PENDING, etc.) → **abortar** el envío. Mostrar
  jobs activos y proponer esperar o cancelar a petición del usuario.

### 2. Elegir o crear el `.slurm`

- Si existe un fichero en `slurm/` para la tarea, usarlo.
- Si no, copiar la plantilla de [slurm-template.md](slurm-template.md) y los
  valores de un `.slurm` existente del mismo repo (cuenta, partición, venv,
  `PYTHONPATH`).

### 3. Preparar directorio de salida

El `.slurm` debe crear el directorio de logs si no existe:

```bash
mkdir -p output/<nombre_tarea>
```

### 4. Enviar y verificar

```bash
cd <REPO_ROOT>
sbatch slurm/<nombre>.slurm
squeue -u "$USER" -h -o "%i %j %T %M %l"
```

Anotar el `JOBID` devuelto por `sbatch`.

### 5. Seguimiento

```bash
squeue -j <JOBID>
tail -f output/<nombre_tarea>/<nombre>.out
tail -f output/<nombre_tarea>/<nombre>.log
```

No lanzar otro `sbatch` hasta que ese job desaparezca de `squeue`.

---

## Convenciones habituales (cluster Taurus / repos de doctorado)

Leer siempre un `.slurm` del repo antes de inventar valores. Patrón típico en
repos como `fnl_matching_error_reduction`:

- Cuenta: `-A 16cores`
- Partición: `--partition=all`, `--exclude=epi`
- CPUs por defecto: `16` (`OMP_NUM_THREADS=16`)
- `PYTHONPATH`: `<REPO_ROOT>/src` (si el repo usa layout `src/`)
- Venv: `source <REPO_ROOT>/.venv/bin/activate` (o `src/.venv` según el repo)
- Tiempo por defecto: `--time=30-00:00:00`
- Ejecutar con `srun python ...`, no `python` a secas tras las directivas SBATCH

---

## Cuándo NO usar esta skill

- Tests unitarios o pre-commit → local con `pytest-and-coverage` /
  `pre-commit-and-lint`.
- Instalación de dependencias → skill `venv-and-deps`.
- Varios jobs en paralelo → **prohibido** salvo instrucción explícita del
  usuario (y aun así advertir del riesgo de saturar el cluster).

---

## Salida esperada

- Decisión documentada: local vs Slurm y por qué (>3 min o no).
- Resultado de `squeue` antes del envío (mutex OK).
- Comando `sbatch` ejecutado y `JOBID`.
- Rutas de `.out` / `.log` para seguimiento.
- Si el mutex falla: jobs bloqueantes listados, sin nuevo `sbatch`.

---

## Referencias

- Plantilla genérica: [slurm-template.md](slurm-template.md)
- Ejemplos reales: `slurm/` en la raíz del repo de producto activo
