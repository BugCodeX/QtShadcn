"""QPushButton page for the gallery."""

from __future__ import annotations

from typing import ClassVar

from examples.gallery.pages._helpers import (
    _PAGE_MARGIN,
    _SPACING,
    QPushButtonVariantRow,
    muted_label,
    page_title,
    section_label,
    separator,
    variant_grid,
)
from qtshadcn._qt import QtWidgets


class PushButtonPage:
    """QPushButton page for the gallery."""

    label: ClassVar[str] = "QPushButton"

    def build(self) -> QtWidgets.QWidget:
        """Build the QPushButton page covering variants, sizes, and states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QPushButton"))
        layout.addWidget(
            muted_label(
                "Buttons support variant and size properties, plus enabled and disabled states."
            )
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("Variants"))
        layout.addLayout(variant_grid(QPushButtonVariantRow))

        layout.addWidget(section_label("Sizes"))
        sizes = QtWidgets.QHBoxLayout()
        sizes.setSpacing(_SPACING)
        for size, label in [
            ("xs", "Extra small"),
            ("sm", "Small"),
            ("default", "Default"),
            ("lg", "Large"),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setProperty("size", size)
            sizes.addWidget(btn)
        layout.addLayout(sizes)

        layout.addWidget(section_label("Icon sizes"))
        icon_sizes = QtWidgets.QHBoxLayout()
        icon_sizes.setSpacing(_SPACING)
        for size, label in [
            ("icon-xs", "XS"),
            ("icon-sm", "S"),
            ("icon", "M"),
            ("icon-lg", "L"),
        ]:
            btn = QtWidgets.QPushButton(label)
            btn.setProperty("variant", "outline")
            btn.setProperty("size", size)
            icon_sizes.addWidget(btn)
        layout.addLayout(icon_sizes)

        layout.addStretch(1)
        return page
