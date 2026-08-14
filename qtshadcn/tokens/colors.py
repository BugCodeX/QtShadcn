"""QSS-safe color helpers for shadcn-style token transforms."""

import logging
import re

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_HEX_RE = re.compile(r"^#(?P<hex>[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_RE = re.compile(
    r"^rgba?\(\s*(?P<r>\d+)\s*,\s*(?P<g>\d+)\s*,\s*(?P<b>\d+)"
    r"(?:\s*,\s*(?P<a>\d*(?:\.\d+)?))?\s*\)$"
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def withAlpha(baseColor: str, alphaValue: float) -> str:
    """Return `baseColor` with a CSS-like opacity as a Qt-compatible `rgba()` string.

    Useful for hover/pressed states where the design token must be
    translucent without introducing a new color.

    Args:
        baseColor (str): Base color in hex or rgb format, e.g. "#3b82f6" or "rgb(59, 130, 246)".
        alphaValue (float): Opacity in the range [0.0, 1.0]. Values outside this range are clamped.

    Returns:
        str: A Qt-compatible `rgba(r, g, b, a)` string. If `baseColor`
            cannot be parsed, the original string is returned unchanged
            and a warning is logged.

    Examples:
        >>> withAlpha("#000000", 0.5)
        'rgba(0, 0, 0, 0.5)'
        >>> withAlpha("rgb(255, 0, 0)", 1.0)
        'rgba(255, 0, 0, 1)'
    """
    parsed = _parseColor(baseColor)
    if parsed is None:
        logger.warning("Cannot parse color for alpha: %s", baseColor)
        return baseColor
    r, g, b = parsed
    return f"rgba({r}, {g}, {b}, {_toAlphaString(_clampUnit(alphaValue))})"


def blendColors(sourceColor: str, targetColor: str, blendAmount: float) -> str:
    """Return a linear RGB mix of `sourceColor` toward `targetColor` by `blendAmount`.

    Used to derive intermediate states (hover, active, disabled) from
    two design tokens without hard-coding hex values.

    Args:
        sourceColor (str): Starting color in hex or rgb format.
        targetColor (str): Ending color in hex or rgb format.
        blendAmount (float): Interpolation factor in [0.0, 1.0]. 0.0 returns `sourceColor`; 1.0 returns `targetColor`.

    Returns:
        str: A Qt-compatible `rgb(r, g, b)` string. If either color
            cannot be parsed, `sourceColor` is returned unchanged and
            a warning is logged.

    Examples:
        >>> blendColors("#000000", "#ffffff", 0.5)
        'rgb(128, 128, 128)'
        >>> blendColors("rgb(255, 0, 0)", "rgb(0, 0, 255)", 0.0)
        'rgb(255, 0, 0)'
    """
    first = _parseColor(sourceColor)
    second = _parseColor(targetColor)
    if first is None or second is None:
        logger.warning("Cannot parse colors for mix: %s, %s", sourceColor, targetColor)
        return sourceColor
    blendAmount = _clampUnit(blendAmount)
    r = round(first[0] * (1 - blendAmount) + second[0] * blendAmount)
    g = round(first[1] * (1 - blendAmount) + second[1] * blendAmount)
    b = round(first[2] * (1 - blendAmount) + second[2] * blendAmount)
    return f"rgb({r}, {g}, {b})"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parseColor(colorString: str) -> tuple[int, int, int] | None:
    """Parse a hex or rgb color string into its (r, g, b) components.

    Supports 3-digit hex (`#abc`), 6-digit hex (`#aabbcc`), `rgb()` and
    `rgba()` formats. Alpha channel is ignored because this helper only
    returns the RGB triple.

    Args:
        colorString (str): Color string to parse.

    Returns:
        tuple[int, int, int] | None: The (r, g, b) components, or None
            if the format is unrecognized (a debug message is logged).
    """
    value = colorString.strip()
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
        logger.debug("Unrecognized color format: %s", colorString)
        return None
    return (
        int(rgb_match.group("r")),
        int(rgb_match.group("g")),
        int(rgb_match.group("b")),
    )


def _clampUnit(unitValue: float) -> float:
    """Clamp `unitValue` to the unit interval [0.0, 1.0]."""
    return max(0, min(1, unitValue))


def _toAlphaString(alphaValue: float) -> str:
    """Format `alphaValue` as a compact decimal string, dropping trailing zeros."""
    return f"{alphaValue:.2f}".rstrip("0").rstrip(".")
