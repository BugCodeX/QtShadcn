"""Tests for the QtShadcn XML theme parser."""

import re
from pathlib import Path

import pytest
from qtshadcn.common.theme_parser import parse_theme_source, resolve_value
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
    <primary>oklch(0.55 0.15 270)</primary>
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
    <radius>0.5rem</radius>
    <font_family>system-ui, sans-serif</font_family>
  </light>
  <dark>
    <background>#020617</background>
    <foreground>#f8fafc</foreground>
    <card>#020617</card>
    <card_foreground>#f8fafc</card_foreground>
    <popover>#020617</popover>
    <popover_foreground>#f8fafc</popover_foreground>
    <primary>oklch(0.85 0.05 270)</primary>
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
    <radius>0.5rem</radius>
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

    def test_convertible_value_not_defaulted(self, sample_xml: Path):
        """Test that convertible values are not defaulted."""
        theme = parse_theme_source(sample_xml)
        assert theme.light.radius == "8px"
        assert theme.light.spacing == "4px"
        assert theme.light.primary.startswith("rgb(")


class TestResolveValue:
    """Tests for the value resolver."""

    def test_oklch_to_rgb(self):
        """Test that oklch is converted to rgb."""
        result = resolve_value("oklch(0.55 0.15 270)")
        assert result.startswith("rgb(")
        match = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", result)
        assert match is not None
        r, g, b = map(int, match.groups())
        assert 0 <= r <= 255
        assert 0 <= g <= 255
        assert 0 <= b <= 255

    def test_oklch_to_rgb_channel_accuracy(self):
        """Test that oklch is converted to rgb with channel accuracy."""
        # oklch(1 0 0) -> white
        assert resolve_value("oklch(1 0 0)") == "rgb(255, 255, 255)"
        # oklch(0 0 0) -> black
        assert resolve_value("oklch(0 0 0)") == "rgb(0, 0, 0)"

    def test_oklch_with_alpha(self):
        """Test that oklch is converted to rgba with alpha."""
        result = resolve_value("oklch(0.55 0.15 270 / 0.5)")
        assert result.startswith("rgba(")
        assert result.endswith(", 0.5)")

    def test_oklch_with_percentage_alpha(self):
        """Test that oklch is converted to rgba with percentage alpha."""
        result = resolve_value("oklch(0.55 0.15 270 / 50%)")
        assert result == "rgba(80, 105, 200, 0.5)"

    def test_oklch_with_percentage_lightness(self):
        """Test that oklch is converted to rgba with percentage lightness."""
        result = resolve_value("oklch(100% 0 0)")
        assert result == "rgb(255, 255, 255)"

    def test_hsl_to_rgb(self):
        """Test that hsl is converted to rgb."""
        result = resolve_value("hsl(0 100% 50%)")
        assert result == "rgb(255, 0, 0)"

    def test_hsl_with_alpha(self):
        """Test that hsl is converted to rgba with alpha."""
        result = resolve_value("hsl(0 100% 50% / 0.5)")
        assert result == "rgba(255, 0, 0, 0.5)"

    def test_rem_to_px(self):
        """Test that rem is converted to px."""
        assert resolve_value("0.5rem") == "8px"
        assert resolve_value("1rem") == "16px"
        assert resolve_value("1.5rem") == "24px"

    def test_rgb_passthrough(self):
        """Test that rgb is passed through."""
        assert resolve_value("rgb(255, 0, 0)") == "rgb(255, 0, 0)"

    def test_rgba_passthrough(self):
        """Test that rgba is passed through."""
        assert resolve_value("rgba(255, 0, 0, 0.5)") == "rgba(255, 0, 0, 0.5)"

    def test_hex_passthrough(self):
        """Test that hex is passed through."""
        assert resolve_value("#0f172a") == "#0f172a"

    def test_px_passthrough(self):
        """Test that px is passed through."""
        assert resolve_value("16px") == "16px"
