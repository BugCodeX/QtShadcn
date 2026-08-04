"""Tests for the QtShadcn theme application."""

from pathlib import Path
from unittest.mock import patch

import pytest
from qtshadcn._qt import QtWidgets
from qtshadcn.app import _load_theme_cache, apply_theme
from qtshadcn.models import ThemeConfig
from qtshadcn._parser import ThemeParseError

SAMPLE_XML = """\
<theme>
  <light>
    <background>#ffffff</background>
    <foreground>#020617</foreground>
    <card>#ffffff</card>
    <card_foreground>#020617</card_foreground>
    <popover>#ffffff</popover>
    <popover_foreground>#020617</popover_foreground>
    <primary>#0f172a</primary>
    <primary_foreground>#f8fafc</primary_foreground>
    <secondary>#f1f5f9</secondary>
    <secondary_foreground>#0f172a</secondary_foreground>
    <muted>#f1f5f9</muted>
    <muted_foreground>#64748b</muted_foreground>
    <accent>#f1f5f9</accent>
    <accent_foreground>#0f172a</accent_foreground>
    <destructive>#ef4444</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#e2e8f0</border>
    <input>#e2e8f0</input>
    <ring>#0f172a</ring>
    <spacing>0.25rem</spacing>
    <radius>8px</radius>
    <font_family>system-ui, sans-serif</font_family>
  </light>
  <dark>
    <background>#020617</background>
    <foreground>#f8fafc</foreground>
    <card>#020617</card>
    <card_foreground>#f8fafc</card_foreground>
    <popover>#020617</popover>
    <popover_foreground>#f8fafc</popover_foreground>
    <primary>#f8fafc</primary>
    <primary_foreground>#0f172a</primary_foreground>
    <secondary>#1e293b</secondary>
    <secondary_foreground>#f8fafc</secondary_foreground>
    <muted>#1e293b</muted>
    <muted_foreground>#94a3b8</muted_foreground>
    <accent>#1e293b</accent>
    <accent_foreground>#f8fafc</accent_foreground>
    <destructive>#7f1d1d</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#1e293b</border>
    <input>#1e293b</input>
    <ring>#cbd5e1</ring>
    <spacing>0.25rem</spacing>
    <radius>8px</radius>
    <font_family>system-ui, sans-serif</font_family>
  </dark>
</theme>
"""


@pytest.fixture
def sample_xml(tmp_path: Path) -> Path:
    """Return a path to a temporary theme.xml file."""
    path = tmp_path / "theme.xml"
    path.write_text(SAMPLE_XML, encoding="utf-8")
    return path


class TestApplyTheme:
    """Tests for the apply_theme function."""

    def test_applies_theme_and_returns_active_palette(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the theme is applied and the active palette is returned."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="light")
        tokens = apply_theme(qapp, config)
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_explicit_dark_palette(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the dark palette is applied."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="dark")
        tokens = apply_theme(qapp, config)
        assert tokens.background == "#020617"

    def test_default_theme_applies_without_source_path(self, qapp: QtWidgets.QApplication):
        """Test that the default theme is applied without a source path."""
        config = ThemeConfig(theme_mode="light")
        tokens = apply_theme(qapp, config)
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_default_theme_applies_without_config(self, qapp: QtWidgets.QApplication):
        """Test that the default theme is applied without a config object."""
        with patch("qtshadcn.app.darkdetect.isDark", return_value=False):
            tokens = apply_theme(qapp)
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_missing_file_raises_theme_parse_error(self, qapp: QtWidgets.QApplication):
        """Test that a missing file raises a ThemeParseError."""
        config = ThemeConfig(theme_source_path="missing-theme.xml", theme_mode="light")
        with pytest.raises(ThemeParseError, match="Could not read theme source"):
            apply_theme(qapp, config)

    def test_auto_mode_selects_dark_when_detected(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the auto mode selects dark when detected."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="auto")
        with patch("qtshadcn.app.darkdetect.isDark", return_value=True):
            tokens = apply_theme(qapp, config)
        assert tokens.background == "#020617"

    def test_auto_mode_selects_light_when_not_detected(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the auto mode selects light when not detected."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="auto")
        with patch("qtshadcn.app.darkdetect.isDark", return_value=False):
            tokens = apply_theme(qapp, config)
        assert tokens.background == "#ffffff"

    def test_json_rejected(self, qapp: QtWidgets.QApplication, tmp_path: Path):
        """Test that JSON files are rejected."""
        path = tmp_path / "theme.json"
        path.write_text("{}", encoding="utf-8")
        config = ThemeConfig(theme_source_path=str(path), theme_mode="light")
        with pytest.raises(ThemeParseError, match="JSON"):
            apply_theme(qapp, config)

    def test_css_rejected(self, qapp: QtWidgets.QApplication, tmp_path: Path):
        """Test that CSS files are rejected."""
        path = tmp_path / "theme.css"
        path.write_text("* { color: red; }", encoding="utf-8")
        config = ThemeConfig(theme_source_path=str(path), theme_mode="light")
        with pytest.raises(ThemeParseError, match="CSS"):
            apply_theme(qapp, config)


class TestCache:
    """Tests for the theme cache."""

    def test_cache_stores_config_and_theme(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the cache stores the config and theme."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="light")
        apply_theme(qapp, config)

        saved_config, saved_theme, saved_mtime = _load_theme_cache()
        assert saved_config is not None
        assert saved_theme is not None
        assert saved_mtime is not None
        assert saved_config.theme_source_path == str(sample_xml)

    def test_cache_reused_on_same_mtime(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the cache is reused on the same mtime."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="light")
        apply_theme(qapp, config)

        with patch("qtshadcn.app.parse_theme_source") as mock_parse:
            apply_theme(qapp, config)
            mock_parse.assert_not_called()

    def test_cache_refreshed_on_source_change(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the cache is refreshed when the source file changes."""
        config = ThemeConfig(theme_source_path=str(sample_xml), theme_mode="light")
        apply_theme(qapp, config)

        # Modify the source file to change its mtime.
        sample_xml.write_text(SAMPLE_XML + "\n<!-- changed -->\n", encoding="utf-8")

        with patch("qtshadcn.app.parse_theme_source") as mock_parse:
            mock_parse.return_value = _load_theme_cache()[1]  # cached theme
            apply_theme(qapp, config)
            mock_parse.assert_called_once()
