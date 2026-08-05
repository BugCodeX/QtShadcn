# QtShadcn

**Modern styling and theming framework for Qt/PySide and PyQt applications, inspired by [shadcn/ui](https://ui.shadcn.com).**

QtShadcn applies a design-token–based QSS stylesheet to your `QApplication` in a single function call. Themes are plain XML files — no web tooling required.

---

## Features

- 🎨 **Light & dark palettes** — single XML file, both modes
- 🔄 **Auto mode** — follows the OS preference via `darkdetect`
- 🖥️ **Binding neutral** — works with PySide6, PyQt6, PySide2, or PyQt5
- **Bundled fonts** — Open Sans and Roboto included out of the box
- ⚡ **Disk cache** — QSS is re-rendered only when the theme file changes
- ✅ **App-provided Qt runtime** — install the binding your application already uses
- 🎯 **Themed icons** — SVG check icons generated and cached at runtime

---

## Quick Example

```python
import sys
from qtshadcn._qt import QtWidgets
from qtshadcn import ThemeConfig, apply_theme

app = QtWidgets.QApplication(sys.argv)

config = ThemeConfig(
    theme_source_path="my_theme.xml",
    theme_mode="auto",
)
apply_theme(app, config)

btn = QtWidgets.QPushButton("Hello, QtShadcn!")
btn.show()
sys.exit(app.exec())
```

---

## Widget Gallery

Run the gallery to explore every supported widget and state:

```bash
make gallery
```

The gallery has a sidebar, a light/dark toggle, and one page per supported widget.

---

## Installation

```bash
pip install qtshadcn
# or
uv add qtshadcn
```

QtShadcn is distributed through [PyPI](https://pypi.org/project/qtshadcn/). A Qt binding is app-provided rather than bundled, so install PySide6, PyQt6, PySide2, or PyQt5 in your application environment.

See [Getting Started](getting-started.md) for the full setup guide.

---

## What's Next

- See the [Theme Format](theme-format.md) for every supported token and color syntax.
- See [API Reference](api-reference.md) for `apply_theme`, `ThemeConfig`, and the supported widget list.
- See [Roadmap](roadmap.md) for planned widget coverage and release milestones.
