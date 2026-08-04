"""QtShadcn color utilities."""


def blend_colors(base_hex: str, overlay_hex: str, opacity: float) -> str:
    """Blend an overlay color over a base color with a given opacity.

    Uses the Porter-Duff over-a-solid-background formula.
    Returns the resulting color as a lowercase ``#rrggbb`` hex string.
    """
    if not base_hex or not overlay_hex:
        return base_hex

    base = base_hex.lstrip("#")
    overlay = overlay_hex.lstrip("#")

    # Strip leading alpha byte from 8-char ARGB hex (e.g. "#ff0f172a" → "0f172a")
    if len(base) == 8:
        base = base[2:]
    if len(overlay) == 8:
        overlay = overlay[2:]

    if len(base) != 6 or len(overlay) != 6:
        return base_hex

    r1, g1, b1 = int(base[0:2], 16), int(base[2:4], 16), int(base[4:6], 16)
    r2, g2, b2 = int(overlay[0:2], 16), int(overlay[2:4], 16), int(overlay[4:6], 16)

    # Alpha compositing over a solid background
    r = int((r2 * opacity) + (r1 * (1 - opacity)))
    g = int((g2 * opacity) + (g1 * (1 - opacity)))
    b = int((b2 * opacity) + (b1 * (1 - opacity)))

    # Clamp to 0-255
    r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

    return f"#{r:02x}{g:02x}{b:02x}"
