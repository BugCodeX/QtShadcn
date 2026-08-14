"""QtShadcn — modern styling and theming framework for Qt/PyQt/PySide."""

from .exceptions import QtBindingError, QtShadcnError, ThemeParseError, ThemeRenderError
from .models import ShadcnTheme, ShadcnThemeTokens

__version__ = "0.4.0"

try:
    from qtpy import QtBindingsNotFoundError, QtModuleNotInstalledError
except ImportError as exc:
    raise QtBindingError(
        "No supported Qt binding found. Install one of: PySide6, PyQt6, "
        "PySide2, or PyQt5, then set QT_API to the binding name "
        "(e.g., QT_API=pyside6) before importing qtshadcn."
    ) from exc

try:
    from .common.config import ThemeMode, qsettings
    from .common.stylesheet import (
        getStyleSheet,
        getTheme,
        isDarkTheme,
        setStyleSheet,
        setTheme,
        setThemeMode,
        themeMode,
        toggleThemeMode,
    )
    from .common.theme_watcher import SystemThemeListener
except (QtBindingsNotFoundError, QtModuleNotInstalledError) as exc:
    raise QtBindingError(
        "No supported Qt binding found. Install one of: PySide6, PyQt6, "
        "PySide2, or PyQt5, then set QT_API to the binding name "
        "(e.g., QT_API=pyside6) before importing qtshadcn."
    ) from exc

__all__ = [
    # Version
    "__version__",
    # Models
    "ShadcnTheme",
    "ShadcnThemeTokens",
    # API
    "qsettings",
    "setThemeMode",
    "toggleThemeMode",
    "themeMode",
    "isDarkTheme",
    "setTheme",
    "getTheme",
    "setStyleSheet",
    "getStyleSheet",
    "ThemeMode",
    "SystemThemeListener",
    # Errors
    "QtShadcnError",
    "ThemeParseError",
    "ThemeRenderError",
    "QtBindingError",
]
