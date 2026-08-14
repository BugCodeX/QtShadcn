"""QtShadcn persistent configuration system.

Provides ``ThemeMode``, ``ConfigItem``, and the ``qsettings`` singleton that
backs the three-concept theme API in :mod:`~qtshadcn.common.stylesheet`.
"""

from __future__ import annotations

import copy
import json
import logging
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

from qtpy import QtCore

from ..models import ShadcnTheme
from .helpers import _atomic_write, _looks_like_jinja

logger = logging.getLogger(__name__)


class ThemeMode(StrEnum):
    """Theme mode selection."""

    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


_QObject: Any = QtCore.QObject


class ConfigItem(_QObject):
    """A single persisted configuration value with change notification.

    Args:
        key: Identifier used for persistence and diagnostics.
        default: Value returned before any load or set call.
        validator: Optional callable that returns ``True`` for valid values.
        parent: Optional Qt parent object.

    """

    valueChanged = QtCore.Signal(object)

    def __init__(
        self,
        key: str,
        default: Any,
        validator: Callable[[Any], bool] | None = None,
        parent: QtCore.QObject | None = None,
    ) -> None:
        """Create a config item with a key, default, and optional validator."""
        super().__init__(parent)
        self._key = key
        self._default = default
        self._value = copy.deepcopy(default)
        self._validator = validator

    @property
    def value(self) -> Any:
        """Return the current item value."""
        return self._value

    def set(self, value: Any, *, block_signal: bool = False) -> None:
        """Set the item value and emit ``valueChanged`` unless blocked."""
        if self._validator is not None and not self._validator(value):
            return
        if value == self._value:
            return
        self._value = value
        if not block_signal:
            self.valueChanged.emit(value)

    def reset(self, *, block_signal: bool = False) -> None:
        """Reset the value to the configured default and notify listeners."""
        self.set(self._default, block_signal=block_signal)

    def serialize(self) -> Any:
        """Return a JSON-serializable representation of the value."""
        return self._value

    def deserialize(self, raw: Any) -> bool:
        """Load a raw value and return whether validation passed."""
        if self._validator is not None and not self._validator(raw):
            return False
        self._value = raw
        return True


