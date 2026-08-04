"""QtShadcn native XML theme parser.

The core runtime only accepts local QtShadcn XML theme files. tweakcn/shadcn
JSON registries and raw CSS files are rejected at this boundary. Optional
converter tooling that turns those formats into QtShadcn XML lives outside the
application path.
"""

import logging
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET

from .models import ShadcnTheme, ShadcnThemeTokens

logger = logging.getLogger(__name__)


_REQUIRED_TOKENS = tuple(ShadcnThemeTokens.model_fields)

# Match CSS functional values.
_RE_OKLCH = re.compile(
    r"oklch\(\s*"
    r"(?P<L>[-+]?\d*\.?\d+)%?\s+"
    r"(?P<C>[-+]?\d*\.?\d+)\s+"
    r"(?P<H>[-+]?\d*\.?\d+)(?:deg)?\s*"
    r"(?:/\s*(?P<A>[-+]?\d*\.?\d+%?)\s*)?"
    r"\)",
    re.IGNORECASE,
)
_RE_HSL = re.compile(
    r"hsl\(\s*"
    r"(?P<H>[-+]?\d*\.?\d+)(?:deg)?\s+"
    r"(?P<S>[-+]?\d*\.?\d+)%\s+"
    r"(?P<L>[-+]?\d*\.?\d+)%\s*"
    r"(?:/\s*(?P<A>[-+]?\d*\.?\d+%?)\s*)?"
    r"\)",
    re.IGNORECASE,
)
_RE_REM = re.compile(r"^([\d.]+)rem$", re.IGNORECASE)
_RE_RGB_RGBA = re.compile(
    r"^(rgba?)\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*"
    r"(?:,\s*([\d.]+)\s*)?\)$"
)


class ThemeParseError(ValueError):
    """Raised when a QtShadcn XML theme cannot be parsed or validated."""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_theme_source(path: Path | str) -> ShadcnTheme:
    """Load a local QtShadcn XML theme and return resolved light/dark palettes.

    Args:
        path: Local filesystem path to a ``.xml`` theme file.

    Returns:
        A validated ``ShadcnTheme`` with resolved light and dark tokens.

    Raises:
        ThemeParseError: For unsupported sources, malformed XML, or missing
            required ``<light>``/``<dark>`` sections.

    """
    path_str = str(path)
    _validate_source(path_str)
    path = Path(path)

    logger.debug("Parsing XML theme: %s", path)
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        raise ThemeParseError(f"Invalid XML in theme file {path}: {e}") from e
    except OSError as e:
        raise ThemeParseError(f"Could not read theme file {path}: {e}") from e

    light_section = root.find("light")
    dark_section = root.find("dark")

    if light_section is None or dark_section is None:
        raise ThemeParseError(
            f"QtShadcn XML theme must contain both <light> and <dark> sections: {path}"
        )

    light_tokens = _resolve_palette(light_section, "light")
    dark_tokens = _resolve_palette(dark_section, "dark")

    logger.debug(
        "Theme resolved: %d light tokens, %d dark tokens",
        len(light_tokens),
        len(dark_tokens),
    )
    return ShadcnTheme(
        light=ShadcnThemeTokens(**light_tokens), dark=ShadcnThemeTokens(**dark_tokens)
    )


def resolve_value(raw: str) -> str:
    """Resolve a single theme value to a Qt-safe string.

    Supported conversions:

    - ``oklch(L C H)`` -> ``rgb(r, g, b)``
    - ``oklch(L C H / alpha)`` -> ``rgba(r, g, b, alpha)``
    - ``hsl(H S% L%)`` -> ``rgb(r, g, b)``
    - ``hsl(H S% L% / alpha)`` -> ``rgba(r, g, b, alpha)``
    - ``<number>rem`` -> ``<number * 16>px``
    - ``rgb(...)`` / ``rgba(...)`` -> passthrough
    - hex values -> passthrough
    - already resolved values (e.g. ``8px``) -> passthrough

    Args:
        raw: Token value as written in the XML theme.

    Returns:
        Qt-safe resolved value. Unresolvable inputs are returned unchanged so
        the caller can decide whether to fall back.

    """
    raw = raw.strip()

    if match := _RE_OKLCH.match(raw):
        return _oklch_to_rgb(
            match.group("L"),
            match.group("C"),
            match.group("H"),
            match.group("A"),
        )

    if match := _RE_HSL.match(raw):
        return _hsl_to_rgb(
            match.group("H"),
            match.group("S"),
            match.group("L"),
            match.group("A"),
        )

    if match := _RE_REM.match(raw):
        return _rem_to_px(match.group(1))

    # rgb()/rgba() and hex are already Qt-safe; pass them through.
    return raw


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_source(path_str: str) -> None:
    """Reject unsupported theme sources before touching the filesystem."""
    text_path = path_str.lower()

    if text_path.startswith(("http://", "https://", "ftp://")):
        raise ThemeParseError("URL theme sources are not supported; use a local XML file")

    if text_path.endswith(".json"):
        raise ThemeParseError(
            "JSON theme registries are not accepted by the core runtime; "
            "convert to QtShadcn XML first"
        )

    if text_path.endswith(".css"):
        raise ThemeParseError(
            "Raw CSS theme files are not accepted by the core runtime; "
            "convert to QtShadcn XML first"
        )

    path = Path(path_str)

    if not path.exists():
        raise ThemeParseError(f"Theme file not found: {path}")

    if not path.is_file():
        raise ThemeParseError(f"Theme path is not a file: {path}")

    if not text_path.endswith(".xml"):
        raise ThemeParseError(f"QtShadcn core only accepts .xml theme files: {path}")


