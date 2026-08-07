"""Compact page selector for the gallery."""

from __future__ import annotations

from qtshadcn._qt import QtWidgets, Signal


class PageSelector(QtWidgets.QWidget):
    """Compact selector that wraps a QComboBox for choosing gallery pages."""

    currentIndexChanged = Signal(int)

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        """Create a page selector with a drop-down of page labels."""
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self._combo = QtWidgets.QComboBox()
        self._combo.currentIndexChanged.connect(self.currentIndexChanged.emit)
        layout.addWidget(self._combo)

    def add_page(self, label: str) -> None:
        """Add a page label to the selector."""
        self._combo.addItem(label)

    def count(self) -> int:
        """Return the number of pages in the selector."""
        return self._combo.count()

    def setCurrentRow(self, row: int) -> None:
        """Select the page at the given zero-based index."""
        self._combo.setCurrentIndex(row)
