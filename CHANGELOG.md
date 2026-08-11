# QtShadcn v0.1.0

## Breaking Changes

- Refactor `apply_theme()` to a keyword-driven signature. `ThemeConfig` is no longer part of the public API.
  - New signature: `apply_theme(app=None, theme_file=None, *, theme_mode="auto", custom_tokens=None, additional_qss=None, default_theme="dark")`.
  - `app` is now optional and falls back to `QApplication.instance()`; raises `QtShadcnError` when no instance exists.
  - `theme_file` replaces `ThemeConfig.theme_source_path`; `None` loads the packaged default theme.
  - `theme_mode` accepts `"auto"`, `"light"`, or `"dark"` as strings.
  - `custom_tokens` replaces per-palette overrides; mode-specific when top-level keys are `"light"`/`"dark"`.
  - `additional_qss` replaces `theme_custom`; appended to the base stylesheet as an inline string, `.qss` file, or `.jinja` file.
  - `default_theme` is used when `theme_mode="auto"` and `darkdetect.theme()` returns `None`.
  - The disk cache key now includes `custom_tokens` and `additional_qss`.

## What's New

- Add `theme_custom` field to `ThemeConfig` for custom Jinja/QSS snippets appended to the base stylesheet.
- Extend the shadcn QSS template with `QGroupBox` styling, `QPlainTextEdit` support, `QFontComboBox` grouping, rounded-full scale variants, and progress-bar labeled fixes. Button sizing now uses `scale=` instead of `size=`.
- Support only PySide6 and PyQt6 bindings; PySide2 and PyQt5 are no longer selected.

## Changes

- Rewrite the gallery example as a single-file application with embedded pages and new UI assets.
- Hardcode `__version__` in `qtshadcn/__init__.py` and synchronize it with `pyproject.toml` on every release.

## Verification

```bash
pip install qtshadcn==0.1.0
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.20

## What's New

- Added `QTabWidget` styling support with default pill tabs on a muted background and a `variant="line"` style with bottom/right indicators.
- Added a gallery page demonstrating default, line, vertical line, and disabled tab widgets.

## Changes

- Improved the default `QTabWidget` pane background, padding, and margin in `qtshadcn/styles/shadcn.jinja`.
- Updated the documentation link in the gallery window from `https://BugCodeX.github.io/QtShadcn/` to `https://qtshadcn.readthedocs.io/`.

## Fixes

- Resolved `ruff format --check` failure by reformatting multiline assert strings in `tests/test_renderer.py`.

## Verification

```bash
pip install qtshadcn==0.0.20
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.19

## What's New

- Added `QTabWidget` styling support with default pill tabs on a muted background and a `variant="line"` style with bottom/right indicators.
- Added a gallery page demonstrating default, line, vertical line, and disabled tab widgets.

## Fixes

- Improved the default `QTabWidget` pane background, padding, and margin in `qtshadcn/styles/shadcn.jinja`.
- Updated the documentation link in the gallery window from `https://BugCodeX.github.io/QtShadcn/` to `https://qtshadcn.readthedocs.io/`.

## Verification

```bash
pip install qtshadcn==0.0.19
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.18

## Fixes

- Split the `QDoubleSpinBox` gallery page out from `QSpinBox` for clearer examples.
- Rounded the hover state of spin-box step buttons.
- Restored the PyPI logo in the README/package metadata.

## Documentation

- Updated the roadmap and switched status markers to emoji checkmarks.
- Removed obsolete `make build` references from the docs.

## Verification

```bash
pip install qtshadcn==0.0.18
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.17

## What's New

- Added QSpinBox and QDoubleSpinBox styling support with themed step buttons and validation states.

## Fixes

- Installed `mkdocs-material` into the Read the Docs virtualenv to restore documentation builds.

## Verification

```bash
pip install qtshadcn==0.0.17
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.16

## What's New

- Added an AI assistant skill management system for project-specific skills.
- Added a richer gallery overview page with component navigation.
- Added a gallery logo, copy XML button, and wider sidebar.
- Redesigned the gallery theme editor with tabs and color rows.

## Documentation

- Migrated documentation hosting to Read the Docs.
- Added `skills/README.md` with setup, usage, and authoring guidance.
- Restructured README and added `CONTRIBUTING.md` and `RELEASE.md` guides.
- Added logo assets for docs and README.
- Updated `AGENTS.md` with the current project structure.
- Updated README with logo and shields badges.
- Removed `release.md` and updated roadmap navigation.

## Verification

```bash
pip install qtshadcn==0.0.16
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```
