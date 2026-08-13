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

from qtpy import API_NAME, QtWidgets
from qtshadcn import isDarkTheme, setThemeMode, toggleThemeMode
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler()],
)

logger = logging.getLogger(__name__)


UI_FILE = str(Path(__file__).resolve().parent / "main_window.ui")


# ---------------------------------------------------------------------------
# UI loader
# ---------------------------------------------------------------------------


def _load_ui(ui_file: str | Path, base_instance: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """Load a Qt Designer ``.ui`` file for the active binding.

    PySide bindings provide ``QUiLoader``; PyQt bindings provide ``uic.loadUi``.
    qtpy does not expose a unified ``loadUi`` across all four bindings, so we
    dispatch locally.
    """
    path = str(ui_file)
    if API_NAME in ("PySide6", "PySide2"):
        from qtpy.QtUiTools import QUiLoader

        return QUiLoader().load(path, base_instance)
    if API_NAME == "PyQt6":
        from PyQt6.uic import loadUi as _loadUi

        return _loadUi(path, base_instance)
    if API_NAME == "PyQt5":
        from PyQt5.uic import loadUi as _loadUi

        return _loadUi(path, base_instance)
    raise RuntimeError(f"Unsupported Qt binding: {API_NAME}")


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
