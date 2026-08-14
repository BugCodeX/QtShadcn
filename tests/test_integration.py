"""Integration tests for the QtShadcn theme pipeline."""

from pathlib import Path

import pytest
from qtpy import QtWidgets
from qtshadcn import getTheme, setTheme, setThemeMode
from qtshadcn.common.renderer import _build_theme
from qtshadcn.models import ShadcnThemeTokens

FULL_THEME = """\
<theme>
  <light>
    <background>#ffffff</background>
    <foreground>#020617</foreground>
    <card>#ffffff</card>
    <card_foreground>#020617</card_foreground>
    <popover>#ffffff</popover>
    <popover_foreground>#020617</popover_foreground>
    <primary>#0f172a</primary>
    <primary_foreground>#f8fafc</primary_foreground>
    <secondary>#f1f5f9</secondary>
    <secondary_foreground>#0f172a</secondary_foreground>
    <muted>#f1f5f9</muted>
    <muted_foreground>#64748b</muted_foreground>
    <accent>#f1f5f9</accent>
    <accent_foreground>#0f172a</accent_foreground>
    <destructive>#ef4444</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#e2e8f0</border>
    <input>#e2e8f0</input>
    <ring>#0f172a</ring>
    <spacing>4px</spacing>
    <radius>8px</radius>
    <font_family>Open Sans</font_family>
  </light>
  <dark>
    <background>#020617</background>
    <foreground>#f8fafc</foreground>
    <card>#020617</card>
    <card_foreground>#f8fafc</card_foreground>
    <popover>#020617</popover>
    <popover_foreground>#f8fafc</popover_foreground>
    <primary>#f8fafc</primary>
    <primary_foreground>#0f172a</primary_foreground>
    <secondary>#1e293b</secondary>
    <secondary_foreground>#f8fafc</secondary_foreground>
    <muted>#1e293b</muted>
    <muted_foreground>#94a3b8</muted_foreground>
    <accent>#1e293b</accent>
    <accent_foreground>#f8fafc</accent_foreground>
    <destructive>#7f1d1d</destructive>
    <destructive_foreground>#f8fafc</destructive_foreground>
    <border>#1e293b</border>
    <input>#1e293b</input>
    <ring>#cbd5e1</ring>
    <spacing>4px</spacing>
    <radius>8px</radius>
    <font_family>Open Sans</font_family>
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
        setThemeMode("light", save=False)
        setTheme(full_theme_path, save=False)
        tokens = getTheme()
        assert isinstance(tokens, ShadcnThemeTokens)
        assert tokens.background == "#ffffff"
        assert tokens.primary == "#0f172a"
        assert "px" in tokens.radius
        assert tokens.spacing == "4px"
        assert qapp.styleSheet() != ""

    def test_qss_output_is_qt_safe(self, qapp: QtWidgets.QApplication, full_theme_path: Path):
        """Test that the QSS output is safe for Qt."""
        setThemeMode("light", save=False)
        setTheme(full_theme_path, save=False)
        tokens = getTheme()
        qss = _build_theme(tokens)
        assert "oklch(" not in qss
        assert "rem" not in qss
