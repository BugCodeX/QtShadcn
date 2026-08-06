"""QComboBox page for the gallery."""

from __future__ import annotations

from typing import ClassVar

from examples.gallery.pages._helpers import (
    _PAGE_MARGIN,
    _SPACING,
    muted_label,
    page_title,
    section_label,
    separator,
)
from qtshadcn._qt import QtGui, QtWidgets


class ComboBoxPage:
    """QComboBox page for the gallery."""

    label: ClassVar[str] = "QComboBox"

    def build(self) -> QtWidgets.QWidget:
        """Build the QComboBox page covering common combo box states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QComboBox"))
        layout.addWidget(muted_label("Dropdown selection controls with styled trigger and popup."))
        layout.addWidget(separator())

        layout.addWidget(section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        default = QtWidgets.QComboBox()
        default.addItems(["Next.js", "SvelteKit", "Nuxt.js", "Remix", "Astro"])
        default.setCurrentIndex(-1)
        default.setPlaceholderText("Select a framework")
        states.addWidget(default)

        selected = QtWidgets.QComboBox()
        selected.addItems(["Next.js", "SvelteKit", "Nuxt.js", "Remix", "Astro"])
        selected.setCurrentIndex(0)
        states.addWidget(selected)

        disabled = QtWidgets.QComboBox()
        disabled.addItems(["Option 1", "Option 2", "Option 3"])
        disabled.setEnabled(False)
        states.addWidget(disabled)

        layout.addLayout(states)

        layout.addWidget(separator())
        layout.addWidget(section_label("Invalid"))

        invalid_layout = QtWidgets.QVBoxLayout()
        invalid_layout.setSpacing(_SPACING)

        invalid = QtWidgets.QComboBox()
        invalid.addItems(["Option 1", "Option 2", "Option 3"])
        invalid.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid)

        invalid_selected = QtWidgets.QComboBox()
        invalid_selected.addItems(["Option 1", "Option 2", "Option 3"])
        invalid_selected.setCurrentIndex(1)
        invalid_selected.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_selected)

        layout.addLayout(invalid_layout)

        layout.addWidget(separator())
        layout.addWidget(section_label("QFontComboBox"))
        layout.addWidget(muted_label("Font selection dropdown with the same styling as QComboBox."))

        font_combo = QtWidgets.QFontComboBox()
        font_combo.setCurrentIndex(-1)
        layout.addWidget(font_combo)

        font_combo_selected = QtWidgets.QFontComboBox()
        selected_font = QtGui.QFont("Arial")
        selected_font.setPointSize(12)
        font_combo_selected.setCurrentFont(selected_font)
        layout.addWidget(font_combo_selected)

        font_combo_disabled = QtWidgets.QFontComboBox()
        font_combo_disabled.setEnabled(False)
        layout.addWidget(font_combo_disabled)

        layout.addStretch(1)
        return page
