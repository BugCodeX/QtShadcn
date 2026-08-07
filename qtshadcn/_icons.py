"""Internal themed SVG icon cache helpers."""

from __future__ import annotations

import hashlib
import logging
import re
import tempfile
from html import escape
from pathlib import Path

from ._qt import QtCore

logger = logging.getLogger(__name__)

_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


class ThemedIconManager:
    """Generate and cache small themed SVG assets for QSS usage."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Create a manager that writes icons to a runtime cache directory."""
        self.cache_dir = cache_dir or _runtime_icon_cache_dir()
        logger.debug("Icon cache directory: %s", self.cache_dir)

    def checkbox_check(self, color: str) -> str:
        """Return a QSS-safe URL for a checkbox check icon using ``color``."""
        logger.debug("Generating checkbox check icon for color: %s", color)
        return self._write_icon("checkbox-check", color, _checkbox_check_svg(color))

    def checkbox_indeterminate(self, color: str) -> str:
        """Return a QSS-safe URL for a checkbox indeterminate icon using ``color``."""
        logger.debug("Generating checkbox indeterminate icon for color: %s", color)
        return self._write_icon("checkbox-indeterminate", color, _checkbox_indeterminate_svg(color))

    def radio_checked(self, color: str) -> str:
        """Return a QSS-safe URL for a radio button checked icon using ``color``."""
        logger.debug("Generating radio button checked icon for color: %s", color)
        return self._write_icon("radio-checked", color, _radio_checked_svg(color))

    def chevron_down(self, color: str) -> str:
        """Return a QSS-safe URL for a chevron down icon using ``color``."""
        logger.debug("Generating chevron down icon for color: %s", color)
        return self._write_icon("chevron-down", color, _chevron_down_svg(color))

    def chevron_up(self, color: str) -> str:
        """Return a QSS-safe URL for a chevron up icon using ``color``."""
        logger.debug("Generating chevron up icon for color: %s", color)
        return self._write_icon("chevron-up", color, _chevron_up_svg(color))

    def slider_thumb(self, fill: str, border: str, size: int) -> str:
        """Return a QSS-safe URL for a circular slider thumb icon.

        Args:
            fill: Fill color for the thumb circle.
            border: Stroke color for the thumb border.
            size: Width and height of the generated SVG in pixels.

        """
        logger.debug("Generating slider thumb icon for fill: %s border: %s", fill, border)
        name = f"slider-thumb-{size}"
        key = f"{fill}-{border}-{size}"
        svg = _slider_thumb_svg(fill, border, size)
        return self._write_icon(name, key, svg)

    def _write_icon(self, name: str, color: str, svg: str) -> str:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        color_key = _safe_name(color)
        digest = hashlib.sha256(color.encode("utf-8")).hexdigest()[:12]
        path = self.cache_dir / f"{name}-{color_key}-{digest}.svg"

        if not path.exists() or path.read_text(encoding="utf-8") != svg:
            try:
                path.write_text(svg, encoding="utf-8")
                logger.debug("Wrote icon: %s", path)
            except OSError as e:
                logger.error("Failed to write icon %s: %s", path, e)
                raise

        return str(path.resolve()).replace("\\", "/")


def _runtime_icon_cache_dir() -> Path:
    for location in (
        QtCore.QStandardPaths.CacheLocation,
        QtCore.QStandardPaths.AppDataLocation,
    ):
        base = QtCore.QStandardPaths.writableLocation(location)
        if base:
            return Path(base) / "icons"

    return Path(tempfile.gettempdir()) / "qtshadcn" / "icons"


def _safe_name(value: str) -> str:
    safe = _SAFE_NAME_RE.sub("-", value.strip()).strip("-._").lower()
    return safe[:40] or "color"


def _checkbox_check_svg(color: str) -> str:
    safe_color = escape(color, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16" fill="none">'
        f'<path d="M13.333 4 6 11.333 2.667 8" stroke="{safe_color}" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )


def _checkbox_indeterminate_svg(color: str) -> str:
    safe_color = escape(color, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16" fill="none">'
        f'<path d="M3 8h10" stroke="{safe_color}" '
        'stroke-width="2" stroke-linecap="round"/>'
        "</svg>"
    )


def _radio_checked_svg(color: str) -> str:
    safe_color = escape(color, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16" fill="none">'
        f'<circle cx="8" cy="8" r="4" fill="{safe_color}"/>'
        "</svg>"
    )


def _chevron_down_svg(color: str) -> str:
    safe_color = escape(color, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16" fill="none">'
        f'<path d="M4 6l4 4 4-4" stroke="{safe_color}" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )


def _chevron_up_svg(color: str) -> str:
    safe_color = escape(color, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" '
        'viewBox="0 0 16 16" fill="none">'
        f'<path d="M4 10l4-4 4 4" stroke="{safe_color}" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        "</svg>"
    )


def _slider_thumb_svg(fill: str, border: str, size: int) -> str:
    safe_fill = escape(fill, quote=True)
    safe_border = escape(border, quote=True)
    radius = size / 2
    stroke_width = radius / 5
    # Inset the circle so the stroke stays fully inside the viewBox.
    r = radius - stroke_width / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        f'viewBox="0 0 {size} {size}" fill="none">'
        f'<circle cx="{radius}" cy="{radius}" r="{r}" fill="{safe_fill}" '
        f'stroke="{safe_border}" stroke-width="{stroke_width}"/>'
        "</svg>"
    )
