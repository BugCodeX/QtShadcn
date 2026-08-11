# Getting Started

## Requirements

- Python ≥ 3.11
- One of the supported Qt bindings: **PySide6**, **PyQt6**, **PySide2**, or **PyQt5**

## Installation

QtShadcn is published on PyPI. A Qt binding is intentionally not bundled; install the one your application already uses so your app controls the Qt runtime version.

/// tab | pip

```bash
pip install qtshadcn
pip install PySide6  # or PyQt6, PySide2, PyQt5
```

///

/// tab | uv

```bash
uv add qtshadcn
uv add PySide6  # or PyQt6, PySide2, PyQt5
```

///

/// tab | development

```bash
# Clones the repo and installs all dev deps (PySide6, ruff, pytest, mkdocs…)
git clone https://github.com/BugCodeX/QtShadcn
cd QtShadcn
uv sync --extra dev
```

///

---

## Minimal Setup

### 1. Create a theme file

Save this as `my_theme.xml` next to your script:

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
    <background>#020617</background>
    <foreground>#f8fafc</foreground>
    <primary>#f8fafc</primary>
    <primary_foreground>#0f172a</primary_foreground>
    <secondary>#1e293b</secondary>
    <secondary_foreground>#f8fafc</secondary_foreground>
    <accent>#1e293b</accent>
    <accent_foreground>#f8fafc</accent_foreground>
    <muted>#1e293b</muted>
    <muted_foreground>#94a3b8</muted_foreground>
    <destructive>#7f1d1d</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#1e293b</border>
    <input>#1e293b</input>
    <ring>#cbd5e1</ring>
    <radius>8px</radius>
    <font_family>system-ui, sans-serif</font_family>
    <spacing>4px</spacing>
    <card>#020617</card>
    <card_foreground>#f8fafc</card_foreground>
    <popover>#020617</popover>
    <popover_foreground>#f8fafc</popover_foreground>
  </dark>
</theme>
```

### 2. Apply the theme

```python
import sys
from qtpy import QtWidgets
from qtshadcn import ThemeParseError, apply_theme

app = QtWidgets.QApplication(sys.argv)

try:
    tokens = apply_theme(
        app,
        theme_file="my_theme.xml",
        theme_mode="auto",  # follows the OS — or use "light" / "dark"
    )
except ThemeParseError as e:
    print(f"Could not load theme: {e}")
    sys.exit(1)

print(f"Active primary color: {tokens.primary}")

btn = QtWidgets.QPushButton("Hello, QtShadcn!")
btn.show()
sys.exit(app.exec())
```

---

## Using the Default Theme

QtShadcn ships with a default theme. Pass no `theme_file` and it loads automatically:

```python
from qtshadcn import apply_theme

apply_theme(app, theme_mode="dark")
```

---

## Using Bundled Fonts

QtShadcn includes **Open Sans** and **Roboto** under `qtshadcn/fonts/`. To activate them, set `font_family` in your XML:

```xml
<font_family>Open Sans, system-ui, sans-serif</font_family>
```

The fonts are registered automatically by `apply_theme` before the stylesheet is applied.

---

## Theme Mode Options

| Value | Behavior |
| --- | --- |
| `"auto"` | Follows the OS light/dark preference (default) |
| `"light"` | Always use the `<light>` palette |
| `"dark"` | Always use the `<dark>` palette |

The `theme_mode` argument accepts the string values `"auto"`, `"light"`, and `"dark"`:

```python
from qtshadcn import apply_theme

apply_theme(app, theme_file="my_theme.xml", theme_mode="dark")
```

---

## Supported Qt Bindings

QtShadcn supports four Qt bindings through [qtpy](https://github.com/spyder-ide/qtpy):

1. PySide6 (`QT_API=pyside6`)
2. PyQt6 (`QT_API=pyqt6`)
3. PySide2 (`QT_API=pyside2`)
4. PyQt5 (`QT_API=pyqt5`)

### Choosing a binding

If only one supported binding is installed, qtpy uses it automatically. When
multiple bindings are installed, set `QT_API` before importing QtShadcn:

```bash
export QT_API=pyside6
```

Import Qt classes directly from qtpy in your application code:

```python
from qtpy import QtWidgets

app = QtWidgets.QApplication([])
```

The public API remains the same regardless of which binding is active.
