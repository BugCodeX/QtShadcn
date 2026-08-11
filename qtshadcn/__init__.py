from typing import Any

from .exceptions import QtBindingError, QtShadcnError, ThemeParseError, ThemeRenderError
from .models import ShadcnTheme, ShadcnThemeTokens

__version__ = "0.2.0"


def __getattr__(name: str) -> Any:
    """Lazily resolve Qt-dependent package exports."""
    if name in {"apply_theme", "get_theme"}:
        try:
            from .common.theme import apply_theme, get_theme
        except ImportError as exc:
            try:
                from qtpy import QtBindingsNotFoundError, QtModuleNotInstalledError
            except ImportError:
                # qtpy itself is unavailable; treat import failures that involve
                # qtpy or a Qt binding as a binding error.
                failed_module = getattr(exc, "name", "") or str(exc) or ""
                root = failed_module.split(".", 1)[0]
                if root in {"qtpy", "PySide6", "PyQt6", "PySide2", "PyQt5"}:
                    raise QtBindingError(
                        "No supported Qt binding found. Install one of: PySide6, PyQt6, "
                        "PySide2, or PyQt5, then set QT_API to the binding name "
                        "(e.g., QT_API=pyside6) before importing qtshadcn."
                    ) from exc
                raise
            if isinstance(exc, QtBindingsNotFoundError | QtModuleNotInstalledError):
                raise QtBindingError(
                    "No supported Qt binding found. Install one of: PySide6, PyQt6, "
                    "PySide2, or PyQt5, then set QT_API to the binding name "
                    "(e.g., QT_API=pyside6) before importing qtshadcn."
                ) from exc
            raise

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
