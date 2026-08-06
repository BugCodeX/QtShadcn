"""Static shadcn/Tailwind-inspired design scale tokens.

These values represent stable system-scale tokens, not theme-specific color
tokens. They are resolved to Qt/QSS-friendly values because Qt stylesheets do
not support CSS custom properties, ``rem`` units, or ``calc()`` expressions.
"""

import re

REM_PX = 16

BREAKPOINT_2XL = "1536px"

CONTAINER_XS = "320px"
CONTAINER_SM = "384px"
CONTAINER_MD = "448px"
CONTAINER_LG = "512px"
CONTAINER_XL = "576px"
CONTAINER_2XL = "672px"
CONTAINER_3XL = "768px"
CONTAINER_4XL = "896px"
CONTAINER_5XL = "1024px"
CONTAINER_6XL = "1152px"

TEXT_XS = "12px"
TEXT_XS_LINE_HEIGHT = 1 / 0.75
TEXT_SM = "14px"
TEXT_SM_LINE_HEIGHT = 1.25 / 0.875
TEXT_BASE = "16px"
TEXT_BASE_LINE_HEIGHT = 1.5
TEXT_LG = "18px"
TEXT_LG_LINE_HEIGHT = 1.75 / 1.125
TEXT_XL = "20px"
TEXT_XL_LINE_HEIGHT = 1.75 / 1.25
TEXT_2XL = "24px"
TEXT_2XL_LINE_HEIGHT = 2 / 1.5
TEXT_3XL = "30px"
TEXT_3XL_LINE_HEIGHT = 2.25 / 1.875
TEXT_4XL = "36px"
TEXT_4XL_LINE_HEIGHT = 2.5 / 2.25
TEXT_5XL = "48px"
TEXT_5XL_LINE_HEIGHT = 1
TEXT_7XL = "72px"
TEXT_7XL_LINE_HEIGHT = 1

FONT_WEIGHT_LIGHT = 300
FONT_WEIGHT_NORMAL = 400
FONT_WEIGHT_MEDIUM = 500
FONT_WEIGHT_SEMIBOLD = 600
FONT_WEIGHT_BOLD = 700
FONT_WEIGHT_EXTRABOLD = 800

TRACKING_TIGHTER = "-0.05em"
TRACKING_TIGHT = "-0.025em"
TRACKING_NORMAL = "0em"
TRACKING_WIDE = "0.025em"
TRACKING_WIDER = "0.05em"
TRACKING_WIDEST = "0.1em"

LEADING_TIGHT = 1.25
LEADING_SNUG = 1.375
LEADING_NORMAL = 1.5
LEADING_RELAXED = 1.625
LEADING_LOOSE = 2

_PX_RE = re.compile(r"^(-?\d+(?:\.\d+)?)px$")


def scale_px(value: str, factor: float) -> str:
    """Return a Qt-safe pixel value scaled by ``factor``."""
    match = _PX_RE.match(value.strip())
    if match is None:
        return value

    scaled = float(match.group(1)) * factor
    if scaled % 1 == 0:
        return f"{int(scaled)}px"
    return f"{scaled:.2f}".rstrip("0").rstrip(".") + "px"


def spacing_px(value: str, multiple: float) -> str:
    """Return a Qt-safe spacing multiple."""
    return scale_px(value, multiple)


def spacing_int(value: str, multiple: float) -> int:
    """Return a spacing multiple as an integer pixel value."""
    match = _PX_RE.match(scale_px(value, multiple).strip())
    if match is None:
        return 0
    return int(float(match.group(1)))
