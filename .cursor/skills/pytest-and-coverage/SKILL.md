---
name: pytest-and-coverage
description: >-
  Prepara comandos de pytest y cobertura, o crea/modifica tests siguiendo el
  layout del repo. Usar al validar tests o escribir tests; el usuario ejecuta
  pytest en su terminal.
---

# pytest — ejecutar y escribir tests

## Cuándo usar

**Ejecutar**

- Correr suite, módulo o test concreto.
- Depurar fallos (`-k`, `::test_nombre`; evitar `-x` en tests parametrizados).
- Comprobar cobertura y `fail_under` del repo.

**Escribir o modificar**

- Añadir tests para código nuevo o regresión.
- Ampliar cobertura de casos existentes.

## Cuándo NO usar

- Tests que dependen de un stack concreto del repo (framework, orquestador, settings propios) → seguir la skill o documentación de tests de **ese** repositorio.
- Solo linters o formato → skill `pre-commit-and-lint`.

---

## Entorno

- Ejecutar pytest desde **`src/`**.
- Venv habitual en `src/.venv`; también válido en la raíz del repo.
- Si falta venv o deps → skill `venv-and-deps`: comprobar existencia y **dar
  comandos al usuario**; no ejecutar `python -m venv` ni `pip install`.
- Asumir venv activo en terminal del usuario.

---

## A. Ejecutar tests

**No ejecutes `pytest` en el terminal del agente** (output largo, consume
contexto). Da los comandos al usuario; continúa según el resultado que reporte.
El agente **sí** puede escribir o modificar ficheros de test.

Antes de usar los ejemplos de abajo, revisa la **config de CI del repo**
(`.github/workflows/`, `Makefile`): cada repo puede definir su propio `cd`, exports, flags e invocaciones `pytest`. **Esos comandos del CI tienen prioridad** sobre los genéricos de esta sección.

### Comandos

Muchos repos traen **`--cov` en `pytest.ini`** (`addopts`); en ejecuciones
acotadas añade **`--no-cov`** para no fallar por umbral de cobertura.

```bash
pytest tests/test_modulo.py::test_caso --no-cov   # test unitario / acotado
pytest -k "fragmento_nombre" --no-cov
pytest tests/test_modulo.py --no-cov
pytest                                          # suite (cov si addopts lo incluye)
pytest --cov-report term-missing                # cobertura explícita en terminal
```

Para suite completa o validar `fail_under`, usar flags del pipeline o
`pytest.ini` (con `--cov`). Umbral en `.coveragerc` (`fail_under`).

### Marcadores por defecto

Muchos repos excluyen suites en `addopts`, p. ej. `-m "not migration_test"` o `-m "not benchmark"`. Para ejecutarlas:

```bash
pytest -m migration_test
```

### Reglas al ejecutar

- No asumir verde; el usuario debe ejecutar y reportar pass/fail.
- Preferir **`-k`** y **`--no-cov`** frente a **`-x`** en tests parametrizados
  (`-x` solo reporta el primer fallo de la parametrización).
- Respetar variables de entorno del repo (`DB_*`, `DJANGO_SETTINGS_MODULE`, etc.).

---

## B. Crear o modificar tests

### Alcance (solo lo pedido)

- Limitarse al test, fichero o comportamiento que el usuario haya pedido.
- **No** refactorizar, renombrar, reformatear ni «mejorar» otros tests del mismo módulo o del repo.
- **No** unificar fixtures, extraer helpers ni cambiar estilo ajeno al encargo salvo que el usuario lo pida explícitamente.
- Si al leer `conftest.py` ves mejoras posibles, mencionarlas en una línea; no aplicarlas sin permiso.

Lo específico de pytest (asserts, `parametrize`, fixtures, mocks) aplicar como en cualquier proyecto Python; aquí solo lo **propio del ecosistema**.

### Convenciones del repo (obligatorio)

1. **Ubicación:** no inventar layout. Buscar tests del módulo ya existentes (`src/tests/`, `src/test/`, `src/<modulo>/tests/`, etc.) y colocar el nuevo test en el mismo estilo.
2. **Fixtures:** revisar `conftest.py` del árbol antes de crear fixtures nuevas;
   reutilizar las existentes. **Un solo módulo de tests** → fixture en ese
   fichero; **varios módulos** → `conftest.py` (regla `python-naming`).
3. **Estilo:** mismo criterio que los ficheros vecinos (nombres `test_*`, imports, marcadores del repo).
4. **Marcadores y plugins:** respetar los definidos en `pytest.ini` / `conftest.py` del repo (p. ej. `django_db`, `vcr`, exclusiones en `addopts`).
5. **Cobertura:** el umbral está en `.coveragerc` (`fail_under`); no asumir un porcentaje fijo.

### Flujo

1. Localizar tests y `conftest.py` del área afectada.
2. Escribir o ajustar tests (misma lógica y herramientas que el resto del repo).
3. Entregar comandos de verificación al usuario:

```bash
pytest path/to/test_file.py::test_nuevo --no-cov
pytest path/to/test_file.py --no-cov
# o pytest -k "fragmento" --no-cov
```

4. Si el encargo pide cobertura de suite, omitir `--no-cov` y usar flags de `pytest.ini`/pipeline.

### Reglas al escribir

- **Diff mínimo:** solo líneas necesarias para el test pedido; el resto del fichero intacto.
- No tests triviales ni mocks de lógica interna sin necesidad.
- Tras cambiar tests, **dar comandos** para validar al menos el fichero tocado.
- Integración pesada o suites excluidas por defecto: comprobar si el repo documenta variables o marcadores extra.

---

## Salida esperada

**Ejecutar:** comandos copy-paste; qué debe reportar el usuario (pass/fail, cobertura vs `fail_under`).

**Escribir:** ficheros tocados; qué comportamientos cubren; comandos pytest para que el usuario valide.
