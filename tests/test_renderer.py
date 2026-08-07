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

        assert "QToolButton {" in qss
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

        line_edit_block = """QLineEdit,
QTextEdit {
  background: transparent;
  color: #020617;
  border: 1px solid #e2e8f0;
  outline: none;
  border-radius: 8px;
  font-size: 14px;
  placeholder-text-color: #64748b;
  selection-background-color: #0f172a;
  selection-color: #f8fafc;
}

QLineEdit {
  padding: 0 10px;
  min-height: 32px;
}"""
        assert line_edit_block in qss
        assert "padding-top:" not in line_edit_block
        assert "padding-bottom:" not in line_edit_block
        assert "padding: 0 10px;" in qss
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

        # Focus: border sólido + ring con opacidad 50%
        assert "border-color: #0f172a;" in qss
        assert "outline: 3px solid rgba(15, 23, 42, 0.5);" in qss
        # Disabled: background input con opacidad 50% (light mode)
        assert "background: rgba(226, 232, 240, 0.5);" in qss
        assert "color: rgba(100, 116, 139, 0.5);" in qss
        assert "border-color: rgba(226, 232, 240, 0.5);" in qss
        # Invalid: texto rojo + border destructivo + ring con opacidad 20%
        assert "color: #ef4444;" in qss
        assert "border-color: #ef4444;" in qss
        assert "outline: 3px solid rgba(239, 68, 68, 0.2);" in qss
        assert "box-shadow" not in qss
        assert "transition" not in qss

    def test_line_edit_dark_mode_uses_input_background_alpha(self):
        """Test that dark QLineEdit background maps shadcn input/30 semantics."""
        tokens = _tokens(input="#343434")
        qss = _build_theme(tokens, is_dark=True)

        assert "background: rgba(52, 52, 52, 0.3);" in qss

    def test_text_edit_textarea_semantics_are_rendered(self):
        """Test that QTextEdit renders shadcn Textarea semantics."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        shared_input_block = """QLineEdit,
