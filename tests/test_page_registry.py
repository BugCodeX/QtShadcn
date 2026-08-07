from examples.gallery.pages import PAGE_REGISTRY, build_pages
from qtshadcn._qt import QtWidgets


def test_page_registry_has_twelve_unique_labels():
    """The registry must list twelve pages with unique labels."""
    labels = [label for label, _ in PAGE_REGISTRY]
    assert len(labels) == 12
    assert len(set(labels)) == 12


def test_page_registry_builds_all_pages(qapp: QtWidgets.QApplication):
    """Every registered page builder must return a non-null QWidget."""
    pages = build_pages()
    assert len(pages) == 12
    for page in pages:
        assert page is not None
        assert isinstance(page, QtWidgets.QWidget)
