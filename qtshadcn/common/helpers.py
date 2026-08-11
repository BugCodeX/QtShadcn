"""QtShadcn theme application helpers."""

import logging
from pathlib import Path
from typing import Any

from ..exceptions import QtShadcnError, ThemeParseError
from ..models import ShadcnTheme, ShadcnThemeTokens
from .binding import QtGui, QtWidgets
from .theme_parser import resolve_value

logger = logging.getLogger(__name__)

DEFAULT_THEME_FILE = Path(__file__).resolve().parents[1] / "themes" / "default.xml"


def _resolve_theme_file(theme_file: str | None) -> Path:
    """Return the configured XML path or the packaged default theme path."""
    if theme_file:
        return Path(theme_file)
    return DEFAULT_THEME_FILE


def _resolve_application(app: QtWidgets.QApplication | None) -> QtWidgets.QApplication:
    """Return the provided app or the existing QApplication instance."""
    if app is None:
        app = QtWidgets.QApplication.instance()  # type: ignore[assignment]
    if app is None:
        raise QtShadcnError("No QApplication instance found")
    return app


def _get_mtime(path: Path) -> float:
    """Return the modification time of the theme source file."""
    try:
        return path.stat().st_mtime
    except OSError as e:
        raise ThemeParseError(f"Could not read theme source: {path}") from e


def _add_fonts() -> None:
    """Register local font files found under the package ``fonts`` directory."""
    if QtWidgets.QApplication.instance() is None:
        return

    fonts_path = Path(__file__).resolve().parents[1] / "fonts"

    if not fonts_path.exists() or not fonts_path.is_dir():
        return

    for font_dir in fonts_path.iterdir():
        if not font_dir.is_dir():
            continue

        for font_file in font_dir.glob("*.[to]tf"):
            font_id = QtGui.QFontDatabase.addApplicationFont(str(font_file))
            if font_id == -1:
                logger.warning("Could not load font: %s", font_file.name)


def _apply_custom_tokens(
    theme: ShadcnTheme,
    custom_tokens: dict[str, dict[str, str] | str] | None,
) -> ShadcnTheme:
    """Apply token overrides after parsing and before palette selection."""
    if not custom_tokens:
        return theme

    if set(custom_tokens.keys()) <= {"light", "dark"}:
        light_overrides = _as_token_overrides(custom_tokens.get("light"))
        dark_overrides = _as_token_overrides(custom_tokens.get("dark"))
    else:
        shared = _as_token_overrides(custom_tokens)
        light_overrides = shared
        dark_overrides = shared

    return ShadcnTheme(
        light=_override_tokens(theme.light, light_overrides),
        dark=_override_tokens(theme.dark, dark_overrides),
    )


def _as_token_overrides(value: dict[str, Any] | str | None) -> dict[str, str]:
    """Normalize a custom token section to a mapping of token overrides."""
    if isinstance(value, dict):
        return {k: v for k, v in value.items() if isinstance(v, str)}
    return {}


def _override_tokens(tokens: ShadcnThemeTokens, overrides: dict[str, str]) -> ShadcnThemeTokens:
    """Return a new token set with resolved overrides applied."""
    if not overrides:
        return tokens
    data = tokens.model_dump()
    for key, raw_value in overrides.items():
        if key not in data:
            continue
        data[key] = resolve_value(raw_value)
    return ShadcnThemeTokens(**data)
