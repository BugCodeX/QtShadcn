from typing import Any

from .exceptions import QtBindingError, QtShadcnError, ThemeParseError, ThemeRenderError
from .models import ShadcnTheme, ShadcnThemeTokens

__version__ = "0.1.1"


def __getattr__(name: str) -> Any:
    """Lazily resolve Qt-dependent package exports."""
    if name in {"apply_theme", "get_theme"}:
        from .common.theme import apply_theme, get_theme

        return {"apply_theme": apply_theme, "get_theme": get_theme}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Models
    "ShadcnTheme",
    "ShadcnThemeTokens",
    # Functions
    "apply_theme",
    "get_theme",
    "__version__",
    # Errors
    "QtShadcnError",
    "ThemeParseError",
    "ThemeRenderError",
    "QtBindingError",
]
