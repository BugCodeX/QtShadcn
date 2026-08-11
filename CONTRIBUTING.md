# Contributing to QtShadcn

Thank you for contributing. This guide covers the development environment, workflow, and conventions for QtShadcn.

---

## Development Environment

QtShadcn uses [`uv`](https://github.com/astral-sh/uv) and [`make`](https://www.gnu.org/software/make/). Python >= 3.11 is required.

Install all development dependencies:

```bash
make install-dev
```

The equivalent `uv` command is:

```bash
uv sync --extra dev
```

---

## Common Commands

| Command | Description |
| --- | --- |
| `make lint` | Run `ruff check` (report only) |
| `make format` | Run `ruff format` and `ruff check --fix` |
| `make type-check` | Run the `ty` type checker |
| `make test` | Run the `pytest` suite |
| `make test-cov` | Run tests with a coverage report |
| `make docs-serve` | Serve the docs locally at `http://127.0.0.1:8000` |
| `make gallery` | Run the widget gallery example |
| `make build` | Build the wheel and sdist distributions |
| `make clean` | Remove `dist/`, caches, `.coverage`, and other build artifacts |

Run `make help` for the full list of targets.

---

## Coding Conventions

- **Python**: >= 3.11
- **Package manager**: `uv`
- **Build backend**: Hatchling
- **Test runner**: pytest
- **Linter/formatter**: ruff
- **Type checker**: ty
- **Quotes**: double quotes
- **Indentation**: spaces
- **Line length**: 100 characters (E501 is ignored in ruff, but keep it reasonable)
- **Docstrings**: required on all public modules, classes, and functions
- **Imports**: isort-ordered; no star imports
- **Type annotations**: required on all public functions; `ty` must pass with no warnings
- **Tests**: no docstrings required in `tests/` or `examples/`

Run `make lint`, `make format`, and `make type-check` before opening a pull request.

---

## Architecture Rules

To keep the project maintainable, follow these rules when making changes:

- **Widget styles belong in `qtshadcn/styles/shadcn.jinja` only** — do not create new QSS files.
- **No hardcoded colors or pixel values in the Jinja template** — use tokens and helpers exclusively.
- **Token helpers** (`colors.alpha`, `colors.mix`, `radius.class_px`, `scale.spacing_px`) are the only way to transform token values.
- **Theme tokens are defined in XML** (`themes/default.xml`) — do not add Python-level color constants.
- **Public API surface**: `apply_theme()`, `get_theme()`, `ShadcnThemeTokens` — keep it minimal.

---

## Versioning

QtShadcn follows [semver](https://semver.org). The version is defined in `pyproject.toml` and must match the git tag (`vMAJOR.MINOR.PATCH`).

- `feat!:` commits → MAJOR bump
- `feat:` commits → MINOR bump
- `fix:` commits → PATCH bump

---

## Getting Help

Open an issue on GitHub at [https://github.com/BugCodeX/QtShadcn/issues](https://github.com/BugCodeX/QtShadcn/issues).
