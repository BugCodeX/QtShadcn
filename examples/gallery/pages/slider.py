"""QSlider page for the gallery."""

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
from qtshadcn._qt import QtCore, QtWidgets


class SliderPage:
    """QSlider page for the gallery."""

    label: ClassVar[str] = "QSlider"

    def build(self) -> QtWidgets.QWidget:
        """Build the QSlider page covering common slider states."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QSlider"))
        layout.addWidget(
            muted_label(
                "Numeric range selector with horizontal, vertical, and disabled states."
            )
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("Horizontal"))
        horizontal = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        horizontal.setRange(0, 100)
        horizontal.setValue(50)
        layout.addWidget(horizontal)

        layout.addWidget(section_label("Vertical"))
        vertical_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        vertical_slider.setRange(0, 100)
        vertical_slider.setValue(30)
        vertical_slider.setMinimumHeight(120)
        layout.addWidget(vertical_slider)

        layout.addWidget(section_label("Disabled"))
        disabled = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        disabled.setRange(0, 100)
        disabled.setValue(70)
        disabled.setEnabled(False)
        layout.addWidget(disabled)

        layout.addStretch(1)
        return page