def _extract_tokens(section) -> dict[str, str]:
    """Read child tag names/values from a light/dark XML section."""
    tokens = {}
    for child in section:
        if child.tag is ET.Comment:
            continue
        if child.text:
            tokens[child.tag] = child.text.strip()
    return tokens


def _resolve_palette(section, section_name: str) -> dict[str, str]:
    """Resolve every required token in a complete palette."""
    raw_tokens = _extract_tokens(section)
    missing = [
        name for name in _REQUIRED_TOKENS if name not in raw_tokens or raw_tokens[name] == ""
    ]
    if missing:
        missing_tokens = ", ".join(missing)
        raise ThemeParseError(
            f"QtShadcn XML theme section <{section_name}> is missing required token(s): "
            f"{missing_tokens}"
        )

    resolved: dict[str, str] = {}

    for name in _REQUIRED_TOKENS:
        raw = raw_tokens[name]
        try:
            value = resolve_value(raw)
        except Exception as e:
            logger.warning("Could not resolve token %r with value %r: %s", name, raw, e)
            value = raw

        resolved[name] = value

    return resolved


def _rem_to_px(value: str) -> str:
    """Convert a rem value to px using 1rem = 16px."""
    px = float(value) * 16
    if px % 1 == 0:
        return f"{int(px)}px"
    return f"{px}px"


def _oklch_to_rgb(l_str: str, c_str: str, h_str: str, alpha_str: str | None) -> str:
    """Convert OKLCH to sRGB, returning rgb() or rgba()."""
    l_val = float(l_str) / 100.0 if l_str.endswith("%") else float(l_str)
    c_val = float(c_str)
    h_deg = float(h_str)
    if alpha_str is None:
        alpha = None
    elif alpha_str.endswith("%"):
        alpha = float(alpha_str[:-1]) / 100.0
    else:
        alpha = float(alpha_str)

    # OKLCH -> OKLab
    h_rad = math.radians(h_deg)
    a = c_val * math.cos(h_rad)
    b = c_val * math.sin(h_rad)

    # OKLab -> linear LMS
    lms_l = l_val + 0.3963377774 * a + 0.2158037573 * b
    lms_m = l_val - 0.1055613458 * a - 0.0638541728 * b
    lms_s = l_val - 0.0894841775 * a - 1.2914855480 * b

    # Non-linear LMS
    lms_l = lms_l**3
    lms_m = lms_m**3
    lms_s = lms_s**3

    # LMS (non-linear) -> linear sRGB. Matrix is the product of the standard
    # XYZ->linear-sRGB matrix and the inverse of the OKLab LMS->XYZ matrix.
    r_lin = 4.07718682 * lms_l - 3.30762252 * lms_m + 0.23085920 * lms_s
    g_lin = -1.26857649 * lms_l + 2.60968711 * lms_m - 0.34115575 * lms_s
    b_lin = -0.00419654 * lms_l - 0.70339968 * lms_m + 1.70679603 * lms_s

    r = _gamma_correct(r_lin)
    g = _gamma_correct(g_lin)
    b = _gamma_correct(b_lin)

    if alpha is not None:
        return f"rgba({r}, {g}, {b}, {alpha})"
    return f"rgb({r}, {g}, {b})"


def _hsl_to_rgb(h_str: str, s_str: str, l_str: str, alpha_str: str | None) -> str:
    """Convert HSL to sRGB, returning rgb() or rgba()."""
    h = float(h_str) % 360.0
    s = float(s_str) / 100.0
    lightness = float(l_str) / 100.0
    if alpha_str is None:
        alpha = None
    elif alpha_str.endswith("%"):
        alpha = float(alpha_str[:-1]) / 100.0
    else:
        alpha = float(alpha_str)

    c = (1.0 - abs(2.0 * lightness - 1.0)) * s
    x = c * (1.0 - abs((h / 60.0) % 2.0 - 1.0))
    m = lightness - c / 2.0

    if 0 <= h < 60:
        r1, g1, b1 = c, x, 0.0
    elif 60 <= h < 120:
        r1, g1, b1 = x, c, 0.0
    elif 120 <= h < 180:
        r1, g1, b1 = 0.0, c, x
    elif 180 <= h < 240:
        r1, g1, b1 = 0.0, x, c
    elif 240 <= h < 300:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x

    r = int(round((r1 + m) * 255))
    g = int(round((g1 + m) * 255))
    b = int(round((b1 + m) * 255))

    if alpha is not None:
        return f"rgba({r}, {g}, {b}, {alpha})"
    return f"rgb({r}, {g}, {b})"


def _gamma_correct(channel: float) -> int:
    """Apply sRGB gamma correction and clamp to 0-255."""
    linear = channel * 12.92 if channel <= 0.0031308 else 1.055 * channel ** (1.0 / 2.4) - 0.055
    return max(0, min(255, int(round(linear * 255))))
