"""Interactive theme editor for the gallery."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import ClassVar
from xml.etree import ElementTree as ET

from qtshadcn._qt import QtCore, QtWidgets
from qtshadcn.app import DEFAULT_THEME_FILE

logger = logging.getLogger(__name__)


class ThemeEditor(QtWidgets.QWidget):
    """Color token editor that writes to both light and dark palettes.

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

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """Load the default or saved palette and build the editor UI."""
        super().__init__(parent)
        self._swatches: dict[str, QtWidgets.QPushButton] = {}
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
        """Update ``name`` in the active palette and refresh the swatch.

        Args:
            section: Category label (used only for UI grouping).
            name: Token name as it appears in the XML palette.
            value: New color value, typically a hex string.

        """
        if name not in self._tokens[self._active_mode]:
            raise KeyError(f"Unknown theme token: {name}")
        logger.debug("Setting token %s in %s to %s", name, section, value)
        self._tokens[self._active_mode][name] = value
        self._refresh_swatch(name)
        self.themeChanged.emit()

    def set_active_mode(self, mode: str) -> None:
        """Switch the active palette that the editor displays and mutates.

        Args:
            mode: Either ``"light"`` or ``"dark"``.

        """
        if mode not in {"light", "dark"}:
            raise ValueError(f"Invalid theme mode: {mode!r}")
        self._active_mode = mode
        self._refresh_swatches()

    def reset_to_default(self) -> None:
        """Reload the packaged default theme into both palettes."""
        self._tokens = self._load_default_tokens()
        self._refresh_swatches()
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
        """Create a grouped editor with color swatches inside QGroupBox sections."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        for category, names in self._CATEGORIES:
            group = QtWidgets.QGroupBox(category)
            group_layout = QtWidgets.QVBoxLayout(group)
            group_layout.setSpacing(4)
            group_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            for name in names:
                value = self._tokens[self._active_mode].get(name, "#000000")
                label = name.replace("_", " ").title()
                swatch = self._create_swatch(name, value)
                group_layout.addLayout(self._create_swatch_row(label, swatch))

            layout.addWidget(group)

    def _create_swatch(self, name: str, value: str) -> QtWidgets.QPushButton:
        """Create a color swatch button that opens a QColorDialog."""
        button = QtWidgets.QPushButton(value)
        button.setProperty("token", name)
        button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        button.setFixedSize(90, 28)
        button.clicked.connect(lambda _checked, n=name: self._on_swatch_clicked(n))
        self._swatches[name] = button
        self._apply_swatch_style(button, value)
        return button

    @staticmethod
    def _create_swatch_row(label: str, swatch: QtWidgets.QPushButton) -> QtWidgets.QHBoxLayout:
        """Return a row with the label left and the swatch pushed to the right."""
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(8)
        row.setContentsMargins(0, 0, 0, 0)

        text = QtWidgets.QLabel(label)
        text.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        text.setWordWrap(False)
        row.addWidget(text)
        row.addStretch(1)
        row.addWidget(swatch, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        return row

    def _on_swatch_clicked(self, name: str) -> None:
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

    def _category_for_token(self, name: str) -> str:
        """Return the category label that owns the given token."""
        for category, names in self._CATEGORIES:
            if name in names:
                return category
        return ""

    def _refresh_swatch(self, name: str) -> None:
        """Update the displayed value and color of a single swatch."""
        button = self._swatches.get(name)
        if button is None:
            return
        value = self._tokens[self._active_mode][name]
        button.setText(value)
        self._apply_swatch_style(button, value)

    def _refresh_swatches(self) -> None:
        """Refresh every swatch from the active palette."""
        for name, button in self._swatches.items():
            value = self._tokens[self._active_mode].get(name, "#000000")
            button.setText(value)
            self._apply_swatch_style(button, value)

    @staticmethod
    def _apply_swatch_style(button: QtWidgets.QPushButton, value: str) -> None:
        """Style the swatch so its background reflects the token color."""
        button.setStyleSheet(
            "QPushButton {"
            f"  background-color: {value};"
            "  border: 1px solid rgba(127, 127, 127, 0.5);"
            "  border-radius: 4px;"
            "  color: #000000;"
            "}"
        )


# Import QtGui here so the module does not depend on it at the top level.
from qtshadcn._qt import QtGui  # noqa: E402
