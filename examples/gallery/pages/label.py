"""QLabel page for the gallery."""

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


class LabelPage:
    """QLabel page for the gallery."""

    label: ClassVar[str] = "QLabel"

    def build(self) -> QtWidgets.QWidget:
        """Build the QLabel page covering common label states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QLabel"))
        layout.addWidget(muted_label("Text labels with shadcn typography styles."))
        layout.addWidget(separator())

        layout.addWidget(section_label("States"))
        states = QtWidgets.QVBoxLayout()
        states.setSpacing(_SPACING)

        default = QtWidgets.QLabel("Email address")
        states.addWidget(default)

        disabled = QtWidgets.QLabel("Disabled label")
        disabled.setEnabled(False)
        states.addWidget(disabled)

        layout.addLayout(states)

        layout.addWidget(separator())
        layout.addWidget(section_label("As field label"))

        form = QtWidgets.QFormLayout()
        form.setSpacing(_SPACING)
        form.setVerticalSpacing(_SPACING)

        email_label = QtWidgets.QLabel("Email")
        email_input = QtWidgets.QLineEdit()
        email_input.setPlaceholderText("Enter your email")
        form.addRow(email_label, email_input)

        password_label = QtWidgets.QLabel("Password")
        password_input = QtWidgets.QLineEdit()
        password_input.setPlaceholderText("Enter your password")
        password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        form.addRow(password_label, password_input)

        layout.addLayout(form)
        layout.addStretch(1)
        return page
