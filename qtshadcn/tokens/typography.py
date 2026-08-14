"""Static shadcn/Tailwind-inspired typography design tokens."""

from enum import IntEnum, StrEnum


class FontSize(StrEnum):
    """Shadcn/Tailwind text-* size scale; each member is a pixel string usable directly in QSS."""

    XS = "12px"
    SM = "14px"
    BASE = "16px"
    LG = "18px"
    XL = "20px"
    XL2 = "24px"
    XL3 = "30px"
    XL4 = "36px"
    XL5 = "48px"
    XL7 = "72px"

    def __str__(self) -> str:
        """Return the font size as a string for QSS."""
        return str(self.value)


class FontWeight(IntEnum):
    """CSS numeric font-weight scale from Thin (100) to Black (900); members render as integers."""

    THIN = 100
    EXTRA_LIGHT = 200
    LIGHT = 300
    NORMAL = 400
    MEDIUM = 500
    SEMI_BOLD = 600
    BOLD = 700
    EXTRA_BOLD = 800
    BLACK = 900

    def __str__(self) -> str:
        """Return the font weight as a string for QSS."""
        return str(int(self))
