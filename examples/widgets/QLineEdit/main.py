from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton

try:
    import qtshadcn
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    import qtshadcn


LINE_EDIT_PROPERTIES = {
    "invalidInput": {"invalid": "true"},
}

BUTTON_PROPERTIES = {
    "darkModeButton": {"variant": "outline"},
}


def repolish(widget) -> None:
    """Reapply documented .ui properties and polish QSS property selectors."""
    for line_edit in widget.findChildren(QLineEdit):
        for name, value in LINE_EDIT_PROPERTIES.get(line_edit.objectName(), {}).items():
            line_edit.setProperty(name, value)
        line_edit.style().unpolish(line_edit)
        line_edit.style().polish(line_edit)
        line_edit.update()

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
        repolish(window)

    dark_mode_button = window.findChild(QPushButton, "darkModeButton")
    if dark_mode_button is None:
        raise RuntimeError("Could not find dark mode toggle in UI file")

    dark_mode_button.toggled.connect(apply_selected_theme)
    apply_selected_theme(dark_mode_button.isChecked())
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
