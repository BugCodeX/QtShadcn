"""QtShadcn theme models.

Native XML/JSON-loaded theme tokens. Material models have been removed; the
runtime accepts local QtShadcn XML themes and JSON palettes.
"""

from pydantic import BaseModel, ConfigDict


class ShadcnThemeTokens(BaseModel):
    """Resolved tokens for a single palette (light or dark).

    Extra tokens are ignored so manually authored themes do not fail when they
    contain additional variables.
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
    """Resolved light and dark palettes loaded from one QtShadcn theme document."""

    model_config = ConfigDict(frozen=True)

    light: ShadcnThemeTokens
    dark: ShadcnThemeTokens
