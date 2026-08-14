"""Tests for the QtShadcn OS theme watcher."""

from unittest.mock import patch

import pytest
from qtshadcn.common.config import ThemeMode, qsettings
from qtshadcn.common.stylesheet import setThemeMode, themeMode
from qtshadcn.common.theme_watcher import SystemThemeWatcher


@pytest.fixture(autouse=True)
def _reset_settings():
    qsettings.reset_for_test()
    yield
    qsettings.reset_for_test()


def _theme_sequence(*values):
    state = {"index": 0}

    def theme():
        if state["index"] < len(values):
            value = values[state["index"]]
            state["index"] += 1
            return value
        return values[-1]

    return theme


class TestLifecycle:
    def test_manual_start_stop(self):
        listener = SystemThemeWatcher(pollIntervalMs=50)
        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            return_value="Light",
        ):
            listener.start()
            listener.wait(1000)
            listener.stop()
            assert listener.isRunning() is False

    def test_stop_exits_polling_loop(self):
        listener = SystemThemeWatcher(pollIntervalMs=50)
        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            return_value="Light",
        ):
            listener.start()
            listener.wait(1000)
            listener.stop()
            assert listener.isRunning() is False


class TestSignalEmission:
    def test_signal_emitted_on_theme_change(self, qtbot):
        listener = SystemThemeWatcher(pollIntervalMs=50)
        collected = []
        listener.themeChanged.connect(collected.append)

        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            side_effect=_theme_sequence("Light", "Dark"),
        ):
            listener.start()
            qtbot.wait(500)
            listener.stop()

        assert "Dark" in collected

    def test_polling_detects_theme_change(self, qtbot):
        listener = SystemThemeWatcher(pollIntervalMs=50)
        collected = []
        listener.themeChanged.connect(collected.append)

        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            side_effect=_theme_sequence("Light", "Light", "Dark"),
        ):
            listener.start()
            qtbot.wait(500)
            listener.stop()

        assert "Dark" in collected


class TestAutoModeOnly:
    def test_mode_flips_only_when_auto(self, qapp):
        setThemeMode(ThemeMode.AUTO)
        listener = SystemThemeWatcher()
        received = []

        def on_change(theme):
            if themeMode() == ThemeMode.AUTO:
                setThemeMode(
                    ThemeMode.DARK if theme == "Dark" else ThemeMode.LIGHT,
                    save=False,
                )
            received.append(theme)

        listener.themeChanged.connect(on_change)
        listener.themeChanged.emit("Dark")

        assert received == ["Dark"]
        assert themeMode() == ThemeMode.DARK

    def test_mode_does_not_flip_when_manual(self, qapp):
        setThemeMode(ThemeMode.LIGHT)
        listener = SystemThemeWatcher()
        received = []

        def on_change(theme):
            if themeMode() == ThemeMode.AUTO:
                setThemeMode(
                    ThemeMode.DARK if theme == "Dark" else ThemeMode.LIGHT,
                    save=False,
                )
            received.append(theme)

        listener.themeChanged.connect(on_change)
        listener.themeChanged.emit("Dark")

        assert received == ["Dark"]
        assert themeMode() == ThemeMode.LIGHT
