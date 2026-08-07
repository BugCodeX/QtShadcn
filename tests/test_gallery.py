"""Integration tests for the gallery example."""

from examples.gallery.pages import PAGE_REGISTRY, build_pages
from examples.gallery.window import GalleryWindow
from qtshadcn._qt import QtWidgets


def test_build_pages_returns_fourteen_qwidgets(qapp: QtWidgets.QApplication):
    """Test that build_pages returns 14 QWidget instances."""
    pages = build_pages()
    assert len(pages) == 14
    for page in pages:
        assert page is not None
        assert isinstance(page, QtWidgets.QWidget)


def test_gallery_window_creates_pages(qapp: QtWidgets.QApplication):
    """Test that the gallery window mounts all expected pages."""
    window = GalleryWindow(qapp)
    assert window._stack.count() == 14
    assert window._selector.count() == 14

    labels = [window._selector._combo.itemText(i) for i in range(window._selector.count())]
    assert labels == [label for label, _ in PAGE_REGISTRY]


def test_gallery_theme_toggle_reapplies_qss(qapp: QtWidgets.QApplication):
    """Test that toggling the theme mode applies a different QSS stylesheet."""
    window = GalleryWindow(qapp)
    light_sheet = qapp.styleSheet()
    assert light_sheet != ""

    window.apply_theme("dark")
    dark_sheet = qapp.styleSheet()
    assert dark_sheet != ""
    assert dark_sheet != light_sheet
    assert window._theme_toggle.text() == "Light mode"


def test_gallery_selector_switch_changes_page(qapp: QtWidgets.QApplication):
    """Test that selecting a page in the selector changes the visible page."""
    window = GalleryWindow(qapp)
    window._selector.setCurrentRow(2)
    assert window._stack.currentIndex() == 2
