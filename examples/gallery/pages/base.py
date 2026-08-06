"""Gallery page protocol."""

from __future__ import annotations

from typing import ClassVar, Protocol

from qtshadcn._qt import QtWidgets


class GalleryPage(Protocol):
    """A single gallery page that can build its own widget."""

    label: ClassVar[str]

    def build(self) -> QtWidgets.QWidget:
        """Build and return the page widget."""
        ...
