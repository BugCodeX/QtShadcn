"""Shared pytest fixtures."""

import pytest
from qtpy import QtGui, QtWidgets


@pytest.fixture(scope="session")
def qapp():
    """Provide a single QApplication instance for the test session."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app
    app.deleteLater()


@pytest.fixture(autouse=True)
def _reset_qapp_state(qapp):
    """Reset global QApplication state after each test to avoid leakage."""
    yield
    qapp.setStyleSheet("")
    qapp.setPalette(QtGui.QPalette())
