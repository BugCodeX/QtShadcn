"""QProgressBar page for the gallery."""

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


class ProgressBarPage:
    """QProgressBar page for the gallery."""

    label: ClassVar[str] = "QProgressBar"

    def build(self) -> QtWidgets.QWidget:
        """Build the QProgressBar page covering common progress states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QProgressBar"))
        layout.addWidget(
            muted_label(
                "Displays the progress of an operation, including determinate, "
                "indeterminate, thin, and disabled states."
            )
        )
        layout.addWidget(separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QProgressBar()
        default.setValue(50)
        form.addRow("Default (50%)", default)

        complete = QtWidgets.QProgressBar()
        complete.setValue(100)
        form.addRow("Complete (100%)", complete)

        indeterminate = QtWidgets.QProgressBar()
        indeterminate.setRange(0, 0)
        form.addRow("Indeterminate", indeterminate)

        thin = QtWidgets.QProgressBar()
        thin.setProperty("thin", "true")
        thin.setValue(75)
        form.addRow("Thin variant", thin)

        disabled = QtWidgets.QProgressBar()
        disabled.setValue(30)
        disabled.setEnabled(False)
        form.addRow("Disabled", disabled)

        layout.addLayout(form)

        labeled_row = QtWidgets.QHBoxLayout()
        labeled_row.setSpacing(_SPACING)
        labeled_value = QtWidgets.QProgressBar()
        labeled_value.setValue(65)
        labeled_value.setTextVisible(True)
        label = QtWidgets.QLabel("Upload progress")
        labeled_row.addWidget(label)
        labeled_row.addWidget(labeled_value, 1)
        layout.addLayout(labeled_row)

        layout.addStretch(1)
        return page
