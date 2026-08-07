"""Tests for package version exports."""

import importlib
import importlib.abc
import importlib.metadata
import sys
import tomllib
from pathlib import Path

import pytest
import qtshadcn

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _pyproject_version() -> str:
    """Return the project version declared in pyproject.toml."""
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)
    return str(pyproject["project"]["version"])


def _expected_version() -> str:
    """Return the expected package version for installed or source-checkout tests."""
    try:
        return importlib.metadata.version("qtshadcn")
    except importlib.metadata.PackageNotFoundError:
        return _pyproject_version()


def test_version_matches_available_project_version():
    """Test that the public version matches metadata or the source fallback."""
    assert qtshadcn.__version__ == _expected_version()


class _BlockQtBindings(importlib.abc.MetaPathFinder):
    """Meta path finder that blocks Qt binding imports."""

    def find_spec(self, fullname: str, path: object = None, target: object = None) -> None:
        if fullname.split(".", 1)[0] in {"PySide6", "PyQt6", "PySide2", "PyQt5"}:
            raise ImportError(fullname)
        return None


class _BlockQtShimsAndBindings(importlib.abc.MetaPathFinder):
    """Meta path finder that blocks Qt bindings and the qtshadcn._qt shim."""

    def find_spec(self, fullname: str, path: object = None, target: object = None) -> None:
        if fullname == "qtshadcn._qt":
            raise ImportError(fullname)
        if fullname.split(".", 1)[0] in {"PySide6", "PyQt6", "PySide2", "PyQt5"}:
            raise ImportError(fullname)
        return None


@pytest.fixture
def isolated_qtshadcn_import():
    """Remove qtshadcn modules from sys.modules and restore state after the test."""
    original_meta_path = sys.meta_path.copy()
    original_modules = dict(sys.modules)

    for name in list(sys.modules):
        if name == "qtshadcn" or name.startswith("qtshadcn."):
            del sys.modules[name]

    try:
        yield
    finally:
        sys.meta_path[:] = original_meta_path
        sys.modules.clear()
        sys.modules.update(original_modules)


def test_import_succeeds_without_qt_binding(isolated_qtshadcn_import: None):
    """Test that importing the package does not require a Qt binding."""
    sys.meta_path.insert(0, _BlockQtBindings())

    import qtshadcn

    assert qtshadcn.__version__ == _expected_version()
    assert "qtshadcn._qt" not in sys.modules


def test_version_falls_back_to_pyproject_without_metadata_or_qt_import(
    isolated_qtshadcn_import: None, monkeypatch: pytest.MonkeyPatch
):
    """Test that source checkout imports still expose a version without Qt imports."""
    original_version = importlib.metadata.version

    def missing_metadata(name: str) -> str:
        if name == "qtshadcn":
            raise importlib.metadata.PackageNotFoundError(name)
        return original_version(name)

    monkeypatch.setattr(importlib.metadata, "version", missing_metadata)
    sys.meta_path.insert(0, _BlockQtShimsAndBindings())

    import qtshadcn

    assert qtshadcn.__version__ == _pyproject_version()
    assert "qtshadcn._qt" not in sys.modules
