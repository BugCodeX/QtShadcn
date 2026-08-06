"""Tests for static token helper modules."""

import pytest
from qtshadcn.tokens import colors, radius, scale


def test_color_alpha_renders_rgba_from_hex():
    """Test that CSS slash-alpha equivalents become static rgba values."""
    assert colors.alpha("#0f172a", 0.8) == "rgba(15, 23, 42, 0.8)"
    assert colors.alpha("#fff", 0.5) == "rgba(255, 255, 255, 0.5)"


def test_color_mix_renders_static_rgb():
    """Test that color-mix equivalents become static rgb values."""
    assert colors.mix("#f1f5f9", "#020617", 0.05) == "rgb(229, 233, 238)"


def test_radius_min_px_uses_static_cap():
    """Test that CSS min() radius equivalents become static pixel values."""
    assert radius.min_px("8px", "md", "10px") == "6.4px"
    assert radius.min_px("20px", "md", "10px") == "10px"


def test_radius_class_px_maps_tailwind_names():
    """Test Tailwind rounded-* names become static QSS pixel values."""
    assert radius.class_px("10px", "none") == "0px"
    assert radius.class_px("10px", "xs") == "2px"
    assert radius.class_px("10px", "sm") == "6px"
    assert radius.class_px("10px", "md") == "8px"
    assert radius.class_px("10px", "lg") == "10px"
    assert radius.class_px("10px", "xl") == "14px"
    assert radius.class_px("10px", "2xl") == "18px"
    assert radius.class_px("10px", "3xl") == "22px"
    assert radius.class_px("10px", "4xl") == "26px"
    assert radius.class_px("10px", "full") == "9999px"


def test_radius_arithmetic_helpers_render_static_pixels():
    """Test radius arithmetic helpers avoid CSS functions in QSS output."""
    assert radius.min_px("20px", "md", "10px") == "10px"
    assert radius.min_px("8px", "md", "10px") == "6.4px"
    assert radius.add_px("8px", "md", "2px") == "8.4px"
    assert radius.sub_px("8px", "md", "2px") == "4.4px"
    assert radius.sub_px("8px", "none", "2px") == "0px"


def test_radius_helpers_reject_non_px_values():
    """Test radius helpers fail before emitting unsupported QSS units."""
    with pytest.raises(ValueError, match="Expected a pixel value"):
        radius.class_px("0.5rem", "lg")


def test_spacing_px_matches_scale_px():
    """Test spacing multiples keep the existing scale behavior."""
    assert scale.spacing_px("4px", 1.5) == "6px"


def test_spacing_int_returns_integer_pixels():
    """Test spacing multiples can be returned as integer pixel values."""
    assert scale.spacing_int("4px", 1) == 4
    assert scale.spacing_int("4px", 3) == 12
    assert scale.spacing_int("6px", 1.5) == 9
