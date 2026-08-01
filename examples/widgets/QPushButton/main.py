from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QPushButton

try:
    import qtshadcn
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    import qtshadcn


BUTTON_PROPERTIES = {
    "darkModeButton": {"variant": "outline"},
    "defaultButton": {"variant": "default"},
    "defaultDisabledButton": {"variant": "default"},
    "outlineButton": {"variant": "outline"},
    "outlineDisabledButton": {"variant": "outline"},
    "secondaryButton": {"variant": "secondary"},
    "secondaryDisabledButton": {"variant": "secondary"},
    "ghostButton": {"variant": "ghost"},
    "ghostDisabledButton": {"variant": "ghost"},
    "destructiveButton": {"variant": "destructive"},
    "destructiveDisabledButton": {"variant": "destructive"},
    "linkButton": {"variant": "link"},
    "linkDisabledButton": {"variant": "link"},
    "xsButton": {"buttonSize": "xs"},
    "smButton": {"buttonSize": "sm"},
    "defaultSizeButton": {"buttonSize": "default"},
    "lgButton": {"buttonSize": "lg"},
    "iconXsButton": {"variant": "outline", "buttonSize": "icon-xs"},
    "iconSmButton": {"variant": "outline", "buttonSize": "icon-sm"},
    "iconButton": {"variant": "outline", "buttonSize": "icon"},
    "iconLgButton": {"variant": "outline", "buttonSize": "icon-lg"},
}


def refresh_dynamic_property_styles(widget) -> None:
    """Reapply documented .ui properties and polish QSS property selectors."""
    for button in widget.findChildren(QPushButton):
        for name, value in BUTTON_PROPERTIES.get(button.objectName(), {}).items():
            button.setProperty(name, value)
        button.style().unpolish(button)
        button.style().polish(button)
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
