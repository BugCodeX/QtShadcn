"""QtShadcn .ui Gallery example application.

Demonstrates loading a Qt Designer .ui file using qtpy with a per-binding
loadUi helper (PySide uses QUiLoader, PyQt uses uic.loadUi).
"""

from __future__ import annotations

import logging
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from qtpy import API_NAME, QtCore, QtGui, QtWidgets
from qtshadcn import qsettings, setStyleSheet, setTheme, setThemeMode
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler()],
)

logger = logging.getLogger(__name__)


UI_FILE = str(Path(__file__).resolve().parent / "main_window.ui")
THEME_FILE = str(Path(__file__).resolve().parent / "theme.xml")
CUSTOM_PATH = str(Path(__file__).resolve().parent / "custom.jinja")
QRC_FILE = Path(__file__).resolve().parent / "resources.qrc"
RCC_FILE = Path(__file__).resolve().parent / "resources.rcc"

# Maps the qtpy rcc binary selection to the per-binding tool name.
# Keys are lower-cased because qtpy.API_NAME is capitalized (e.g. "PySide6").
_RCC_BINARIES = {
    "pyside6": "pyside6-rcc",
    "pyside2": "pyside2-rcc",
    "pyqt6": "pyrcc6",
    "pyqt5": "pyrcc5",
}

# Maps the label shown in select_component to the objectName of each page
# inside the QStackedWidget. Add or reorder entries freely here.
PAGES: dict[str, str] = {
    "Overview": "overview_page",
    "Button": "button_page",
    "Checkbox": "checkbox_page",
    "Icon Button": "icon_button_page",
    "Fieldset": "fielset_page",
    "Input": "input_page",
    "Input Number": "input_number_page",
    "Label": "label_page",
    "Progress": "progress_page",
    "Radio": "radio_page",
    "Select": "select_page",
    "Slider": "slider_page",
    "Tabs": "tabs_page",
    "Textarea": "textarea_page",
}

_HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
_FONT_FAMILIES = ["Inter", "Open Sans", "Roboto", "Segoe UI", "Arial", "Helvetica", "System"]

# (token_name, square_widget_name, hex_input_widget_name)
_TOKEN_WIDGETS: list[tuple[str, str, str]] = [
    ("primary", "square_primary_bg", "input_hex_primary_bg"),
    ("primary_foreground", "square_primary_fg", "input_hex_primary_fg"),
    ("secondary", "square_secondary_bg", "input_hex_secondary_bg"),
    ("secondary_foreground", "square_secondary_fg", "input_hex_secondary_fg"),
    ("accent", "square_primary_bg_7", "input_hex_primary_bg_7"),
    ("accent_foreground", "square_primary_fg_7", "input_hex_primary_fg_7"),
    ("background", "square_base_bg", "input_hex_base_bg"),
    ("foreground", "square_base_fg", "input_hex_base_fg"),
    ("card", "square_card_bg", "input_hex_card_bg"),
    ("card_foreground", "square_card_fg", "input_hex_card_fg"),
    ("popover", "square_popover_bg", "input_hex_popover_bg"),
    ("popover_foreground", "square_popover_fg", "input_hex_popover_fg"),
    ("muted", "square_muted_bg", "input_hex_muted_bg"),
    ("muted_foreground", "square_muted_fg", "input_hex_muted_fg"),
    ("destructive", "square_destructive_bg", "input_hex_destructive_bg"),
    ("destructive_foreground", "square_destructive_fg", "input_hex_destructive_fg"),
    ("border", "square_border_input_bg", "input_hex_border_input_bg"),
    ("input", "square_border_input_fg", "input_hex_border_input_fg"),
    ("ring", "square_border_input_ring", "input_hex_border_input_ring"),
]


# ---------------------------------------------------------------------------
# Standalone XML helpers — no dependency on examples.gallery
# ---------------------------------------------------------------------------


def _event_position(event: QtGui.QMouseEvent) -> QtCore.QPoint:
    """Return the local mouse position as a QPoint, compatible with Qt5 and Qt6."""
    position = getattr(event, "position", None)
    if position is not None:
        return position().toPoint()
    return event.pos()


