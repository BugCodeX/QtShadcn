"""Tests for the QtShadcn font registry and public API."""

import json

import pytest
from qtshadcn.common.config import qsettings
from qtshadcn.common.font import (
    _ensureFontFamilyRegistered,
    _fontRegistry,
    _registeredFamilies,
    getFontFamilies,
    getFontFamily,
    registerFontFamily,
    setFontFamilies,
    setFontFamily,
)
from qtshadcn.common.stylesheet import setTheme


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
        "font_family": "Open Sans",
    }
    values.update(overrides)
    return values


@pytest.fixture
def sample_theme_json(tmp_path):
    path = tmp_path / "theme.json"
    data = {"light": _tokens(), "dark": _tokens(background="#000000")}
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


@pytest.fixture(autouse=True)
def _reset_settings(tmp_path):
    qsettings.reset_for_test()
    qsettings.set_config_dir(tmp_path)
    original_registry = dict(_fontRegistry)
    _registeredFamilies.clear()
    yield
    qsettings.reset_for_test()
    _registeredFamilies.clear()
    _fontRegistry.clear()
    _fontRegistry.update(original_registry)


class TestFontApi:
    def test_set_font_family_persists(self, tmp_path):
        setFontFamily("Open Sans", save=True)

        assert getFontFamily() == "Open Sans"
        assert (tmp_path / "font_family.json").exists()
        assert getFontFamilies() == ["Open Sans"]

    def test_set_font_families_without_save(self, tmp_path):
        setFontFamilies(["Open Sans", "sans-serif"], save=False)

        assert getFontFamilies() == ["Open Sans", "sans-serif"]
        assert not (tmp_path / "font_family.json").exists()

    def test_set_font_family_to_none_clears_stored_value(self):
        setFontFamily("Open Sans")
        setFontFamily(None)

        assert qsettings.font_family.value == []

    def test_get_font_family_falls_back_to_theme_tokens(self, qapp, sample_theme_json):
        setTheme(sample_theme_json)
        qsettings.font_family.reset()

        assert getFontFamily() == "Open Sans"
        assert getFontFamilies() == ["Open Sans"]

    def test_register_font_family_from_file(self, tmp_path):
        font_file = tmp_path / "Custom.ttf"
        font_file.write_text("dummy", encoding="utf-8")

        registerFontFamily("Custom Family", font_file)

        assert "Custom Family" in _fontRegistry
        assert any(p.name == "Custom.ttf" for p in _fontRegistry["Custom Family"])

    def test_register_font_family_from_directory(self, tmp_path):
        (tmp_path / "A.ttf").write_text("dummy", encoding="utf-8")
        (tmp_path / "B.otf").write_text("dummy", encoding="utf-8")
        (tmp_path / "ignore.txt").write_text("dummy", encoding="utf-8")

        registerFontFamily("Dir Family", tmp_path)

        names = {p.name for p in _fontRegistry["Dir Family"]}
        assert names == {"A.ttf", "B.otf"}

    def test_ensure_font_family_registered_skips_already_registered(self):
        _registeredFamilies.add("Already Registered")

        assert _ensureFontFamilyRegistered("Already Registered") is True