class QtShadcnSettings(_QObject):
    """Persistent settings backbone for QtShadcn.

    Holds three scalar config items (``theme_mode``, ``theme`` source path, and
    ``additional_style_sheet``) plus the parsed ``ShadcnTheme`` in memory. The
    actual QSS rendering lives in
    :mod:`~qtshadcn.common.stylesheet`.
    """

    themeChanged = QtCore.Signal()
    additionalStyleSheetChanged = QtCore.Signal()

    def __init__(self, parent: QtCore.QObject | None = None) -> None:
        """Create the settings backbone with default config items."""
        super().__init__(parent)
        self.theme_mode = ConfigItem(
            "theme_mode",
            ThemeMode.AUTO.value,
            self._validate_mode,
            self,
        )
        self.theme = ConfigItem(
            "theme",
            "",
            self._validate_theme_source,
            self,
        )
        self.additional_style_sheet = ConfigItem(
            "additional_style_sheet",
            "",
            None,
            self,
        )
        self._config_dir: Path | None = None
        self._on_load: Callable[[QtShadcnSettings], None] | None = None
        self._theme: ShadcnTheme | None = None

    @staticmethod
    def _validate_mode(value: Any) -> bool:
        return isinstance(value, str) and value in set(ThemeMode)

    @staticmethod
    def _validate_theme_source(value: Any) -> bool:
        return isinstance(value, str)

    def config_dir(self) -> Path:
        """Return the directory used for persisted config files."""
        if self._config_dir is not None:
            return self._config_dir
        app_data = QtCore.QStandardPaths.writableLocation(
            cast(Any, QtCore.QStandardPaths.StandardLocation.AppDataLocation)
        )
        return Path(app_data) / "config"

    def set_config_dir(self, config_dir: str | Path | None) -> None:
        """Override the default config directory."""
        self._config_dir = Path(config_dir) if config_dir is not None else None

    def load(
        self,
        config_dir: str | Path | None = None,
        *,
        settings: QtShadcnSettings | None = None,
    ) -> None:
        """Restore persisted state from ``config_dir``.

        Args:
            config_dir: Directory to read config files from. Uses
                ``QStandardPaths.AppDataLocation/config/`` when omitted.
            settings: Optional custom settings instance to populate instead of
                the singleton. This lets advanced callers load into their own
                settings object while still using the same file layout.

        """
        target = settings if settings is not None else self
        if config_dir is not None:
            target.set_config_dir(config_dir)
        elif target._config_dir is None:
            target.set_config_dir(None)

        cfg_dir = target.config_dir()
        cfg_dir.mkdir(parents=True, exist_ok=True)

        self._load_theme_mode(target, cfg_dir)
        self._load_theme(target, cfg_dir)
        self._load_style_sheet(target, cfg_dir)

        callback = target._on_load if target._on_load is not None else self._on_load
        if callback is not None:
            callback(target)

        target.theme_mode.valueChanged.emit(target.theme_mode.value)
        target.themeChanged.emit()
        target.additionalStyleSheetChanged.emit()

    def _load_theme_mode(self, target: QtShadcnSettings, cfg_dir: Path) -> None:
        mode_path = cfg_dir / "theme_mode.json"
        mode = ThemeMode.AUTO.value
        if mode_path.exists():
            try:
                data = json.loads(mode_path.read_text(encoding="utf-8"))
                mode = data.get("mode", ThemeMode.AUTO.value)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Corrupt theme_mode.json, resetting to auto: %s", e)
        if not target.theme_mode.deserialize(mode):
            target.theme_mode.reset(block_signal=True)

    def _load_theme(self, target: QtShadcnSettings, cfg_dir: Path) -> None:
        theme, source = _load_theme_from_dir(cfg_dir)
        target._theme = theme
        target.theme.deserialize(source)

    def _load_style_sheet(self, target: QtShadcnSettings, cfg_dir: Path) -> None:
        style_jinja = cfg_dir / "style.jinja"
        style_qss = cfg_dir / "style.qss"
        content = ""
        if style_jinja.exists():
            content = style_jinja.read_text(encoding="utf-8")
        elif style_qss.exists():
            content = style_qss.read_text(encoding="utf-8")
        target.additional_style_sheet.deserialize(content)

    def save(self, *, only: set[str] | None = None) -> None:
        """Persist current state to ``config_dir``.

        Args:
            only: Optional subset of
                ``{"theme_mode", "theme", "additional_style_sheet"}`` to write.
                When omitted, all known files are written.

        """
        cfg_dir = self.config_dir()
        cfg_dir.mkdir(parents=True, exist_ok=True)

        keys = only if only is not None else {"theme_mode", "theme", "additional_style_sheet"}
        if "theme_mode" in keys:
            _atomic_write(
                cfg_dir / "theme_mode.json",
                json.dumps({"mode": self.theme_mode.serialize()}, indent=2),
            )
        if "theme" in keys and self._theme is not None:
            data = self._theme.model_dump()
            _atomic_write(cfg_dir / "theme.json", json.dumps(data, indent=2))
        if "additional_style_sheet" in keys:
            self._save_style_sheet(cfg_dir)

    def _save_style_sheet(self, cfg_dir: Path) -> None:
        content = self.additional_style_sheet.serialize()
        if _looks_like_jinja(content):
            _atomic_write(cfg_dir / "style.jinja", content)
            (cfg_dir / "style.qss").unlink(missing_ok=True)
        elif content:
            _atomic_write(cfg_dir / "style.qss", content)
            (cfg_dir / "style.jinja").unlink(missing_ok=True)

    def reset_for_test(self) -> None:
        """Reset all values to defaults and clear custom config directory."""
        self.theme_mode.reset()
        self.theme.reset()
        self.additional_style_sheet.reset()
        self._theme = None
        self._config_dir = None


def _load_theme_from_dir(cfg_dir: Path) -> tuple[ShadcnTheme | None, str]:
    """Load a persisted theme from ``cfg_dir`` (JSON primary, XML fallback).

    Returns:
        A tuple of the parsed theme (or ``None`` if no valid theme was found)
        and the source file path (empty string if no theme was found).

    """
    theme_json = cfg_dir / "theme.json"
    if theme_json.exists():
        try:
            data = json.loads(theme_json.read_text(encoding="utf-8"))
            return ShadcnTheme.model_validate(data), str(theme_json)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Could not load theme.json from %s: %s", cfg_dir, e)
    theme_xml = cfg_dir / "theme.xml"
    if theme_xml.exists():
        try:
            from .theme_parser import parse_theme_source

            return parse_theme_source(theme_xml), str(theme_xml)
        except Exception as e:
            logger.warning("Could not load theme.xml from %s: %s", cfg_dir, e)
    return None, ""


qsettings: QtShadcnSettings = QtShadcnSettings()
