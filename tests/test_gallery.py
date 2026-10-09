"""Deterministic regression tests for the gallery theme mode handler."""

from unittest.mock import patch

import pytest
from examples.gallery.main import CUSTOM_PATH, THEME_FILE, GalleryUiWindow
from qtpy import QtWidgets


@pytest.mark.parametrize(
    "index, expected_mode",
    [
        (0, "dark"),
        (1, "light"),
        (2, "dark"),
    ],
)
@patch("examples.gallery.main.setStyleSheet")
@patch("examples.gallery.main.setTheme")
@patch("examples.gallery.main.setThemeMode")
def test_theme_changed_only_sets_mode(
    mock_set_mode,
    mock_set_theme,
    mock_set_style,
    qapp: QtWidgets.QApplication,
    index: int,
    expected_mode: str,
):
    with patch.object(GalleryUiWindow, "_refresh_editor_widgets"):
        window = GalleryUiWindow(qapp)
        window._on_theme_changed(index)

    assert window._active_mode == expected_mode
    expected_call = ["auto", "light", "dark"][index]
    mock_set_mode.assert_called_once_with(expected_call, target=window, save=False)
    mock_set_theme.assert_called_once_with(THEME_FILE, target=window, save=False)
    mock_set_style.assert_called_once_with(CUSTOM_PATH, target=window, save=False)
