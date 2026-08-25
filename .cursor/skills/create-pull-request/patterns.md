# Patrones — crear pull request (PhD)

## PR description template

Adapt to the task; keep sections even if some are brief. **Write in English.**

```markdown
## Objective

{What problem this solves or what capability it adds. Research or technical
context. Reference acceptance criteria from a GitHub issue or local spec if
they exist.}

## Changes

- {Concrete change 1 — module or behaviour}
- {Change 2}
- {Tests added or updated, if applicable}

## Outcome

{What works after merge: scripts, pipelines, metrics, data contracts, etc.
Observable behaviour for reviewers.}

## References

- **GitHub issue:** [#42](https://github.com/{owner}/{repo}/issues/42)
- **Local docs:** `docs/haloscope-pipeline.md` (if applicable)

## Test plan

- [ ] {Command or scenario 1 — e.g. pytest for touched module}
- [ ] {Manual validation or integration run}
- [ ] {Regression in related flow}
```

If there is no GitHub issue, omit that line. If there is no local doc, omit or
state «context from agent session only».

Add `Closes #42` at the top or bottom when the PR should auto-close the issue.

---

## Sources for Objective and Outcome

| Source | What to extract |
| --- | --- |
| GitHub issue (`issue_read`) | Title, body, acceptance criteria, comments |
| `README.md`, `docs/`, `specs/` | Scope, methodology, constraints |
| `notes/` in repo | Design decisions, experiment logs |
| Agent thread | Actual implementation vs plan, justified deviations |

**Outcome** must describe the state **after** merge, not repeat the file diff.

---

## Create PR on GitHub

### `gh` CLI (preferred)

After push with `-u`:

```bash
gh pr create \
  --base main \
  --head "$(git branch --show-current)" \
  --title "[#42] Add haloscope scan pipeline" \
  --body "$(cat <<'EOF'
## Objective
...
Closes #42
EOF
)"
```

Use `--base master` if the repo default branch is `master`.

Check for an existing open PR from the same branch:

```bash
gh pr list --head "$(git branch --show-current)"
```

### GitHub MCP (`user-github`)

```json
{
  "owner": "your-org",
  "repo": "your-research-repo",
  "title": "[#42] Add haloscope scan pipeline",
  "head": "feature/42-haloscope-scan",
  "base": "main",
  "body": "## Objective\n\n...\n\nCloses #42"
}
```

Tool: `create_pull_request`.

Obtain `owner` and `repo` from `git remote -v`
(e.g. `git@github.com:owner/repo.git`).

### PR template in repo

Before writing the body, check:

```bash
find .github -iname '*pull_request*' 2>/dev/null
```

If a template exists, follow its structure but keep content in English.

---

## Measure diff size

```bash
BASE=main
git fetch origin
ADDED=$(git diff --numstat "origin/${BASE}...HEAD" | awk '{a+=$1} END {print a+0}')
DELETED=$(git diff --numstat "origin/${BASE}...HEAD" | awk '{d+=$2} END {print d+0}')
TOTAL=$((ADDED + DELETED))
echo "Added: $ADDED, deleted: $DELETED, total: $TOTAL"
```

Automatic code review threshold: **total > 100**.

---

## Pre-commit and pytest (step 2)

### When to run

| Tool | Condition |
| --- | --- |
| Pre-commit | Diff includes `.py` or other files covered by repo hooks |
| Pytest | Changes in `tests/` or in Python package code under test |

### Pre-commit (diff scope)

```bash
FILES=$(git diff --name-only "origin/${BASE}...HEAD" | tr '\n' ' ')
pre-commit run --files $FILES
```

Run from repo root or `src/` per `pre-commit-and-lint` and
`.pre-commit-config.yaml` location.

### Pytest (related tests)

```bash
pytest tests/path/test_module.py --no-cov
```

Derive test paths from the diff: same subtree under `tests/` as the modified
module under `src/` or package root. For broad changes, run the smallest folder
that covers the touched area.

---

## Base branch (merge target)

| Work type | Typical target |
| --- | --- |
| Feature | `main` |
| Fix | `main` |
| Docs | `main` |

Some older repos use `master`. Confirm with:

```bash
git remote show origin | sed -n '/HEAD branch/s/.*: //p'
```

See full branching rules in `git-workflow`.

---

## Detect GitHub issue number

| Signal | Example |
| --- | --- |
| Branch name | `feature/42-haloscope`, `fix/17-catalog-timeout` |
| Commit message | `Fixes #42`, `Closes #17` |
| User thread | «para el issue 42», «closes #42» |

If ambiguous, ask the user before linking in the PR title or body.
