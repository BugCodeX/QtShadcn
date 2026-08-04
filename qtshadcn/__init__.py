import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

from .models import ShadcnTheme, ShadcnThemeTokens, ThemeConfig, ThemeMode
from ._parser import ThemeParseError
from .utils import blend_colors


def _resolve_version() -> str:
    """Return the installed package version or a source checkout fallback."""
    try:
        return version("qtshadcn")
    except PackageNotFoundError:
        pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
        try:
            with pyproject_path.open("rb") as pyproject_file:
                pyproject = tomllib.load(pyproject_file)
        except OSError:
            return "0+unknown"
        return str(pyproject.get("project", {}).get("version", "0+unknown"))


__version__ = _resolve_version()


def __getattr__(name: str) -> Any:
    """Lazily resolve Qt-dependent package exports."""
    if name in {"apply_theme", "get_theme"}:
        from .app import apply_theme, get_theme

        return {"apply_theme": apply_theme, "get_theme": get_theme}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Config
    "ThemeConfig",
    "ThemeMode",
    # Models
    "ShadcnTheme",
    "ShadcnThemeTokens",
    # Functions
    "apply_theme",
    "get_theme",
    "blend_colors",
    "__version__",
    # Errors
    "ThemeParseError",
]
