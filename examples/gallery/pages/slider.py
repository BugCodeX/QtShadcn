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
                "Numeric range selector with horizontal, vertical, tick, and disabled variants."
            )
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("Horizontal"))
        layout.addLayout(self._horizontal_row())

        layout.addWidget(section_label("Vertical"))
        layout.addLayout(self._vertical_row())

        layout.addWidget(section_label("States"))
        layout.addLayout(self._states_row())

        layout.addStretch(1)
        return page

    def _horizontal_row(self) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(_SPACING * 2)

        default = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        default.setRange(0, 100)
        default.setValue(50)
        self._set_horizontal_expanding(default)
        row.addWidget(self._labeled_group("Default", default), stretch=1)

        ticks = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        ticks.setRange(0, 100)
        ticks.setValue(25)
        ticks.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        ticks.setTickInterval(25)
        self._set_horizontal_expanding(ticks)
        row.addWidget(self._labeled_group("Ticks", ticks), stretch=1)

        labeled = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        labeled.setRange(0, 100)
        labeled.setValue(75)
        self._set_horizontal_expanding(labeled)
        row.addWidget(self._labeled_group("With value", labeled, show_value=True), stretch=1)

        return row

    def _vertical_row(self) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(_SPACING * 2)
        row.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        for label, value in (("Default", 60), ("Ticks", 40), ("Disabled", 80)):
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
            slider.setRange(0, 100)
            slider.setValue(value)
            slider.setMinimumHeight(260)
            slider.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Fixed,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
            if label == "Ticks":
                slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksRight)
                slider.setTickInterval(25)
            if label == "Disabled":
                slider.setEnabled(False)
            row.addWidget(self._labeled_group(label, slider))

        row.addStretch(1)
        return row

    def _states_row(self) -> QtWidgets.QHBoxLayout:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(_SPACING * 2)

        enabled = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        enabled.setRange(0, 100)
        enabled.setValue(50)
        self._set_horizontal_expanding(enabled)
        row.addWidget(self._labeled_group("Enabled", enabled), stretch=1)

        disabled = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        disabled.setRange(0, 100)
        disabled.setValue(70)
        disabled.setEnabled(False)
        self._set_horizontal_expanding(disabled)
        row.addWidget(self._labeled_group("Disabled", disabled), stretch=1)

        return row

    def _set_horizontal_expanding(self, slider: QtWidgets.QSlider) -> None:
        slider.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed,
        )
        slider.setMinimumWidth(160)

    def _labeled_group(
        self,
        label: str,
        slider: QtWidgets.QSlider,
        *,
        show_value: bool = False,
    ) -> QtWidgets.QWidget:
        group = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        header = QtWidgets.QHBoxLayout()
        header.setSpacing(8)
        header.addWidget(muted_label(label))

        value_label: QtWidgets.QLabel | None = None
        if show_value:
            value_label = QtWidgets.QLabel(str(slider.value()))
            value_label.setProperty("class", "muted")
            header.addWidget(value_label)
            slider.valueChanged.connect(value_label.setNum)

        header.addStretch(1)
        layout.addLayout(header)
        layout.addWidget(slider)
        return group
