from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
from examples.gallery.theme_editor import ThemeEditor
from qtshadcn._parser import parse_theme_source
from qtshadcn._qt import QtCore, QtWidgets
from qtshadcn.app import DEFAULT_THEME_FILE


def test_theme_editor_round_trip(qapp: QtWidgets.QApplication, tmp_path: Path):
    """Serializing the editor and parsing it back yields the default theme."""
    editor = ThemeEditor()
    path = tmp_path / "round_trip.xml"
    path.write_bytes(editor.to_xml_bytes())

    default = parse_theme_source(DEFAULT_THEME_FILE)
    loaded = parse_theme_source(path)
    assert loaded == default


def test_theme_editor_set_token_writes_active_palette(
    qapp: QtWidgets.QApplication,
):
    """Changing one color token updates only the active palette."""
    editor = ThemeEditor()
    editor.set_token("Primary", "primary", "#123456")

    tokens = editor.current_tokens()
    assert tokens["light"]["primary"] == "#123456"
    assert tokens["dark"]["primary"] != "#123456"


def test_theme_editor_set_token_writes_dark_palette_when_active(
    qapp: QtWidgets.QApplication,
):
    """Changing one color token updates the dark palette when dark is active."""
    editor = ThemeEditor()
    editor.set_active_mode("dark")
    editor.set_token("Primary", "primary", "#654321")

    tokens = editor.current_tokens()
    assert tokens["dark"]["primary"] == "#654321"
    assert tokens["light"]["primary"] != "#654321"


def test_theme_editor_reset_reloads_default(
    qapp: QtWidgets.QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Reset reloads the default theme file, even after mutations."""
    from examples.gallery import theme_editor as theme_editor_module

    fake_default = tmp_path / "default.xml"
    fake_default.write_text(
        "<theme>"
        "  <light>"
        "    <background>#ffffff</background>"
        "    <foreground>#000000</foreground>"
        "    <card>#ffffff</card>"
        "    <card_foreground>#000000</card_foreground>"
        "    <popover>#ffffff</popover>"
        "    <popover_foreground>#000000</popover_foreground>"
        "    <primary>#ff0000</primary>"
        "    <primary_foreground>#000000</primary_foreground>"
        "    <secondary>#f5f5f5</secondary>"
        "    <secondary_foreground>#000000</secondary_foreground>"
        "    <muted>#f5f5f5</muted>"
        "    <muted_foreground>#737373</muted_foreground>"
        "    <accent>#f5f5f5</accent>"
        "    <accent_foreground>#000000</accent_foreground>"
        "    <destructive>#e7000b</destructive>"
        "    <destructive_foreground>#ffffff</destructive_foreground>"
        "    <border>#e5e5e5</border>"
        "    <input>#e5e5e5</input>"
        "    <ring>#a1a1a1</ring>"
        "    <spacing>4px</spacing>"
        "    <radius>8px</radius>"
        "    <font_family>Open Sans</font_family>"
        "  </light>"
        "  <dark>"
        "    <background>#000000</background>"
        "    <foreground>#ffffff</foreground>"
        "    <card>#000000</card>"
        "    <card_foreground>#ffffff</card_foreground>"
        "    <popover>#000000</popover>"
        "    <popover_foreground>#ffffff</popover_foreground>"
        "    <primary>#ff0000</primary>"
        "    <primary_foreground>#000000</primary_foreground>"
        "    <secondary>#262626</secondary>"
        "    <secondary_foreground>#ffffff</secondary_foreground>"
        "    <muted>#262626</muted>"
        "    <muted_foreground>#a1a1a1</muted_foreground>"
        "    <accent>#404040</accent>"
        "    <accent_foreground>#ffffff</accent_foreground>"
        "    <destructive>#ff6467</destructive>"
        "    <destructive_foreground>#ffffff</destructive_foreground>"
        "    <border>#282828</border>"
        "    <input>#343434</input>"
        "    <ring>#737373</ring>"
        "    <spacing>4px</spacing>"
        "    <radius>8px</radius>"
        "    <font_family>Open Sans</font_family>"
        "  </dark>"
        "</theme>"
    )
    monkeypatch.setattr(theme_editor_module, "DEFAULT_THEME_FILE", fake_default)

    editor = ThemeEditor()
    editor.set_token("Primary", "primary", "#123456")
    editor.reset_to_default()

    assert editor.current_tokens()["light"]["primary"] == "#ff0000"


def test_theme_editor_save_to_appdata(
    qapp: QtWidgets.QApplication,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """save_to_appdata writes the palette to a known AppData path."""
    monkeypatch.setattr(
        QtCore.QStandardPaths,
        "writableLocation",
        lambda _location: str(tmp_path),
    )
    editor = ThemeEditor()
    saved = editor.save_to_appdata()
    assert saved == tmp_path / "qtshadcn" / "gallery" / "saved.xml"
    assert saved.exists()

    root = ET.parse(saved).getroot()
    assert root.find("light") is not None
    assert root.find("dark") is not None


def test_theme_editor_export_to(qapp: QtWidgets.QApplication, tmp_path: Path):
    """export_to writes the palette to the caller-supplied path."""
    editor = ThemeEditor()
    dest = tmp_path / "exported.xml"
    written = editor.export_to(dest)
    assert written == dest
    assert written.exists()


@pytest.mark.usefixtures("qapp")
def test_theme_editor_theme_changed_signal(qtbot):
    """set_token emits the themeChanged signal."""
    editor = ThemeEditor()
    with qtbot.waitSignal(editor.themeChanged, timeout=1000):
        editor.set_token("Primary", "primary", "#654321")
