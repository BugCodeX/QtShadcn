"""QtShadcn custom exceptions."""


class QtShadcnError(Exception):
    """Base exception for all errors raised by QtShadcn."""


class ThemeParseError(QtShadcnError, ValueError):
    """Raised when a QtShadcn XML theme cannot be parsed or validated."""


class ThemeRenderError(QtShadcnError, RuntimeError):
    """Raised when a QSS stylesheet cannot be rendered or compiled from Jinja2 template."""


class QtBindingError(QtShadcnError, ImportError):
    """Raised when no supported Qt binding can be loaded.

    QtShadcn supports PySide6, PyQt6, PySide2, and PyQt5 via ``qtpy``.
    Set the ``QT_API`` environment variable to choose a specific binding
    (``pyside6``, ``pyqt6``, ``pyside2``, or ``pyqt5``) before importing.
    """
