"""QtShadcn CSS → Theme Generator GUI.

Loads main_window.ui, parses a pasted CSS snippet, and renders
the QtShadcn theme.xml content directly in the output textarea.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from qtpy import API_NAME, QtCore, QtGui, QtWidgets
from qtshadcn import setTheme, setThemeMode

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve().parent
UI_FILE = str(_HERE / "main_window.ui")
THEME_FILE = str(_HERE / "theme.xml")

# ---------------------------------------------------------------------------
# CSS → XML token mapping (CSS var name → XML element tag)
# ---------------------------------------------------------------------------

TOKEN_MAP: dict[str, str] = {
    "background": "background",
    "foreground": "foreground",
    "card": "card",
    "card-foreground": "card_foreground",
    "popover": "popover",
    "popover-foreground": "popover_foreground",
    "primary": "primary",
    "primary-foreground": "primary_foreground",
    "secondary": "secondary",
    "secondary-foreground": "secondary_foreground",
    "muted": "muted",
    "muted-foreground": "muted_foreground",
    "accent": "accent",
    "accent-foreground": "accent_foreground",
    "destructive": "destructive",
    "destructive-foreground": "destructive_foreground",
    "border": "border",
    "input": "input",
    "ring": "ring",
    "spacing": "spacing",
    "radius": "radius",
    "font-sans": "font_family",
}

# ---------------------------------------------------------------------------
# Pure parsing helpers (no I/O)
# ---------------------------------------------------------------------------


def parse_css_block(css_content: str, selector: str) -> dict[str, str]:
    """Extract CSS custom properties from a single selector block."""
    pattern = rf"{re.escape(selector)}\s*\{{([^}}]+)\}}"
    match = re.search(pattern, css_content)
    if not match:
        return {}
    block = match.group(1)
    var_pattern = r"--([a-zA-Z0-9-]+)\s*:\s*([^;]+);"
    return {name.strip(): value.strip() for name, value in re.findall(var_pattern, block)}


def tokens_to_xml_str(light: dict[str, str], dark: dict[str, str]) -> str:
    """Render a QtShadcn-compatible theme XML string from two token dicts."""
    root = ET.Element("theme")

    for mode_tag, tokens in (("light", light), ("dark", dark)):
        mode_el = ET.SubElement(root, mode_tag)
        for css_var, xml_tag in TOKEN_MAP.items():
            if css_var in tokens:
                child = ET.SubElement(mode_el, xml_tag)
                child.text = tokens[css_var]

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=False)


def generate_xml_from_css(css: str) -> tuple[bool, str]:
    """Parse CSS and return ``(success, xml_string_or_error_message)``."""
    light = parse_css_block(css, ":root")
    dark = parse_css_block(css, ".dark")

    if not light and not dark:
        return False, "No CSS custom properties found in :root or .dark blocks."

    return True, tokens_to_xml_str(light, dark)


# ---------------------------------------------------------------------------
# UI loader helper (PySide6 / PyQt6 compatible)
# ---------------------------------------------------------------------------


def _load_ui(ui_file: str | Path, base_instance: QtWidgets.QWidget) -> QtWidgets.QWidget:
    """Load a Qt Designer .ui file for the active binding."""
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


class GeneratorWindow(QtWidgets.QMainWindow):
    """Main window for the CSS → Theme Generator example."""

    def __init__(self, app: QtWidgets.QApplication) -> None:
        """Initialize the generator window and load the .ui file."""
        super().__init__()
        self.app = app
        self._old_pos = self.pos()

        self.setWindowTitle("QtShadcn — CSS → Theme Generator")
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.ui = _load_ui(UI_FILE, self)
        self._connect_signals()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        """Wire all UI signals to their handlers."""
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(self.showMinimized)
        self.ui.btnGenerate.clicked.connect(self._on_generate)
        self.ui.btnClearCss.clicked.connect(self._on_clear_css)
        self.ui.btnCopyXml.clicked.connect(self._on_copy_xml)

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    def _on_generate(self) -> None:
        """Parse the CSS input and display the generated XML in the output pane."""
        css = self.ui.cssInput.toPlainText().strip()
        if not css:
            self._set_status("⚠ CSS input is empty.", error=True)
            return

        ok, result = generate_xml_from_css(css)
        if ok:
            self.ui.xmlOutput.setPlainText(result)
            self.ui.btnCopyXml.setEnabled(True)
            self._set_status("✓ Theme XML generated successfully.")
        else:
            self.ui.xmlOutput.setPlainText("")
            self.ui.btnCopyXml.setEnabled(False)
            self._set_status(f"✗ {result}", error=True)

    def _on_clear_css(self) -> None:
        """Clear the CSS input area."""
        self.ui.cssInput.clear()
        self.ui.xmlOutput.clear()
        self.ui.btnCopyXml.setEnabled(False)
        self._set_status("")

    def _on_copy_xml(self) -> None:
        """Copy the XML output to the system clipboard."""
        xml = self.ui.xmlOutput.toPlainText()
        if xml:
            QtWidgets.QApplication.clipboard().setText(xml)
            self._set_status("✓ Copied to clipboard!")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _set_status(self, message: str, *, error: bool = False) -> None:
        """Update the status label text."""
        self.ui.statusLabel.setText(message)

    # ------------------------------------------------------------------
    # Frameless window drag
    # ------------------------------------------------------------------

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """Start window drag on left-click in the top bar."""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = getattr(event, "globalPosition", None)
            self._old_pos = pos().toPoint() if pos else event.globalPos()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """Drag the frameless window."""
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            pos = getattr(event, "globalPosition", None)
            current = pos().toPoint() if pos else event.globalPos()
            delta = QtCore.QPoint(current - self._old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._old_pos = current


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    legacy_flags = {"--pyside6", "--pyqt6"}
    filtered_argv = [arg for arg in sys.argv if arg not in legacy_flags]
    app = QtWidgets.QApplication(filtered_argv)

    setThemeMode("dark", save=False)
    setTheme(THEME_FILE, save=False)

    window = GeneratorWindow(app)
    window.show()

    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())
