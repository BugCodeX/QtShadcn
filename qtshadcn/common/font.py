"""QtShadcn font registry and public font API.

This module decouples font registration from stylesheet rendering so that
bundled fonts are registered once per family and theme switches stay fast.
"""

from __future__ import annotations

import logging
from importlib import resources
from pathlib import Path

from qtpy import QtGui

from .config import qsettings

logger = logging.getLogger(__name__)

_FONT_EXTENSIONS = {".ttf", ".otf"}

# Bundled font directories do not always match the declared family name
# (e.g. ``opensans`` contains the ``Open Sans`` family). Keep this map in
# sync when adding new bundled font directories.
_BUNDLED_FAMILY_NAMES: dict[str, str] = {
    "Inter": "Inter",
    "opensans": "Open Sans",
    "roboto": "Roboto",
}

_fontRegistry: dict[str, list[Path]] = {}
_registeredFamilies: set[str] = set()


def _buildBundledFontRegistry() -> dict[str, list[Path]]:
    """Scan bundled font directories and map them to canonical family names."""
    registry: dict[str, list[Path]] = {}
    try:
        fonts_pkg = resources.files("qtshadcn.resources.fonts")
    except Exception:
        logger.warning("Could not locate bundled font package")
        return registry

    if not fonts_pkg.is_dir():
        return registry

    for entry in fonts_pkg.iterdir():
        if not entry.is_dir():
            continue

        family = _BUNDLED_FAMILY_NAMES.get(entry.name, entry.name)
        paths: list[Path] = []
        for font_file in entry.iterdir():
            if not font_file.is_file():
                continue

            suffix = Path(font_file.name).suffix.lower()
            if suffix not in _FONT_EXTENSIONS:
                continue

            # QFontDatabase needs a real filesystem path; ``as_file`` extracts
            # package resources to a temporary file when the package is zipped.
            with resources.as_file(font_file) as font_path:
                paths.append(Path(font_path))

        if paths:
            registry.setdefault(family, []).extend(paths)

    return registry


_fontRegistry = _buildBundledFontRegistry()


def setFontFamily(family: str | None, *, save: bool = True) -> None:
    """Set a single font family and re-render the stylesheet."""
    setFontFamilies([family] if family else [], save=save)


def setFontFamilies(families: list[str], *, save: bool = True) -> None:
    """Set the active font families and re-render the stylesheet.

    The list is stored in ``qsettings.font_family``. Persistence and the
    re-render are skipped independently when requested.
    """
    qsettings.font_family.set(families)
    if save:
        qsettings.save(only={"font_family"})

    # Import is deferred to avoid an import cycle: ``stylesheet`` imports this
    # module, and this module only needs the renderer on explicit user action.
    from .stylesheet import _render_and_apply

    _render_and_apply()


def getFontFamilies() -> list[str]:
    """Return the active font family list, falling back to theme tokens."""
    stored = qsettings.font_family.value
    if stored:
        if isinstance(stored, list):
            return stored
        if isinstance(stored, str):
            return [stored]

    # Deferred import avoids the cycle described in ``setFontFamilies``.
    from .stylesheet import _active_theme, isDarkTheme

    theme = _active_theme()
    tokens = theme.dark if isDarkTheme() else theme.light
    return [tokens.font_family]


def getFontFamily() -> str:
    """Return the primary active font family or an empty string."""
    families = getFontFamilies()
    return families[0] if families else ""


def registerFontFamily(family: str, source: str | Path) -> None:
    """Register a custom font family from a file or directory.

    The fonts are only queued for registration; ``_ensureFontFamilyRegistered``
    performs the actual ``QFontDatabase`` call the first time the family is used.
    """
    source_path = Path(source)
    if source_path.is_dir():
        for font_file in source_path.iterdir():
            if not font_file.is_file():
                continue
            if font_file.suffix.lower() not in _FONT_EXTENSIONS:
                continue
            _fontRegistry.setdefault(family, []).append(font_file.resolve())
    elif source_path.is_file() and source_path.suffix.lower() in _FONT_EXTENSIONS:
        _fontRegistry.setdefault(family, []).append(source_path.resolve())
    else:
        logger.warning("Invalid font source for %s: %s", family, source)


def _ensureFontFamilyRegistered(family: str) -> bool:
    """Register every font file mapped to ``family`` if not registered already.

    Returns ``True`` when the family is known and at least one font file was
    accepted by ``QFontDatabase``.
    """
    if family in _registeredFamilies:
        return True

    paths = _fontRegistry.get(family)
    if not paths:
        return False

    success = False
    for path in paths:
        try:
            font_id = QtGui.QFontDatabase.addApplicationFont(str(path))
        except Exception as e:
            logger.warning("Could not register font %s: %s", path, e)
            continue

        if font_id != -1:
            success = True
        else:
            logger.warning("QFontDatabase rejected font: %s", path)

    if success:
        _registeredFamilies.add(family)

    return success
