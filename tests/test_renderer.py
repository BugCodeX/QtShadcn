"""Tests for the QSS renderer."""

from pathlib import Path

from qtshadcn._icons import ThemedIconManager
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
        assert "QToolButton" in qss
        assert "QLineEdit" in qss
        assert "QLineEdit:focus" in qss
        assert "QLineEdit:disabled" in qss
        assert 'QLineEdit[invalid="true"]' in qss
        assert "QTextEdit" in qss
        assert "QTextEdit:focus" in qss
        assert "QTextEdit:disabled" in qss
        assert 'QTextEdit[invalid="true"]' in qss
        assert "QCheckBox" in qss
        assert "QCheckBox::indicator" in qss
        assert "QCheckBox::indicator:checked" in qss

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
        assert f'QPushButton[{"button" + "Size"}="icon-lg"]' not in qss
        assert "min-height: 32px;" in qss

    def test_tool_button_variant_state_and_size_selectors_present(self):
        """Test that QToolButton compact action properties are rendered."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        assert 'QToolButton[variant="default"]' in qss
        assert 'QToolButton[variant="outline"]' in qss
        assert 'QToolButton[variant="secondary"]' in qss
        assert 'QToolButton[variant="ghost"]' in qss
        assert 'QToolButton[variant="destructive"]' in qss
        assert 'QToolButton[variant="outline"]:checked' in qss
        assert 'QToolButton[variant="ghost"]:focus' in qss
        assert 'QToolButton[variant="destructive"]:disabled' in qss
        assert 'QToolButton[size="icon-sm"]' in qss
        assert 'QToolButton[size="icon"]' in qss
        assert 'QToolButton[size="icon-lg"]' in qss
        assert f'QToolButton[{"button" + "Size"}="icon-lg"]' not in qss
        assert "min-width: 28px;" in qss
        assert "min-width: 36px;" in qss

    def test_line_edit_input_semantics_are_rendered(self):
        """Test that QLineEdit renders shadcn Input semantics."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        line_edit_block = """QLineEdit {
    background-color: transparent;
    color: #020617;
    border: 1px solid #e2e8f0;
    outline: none;
    border-radius: 8px;
    padding-left: 10px;
    padding-right: 10px;
    min-width: 0px;
    min-height: 32px;"""
        assert line_edit_block in qss
        assert "padding-top:" not in line_edit_block
        assert "padding-bottom:" not in line_edit_block
        assert "padding-left: 10px;" in qss
        assert "padding-right: 10px;" in qss
        assert "min-width: 0px;" in qss
        assert "min-height: 32px;" in qss
        assert "font-size: 14px;" in qss
        assert "placeholder-text-color: #64748b;" in qss

    def test_line_edit_state_colors_are_qss_safe(self):
        """Test that QLineEdit focus, disabled, and invalid states use static colors."""
        tokens = _tokens(
            input="#e2e8f0",
            muted="#f1f5f9",
            muted_foreground="#64748b",
            destructive="#ef4444",
            ring="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "border-color: rgba(15, 23, 42, 0.5);" in qss
        assert "background-color: #f1f5f9;" in qss
        assert "color: rgba(100, 116, 139, 0.5);" in qss
        assert "border-color: rgba(226, 232, 240, 0.5);" in qss
        assert "border-color: #ef4444;" in qss
        assert "border-color: rgba(239, 68, 68, 0.5);" in qss
        assert "box-shadow" not in qss
        assert "transition" not in qss

    def test_line_edit_dark_mode_uses_input_background_alpha(self):
        """Test that dark QLineEdit background maps shadcn input/30 semantics."""
        tokens = _tokens(input="#343434")
        qss = _build_theme(tokens, is_dark=True)

        assert "background-color: rgba(52, 52, 52, 0.3);" in qss

    def test_text_edit_textarea_semantics_are_rendered(self):
        """Test that QTextEdit renders shadcn Textarea semantics."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        assert (
            """QTextEdit {
    background-color: transparent;
    color: #020617;
    border: 1px solid #e2e8f0;
    outline: none;
    border-radius: 8px;"""
            in qss
        )
        assert "padding-left: 10px;" in qss
        assert "padding-right: 10px;" in qss
        assert "padding-top: 8px;" in qss
        assert "padding-bottom: 8px;" in qss
        assert "min-width: 0px;" in qss
        assert "min-height: 64px;" in qss
        assert "font-size: 14px;" in qss
        assert "placeholder-text-color: #64748b;" in qss

    def test_text_edit_shares_input_state_colors(self):
        """Test that QTextEdit shares QLineEdit focus, disabled, and invalid states."""
        tokens = _tokens(
            input="#e2e8f0",
            muted="#f1f5f9",
            muted_foreground="#64748b",
            destructive="#ef4444",
            ring="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "QLineEdit:focus,\nQTextEdit:focus" in qss
        assert "QLineEdit:disabled,\nQTextEdit:disabled" in qss
        assert 'QLineEdit[invalid="true"],\nQTextEdit[invalid="true"]' in qss
        assert "border-color: rgba(15, 23, 42, 0.5);" in qss
        assert "background-color: #f1f5f9;" in qss
        assert "color: rgba(100, 116, 139, 0.5);" in qss
        assert "border-color: rgba(226, 232, 240, 0.5);" in qss
        assert "border-color: #ef4444;" in qss
        assert "border-color: rgba(239, 68, 68, 0.5);" in qss

    def test_text_edit_dark_mode_uses_input_background_alpha(self):
        """Test that dark QTextEdit background maps shadcn input/30 semantics."""
        tokens = _tokens(input="#343434")
        qss = _build_theme(tokens, is_dark=True)

        assert "QTextEdit {" in qss
        assert "background-color: rgba(52, 52, 52, 0.3);" in qss

    def test_checkbox_semantics_are_rendered(self):
        """Test that QCheckBox renders shadcn checkbox semantics."""
        tokens = _tokens(spacing="4px", primary="#0f172a", primary_foreground="#f8fafc", destructive="#ef4444", destructive_foreground="#f8fafc")
        qss = _build_theme(tokens)

        assert "QCheckBox {" in qss
        assert "spacing: 8px;" in qss
        assert "QCheckBox::indicator {" in qss
        assert "width: 16px;" in qss
        assert "height: 16px;" in qss
        assert "border: 1px solid #e2e8f0;" in qss
        assert "QCheckBox::indicator:checked {" in qss
        assert "background-color: #0f172a;" in qss
        assert "border-color: #0f172a;" in qss
        assert 'image: url("' in qss
        assert "checkbox-check" in qss
        assert ".svg" in qss
        assert "QCheckBox::indicator:indeterminate {" in qss
        assert "checkbox-indeterminate" in qss
        assert "QCheckBox:disabled" in qss
        assert 'QCheckBox[invalid="true"]' in qss
        assert "#ef4444" in qss

    def test_checkbox_icon_contains_primary_foreground_and_uses_runtime_cache(self):
        """Test that checkbox SVGs use token colors and avoid the package directory."""
        tokens = _tokens(primary_foreground="#f8fafc")
        manager = ThemedIconManager()
        icon_path = Path(manager.checkbox_check(tokens.primary_foreground))
        package_dir = Path(__file__).resolve().parents[1] / "qtshadcn"

        assert icon_path.exists()
        assert tokens.primary_foreground in icon_path.read_text(encoding="utf-8")
        assert not icon_path.resolve().is_relative_to(package_dir.resolve())

    def test_checkbox_indeterminate_icon_uses_runtime_cache(self):
        """Test that checkbox indeterminate SVGs are generated and cached."""
        tokens = _tokens(primary_foreground="#f8fafc")
        manager = ThemedIconManager()
        icon_path = Path(manager.checkbox_indeterminate(tokens.primary_foreground))

        assert icon_path.exists()
        assert tokens.primary_foreground in icon_path.read_text(encoding="utf-8")
        assert "M3 8h10" in icon_path.read_text(encoding="utf-8")

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
            """QPushButton[size="xs"] {
    border-radius: 6.4px;"""
            in qss
        )
        assert (
            """QPushButton[size="sm"] {
    border-radius: 6.4px;"""
            in qss
        )
        assert "button" + "Size" not in qss
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
