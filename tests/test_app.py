"""Tests for the QtShadcn theme application."""

from pathlib import Path
from unittest.mock import patch

import pytest
from qtpy import QtWidgets
from qtshadcn import getTheme, setStyleSheet, setTheme, setThemeMode
from qtshadcn.exceptions import QtShadcnError, ThemeParseError

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
    """Tests for the high-level theme application flow."""

    def test_applies_theme_and_returns_active_palette(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that the theme is applied and the active palette is returned."""
        setThemeMode("light", save=False)
        setTheme(sample_xml, save=False)
        tokens = getTheme()
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_explicit_dark_palette(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the dark palette is applied."""
        setThemeMode("dark", save=False)
        setTheme(sample_xml, save=False)
        tokens = getTheme()
        assert tokens.background == "#020617"

    def test_default_theme_applies_without_source_path(self, qapp: QtWidgets.QApplication):
        """Test that the default theme is applied without a source path."""
        setThemeMode("light", save=False)
        tokens = getTheme()
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_missing_file_raises_theme_parse_error(self, qapp: QtWidgets.QApplication):
        """Test that a missing file raises a ThemeParseError."""
        with pytest.raises(ThemeParseError, match="Could not read theme source"):
            setTheme("missing-theme.xml")

    def test_auto_mode_selects_dark_when_detected(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that the auto mode selects dark when detected."""
        setTheme(sample_xml, save=False)
        with patch("qtshadcn.common.stylesheet.darkdetect.theme", return_value="Dark"):
            setThemeMode("auto", save=False)
            tokens = getTheme()
        assert tokens.background == "#020617"

    def test_auto_mode_selects_light_when_detected(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that the auto mode selects light when detected."""
        setTheme(sample_xml, save=False)
        with patch("qtshadcn.common.stylesheet.darkdetect.theme", return_value="Light"):
            setThemeMode("auto", save=False)
            tokens = getTheme()
        assert tokens.background == "#ffffff"

    def test_auto_mode_falls_back_to_dark_when_detection_fails(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that auto mode falls back to dark when OS detection fails."""
        setTheme(sample_xml, save=False)
        with patch("qtshadcn.common.stylesheet.darkdetect.theme", return_value=None):
            setThemeMode("auto", save=False)
            tokens = getTheme()
        assert tokens.background == "#020617"

    def test_invalid_theme_mode_raises(self, qapp: QtWidgets.QApplication):
        """Test that an invalid theme_mode raises QtShadcnError."""
        with pytest.raises(QtShadcnError, match="Invalid theme_mode"):
            setThemeMode("invalid")

    def test_css_rejected(self, qapp: QtWidgets.QApplication, tmp_path: Path):
        """Test that CSS files are rejected."""
        path = tmp_path / "theme.css"
        path.write_text("* { color: red; }", encoding="utf-8")
        with pytest.raises(ThemeParseError, match="CSS"):
            setTheme(path)


class TestCustomTokens:
    """Tests for custom token overrides."""

    def test_shared_custom_tokens_apply_to_both_palettes(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that shared custom tokens apply to both palettes."""
        setThemeMode("light", save=False)
        setTheme(sample_xml, custom_tokens={"background": "#123456"}, save=False)
        tokens = getTheme()
        assert tokens.background == "#123456"

        setThemeMode("dark", save=False)
        setTheme(sample_xml, custom_tokens={"background": "#123456"}, save=False)
        tokens_dark = getTheme()
        assert tokens_dark.background == "#123456"

    def test_mode_specific_custom_tokens(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that mode-specific custom tokens apply per palette."""
        setThemeMode("light", save=False)
        setTheme(
            sample_xml,
            custom_tokens={
                "light": {"background": "#abcdef"},
                "dark": {"background": "#fedcba"},
            },
            save=False,
        )
        tokens = getTheme()
        assert tokens.background == "#abcdef"

        setThemeMode("dark", save=False)
        setTheme(
            sample_xml,
            custom_tokens={
                "light": {"background": "#abcdef"},
                "dark": {"background": "#fedcba"},
            },
            save=False,
        )
        tokens_dark = getTheme()
        assert tokens_dark.background == "#fedcba"

    def test_custom_tokens_are_resolved(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that custom token values are resolved before use."""
        setThemeMode("light", save=False)
        setTheme(
            sample_xml,
            custom_tokens={"background": "oklch(0.21 0.006 285.885)"},
            save=False,
        )
        tokens = getTheme()
        assert tokens.background.startswith("rgb(")


class TestAdditionalQss:
    """Tests for additional QSS snippets."""

    def test_inline_additional_qss_is_appended(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that an inline additional_qss string is appended."""
        setThemeMode("light", save=False)
        setTheme(sample_xml, save=False)
        setStyleSheet("QWidget { color: red; }", save=False)
        assert "QWidget { color: red; }" in qapp.styleSheet()

    def test_additional_qss_file_is_appended(
        self, qapp: QtWidgets.QApplication, sample_xml: Path, tmp_path: Path
    ):
        """Test that a .qss file path is loaded and appended."""
        qss_path = tmp_path / "extra.qss"
        qss_path.write_text("QWidget { color: blue; }", encoding="utf-8")

        setThemeMode("light", save=False)
        setTheme(sample_xml, save=False)
        setStyleSheet(qss_path, save=False)
        assert "QWidget { color: blue; }" in qapp.styleSheet()
