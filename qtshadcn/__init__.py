"""QtShadcn — modern styling and theming framework for Qt/PyQt/PySide."""

from .exceptions import QtBindingError, QtShadcnError, ThemeParseError, ThemeRenderError
from .models import ShadcnTheme, ShadcnThemeTokens

__version__ = "0.8.0"

from .common.config import ThemeMode, qsettings
from .common.font import (
    getFontFamilies,
    getFontFamily,
    registerFontFamily,
    setFontFamilies,
    setFontFamily,
)
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
from .common.theme_watcher import SystemThemeWatcher

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
    "setFontFamily",
    "setFontFamilies",
    "getFontFamily",
    "getFontFamilies",
    "registerFontFamily",
    "ThemeMode",
    "SystemThemeWatcher",
    # Errors
    "QtShadcnError",
    "ThemeParseError",
    "ThemeRenderError",
    "QtBindingError",
]
