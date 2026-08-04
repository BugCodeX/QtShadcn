"""Integration tests for the gallery example."""

from qtshadcn._qt import QtWidgets
from qtshadcn.app import apply_theme
from qtshadcn.models import ThemeConfig


def test_gallery_window_creates_pages(qapp: QtWidgets.QApplication):
    """Test that the gallery window creates all expected pages."""
    from examples.gallery.main import GalleryWindow

    window = GalleryWindow(qapp)
    assert window._stack.count() == 6
    assert window._sidebar.count() == 6
    labels = [window._sidebar.item(i).text() for i in range(window._sidebar.count())]
    assert labels == [
        "Overview",
        "QPushButton",
        "QToolButton",
        "QLineEdit",
        "QTextEdit",
        "QCheckBox",
    ]


def test_gallery_theme_toggle_reapplies_qss(qapp: QtWidgets.QApplication):
    """Test that the gallery toggle reapplies the theme and refreshes the window."""
    from examples.gallery.main import GalleryWindow

    apply_theme(qapp, ThemeConfig(theme_mode="light"))
    light_sheet = qapp.styleSheet()
    assert light_sheet != ""

    window = GalleryWindow(qapp)
    window._theme_toggle.setChecked(True)
    window._on_theme_toggled(True)

    dark_sheet = qapp.styleSheet()
    assert dark_sheet != ""
    assert dark_sheet != light_sheet
    assert window._theme_toggle.text() == "Light mode"


def test_gallery_sidebar_switch_changes_page(qapp: QtWidgets.QApplication):
    """Test that selecting a sidebar item changes the visible page."""
    from examples.gallery.main import GalleryWindow

    window = GalleryWindow(qapp)
    window._sidebar.setCurrentRow(2)
    assert window._stack.currentIndex() == 2
