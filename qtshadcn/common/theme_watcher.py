"""QtShadcn OS theme change watcher.

The watcher runs in its own ``QThread`` and polls ``darkdetect.theme()``
to detect light/dark switches. After emitting a change it sleeps for two
seconds to avoid repeated signals from short-lived transitions.
"""

from __future__ import annotations

import logging
from typing import Any

import darkdetect
from qtpy import QtCore

# qtpy exposes QtCore.QThread as a binding union at type-check time, so we
# alias it to ``Any`` to keep ``ty`` happy while remaining binding-neutral.
_BaseThread: Any = QtCore.QThread

logger = logging.getLogger(__name__)


class SystemThemeWatcher(_BaseThread):
    """Emit ``themeChanged("Dark"|"Light")`` when the OS theme changes."""

    themeChanged = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtCore.QObject | None = None,
        *,
        pollIntervalMs: int = 1000,
    ) -> None:
        """Initialize the thread.

        Args:
            parent (QtCore.QObject, optional): Standard Qt parent.
            pollIntervalMs (int, optional): How often to check the OS theme (default: 1000).
                A lower value reacts faster but wakes the thread more frequently.
        """
        super().__init__(parent)
        self._pollIntervalMs = pollIntervalMs

    def run(self) -> None:
        """Poll the OS theme and emit ``themeChanged`` on transitions."""
        lastTheme = darkdetect.theme()
        while not self.isInterruptionRequested():
            currentTheme = darkdetect.theme()
            if currentTheme != lastTheme and currentTheme in {"Dark", "Light"}:
                logger.debug("OS theme changed to %s", currentTheme)
                self.themeChanged.emit(currentTheme)
                lastTheme = currentTheme
                # Polling interval is ignored here on purpose: a longer sleep
                # after a change suppresses rapid repeated OS transitions.
                self.msleep(2000)
            else:
                self.msleep(self._pollIntervalMs)

    def stop(self) -> None:
        """Request interruption and wait for the polling loop to exit cleanly."""
        self.requestInterruption()
        self.wait(5000)