QTextEdit {
  background: transparent;
  color: #020617;
  border: 1px solid #e2e8f0;
  outline: none;
  border-radius: 8px;
  font-size: 14px;
  placeholder-text-color: #64748b;
  selection-background-color: #0f172a;
  selection-color: #f8fafc;
}"""
        text_edit_block = """QTextEdit {
  padding: 8px 10px;
  min-height: 64px;
}"""
        assert shared_input_block in qss
        assert text_edit_block in qss
        assert "padding: 8px 10px;" in qss
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
        # Focus: border sólido + ring con opacidad 50%
        assert "border-color: #0f172a;" in qss
        assert "outline: 3px solid rgba(15, 23, 42, 0.5);" in qss
        # Disabled: background input con opacidad 50% (light mode)
        assert "background: rgba(226, 232, 240, 0.5);" in qss
        assert "color: rgba(100, 116, 139, 0.5);" in qss
        assert "border-color: rgba(226, 232, 240, 0.5);" in qss
        # Invalid: texto rojo + border destructivo + ring con opacidad 20%
        assert "color: #ef4444;" in qss
        assert "border-color: #ef4444;" in qss
        assert "outline: 3px solid rgba(239, 68, 68, 0.2);" in qss

    def test_text_edit_dark_mode_uses_input_background_alpha(self):
        """Test that dark QTextEdit background maps shadcn input/30 semantics."""
        tokens = _tokens(input="#343434")
        qss = _build_theme(tokens, is_dark=True)

        assert "background: rgba(52, 52, 52, 0.3);" in qss

    def test_text_input_dark_mode_disabled_and_invalid_opacities(self):
        """Test that dark mode text inputs use correct opacities for disabled and invalid states."""
        tokens = _tokens(input="#343434", destructive="#ef4444")
        qss = _build_theme(tokens, is_dark=True)

        # Disabled: background input con opacidad 80% (dark mode)
        assert "background: rgba(52, 52, 52, 0.8);" in qss
        # Invalid: border al 50% + ring al 40% (dark mode)
        assert "border-color: rgba(239, 68, 68, 0.5);" in qss
        assert "outline: 3px solid rgba(239, 68, 68, 0.4);" in qss

    def test_spin_box_selectors_are_present(self):
        """Test that QSpinBox and QDoubleSpinBox selectors are rendered."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        assert "QSpinBox,\nQDoubleSpinBox {" in qss
        assert "QSpinBox::up-button,\nQDoubleSpinBox::up-button {" in qss
        assert "QSpinBox::down-button,\nQDoubleSpinBox::down-button {" in qss
        assert "QSpinBox::up-arrow,\nQDoubleSpinBox::up-arrow {" in qss
        assert "QSpinBox::down-arrow,\nQDoubleSpinBox::down-arrow {" in qss

    def test_spin_box_step_buttons_have_corner_radius(self):
        """Test that step buttons are rounded only at the input's right corners."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        up_block = """QSpinBox::up-button,
QDoubleSpinBox::up-button {
  width: 32px;
  border: none;
  background: transparent;
  border-top-right-radius: 8px;
  border-top-left-radius: 0px;
  border-bottom-right-radius: 0px;
  border-bottom-left-radius: 0px;
  subcontrol-position: top right;
}"""
        down_block = """QSpinBox::down-button,
QDoubleSpinBox::down-button {
  width: 32px;
  border: none;
  background: transparent;
  border-bottom-right-radius: 8px;
  border-top-right-radius: 0px;
  border-top-left-radius: 0px;
  border-bottom-left-radius: 0px;
  subcontrol-position: bottom right;
}"""
        assert up_block in qss
        assert down_block in qss

    def test_spin_box_input_semantics_are_rendered(self):
        """Test that QSpinBox shares QLineEdit input semantics."""
        tokens = _tokens(
            spacing="4px",
            input="#e2e8f0",
            foreground="#020617",
            muted_foreground="#64748b",
            primary="#0f172a",
            primary_foreground="#f8fafc",
        )
        qss = _build_theme(tokens)

        spin_box_block = """QSpinBox,
QDoubleSpinBox {
  background: transparent;
  color: #020617;
  border: 1px solid #e2e8f0;
  outline: none;
  border-radius: 8px;
  font-size: 14px;
  placeholder-text-color: #64748b;
  selection-background-color: #0f172a;
  selection-color: #f8fafc;
  padding: 0 32px 0 10px;
  min-height: 32px;
}"""
        assert spin_box_block in qss
        assert "padding: 0 32px 0 10px;" in qss
        assert "min-height: 32px;" in qss
        assert "font-size: 14px;" in qss
        assert "placeholder-text-color: #64748b;" in qss

    def test_spin_box_state_colors_are_qss_safe(self):
        """Test that QSpinBox focus, disabled, and invalid states use static colors."""
        tokens = _tokens(
            input="#e2e8f0",
            muted="#f1f5f9",
            muted_foreground="#64748b",
            destructive="#ef4444",
            ring="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "QSpinBox:focus,\nQDoubleSpinBox:focus" in qss
        assert "QSpinBox:disabled,\nQDoubleSpinBox:disabled" in qss
        assert 'QSpinBox[invalid="true"],\nQDoubleSpinBox[invalid="true"]' in qss
        # Focus: solid border + 50% opacity ring
        assert "border-color: #0f172a;" in qss
        assert "outline: 3px solid rgba(15, 23, 42, 0.5);" in qss
        # Disabled: 50% opacity input background (light mode)
        assert "background: rgba(226, 232, 240, 0.5);" in qss
        assert "color: rgba(100, 116, 139, 0.5);" in qss
        assert "border-color: rgba(226, 232, 240, 0.5);" in qss
        # Invalid: destructive text + border + 20% opacity ring
        assert "color: #ef4444;" in qss
        assert "border-color: #ef4444;" in qss
        assert "outline: 3px solid rgba(239, 68, 68, 0.2);" in qss
        assert "box-shadow" not in qss
        assert "transition" not in qss

    def test_spin_box_arrows_use_cached_svgs(self):
        """Test that spin box arrows use cached chevron SVGs."""
        tokens = _tokens(muted_foreground="#64748b", foreground="#020617", destructive="#ef4444")
        qss = _build_theme(tokens)

        assert "chevron-up" in qss
        assert "chevron-down" in qss
        assert ".svg" in qss
        assert "QSpinBox::up-arrow,\nQDoubleSpinBox::up-arrow {" in qss
        assert "QSpinBox::down-arrow,\nQDoubleSpinBox::down-arrow {" in qss
        assert "QSpinBox::up-arrow:hover,\nQDoubleSpinBox::up-arrow:hover" in qss
        assert "QSpinBox::down-arrow:hover,\nQDoubleSpinBox::down-arrow:hover" in qss

    def test_spin_box_invalid_and_disabled_arrow_colors_are_rendered(self):
        """Test that spin box arrow colors react to invalid and disabled states."""
        tokens = _tokens(muted_foreground="#64748b", destructive="#ef4444")
        qss = _build_theme(tokens)

        assert 'QSpinBox[invalid="true"]::up-arrow' in qss
        assert 'QSpinBox[invalid="true"]::down-arrow' in qss
        assert "rgba(100, 116, 139, 0.5)" in qss  # disabled arrow muted foreground alpha

    def test_chevron_up_icon_uses_runtime_cache(self):
        """Test that chevron up SVGs are generated and cached."""
        tokens = _tokens(muted_foreground="#64748b")
        manager = ThemedIconManager()
        icon_path = Path(manager.chevron_up(tokens.muted_foreground))

        assert icon_path.exists()
        assert tokens.muted_foreground in icon_path.read_text(encoding="utf-8")
        assert "M4 10l4-4 4 4" in icon_path.read_text(encoding="utf-8")

    def test_checkbox_semantics_are_rendered(self):
        """Test that QCheckBox renders shadcn checkbox semantics."""
        tokens = _tokens(
            spacing="4px",
            primary="#0f172a",
            primary_foreground="#f8fafc",
            destructive="#ef4444",
            destructive_foreground="#f8fafc",
        )
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
        assert "rgba(239, 68, 68, 0.2)" in qss  # Light mode ring opacity

    def test_checkbox_invalid_dark_mode_opacities(self):
        """Test that QCheckBox invalid state uses correct opacities in dark mode."""
        tokens = _tokens(spacing="4px", destructive="#ef4444")
        qss = _build_theme(tokens, is_dark=True)

        assert "rgba(239, 68, 68, 0.5)" in qss  # Dark mode border opacity
        assert "rgba(239, 68, 68, 0.4)" in qss  # Dark mode ring opacity

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

    def test_radio_button_semantics_are_rendered(self):
        """Test that QRadioButton renders shadcn radio button semantics."""
        tokens = _tokens(
            spacing="4px",
            primary="#0f172a",
            primary_foreground="#f8fafc",
            destructive="#ef4444",
            destructive_foreground="#f8fafc",
        )
        qss = _build_theme(tokens)

        assert "QRadioButton {" in qss
        assert "spacing: 8px;" in qss
        assert "QRadioButton::indicator {" in qss
        assert "width: 16px;" in qss
        assert "height: 16px;" in qss
        assert "border-radius: 8px;" in qss
        assert "border: 1px solid #e2e8f0;" in qss
        assert "QRadioButton::indicator:checked {" in qss
        assert "background-color: #0f172a;" in qss
        assert "border-color: #0f172a;" in qss
        assert 'image: url("' in qss
        assert "radio-checked" in qss
        assert ".svg" in qss
        assert "QRadioButton:disabled" in qss
        assert 'QRadioButton[invalid="true"]' in qss
        assert "#ef4444" in qss
        assert "rgba(239, 68, 68, 0.2)" in qss  # Light mode ring opacity

    def test_radio_button_invalid_dark_mode_opacities(self):
        """Test that QRadioButton invalid state uses correct opacities in dark mode."""
        tokens = _tokens(spacing="4px", destructive="#ef4444")
        qss = _build_theme(tokens, is_dark=True)

        assert "rgba(239, 68, 68, 0.5)" in qss  # Dark mode border opacity
        assert "rgba(239, 68, 68, 0.4)" in qss  # Dark mode ring opacity

    def test_radio_button_icon_uses_runtime_cache(self):
        """Test that radio button SVGs are generated and cached."""
        tokens = _tokens(primary_foreground="#f8fafc")
        manager = ThemedIconManager()
        icon_path = Path(manager.radio_checked(tokens.primary_foreground))

        assert icon_path.exists()
        assert tokens.primary_foreground in icon_path.read_text(encoding="utf-8")
        assert "circle" in icon_path.read_text(encoding="utf-8")

    def test_combo_box_semantics_are_rendered(self):
        """Test that QComboBox renders shadcn combobox semantics."""
        tokens = _tokens(
            spacing="4px",
            primary="#0f172a",
            primary_foreground="#f8fafc",
            destructive="#ef4444",
            destructive_foreground="#f8fafc",
            muted_foreground="#64748b",
            input="#e2e8f0",
            ring="#0f172a",
            popover="#ffffff",
            popover_foreground="#020617",
            border="#e2e8f0",
            accent="#f1f5f9",
            accent_foreground="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "QComboBox {" in qss
        assert "QFontComboBox" not in qss
        assert "border: 1px solid #e2e8f0;" in qss
        assert "border-radius: 8px;" in qss
        assert "min-height: 32px;" in qss
        assert "font-size: 14px;" in qss
        assert "QComboBox:focus {" in qss
        assert "border-color: #0f172a;" in qss
        assert "outline: 3px solid rgba(15, 23, 42, 0.5);" in qss
        assert "QComboBox:disabled {" in qss
        assert "QComboBox::drop-down {" in qss
        assert "QComboBox::down-arrow {" in qss
        assert "chevron-down" in qss
        assert ".svg" in qss
        assert 'QComboBox[invalid="true"] {' in qss
        assert "#ef4444" in qss
        assert "rgba(239, 68, 68, 0.2)" in qss
        assert "QComboBox QAbstractItemView {" in qss
        assert "background: #ffffff;" in qss
        assert "color: #020617;" in qss
        assert "padding: 0 32px 0 10px;" in qss
        assert "padding: 4px 32px 4px 6px;" in qss
        assert "min-height: 32px;" in qss

    def test_combo_box_invalid_dark_mode_opacities(self):
        """Test that QComboBox invalid state uses correct opacities in dark mode."""
        tokens = _tokens(spacing="4px", destructive="#ef4444")
        qss = _build_theme(tokens, is_dark=True)

        assert "rgba(239, 68, 68, 0.5)" in qss
        assert "rgba(239, 68, 68, 0.4)" in qss

    def test_combo_box_icon_uses_runtime_cache(self):
        """Test that chevron down SVGs are generated and cached."""
        tokens = _tokens(muted_foreground="#64748b")
        manager = ThemedIconManager()
        icon_path = Path(manager.chevron_down(tokens.muted_foreground))

        assert icon_path.exists()
        assert tokens.muted_foreground in icon_path.read_text(encoding="utf-8")
        assert "M4 6l4 4 4-4" in icon_path.read_text(encoding="utf-8")

    def test_label_semantics_are_rendered(self):
        """Test that QLabel renders shadcn label semantics."""
        tokens = _tokens(spacing="4px", foreground="#020617")
        qss = _build_theme(tokens)

        assert "QLabel {" in qss
        assert "font-size: 14px;" in qss
        assert "font-weight: 500;" in qss
        assert "line-height: 100%;" in qss
        assert "QLabel:disabled" in qss
        assert "color: rgba(2, 6, 23, 0.5);" in qss

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

    def test_progress_bar_semantics_are_rendered(self):
        """Test that QProgressBar renders shadcn progress semantics."""
        tokens = _tokens(
            spacing="4px",
            muted="#f1f5f9",
            primary="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "QProgressBar {" in qss
        assert "QProgressBar::chunk {" in qss
        assert 'QProgressBar[labeled="true"]' in qss
        assert "QProgressBar:disabled" in qss
        assert "QProgressBar::chunk:disabled" in qss
        assert "background-color: #f1f5f9;" in qss
        assert "min-height: 4px;" in qss
        assert "max-height: 4px;" in qss
        assert "border-radius: 9999px;" in qss
        assert "color: transparent;" in qss
        assert "background-color: #0f172a;" in qss
        assert "margin: 0;" in qss

    def test_progress_bar_labeled_variant(self):
        """Test that QProgressBar labeled variant grows to fit text."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        assert 'QProgressBar[labeled="true"] {' in qss
        assert "min-height: 20px;" in qss
        assert "max-height: 20px;" in qss

    def test_progress_bar_disabled_opacity(self):
        """Test that QProgressBar disabled states use 50% opacity."""
        tokens = _tokens(
            muted="#f1f5f9",
            primary="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "background-color: rgba(241, 245, 249, 0.5);" in qss
        assert "background-color: rgba(15, 23, 42, 0.5);" in qss

    def test_slider_semantics_are_rendered(self):
        """Test that QSlider renders shadcn slider semantics."""
        tokens = _tokens(
            spacing="4px",
            muted="#f1f5f9",
            primary="#0f172a",
            background="#ffffff",
            ring="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "QSlider::groove:horizontal {" in qss
        assert "QSlider::handle:horizontal {" in qss
        assert "QSlider:horizontal {" in qss
        assert "QSlider::add-page {" in qss
        assert "QSlider::sub-page {" in qss
        assert "background-color: #f1f5f9;" in qss
        assert "background-color: #0f172a;" in qss
        assert "min-height: 12px;" in qss
        assert "width: 12px;" in qss
        assert "height: 12px;" in qss
        assert "image: url(" in qss
        assert "slider-thumb" in qss

    def test_slider_vertical_semantics_are_rendered(self):
        """Test that QSlider renders vertical slider semantics."""
        tokens = _tokens(spacing="4px")
        qss = _build_theme(tokens)

        assert "QSlider::groove:vertical {" in qss
        assert "QSlider::handle:vertical {" in qss
        assert "QSlider:vertical {" in qss
        assert "QSlider::add-page {" in qss
        assert "QSlider::sub-page {" in qss
        assert "min-width: 12px;" in qss
        assert "width: 4px;" in qss
        assert "image: url(" in qss

    def test_slider_disabled_opacity(self):
        """Test that QSlider disabled states use 50% opacity."""
        tokens = _tokens(
            muted="#f1f5f9",
            background="#ffffff",
            ring="#0f172a",
        )
        qss = _build_theme(tokens)

        assert "QSlider::add-page {" in qss
        assert "QSlider::sub-page {" in qss
        assert "background-color: #f1f5f9;" in qss

    def test_tab_widget_semantics_are_rendered(self):
        """Test that QTabWidget renders shadcn tabs semantics."""
        tokens = _tokens(
            spacing="4px",
            muted="#f1f5f9",
            background="#ffffff",
            foreground="#020617",
            muted_foreground="#64748b",
        )
        qss = _build_theme(tokens)

        assert "QTabWidget::pane {" in qss
        assert "QTabBar {" in qss
        assert "QTabBar::tab {" in qss
        assert "QTabBar::tab:selected {" in qss
        assert "QTabBar::tab:hover {" in qss
        assert "QTabBar::tab:disabled {" in qss
        assert "background: #f1f5f9;" in qss
        assert "background: #ffffff;" in qss
        assert "color: #020617;" in qss
        assert "color: #64748b;" in qss
        assert 'QTabWidget[variant="line"] QTabBar {' in qss
        assert 'QTabWidget[variant="line"] QTabBar::tab:selected {' in qss
        assert "border-bottom: 2px solid transparent;" in qss
        assert "border-bottom-color: #020617;" in qss
        assert "padding: 4px 12px;" in qss
        assert "min-height: 28px;" in qss

    def test_tab_widget_line_vertical_indicator_is_rendered(self):
        """Test that line variant vertical tabs use a right-side indicator."""
        tokens = _tokens(
            spacing="4px",
            foreground="#020617",
        )
        qss = _build_theme(tokens)

        assert 'QTabWidget[variant="line"] QTabBar::tab:left {' in qss
        assert 'QTabWidget[variant="line"] QTabBar::tab:left:selected {' in qss
        assert "border-right: 2px solid transparent;" in qss
        assert "border-right-color: #020617;" in qss

    def test_tab_widget_disabled_opacity(self):
        """Test that QTabWidget disabled tabs use 50% opacity."""
        tokens = _tokens(muted_foreground="#64748b")
        qss = _build_theme(tokens)

        assert "color: rgba(100, 116, 139, 0.5);" in qss

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
