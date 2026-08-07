"""QTabWidget page for the gallery."""

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


class TabWidgetPage:
    """QTabWidget page for the gallery."""

    label: ClassVar[str] = "QTabWidget"

    def build(self) -> QtWidgets.QWidget:
        """Build the QTabWidget page covering default, line, vertical and disabled variants."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.setContentsMargins(_PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN, _PAGE_MARGIN)
        layout.setSpacing(_SPACING)

        layout.addWidget(page_title("QTabWidget"))
        layout.addWidget(
            muted_label(
                "Tabbed containers with default pills, line, vertical, and disabled variants."
            )
        )
        layout.addWidget(separator())

        layout.addWidget(section_label("Default"))
        layout.addWidget(self._default_tab_widget())

        layout.addWidget(section_label("Line"))
        layout.addWidget(self._line_tab_widget())

        layout.addWidget(section_label("Vertical line"))
        layout.addWidget(self._vertical_line_tab_widget())

        layout.addWidget(section_label("Disabled"))
        layout.addWidget(self._disabled_tab_widget())

        layout.addStretch(1)
        return page

    def _default_tab_widget(self) -> QtWidgets.QTabWidget:
        """Return a default pill-style tab widget."""
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._placeholder("Account content", padded=True), "Account")
        tabs.addTab(self._placeholder("Password content", padded=True), "Password")
        return tabs

    def _line_tab_widget(self) -> QtWidgets.QTabWidget:
        """Return a line-variant tab widget."""
        tabs = QtWidgets.QTabWidget()
        tabs.setProperty("variant", "line")
        tabs.addTab(self._placeholder("Profile content"), "Profile")
        tabs.addTab(self._placeholder("Settings content"), "Settings")
        return tabs

    def _vertical_line_tab_widget(self) -> QtWidgets.QTabWidget:
        """Return a vertical line-variant tab widget."""
        tabs = QtWidgets.QTabWidget()
        tabs.setProperty("variant", "line")
        tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        tabs.addTab(self._placeholder("General content"), "General")
        tabs.addTab(self._placeholder("Advanced content"), "Advanced")
        return tabs

    def _disabled_tab_widget(self) -> QtWidgets.QTabWidget:
        """Return a disabled default tab widget."""
        tabs = QtWidgets.QTabWidget()
        tabs.setEnabled(False)
        tabs.addTab(self._placeholder("Tab one content"), "Tab one")
        tabs.addTab(self._placeholder("Tab two content"), "Tab two")
        return tabs

    def _placeholder(self, text: str, padded: bool = False) -> QtWidgets.QWidget:
        """Return a placeholder page with the given description text."""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        if padded:
            layout.setContentsMargins(_SPACING, _SPACING, _SPACING, _SPACING)
        layout.addWidget(QtWidgets.QLabel(text))
        layout.addStretch(1)
        return widget
