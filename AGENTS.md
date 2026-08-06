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
├── _qt.py          # Binding-neutral Qt shim (PySide6 / PyQt6 / PySide2 / PyQt5)
├── _icons.py       # Runtime themed SVG icon cache helpers
├── _shim.py        # Runtime Qt binding selection helpers
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
├── test_gallery.py
├── test_integration.py
├── test_models.py
├── test_page_registry.py
├── test_parser.py
├── test_renderer.py  # QSS output assertions
├── test_shim.py
├── test_theme_editor.py
├── test_tokens.py
└── test_version.py
```

---

## Development Commands

```bash
make install-dev   # set up the virtual environment (uv sync --extra dev)
make lint          # ruff check (report only)
make format        # ruff format + ruff check --fix
make type-check    # ty check
make test          # pytest
make test-cov      # pytest with HTML coverage report
make docs-serve    # live-reload docs at http://127.0.0.1:8000
make build         # wheel + sdist
make clean         # remove dist/, caches, .coverage
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

## Skills

These skills are active for this project. Read the corresponding `SKILL.md` before performing the related task.

| Skill              | When to use                                                  | Path                                                         |
|--------------------|--------------------------------------------------------------|--------------------------------------------------------------|
| `commit-hygiene`   | Any commit creation, message review, or branch cleanup       | [SKILL.md](.gemini/skills/commit-hygiene/SKILL.md)           |
| `release-notes`    | Creating or updating release notes for any version tag       | [SKILL.md](.gemini/skills/release-notes/SKILL.md)            |

---

## Versioning

Follows [semver](https://semver.org). Version is defined in `pyproject.toml` and must match the git tag (`vMAJOR.MINOR.PATCH`).

- `feat!:` commits → MAJOR bump
- `feat:` commits → MINOR bump
- `fix:` commits → PATCH bump
