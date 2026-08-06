"""QRadioButton page for the gallery."""

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
from qtshadcn._qt import QtWidgets


class RadioButtonPage:
    """QRadioButton page for the gallery."""

    label: ClassVar[str] = "QRadioButton"

    def build(self) -> QtWidgets.QWidget:
        """Build the QRadioButton page covering common radio button states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QRadioButton"))
        layout.addWidget(
            muted_label(
                "Radio buttons for selecting one option from a set, with checked, unchecked, "
                "and disabled states."
            )
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        unchecked = QtWidgets.QRadioButton("Default")
        states.addWidget(unchecked)

        checked = QtWidgets.QRadioButton("Selected option")
        checked.setChecked(True)
        states.addWidget(checked)

        disabled_unchecked = QtWidgets.QRadioButton("Disabled option")
        disabled_unchecked.setEnabled(False)
        states.addWidget(disabled_unchecked)

        disabled_checked = QtWidgets.QRadioButton("Disabled selected")
        disabled_checked.setChecked(True)
        disabled_checked.setEnabled(False)
        states.addWidget(disabled_checked)

        layout.addLayout(states)

        layout.addWidget(separator())
        layout.addWidget(section_label("Invalid"))

        invalid_layout = QtWidgets.QVBoxLayout()
        invalid_layout.setSpacing(_SPACING)

        invalid = QtWidgets.QRadioButton("Invalid radio button")
        invalid.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid)

        invalid_checked = QtWidgets.QRadioButton("Invalid selected radio button")
        invalid_checked.setChecked(True)
        invalid_checked.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_checked)

        layout.addLayout(invalid_layout)
        layout.addStretch(1)
        return page
