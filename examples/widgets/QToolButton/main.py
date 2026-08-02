from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QPushButton, QToolButton

try:
    import qtshadcn
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    import qtshadcn


TOOL_BUTTON_PROPERTIES = {
    "defaultButton": {"variant": "default", "size": "icon"},
    "defaultDisabledButton": {"variant": "default", "size": "icon"},
    "outlineButton": {"variant": "outline", "size": "icon"},
    "outlineDisabledButton": {"variant": "outline", "size": "icon"},
    "secondaryButton": {"variant": "secondary", "size": "icon"},
    "secondaryDisabledButton": {"variant": "secondary", "size": "icon"},
    "ghostButton": {"variant": "ghost", "size": "icon"},
    "ghostDisabledButton": {"variant": "ghost", "size": "icon"},
    "destructiveButton": {"variant": "destructive", "size": "icon"},
    "destructiveDisabledButton": {"variant": "destructive", "size": "icon"},
    "toggleButton": {"variant": "outline", "size": "icon"},
    "iconSmButton": {"variant": "outline", "size": "icon-sm"},
    "iconButton": {"variant": "outline", "size": "icon"},
    "iconLgButton": {"variant": "outline", "size": "icon-lg"},
}

ICON_SIZE_PRESENTATION = {
    "iconSmButton": 28,
    "iconButton": 36,
    "iconLgButton": 48,
}


def refresh_dynamic_property_styles(widget) -> None:
    """Reapply documented .ui properties and polish QSS property selectors."""
    for button in widget.findChildren(QToolButton):
        for name, value in TOOL_BUTTON_PROPERTIES.get(button.objectName(), {}).items():
            button.setProperty(name, value)
        button.style().unpolish(button)
        button.style().polish(button)
        if button.objectName() in ICON_SIZE_PRESENTATION:
            size = ICON_SIZE_PRESENTATION[button.objectName()]
            button.setFixedSize(size, size)
        button.update()


def main() -> int:
    app = QApplication(sys.argv)

    ui_path = Path(__file__).with_name("app.ui")
    window = QUiLoader().load(str(ui_path))
    if window is None:
        raise RuntimeError(f"Could not load UI file: {ui_path}")

    def apply_selected_theme(checked: bool) -> None:
        theme_mode = "dark" if checked else "light"
        qtshadcn.apply_theme(app, qtshadcn.ThemeConfig(theme_mode=theme_mode))
        refresh_dynamic_property_styles(window)

    dark_mode_button = window.findChild(QPushButton, "darkModeButton")
    if dark_mode_button is None:
        raise RuntimeError("Could not find dark mode toggle in UI file")

    dark_mode_button.toggled.connect(apply_selected_theme)
    apply_selected_theme(dark_mode_button.isChecked())
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
