"""Deterministic regression tests for the gallery theme mode handler."""

from unittest.mock import patch

import pytest
from examples.gallery.main import GalleryUiWindow
from qtpy import QtWidgets


@pytest.mark.parametrize(
    ("index", "expected_mode"),
    [(0, "dark"), (1, "light"), (2, "dark")],
)
def test_theme_changed_only_sets_mode(index, expected_mode, qapp: QtWidgets.QApplication):
    window = GalleryUiWindow(qapp)
    with (
        patch("examples.gallery.main.setThemeMode") as mock_set_mode,
        patch("examples.gallery.main.setTheme") as mock_set_theme,
        patch("examples.gallery.main.setStyleSheet") as mock_set_style,
        patch.object(window, "_refresh_editor_widgets") as mock_refresh,
    ):
        window._on_theme_changed(index)

    assert window._active_mode == expected_mode
    mock_set_mode.assert_called_once_with(
        ["auto", "light", "dark"][index], target=window, save=False
    )
    mock_set_theme.assert_not_called()
    mock_set_style.assert_not_called()
    mock_refresh.assert_called_once_with()
