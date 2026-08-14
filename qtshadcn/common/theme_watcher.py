"""QtShadcn OS theme change listener.

The listener runs in its own ``QThread`` and polls ``darkdetect.theme()``
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


class SystemThemeListener(_BaseThread):
    """Emit ``themeChanged("Dark"|"Light")`` when the OS theme changes."""

    themeChanged = QtCore.Signal(str)

    def __init__(
        self,
        parent: QtCore.QObject | None = None,
        *,
        poll_interval_ms: int = 1000,
    ) -> None:
        """Set up the polling thread."""
        super().__init__(parent)
        self._poll_interval_ms = poll_interval_ms

    def run(self) -> None:
        """Poll the OS theme and emit ``themeChanged`` on transitions."""
        last_theme = darkdetect.theme()
        while not self.isInterruptionRequested():
            current = darkdetect.theme()
            if current != last_theme and current in {"Dark", "Light"}:
                logger.debug("OS theme changed to %s", current)
                self.themeChanged.emit(current)
                last_theme = current
                # Polling interval is ignored here on purpose: a longer sleep
                # after a change suppresses rapid repeated OS transitions.
                self.msleep(2000)
            else:
                self.msleep(self._poll_interval_ms)

    def stop(self) -> None:
        """Request a clean thread shutdown."""
        self.requestInterruption()
        self.wait(5000)
