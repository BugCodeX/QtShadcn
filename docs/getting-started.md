# Getting Started

## Requirements

- Python ≥ 3.11
- PySide6 ≥ 6.11 (provided by your application environment)

## Installation

/// tab | pip

```bash
pip install qtshadcn
```

///

/// tab | uv

```bash
uv add qtshadcn
```

///

/// tab | development

```bash
# Clones the repo and installs all dev deps (PySide6, ruff, pytest, mkdocs…)
git clone https://github.com/GoMuse/qtshadcn
cd qtshadcn
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
    <font_size>16px</font_size>
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
    <font_size>16px</font_size>
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
from PySide6.QtWidgets import QApplication, QPushButton
from qtshadcn import ThemeConfig, ThemeParseError, apply_theme

app = QApplication(sys.argv)

config = ThemeConfig(
    theme_source_path="my_theme.xml",
    theme_mode="auto",  # follows the OS — or use "light" / "dark"
)

try:
    tokens = apply_theme(app, config)
except ThemeParseError as e:
    print(f"Could not load theme: {e}")
    sys.exit(1)

print(f"Active primary color: {tokens.primary}")

btn = QPushButton("Hello, QtShadcn!")
btn.show()
sys.exit(app.exec())
```

---

## Using the Default Theme

QtShadcn ships with a default theme. Pass no `theme_source_path` and it loads automatically:

```python
from qtshadcn import ThemeConfig, apply_theme

config = ThemeConfig(theme_mode="dark")
apply_theme(app, config)
```

---

## Using Bundled Fonts

QtShadcn includes **Open Sans** and **Roboto**. To activate them, set `font_family` in your XML:

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

You can also use the `ThemeMode` enum:

```python
from qtshadcn import ThemeConfig, ThemeMode

config = ThemeConfig(
    theme_source_path="my_theme.xml",
    theme_mode=ThemeMode.DARK,
)
```
