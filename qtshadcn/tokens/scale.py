"""Static shadcn/Tailwind-inspired design scale tokens."""

import logging
import re

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PX_RE = re.compile(r"^(-?\d+(?:\.\d+)?)px$")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolveSpacing(pixelValue: str, scaleFactor: float) -> str:
    """Scale a base spacing token by a multiplier and return a QSS-ready pixel string.

    Args:
        pixelValue (str): Base spacing token in pixels, e.g. "4px".
        scaleFactor (float): Tailwind spacing multiplier (e.g. 2.5 → "10px" for a "4px" base).

    Returns:
        str: Scaled pixel value ready for QSS (e.g. "10px").

    Examples:
        >>> resolveSpacing("4px", 2)
        '8px'
        >>> resolveSpacing("4px", 2.5)
        '10px'
    """
    return _scalePixel(pixelValue, scaleFactor)


def toSpacingInt(pixelValue: str, scaleFactor: float) -> int:
    """Scale a base spacing token by a multiplier and return an integer pixel value.

    Useful when Qt requires an integer (e.g. setContentsMargins, resize).
    Falls back to 0 when pixelValue is not a valid pixel string.

    Args:
        pixelValue (str): Base spacing token in pixels, e.g. "4px".
        scaleFactor (float): Tailwind spacing multiplier.

    Returns:
        int: Scaled pixel value as an integer, or 0 if pixelValue is not a valid pixel string.

    Examples:
        >>> toSpacingInt("4px", 2)
        8
        >>> toSpacingInt("auto", 2)
        0
    """
    match = _PX_RE.match(_scalePixel(pixelValue, scaleFactor).strip())
    if match is None:
        logger.warning("Unrecognized pixel value format: %s", pixelValue)
        return 0
    return int(float(match.group(1)))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _scalePixel(pixelString: str, scaleFactor: float) -> str:
    """Return a Qt-safe pixel value scaled by `scaleFactor`."""
    match = _PX_RE.match(pixelString.strip())
    if match is None:
        logger.warning("Unrecognized pixel value format: %s", pixelString)
        return pixelString
    scaled = float(match.group(1)) * scaleFactor
    if scaled % 1 == 0:
        return f"{int(scaled)}px"
    return f"{scaled:.2f}".rstrip("0").rstrip(".") + "px"
