"""Tests for the QtShadcn stylesheet rendering and 3-concept API."""

import json
from unittest.mock import patch

import pytest
from qtpy import QtWidgets
from qtshadcn.common.config import ThemeMode, qsettings
from qtshadcn.common.stylesheet import (
    getStyleSheet,
    getTheme,
    isDarkTheme,
    setStyleSheet,
    setTheme,
    setThemeMode,
    themeMode,
    toggleThemeMode,
)


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
    return values


@pytest.fixture
def sample_xml(tmp_path):
    path = tmp_path / "theme.xml"
    path.write_text(
        """\
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
    <font_family>system-ui, sans-serif</font_family>
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
    <font_family>system-ui, sans-serif</font_family>
  </dark>
</theme>
""",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def sample_json(tmp_path):
    path = tmp_path / "theme.json"
    data = {"version": 1, "light": _tokens(), "dark": _tokens(background="#000000")}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def _reset_settings(tmp_path):
    qsettings.reset_for_test()
    qsettings.set_config_dir(tmp_path)
    yield
    qsettings.reset_for_test()


class TestThemeMode:
    def test_set_theme_mode(self):
        setThemeMode("dark")
        assert themeMode() == ThemeMode.DARK

    def test_set_theme_mode_enum(self):
        setThemeMode(ThemeMode.LIGHT)
        assert themeMode() == ThemeMode.LIGHT

    def test_invalid_theme_mode_raises(self):
        with pytest.raises(Exception, match="Invalid theme_mode"):
            setThemeMode("invalid")

    def test_toggle_theme_mode(self):
        setThemeMode(ThemeMode.AUTO)
        toggleThemeMode()
        assert themeMode() == ThemeMode.LIGHT
        toggleThemeMode()
        assert themeMode() == ThemeMode.DARK
        toggleThemeMode()
        assert themeMode() == ThemeMode.AUTO

    def test_is_dark_theme_resolves_dark(self):
        setThemeMode(ThemeMode.DARK)
        assert isDarkTheme() is True

    def test_is_dark_theme_resolves_light(self):
        setThemeMode(ThemeMode.LIGHT)
        assert isDarkTheme() is False

    def test_is_dark_theme_auto_detects_dark(self):
        with patch("qtshadcn.common.stylesheet.darkdetect.theme", return_value="Dark"):
            setThemeMode(ThemeMode.AUTO)
            assert isDarkTheme() is True

    def test_theme_mode_persists(self, tmp_path):
        setThemeMode(ThemeMode.DARK, save=True)
        assert (tmp_path / "theme_mode.json").exists()


class TestSetTheme:
    def test_set_xml_theme(self, qapp, sample_xml, tmp_path):
        setTheme(sample_xml, save=True)
        tokens = getTheme()
        assert tokens.background == "#ffffff"
        assert (tmp_path / "theme.xml").exists()
        assert (tmp_path / "theme.json").exists()

    def test_set_json_theme(self, qapp, sample_json, tmp_path):
        setThemeMode(ThemeMode.LIGHT)
        setTheme(sample_json, save=True)
        tokens = getTheme()
        assert tokens.background == "#ffffff"
        assert (tmp_path / "theme.json").exists()

    def test_get_theme_respects_mode(self, qapp, sample_xml):
        setThemeMode(ThemeMode.DARK)
        setTheme(sample_xml)
        tokens = getTheme()
        assert tokens.background == "#020617"

    def test_set_theme_with_custom_tokens(self, qapp, sample_xml):
        setThemeMode(ThemeMode.LIGHT)
        setTheme(sample_xml, custom_tokens={"background": "#123456"})
        tokens = getTheme()
        assert tokens.background == "#123456"

    def test_missing_theme_file_raises(self):
        with pytest.raises(Exception, match="Could not read theme source"):
            setTheme("missing-theme.xml")

    def test_css_theme_rejected(self, tmp_path):
        path = tmp_path / "theme.css"
        path.write_text("* { color: red; }", encoding="utf-8")
        with pytest.raises(Exception, match="CSS"):
            setTheme(path)


class TestSetStyleSheet:
    def test_set_inline_qss(self, qapp):
        setStyleSheet("QWidget { color: red; }")
        assert getStyleSheet() == "QWidget { color: red; }"
        assert "QWidget { color: red; }" in qapp.styleSheet()

    def test_set_qss_file(self, qapp, tmp_path):
        path = tmp_path / "extra.qss"
        path.write_text("QWidget { color: blue; }", encoding="utf-8")
        setStyleSheet(path, save=True)
        assert "QWidget { color: blue; }" in qapp.styleSheet()
        assert (tmp_path / "style.qss").exists()

    def test_set_jinja_file(self, qapp, tmp_path):
        path = tmp_path / "extra.jinja"
        path.write_text("QWidget { color: {{ tokens.primary }}; }", encoding="utf-8")
        setStyleSheet(path, save=True)
        assert (tmp_path / "style.jinja").exists()
        assert not (tmp_path / "style.qss").exists()

    def test_set_inline_jinja_detected(self, qapp, tmp_path):
        setStyleSheet("QWidget { color: {{ tokens.primary }}; }", save=True)
        assert (tmp_path / "style.jinja").exists()


class TestRendering:
    def test_set_theme_mode_renders_qss(self, qapp, sample_xml):
        setTheme(sample_xml)
        before = qapp.styleSheet()
        setThemeMode(ThemeMode.DARK)
        after = qapp.styleSheet()
        assert after != before or "#020617" in after

    def test_no_application_is_no_op(self, monkeypatch, sample_xml):
        monkeypatch.setattr(QtWidgets.QApplication, "instance", lambda: None)
        setThemeMode(ThemeMode.DARK)
        setTheme(sample_xml)
        setStyleSheet("QWidget { color: red; }")
