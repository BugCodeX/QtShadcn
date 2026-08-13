"""QtShadcn OS theme change listener.

The listener runs in its own ``QThread``. On Windows it tries to use
``darkdetect.listener``; on other platforms it polls once per second.
"""

from __future__ import annotations

import logging
import sys
import time
from typing import Any

import darkdetect
from qtpy import QtCore

logger = logging.getLogger(__name__)

_QThread: Any = QtCore.QThread


class SystemThemeListener(_QThread):
    """Emit ``themeChanged("Dark"|"Light")`` when the OS theme changes.

    The listener lifecycle is manual: the caller constructs the instance,
    connects to ``themeChanged``, calls ``start()``, and later calls
    ``stop()``.
    """

    themeChanged = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtCore.QObject | None = None,
        *,
        poll_interval_ms: int = 1000,
    ) -> None:
        """Create a listener with the requested polling fallback interval."""
        super().__init__(parent)
        self._poll_interval_ms = poll_interval_ms
        self._running = False

    def run(self) -> None:
        """Start listening for OS theme changes.

        On Windows this attempts to use ``darkdetect.listener``; if that fails
        or on other platforms it falls back to polling.
        """
        self._running = True
        if sys.platform == "win32":
            try:
                darkdetect.listener(self._on_theme_changed)
            except Exception as e:
                logger.warning("darkdetect listener failed, falling back to polling: %s", e)
                self._poll_loop()
        else:
            self._poll_loop()

    def _poll_loop(self) -> None:
        last_theme = darkdetect.theme()
        while self._running:
            current = darkdetect.theme()
            if current != last_theme and current in {"Dark", "Light"}:
                self._on_theme_changed(current)
                last_theme = current
            # Short sleeps make stop() responsive while keeping overhead low.
            for _ in range(self._poll_interval_ms // 100):
                if not self._running:
                    break
                time.sleep(0.1)

    def _on_theme_changed(self, theme: str) -> None:
        self.themeChanged.emit(theme)

    def stop(self) -> None:
        """Request the listener thread to exit and wait for it to finish."""
        self._running = False
        self.wait(5000)


_ = Any
