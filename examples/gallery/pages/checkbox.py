"""QCheckBox page for the gallery."""

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
from qtshadcn._qt import QtCore, QtWidgets


class CheckboxPage:
    """QCheckBox page for the gallery."""

    label: ClassVar[str] = "QCheckBox"

    def build(self) -> QtWidgets.QWidget:
        """Build the QCheckBox page covering common checkbox states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QCheckBox"))
        layout.addWidget(
            muted_label(
                "Toggle controls for boolean choices, with checked, unchecked, indeterminate, "
                "and disabled states."
            )
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        unchecked = QtWidgets.QCheckBox("Accept terms and conditions")
        states.addWidget(unchecked)

        checked = QtWidgets.QCheckBox("Subscribe to newsletter")
        checked.setChecked(True)
        states.addWidget(checked)

        indeterminate = QtWidgets.QCheckBox("Partially selected option")
        indeterminate.setTristate(True)
        indeterminate.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        states.addWidget(indeterminate)

        disabled_unchecked = QtWidgets.QCheckBox("Disabled option")
        disabled_unchecked.setEnabled(False)
        states.addWidget(disabled_unchecked)

        disabled_checked = QtWidgets.QCheckBox("Disabled checked option")
        disabled_checked.setChecked(True)
        disabled_checked.setEnabled(False)
        states.addWidget(disabled_checked)

        layout.addLayout(states)

        layout.addWidget(separator())
        layout.addWidget(section_label("Invalid"))

        invalid_layout = QtWidgets.QVBoxLayout()
        invalid_layout.setSpacing(_SPACING)

        invalid = QtWidgets.QCheckBox("Invalid checkbox")
        invalid.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid)

        invalid_checked = QtWidgets.QCheckBox("Invalid checked checkbox")
        invalid_checked.setChecked(True)
        invalid_checked.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_checked)

        invalid_indeterminate = QtWidgets.QCheckBox("Invalid indeterminate checkbox")
        invalid_indeterminate.setTristate(True)
        invalid_indeterminate.setCheckState(QtCore.Qt.CheckState.PartiallyChecked)
        invalid_indeterminate.setProperty("invalid", "true")
        invalid_layout.addWidget(invalid_indeterminate)

        layout.addLayout(invalid_layout)
        layout.addStretch(1)
        return page
