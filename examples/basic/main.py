"""Basic QtShadcn example — UI loaded from main_window.ui.

Demonstrates the main widget types styled by QtShadcn, with a live
light/dark theme toggle.  The interface is defined in main_window.ui and
loaded at runtime; no custom theme file is required — the bundled default
theme is resolved at start-up.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6 import QtWidgets
from qtshadcn import isDarkTheme, setThemeMode, toggleThemeMode

try:
    from rich.logging import RichHandler

    _logging_handler: logging.Handler = RichHandler()
except ImportError:
    _logging_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[_logging_handler],
)

logger = logging.getLogger(__name__)


UI_FILE = str(Path(__file__).resolve().parent / "main_window.ui")


# ---------------------------------------------------------------------------
# UI loader
# ---------------------------------------------------------------------------


def _load_ui(ui_file: str | Path, base_instance: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """Load a Qt Designer ``.ui`` file for PySide6."""
    from PySide6.QtUiTools import QUiLoader

    class UiLoader(QUiLoader):
        def __init__(self, base_instance):
            super().__init__(base_instance)
            self.base_instance = base_instance

        def createWidget(self, class_name, parent=None, name=""):
            if parent is None and self.base_instance:
                return self.base_instance
            widget = super().createWidget(class_name, parent, name)
            if self.base_instance:
                setattr(self.base_instance, name, widget)
            return widget

    loader = UiLoader(base_instance)
    return loader.load(str(ui_file))


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------


class MainWindow(QtWidgets.QMainWindow):
    """Main application window for the QtShadcn basic example."""

    def __init__(self) -> None:
        """Initialise the window, load the .ui file, and wire up signals."""
        super().__init__()
        self.ui = _load_ui(UI_FILE, self)
        self.setWindowTitle("QtShadcn \u2014 Basic Example")
        self.resize(880, 620)
        self._connect_signals()

    # ------------------------------------------------------------------
    # Signal wiring
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        """Connect widget signals to their handler slots."""
        self.ui.themeToggle.clicked.connect(lambda: toggleThemeMode(save=True))
        self.ui.slider.valueChanged.connect(lambda v: self.ui.sliderValueLabel.setText(str(v)))
        self.ui.textEditor.setPlainText(
            "QtShadcn applies a consistent design language across all Qt widgets.\n"
            "Edit this text to see the styled QTextEdit in action."
        )

    # ------------------------------------------------------------------
    # Theme toggle
    # ------------------------------------------------------------------

    def _toggle_label(self) -> str:
        """Return the appropriate toggle button label for the current theme mode."""
        return "\u263e Dark" if isDarkTheme() else "\u2600 Light"

    def _on_toggle_theme(self) -> None:
        """Toggle between light and dark theme modes."""
        toggleThemeMode(save=True)
        self.ui.themeToggle.setText(self._toggle_label())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    setThemeMode("dark", save=True)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
