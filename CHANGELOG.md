# QtShadcn v0.5.0

## Changes

- **Breaking:** renamed `SystemThemeListener` to `SystemThemeWatcher`.
- Moved bundled icon sources and font files under `qtshadcn/resources/`.
- `ThemedIconManager` now loads SVG icon sources from package resources via `importlib.resources`.
- `_add_fonts()` loads fonts from `qtshadcn.resources.fonts` so assets work when installed as a wheel.
- Normalized QSS template helpers: `icons` -> `Icons`, `radius` -> `Radius`.
- Renamed `ThemedIconManager` methods to `getIconUrl` and `renderSliderThumb`.

## Verification

```bash
pip install qtshadcn==0.5.0
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

---

# QtShadcn v0.4.0

## Changes

- Modernized theme engine internals.
- Modernized token helpers and added typography tokens.
- Updated default theme and QSS template.
- Consolidated font bundles with Inter, updated Roboto, and removed italic/condensed variants.
- Updated guides and examples.

## Verification

```bash
pip install qtshadcn==0.4.0
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

---

# QtShadcn v0.3.0

## Breaking Changes

- Removed `apply_theme()` and `get_theme()` from the public API; use `setTheme()` and `getTheme()` instead.
- Removed the internal `cache.py` module; theme caching is no longer part of the public contract.

## What's New

- Added a persistent config system via a `qsettings` singleton for storing theme preferences across sessions.
- Added a 3-concept stylesheet API with a full rendering pipeline (`setStyleSheet`, `getStyleSheet`, `setTheme`, `getTheme`).
- Added `SystemThemeListener` for automatic OS-level light/dark theme reactivity.
- Exported all new public symbols from the package root.

## Fixes

- Made `toggleThemeMode()` deterministic when no mode is set.
- Set light mode explicitly in XML theme tests to avoid environment-dependent failures.

## Verification

```bash
pip install qtshadcn==0.3.0
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

---

# QtShadcn v0.2.0


## Breaking Changes

- Migrated the Qt binding layer from the internal `qtshadcn/common/binding.py` shim to `qtpy>=2.4.0`.
- Added support for `PySide2` and `PyQt5` alongside `PySide6` and `PyQt6`.
- Removed the `QTSHADCN_BINDING` environment variable; use `QT_API` (`pyside6`, `pyqt6`, `pyside2`, `pyqt5`) instead.
- Removed `qtshadcn.common.binding` and `qtshadcn.binding_name`; use `qtpy.API_NAME` if needed.

## What's New

- `qtpy` is now a mandatory runtime dependency.
- CI runs a four-binding matrix (`pyside6`, `pyqt6`, `pyside2`, `pyqt5`) plus a no-binding error-path job.
- Gallery example uses a per-binding `loadUi` helper (PySide `QUiLoader`, PyQt `uic.loadUi`).

## Changes

- Internal Qt imports now come from `qtpy` instead of `qtshadcn.common.binding`.
- `QtBindingError` messages now reference `QT_API` and all four supported bindings.
- README and `docs/getting-started.md` document the new binding model.

## Fixes

- Fixed RCC binary lookup casing for capitalized `qtpy.API_NAME` values.
- Fixed Qt6-only mouse-event APIs so the gallery window drag works on Qt5 bindings.
- Narrowed `ImportError` handling in `qtshadcn.__init__` to qtpy-specific binding errors.

## Verification

```bash
pip install qtshadcn==0.2.0
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.1.1

## Changes

- Reorganize internal implementation modules into `qtshadcn/common/` and split `app.py` into focused modules (`theme.py`, `renderer.py`, `cache.py`, `theme_mode.py`, `helpers.py`). Rename `_qt.py`, `_parser.py`, and `_icons.py` to `common/binding.py`, `common/theme_parser.py`, and `common/icon.py`.
- Public API remains unchanged; `from qtshadcn import apply_theme, get_theme` continues to work.

## Verification

```bash
pip install qtshadcn==0.1.1
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

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
