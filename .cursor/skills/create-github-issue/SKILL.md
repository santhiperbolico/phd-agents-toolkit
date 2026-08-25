---
name: create-github-issue
description: >-
  Redacta y publica issues de GitHub con estructura Summary / Background /
  Target behaviour (flujo, tablas de config y salida). Usar cuando el usuario
  pida crear, abrir o redactar una issue en GitHub, definir alcance de un
  encargo o formalizar comportamiento objetivo antes de implementar.
---

# Crear issue de GitHub (repos PhD)

Orquesta la redacción y publicación de issues con una plantilla **breve y
orientada al comportamiento**. El detalle de implementación (requisitos R1–Rn,
fases, edge cases) puede vivir en docs locales; la issue queda como contrato
de alto nivel.

**Idioma de la issue:** título y cuerpo siempre en **inglés** (regla
`language-conventions`). Las respuestas al usuario siguen en castellano.

## Cuándo usar

- El usuario pide crear, abrir o redactar una issue en GitHub.
- Hay que formalizar alcance o comportamiento objetivo antes de codificar.
- Se menciona «abrir issue», «crear ticket» o «definir target behaviour».

## Cuándo NO usar

- Crear o actualizar PR → `create-pull-request`.
- Solo commit o rama sin issue → `git-workflow`.
- Tareas personales en Notion → `notion-phd-tasks`.
- Issue ya existe y solo hay que implementar → leer con `issue_read` y seguir.

---

## Flujo operativo (orden obligatorio)

```
0. Preparación (repo, duplicados, permisos)
        ↓
1. Recopilar contexto (hilo, código, docs locales)
        ↓
2. Redactar issue (inglés, plantilla simplificada)
        ↓
3. Revisar con el usuario (borrador) — opcional si el texto ya está claro
        ↓
4. Publicar en GitHub (solo con permiso explícito)
        ↓
5. Opcional: guardar copia local y enlace en Notion
```

No publicar en GitHub sin permiso explícito del usuario.

---

### 0. Preparación

Determinar **owner/repo** destino:

| Escenario | Repo destino |
| --- | --- |
| Issue en repo canónico (upstream) | `galform/repo`, `org/repo`, etc. |
| Issue en fork personal | `origin` del fork (menos habitual) |

Buscar duplicados antes de crear:

```bash
gh issue list --repo {owner}/{repo} --search "keywords" --state all --limit 10
```

O MCP `user-github` → `search_issues` con términos del encargo.

---

### 1. Recopilar contexto

| Fuente | Qué extraer |
| --- | --- |
| Hilo del agente | Objetivo, motivación, comportamiento deseado |
| Código existente | Nombres de funciones, flags, rutas parciales ya implementadas |
| `docs/`, `notes/` | Spec ampliada (no copiar entera a la issue) |
| Issues relacionadas | Alcance excluido, dependencias entre repos |

**Principio:** la issue resume el **qué** y el **comportamiento objetivo**; el
**cómo** detallado (checklists R1–Rn, fases, edge cases) va en docs locales si
hace falta.

---

### 2. Redactar la issue

Usar la plantilla de [patterns.md](patterns.md). Secciones obligatorias:

1. **Summary** — qué se integra o cambia; estado parcial en el código; límites
   de alcance (repos relacionados fuera de scope).
2. **Background / motivation** — por qué importa (ciencia, regresión, contrato
   de datos).
3. **Target behaviour** — especificación observable:
   - subsección de **flujo** (pasos numerados del API o pipeline principal);
   - tabla de **configuración** (parámetros y significado);
   - tabla de **salida** (HDF5, ficheros, columnas, API) cuando aplique.

Separar secciones con `---` entre Summary, Background y Target behaviour.

**Título:** descriptivo, ≤72 caracteres si es posible; sin punto final.
Incluir referencia breve al dominio (p. ej. método, flag, módulo).

---

### 3. Revisar con el usuario

Mostrar título y cuerpo completos antes de publicar salvo que el usuario haya
pedido crear la issue directamente con el texto ya acordado.

---

### 4. Publicar en GitHub

**Preferido:** `gh` CLI (mismo patrón que `create-pull-request`):

```bash
gh issue create \
  --repo {owner}/{repo} \
  --title "{title}" \
  --body "$(cat <<'EOF'
{body markdown}
EOF
)"
```

**Alternativa:** MCP `user-github` → `issue_write` con `method: create`,
`owner`, `repo`, `title`, `body`.

Tras crear, devolver la **URL** de la issue.

---

### 5. Copia local y Notion (opcional)

- Guardar borrador o copia en `docs/{proyecto}/issue-description.md` o
  `notes/` del repo activo si el usuario lo pide o ya existe convención.
- Enlazar en Notion (`notion-phd-tasks`) con propiedad **GitHub Issue** si el
  encargo está registrado allí.

---

## Reglas críticas

- **Inglés** en título y cuerpo.
- **Brevedad:** no incluir en la issue checklists de requisitos, fases de
  implementación ni tablas de bugs conocidos — salvo petición explícita.
- **Target behaviour** describe el estado **después** del merge, no el diff.
- **Alcance:** declarar repos o PRs relacionados **fuera de scope** en Summary.
- **Duplicados:** buscar antes de crear.
- **Permisos:** publicar solo con permiso explícito; nunca en nombre del usuario
  sin confirmación.

---

## Integración con otras skills

| Necesidad | Skill / herramienta |
| --- | --- |
| PR que cierra la issue | `create-pull-request` |
| Ramas y commits | `git-workflow` |
| Spec local amplia | `phd-local-docs` |
| Leer issue existente | MCP `issue_read` |
| Tarea Notion | `notion-phd-tasks` |

---

## Salida esperada

- Título y cuerpo redactados en inglés (mostrados al usuario).
- URL de la issue creada (si se publicó).
- Indicación de docs locales ampliados (si aplica).

---

## Checklist

- [ ] Owner/repo correcto y sin issue duplicada
- [ ] Summary con alcance y estado parcial en código
- [ ] Background con motivación en una frase o párrafo corto
- [ ] Target behaviour con flujo numerado y tablas cuando aplique
- [ ] Texto en **inglés**; secciones separadas con `---`
- [ ] Permiso explícito antes de `gh issue create` / `issue_write`
- [ ] URL devuelta al usuario

## Referencias

- [Plantilla y convenciones](patterns.md)
- [Ejemplo real (GNE #37)](examples.md)
