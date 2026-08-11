"""Static tests asserting Qt imports come from qtpy, not the removed shim."""

import ast
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Modules that import Qt classes must do so through qtpy, never directly from a
# binding or from the legacy internal shim.
QT_MODULES = {"qtpy"}
BINDING_MODULES = {"PySide6", "PyQt6", "PySide2", "PyQt5"}
LEGACY_SHIMS = {"qtshadcn.common.binding", "binding"}


def _imports_qt(source: str) -> bool:
    """Return True when a module source imports any Qt name."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module in QT_MODULES or module.split(".", 1)[0] in BINDING_MODULES:
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in BINDING_MODULES:
                    return True
    return False


MODULES = sorted(
    path
    for path in (PROJECT_ROOT / "qtshadcn").rglob("*.py")
    if _imports_qt(path.read_text(encoding="utf-8"))
)


@pytest.mark.parametrize("module_path", MODULES)
def test_internal_module_imports_qtpy(module_path: Path):
    """Each runtime module that uses Qt must import Qt classes from qtpy."""
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom | ast.Import):
            imports.append(node)

    binding_imports = []
    for node in imports:
        if isinstance(node, ast.ImportFrom) and node.module:
            if (
                node.module.split(".", 1)[0] in BINDING_MODULES
                or node.module in LEGACY_SHIMS
                or "binding" in node.module
            ):
                binding_imports.append(node)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in BINDING_MODULES:
                    binding_imports.append(node)
    assert not binding_imports, f"{module_path.name} still imports from a Qt binding or shim"

    qtpy_imports = [
        node for node in imports if isinstance(node, ast.ImportFrom) and node.module == "qtpy"
    ]
    assert qtpy_imports, f"{module_path.name} does not import from qtpy"
