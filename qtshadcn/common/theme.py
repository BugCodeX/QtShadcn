"""QtShadcn theme application.

Loads a native QtShadcn XML theme, resolves tokens, caches the resolved output,
renders QSS, and applies it to the Qt application. The core runtime only accepts
local XML themes.
"""

import logging

from qtpy import QtWidgets

from ..exceptions import QtShadcnError
from ..models import ShadcnTheme, ShadcnThemeTokens, ThemeConfig
from .cache import _cache_hit, _load_theme_cache, _save_theme
from .helpers import _apply_custom_tokens, _get_mtime, _resolve_application, _resolve_theme_file
from .renderer import _build_theme
from .theme_mode import _normalize_theme_mode, _resolve_is_dark
from .theme_parser import parse_theme_source

logger = logging.getLogger(__name__)


def apply_theme(
    app: QtWidgets.QApplication | None = None,
    theme_file: str | None = None,
    *,
    theme_mode: str = "auto",
    custom_tokens: dict[str, dict[str, str] | str] | None = None,
    additional_qss: str | None = None,
    default_theme: str = "dark",
) -> ShadcnThemeTokens:
    """Apply a QtShadcn XML theme and return the active palette.

    If ``app`` is ``None``, the existing ``QApplication.instance()`` is used.
    If no instance exists, :class:`~qtshadcn.exceptions.QtShadcnError` is raised.

    If ``theme_file`` is ``None``, the packaged default XML theme is used.
    ``theme_mode`` may be ``"light"``, ``"dark"`` or ``"auto"``. In ``"auto"``
    mode the OS preference is detected via ``darkdetect``; when detection fails,
    ``default_theme`` is used.

    ``custom_tokens`` are applied after the XML is parsed and before the active
    palette is selected. When the top-level keys are ``"light"`` and/or
    ``"dark"`` the overrides are applied per palette; otherwise the same
    overrides are applied to both palettes.

    ``additional_qss`` is appended to the base stylesheet. It may be an inline
    Jinja snippet, a ``.qss`` file path, or a ``.jinja`` file path.
    """
    app = _resolve_application(app)
    mode = _normalize_theme_mode(theme_mode)
    source_path = _resolve_theme_file(theme_file)

    if default_theme not in {"light", "dark"}:
        raise QtShadcnError(f"Invalid default_theme {default_theme!r}; expected 'light' or 'dark'")

    config = ThemeConfig(
        theme_mode=mode,
        theme_file=str(source_path),
        custom_tokens=custom_tokens,
        additional_qss=additional_qss,
        default_theme=default_theme,
    )

    saved_config, saved_theme, saved_mtime = _load_theme_cache()
    current_mtime = _get_mtime(source_path)

    if _cache_hit(saved_config, saved_theme, saved_mtime, config, current_mtime):
        logger.debug("Theme cache hit: %s", source_path)
        theme = saved_theme
    else:
        logger.debug("Parsing theme: %s", source_path)
        theme = parse_theme_source(source_path)
        theme = _apply_custom_tokens(theme, custom_tokens)
        _save_theme(config, theme, current_mtime)

    is_dark = _resolve_is_dark(mode, default_theme)
    if theme is None:
        raise QtShadcnError("Theme could not be loaded from cache or source")
    active_tokens = theme.dark if is_dark else theme.light
    mode_label = "dark" if is_dark else "light"

    stylesheet = _build_theme(active_tokens, is_dark=is_dark, additional_qss=additional_qss)

    app.setStyleSheet(stylesheet)
    logger.info("Applied %s theme from: %s", mode_label, source_path)

    return active_tokens


def get_theme() -> ShadcnTheme | None:
    """Return the resolved QtShadcn theme currently stored in cache."""
    _, saved_theme, _ = _load_theme_cache()
    return saved_theme
