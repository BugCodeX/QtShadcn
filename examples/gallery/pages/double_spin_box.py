"""QDoubleSpinBox page for the gallery."""

from __future__ import annotations

from typing import ClassVar

from examples.gallery.pages._helpers import (
    _PAGE_MARGIN,
    _SPACING,
    muted_label,
    page_title,
    separator,
)
from qtshadcn._qt import QtWidgets


class DoubleSpinBoxPage:
    """QDoubleSpinBox page for the gallery."""

    label: ClassVar[str] = "QDoubleSpinBox"

    def build(self) -> QtWidgets.QWidget:
        """Build the double spin box page covering common input states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QDoubleSpinBox"))
        layout.addWidget(
            muted_label(
                "Numeric input fields with step buttons, including validation and disabled states."
            )
        )
        layout.addWidget(separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QDoubleSpinBox()
        default.setRange(0.0, 1.0)
        default.setSingleStep(0.05)
        form.addRow("Default", default)

        prefilled = QtWidgets.QDoubleSpinBox()
        prefilled.setRange(0.0, 1.0)
        prefilled.setSingleStep(0.05)
        prefilled.setValue(0.42)
        form.addRow("Prefilled", prefilled)

        disabled = QtWidgets.QDoubleSpinBox()
        disabled.setRange(0.0, 1.0)
        disabled.setSingleStep(0.05)
        disabled.setValue(0.1)
        disabled.setEnabled(False)
        form.addRow("Disabled", disabled)

        invalid = QtWidgets.QDoubleSpinBox()
        invalid.setRange(0.0, 1.0)
        invalid.setSingleStep(0.05)
        invalid.setValue(2.0)
        invalid.setProperty("invalid", "true")
        form.addRow("Invalid", invalid)

        layout.addLayout(form)
        layout.addStretch(1)
        return page
