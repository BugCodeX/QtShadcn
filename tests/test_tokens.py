"""Tests for static token helper modules."""

from qtshadcn.tokens import colors, scale


def test_color_alpha_renders_rgba_from_hex():
    """Test that CSS slash-alpha equivalents become static rgba values."""
    assert colors.alpha("#0f172a", 0.8) == "rgba(15, 23, 42, 0.8)"
    assert colors.alpha("#fff", 0.5) == "rgba(255, 255, 255, 0.5)"


def test_color_mix_renders_static_rgb():
    """Test that color-mix equivalents become static rgb values."""
    assert colors.mix("#f1f5f9", "#020617", 0.05) == "rgb(229, 233, 238)"


def test_radius_min_px_uses_static_cap():
    """Test that CSS min() radius equivalents become static pixel values."""
    assert scale.radius_min_px("8px", scale.RADIUS_MD_RATIO, "10px") == "6.4px"
    assert scale.radius_min_px("20px", scale.RADIUS_MD_RATIO, "10px") == "10px"


def test_spacing_px_matches_scale_px():
    """Test spacing multiples keep the existing scale behavior."""
    assert scale.spacing_px("4px", 1.5) == "6px"
