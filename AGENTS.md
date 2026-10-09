# AGENTS.md — QtShadcn

Modern styling and theming framework for Qt/PySide6 applications, inspired by [shadcn/ui](https://ui.shadcn.com).

## Available Skills

Use these specialized skills for detailed patterns and strict project conventions:

| Skill | Description | Location |
| --- | --- | --- |
| `numpy-docstrings` | Strict NumPy-style docstrings and human-sounding comments | [.agents/skills/numpy-docstrings/SKILL.md](.agents/skills/numpy-docstrings/SKILL.md) |
| `naming-conventions` | Strict camelCase/PascalCase naming, no abbreviations, Qt properties/signals/slots | [.agents/skills/naming-conventions/SKILL.md](.agents/skills/naming-conventions/SKILL.md) |
| `commit-hygiene` | Conventional Commits, project-specific scopes, and atomic Git history | [.agents/skills/commit-hygiene/SKILL.md](.agents/skills/commit-hygiene/SKILL.md) |

---

## Auto-invoke Trigger Matrix

When performing any of these actions, **ALWAYS invoke the corresponding skill FIRST**:

| Action / Intent | Required Skill |
| --- | --- |
| Writing or modifying public modules, classes, functions, or methods | `numpy-docstrings` |
| Writing inline code comments or documenting architectural decisions | `numpy-docstrings` |
| Declaring or renaming functions, methods, variables, or parameters | `naming-conventions` |
| Declaring or refactoring Qt signals, slots, or event handlers | `naming-conventions` |
| Implementing Qt properties (`Property(...)`), getters, or setters | `naming-conventions` |
| Defining enum classes, enum members, or global constants | `naming-conventions` |
| Reviewing code for naming consistency or abbreviation violations | `naming-conventions` |
| Creating, reviewing, drafting, or staging Git commits | `commit-hygiene` |
| Creating, drafting, or publishing release notes, changelogs, version tags, or GitHub Releases | `release-notes` |

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
├── __init__.py     # Public package exports
├── models.py       # Pydantic models: ShadcnTheme and ShadcnThemeTokens
├── exceptions.py   # QtShadcnError, ThemeParseError, ThemeRenderError, QtBindingError
├── common/         # Internal runtime modules
│   ├── binding.py      # Binding-neutral Qt shim (PySide6 / PyQt6)
│   ├── cache.py        # Theme cache persistence
│   ├── helpers.py      # Application, file, mtime, font, and token-override helpers
│   ├── icon.py         # Runtime themed SVG icon cache helpers
│   ├── renderer.py     # QSS stylesheet renderer
│   ├── stylesheet.py   # Public API: setThemeMode(), setTheme(), setStyleSheet(), etc.
│   ├── theme_mode.py   # Theme mode normalization and dark/light resolution
│   └── theme_parser.py # Internal XML parsing implementation
├── styles/
│   └── shadcn.jinja  # QSS template — the ONLY file for widget styles
├── themes/
│   └── default.xml   # Default light/dark token values
├── tokens/
│   ├── colors.py     # withAlpha(), blendColors() helpers
│   ├── radius.py     # resolveRadius() helper
│   └── scale.py      # resolveSpacing(), toSpacingInt()
├── resources/
│   ├── fonts/        # Bundled font files
│   └── icons/        # Bundled SVG icon sources

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

## Agent Workflows

- Use codegraph for refactors, code fixes and investigations, including in subagents and when working in worktrees; codegraph is workspace-scoped: in a worktree, run operation init before the first query there, and when a subagent cannot call codegraph, the parent session runs the query and passes the findings in the task handoff

---

## Coding Conventions

- **Docstrings**: required on all public modules, classes, and functions (pydocstyle enforced via ruff `D` rules)
- **Imports**: isort-ordered (`I` rules); no star imports
- **Quotes**: double quotes
- **Indent**: spaces
- **Line length**: 100 characters (E501 ignored in ruff, but keep it reasonable)
- **Type annotations**: required on all public functions; `ty` must pass with no warnings
- **Tests & Examples**: no docstrings required in `tests/` or `examples/`.
- **Git Commits**: NEVER run `git commit` without asking the user first. Always request explicit confirmation before creating any Git commit.
- **Type aliases**: use domain `TypeAlias` definitions (`Pixels`, `ColorLike`) from `_base.py` / `qmaterialyou` instead of repeating raw unions (`QColor | str | None`) across widget signatures.

## Architecture Rules

- **Widget styles belong in `qtshadcn/styles/shadcn.jinja` only** — do not create new QSS files
- **No hardcoded colors or pixel values in the Jinja template** — use tokens and helpers exclusively
- **Token helpers** (`Colors.withAlpha`, `Colors.blendColors`, `radius.resolveRadius`, `Scale.resolveSpacing`) are the only way to transform token values
- **Theme tokens are defined in XML** (`themes/default.xml`) — do not add Python-level color constants
- **Public API surface**: `qsettings`, `ThemeMode`, `setThemeMode()`, `toggleThemeMode()`,
  `themeMode()`, `isDarkTheme()`, `setTheme()`, `getTheme()`, `setStyleSheet()`,
  `getStyleSheet()`, `SystemThemeWatcher`, `ShadcnThemeTokens` — keep it minimal

---

## Versioning

Follows [semver](https://semver.org). Version is defined in `pyproject.toml` and must match the git tag (`vMAJOR.MINOR.PATCH`).

- `feat!:` commits → MAJOR bump
- `feat:` commits → MINOR bump
- `fix:` commits → PATCH bump
