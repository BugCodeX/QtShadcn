"""QtShadcn theme application.

Loads a native QtShadcn XML theme, resolves tokens, caches the resolved output,
renders QSS, and applies it to the Qt application. The core runtime only accepts
local XML themes.
"""

import json
import logging
from pathlib import Path

import darkdetect
import jinja2
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from .models import ShadcnTheme, ShadcnThemeTokens, ThemeConfig
from .parser import ThemeParseError, parse_theme_source
from .tokens import colors, radius, scale

logger = logging.getLogger(__name__)

TEMPLATE_FILE = str(Path(__file__).resolve().parent / "styles" / "shadcn.jinja")
DEFAULT_THEME_FILE = Path(__file__).resolve().parent / "themes" / "default.xml"


def apply_theme(app: QApplication, config: ThemeConfig | None = None) -> ShadcnThemeTokens:
    """Apply a QtShadcn XML theme and return the active palette.

    If ``config`` is None or omits ``theme_source_path``, the packaged default
    XML theme is used. The theme source is parsed, resolved, cached by path +
    mtime, rendered to QSS, and applied via ``setStyleSheet``.
    """
    saved_config, saved_theme, saved_mtime = _load_theme_cache()

    if config is None:
        config = ThemeConfig()

    source_path = _resolve_theme_source_path(config)
    source_key = str(source_path)
    saved_source_key = str(_resolve_theme_source_path(saved_config)) if saved_config else None
    is_dark = (
        bool(darkdetect.isDark()) if config.theme_mode == "auto" else config.theme_mode == "dark"
    )

    # Cache hit: same source path and unchanged mtime.
    current_mtime = _get_mtime(source_path)
    if (
        saved_config
        and saved_theme
        and saved_mtime is not None
        and source_key == saved_source_key
        and config.theme_mode == saved_config.theme_mode
        and current_mtime == saved_mtime
    ):
        logger.debug("Theme cache hit: %s", source_path)
        theme = saved_theme
    else:
        logger.debug("Parsing theme: %s", source_path)
        theme = parse_theme_source(source_path)
        _save_theme(config, theme, current_mtime)

    active_tokens = theme.dark if is_dark else theme.light
    mode_label = "dark" if is_dark else "light"

    stylesheet = _build_theme(active_tokens, is_dark=is_dark)

    # test export css
    # with open("debug_theme.qss", "w", encoding="utf-8") as f:
    #     f.write(stylesheet)

    app.setStyleSheet(stylesheet)
    logger.info("Applied %s theme from: %s", mode_label, source_path)

    return active_tokens


def get_theme() -> ShadcnTheme | None:
    """Return the resolved QtShadcn theme currently stored in cache."""
    _, saved_theme, _ = _load_theme_cache()
    return saved_theme


def _build_theme(
    tokens: ShadcnThemeTokens, template: str = TEMPLATE_FILE, *, is_dark: bool = False
) -> str:
    """Render the QSS stylesheet from resolved tokens."""
    try:
        _add_fonts()
    except Exception as e:
        logger.warning("Error loading fonts: %s", e)

    template_path = Path(template)
    if template_path.exists():
        parent = str(template_path.parent)
        template_name = template_path.name
        loader = jinja2.FileSystemLoader(parent)
        env = jinja2.Environment(autoescape=False, loader=loader)
        stylesheet = env.get_template(template_name)
    else:
        env = jinja2.Environment(autoescape=False, loader=jinja2.BaseLoader())
        stylesheet = env.from_string(template)

    return stylesheet.render(
        tokens=tokens,
        colors=colors,
        radius=radius,
        scale=scale,
        is_dark=is_dark,
    )


def _resolve_theme_source_path(config: ThemeConfig) -> Path:
    """Return the configured XML path or the packaged default theme path."""
    if config.theme_source_path:
        return Path(config.theme_source_path)
    return DEFAULT_THEME_FILE


def _save_theme(config: ThemeConfig, theme: ShadcnTheme, mtime: float) -> None:
    """Persist configuration, resolved theme, and source mtime to AppData."""
    try:
        app_data_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
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
        app_data_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
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
    if QApplication.instance() is None:
        return

    fonts_path = Path(__file__).parent / "fonts"

    if not fonts_path.exists() or not fonts_path.is_dir():
        return

    for font_dir in fonts_path.iterdir():
        if not font_dir.is_dir():
            continue

        for font_file in font_dir.glob("*.[to]tf"):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id == -1:
                logger.warning("Could not load font: %s", font_file.name)
