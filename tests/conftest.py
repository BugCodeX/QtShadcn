"""Shared pytest fixtures."""

import pytest
from qtshadcn.common.binding import QtWidgets


@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication instance for the test session."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app
    app.deleteLater()
