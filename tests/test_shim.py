"""Tests for the internal Qt binding shim."""

from types import ModuleType
from unittest.mock import patch

import pytest
import qtshadcn.common.binding as shim


def _make_module(full_name: str) -> ModuleType:
    """Return a minimal module object with the given fully qualified name."""
    return ModuleType(full_name)


class TestShimImports:
    """Tests that the shim imports are available."""

    def test_qapplication_available(self):
        """Test that QApplication is available through the shim."""
        assert shim.QtWidgets.QApplication is not None

    def test_qfontdatabase_available(self):
        """Test that QFontDatabase is available through the shim."""
        assert shim.QtGui.QFontDatabase is not None

    def test_qstandardpaths_available(self):
        """Test that QStandardPaths is available through the shim."""
        assert shim.QtCore.QStandardPaths is not None


class TestAtomicBindingSelection:
    """Tests that the shim selects one complete binding atomically."""

    def test_all_modules_share_same_binding(self):
        """Test that QtCore, QtGui, and QtWidgets come from the same binding."""
        prefixes = {
            shim.QtCore.__name__.split(".")[0],
            shim.QtGui.__name__.split(".")[0],
            shim.QtWidgets.__name__.split(".")[0],
        }
        assert len(prefixes) == 1

    def test_binding_name_matches_module_prefix(self):
        """Test that binding_name reflects the selected binding package."""
        prefix = shim.QtCore.__name__.split(".")[0]
        assert shim.binding_name == prefix

    def test_select_binding_prefers_first_complete_binding(self, monkeypatch):
        """Test that the preferred binding order starts with PySide6."""
        monkeypatch.delenv("QTSHADCN_BINDING", raising=False)
        with patch("importlib.import_module") as mock_import:
            modules = {
                "QtCore": _make_module("PySide6.QtCore"),
                "QtGui": _make_module("PySide6.QtGui"),
                "QtWidgets": _make_module("PySide6.QtWidgets"),
            }
            mock_import.side_effect = lambda name: modules[name.split(".", 1)[1]]
            binding, selected = shim._select_binding()
            assert binding == "PySide6"
            assert selected["QtCore"].__name__ == "PySide6.QtCore"
            assert mock_import.call_args_list[0].args[0] == "PySide6.QtCore"

    def test_select_binding_falls_back_on_partial_failure(self):
        """Test that a missing submodule triggers fallback to the next binding."""
        pyside6_modules = {
            "QtCore": _make_module("PySide6.QtCore"),
            "QtWidgets": _make_module("PySide6.QtWidgets"),
        }
        pyqt6_modules = {
            "QtCore": _make_module("PyQt6.QtCore"),
            "QtGui": _make_module("PyQt6.QtGui"),
            "QtWidgets": _make_module("PyQt6.QtWidgets"),
        }

        with patch("importlib.import_module") as mock_import:
            calls = []

            def fake_import(name: str):
                calls.append(name)
                parts = name.split(".")
                binding, mod = parts[0], parts[1]
                # First binding: QtCore is available, QtGui is missing -> abort
                if binding == "PySide6":
                    if mod == "QtGui":
                        raise ImportError("missing QtGui")
                    return pyside6_modules[mod]
                # Second binding is complete
                if binding == "PyQt6":
                    return pyqt6_modules[mod]
                raise ImportError(name)

            mock_import.side_effect = fake_import
            binding, selected = shim._select_binding()
            assert binding == "PyQt6"
            assert selected["QtCore"].__name__ == "PyQt6.QtCore"
            assert selected["QtGui"].__name__ == "PyQt6.QtGui"
            assert selected["QtWidgets"].__name__ == "PyQt6.QtWidgets"
            # Do not keep partially imported modules from the failed candidate
            assert "PySide6.QtWidgets" not in calls

    def test_select_binding_raises_actionable_error(self):
        """Test that the shim raises a clear error when no binding exists."""
        with (
            patch("importlib.import_module", side_effect=ImportError("not installed")),
            pytest.raises(ImportError, match="PySide6, PyQt6"),
        ):
            shim._select_binding()


class TestBindingOrderEnv:
    """Tests for the QTSHADCN_BINDING environment variable."""

    def test_qtshadcn_binding_forces_single_binding(self, monkeypatch):
        """A single binding in QTSHADCN_BINDING restricts selection to that binding."""
        monkeypatch.setenv("QTSHADCN_BINDING", "PyQt6")
        pyqt6_modules = {
            "QtCore": _make_module("PyQt6.QtCore"),
            "QtGui": _make_module("PyQt6.QtGui"),
            "QtWidgets": _make_module("PyQt6.QtWidgets"),
        }

        with patch("importlib.import_module") as mock_import:

            def fake_import(name: str):
                if name.startswith("PyQt6"):
                    return pyqt6_modules[name.split(".", 1)[1]]
                raise ImportError(name)

            mock_import.side_effect = fake_import
            binding, selected = shim._select_binding()
            assert binding == "PyQt6"
            assert selected["QtCore"].__name__ == "PyQt6.QtCore"
            assert all(call.args[0].startswith("PyQt6") for call in mock_import.call_args_list)

    def test_qtshadcn_binding_accepts_comma_separated_list(self, monkeypatch):
        """QTSHADCN_BINDING accepts a comma-separated list tried in order."""
        monkeypatch.setenv("QTSHADCN_BINDING", "PySide6,PyQt6")
        pyqt6_modules = {
            "QtCore": _make_module("PyQt6.QtCore"),
            "QtGui": _make_module("PyQt6.QtGui"),
            "QtWidgets": _make_module("PyQt6.QtWidgets"),
        }

        with patch("importlib.import_module") as mock_import:

            def fake_import(name: str):
                if name.startswith("PySide6"):
                    raise ImportError(name)
                if name.startswith("PyQt6"):
                    return pyqt6_modules[name.split(".", 1)[1]]
                raise ImportError(name)

            mock_import.side_effect = fake_import
            binding, selected = shim._select_binding()
            assert binding == "PyQt6"
            assert selected["QtCore"].__name__ == "PyQt6.QtCore"
            assert mock_import.call_args_list[0].args[0].startswith("PySide6")

    def test_qtshadcn_binding_unset_uses_default_order(self, monkeypatch):
        """When QTSHADCN_BINDING is unset, the default binding order is used."""
        monkeypatch.delenv("QTSHADCN_BINDING", raising=False)
        pyside6_modules = {
            "QtCore": _make_module("PySide6.QtCore"),
            "QtGui": _make_module("PySide6.QtGui"),
            "QtWidgets": _make_module("PySide6.QtWidgets"),
        }

        with patch("importlib.import_module") as mock_import:

            def fake_import(name: str):
                if name.startswith("PySide6"):
                    return pyside6_modules[name.split(".", 1)[1]]
                raise ImportError(name)

            mock_import.side_effect = fake_import
            binding, _ = shim._select_binding()
            assert binding == "PySide6"
            assert mock_import.call_args_list[0].args[0] == "PySide6.QtCore"


class TestSignalAlias:
    """Tests for the binding-neutral Signal alias."""

    def test_signal_alias_matches_binding(self):
        """Signal is exposed and points to the binding-specific signal type."""
        assert hasattr(shim, "Signal")
        if shim.binding_name.startswith("PySide"):
            assert shim.Signal is shim.QtCore.Signal
        else:
            assert shim.Signal is shim.QtCore.pyqtSignal
