"""Tests for the QtShadcn XML theme parser."""

from pathlib import Path

import pytest
from qtshadcn.common.theme_parser import parse_theme_source
from qtshadcn.exceptions import ThemeParseError

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
    <spacing>4px</spacing>
    <radius>8px</radius>
    <font_family>Open Sans</font_family>
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
    <spacing>4px</spacing>
    <radius>8px</radius>
    <font_family>Open Sans</font_family>
  </dark>
</theme>
"""


@pytest.fixture
def sample_xml(tmp_path: Path) -> Path:
    """Return a path to a temporary theme.xml file."""
    path = tmp_path / "theme.xml"
    path.write_text(SAMPLE_XML, encoding="utf-8")
    return path


class TestParseThemeSource:
    """Tests for the theme parser."""

    def test_parses_light_and_dark(self, sample_xml: Path):
        """Test that the parser parses both light and dark themes."""
        theme = parse_theme_source(sample_xml)
        assert theme.light.background == "#ffffff"
        assert theme.dark.background == "#020617"

    def test_missing_light_section_fails(self, tmp_path: Path):
        """Test that a missing light section fails parsing."""
        path = tmp_path / "theme.xml"
        path.write_text(
            "<theme><dark><background>#000000</background></dark></theme>",
            encoding="utf-8",
        )
        with pytest.raises(ThemeParseError, match="<light>"):
            parse_theme_source(path)

    def test_missing_dark_section_fails(self, tmp_path: Path):
        """Test that a missing dark section fails parsing."""
        path = tmp_path / "theme.xml"
        path.write_text(
            "<theme><light><background>#ffffff</background></light></theme>",
            encoding="utf-8",
        )
        with pytest.raises(ThemeParseError, match="<dark>"):
            parse_theme_source(path)

    def test_missing_file_fails(self, tmp_path: Path):
        """Test that a missing file fails parsing."""
        with pytest.raises(ThemeParseError, match="not found"):
            parse_theme_source(tmp_path / "missing.xml")

    def test_json_rejected(self, tmp_path: Path):
        """Test that JSON files are rejected."""
        path = tmp_path / "theme.json"
        path.write_text("{}", encoding="utf-8")
        with pytest.raises(ThemeParseError, match="JSON"):
            parse_theme_source(path)

    def test_css_rejected(self, tmp_path: Path):
        """Test that CSS files are rejected."""
        path = tmp_path / "theme.css"
        path.write_text("* { color: red; }", encoding="utf-8")
        with pytest.raises(ThemeParseError, match="CSS"):
            parse_theme_source(path)

    def test_url_rejected(self):
        """Test that URLs are rejected."""
        with pytest.raises(ThemeParseError, match="URL"):
            parse_theme_source("https://example.com/theme.xml")

    def test_unknown_token_ignored(self, sample_xml: Path):
        """Test that unknown tokens are ignored."""
        theme = parse_theme_source(sample_xml)
        assert "unknown_token" not in theme.light.model_dump()

    def test_custom_theme_missing_required_token_fails(self, tmp_path: Path):
        """Test that a custom theme missing a required token fails parsing."""
        path = tmp_path / "theme.xml"
        path.write_text(
            SAMPLE_XML.replace("    <secondary>#f1f5f9</secondary>\n", ""), encoding="utf-8"
        )
        with pytest.raises(ThemeParseError, match=r"<light>.*secondary"):
            parse_theme_source(path)

    def test_packaged_default_theme_is_complete(self):
        """Test that the packaged default theme is complete."""
        path = Path(__file__).resolve().parent.parent / "qtshadcn" / "themes" / "default.xml"
        theme = parse_theme_source(path)
        assert theme.light.secondary == "#f5f5f5"
        assert theme.dark.secondary == "#262626"

    def test_values_are_passed_through(self, sample_xml: Path):
        """Test that raw HEX and px values are used unchanged."""
        theme = parse_theme_source(sample_xml)
        assert theme.light.radius == "8px"
        assert theme.light.spacing == "4px"
        assert theme.light.primary == "#0f172a"
