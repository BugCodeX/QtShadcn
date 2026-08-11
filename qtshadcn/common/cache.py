"""QtShadcn theme cache persistence."""

import json
import logging
from pathlib import Path

from ..models import ShadcnTheme, ThemeConfig
from .binding import QtCore

logger = logging.getLogger(__name__)


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
