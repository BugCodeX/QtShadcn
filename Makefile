# =============================================================
# Makefile — qtshadcn
# Requires: make, uv
#
# Note: This Makefile is written for PowerShell on Windows. Most targets
# use uv and are therefore cross-platform, but the SHELL and any target
# that manipulates environment variables assumes Windows PowerShell syntax.
# Running on Linux/macOS may require invoking the equivalent uv commands
# directly or using a POSIX-compatible shell override.
# =============================================================

SHELL        := pwsh.exe
.SHELLFLAGS  := -NoProfile -Command

.DEFAULT_GOAL := help
.PHONY: help install install-dev setup-hooks setup-skills lint format type-check test test-cov \
        test-pyqt6 publish docs docs-serve docs-deploy clean gallery

UV := uv

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

install:
	$(UV) sync --no-dev

install-dev:
	$(UV) sync --extra dev

setup-hooks:
	$(UV) run --extra dev pre-commit install --install-hooks

setup-skills:
	$(UV) run python skills/setup.py

# ---------------------------------------------------------------------------
# Quality
# ---------------------------------------------------------------------------

lint:
	$(UV) run --extra dev ruff check .

format:
	$(UV) run --extra dev ruff format .
	$(UV) run --extra dev ruff check --fix .

type-check:
	$(UV) run --extra dev ty check

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

test:
	$(UV) run --extra dev pytest

test-cov:
	$(UV) run --extra dev pytest --cov=qtshadcn --cov-report=term-missing --cov-report=html

test-pyqt6:
ifeq ($(OS),Windows_NT)
	$$env:QT_API='pyqt6'; $(UV) run --extra dev pytest
else
	QT_API=pyqt6 $(UV) run --extra dev pytest
endif

# ---------------------------------------------------------------------------
# Build & Release
# ---------------------------------------------------------------------------

publish:
	@$(UV) run python -c "print('Default releases publish to PyPI through GitHub Actions Trusted Publishing. Push a vMAJOR.MINOR.PATCH tag and use the pypi environment. Manual fallback: uv run --extra dev twine upload dist/*')"

# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------

docs:
	$(UV) run --extra dev mkdocs build --strict

docs-serve:
	$(UV) run --extra dev mkdocs serve

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	$(UV) run python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['dist','site','htmlcov','.pytest_cache','.ruff_cache']]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"

# ---------------------------------------------------------------------------
# Examples
# ---------------------------------------------------------------------------

gallery:
	$(UV) run python examples/gallery/main.py

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help:
	@$(UV) run python -c "targets=[('install','Install production dependencies only'),('install-dev','Install all dev dependencies'),('setup-hooks','Install pre-commit git hooks'),('setup-skills','Configure AI assistant skills for this repo'),('lint','Run ruff linter (check only)'),('format','Auto-format and fix lint issues with ruff'),('type-check','Run ty type checker'),('test','Run test suite'),('test-cov','Run tests with coverage report'),('test-pyqt6','Run tests with PyQt6 binding'),('publish','Show PyPI Trusted Publishing guidance'),('docs','Build static documentation site'),('docs-serve','Serve docs locally at http://127.0.0.1:8000'),('docs-deploy','Deploy docs to the docs branch (GitHub Pages)'),('gallery','Run the widget gallery example'),('clean','Remove build artifacts and caches')]; print('\nUsage: make <target>\n'); [print(f'  {t:<16} {d}') for t,d in targets]; print()"
