"""QLineEdit page for the gallery."""

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


class LineEditPage:
    """QLineEdit page for the gallery."""

    label: ClassVar[str] = "QLineEdit"

    def build(self) -> QtWidgets.QWidget:
        """Build the QLineEdit page covering common input states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QLineEdit"))
        layout.addWidget(
            muted_label(
                "Input fields for short text values, including validation and disabled states."
            )
        )
        layout.addWidget(separator())

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        default = QtWidgets.QLineEdit()
        default.setPlaceholderText("Enter your email")
        form.addRow("Default", default)

        prefilled = QtWidgets.QLineEdit("Olivia Martin")
        prefilled.setPlaceholderText("Full name")
        form.addRow("Prefilled", prefilled)

        disabled = QtWidgets.QLineEdit()
        disabled.setPlaceholderText("Unavailable field")
        disabled.setEnabled(False)
        form.addRow("Disabled", disabled)

        invalid = QtWidgets.QLineEdit("not-an-email")
        invalid.setPlaceholderText("Email address")
        invalid.setProperty("invalid", "true")
        form.addRow("Invalid", invalid)

        password = QtWidgets.QLineEdit("correct-horse-battery-staple")
        password.setPlaceholderText("Password")
        password.setEchoMode(QtWidgets.QLineEdit.Password)
        form.addRow("Password", password)

        layout.addLayout(form)
        layout.addStretch(1)
        return page