def _event_global_position(event: QtGui.QMouseEvent) -> QtCore.QPoint:
    """Return the global mouse position as a QPoint, compatible with Qt5 and Qt6."""
    global_pos = getattr(event, "globalPosition", None)
    if global_pos is not None:
        return global_pos().toPoint()
    return event.globalPos()


def _load_xml_tokens(path: str | Path) -> dict[str, dict[str, str]]:
    """Parse a QtShadcn XML theme into ``{mode: {token: value}}``."""
    root = ET.parse(path).getroot()
    tokens: dict[str, dict[str, str]] = {}
    for mode in ("light", "dark"):
        section = root.find(mode)
        if section is None:
            raise ValueError(f"Missing <{mode}> section in {path}")
        tokens[mode] = {
            child.tag: (child.text.strip() if child.text else "")
            for child in section
            if child.tag is not ET.Comment
        }
    return tokens


def _tokens_to_xml_bytes(tokens: dict[str, dict[str, str]]) -> bytes:
    """Serialize ``{mode: {token: value}}`` back to QtShadcn XML UTF-8 bytes."""
    root = ET.Element("theme")
    for mode in ("light", "dark"):
        section = ET.SubElement(root, mode)
        for name, value in tokens[mode].items():
            child = ET.SubElement(section, name)
            child.text = value
    ET.indent(root, space="  ")
    return b'<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="utf-8")


def _color_square_style(widget_name: str, color: str) -> str:
    """Return QSS that paints a specific QToolButton swatch with ``color``."""
    return (
        f"QToolButton#{widget_name} {{"
        f"  background-color: {color};"
        "  border: 1px solid rgba(127, 127, 127, 0.5);"
        "  border-radius: 4px;"
        "}"
    )


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


def compile_qrc_if_needed():
    """Recompile resources.qrc -> resources.rcc if the source changed."""
    if not RCC_FILE.exists() or QRC_FILE.stat().st_mtime > RCC_FILE.stat().st_mtime:
        rcc_binary = _RCC_BINARIES.get(API_NAME.lower())
        if rcc_binary is None:
            logger.warning("No rcc binary known for binding %s; skipping qrc compile", API_NAME)
            return

        rcc_path = shutil.which(rcc_binary)
        if rcc_path is None:
            logger.warning("Could not find %s in PATH; skipping qrc compile", rcc_binary)
            return

        logger.info("Compiling resources.qrc with %s...", rcc_binary)
        subprocess.run([rcc_path, "--binary", QRC_FILE, "-o", str(RCC_FILE)], check=True)


