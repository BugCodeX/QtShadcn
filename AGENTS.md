# AGENTS.md — QtShadcn

Modern styling and theming framework for Qt/PySide6 applications, inspired by [shadcn/ui](https://ui.shadcn.com).

---

## Project Overview

QtShadcn loads a local **XML theme file** with `<light>` and `<dark>` palettes, resolves design tokens, renders a QSS stylesheet via Jinja2, and applies it to a `QApplication` in one call.

- **Language**: Python ≥ 3.11
- **Package manager**: `uv`
- **Build backend**: Hatchling
- **Test runner**: pytest
- **Linter/formatter**: ruff (line length: 100)
- **Type checker**: ty
- **Docs**: MkDocs + Material theme

---

## Repository Structure

```text
qtshadcn/
├── app.py          # Public API: apply_theme(), get_theme(), ThemeConfig
├── models.py       # Pydantic models: ShadcnTheme, ShadcnThemeTokens, ThemeConfig
├── parser.py       # XML theme parser (public façade)
├── _parser.py      # Internal XML parsing implementation
├── _qt.py          # Binding-neutral Qt shim (PySide6 / PyQt6)
├── _icons.py       # Runtime themed SVG icon cache helpers
├── styles/
│   └── shadcn.jinja  # QSS template — the ONLY file for widget styles
├── themes/
│   └── default.xml   # Default light/dark token values
├── tokens/
│   ├── colors.py     # alpha(), mix() helpers
│   ├── radius.py     # class_px() helper
│   └── scale.py      # spacing_px(), spacing_int(), TEXT_*, FONT_WEIGHT_* constants
└── fonts/            # Bundled font files
examples/
└── gallery/          # Modular widget gallery with live theme editor
    ├── main.py
    ├── window.py
    ├── theme_editor.py
    ├── page_selector.py
    ├── pages/
    │   ├── _helpers.py
    │   └── ...       # One page per styled widget
    └── ...
tests/
├── test_app.py
├── test_exceptions.py
├── test_integration.py
├── test_models.py
├── test_parser.py
├── test_renderer.py  # QSS output assertions
├── test_shim.py
├── test_tokens.py
└── test_version.py
```

---

## Development Commands

```bash
make install-dev   # set up the virtual environment (uv sync --extra dev)
make setup-hooks   # install pre-commit git hooks
make lint          # ruff check (report only)
make format        # ruff format + ruff check --fix
make type-check    # ty check
make test          # pytest
make test-pyqt6    # pytest with PyQt6 binding
make test-cov      # pytest with HTML coverage report
make docs-serve    # live-reload docs at http://127.0.0.1:8000
make clean         # remove dist/, caches, .coverage

pre-commit install                      # install git hooks
pre-commit run --all-files              # run hooks manually
pre-commit run pytest --hook-stage pre-push  # run pytest hook manually
pre-commit run uv-lock                  # validate uv.lock is up to date
pre-commit run renovate-config-validator # validate Renovate config
```

---

## Coding Conventions

- **Docstrings**: required on all public modules, classes, and functions (pydocstyle enforced via ruff `D` rules)
- **Imports**: isort-ordered (`I` rules); no star imports
- **Quotes**: double quotes
- **Indent**: spaces
- **Line length**: 100 characters (E501 ignored in ruff, but keep it reasonable)
- **Type annotations**: required on all public functions; `ty` must pass with no warnings
- **Tests**: no docstrings required in `tests/` or `examples/`

---

## Architecture Rules

- **Widget styles belong in `qtshadcn/styles/shadcn.jinja` only** — do not create new QSS files
- **No hardcoded colors or pixel values in the Jinja template** — use tokens and helpers exclusively
- **Token helpers** (`colors.alpha`, `colors.mix`, `radius.class_px`, `scale.spacing_px`) are the only way to transform token values
- **Theme tokens are defined in XML** (`themes/default.xml`) — do not add Python-level color constants
- **Public API surface**: `apply_theme()`, `get_theme()`, `ThemeConfig`, `ShadcnThemeTokens` — keep it minimal

---

## Versioning

Follows [semver](https://semver.org). Version is defined in `pyproject.toml` and must match the git tag (`vMAJOR.MINOR.PATCH`).

- `feat!:` commits → MAJOR bump
- `feat:` commits → MINOR bump
- `fix:` commits → PATCH bump
## Available Skills

Use these skills for detailed patterns on-demand:

### Generic Skills (Any Project)

| Skill | Description | URL |
|-------|-------------|-----|
| `commit-hygiene` | Trigger: commit, git commit, conventional commit, branch cleanup. Enforce conventional commits and publishing approval for QtShadcn. | [SKILL.md](skills/commit-hygiene/SKILL.md) |
| `pytest` | Trigger: pytest tests, pytest coverage, fixtures, mocking, markers, parametrize, test discovery. Write idiomatic Python pytest tests and test helpers. | [SKILL.md](skills/pytest/SKILL.md) |
| `skill-creator` | Trigger: new skills, agent instructions, documenting AI usage patterns. Create LLM-first skills with valid frontmatter. | [SKILL.md](skills/skill-creator/SKILL.md) |
| `skill-improver` | Trigger: improve skills, audit skills, refactor skills, skill quality. Audit and upgrade existing LLM-first skills. | [SKILL.md](skills/skill-improver/SKILL.md) |

### QtShadcn Specific Skills

| Skill | Description | URL |
|-------|-------------|-----|
| `release-notes` | Trigger: release, release notes, changelog, tag, version. Run the QtShadcn release process: draft notes, verify version, create tag and GitHub Release. | [SKILL.md](skills/release-notes/SKILL.md) |
| `skill-sync` | Syncs skill metadata to AGENTS.md Available Skills sections. Trigger: When updating skill metadata (metadata.scope/metadata.auto_invoke), regenerating Available Skills tables, or running ./skills/skill-sync/assets/sync.py (including --dry-run/--scope). | [SKILL.md](skills/skill-sync/SKILL.md) |

### Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action | Skill |
|--------|-------|
| After creating/modifying a skill | `skill-sync` |
| Auditing or improving existing skills | `skill-improver` |
| Checking pytest coverage or test discovery | `pytest` |
| Cleaning up or reorganizing branches | `commit-hygiene` |
| Creating a new skill or AI agent instructions | `skill-creator` |
| Creating or amending a git commit | `commit-hygiene` |
| Creating or updating release notes | `release-notes` |
| Documenting reusable AI usage patterns | `skill-creator` |
| Generating a changelog or version tag | `release-notes` |
| Preparing a QtShadcn release | `release-notes` |
| Pushing commits, tags, or GitHub releases | `commit-hygiene` |
| Refactoring or normalizing SKILL.md files | `skill-improver` |
| Regenerate AGENTS.md Available Skills tables (sync.py) | `skill-sync` |
| Troubleshoot why a skill is missing from AGENTS.md | `skill-sync` |
| Working with test fixtures, mocking, or markers | `pytest` |
| Writing a conventional commit message | `commit-hygiene` |
| Writing, reviewing, or running Python pytest tests | `pytest` |
