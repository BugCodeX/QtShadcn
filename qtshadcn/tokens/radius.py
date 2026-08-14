"""Static shadcn/Tailwind-inspired design scale tokens."""

import re

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolveRadius(baseRadius: str, radiusSize: str) -> str:
    """Map a Tailwind rounded-{name} class to a static pixel value.

    The `sm` and `md` tiers are derived from baseRadius so they
    track theme customisation; the rest are fixed shadcn defaults.

    Args:
        baseRadius (str): Base radius in pixels, e.g. "8px".
        radiusSize (str): One of "none" | "xs" | "sm" | "md" | "lg" | "xl" |
            "2xl" | "3xl" | "4xl" | "full".

    Returns:
        str: Static pixel value for the given radius class.

    Raises:
        ValueError: If name is not one of the accepted radius classes.

    Examples:
        >>> resolveRadius("8px", "none")
        '0px'
        >>> resolveRadius("8px", "sm")  # sm = base - 4
        '4px'
        >>> resolveRadius("8px", "md")  # md = base - 2
        '6px'
        >>> resolveRadius("8px", "lg")  # lg = base
        '8px'

    """
    match radiusSize:
        case "none":
            return "0px"
        case "xs":
            return "2px"
        case "sm":
            return _toPixelString(_parsePixel(baseRadius) - 4)
        case "md":
            return _toPixelString(_parsePixel(baseRadius) - 2)
        case "lg":
            return _toPixelString(_parsePixel(baseRadius))
        case "xl":
            return _toPixelString(_parsePixel(baseRadius) + 4)
        case "2xl":
            return "16px"
        case "3xl":
            return "24px"
        case "4xl":
            return "32px"
        case "full":
            return "9999px"
        case _:
            raise ValueError(f"Unsupported radius class: {radiusSize}")


def clampRadius(baseRadius: str, radiusSize: str, maxRadius: str) -> str:
    """Clamp a rounded-* radius to limit.

    Needed for pill-shaped widgets where the design token may exceed the
    widget height — Qt renders that as an invisible rounded rectangle.

    Args:
        baseRadius (str): Base radius in pixels.
        radiusSize (str): Radius class name (e.g. "xl").
        maxRadius (str): Maximum allowed radius in pixels.

    Returns:
        str: The clamped pixel value.

    Examples:
        >>> clampRadius("8px", "xl", "10px")  # xl=12px, clamped to 10px
        '10px'

    """
    return _toPixelString(
        min(_parsePixel(resolveRadius(baseRadius, radiusSize)), _parsePixel(maxRadius))
    )


def expandRadius(baseRadius: str, radiusSize: str, pixelOffset: str) -> str:
    """Offset a rounded-* radius outward, typically to match a parent's border.

    Args:
        baseRadius (str): Base radius in pixels.
        radiusSize (str): Radius class name.
        pixelOffset (str): Pixels to add.

    Returns:
        str: The increased pixel value.

    """
    return _toPixelString(
        _parsePixel(resolveRadius(baseRadius, radiusSize)) + _parsePixel(pixelOffset)
    )


def shrinkRadius(baseRadius: str, radiusSize: str, pixelOffset: str) -> str:
    """Offset a rounded-* radius inward, floored at 0 to stay Qt-safe.

    Args:
        baseRadius (str): Base radius in pixels.
        radiusSize (str): Radius class name.
        pixelOffset (str): Pixels to subtract.

    Returns:
        str: The decreased pixel value (never negative).

    """
    return _toPixelString(
        max(_parsePixel(resolveRadius(baseRadius, radiusSize)) - _parsePixel(pixelOffset), 0)
    )


def halveRadius(pixelValue: str) -> str:
    """Halve a pixel value — intermediate step for circle math.

    QSS doesn't support 50%, so we need an explicit pixel value.

    Args:
        pixelValue (str): Pixel value to halve (e.g. "32px").

    Returns:
        str: Half of the input value as a pixel string.

    """
    return _toPixelString(_parsePixel(pixelValue) / 2)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parsePixel(pixelString: str) -> float:
    """Parse a `"<number>px"` string into its numeric value."""
    match = re.compile(r"^(-?\d+(?:\.\d+)?)px$").match(pixelString.strip())
    if match is None:
        raise ValueError(f"Expected a pixel value, got: {pixelString}")
    return float(match.group(1))


def _toPixelString(numericValue: float) -> str:
    """Format a float as a pixel string, dropping unnecessary decimals."""
    if numericValue % 1 == 0:
        return f"{int(numericValue)}px"
    return f"{numericValue:.2f}".rstrip("0").rstrip(".") + "px"
