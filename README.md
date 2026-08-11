<p align="center">
  <img src="https://raw.githubusercontent.com/BugCodeX/QtShadcn/master/docs/source/logo.png" alt="QtShadcn logo" width="20%">
</p>

<h1 align="center">QtShadcn</h1>

<p align="center">
  <a href="https://pypi.org/project/qtshadcn/"><img src="https://img.shields.io/pypi/v/qtshadcn" alt="PyPI version"></a>
  <a href="https://pypi.org/project/qtshadcn/"><img src="https://img.shields.io/pypi/dm/qtshadcn" alt="PyPI downloads"></a>
  <a href="https://github.com/BugCodeX/QtShadcn/blob/master/LICENSE"><img src="https://img.shields.io/github/license/BugCodeX/QtShadcn" alt="License"></a>
  <a href="https://pypi.org/project/qtshadcn/"><img src="https://img.shields.io/pypi/pyversions/qtshadcn" alt="Python versions"></a>
  <img src="https://img.shields.io/badge/Platform-Win%20%7C%20Linux%20%7C%20macOS-blue" alt="Platform">
</p>

> Modern styling and theming framework for Qt/PySide and PyQt applications, inspired by [shadcn/ui](https://ui.shadcn.com).

QtShadcn loads a local **XML theme file** containing `<light>` and `<dark>` palettes, resolves the design tokens, renders a QSS stylesheet via Jinja2, and applies it to your `QApplication` in one call.

---

## Features

- **Light & dark palettes** — single XML file, both modes
- **Auto mode** — follows the OS theme via `darkdetect`
- **Binding neutral** — works with PySide6, PyQt6, PySide2, or PyQt5 via qtpy
- **Custom fonts** — drop font files in the package `fonts/` directory
- **Disk cache** — theme is re-rendered only when the source file changes
- **App-provided Qt runtime** — install the Qt binding your app already uses
- **Themed icons** — SVG check icons generated and cached at runtime

---

## Requirements

- Python >= 3.11
- One of: PySide6, PyQt6, PySide2, or PyQt5 (provided by your application environment)

---

## Installation

```bash
# Install QtShadcn from PyPI
pip install qtshadcn

# Or with uv
uv add qtshadcn
```

QtShadcn does not bundle a Qt binding. Install the binding your application already uses and
optionally set ``QT_API`` to select one when multiple bindings are present:

```bash
# PySide6 (recommended)
pip install PySide6
export QT_API=pyside6

# Or PyQt6
pip install PyQt6
export QT_API=pyqt6

# Or PySide2
pip install PySide2
export QT_API=pyside2

# Or PyQt5
pip install PyQt5
export QT_API=pyqt5
```

---

## Quick Start

```python
import sys
from qtpy import QtWidgets
from qtshadcn import apply_theme

app = QtWidgets.QApplication(sys.argv)

tokens = apply_theme(
    app,
    theme_file="path/to/my_theme.xml",
    theme_mode="auto",  # "auto" | "light" | "dark"
)
print(tokens.primary)  # resolved hex color

label = QtWidgets.QLabel("Hello, QtShadcn!")
label.show()
sys.exit(app.exec())
```

---

## Widget Gallery

Explore the supported widgets by running the gallery:

```bash
make gallery
```

The gallery includes a sidebar navigator, a light/dark toggle, and pages for every currently styled widget.

---

## Supported Styled Widgets

QtShadcn currently ships QSS for:

- `QWidget` — base background, foreground, and typography classes
- `QLabel` — typography and disabled state
- `QPushButton` — variants, sizes, and disabled states
- `QToolButton` — compact icon/action variants
- `QCheckBox` — toggle controls with themed check icons and disabled states
- `QRadioButton` — radio controls with themed checked icons
- `QLineEdit` — input states including focus, disabled, and invalid
- `QTextEdit` — textarea states including focus, disabled, and invalid
- `QComboBox` and `QFontComboBox` — dropdowns, popups, and invalid states
- `QProgressBar` — determinate, thin, and disabled states
- `QSlider` — horizontal, vertical, tick, and disabled states
- `QGroupBox` and `QFrame` — layout containers

See the [roadmap](docs/roadmap.md) for what is planned next.

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

### `apply_theme(app, theme_file, *, theme_mode, custom_tokens, additional_qss, default_theme) -> ShadcnThemeTokens`

Parses the XML theme, renders the QSS stylesheet, and calls `app.setStyleSheet()`.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `app` | `QApplication \| None` | `None` | The running Qt application instance |
| `theme_file` | `str \| None` | `None` | Path to the `.xml` theme file; `None` loads the default |
| `theme_mode` | `str` | `"auto"` | `"auto"`, `"light"`, or `"dark"` |
| `custom_tokens` | `dict[str, dict[str, str] \| str] \| None` | `None` | Token overrides (mode-specific when keys are `"light"`/`"dark"`) |
| `additional_qss` | `str \| None` | `None` | Inline Jinja snippet, `.qss` file path, or `.jinja` file path to append |
| `default_theme` | `str` | `"dark"` | Fallback mode when `theme_mode="auto"` and OS detection fails |

Returns the active `ShadcnThemeTokens` (light or dark, resolved).

### `get_theme() -> ShadcnTheme | None`

Returns the full resolved theme (both palettes) from disk cache, or `None` if no theme has been applied yet.

### `ShadcnThemeTokens`

Immutable Pydantic model with one field per design token (`background`, `primary`, `border`, `radius`, `font_family`, ...). Every token is required in both XML palettes; missing tokens raise `ThemeParseError`.

---

## Documentation

- **Docs site**: [https://qtshadcn.readthedocs.io/](https://qtshadcn.readthedocs.io/)
- **Widget gallery**: `examples/gallery/main.py` (run `make gallery`)

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, coding conventions, and architecture rules.

---

## License

MIT
