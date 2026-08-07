"""Shared helpers for building gallery pages."""

from __future__ import annotations

from qtshadcn._qt import QtWidgets

_PAGE_MARGIN = 24
_SPACING = 16


def page_title(text: str) -> QtWidgets.QLabel:
    """Return a page title label."""
    label = QtWidgets.QLabel(text)
    label.setProperty("class", "h3")
    return label


def section_label(text: str) -> QtWidgets.QLabel:
    """Return a section label."""
    label = QtWidgets.QLabel(text)
    label.setProperty("class", "h4")
    return label


def muted_label(text: str) -> QtWidgets.QLabel:
    """Return a muted description label."""
    label = QtWidgets.QLabel(text)
    label.setProperty("class", "muted")
    label.setWordWrap(True)
    return label


def separator() -> QtWidgets.QFrame:
    """Return a horizontal separator line."""
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
    line.setProperty("class", "separator")
    return line


def variant_grid(row_class: type[QtWidgets.QHBoxLayout]) -> QtWidgets.QGridLayout:
    """Return a grid of variant rows for buttons."""
    grid = QtWidgets.QGridLayout()
    grid.setSpacing(_SPACING)

    variants = ["default", "outline", "secondary", "ghost", "destructive"]
    for row, variant in enumerate(variants):
        grid.addWidget(QtWidgets.QLabel(variant), row, 0)
        grid.addLayout(row_class(variant), row, 1)
    return grid


def _button_with_property(variant: str, enabled: bool) -> QtWidgets.QPushButton:
    """Create a QPushButton with the given variant and enabled state."""
    btn = QtWidgets.QPushButton(variant.capitalize())
    btn.setProperty("variant", variant)
    btn.setEnabled(enabled)
    return btn


def _tool_button_with_property(variant: str, enabled: bool) -> QtWidgets.QToolButton:
    """Create a QToolButton with the given variant and enabled state."""
    btn = QtWidgets.QToolButton()
    btn.setText(variant.capitalize())
    btn.setProperty("variant", variant)
    btn.setEnabled(enabled)
    return btn


class QPushButtonVariantRow(QtWidgets.QHBoxLayout):
    """Row showing an enabled and disabled QPushButton for a variant."""

    def __init__(self, variant: str) -> None:
        """Create a row with enabled and disabled push buttons for the variant."""
        super().__init__()
        self.setSpacing(_SPACING)
        self.addWidget(_button_with_property(variant, True))
        self.addWidget(_button_with_property(variant, False))
        self.addStretch(1)


class QToolButtonVariantRow(QtWidgets.QHBoxLayout):
    """Row showing an enabled and disabled QToolButton for a variant."""

    def __init__(self, variant: str) -> None:
        """Create a row with enabled and disabled tool buttons for the variant."""
        super().__init__()
        self.setSpacing(_SPACING)
        self.addWidget(_tool_button_with_property(variant, True))
        self.addWidget(_tool_button_with_property(variant, False))
        self.addStretch(1)
