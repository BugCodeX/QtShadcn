"""Tests for the QtShadcn OS theme listener."""

from unittest.mock import patch

import pytest
from qtshadcn.common.config import ThemeMode, qsettings
from qtshadcn.common.stylesheet import setThemeMode, themeMode
from qtshadcn.common.theme_watcher import SystemThemeListener


@pytest.fixture(autouse=True)
def _reset_settings():
    qsettings.reset_for_test()
    yield
    qsettings.reset_for_test()


def _theme_sequence(*values):
    """Return a callable that yields ``values`` and then repeats the last one."""
    state = {"index": 0}

    def theme():
        if state["index"] < len(values):
            value = values[state["index"]]
            state["index"] += 1
            return value
        return values[-1]

    return theme


def _listener_raises(_callback):
    raise RuntimeError("listener unavailable")


class TestLifecycle:
    def test_manual_start_stop(self):
        listener = SystemThemeListener(poll_interval_ms=50)
        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.listener",
            side_effect=_listener_raises,
        ), patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            return_value="Light",
        ):
            listener.start()
            listener.wait(1000)
            listener.stop()
            assert listener.isRunning() is False

    def test_stop_exits_polling_loop(self):
        listener = SystemThemeListener(poll_interval_ms=50)
        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.listener",
            side_effect=_listener_raises,
        ), patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            return_value="Light",
        ):
            listener.start()
            listener.wait(1000)
            listener.stop()
            assert listener.isRunning() is False


class TestSignalEmission:
    def test_signal_emitted_on_theme_change(self, qtbot):
        listener = SystemThemeListener(poll_interval_ms=50)
        collected = []
        listener.themeChanged.connect(collected.append)

        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.listener",
            side_effect=_listener_raises,
        ), patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            side_effect=_theme_sequence("Light", "Dark"),
        ):
            listener.start()
            qtbot.wait(1000)
            listener.stop()

        assert "Dark" in collected

    def test_polling_fallback_emits_signal(self, qtbot):
        listener = SystemThemeListener(poll_interval_ms=50)
        collected = []
        listener.themeChanged.connect(collected.append)

        with patch(
            "qtshadcn.common.theme_watcher.darkdetect.listener",
            side_effect=_listener_raises,
        ), patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            side_effect=_theme_sequence("Light", "Light", "Dark"),
        ):
            listener.start()
            qtbot.wait(1000)
            listener.stop()

        assert "Dark" in collected

    def test_polling_fallback_used_on_non_windows(self, qtbot):
        listener = SystemThemeListener(poll_interval_ms=50)
        collected = []
        listener.themeChanged.connect(collected.append)

        with patch(
            "qtshadcn.common.theme_watcher.sys.platform",
            "darwin",
        ), patch(
            "qtshadcn.common.theme_watcher.darkdetect.theme",
            side_effect=_theme_sequence("Light", "Dark"),
        ):
            listener.start()
            qtbot.wait(1000)
            listener.stop()

        assert "Dark" in collected


class TestAutoModeOnly:
    def test_mode_flips_only_when_auto(self, qapp):
        setThemeMode(ThemeMode.AUTO)
        listener = SystemThemeListener()
        received = []

        def on_change(theme):
            if themeMode() == ThemeMode.AUTO:
                setThemeMode(
                    ThemeMode.DARK if theme == "Dark" else ThemeMode.LIGHT,
                    save=False,
                )
            received.append(theme)

        listener.themeChanged.connect(on_change)
        listener._on_theme_changed("Dark")

        assert received == ["Dark"]
        assert themeMode() == ThemeMode.DARK

    def test_mode_does_not_flip_when_manual(self, qapp):
        setThemeMode(ThemeMode.LIGHT)
        listener = SystemThemeListener()
        received = []

        def on_change(theme):
            if themeMode() == ThemeMode.AUTO:
                setThemeMode(
                    ThemeMode.DARK if theme == "Dark" else ThemeMode.LIGHT,
                    save=False,
                )
            received.append(theme)

        listener.themeChanged.connect(on_change)
        listener._on_theme_changed("Dark")

        assert received == ["Dark"]
        assert themeMode() == ThemeMode.LIGHT
