"""QTextEdit page for the gallery."""

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


class TextEditPage:
    """QTextEdit page for the gallery."""

    label: ClassVar[str] = "QTextEdit"

    def build(self) -> QtWidgets.QWidget:
        """Build the QTextEdit page covering textarea states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QTextEdit"))
        layout.addWidget(
            muted_label("Textarea control for longer content, with focus and invalid states.")
        )
        layout.addWidget(separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QTextEdit()
        default.setPlaceholderText("Enter a longer message...")
        default.setMinimumHeight(120)
        form.addRow("Default", default)

        disabled = QtWidgets.QTextEdit("This field is disabled.")
        disabled.setEnabled(False)
        disabled.setMinimumHeight(120)
        form.addRow("Disabled", disabled)

        invalid = QtWidgets.QTextEdit()
        invalid.setPlaceholderText("This field is invalid.")
        invalid.setProperty("invalid", "true")
        invalid.setMinimumHeight(120)
        form.addRow("Invalid", invalid)

        layout.addLayout(form)
        layout.addStretch(1)
        return page
