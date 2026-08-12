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
from .config import ThemeMode, _atomic_write, qsettings
from .helpers import _apply_custom_tokens, _looks_like_jinja, _resolve_theme_file
from .renderer import _build_theme
from .theme_parser import parse_theme_source

logger = logging.getLogger(__name__)

_default_theme: str = "dark"


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


def _load_theme_from_dir(cfg_dir: Path) -> ShadcnTheme | None:
    """Load a persisted theme from ``cfg_dir`` (JSON primary, XML fallback)."""
    theme_json = cfg_dir / "theme.json"
    if theme_json.exists():
        try:
            data = json.loads(theme_json.read_text(encoding="utf-8"))
            data.pop("version", None)
            return ShadcnTheme.model_validate(data)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not load theme.json from %s: %s", cfg_dir, e)
    theme_xml = cfg_dir / "theme.xml"
    if theme_xml.exists():
        try:
            return parse_theme_source(theme_xml)
        except ThemeParseError as e:
            logger.warning("Could not load theme.xml from %s: %s", cfg_dir, e)
    return None


def _active_theme() -> ShadcnTheme:
    """Return the currently active theme, loading the default if needed."""
    if qsettings._theme is None:
        loaded = _load_theme_from_dir(qsettings.config_dir())
        qsettings._theme = loaded or parse_theme_source(_resolve_theme_file(None))
    return qsettings._theme


def _render_and_apply(*, default_theme: str | None = None) -> None:
    """Render the current theme and apply it to ``QApplication`` if it exists."""
    app = cast(Any, QtWidgets.QApplication.instance())
    if app is None:
        return

    theme = _active_theme()
    mode = ThemeMode(qsettings.theme_mode.value)
    fallback = default_theme if default_theme is not None else _default_theme
    is_dark = _resolve_is_dark(mode, fallback)
    tokens = theme.dark if is_dark else theme.light
    additional = qsettings.additional_style_sheet.value

    try:
        stylesheet = _build_theme(tokens, is_dark=is_dark, additional_qss=additional)
        app.setStyleSheet(stylesheet)
    except ThemeRenderError:
        logger.exception("Failed to render stylesheet")
        raise


def _load_callback(_settings: Any) -> None:
    """Apply loaded state by re-rendering the stylesheet."""
    _render_and_apply()


qsettings._on_load = _load_callback


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


def _set_theme_mode(
    mode: ThemeMode | str, *, save: bool = True, default_theme: str | None = None
) -> ThemeMode:
    """Set the active theme mode and re-render the stylesheet.

    Args:
        mode: One of ``ThemeMode.AUTO``, ``ThemeMode.LIGHT``, ``ThemeMode.DARK``,
            or the equivalent string values.
        save: When ``True`` (default), persist the mode to
            ``config/theme_mode.json``.
        default_theme: Optional fallback palette for ``auto`` mode when OS
            detection fails. Used internally by deprecated wrappers.

    Returns:
        The normalized ``ThemeMode`` that was applied.

    """
    mode_enum = _normalize_theme_mode(mode)
    qsettings.theme_mode.set(mode_enum.value)
    if save:
        qsettings.save(only={"theme_mode"})
    _render_and_apply(default_theme=default_theme)
    return mode_enum


def setThemeMode(mode: ThemeMode | str, *, save: bool = True) -> None:
    """Set the active theme mode and re-render the stylesheet.

    Args:
        mode: One of ``ThemeMode.AUTO``, ``ThemeMode.LIGHT``, ``ThemeMode.DARK``,
            or the equivalent string values.
        save: When ``True`` (default), persist the mode to
            ``config/theme_mode.json``.

    """
    _set_theme_mode(mode, save=save)


def toggleThemeMode(save: bool = True) -> None:
    """Cycle the theme mode: auto → light → dark → auto."""
    theme = ThemeMode.LIGHT if isDarkTheme() else ThemeMode.DARK
    setThemeMode(theme, save=save)


def themeMode() -> ThemeMode:
    """Return the active theme mode."""
    return ThemeMode(qsettings.theme_mode.value)


def isDarkTheme() -> bool:
    """Return whether the resolved active palette is dark."""
    return _resolve_is_dark(themeMode(), _default_theme)


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
    data.pop("version", None)
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


def setTheme(
    source: str | Path | None = None,
    *,
    custom_tokens: dict[str, Any] | None = None,
    save: bool = True,
) -> None:
    """Set the active color palette and re-render the stylesheet.

    Args:
        source: Path to a QtShadcn ``.xml`` or ``.json`` theme file. If
            ``None`` (default), the bundled default theme is used.
        custom_tokens: Optional in-memory token overrides. Shared overrides
            apply to both palettes; per-mode overrides use ``light``/``dark``
            top-level keys.
        save: When ``True`` (default), persist the palette to ``config/``.

    """
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
            data["version"] = 1
            _atomic_write(cfg_dir / "theme.json", json.dumps(data, indent=2))
        else:
            _write_theme_json(cfg_dir, theme)

    qsettings.themeChanged.emit()
    _render_and_apply()


def _write_theme_json(cfg_dir: Path, theme: ShadcnTheme) -> None:
    data = {"version": 1, **theme.model_dump()}
    _atomic_write(cfg_dir / "theme.json", json.dumps(data, indent=2))


def getTheme() -> ShadcnThemeTokens:
    """Return the active palette tokens for the current mode."""
    theme = _active_theme()
    return theme.dark if isDarkTheme() else theme.light


def _read_style_source(source: str | Path) -> str:
    """Return the contents of ``source`` if it is a path, otherwise the string."""
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return str(source)


def setStyleSheet(source: str | Path, *, save: bool = True) -> None:
    """Set the additional stylesheet layered on top of the base QSS.

    Args:
        source: Inline QSS/Jinja string or path to a ``.qss``/``.jinja`` file.
        save: When ``True`` (default), persist to ``config/style.jinja`` or
            ``config/style.qss``.

    """
    content = _read_style_source(source)
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


# Keep QtCore.Qt alias import for type checkers that need Signal type reference.
_ = QtCore
