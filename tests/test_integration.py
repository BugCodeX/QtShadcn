"""Integration tests for the QtShadcn theme pipeline."""

import sys
from pathlib import Path

import pytest
from qtshadcn._qt import QtWidgets
from qtshadcn.app import _build_theme, apply_theme
from qtshadcn.models import ShadcnThemeTokens, ThemeConfig

FULL_THEME = """\
<theme>
  <light>
    <background>#ffffff</background>
    <foreground>#020617</foreground>
    <card>#ffffff</card>
    <card_foreground>#020617</card_foreground>
    <popover>#ffffff</popover>
    <popover_foreground>#020617</popover_foreground>
    <primary>oklch(0.21 0.006 285.885)</primary>
    <primary_foreground>#f8fafc</primary_foreground>
    <secondary>oklch(0.967 0.001 286.375)</secondary>
    <secondary_foreground>#0f172a</secondary_foreground>
    <muted>oklch(0.967 0.001 286.375)</muted>
    <muted_foreground>oklch(0.552 0.016 285.938)</muted_foreground>
    <accent>oklch(0.967 0.001 286.375)</accent>
    <accent_foreground>#0f172a</accent_foreground>
    <destructive>oklch(0.577 0.245 27.325)</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>oklch(0.92 0.004 286.32)</border>
    <input>oklch(0.92 0.004 286.32)</input>
    <ring>oklch(0.705 0.015 286.067)</ring>
    <spacing>0.25rem</spacing>
    <radius>0.5rem</radius>
    <font_family>system-ui, sans-serif</font_family>
  </light>
  <dark>
    <background>#020617</background>
    <foreground>#f8fafc</foreground>
    <card>#020617</card>
    <card_foreground>#f8fafc</card_foreground>
    <popover>#020617</popover>
    <popover_foreground>#f8fafc</popover_foreground>
    <primary>oklch(0.985 0 0)</primary>
    <primary_foreground>#0f172a</primary_foreground>
    <secondary>oklch(0.274 0.006 286.033)</secondary>
    <secondary_foreground>#f8fafc</secondary_foreground>
    <muted>oklch(0.274 0.006 286.033)</muted>
    <muted_foreground>oklch(0.705 0.015 286.067)</muted_foreground>
    <accent>oklch(0.274 0.006 286.033)</accent>
    <accent_foreground>#f8fafc</accent_foreground>
    <destructive>oklch(0.396 0.141 25.723)</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>oklch(0.274 0.006 286.033)</border>
    <input>oklch(0.274 0.006 286.033)</input>
    <ring>oklch(0.442 0.017 285.786)</ring>
    <spacing>0.25rem</spacing>
    <radius>0.5rem</radius>
    <font_family>system-ui, sans-serif</font_family>
  </dark>
</theme>
"""


@pytest.fixture
def full_theme_path(tmp_path: Path) -> Path:
    """Return a path to a temporary theme.xml file."""
    path = tmp_path / "theme.xml"
    path.write_text(FULL_THEME, encoding="utf-8")
    return path


class TestIntegration:
    """Tests for the integration of the QtShadcn theme pipeline."""

    def test_full_pipeline(self, qapp: QtWidgets.QApplication, full_theme_path: Path):
        """Test the full theme application pipeline."""
        config = ThemeConfig(theme_source_path=str(full_theme_path), theme_mode="light")
        tokens = apply_theme(qapp, config)
        assert isinstance(tokens, ShadcnThemeTokens)
        assert tokens.background == "#ffffff"
        assert "rgb(" in tokens.primary
        assert "px" in tokens.radius
        assert tokens.spacing == "4px"
        assert qapp.styleSheet() != ""

    def test_qss_output_is_qt_safe(self, qapp: QtWidgets.QApplication, full_theme_path: Path):
        """Test that the QSS output is safe for Qt."""
        config = ThemeConfig(theme_source_path=str(full_theme_path), theme_mode="light")
        tokens = apply_theme(qapp, config)
        qss = _build_theme(tokens)
        assert "oklch(" not in qss
        assert "rem" not in qss
        assert "rgba(" in qss or "rgb(" in qss

    def test_material_imports_absent(self):
        """Material modules must not be importable after migration."""
        with pytest.raises(ImportError):
            import qtshadcn.generator  # noqa: F401  # ty:ignore[unresolved-import]

        with pytest.raises(ImportError):
            from qtshadcn.tokens import MD3Elevation  # noqa: F401  # ty:ignore[unresolved-import]

        with pytest.raises(ImportError):
            from qtshadcn.models import MaterialScheme  # noqa: F401  # ty:ignore[unresolved-import]

    def test_no_materialyoucolor_import(self):
        """The materialyoucolor package must not be imported by the core path."""
        assert "materialyoucolor" not in sys.modules
        assert "materialyoucolor" not in str(sys.modules.keys())
