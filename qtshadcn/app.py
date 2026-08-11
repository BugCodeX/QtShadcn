"""QtShadcn theme application.

Loads a native QtShadcn XML theme, resolves tokens, caches the resolved output,
renders QSS, and applies it to the Qt application. The core runtime only accepts
local XML themes.
"""

import json
import logging
from pathlib import Path
from typing import Any

import darkdetect
import jinja2

from ._icons import ThemedIconManager
from ._parser import ThemeParseError, parse_theme_source, resolve_value
from ._qt import QtCore, QtGui, QtWidgets
from .exceptions import QtShadcnError, ThemeRenderError
from .models import ShadcnTheme, ShadcnThemeTokens, ThemeConfig, ThemeMode
from .tokens import colors, radius, scale

logger = logging.getLogger(__name__)

TEMPLATE_FILE = str(Path(__file__).resolve().parent / "styles" / "shadcn.jinja")
DEFAULT_THEME_FILE = Path(__file__).resolve().parent / "themes" / "default.xml"


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
    assert theme is not None
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


def _build_theme(
    tokens: ShadcnThemeTokens,
    template: str = TEMPLATE_FILE,
    *,
    is_dark: bool = False,
    additional_qss: str | None = None,
) -> str:
    """Render the QSS stylesheet from resolved tokens.

    If ``additional_qss`` is provided it is treated as a Jinja template string
    and rendered with the same token context, then appended to the base
    stylesheet. It may also be a path to a ``.jinja`` or ``.qss`` file, in
    which case its content is loaded from disk before rendering.
    """
    try:
        _add_fonts()
    except Exception as e:
        logger.warning("Error loading fonts: %s", e)

    render_context = {
        "tokens": tokens,
        "colors": colors,
        "icons": ThemedIconManager(),
        "radius": radius,
        "scale": scale,
        "is_dark": is_dark,
    }

    try:
        template_path = Path(template)
        if template_path.exists():
            parent = str(template_path.parent)
            template_name = template_path.name
            loader = jinja2.FileSystemLoader(parent)
            env = jinja2.Environment(autoescape=False, loader=loader)
            base_tpl = env.get_template(template_name)
        else:
            env = jinja2.Environment(autoescape=False, loader=jinja2.BaseLoader())
            base_tpl = env.from_string(template)

        stylesheet = base_tpl.render(**render_context)
    except jinja2.TemplateError as e:
        raise ThemeRenderError(f"Failed to render QSS theme template: {e}") from e

    if additional_qss:
        stylesheet += "\n" + _render_custom_snippet(additional_qss, render_context)

    return stylesheet


def _render_custom_snippet(custom: str, context: dict) -> str:
    """Render a custom QSS Jinja snippet and return the resulting string.

    ``custom`` may be:

    * A path to a ``.jinja`` or ``.qss`` file — its content is loaded from
      disk and rendered as a Jinja template.
    * A raw Jinja template string — rendered directly.

    Raises :class:`~qtshadcn.exceptions.ThemeRenderError` on any Jinja error.
    """
    custom_path = Path(custom)
    if custom_path.suffix.lower() in {".jinja", ".qss"} and custom_path.exists():
        logger.debug("Loading custom theme snippet from file: %s", custom_path)
        try:
            loader = jinja2.FileSystemLoader(str(custom_path.parent))
            env = jinja2.Environment(autoescape=False, loader=loader)
            tpl = env.get_template(custom_path.name)
        except jinja2.TemplateError as e:
            raise ThemeRenderError(f"Failed to load custom theme file '{custom_path}': {e}") from e
    else:
        env = jinja2.Environment(autoescape=False, loader=jinja2.BaseLoader())
        try:
            tpl = env.from_string(custom)
        except jinja2.TemplateError as e:
            raise ThemeRenderError(f"Failed to parse custom theme snippet: {e}") from e

    try:
        return tpl.render(**context)
    except jinja2.TemplateError as e:
        raise ThemeRenderError(f"Failed to render custom theme snippet: {e}") from e


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


def _cache_hit(
    saved_config: ThemeConfig | None,
    saved_theme: ShadcnTheme | None,
    saved_mtime: float | None,
    config: ThemeConfig,
    current_mtime: float,
) -> bool:
    """Return True when the saved cache matches the requested configuration."""
    return (
        saved_config is not None
        and saved_theme is not None
        and saved_mtime is not None
        and saved_config == config
        and saved_mtime == current_mtime
    )


def _save_theme(config: ThemeConfig, theme: ShadcnTheme, mtime: float) -> None:
    """Persist configuration, resolved theme, and source mtime to AppData."""
    try:
        app_data_path = QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.AppDataLocation
        )
        dir_path = Path(app_data_path)
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / "theme.json"

        data = {
            "config": config.model_dump(),
            "theme": theme.model_dump(),
            "mtime": mtime,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        logger.error("Could not save theme cache to AppData: %s", e)


def _load_theme_cache() -> tuple[ThemeConfig | None, ShadcnTheme | None, float | None]:
    """Load the cached theme, configuration, and source mtime from disk."""
    try:
        app_data_path = QtCore.QStandardPaths.writableLocation(
            QtCore.QStandardPaths.StandardLocation.AppDataLocation
        )
        file_path = Path(app_data_path) / "theme.json"

        if not file_path.exists():
            return None, None, None

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        saved_config = ThemeConfig.model_validate(data.get("config", {}))
        saved_mtime = data.get("mtime")
        saved_theme = None
        if "theme" in data:
            saved_theme = ShadcnTheme.model_validate(data["theme"])

        return saved_config, saved_theme, saved_mtime
    except Exception as e:
        logger.error("Error reading theme cache: %s", e)
        return None, None, None


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

    fonts_path = Path(__file__).parent / "fonts"

    if not fonts_path.exists() or not fonts_path.is_dir():
        return

    for font_dir in fonts_path.iterdir():
        if not font_dir.is_dir():
            continue

        for font_file in font_dir.glob("*.[to]tf"):
            font_id = QtGui.QFontDatabase.addApplicationFont(str(font_file))
            if font_id == -1:
                logger.warning("Could not load font: %s", font_file.name)
