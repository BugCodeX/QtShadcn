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
from qtshadcn._qt import QtCore, QtWidgets


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
                "indeterminate, and disabled states."
            )
        )
        layout.addWidget(separator())

        rows: list[tuple[str, int | None, bool, bool]] = [
            ("Default (50%)", 50, True, True),
            ("Complete (100%)", 100, True, True),
            ("Indeterminate", None, False, True),
            ("Disabled", 30, True, False),
        ]

        for label_text, value, show_value, enabled in rows:
            row = QtWidgets.QHBoxLayout()
            row.setSpacing(_SPACING)

            label = QtWidgets.QLabel(label_text)
            label.setMinimumWidth(140)
            row.addWidget(label)

            bar = QtWidgets.QProgressBar()
            bar.setTextVisible(False)
            bar.setEnabled(enabled)
            if value is None:
                bar.setRange(0, 0)
            else:
                bar.setValue(value)
            row.addWidget(bar, 1)

            if show_value:
                value_text = f"{value}%" if value is not None else ""
                value_label = QtWidgets.QLabel(value_text)
                value_label.setProperty("class", "muted")
                value_label.setMinimumWidth(40)
                value_label.setAlignment(
                    QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                )
                row.addWidget(value_label)

            layout.addLayout(row)

        layout.addStretch(1)
        return page
