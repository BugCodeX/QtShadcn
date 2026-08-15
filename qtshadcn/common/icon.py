"""Internal themed SVG icon cache helpers."""

from __future__ import annotations

import hashlib
import logging
import re
import tempfile
from collections.abc import Callable
from html import escape
from importlib import resources
from pathlib import Path
from typing import Any, cast

from qtpy import QtCore

from ..exceptions import QtShadcnError

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class ThemedIconManager:
    """Generate and cache small themed SVG assets for QSS usage."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Create a manager that writes icons to a runtime cache directory."""
        self.cache_dir = cache_dir or _resolveRuntimeIconCacheDir()
        self._sessionCache: dict[str, str] = {}
        logger.debug("Icon cache directory: %s", self.cache_dir)

    def getIconUrl(self, icon_id: str, color: str) -> str:
        """Return a QSS-safe URL for the registered icon, colored with ``color``."""
        entry = _ICON_REGISTRY.get(icon_id)
        if callable(entry):
            raise QtShadcnError(
                f"Icon '{icon_id}' is dynamic and must be requested via its dedicated method."
            )
        if not isinstance(entry, str):
            raise QtShadcnError(f"Unknown icon '{icon_id}'.")
        svg = self._colorSvg(entry, color)
        return self._writeIcon(icon_id, color, svg)

    def renderSliderThumb(self, fill: str, border: str, size: int) -> str:
        """Return a QSS-safe URL for a circular slider thumb icon."""
        logger.debug("Generating slider thumb icon for fill: %s border: %s", fill, border)
        key = f"{fill}-{border}-{size}"
        svg = _buildSliderThumbSvg(fill, border, size)
        return self._writeIcon("slider-thumb", key, svg)

    def _colorSvg(self, source: str, color: str) -> str:
        """Return ``source`` with ``currentColor`` replaced by ``color``."""
        safe_color = escape(color, quote=True)
        # Modern icons use ``currentColor`` for both stroke and fill.
        # Direct string replacement is fast and avoids regex overhead.
        return source.replace("currentColor", safe_color)

    def _writeIcon(self, name: str, key: str, svg: str) -> str:
        """Write ``svg`` to disk once per unique key and return its file URL."""
        color_key = _normalizeSafeName(key)
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
        path = self.cache_dir / f"{name}-{color_key}-{digest}.svg"
        path_str = str(path.resolve()).replace("\\", "/")

        if self._sessionCache.get(key) == path_str:
            return path_str

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Compare file contents to avoid unnecessary writes and detect color changes.
        if not path.exists() or path.read_text(encoding="utf-8") != svg:
            try:
                path.write_text(svg, encoding="utf-8")
                logger.debug("Wrote icon: %s", path)
            except OSError as e:
                logger.error("Failed to write icon %s: %s", path, e)
                raise QtShadcnError(f"Failed to write icon {path}: {e}") from e

        self._sessionCache[key] = path_str
        return path_str


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _buildSliderThumbSvg(fill: str, border: str, size: int) -> str:
    """Build a circular slider thumb SVG with the exact requested size and colors.

    Kept as a factory because the thumb dimensions and colors are dynamic, unlike
    the fixed icons loaded from ``qtshadcn.resources.icons``.
    """
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


def _resolveRuntimeIconCacheDir() -> Path:
    """Return a writable directory for cached SVG icon files.

    Prefers the platform cache location and falls back to a temporary directory
    when the standard locations are unavailable (e.g. in restricted environments).
    """
    for location in (
        QtCore.QStandardPaths.StandardLocation.CacheLocation,
        QtCore.QStandardPaths.StandardLocation.AppDataLocation,
    ):
        base = QtCore.QStandardPaths.writableLocation(cast(Any, location))
        if base:
            return Path(base) / "icons"

    return Path(tempfile.gettempdir()) / "qtshadcn" / "icons"


def _normalizeSafeName(value: str) -> str:
    """Normalize ``value`` into a filesystem-safe, lowercase identifier."""
    safe = _SAFE_NAME_RE.sub("-", value.strip()).strip("-._").lower()
    # 40 characters keeps filenames readable while the digest provides uniqueness.
    return safe[:40] or "color"


def _loadIconRegistry() -> dict[str, str | Callable[..., str]]:
    """Load base SVG icons from the package resources into the icon registry.

    The registry maps icon ids to either an SVG string (for static assets) or a
    callable factory (for dynamic assets such as the slider thumb).
    """
    registry: dict[str, str | Callable[..., str]] = {"slider-thumb": _buildSliderThumbSvg}
    icons_pkg = resources.files("qtshadcn.resources.icons")
    for entry in icons_pkg.iterdir():
        if not entry.is_file():
            continue
        # ``Traversable`` exposes ``name`` but not ``suffix``/``stem`` in stubs.
        name = Path(entry.name)
        if name.suffix.lower() != ".svg":
            continue
        # ``name.stem`` matches the former ``_SVG_RESOURCES`` keys.
        registry[name.stem] = entry.read_text(encoding="utf-8")
    return registry


_ICON_REGISTRY: dict[str, str | Callable[..., str]] = _loadIconRegistry()
