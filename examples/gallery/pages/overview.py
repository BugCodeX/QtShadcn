"""Overview page for the gallery."""

from __future__ import annotations

from typing import ClassVar

from examples.gallery.pages._helpers import (
    _PAGE_MARGIN,
    _SPACING,
    muted_label,
    page_title,
)
from qtshadcn._qt import QtWidgets


class OverviewPage:
    """Overview page for the gallery."""

    label: ClassVar[str] = "Overview"

    def build(self) -> QtWidgets.QWidget:
        """Build the overview page."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("Overview"))
        layout.addWidget(
            muted_label(
                "QtShadcn styles common Qt widgets with a single XML theme. "
                "Use the selector to explore supported widgets and states."
            )
        )

        content = QtWidgets.QLabel(
            "Supported widgets in this release: QWidget, QPushButton, QToolButton, "
            "QLineEdit, QTextEdit, QCheckBox, QRadioButton, QFontComboBox, QLabel."
        )
        content.setWordWrap(True)
        layout.addWidget(content)

        layout.addStretch(1)
        return page
