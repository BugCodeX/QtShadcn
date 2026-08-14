"""Tests for static token helper modules."""

import pytest
from qtshadcn.tokens import colors, radius, scale


def test_color_with_alpha_renders_rgba_from_hex():
    """Test that CSS slash-alpha equivalents become static rgba values."""
    assert colors.withAlpha("#0f172a", 0.8) == "rgba(15, 23, 42, 0.8)"
    assert colors.withAlpha("#fff", 0.5) == "rgba(255, 255, 255, 0.5)"


def test_color_blend_colors_renders_static_rgb():
    """Test that color-mix equivalents become static rgb values."""
    assert colors.blendColors("#f1f5f9", "#020617", 0.05) == "rgb(229, 233, 238)"


def test_radius_clamp_radius_uses_static_cap():
    """Test that CSS min() radius equivalents become static pixel values."""
    assert radius.clampRadius("8px", "md", "10px") == "6px"
    assert radius.clampRadius("20px", "md", "10px") == "10px"


def test_radius_resolve_radius_maps_tailwind_names():
    """Test Tailwind rounded-* names become static QSS pixel values."""
    assert radius.resolveRadius("10px", "none") == "0px"
    assert radius.resolveRadius("10px", "xs") == "2px"
    assert radius.resolveRadius("10px", "sm") == "6px"
    assert radius.resolveRadius("10px", "md") == "8px"
    assert radius.resolveRadius("10px", "lg") == "10px"
    assert radius.resolveRadius("10px", "xl") == "14px"
    assert radius.resolveRadius("10px", "2xl") == "16px"
    assert radius.resolveRadius("10px", "3xl") == "24px"
    assert radius.resolveRadius("10px", "4xl") == "32px"
    assert radius.resolveRadius("10px", "full") == "9999px"


def test_radius_arithmetic_helpers_render_static_pixels():
    """Test radius arithmetic helpers avoid CSS functions in QSS output."""
    assert radius.clampRadius("20px", "md", "10px") == "10px"
    assert radius.clampRadius("8px", "md", "10px") == "6px"
    assert radius.expandRadius("8px", "md", "2px") == "8px"
    assert radius.shrinkRadius("8px", "md", "2px") == "4px"
    assert radius.shrinkRadius("8px", "none", "2px") == "0px"


def test_radius_helpers_reject_non_px_values():
    """Test radius helpers fail before emitting unsupported QSS units."""
    with pytest.raises(ValueError, match="Expected a pixel value"):
        radius.resolveRadius("0.5em", "lg")


def test_resolve_spacing_matches_scale_px():
    """Test spacing multiples keep the existing scale behavior."""
    assert scale.resolveSpacing("4px", 1.5) == "6px"


def test_to_spacing_int_returns_integer_pixels():
    """Test spacing multiples can be returned as integer pixel values."""
    assert scale.toSpacingInt("4px", 1) == 4
    assert scale.toSpacingInt("4px", 3) == 12
    assert scale.toSpacingInt("6px", 1.5) == 9
