"""Tests for the QtShadcn persistent configuration system."""

import json
import warnings

from qtpy import QtCore
from qtshadcn.common.config import ConfigItem, QtShadcnSettings, ThemeMode, qsettings
from qtshadcn.models import ShadcnTheme, ShadcnThemeTokens


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


class TestSingleton:
    def test_qsettings_is_singleton(self):
        from qtshadcn.common.config import qsettings as qsettings2

        assert qsettings2 is qsettings


class TestConfigItem:
    def test_default_value(self):
        item = ConfigItem("mode", "auto")
        assert item.value == "auto"

    def test_set_updates_value(self):
        item = ConfigItem("mode", "auto")
        item.set("dark")
        assert item.value == "dark"

    def test_validator_rejects_invalid_value(self):
        item = ConfigItem("mode", "auto", lambda v: v in {"auto", "light", "dark"})
        item.set("invalid")
        assert item.value == "auto"

    def test_block_signal_prevents_emit(self, qtbot):
        item = ConfigItem("mode", "auto")
        received = []
        item.valueChanged.connect(lambda v: received.append(v))
        item.set("dark", block_signal=True)
        assert item.value == "dark"
        assert received == []


class TestConfigDir:
    def test_default_config_dir_uses_app_data_location(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            QtCore.QStandardPaths,
            "writableLocation",
            lambda _loc: str(tmp_path),
        )
        qsettings.reset_for_test()
        assert qsettings.config_dir() == tmp_path / "config"

    def test_custom_config_dir(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path / "custom")
        assert qsettings.config_dir() == tmp_path / "custom"


class TestLoadAndSave:
    def test_load_restores_theme_mode(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        (tmp_path / "theme_mode.json").write_text(json.dumps({"mode": "dark"}), encoding="utf-8")

        qsettings.load()

        assert qsettings.theme_mode.value == "dark"

    def test_load_restores_theme_from_json(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        theme_data = {
            "version": 1,
            "light": _tokens(),
            "dark": _tokens(background="#000000"),
        }
        (tmp_path / "theme.json").write_text(json.dumps(theme_data), encoding="utf-8")

        qsettings.load()

        assert qsettings._theme is not None
        assert qsettings._theme.dark.background == "#000000"
        assert qsettings.theme.value == str(tmp_path / "theme.json")

    def test_load_restores_theme_from_xml(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        xml = """\
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
"""
        (tmp_path / "theme.xml").write_text(xml, encoding="utf-8")

        qsettings.load()

        assert qsettings._theme is not None
        assert qsettings._theme.light.background == "#ffffff"
        assert qsettings.theme.value == str(tmp_path / "theme.xml")

    def test_load_restores_style_sheet(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        (tmp_path / "style.qss").write_text("QWidget { color: red; }", encoding="utf-8")

        qsettings.load()

        assert qsettings.additional_style_sheet.value == str(tmp_path / "style.qss")

    def test_load_with_config_dir_argument(self, tmp_path):
        qsettings.reset_for_test()
        (tmp_path / "theme_mode.json").write_text(json.dumps({"mode": "light"}), encoding="utf-8")

        qsettings.load(config_dir=tmp_path)

        assert qsettings.theme_mode.value == "light"
        assert qsettings.config_dir() == tmp_path

    def test_load_with_custom_settings_instance(self, tmp_path):
        custom = QtShadcnSettings()
        (tmp_path / "theme_mode.json").write_text(json.dumps({"mode": "dark"}), encoding="utf-8")

        qsettings.load(config_dir=tmp_path, settings=custom)

        assert custom.theme_mode.value == "dark"
        assert custom.config_dir() == tmp_path

    def test_save_writes_theme_mode_atomically(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        qsettings.theme_mode.set("dark")

        qsettings.save(only={"theme_mode"})

        path = tmp_path / "theme_mode.json"
        assert path.exists()
        assert json.loads(path.read_text(encoding="utf-8")) == {"mode": "dark"}
        assert not (tmp_path / "theme_mode.json.tmp").exists()

    def test_save_writes_theme_and_style(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        qsettings._theme = ShadcnTheme(
            light=ShadcnThemeTokens(**_tokens()),
            dark=ShadcnThemeTokens(**_tokens(background="#000000")),
        )
        qsettings.additional_style_sheet.set("QWidget { color: blue; }")

        qsettings.save(only={"theme", "additional_style_sheet"})

        theme_path = tmp_path / "theme.json"
        assert theme_path.exists()
        data = json.loads(theme_path.read_text(encoding="utf-8"))
        assert data["version"] == 1
        assert data["dark"]["background"] == "#000000"
        style_path = tmp_path / "style.qss"
        assert style_path.exists()
        assert style_path.read_text(encoding="utf-8") == "QWidget { color: blue; }"

    def test_corrupt_theme_mode_json_falls_back_to_auto(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        (tmp_path / "theme_mode.json").write_text("not json", encoding="utf-8")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            qsettings.load()

        assert qsettings.theme_mode.value == ThemeMode.AUTO.value
        assert any("Corrupt theme_mode.json" in str(warning.message) for warning in w)

    def test_save_jinja_style_sheet(self, tmp_path):
        qsettings.reset_for_test()
        qsettings.set_config_dir(tmp_path)
        qsettings.additional_style_sheet.set("QWidget { color: {{ tokens.primary }}; }")

        qsettings.save(only={"additional_style_sheet"})

        assert (tmp_path / "style.jinja").exists()
        assert not (tmp_path / "style.qss").exists()
