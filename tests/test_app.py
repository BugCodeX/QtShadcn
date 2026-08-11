"""Tests for the QtShadcn theme application."""

from pathlib import Path
from unittest.mock import patch

import pytest
from qtpy import QtWidgets
from qtshadcn.common.cache import _load_theme_cache
from qtshadcn.common.theme import apply_theme
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
    """Tests for the apply_theme function."""

    def test_applies_theme_and_returns_active_palette(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that the theme is applied and the active palette is returned."""
        tokens = apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_explicit_dark_palette(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the dark palette is applied."""
        tokens = apply_theme(qapp, theme_file=str(sample_xml), theme_mode="dark")
        assert tokens.background == "#020617"

    def test_default_theme_applies_without_source_path(self, qapp: QtWidgets.QApplication):
        """Test that the default theme is applied without a source path."""
        tokens = apply_theme(qapp, theme_mode="light")
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_apply_theme_without_app_uses_instance(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that passing no app uses the existing QApplication instance."""
        tokens = apply_theme(theme_file=str(sample_xml), theme_mode="light")
        assert tokens.background == "#ffffff"
        assert qapp.styleSheet() != ""

    def test_apply_theme_without_app_and_no_instance_raises(self):
        """Test that passing no app when no instance exists raises an error."""
        with (
            patch.object(QtWidgets.QApplication, "instance", return_value=None),
            pytest.raises(QtShadcnError, match="No QApplication instance found"),
        ):
            apply_theme(theme_file="theme.xml", theme_mode="light")

    def test_missing_file_raises_theme_parse_error(self, qapp: QtWidgets.QApplication):
        """Test that a missing file raises a ThemeParseError."""
        with pytest.raises(ThemeParseError, match="Could not read theme source"):
            apply_theme(qapp, theme_file="missing-theme.xml", theme_mode="light")

    def test_auto_mode_selects_dark_when_detected(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that the auto mode selects dark when detected."""
        with patch("qtshadcn.common.theme_mode.darkdetect.theme", return_value="Dark"):
            tokens = apply_theme(qapp, theme_file=str(sample_xml), theme_mode="auto")
        assert tokens.background == "#020617"

    def test_auto_mode_selects_light_when_detected(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that the auto mode selects light when detected."""
        with patch("qtshadcn.common.theme_mode.darkdetect.theme", return_value="Light"):
            tokens = apply_theme(qapp, theme_file=str(sample_xml), theme_mode="auto")
        assert tokens.background == "#ffffff"

    def test_auto_mode_uses_default_theme_when_detection_fails(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that auto mode falls back to default_theme when detection fails."""
        with patch("qtshadcn.common.theme_mode.darkdetect.theme", return_value=None):
            tokens = apply_theme(
                qapp,
                theme_file=str(sample_xml),
                theme_mode="auto",
                default_theme="light",
            )
        assert tokens.background == "#ffffff"

    def test_invalid_theme_mode_raises(self, qapp: QtWidgets.QApplication):
        """Test that an invalid theme_mode raises QtShadcnError."""
        with pytest.raises(QtShadcnError, match="Invalid theme_mode"):
            apply_theme(qapp, theme_mode="invalid")

    def test_invalid_default_theme_raises(self, qapp: QtWidgets.QApplication):
        """Test that an invalid default_theme raises QtShadcnError."""
        with pytest.raises(QtShadcnError, match="Invalid default_theme"):
            apply_theme(qapp, default_theme="invalid")

    def test_json_rejected(self, qapp: QtWidgets.QApplication, tmp_path: Path):
        """Test that JSON files are rejected."""
        path = tmp_path / "theme.json"
        path.write_text("{}", encoding="utf-8")
        with pytest.raises(ThemeParseError, match="JSON"):
            apply_theme(qapp, theme_file=str(path), theme_mode="light")

    def test_css_rejected(self, qapp: QtWidgets.QApplication, tmp_path: Path):
        """Test that CSS files are rejected."""
        path = tmp_path / "theme.css"
        path.write_text("* { color: red; }", encoding="utf-8")
        with pytest.raises(ThemeParseError, match="CSS"):
            apply_theme(qapp, theme_file=str(path), theme_mode="light")


class TestCustomTokens:
    """Tests for custom token overrides."""

    def test_shared_custom_tokens_apply_to_both_palettes(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that shared custom tokens apply to both palettes."""
        tokens = apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="light",
            custom_tokens={"background": "#123456"},
        )
        assert tokens.background == "#123456"

        tokens_dark = apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="dark",
            custom_tokens={"background": "#123456"},
        )
        assert tokens_dark.background == "#123456"

    def test_mode_specific_custom_tokens(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that mode-specific custom tokens apply per palette."""
        tokens = apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="light",
            custom_tokens={
                "light": {"background": "#abcdef"},
                "dark": {"background": "#fedcba"},
            },
        )
        assert tokens.background == "#abcdef"

        tokens_dark = apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="dark",
            custom_tokens={
                "light": {"background": "#abcdef"},
                "dark": {"background": "#fedcba"},
            },
        )
        assert tokens_dark.background == "#fedcba"

    def test_custom_tokens_are_resolved(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that custom token values are resolved before use."""
        tokens = apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="light",
            custom_tokens={"background": "oklch(0.21 0.006 285.885)"},
        )
        assert tokens.background.startswith("rgb(")


class TestAdditionalQss:
    """Tests for additional QSS snippets."""

    def test_inline_additional_qss_is_appended(
        self, qapp: QtWidgets.QApplication, sample_xml: Path
    ):
        """Test that an inline additional_qss string is appended."""
        apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="light",
            additional_qss="QWidget { color: red; }",
        )
        assert "QWidget { color: red; }" in qapp.styleSheet()

    def test_additional_qss_file_is_appended(
        self, qapp: QtWidgets.QApplication, sample_xml: Path, tmp_path: Path
    ):
        """Test that a .qss file path is loaded and appended."""
        qss_path = tmp_path / "extra.qss"
        qss_path.write_text("QWidget { color: blue; }", encoding="utf-8")

        apply_theme(
            qapp,
            theme_file=str(sample_xml),
            theme_mode="light",
            additional_qss=str(qss_path),
        )
        assert "QWidget { color: blue; }" in qapp.styleSheet()


class TestCache:
    """Tests for the theme cache."""

    def test_cache_stores_config_and_theme(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the cache stores the config and theme."""
        apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")

        saved_config, saved_theme, saved_mtime = _load_theme_cache()
        assert saved_config is not None
        assert saved_theme is not None
        assert saved_mtime is not None
        assert saved_config.theme_file == str(sample_xml)

    def test_cache_reused_on_same_mtime(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the cache is reused on the same mtime."""
        apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")

        with patch("qtshadcn.common.theme.parse_theme_source") as mock_parse:
            apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")
            mock_parse.assert_not_called()

    def test_cache_refreshed_on_source_change(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that the cache is refreshed when the source file changes."""
        apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")

        # Modify the source file to change its mtime.
        sample_xml.write_text(SAMPLE_XML + "\n<!-- changed -->\n", encoding="utf-8")

        with patch("qtshadcn.common.theme.parse_theme_source") as mock_parse:
            mock_parse.return_value = _load_theme_cache()[1]  # cached theme
            apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")
            mock_parse.assert_called_once()

    def test_cache_includes_custom_tokens(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that changing custom_tokens invalidates the cache."""
        apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")
        cached_theme = _load_theme_cache()[1]

        with patch("qtshadcn.common.theme.parse_theme_source") as mock_parse:
            mock_parse.return_value = cached_theme
            apply_theme(
                qapp,
                theme_file=str(sample_xml),
                theme_mode="light",
                custom_tokens={"background": "#000000"},
            )
            mock_parse.assert_called_once()

    def test_cache_includes_additional_qss(self, qapp: QtWidgets.QApplication, sample_xml: Path):
        """Test that changing additional_qss invalidates the cache."""
        apply_theme(qapp, theme_file=str(sample_xml), theme_mode="light")
        cached_theme = _load_theme_cache()[1]

        with patch("qtshadcn.common.theme.parse_theme_source") as mock_parse:
            mock_parse.return_value = cached_theme
            apply_theme(
                qapp,
                theme_file=str(sample_xml),
                theme_mode="light",
                additional_qss="QWidget { color: green; }",
            )
            mock_parse.assert_called_once()
