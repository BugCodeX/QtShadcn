"""QtShadcn stylesheet rendering and three-concept theme API.

This module owns the render pipeline and the public functions for controlling
mode, color palette, and additional QSS.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any, cast

import darkdetect
from qtpy import QtCore, QtWidgets

from ..exceptions import QtShadcnError, ThemeParseError, ThemeRenderError
from ..models import ShadcnTheme, ShadcnThemeTokens
from .config import ThemeMode, _load_theme_from_dir, qsettings
from .helpers import _apply_custom_tokens, _atomic_write, _looks_like_jinja, _resolve_theme_file
from .renderer import _build_theme
from .theme_parser import _parse_theme_source

logger = logging.getLogger(__name__)

_default_theme: str = "dark"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_is_dark(mode: ThemeMode, default_theme: str = "dark") -> bool:
    """Resolve whether the active palette should be dark."""
    if mode == ThemeMode.AUTO:
        detected = darkdetect.theme()
        if detected == "Dark":
            return True
        if detected == "Light":
            return False
        return default_theme == "dark"
    return mode == ThemeMode.DARK


def _active_theme() -> ShadcnTheme:
    """Return the currently active theme, loading the default if needed."""
    if qsettings._theme is None:
        loaded, _ = _load_theme_from_dir(qsettings.config_dir())
        qsettings._theme = loaded or _parse_theme_source(_resolve_theme_file(None))
    return qsettings._theme


def _render_and_apply() -> None:
    """Render the current theme and apply it to ``QApplication`` if it exists."""
    app = cast(Any, QtWidgets.QApplication.instance())
    if app is None:
        return

    theme = _active_theme()
    mode = ThemeMode(qsettings.theme_mode.value)
    is_dark = _resolve_is_dark(mode, _default_theme)
    tokens = theme.dark if is_dark else theme.light
    additional = qsettings.additional_style_sheet.value

    try:
        stylesheet = _build_theme(tokens, is_dark=is_dark, additional_qss=additional)
        app.setStyleSheet(stylesheet)
    except ThemeRenderError:
        logger.exception("Failed to render stylesheet")
        raise


def _normalize_theme_mode(mode: ThemeMode | str) -> ThemeMode:
    """Validate and return a normalized ``ThemeMode`` value."""
    if isinstance(mode, ThemeMode):
        return mode
    try:
        return ThemeMode(mode)
    except ValueError as e:
        raise QtShadcnError(
            f"Invalid theme_mode {mode!r}; expected 'light', 'dark', or 'auto'"
        ) from e


def _write_theme_json(cfg_dir: Path, theme: ShadcnTheme) -> None:
    """Persist the parsed theme as JSON in the config directory."""
    data = theme.model_dump()
    _atomic_write(cfg_dir / "theme.json", json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def setThemeMode(mode: ThemeMode | str, *, save: bool = True) -> None:
    """Set the active theme mode and re-render the stylesheet."""
    mode_enum = _normalize_theme_mode(mode)
    qsettings.theme_mode.set(mode_enum.value)
    if save:
        qsettings.save(only={"theme_mode"})
    _render_and_apply()


def toggleThemeMode(*, save: bool = True) -> None:
    """Toggle between light and dark based on the resolved active palette."""
    theme = ThemeMode.LIGHT if isDarkTheme() else ThemeMode.DARK
    setThemeMode(theme, save=save)


def themeMode() -> ThemeMode:
    """Return the active theme mode."""
    return ThemeMode(qsettings.theme_mode.value)


def isDarkTheme() -> bool:
    """Return whether the resolved active palette is dark."""
    return _resolve_is_dark(themeMode(), _default_theme)


def setTheme(
    source: str | Path | None = None,
    *,
    custom_tokens: dict[str, Any] | None = None,
    save: bool = True,
) -> None:
    """Set the active color palette and re-render the stylesheet."""
    path = _resolve_theme_file(source) if source is None else Path(source)
    if not path.exists():
        raise ThemeParseError(f"Could not read theme source: {path}")

    theme = _parse_theme_source(path)
    theme = _apply_custom_tokens(theme, custom_tokens)

    qsettings._theme = theme
    qsettings.theme.set(str(path))

    if save:
        cfg_dir = qsettings.config_dir()
        cfg_dir.mkdir(parents=True, exist_ok=True)
        suffix = path.suffix.lower()
        if suffix == ".xml":
            dst_xml = cfg_dir / "theme.xml"
            if path.resolve() != dst_xml.resolve():
                shutil.copy2(path, dst_xml)
            _write_theme_json(cfg_dir, theme)
        elif suffix == ".json":
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                raise ThemeParseError(f"Could not read theme source: {path}") from e
            _atomic_write(cfg_dir / "theme.json", json.dumps(data, indent=2))
        else:
            _write_theme_json(cfg_dir, theme)

    qsettings.themeChanged.emit()
    _render_and_apply()


def getTheme() -> ShadcnThemeTokens:
    """Return the active palette tokens for the current mode."""
    theme = _active_theme()
    return theme.dark if isDarkTheme() else theme.light


def setStyleSheet(source: str | Path, *, save: bool = True) -> None:
    """Set the additional stylesheet layered on top of the base QSS."""
    path = Path(source)
    content = path.read_text(encoding="utf-8") if path.exists() else str(source)
    qsettings.additional_style_sheet.set(content)

    if save:
        cfg_dir = qsettings.config_dir()
        cfg_dir.mkdir(parents=True, exist_ok=True)
        if _looks_like_jinja(content):
            _atomic_write(cfg_dir / "style.jinja", content)
            (cfg_dir / "style.qss").unlink(missing_ok=True)
        else:
            _atomic_write(cfg_dir / "style.qss", content)
            (cfg_dir / "style.jinja").unlink(missing_ok=True)

    qsettings.additionalStyleSheetChanged.emit()
    _render_and_apply()


def getStyleSheet() -> str:
    """Return the current additional stylesheet content."""
    return qsettings.additional_style_sheet.value


# Re-render when cached settings are loaded after QApplication startup.
qsettings._on_load = lambda _settings: _render_and_apply()

# Keep QtCore.Qt alias import for type checkers that need Signal type reference.
_ = QtCore
