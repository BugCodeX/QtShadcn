"""QtShadcn theme application helpers."""

import os
from pathlib import Path
from typing import Any, cast

from qtpy import QtWidgets

from ..exceptions import QtShadcnError
from ..models import ShadcnTheme, ShadcnThemeTokens

DEFAULT_THEME_FILE = Path(__file__).resolve().parents[1] / "themes" / "default.xml"


def _resolve_theme_file(theme_file: str | None) -> Path:
    """Return the configured theme path or the packaged default theme path."""
    if theme_file:
        return Path(theme_file)
    return DEFAULT_THEME_FILE


def _resolve_application(app: QtWidgets.QApplication | None) -> QtWidgets.QApplication:
    """Return the provided app or the existing QApplication instance."""
    if app is None:
        app = cast(Any, QtWidgets.QApplication.instance())
    if app is None:
        raise QtShadcnError("No QApplication instance found")
    return app


def _apply_custom_tokens(
    theme: ShadcnTheme,
    custom_tokens: dict[str, dict[str, str] | str] | None,
) -> ShadcnTheme:
    """Apply token overrides after parsing and before palette selection."""
    if not custom_tokens:
        return theme

    if all(key in {"light", "dark"} for key in custom_tokens):
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
    """Return a new token set with overrides applied."""
    if not overrides:
        return tokens
    data = tokens.model_dump()
    for key, raw_value in overrides.items():
        if key not in data:
            continue
        data[key] = raw_value
    return ShadcnThemeTokens(**data)


def _looks_like_jinja(content: str) -> bool:
    """Return True when ``content`` contains Jinja delimiters."""
    return "{{" in content or "{%" in content


def _atomic_write(path: Path, content: str) -> None:
    """Write ``content`` to ``path`` atomically via a temporary file."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
