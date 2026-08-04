"""Tests for package version exports."""

import importlib.metadata
import subprocess
import sys
import tomllib
from pathlib import Path

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


def test_import_succeeds_without_qt_binding():
    """Test that importing the package does not require a Qt binding."""
    script = """
import importlib.abc
import sys


class BlockQtBindings(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".", 1)[0] in {"PySide6", "PyQt6", "PySide2", "PyQt5"}:
            raise ImportError(fullname)
        return None


sys.meta_path.insert(0, BlockQtBindings())
import qtshadcn
print(qtshadcn.__version__)
assert "qtshadcn._qt" not in sys.modules
"""
    command = [
        sys.executable,
        "-c",
        script,
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    assert result.stdout.strip() == _expected_version()


def test_version_falls_back_to_pyproject_without_metadata_or_qt_import():
    """Test that source checkout imports still expose a version without Qt imports."""
    script = """
import importlib.abc
import importlib.metadata
import sys


class BlockQtShimsAndBindings(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "qtshadcn._qt":
            raise ImportError(fullname)
        if fullname.split(".", 1)[0] in {"PySide6", "PyQt6", "PySide2", "PyQt5"}:
            raise ImportError(fullname)
        return None


def missing_metadata(name):
    if name == "qtshadcn":
        raise importlib.metadata.PackageNotFoundError(name)
    return original_version(name)


original_version = importlib.metadata.version
importlib.metadata.version = missing_metadata
sys.meta_path.insert(0, BlockQtShimsAndBindings())

import qtshadcn

print(qtshadcn.__version__)
assert "qtshadcn._qt" not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    assert result.stdout.strip() == _pyproject_version()
