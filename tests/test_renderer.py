"""Tests for the QSS renderer."""

from pathlib import Path

from qtshadcn.app import _build_theme
from qtshadcn.models import ShadcnThemeTokens

TEMPLATE_FILE = str(Path(__file__).resolve().parent.parent / "qtshadcn" / "styles" / "shadcn.jinja")


class TestRenderer:
    """Tests for the QSS renderer."""

    def test_base_widgets_present(self):
        """Test that base widgets are present in the QSS."""
        tokens = _tokens()
        qss = _build_theme(tokens)
        assert "QWidget" in qss
        assert "QPushButton" in qss
        assert "QLineEdit" in qss

    def test_typography_classes_present(self):
        """Test that typography classes are present in the QSS."""
        tokens = _tokens()
        qss = _build_theme(tokens)
        assert '[class~="h1"]' in qss
        assert '[class~="h2"]' in qss
        assert '[class~="p"]' in qss
        assert '[class~="muted"]' in qss

    def test_resolved_values_used(self):
        """Test that resolved values are used in the QSS."""
        tokens = _tokens(primary="rgb(255, 0, 0)")
        qss = _build_theme(tokens)
        assert "rgb(255, 0, 0)" in qss
        assert "QPushButton" in qss

    def test_button_variant_and_size_selectors_present(self):
        """Test that QPushButton semantic properties are rendered."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        assert 'QPushButton[variant="outline"]' in qss
        assert 'QPushButton[variant="destructive"]' in qss
        assert 'QPushButton[size="sm"]' in qss
        assert 'QPushButton[size="icon-lg"]' in qss
        assert 'QPushButton[buttonSize="icon-lg"]' in qss
        assert "min-height: 32px;" in qss

    def test_base_button_focus_preserves_default_variant_style(self):
        """Test that an unvariant button keeps default visual styling on focus."""
        tokens = _tokens()
        qss = _build_theme(tokens)

        assert (
            """QPushButton:focus {
    background-color: #0f172a;
    color: #f8fafc;
    border-color: rgba(15, 23, 42, 0.5);
    outline: none;
}"""
            in qss
        )

    def test_button_shadcn_color_mapping_is_qss_safe(self):
        """Test that web color transforms render to static QSS colors."""
        tokens = _tokens(
            primary="#0f172a",
            primary_foreground="#f8fafc",
            secondary="#f1f5f9",
            foreground="#020617",
            destructive="#ef4444",
            ring="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "rgba(15, 23, 42, 0.8)" in qss
        assert "rgba(15, 23, 42, 0.5)" in qss
        assert "rgba(239, 68, 68, 0.1)" in qss
        assert "rgba(239, 68, 68, 0.2)" in qss
        assert "rgb(229, 233, 238)" in qss
        assert "color-mix" not in qss
        assert "calc(" not in qss
        assert "var(" not in qss

    def test_button_radius_min_mapping_is_static(self):
        """Test that rounded min() equivalents render to static pixels."""
        tokens = _tokens(radius="20px")
        qss = _build_theme(tokens)

        assert "border-radius: 20px;" in qss
        assert "border-radius: 10px;" in qss
        assert "border-radius: 12px;" in qss
        assert "min(" not in qss

    def test_button_radius_selectors_use_static_radius_api(self):
        """Test rendered QPushButton selectors use static rounded values."""
        tokens = _tokens(radius="8px")
        qss = _build_theme(tokens)

        assert (
            """QPushButton {
    background-color: #0f172a;
    color: #f8fafc;
    border: 1px solid transparent;
    outline: none;
    border-radius: 8px;"""
            in qss
        )
        assert (
            """QPushButton[size="xs"],
QPushButton[buttonSize="xs"] {
    border-radius: 6.4px;"""
            in qss
        )
        assert (
            """QPushButton[size="sm"],
QPushButton[buttonSize="sm"] {
    border-radius: 6.4px;"""
            in qss
        )
        assert "var(" not in qss
        assert "calc(" not in qss

    def test_no_material_tokens(self):
        """Test that no material tokens are present in the QSS."""
        tokens = _tokens()
        qss = _build_theme(tokens)
        assert "surface" not in qss
        assert "onSurface" not in qss
        assert "primaryContainer" not in qss

    def test_render_rgba_alpha(self):
        """Test that rgba with alpha is rendered correctly."""
        tokens = _tokens(primary="rgba(255, 0, 0, 0.5)")
        qss = _build_theme(tokens)
        assert "rgba(255, 0, 0, 0.5)" in qss

    def test_template_file_exists(self):
        """Test that the template file exists."""
        assert Path(TEMPLATE_FILE).exists()


def _tokens(**overrides):
    values = {
        "background": "#ffffff",
        "foreground": "#020617",
        "card": "#ffffff",
        "card_foreground": "#020617",
        "popover": "#ffffff",
        "popover_foreground": "#020617",
        "primary": "#0f172a",
        "primary_foreground": "#f8fafc",
        "secondary": "#f1f5f9",
        "secondary_foreground": "#0f172a",
        "muted": "#f1f5f9",
        "muted_foreground": "#64748b",
        "accent": "#f1f5f9",
        "accent_foreground": "#0f172a",
        "destructive": "#ef4444",
        "destructive_foreground": "#f8fafc",
        "border": "#e2e8f0",
        "input": "#e2e8f0",
        "ring": "#0f172a",
        "spacing": "4px",
        "radius": "8px",
        "font_family": "system-ui, sans-serif",
    }
    values.update(overrides)
    return ShadcnThemeTokens(**values)
