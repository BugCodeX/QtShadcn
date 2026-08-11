"""QtShadcn .ui Gallery example application.

Demonstrates loading a Qt Designer .ui file using PySide6 or PyQt6.
"""

from __future__ import annotations

import logging
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from qtshadcn import apply_theme, get_theme
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


def compile_qrc_if_needed():
    """Recompila resources.qrc -> resources.rcc si cambió."""
    if not RCC_FILE.exists() or QRC_FILE.stat().st_mtime > RCC_FILE.stat().st_mtime:
        logging.info("Compilando resources.qrc...")
        subprocess.run(["pyside6-rcc", "--binary", QRC_FILE, "-o", str(RCC_FILE)], check=True)


if "--pyside6" in sys.argv:
    from PySide6 import QtCore
    from PySide6.QtCore import QPoint, QResource, QSize, Qt
    from PySide6.QtGui import QColor, QCursor, QIcon
    from PySide6.QtUiTools import QUiLoader
    from PySide6.QtWidgets import QApplication, QColorDialog, QFileDialog, QMainWindow, QToolTip

    uic = None

elif "--pyqt6" in sys.argv:
    from PyQt6 import QtCore, uic
    from PyQt6.QtCore import QPoint, QResource, QSize, Qt
    from PyQt6.QtGui import QColor, QCursor, QIcon
    from PyQt6.QtWidgets import QApplication, QColorDialog, QFileDialog, QMainWindow, QToolTip

    QUiLoader = None

else:
    try:
        from PySide6 import QtCore
        from PySide6.QtCore import QPoint, QResource, QSize, Qt
        from PySide6.QtGui import QColor, QCursor, QIcon
        from PySide6.QtUiTools import QUiLoader
        from PySide6.QtWidgets import QApplication, QColorDialog, QFileDialog, QMainWindow, QToolTip

        uic = None
    except ImportError:
        from PyQt6 import QtCore, uic
        from PyQt6.QtCore import QPoint, QResource, QSize, Qt
        from PyQt6.QtGui import QColor, QCursor, QIcon
        from PyQt6.QtWidgets import QApplication, QColorDialog, QFileDialog, QMainWindow, QToolTip

        QUiLoader = None


class GalleryUiWindow(QMainWindow):
    """Main window class for the .ui gallery example."""

    def __init__(self, app: QApplication):
        """Initialize the gallery UI window and load main_window.ui."""
        super().__init__()
        self.app = app
        self.oldPos = self.pos()
        self._active_mode: str = "dark"
        # In-memory token store: {mode: {token: value}}
        self._tokens: dict[str, dict[str, str]] = _load_xml_tokens(THEME_FILE)

        icon = QIcon()
        icon.addFile(":/resources/assets/logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("QtShadcn Gallery")

        if "--pyside6" in sys.argv:
            self.ui = QUiLoader().load(UI_FILE)
            self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setCentralWidget(self.ui)

        elif "--pyqt6" in sys.argv:
            self.ui = uic.loadUi(UI_FILE)
            self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setCentralWidget(self.ui)

        else:
            logging.error("Please include --pyside6 or --pyqt6 in arguments.")
            sys.exit()

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
                val = int(raw.replace("px", "").replace("rem", "").strip())
            except ValueError:
                val = 0
            slider.blockSignals(True)
            slider.setValue(val)
            slider.blockSignals(False)
            label.setText(f"{val}px")

    def _apply_editor_theme(self) -> None:
        """Write current tokens to a temp XML file and apply the theme."""
        tmp = Path(tempfile.mktemp(suffix=".xml"))
        tmp.write_bytes(_tokens_to_xml_bytes(self._tokens))
        apply_theme(
            self.app,
            theme_file=str(tmp),
            theme_mode=self._active_mode,
            additional_qss=CUSTOM_PATH,
        )
        tmp.unlink(missing_ok=True)
        # Re-apply color squares AFTER app.setStyleSheet so they survive re-polish
        self._refresh_editor_widgets()

    def _on_color_square_clicked(self, token: str) -> None:
        """Open color picker and commit the chosen color."""
        current = self._tokens[self._active_mode].get(token, "#000000")
        color = QColorDialog.getColor(QColor(current), self, f"Edit {token}")
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
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Theme", "", "Theme files (*.xml);;All files (*)"
        )
        if path:
            self._tokens = _load_xml_tokens(path)
            self._refresh_editor_widgets()
            self._apply_editor_theme()

    def _on_export_theme(self) -> None:
        """Export the current theme tokens to an XML file."""
        path, _ = QFileDialog.getSaveFileName(
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
        apply_theme(
            self.app,
            theme_file=THEME_FILE,
            theme_mode=_mode_keys[index],
            additional_qss=CUSTOM_PATH,
        )
        # Re-apply color squares after app stylesheet update
        self._refresh_editor_widgets()

    # ------------------------------------------------------------------
    # Window events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        """Maneja el evento de clic del ratón pa' mover la ventana."""
        if event.button() == Qt.MouseButton.LeftButton and self.ui.topBarFrame.geometry().contains(
            event.position().toPoint()
        ):
            self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        """Maneja el evento de movimiento del ratón pa' arrastrar la ventana."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.ui.topBarFrame.geometry().contains(
            self.mapFromGlobal(event.globalPosition().toPoint())
        ):
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def enterEvent(self, event):
        """Muestra un tooltip cuando el cursor entra en la ventana."""
        QToolTip.showText(QCursor.pos(), self.toolTip(), self)
        super().enterEvent(event)

    def closeEvent(self, event):
        """Limpia vistas externas antes de cerrar la aplicación."""
        logging.shutdown()
        super().closeEvent(event)


if __name__ == "__main__":
    """Run the .ui gallery application."""
    logger.info("Starting QtShadcn Gallery (.ui example)")
    app = QApplication(sys.argv)

    compile_qrc_if_needed()
    QResource.registerResource(str(RCC_FILE))

    window = GalleryUiWindow(app)

    # Apply initial theme
    logger.info("Applying initial theme (Dark)")
    get_theme()
    apply_theme(
        window.app,
        theme_file=THEME_FILE,
        theme_mode="dark",
        additional_qss=CUSTOM_PATH,
    )

    window.show()
    logger.info("Gallery .ui window displayed")
    # Re-apply color squares after the initial theme stylesheet
    window._refresh_editor_widgets()

    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())
