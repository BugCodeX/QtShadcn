from examples.gallery.pages import PAGE_REGISTRY, build_pages
from qtshadcn._qt import QtWidgets


def test_page_registry_has_fourteen_unique_labels():
    """The registry must list fourteen pages with unique labels."""
    labels = [label for label, _ in PAGE_REGISTRY]
    assert len(labels) == 14
    assert len(set(labels)) == 14


def test_page_registry_builds_all_pages(qapp: QtWidgets.QApplication):
    """Every registered page builder must return a non-null QWidget."""
    pages = build_pages()
    assert len(pages) == 14
    for page in pages:
        assert page is not None
        assert isinstance(page, QtWidgets.QWidget)
