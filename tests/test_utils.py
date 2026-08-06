"""Tests for qtshadcn utility helpers."""

import pytest
from qtshadcn._utils import blend_colors


@pytest.mark.parametrize(
    ("base", "overlay", "opacity", "expected"),
    [
        ("#ffffff", "#000000", 0.5, "#7f7f7f"),
        ("#ff0000", "#0000ff", 0.5, "#7f007f"),
        ("#ffffff", "#000000", 0.0, "#ffffff"),
        ("#ffffff", "#000000", 1.0, "#000000"),
        ("#ffff0000", "#ff00ff00", 0.5, "#7f7f00"),
        ("#12345", "#000000", 0.5, "#12345"),
        ("#ffffff", "#12345", 0.5, "#ffffff"),
        ("#ff0000", "", 0.5, "#ff0000"),
    ],
)
def test_blend_colors(base, overlay, opacity, expected):
    """Test color blending including ARGB stripping and edge cases."""
    assert blend_colors(base, overlay, opacity) == expected
