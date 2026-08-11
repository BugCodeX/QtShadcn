"""QtShadcn theme mode resolution."""

import darkdetect

from ..exceptions import QtShadcnError
from ..models import ThemeMode


def _normalize_theme_mode(theme_mode: str) -> ThemeMode:
    """Validate and return a normalized ThemeMode value."""
    try:
        return ThemeMode(theme_mode)
    except ValueError as e:
        raise QtShadcnError(
            f"Invalid theme_mode {theme_mode!r}; expected 'light', 'dark', or 'auto'"
        ) from e


def _resolve_is_dark(theme_mode: ThemeMode, default_theme: str) -> bool:
    """Resolve whether the active palette should be dark."""
    if theme_mode == ThemeMode.AUTO:
        detected = darkdetect.theme()
        if detected == "Dark":
            return True
        if detected == "Light":
            return False
        return default_theme == "dark"
    return theme_mode == ThemeMode.DARK
