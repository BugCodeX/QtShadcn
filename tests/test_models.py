"""Tests for QtShadcn theme models."""

import pytest
from qtshadcn.models import ShadcnTheme, ShadcnThemeTokens, ThemeConfig


class TestThemeConfig:
    """Tests for the internal theme config model."""

    def test_default_config_has_no_source_path(self):
        """Test that the default config has no source path."""
        config = ThemeConfig()
        assert config.theme_file is None
        assert config.theme_mode == "auto"
        assert config.custom_tokens is None
        assert config.additional_qss is None
        assert config.default_theme == "dark"

    def test_config_stores_theme_file(self):
        """Test that the config stores the theme file path."""
        config = ThemeConfig(theme_file="/tmp/theme.xml")
        assert config.theme_file == "/tmp/theme.xml"

    def test_config_stores_custom_tokens(self):
        """Test that the config stores custom token overrides."""
        config = ThemeConfig(custom_tokens={"background": "#000000"})
        assert config.custom_tokens == {"background": "#000000"}

    def test_config_stores_additional_qss(self):
        """Test that the config stores additional QSS."""
        config = ThemeConfig(additional_qss="QWidget { color: red; }")
        assert config.additional_qss == "QWidget { color: red; }"


class TestShadcnThemeTokens:
    """Tests for the theme tokens model."""

    def test_known_token_available(self):
        """Test that a known token is available."""
        tokens = ShadcnThemeTokens(**_tokens(primary="#123456"))
        assert tokens.primary == "#123456"

    def test_unknown_token_is_ignored(self):
        """Test that an unknown token is ignored."""
        tokens = ShadcnThemeTokens(**_tokens(unknown_color="#abcdef", primary="#123456"))
        assert tokens.primary == "#123456"
        assert "unknown_color" not in tokens.model_dump()

    def test_missing_token_fails_validation(self):
        """Test that a missing token fails validation."""
        values = _tokens()
        del values["primary"]
        with pytest.raises(Exception, match="primary"):
            ShadcnThemeTokens(**values)


class TestShadcnTheme:
    """Tests for the theme model."""

    def test_both_palettes_available(self):
        """Test that both palettes are available."""
        theme = ShadcnTheme(
            light=ShadcnThemeTokens(**_tokens(background="#ffffff")),
            dark=ShadcnThemeTokens(**_tokens(background="#000000")),
        )
        assert theme.light.background == "#ffffff"
        assert theme.dark.background == "#000000"

    def test_theme_is_frozen(self):
        """Test that the theme is frozen."""
        theme = ShadcnTheme(
            light=ShadcnThemeTokens(**_tokens()),
            dark=ShadcnThemeTokens(**_tokens()),
        )
        with pytest.raises(Exception, match="light"):
            theme.light = ShadcnThemeTokens(**_tokens())  # ty:ignore[invalid-assignment]


def _tokens(**overrides):
    """Return a dict of token values."""
    values = {
        "background": "#ffffff",
        "foreground": "#020617",
        "card": "#ffffff",
        "card_foreground": "#020617",
        "popover": "#ffffff",
        "popover_foreground": "#020617",
        "primary": "#0f172a",
        "primary_foreground": "#f8fafc",
        "secondary": "#f1f5f9",
        "secondary_foreground": "#0f172a",
        "muted": "#f1f5f9",
        "muted_foreground": "#64748b",
        "accent": "#f1f5f9",
        "accent_foreground": "#0f172a",
        "destructive": "#ef4444",
        "destructive_foreground": "#f8fafc",
        "border": "#e2e8f0",
        "input": "#e2e8f0",
        "ring": "#0f172a",
        "spacing": "4px",
        "radius": "8px",
        "font_family": "system-ui, sans-serif",
    }
    values.update(overrides)
    return values