class GalleryUiWindow(QtWidgets.QMainWindow):
    """Main window class for the .ui gallery example."""

    def __init__(self, app: QtWidgets.QApplication):
        """Initialize the gallery UI window and load main_window.ui."""
        super().__init__()
        self.app = app
        self.oldPos = self.pos()
        self._active_mode: str = "dark"
        # In-memory token store: {mode: {token: value}}
        self._tokens: dict[str, dict[str, str]] = _load_xml_tokens(THEME_FILE)

        icon = QtGui.QIcon()
        icon.addFile(
            ":/resources/assets/logo.png",
            QtCore.QSize(),
            QtGui.QIcon.Mode.Normal,
            QtGui.QIcon.State.Off,
        )
        self.setWindowIcon(icon)
        self.setWindowTitle("QtShadcn Gallery")

        self.ui = _load_ui(UI_FILE, self)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self._connect_signals()

    def _connect_signals(self):
        # ==================================[WIDGET_STATES]=================================
        self.ui.tristable_checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        self.ui.invalid_tristable_checkbox.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)

        # ==================================[TOP_BAR_ACTIONS]=================================
        self.ui.btnClose.clicked.connect(self.close)
        self.ui.btnMinimize.clicked.connect(self.showMinimized)
        # Sync combo to index 0 (Auto) before connecting to avoid a spurious signal
        self.ui.select_theme.setCurrentIndex(0)
        self.ui.select_theme.currentIndexChanged.connect(self._on_theme_changed)

        # ==================================[COMPONENT_SELECTOR]==============================
        self.ui.select_compont.addItems(list(PAGES.keys()))
        self.ui.select_compont.currentIndexChanged.connect(self._on_component_changed)

        # ==================================[TOTAL COMPONENTS LABEL]=========================
        component_count = len(PAGES) - 1  # exclude "Overview"
        self.ui.total_components.setText(f"All Components ({component_count})")

        # ==================================[THEME EDITOR]===================================
        self._setup_theme_editor()

    # ------------------------------------------------------------------
    # Theme editor wiring
    # ------------------------------------------------------------------

    def _setup_theme_editor(self) -> None:
        """Wire all toolBox widgets to the inline token logic."""
        # Font combo
        self.ui.font_combo.blockSignals(True)
        self.ui.font_combo.clear()
        self.ui.font_combo.addItems(_FONT_FAMILIES)
        self.ui.font_combo.blockSignals(False)
        self.ui.font_combo.currentTextChanged.connect(self._on_font_changed)

        # Sliders
        self.ui.radius_slider.setRange(0, 32)
        self.ui.spacing_slider.setRange(0, 32)
        self.ui.radius_slider.valueChanged.connect(lambda v: self._on_slider_changed("radius", v))
        self.ui.spacing_slider.valueChanged.connect(lambda v: self._on_slider_changed("spacing", v))

        # Color tokens
        for token, sq_name, inp_name in _TOKEN_WIDGETS:
            square = getattr(self.ui, sq_name, None)
            inp = getattr(self.ui, inp_name, None)
            if square:
                square.clicked.connect(lambda _c=False, t=token: self._on_color_square_clicked(t))
            if inp:
                inp.editingFinished.connect(lambda t=token: self._on_hex_input_edited(t))

        # Import / Export
        self.ui.theme_import_button.clicked.connect(self._on_import_theme)
        self.ui.theme_export_button.clicked.connect(self._on_export_theme)

        self._refresh_editor_widgets()

    def _refresh_editor_widgets(self) -> None:
        """Refresh every toolBox widget from the current token palette."""
        palette = self._tokens[self._active_mode]

        for token, sq_name, inp_name in _TOKEN_WIDGETS:
            value = palette.get(token, "#000000")
            square = getattr(self.ui, sq_name, None)
            inp = getattr(self.ui, inp_name, None)
            if square:
                square.setStyleSheet(_color_square_style(sq_name, value))
            if inp:
                inp.blockSignals(True)
                inp.setText(value)
                inp.blockSignals(False)

        # Font
        font_val = palette.get("font_family", "")
        self.ui.font_display.setText(font_val)
        first = font_val.split(",")[0].strip()
        self.ui.font_combo.blockSignals(True)
        self.ui.font_combo.setCurrentText(first if first in _FONT_FAMILIES else "")
        self.ui.font_combo.blockSignals(False)

        # Sliders
        for name, slider, label in [
            ("radius", self.ui.radius_slider, self.ui.radius_value_label),
            ("spacing", self.ui.spacing_slider, self.ui.spacing_value_label),
        ]:
            raw = palette.get(name, "0px")
            try:
                val = int(raw.replace("px", "").strip())
            except ValueError:
                val = 0
            slider.blockSignals(True)
            slider.setValue(val)
            slider.blockSignals(False)
            label.setText(f"{val}px")

    def _apply_editor_theme(self) -> None:
        """Write current tokens to a temp XML file and apply the theme."""
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as tmp_file:
            tmp_file.write(_tokens_to_xml_bytes(self._tokens))
            tmp_path = tmp_file.name
        try:
            setThemeMode(self._active_mode, save=False)
            setTheme(tmp_path, save=False)
            setStyleSheet(CUSTOM_PATH, save=False)
        finally:
            Path(tmp_path).unlink(missing_ok=True)
        # Re-apply color squares AFTER app.setStyleSheet so they survive re-polish
        self._refresh_editor_widgets()

    def _on_color_square_clicked(self, token: str) -> None:
        """Open color picker and commit the chosen color."""
        current = self._tokens[self._active_mode].get(token, "#000000")
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(current), self, f"Edit {token}")
        if color.isValid():
            self._tokens[self._active_mode][token] = color.name()
            self._refresh_editor_widgets()
            self._apply_editor_theme()

    def _on_hex_input_edited(self, token: str) -> None:
        """Validate hex input and update the token."""
        inp_name = next((i for t, _, i in _TOKEN_WIDGETS if t == token), None)
        if not inp_name:
            return
        inp = getattr(self.ui, inp_name, None)
        if not inp:
            return
        text = inp.text().strip()
        if _HEX_RE.fullmatch(text):
            self._tokens[self._active_mode][token] = text
            sq_name = next((s for t, s, _ in _TOKEN_WIDGETS if t == token), None)
            if sq_name:
                getattr(self.ui, sq_name).setStyleSheet(_color_square_style(sq_name, text))
            self._apply_editor_theme()
        else:
            inp.setText(self._tokens[self._active_mode].get(token, "#000000"))

    def _on_font_changed(self, text: str) -> None:
        """Update font_family token and reapply theme."""
        self._tokens[self._active_mode]["font_family"] = text
        self.ui.font_display.setText(text)
        self._apply_editor_theme()

    def _on_slider_changed(self, name: str, value: int) -> None:
        """Update radius/spacing token from slider."""
        self._tokens[self._active_mode][name] = f"{value}px"
        label = self.ui.radius_value_label if name == "radius" else self.ui.spacing_value_label
        label.setText(f"{value}px")
        self._apply_editor_theme()

    def _on_import_theme(self) -> None:
        """Import a theme XML file and apply it."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import Theme", "", "Theme files (*.xml);;All files (*)"
        )
        if path:
            self._tokens = _load_xml_tokens(path)
            self._refresh_editor_widgets()
            self._apply_editor_theme()

    def _on_export_theme(self) -> None:
        """Export the current theme tokens to an XML file."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export Theme", "theme.xml", "Theme files (*.xml);;All files (*)"
        )
        if path:
            Path(path).write_bytes(_tokens_to_xml_bytes(self._tokens))

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _on_component_changed(self, index: int) -> None:
        """Navigate the stackedWidget to the page selected in select_component."""
        page_name = list(PAGES.values())[index]
        page = getattr(self.ui, page_name, None)
        if page:
            self.ui.stackedWidget.setCurrentWidget(page)

    def _on_theme_changed(self, index: int) -> None:
        """Apply the selected theme mode (0=Auto, 1=Light, 2=Dark)."""
        _mode_keys = ["auto", "light", "dark"]
        self._active_mode = _mode_keys[index] if _mode_keys[index] != "auto" else "dark"
        setThemeMode(_mode_keys[index], save=False)
        setTheme(THEME_FILE, save=False)
        setStyleSheet(CUSTOM_PATH, save=False)
        # Re-apply color squares after app stylesheet update
        self._refresh_editor_widgets()

    # ------------------------------------------------------------------
    # Window events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        """Handle mouse press to start dragging the frameless window."""
        if (
            event.button() == QtCore.Qt.MouseButton.LeftButton
            and self.ui.topBarFrame.geometry().contains(_event_position(event))
        ):
            self.oldPos = _event_global_position(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move to drag the frameless window."""
        if (
            event.buttons() == QtCore.Qt.MouseButton.LeftButton
            and self.ui.topBarFrame.geometry().contains(
                self.mapFromGlobal(_event_global_position(event))
            )
        ):
            delta = QtCore.QPoint(_event_global_position(event) - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = _event_global_position(event)

    def enterEvent(self, event):
        """Show a tooltip when the cursor enters the window."""
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), self.toolTip(), self)
        super().enterEvent(event)

    def closeEvent(self, event):
        """Persist current theme preferences before closing the application."""
        qsettings.save()
        logging.shutdown()
        super().closeEvent(event)


if __name__ == "__main__":
    """Run the .ui gallery application."""
    logger.info("Starting QtShadcn Gallery (.ui example)")

    # Legacy binding flags are no longer required; qtpy uses QT_API. Strip them
    # so they are not passed to QApplication.
    legacy_flags = {"--pyside6", "--pyqt6"}
    filtered_argv = [arg for arg in sys.argv if arg not in legacy_flags]
    app = QtWidgets.QApplication(filtered_argv)

    compile_qrc_if_needed()
    QtCore.QResource.registerResource(str(RCC_FILE))

    window = GalleryUiWindow(app)

    # Apply initial theme
    logger.info("Applying initial theme (Dark)")
    setThemeMode("dark", save=False)
    setTheme(THEME_FILE, save=False)
    setStyleSheet(CUSTOM_PATH, save=False)

    window.show()
    logger.info("Gallery .ui window displayed")
    # Re-apply color squares after the initial theme stylesheet
    window._refresh_editor_widgets()

    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())
