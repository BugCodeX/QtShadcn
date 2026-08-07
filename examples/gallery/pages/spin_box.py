"""QSpinBox page for the gallery."""

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


class SpinBoxPage:
    """QSpinBox and QDoubleSpinBox page for the gallery."""

    label: ClassVar[str] = "QSpinBox"

    def build(self) -> QtWidgets.QWidget:
        """Build the spin box page covering common input states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QSpinBox"))
        layout.addWidget(
            muted_label(
                "Numeric input fields with step buttons, including validation and disabled states."
            )
        )
        layout.addWidget(separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QSpinBox()
        default.setRange(0, 100)
        form.addRow("Default", default)

        prefilled = QtWidgets.QSpinBox()
        prefilled.setRange(0, 100)
        prefilled.setValue(42)
        form.addRow("Prefilled", prefilled)

        disabled = QtWidgets.QSpinBox()
        disabled.setRange(0, 100)
        disabled.setValue(10)
        disabled.setEnabled(False)
        form.addRow("Disabled", disabled)

        invalid = QtWidgets.QSpinBox()
        invalid.setRange(0, 100)
        invalid.setValue(200)
        invalid.setProperty("invalid", "true")
        form.addRow("Invalid", invalid)

        double_spin = QtWidgets.QDoubleSpinBox()
        double_spin.setRange(0.0, 1.0)
        double_spin.setSingleStep(0.05)
        double_spin.setValue(0.5)
        form.addRow("QDoubleSpinBox", double_spin)

        layout.addLayout(form)
        layout.addStretch(1)
        return page
