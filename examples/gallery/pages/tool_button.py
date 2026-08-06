"""QToolButton page for the gallery."""

from __future__ import annotations

from typing import ClassVar

from examples.gallery.pages._helpers import (
    _PAGE_MARGIN,
    _SPACING,
    QToolButtonVariantRow,
    muted_label,
    page_title,
    section_label,
    separator,
    variant_grid,
)
from qtshadcn._qt import QtWidgets


class ToolButtonPage:
    """QToolButton page for the gallery."""

    label: ClassVar[str] = "QToolButton"

    def build(self) -> QtWidgets.QWidget:
        """Build the QToolButton page covering variants and icon sizes."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QToolButton"))
        layout.addWidget(
            muted_label("Compact action controls for toolbars, toggles, and icon buttons.")
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("Variants"))
        layout.addLayout(variant_grid(QToolButtonVariantRow))

        layout.addWidget(section_label("Icon sizes"))
        icon_sizes = QtWidgets.QHBoxLayout()
        icon_sizes.setSpacing(_SPACING)
        for size, label, fixed in [
            ("icon-sm", "S", 28),
            ("icon", "M", 36),
            ("icon-lg", "L", 48),
        ]:
            btn = QtWidgets.QToolButton()
            btn.setText(label)
            btn.setProperty("variant", "outline")
            btn.setProperty("size", size)
            btn.setFixedSize(fixed, fixed)
            icon_sizes.addWidget(btn)
        layout.addLayout(icon_sizes)

        layout.addStretch(1)
        return page
