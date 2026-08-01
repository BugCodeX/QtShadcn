# QtShadcn

**Modern styling and theming framework for Qt/PySide6 applications, inspired by [shadcn/ui](https://ui.shadcn.com).**

QtShadcn applies a design-token–based QSS stylesheet to your `QApplication` in a single function call. Themes are plain XML files — no web tooling required.

---

## Features

- 🎨 **Light & dark palettes** — single XML file, both modes
- 🔄 **Auto mode** — follows the OS preference via `darkdetect`
- 🖋 **Bundled fonts** — Open Sans and Roboto included out of the box
- ⚡ **Disk cache** — QSS is re-rendered only when the theme file changes
- ✅ **App-provided Qt runtime** — install PySide6 in your application environment

---

## Quick Example

```python
import sys
from PySide6.QtWidgets import QApplication, QPushButton
from qtshadcn import ThemeConfig, apply_theme

app = QApplication(sys.argv)

config = ThemeConfig(
    theme_source_path="my_theme.xml",
    theme_mode="auto",
)
apply_theme(app, config)

btn = QPushButton("Hello, QtShadcn!")
btn.show()
sys.exit(app.exec())
```

---

## Installation

```bash
pip install qtshadcn
```

See [Getting Started](getting-started.md) for the full setup guide.
