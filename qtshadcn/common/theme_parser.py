"""QtShadcn native XML theme parser.

The core runtime accepts local QtShadcn XML theme files and QtShadcn JSON
palette files. tweakcn/shadcn JSON registries and raw CSS files are rejected
at this boundary. Theme values should be HEX colors or pixel sizes;
``rgb()`` / ``rgba()`` values are passed through as QSS-compatible values.
Optional converter tooling that turns external formats into QtShadcn XML lives
outside the application path.
"""

import json
import logging
from pathlib import Path
from xml.etree import ElementTree as ET

from ..exceptions import ThemeParseError
from ..models import ShadcnTheme, ShadcnThemeTokens

logger = logging.getLogger(__name__)


_REQUIRED_TOKENS = tuple(ShadcnThemeTokens.model_fields)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse_json_theme(path: Path) -> ShadcnTheme:
    """Load a QtShadcn JSON palette and return resolved light/dark tokens."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ThemeParseError(f"Invalid JSON in theme file {path}: {e}") from e
    except OSError as e:
        raise ThemeParseError(f"Could not read theme source: {path}") from e

    if not isinstance(data, dict):
        raise ThemeParseError(f"Invalid JSON theme structure in {path}")
    try:
        return ShadcnTheme.model_validate(data)
    except Exception as e:
        raise ThemeParseError(f"Invalid JSON theme tokens in {path}: {e}") from e


def _parse_theme_source(source: str | Path) -> ShadcnTheme:
    """Load a theme from an XML or JSON source."""
    path = Path(source)
    suffix = path.suffix.lower()
    if suffix == ".css":
        raise ThemeParseError(
            "Raw CSS theme files are not accepted by the core runtime; "
            "convert to QtShadcn XML or JSON first"
        )
    if suffix == ".json":
        return _parse_json_theme(path)
    if suffix == ".xml":
        return parse_theme_source(path)
    raise ThemeParseError(f"QtShadcn core only accepts .xml or .json theme files: {path}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_theme_source(path: Path | str) -> ShadcnTheme:
    """Load a local QtShadcn XML theme and return resolved light/dark palettes.

    Args:
        path: Local filesystem path to a ``.xml`` theme file.

    Returns:
        A validated ``ShadcnTheme`` with light and dark tokens as written in
        the XML file.

    Raises:
        ThemeParseError: For unsupported sources, malformed XML, or missing
            required ``<light>``/``<dark>`` sections.

    """
    path_str = str(path)
    _validate_xml_source(path_str)
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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _validate_xml_source(path_str: str) -> None:
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
        resolved[name] = raw_tokens[name]

    return resolved
