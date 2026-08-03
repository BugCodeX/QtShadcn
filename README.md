# QtShadcn

> Modern styling and theming framework for Qt/PySide6 applications, inspired by [shadcn/ui](https://ui.shadcn.com).

QtShadcn loads a local **XML theme file** containing `<light>` and `<dark>` palettes, resolves the design tokens, renders a QSS stylesheet via Jinja2, and applies it to your `QApplication` in one call.

---

## Features

- 🎨 **Light & dark palettes** — single XML file, both modes
- 🔄 **Auto mode** — follows the OS theme via `darkdetect`
- 🖋 **Custom fonts** — drop font files in the package `fonts/` directory
- ⚡ **Disk cache** — theme is re-rendered only when the source file changes
- ✅ **App-provided Qt runtime** — install PySide6 in your application environment

---

## Requirements

- Python ≥ 3.11
- PySide6 ≥ 6.11 (provided by your application environment)

---

## Installation

```bash
# Install QtShadcn from PyPI
pip install qtshadcn

# Or with uv
uv add qtshadcn
```

QtShadcn does not bundle PySide6. Install PySide6 in your application environment so your app controls the Qt runtime version:

```bash
pip install PySide6
# or
uv add PySide6
```

---

## Distribution

Python distributions are published to [PyPI](https://pypi.org/project/qtshadcn/). GitHub Releases are used for release notes and tags only; wheel and source distribution files should not be attached there once PyPI publishing is active.

---

## Maintainer Release Checklist

Configure PyPI Trusted Publishing before the first release:

| PyPI field | Value |
| --- | --- |
| Project | `qtshadcn` |
| Owner | `BugCodeX` |
| Repository | `QtShadcn` |
| Workflow | `publish-pypi.yml` |
| Environment | `pypi` |

Release path:

1. Confirm the version in `pyproject.toml` matches the next semver release.
2. Push a tag named `vMAJOR.MINOR.PATCH` for future releases.
3. Let `.github/workflows/publish-pypi.yml` build and publish the wheel and sdist to PyPI.
4. For an already-pushed tag such as `v0.0.5`, run the workflow manually from GitHub Actions after Trusted Publishing is configured.
5. Use GitHub Releases for notes/tags, not `.whl` or `.tar.gz` assets.

If the PyPI publish succeeds for `v0.0.5`, existing wheel and source distribution assets can be removed from GitHub Releases.

Local Twine upload should be treated as an explicit fallback only, not the default release path:

```bash
make build
uv run --extra dev twine upload dist/*
```

---

## Quick Start

```python
import sys
from PySide6.QtWidgets import QApplication, QLabel
from qtshadcn import ThemeConfig, apply_theme

app = QApplication(sys.argv)

config = ThemeConfig(
    theme_source_path="path/to/my_theme.xml",
    theme_mode="auto",  # "auto" | "light" | "dark"
)

tokens = apply_theme(app, config)
print(tokens.primary)  # resolved hex color

label = QLabel("Hello, QtShadcn!")
label.show()
sys.exit(app.exec())
```

---

## Theme File Format

A QtShadcn theme is a plain XML file with two palette sections:

```xml
<theme>
  <light>
    <background>#ffffff</background>
    <foreground>#020617</foreground>
    <primary>#0f172a</primary>
    <primary_foreground>#f8fafc</primary_foreground>
    <secondary>#f1f5f9</secondary>
    <secondary_foreground>#0f172a</secondary_foreground>
    <accent>#f1f5f9</accent>
    <accent_foreground>#0f172a</accent_foreground>
    <muted>#f1f5f9</muted>
    <muted_foreground>#64748b</muted_foreground>
    <destructive>#ef4444</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#e2e8f0</border>
    <input>#e2e8f0</input>
    <ring>#0f172a</ring>
    <radius>8px</radius>
    <font_family>system-ui, sans-serif</font_family>
    <spacing>4px</spacing>
    <card>#ffffff</card>
    <card_foreground>#020617</card_foreground>
    <popover>#ffffff</popover>
    <popover_foreground>#020617</popover_foreground>
  </light>
  <dark>
    <!-- same tokens, dark values -->
  </dark>
</theme>
```

Unknown tokens are silently ignored so you can extend the format freely.

---

## API Reference

### `apply_theme(app, config) → ShadcnThemeTokens`

Parses the XML theme, renders the QSS stylesheet, and calls `app.setStyleSheet()`.

| Parameter | Type | Description |
| --- | --- | --- |
| `app` | `QApplication` | The running Qt application instance |
| `config` | `ThemeConfig \| None` | Theme configuration; `None` reloads from cache |

Returns the active `ShadcnThemeTokens` (light or dark, resolved).

### `get_theme() → ShadcnTheme | None`

Returns the full resolved theme (both palettes) from disk cache, or `None` if no theme has been applied yet.

### `ThemeConfig`

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `theme_source_path` | `str \| None` | `None` | Path to the `.xml` theme file |
| `theme_mode` | `"auto" \| "light" \| "dark"` | `"auto"` | Palette selection strategy |

### `ShadcnThemeTokens`

Immutable Pydantic model with one field per design token (`background`, `primary`, `border`, `radius`, `font_family`, …). Every token is required in both XML palettes; missing tokens raise `ThemeParseError`.

---

## Development

This project uses [`uv`](https://github.com/astral-sh/uv) and [`make`](https://www.gnu.org/software/make/).

```bash
make install-dev   # set up the virtual environment
make lint          # ruff check (report only)
make format        # ruff format + ruff check --fix
make type-check    # ty check
make test          # pytest
make test-cov      # pytest with HTML coverage report
make docs-serve    # live-reload docs at http://127.0.0.1:8000
make build         # wheel + sdist
make publish       # show PyPI Trusted Publishing guidance
make clean         # remove dist/, caches, .coverage
```

Run `make help` to see the full list.

---

## License

MIT
