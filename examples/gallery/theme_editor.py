"""Interactive theme editor for the gallery."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import ClassVar
from xml.etree import ElementTree as ET

from qtshadcn._qt import QtCore, QtWidgets
from qtshadcn.app import DEFAULT_THEME_FILE

logger = logging.getLogger(__name__)


class ThemeEditor(QtWidgets.QWidget):
    """Theme token editor that writes to both light and dark palettes.

    The editor mirrors the structure of the default QtShadcn XML theme. Token
    changes are emitted through ``themeChanged``; callers are responsible for
    serializing the palette and applying it.
    """

    themeChanged = QtCore.Signal()

    _CATEGORIES: ClassVar[list[tuple[str, list[str]]]] = [
        ("Primary", ["primary", "primary_foreground"]),
        ("Secondary", ["secondary", "secondary_foreground"]),
        ("Muted", ["muted", "muted_foreground"]),
        ("Accent", ["accent", "accent_foreground"]),
        ("Destructive", ["destructive", "destructive_foreground"]),
        ("Base", ["background", "foreground"]),
        ("Card", ["card", "card_foreground"]),
        ("Popover", ["popover", "popover_foreground"]),
        ("Border & Input", ["border", "input", "ring"]),
    ]

    _FONT_FAMILIES: ClassVar[list[str]] = [
        "Inter",
        "Open Sans",
        "Roboto",
        "Segoe UI",
        "Arial",
        "Helvetica",
        "System",
    ]

    _SLIDER_RANGE: ClassVar[tuple[int, int]] = (0, 32)
    _HEX_PATTERN: ClassVar[re.Pattern[str]] = re.compile(r"^#[0-9A-Fa-f]{6}$")

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """Load the default or saved palette and build the editor UI."""
        super().__init__(parent)
        self._color_squares: dict[str, QtWidgets.QPushButton] = {}
        self._color_inputs: dict[str, QtWidgets.QLineEdit] = {}
        self._color_copy_buttons: dict[str, QtWidgets.QPushButton] = {}
        self._font_combo: QtWidgets.QComboBox | None = None
        self._font_display: QtWidgets.QLineEdit | None = None
        self._radius_slider: QtWidgets.QSlider | None = None
        self._radius_value_label: QtWidgets.QLabel | None = None
        self._spacing_slider: QtWidgets.QSlider | None = None
        self._spacing_value_label: QtWidgets.QLabel | None = None
        self._tokens = self._load_default_tokens()
        self._active_mode = "light"

        saved_path = self._gallery_data_dir() / "saved.xml"
        if saved_path.exists():
            self._tokens = self._load_tokens_from_path(saved_path)

        self._build_ui()

    def current_tokens(self) -> dict[str, dict[str, str]]:
        """Return a copy of the current light and dark token dictionaries."""
        return {
            "light": dict(self._tokens["light"]),
            "dark": dict(self._tokens["dark"]),
        }

    def set_token(self, section: str, name: str, value: str) -> None:
        """Update ``name`` in the active palette and refresh the related widget.

        Args:
            section: Category label (used only for UI grouping).
            name: Token name as it appears in the XML palette.
            value: New token value, typically a hex color string.

        """
        if name not in self._tokens[self._active_mode]:
            raise KeyError(f"Unknown theme token: {name}")
        logger.debug("Setting token %s in %s to %s", name, section, value)
        self._tokens[self._active_mode][name] = value
        self._refresh_token(name)
        self.themeChanged.emit()

    def set_active_mode(self, mode: str) -> None:
        """Switch the active palette that the editor displays and mutates.

        Args:
            mode: Either ``"light"`` or ``"dark"``.

        """
        if mode not in {"light", "dark"}:
            raise ValueError(f"Invalid theme mode: {mode!r}")
        self._active_mode = mode
        self._refresh_all()

    def reset_to_default(self) -> None:
        """Reload the packaged default theme into both palettes."""
        self._tokens = self._load_default_tokens()
        self._refresh_all()
        self.themeChanged.emit()

    def to_xml_bytes(self) -> bytes:
        """Serialize the current palettes to QtShadcn XML as UTF-8 bytes."""
        root = ET.Element("theme")
        for mode in ("light", "dark"):
            section = ET.SubElement(root, mode)
            for name, value in self._tokens[mode].items():
                child = ET.SubElement(section, name)
                child.text = value

        ET.indent(root, space="  ")
        header = b'<?xml version="1.0" encoding="utf-8"?>\n'
        return header + ET.tostring(root, encoding="utf-8")

    def save_to_appdata(self) -> Path:
        """Write ``saved.xml`` under the gallery AppData directory.

        Returns:
            The path of the written file.

        """
        path = self._gallery_data_dir() / "saved.xml"
        path.write_bytes(self.to_xml_bytes())
        return path

    def export_to(self, path: Path) -> Path:
        """Export the current palette to the caller-supplied path.

        Returns:
            The path of the written file.

        """
        path = Path(path)
        path.write_bytes(self.to_xml_bytes())
        return path

    def _load_default_tokens(self) -> dict[str, dict[str, str]]:
        """Read the packaged default XML theme into token dictionaries."""
        return self._load_tokens_from_path(Path(DEFAULT_THEME_FILE))

    @staticmethod
    def _load_tokens_from_path(path: Path) -> dict[str, dict[str, str]]:
        """Read a QtShadcn XML file into ``{mode: {name: value}}``."""
        root = ET.parse(path).getroot()
        tokens: dict[str, dict[str, str]] = {}
        for mode in ("light", "dark"):
            section = root.find(mode)
            if section is None:
                raise ValueError(f"Missing <{mode}> section in {path}")
            tokens[mode] = {
                child.tag: child.text.strip() if child.text else ""
                for child in section
                if child.tag is not ET.Comment
            }
        return tokens

    @staticmethod
    def _gallery_data_dir() -> Path:
        """Return the gallery-specific AppData directory, creating it if needed."""
        app_data = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation)
        path = Path(app_data) / "qtshadcn" / "gallery"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _build_ui(self) -> None:
        """Create the tabbed editor with color, typography, and other controls."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        tabs = QtWidgets.QTabWidget(self)
        tabs.addTab(self._build_colors_tab(), "Colors")
        tabs.addTab(self._build_typography_tab(), "Typography")
        tabs.addTab(self._build_other_tab(), "Other")

        layout.addWidget(tabs)

    def _build_colors_tab(self) -> QtWidgets.QWidget:
        """Build the color editor page grouped by category."""
        page = QtWidgets.QWidget()
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.setSpacing(12)
        page_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        for category, names in self._CATEGORIES:
            group = QtWidgets.QGroupBox(category)
            group_layout = QtWidgets.QVBoxLayout(group)
            group_layout.setSpacing(8)
            group_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            for name in names:
                value = self._tokens[self._active_mode].get(name, "#000000")
                label = name.replace("_", " ").title()
                row = self._create_color_row(name, label, value)
                group_layout.addLayout(row)

            page_layout.addWidget(group)

        return page

    def _create_color_row(self, name: str, label: str, value: str) -> QtWidgets.QHBoxLayout:
        """Create a row with a color square, label, hex input, and copy button."""
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 0, 0, 0)

        square = QtWidgets.QPushButton()
        square.setProperty("token", name)
        square.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        square.setFixedSize(28, 28)
        square.setToolTip(f"Click to edit {label}")
        square.clicked.connect(lambda _checked, n=name: self._on_color_square_clicked(n))
        self._color_squares[name] = square
        self._apply_color_square_style(square, value)

        text = QtWidgets.QLabel(label)
        text.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        text.setWordWrap(False)

        hex_input = QtWidgets.QLineEdit(value)
        hex_input.setFixedWidth(80)
        hex_input.setMaxLength(7)
        hex_input.editingFinished.connect(lambda n=name: self._on_hex_input_edited(n))
        self._color_inputs[name] = hex_input

        copy_button = QtWidgets.QPushButton()
        copy_button.setFixedSize(28, 28)
        copy_button.setToolTip("Copy hex value")
        style = QtWidgets.QApplication.style()
        try:
            icon = style.standardIcon(QtWidgets.QStyle.StandardPixmap.SP_FileDialogDetailedView)
        except AttributeError:
            icon = style.standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        copy_button.setIcon(icon)
        copy_button.clicked.connect(lambda _checked, n=name: self._copy_hex_to_clipboard(n))
        self._color_copy_buttons[name] = copy_button

        row.addWidget(square)
        row.addWidget(text, 1)
        row.addWidget(hex_input)
        row.addWidget(copy_button)
        return row

    def _build_typography_tab(self) -> QtWidgets.QWidget:
        """Build the typography editor page."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(page)
        layout.setSpacing(12)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self._font_combo = QtWidgets.QComboBox()
        self._font_combo.addItems(self._FONT_FAMILIES)
        self._font_combo.currentTextChanged.connect(self._on_font_family_changed)

        self._font_display = QtWidgets.QLineEdit()
        self._font_display.setReadOnly(True)

        layout.addRow("Font family", self._font_combo)
        layout.addRow("Current", self._font_display)

        self._refresh_font_family()
        return page

    def _build_other_tab(self) -> QtWidgets.QWidget:
        """Build the other tokens page with radius and spacing sliders."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(page)
        layout.setSpacing(12)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self._radius_slider, self._radius_value_label = self._create_slider_row("radius")
        self._spacing_slider, self._spacing_value_label = self._create_slider_row("spacing")

        layout.addRow("Radius", self._radius_slider)
        layout.addRow(self._radius_value_label)
        layout.addRow("Spacing", self._spacing_slider)
        layout.addRow(self._spacing_value_label)

        self._refresh_slider("radius")
        self._refresh_slider("spacing")
        return page

    def _create_slider_row(self, name: str) -> tuple[QtWidgets.QSlider, QtWidgets.QLabel]:
        """Create a horizontal slider and value label for a pixel token."""
        slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        slider.setRange(*self._SLIDER_RANGE)
        slider.valueChanged.connect(lambda value, n=name: self._on_slider_changed(n, value))
        label = QtWidgets.QLabel()
        return slider, label

    def _on_color_square_clicked(self, name: str) -> None:
        """Open a color dialog and commit the chosen color."""
        current = self._tokens[self._active_mode].get(name, "#000000")
        color = QtWidgets.QColorDialog.getColor(
            QtGui.QColor(current),
            self,
            f"Edit {name}",
        )
        if color.isValid():
            section = self._category_for_token(name)
            self.set_token(section, name, color.name())

    def _on_hex_input_edited(self, name: str) -> None:
        """Validate a hex input and update the token, or revert on failure."""
        line = self._color_inputs[name]
        text = line.text().strip()
        if self._HEX_PATTERN.fullmatch(text):
            if text != self._tokens[self._active_mode].get(name):
                section = self._category_for_token(name)
                self.set_token(section, name, text)
        else:
            line.setText(self._tokens[self._active_mode].get(name, "#000000"))

    def _copy_hex_to_clipboard(self, name: str) -> None:
        """Copy the current hex value for a token to the application clipboard."""
        value = self._color_inputs[name].text()
        QtWidgets.QApplication.clipboard().setText(value)

    def _on_font_family_changed(self, text: str) -> None:
        """Update the active palette's font family token."""
        self._tokens[self._active_mode]["font_family"] = text
        self._refresh_font_family()
        self.themeChanged.emit()

    def _on_slider_changed(self, name: str, value: int) -> None:
        """Update a pixel-sized token from the slider value."""
        if name not in self._tokens[self._active_mode]:
            return
        self._tokens[self._active_mode][name] = f"{value}px"
        self._refresh_slider(name)
        self.themeChanged.emit()

    def _category_for_token(self, name: str) -> str:
        """Return the category label that owns the given token."""
        for category, names in self._CATEGORIES:
            if name in names:
                return category
        return ""

    def _refresh_all(self) -> None:
        """Refresh every visible widget from the active palette."""
        for name in self._color_squares:
            self._refresh_color(name)
        self._refresh_font_family()
        self._refresh_slider("radius")
        self._refresh_slider("spacing")

    def _refresh_token(self, name: str) -> None:
        """Refresh the widget that displays the given token."""
        if name in self._color_squares:
            self._refresh_color(name)
        elif name == "font_family":
            self._refresh_font_family()
        elif name in ("radius", "spacing"):
            self._refresh_slider(name)

    def _refresh_color(self, name: str) -> None:
        """Update the color square and hex input for a single token."""
        value = self._tokens[self._active_mode].get(name, "#000000")
        square = self._color_squares[name]
        line = self._color_inputs[name]
        self._apply_color_square_style(square, value)
        line.blockSignals(True)
        line.setText(value)
        line.blockSignals(False)

    def _refresh_font_family(self) -> None:
        """Refresh the font family combo and read-only display."""
        value = self._tokens[self._active_mode].get("font_family", "")
        if self._font_display is not None:
            self._font_display.setText(value)
        if self._font_combo is not None:
            self._font_combo.blockSignals(True)
            if value in self._FONT_FAMILIES:
                self._font_combo.setCurrentText(value)
            else:
                first = value.split(",")[0].strip()
                self._font_combo.setCurrentText(first if first in self._FONT_FAMILIES else "")
            self._font_combo.blockSignals(False)

    def _refresh_slider(self, name: str) -> None:
        """Refresh the slider and label for a pixel-sized token."""
        value = self._tokens[self._active_mode].get(name, "0px")
        try:
            int_value = int(value.replace("px", "").strip())
        except ValueError:
            int_value = 0
        label_text = f"{int_value}px"

        if name == "radius" and self._radius_slider is not None:
            self._radius_slider.blockSignals(True)
            self._radius_slider.setValue(int_value)
            self._radius_slider.blockSignals(False)
            if self._radius_value_label is not None:
                self._radius_value_label.setText(label_text)
        elif name == "spacing" and self._spacing_slider is not None:
            self._spacing_slider.blockSignals(True)
            self._spacing_slider.setValue(int_value)
            self._spacing_slider.blockSignals(False)
            if self._spacing_value_label is not None:
                self._spacing_value_label.setText(label_text)

    @staticmethod
    def _apply_color_square_style(button: QtWidgets.QPushButton, value: str) -> None:
        """Style the color square so its background reflects the token color."""
        button.setStyleSheet(
            "QPushButton {"
            f"  background-color: {value};"
            "  border: 1px solid rgba(127, 127, 127, 0.5);"
            "  border-radius: 4px;"
            "}"
        )


# Import QtGui here so the module does not depend on it at the top level.
from qtshadcn._qt import QtGui  # noqa: E402
