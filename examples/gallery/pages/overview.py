"""Overview page for the gallery."""

from __future__ import annotations

from typing import ClassVar

from examples.gallery.pages._helpers import (
    _PAGE_MARGIN,
    _SPACING,
    muted_label,
    section_label,
    separator,
)
from qtshadcn._qt import QtCore, QtGui, QtWidgets, Signal


class OverviewPage(QtCore.QObject):
    """Overview page for the gallery."""

    label: ClassVar[str] = "Overview"
    navigateToPage = Signal(str)

    def build(self) -> QtWidgets.QWidget:
        """Build the overview page."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addLayout(self._build_header())
        layout.addWidget(separator())
        layout.addWidget(section_label(self._components_section_title()))
        layout.addLayout(self._build_component_grid())
        layout.addStretch(1)
        return page

    def _build_header(self) -> QtWidgets.QHBoxLayout:
        """Build a horizontal header with the logo and tagline."""
        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(_SPACING)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        logo = self._load_logo()
        if logo is not None:
            logo_label = QtWidgets.QLabel()
            logo_label.setPixmap(logo)
            layout.addWidget(logo_label)

        tagline = muted_label(
            "Modern styling and theming for Qt/PySide and PyQt applications. "
            "Load an XML theme, call apply_theme(), and your widgets look like shadcn/ui."
        )
        layout.addWidget(tagline, 1)

        return layout

    def _components_section_title(self) -> str:
        """Return the section title including the component count."""
        from examples.gallery.pages import PAGE_REGISTRY

        count = sum(1 for label, _ in PAGE_REGISTRY if label != "Overview")
        return f"All Components ({count})"

    def _build_component_grid(self) -> QtWidgets.QGridLayout:
        """Build a 3-column grid of clickable component links."""
        from examples.gallery.pages import PAGE_REGISTRY

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(_SPACING)

        column = 0
        row = 0
        for label, _ in PAGE_REGISTRY:
            if label == "Overview":
                continue
            link = self._build_component_link(label)
            grid.addWidget(link, row, column)
            column += 1
            if column > 2:
                column = 0
                row += 1

        return grid

    def _build_component_link(self, label: str) -> QtWidgets.QPushButton:
        """Build a clickable component name that emits the navigation signal."""
        button = QtWidgets.QPushButton(label)
        button.setProperty("variant", "link")
        button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        button.setStyleSheet("text-align: left;")
        button.clicked.connect(lambda _checked, name=label: self._on_component_clicked(name))
        return button

    def _on_component_clicked(self, label: str) -> None:
        """Emit the navigation signal when a component link is clicked."""
        self.navigateToPage.emit(label)

    def _load_logo(self) -> QtGui.QPixmap | None:
        """Load the project logo if available."""
        from pathlib import Path

        logo_path = Path(__file__).resolve().parents[3] / "docs" / "source" / "logo.png"
        if not logo_path.exists():
            return None
        pixmap = QtGui.QPixmap(str(logo_path))
        if pixmap.isNull():
            return None
        return pixmap.scaled(
            64,
            64,
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation,
        )
