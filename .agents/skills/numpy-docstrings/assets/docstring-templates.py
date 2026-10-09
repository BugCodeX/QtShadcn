"""
Reference templates and examples for NumPy-style docstrings and natural comments.

Provides copy-pasteable patterns for functions, classes, Qt widgets, and
human-readable code comments.
"""

from collections.abc import Generator

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QToolButton

# ============================================================================
# 1. Complex Function / Method Template
# ============================================================================


def resolveIconColor(
    color: QColor | str | None,
    *,
    defaultToken: str = "foreground",
) -> QColor:
    """
    Resolve a flexible color descriptor into a concrete QColor.

    Parameters
    ----------
    color : QColor | str | None
        Hex string, theme token name, explicit QColor, or None to use default.
    defaultToken : str, optional
        Theme token key to use when color is None (default: ``"foreground"``).

    Returns
    -------
    QColor
        Resolved concrete color ready for painting.

    Raises
    ------
    ValueError
        If color string does not match a valid hex format or registered token.

    Examples
    --------
    >>> resolveIconColor("#ff0000")
    <PySide6.QtGui.QColor(...)>
    >>> resolveIconColor(None, defaultToken="primary")
    <PySide6.QtGui.QColor(...)>
    """
    if color is None:
        # Fallback to default theme token when caller doesn't specify an override
        return QColor("#000000")
    if isinstance(color, str):
        if color.startswith("#"):
            return QColor(color)
        raise ValueError(f"Unknown color token or invalid hex: {color}")
    return color


# ============================================================================
# 2. Generator Template (Yields)
# ============================================================================


def batchItems(items: list[str], batchSize: int = 50) -> Generator[list[str], None, None]:
    """
    Split a collection of items into fixed-size chunks for batch processing.

    Parameters
    ----------
    items : list of str
        Source items to partition.
    batchSize : int, optional
        Number of items per batch (default: 50).

    Yields
    ------
    list of str
        Successive slices of items with length up to ``batchSize``.
    """
    for index in range(0, len(items), batchSize):
        yield items[index : index + batchSize]


# ============================================================================
# 3. Class & Qt Widget Template
# ============================================================================


class IconButton(QToolButton):
    """
    Square icon button with theme token binding and proportional scaling.

    Attributes / Properties
    -----------------------
    variant : str
        Visual style variant: "default", "secondary", "ghost", "destructive".
    scale : str
        Size scale controlling square dimensions: "xs", "sm", "default", "lg".
    isPill : bool
        Whether to render as a circular button (50% border radius).

    Examples
    --------
    >>> button = IconButton(variant="ghost", scale="sm")
    >>> button.setText("Close")
    """

    def __init__(self, variant: str = "default", scale: str = "default") -> None:
        super().__init__()
        self.variant = variant
        self.scale = scale
        self.isPill = False

    # 4. Trivial Setter / Property: One-line docstring is preferred
    def setPill(self, enabled: bool) -> None:
        """Enable or disable circular pill rendering mode."""
        self.isPill = enabled
        self.update()


# ============================================================================
# 5. Commenting Style: Natural Human Tone vs Robotic Narration
# ============================================================================


def processThemeAdjustment(alphaValue: float) -> None:
    """Process the theme adjustment value."""
    # ❌ BAD (Obvious narration / filler):
    # This variable stores the clamped alpha value between 0 and 1
    # clamped = max(0.0, min(1.0, alphaValue))

    # ✅ GOOD (Explains the WHY / non-obvious reasoning in natural human voice):
    # Qt crashes if alpha is outside [0.0, 1.0] when applying QSS opacity rules
    clampedAlpha = max(0.0, min(1.0, alphaValue))

    # ❌ BAD:
    # Check if clamped alpha is zero and return
    # if clampedAlpha == 0.0:
    #     return

    # ✅ GOOD:
    # Skip stylesheet recomputation for fully transparent states to avoid render flicker
    if clampedAlpha == 0.0:
        return
