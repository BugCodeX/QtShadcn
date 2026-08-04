"""QSS-safe color helpers for shadcn-style token transforms."""

import logging
import re

logger = logging.getLogger(__name__)

_HEX_RE = re.compile(r"^#(?P<hex>[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_RE = re.compile(
    r"^rgba?\(\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)"
    r"(?:\s*,\s*(?P<a>\d*(?:\.\d+)?))?\s*\)$"
)


def alpha(color: str, opacity: float) -> str:
    """Return ``color`` with a CSS-like opacity as Qt-compatible ``rgba()``."""
    parsed = _parse_rgb(color)
    if parsed is None:
        logger.warning("Cannot parse color for alpha: %s", color)
        return color

    r, g, b = parsed
    return f"rgba({r}, {g}, {b}, {_format_float(_clamp(opacity))})"


def mix(color: str, other: str, amount: float) -> str:
    """Return a linear RGB mix of ``color`` toward ``other`` by ``amount``."""
    first = _parse_rgb(color)
    second = _parse_rgb(other)
    if first is None or second is None:
        logger.warning("Cannot parse colors for mix: %s, %s", color, other)
        return color

    amount = _clamp(amount)
    r = round(first[0] * (1 - amount) + second[0] * amount)
    g = round(first[1] * (1 - amount) + second[1] * amount)
    b = round(first[2] * (1 - amount) + second[2] * amount)
    return f"rgb({r}, {g}, {b})"


def _parse_rgb(color: str) -> tuple[int, int, int] | None:
    value = color.strip()

    hex_match = _HEX_RE.match(value)
    if hex_match is not None:
        hex_value = hex_match.group("hex")
        if len(hex_value) == 3:
            hex_value = "".join(char * 2 for char in hex_value)
        return (
            int(hex_value[0:2], 16),
            int(hex_value[2:4], 16),
            int(hex_value[4:6], 16),
        )

    rgb_match = _RGB_RE.match(value)
    if rgb_match is None:
        logger.debug("Unrecognized color format: %s", color)
        return None

    return (
        int(rgb_match.group("r")),
        int(rgb_match.group("g")),
        int(rgb_match.group("b")),
    )


def _clamp(value: float) -> float:
    return max(0, min(1, value))


def _format_float(value: float) -> str:
    return f"{value:.2f}".rstrip("0").rstrip(".")
