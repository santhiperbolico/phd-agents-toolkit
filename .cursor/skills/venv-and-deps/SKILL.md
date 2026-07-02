---
name: venv-and-deps
description: >-
  Detecta la ubicación del .venv (habitual src/.venv; también válido en la raíz)
  y prepara los comandos de creación o pip install para que los ejecute el
  usuario en su terminal. Usar al preparar entorno local, .venv ausente o tras
  cambiar requirements.
---

# Virtualenv y dependencias

## Regla principal

**No ejecutes** en el terminal del agente:

- creación o recreación del venv (`python -m venv`, `python3.11 -m venv`, etc.);
- instalación de dependencias (`pip install`, `pip install -r`, `uv pip install`,
  `pip check`, etc.).

El output de esos comandos consume contexto innecesario. En su lugar:

1. Comprueba si el venv existe (p. ej. `test -d src/.venv` o `test -d .venv`).
2. Si falta o hay que reinstalar deps, **escribe los comandos listos para copiar**
   y pide al usuario que los ejecute en su terminal externa.
3. Continúa la tarea solo cuando el usuario confirme o el venv ya exista.

---

## Cuándo usar

- Comprobar si existe `.venv` en `src/` o en la raíz del repo de producto.
- El usuario pide preparar el entorno antes de codificar o testear.
- Tras cambiar `requirements*.txt` y hay que reinstalar dependencias.

## Cuándo NO usar

- Ejecutar tests → `pytest-and-coverage`.
- Linters → `pre-commit-and-lint`.

---

## 1. Ubicación del venv

En la mayoría de repos de investigación el venv está en **`src/.venv`** o en **`<repo>/.venv`** (raíz). Ambas ubicaciones son válidas; no mover ni recrear uno existente sin que el usuario lo pida.

**Detectar cuál usar (en este orden):**

1. Si existe **`src/.venv`** → usar ese.
2. Si no, si existe **`.venv` en la raíz del repo** → usar ese.
3. Si ninguno existe, la ubicación por defecto es **`src/.venv`** cuando hay
   carpeta `src/`; si no hay `src/`, la raíz del repo.

**Directorio de trabajo para comandos** (`pytest`, `pre-commit`): confírmalo leyendo la config del repo (`pyproject.toml`, `.github/workflows/`, `Makefile`) o la estructura de carpetas (`src/` vs raíz).

---

## 2. Verificar el venv (solo comprobación)

Comprobar existencia; **no crear ni instalar**:

```bash
# Desde la raíz del repo de producto — el agente puede usar test -d (output mínimo)
test -d src/.venv && echo "venv en src/.venv"
test -d .venv && echo "venv en raíz"
```

- Debe existir **uno** de los dos con **Python 3.11.x**.
- Si falta o versión incorrecta: **indícalo al usuario** y entrega los comandos de la sección 3; no los ejecutes tú.

---

## 3. Comandos para el usuario (no ejecutar en el agente)

Determina el comando correcto leyendo `.github/workflows/`, `Makefile` o `pyproject.toml`. Fallback: `requirements-dev.txt` → `requirements.txt` → `pyproject.toml` con extras.

**Crear venv** (adaptar `<repo>` y directorio según §1):

```bash
cd /ruta/al/repo-de-producto/src    # o /ruta/al/repo-de-producto/ si venv en raíz
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
```

**Instalar dependencias** (ejemplo; sustituir por el comando del pipeline):

```bash
cd /ruta/al/repo-de-producto/src    # mismo cd que el CI
source .venv/bin/activate             # o source ../.venv/bin/activate si venv en raíz
pip install -r requirements-dev.txt   # comando real del pipeline
```

Entrega al usuario el bloque concreto para su repo. Pide confirmación antes de seguir con tests, linters o código que dependa del entorno.

---

## Salida esperada

- Ruta del venv detectada (`src/.venv` o `.venv` en raíz) o aviso de que falta.
- Si falta o hay que instalar: **comandos copy-paste** para terminal del usuario.
- No volcar output de `pip install` ni de creación de venv en el contexto del agente.
