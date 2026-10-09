"""Binding-neutral Qt shim (PySide6 / PyQt6)."""

import sys
from typing import TYPE_CHECKING

from qtshadcn.exceptions import QtBindingError

if TYPE_CHECKING:
    from PySide6 import QtCore, QtGui, QtWidgets
else:
    # 1. Check if PySide6 or PyQt6 is already loaded in sys.modules
    if "PySide6" in sys.modules:
        from PySide6 import QtCore, QtGui, QtWidgets
    elif "PyQt6" in sys.modules:
        from PyQt6 import QtCore, QtGui, QtWidgets
    else:
        # 2. Fallback to try importing PySide6, then PyQt6
        try:
            from PySide6 import QtCore, QtGui, QtWidgets
        except ImportError:
            try:
                from PyQt6 import QtCore, QtGui, QtWidgets
            except ImportError as exc:
                raise QtBindingError(
                    "No supported Qt binding found. Please install PySide6 or PyQt6."
                ) from exc

    # Normalize Signal, Slot, and Property for PyQt6
    if hasattr(QtCore, "pyqtSignal"):
        QtCore.Signal = QtCore.pyqtSignal
        QtCore.Slot = QtCore.pyqtSlot
        QtCore.Property = getattr(QtCore, "pyqtProperty", None)

__all__ = ["QtCore", "QtGui", "QtWidgets"]
