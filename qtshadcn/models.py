"""QtShadcn theme models.

Native XML-loaded theme tokens. Material models have been removed; the core
runtime only accepts local QtShadcn XML theme files.
"""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class ThemeMode(StrEnum):
    """Theme mode selection."""

    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class ThemeConfig(BaseModel):
    """Internal theme configuration used for cache keys and persistence.

    The public :func:`~qtshadcn.app.apply_theme` signature exposes these values
    as keyword arguments. This frozen model is kept internal so the cache can be
    keyed by every input that affects the rendered stylesheet.
    """

    model_config = ConfigDict(frozen=True, use_enum_values=True)

    theme_mode: ThemeMode = ThemeMode.AUTO
    theme_file: str | None = None
    custom_tokens: dict[str, dict[str, str] | str] | None = None
    additional_qss: str | None = None
    default_theme: str = "dark"


class ShadcnThemeTokens(BaseModel):
    """Resolved tokens for a single XML palette (light or dark).

    Extra XML tokens are ignored so manually authored themes do not fail when
    they contain additional variables.
    """

    model_config = ConfigDict(extra="ignore", frozen=True)

    background: str
    foreground: str
    card: str
    card_foreground: str
    popover: str
    popover_foreground: str
    primary: str
    primary_foreground: str
    secondary: str
    secondary_foreground: str
    muted: str
    muted_foreground: str
    accent: str
    accent_foreground: str
    destructive: str
    destructive_foreground: str
    border: str
    input: str
    ring: str
    spacing: str
    radius: str
    font_family: str


class ShadcnTheme(BaseModel):
    """Resolved light and dark palettes loaded from one QtShadcn XML document."""

    model_config = ConfigDict(frozen=True)

    light: ShadcnThemeTokens
    dark: ShadcnThemeTokens
