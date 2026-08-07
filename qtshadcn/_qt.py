"""Internal runtime shim for supported Qt bindings.

The package intentionally does not depend on ``qtpy``. This module selects the
first available binding in the preferred order and exposes its ``QtCore``,
``QtGui``, and ``QtWidgets`` modules atomically so the rest of the package can
import Qt objects without hardcoding a binding. A candidate binding is only
chosen if it provides all required modules; otherwise the shim falls back to the
next candidate as a complete unit.

Preferred order: ``PySide6`` -> ``PyQt6`` -> ``PySide2`` -> ``PyQt5``.
"""

import importlib
import os
from types import ModuleType

_DEFAULT_BINDING_ORDER = ("PySide6", "PyQt6", "PySide2", "PyQt5")
_REQUIRED_MODULES = ("QtCore", "QtGui", "QtWidgets")


def _binding_order() -> tuple[str, ...]:
    """Return the ordered list of bindings to try.

    The ``QTSHADCN_BINDING`` environment variable overrides the default order.
    When set, it should contain a comma-separated list of binding package names
    (e.g., ``PyQt6`` or ``PySide2,PyQt5``). Whitespace around names is ignored.
    """
    env = os.environ.get("QTSHADCN_BINDING", "")
    if env:
        return tuple(name.strip() for name in env.split(",") if name.strip())
    return _DEFAULT_BINDING_ORDER


def _load_binding(binding: str) -> dict[str, ModuleType]:
    """Import every required module from a single binding package.

    Args:
        binding: Binding package name (e.g., ``PySide6``).

    Returns:
        Dictionary mapping module name to imported module.

    Raises:
        ImportError: If any required module cannot be imported from the binding.

    """
    modules = {}
    for name in _REQUIRED_MODULES:
        try:
            modules[name] = importlib.import_module(f"{binding}.{name}")
        except ImportError as exc:
            raise ImportError(f"Binding {binding!r} is missing required module {name!r}") from exc
    return modules


def _select_binding() -> tuple[str, dict[str, ModuleType]]:
    """Select the first binding that provides all required modules.

    Returns:
        Tuple of ``(binding_name, modules)`` where ``modules`` is a dictionary
        mapping ``QtCore``/``QtGui``/``QtWidgets`` to the selected modules.

    Raises:
        ImportError: If no supported binding provides all required modules.

    """
    for binding in _binding_order():
        try:
            modules = _load_binding(binding)
        except ImportError:
            continue
        return binding, modules

    supported = ", ".join(_DEFAULT_BINDING_ORDER)
    raise ImportError(f"No supported Qt binding found. Install one of: {supported}.")


binding_name, _modules = _select_binding()
QtCore = _modules["QtCore"]
QtGui = _modules["QtGui"]
QtWidgets = _modules["QtWidgets"]

__all__ = ["QtCore", "QtGui", "QtWidgets", "binding_name"]
