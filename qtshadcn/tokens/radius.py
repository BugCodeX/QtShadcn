"""Qt-safe helpers for shadcn/Tailwind radius semantics."""

import re

XS_RADIUS = "2px"
FULL_RADIUS = "9999px"

SM_RATIO = 0.6
MD_RATIO = 0.8
LG_RATIO = 1
XL_RATIO = 1.4
RADIUS_2XL_RATIO = 1.8
RADIUS_3XL_RATIO = 2.2
RADIUS_4XL_RATIO = 2.6

_PX_RE = re.compile(r"^(-?\d+(?:\.\d+)?)px$")

_RATIOS = {
    "sm": SM_RATIO,
    "md": MD_RATIO,
    "lg": LG_RATIO,
    "xl": XL_RATIO,
    "2xl": RADIUS_2XL_RATIO,
    "3xl": RADIUS_3XL_RATIO,
    "4xl": RADIUS_4XL_RATIO,
}


def class_px(base_radius: str, name: str) -> str:
    """Return the static pixel value for a Tailwind rounded-* class name."""
    if name == "none":
        return "0px"
    if name == "xs":
        return XS_RADIUS
    if name == "full":
        return FULL_RADIUS
    if name not in _RATIOS:
        raise ValueError(f"Unsupported radius class: {name}")

    return _format_px(_px_number(base_radius) * _RATIOS[name])


def min_px(base_radius: str, name: str, limit: str) -> str:
    """Return ``min(rounded-name, limit)`` as a static Qt-safe pixel value."""
    return _format_px(min(_px_number(class_px(base_radius, name)), _px_number(limit)))


def add_px(base_radius: str, name: str, amount: str) -> str:
    """Return ``rounded-name + amount`` as a static Qt-safe pixel value."""
    return _format_px(_px_number(class_px(base_radius, name)) + _px_number(amount))


def sub_px(base_radius: str, name: str, amount: str) -> str:
    """Return ``rounded-name - amount`` as a non-negative static pixel value."""
    return _format_px(max(_px_number(class_px(base_radius, name)) - _px_number(amount), 0))


def _px_number(value: str) -> float:
    match = _PX_RE.match(value.strip())
    if match is None:
        raise ValueError(f"Expected a pixel value, got: {value}")
    return float(match.group(1))


def _format_px(value: float) -> str:
    if value % 1 == 0:
        return f"{int(value)}px"
    return f"{value:.2f}".rstrip("0").rstrip(".") + "px"
