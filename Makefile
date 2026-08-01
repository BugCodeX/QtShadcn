# =============================================================
# Makefile — qtshadcn
# Requires: make, uv, PowerShell (pwsh)
# =============================================================

SHELL        := pwsh.exe
.SHELLFLAGS  := -NoProfile -Command

.DEFAULT_GOAL := help
.PHONY: help install install-dev lint format type-check test test-cov \
        build publish docs docs-serve clean

UV := uv

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

install:
	$(UV) sync --no-dev

install-dev:
	$(UV) sync --extra dev

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

# ---------------------------------------------------------------------------
# Build & Publish
# ---------------------------------------------------------------------------

build:
	$(UV) run --extra dev python -m build

publish: build
	$(UV) run --extra dev twine upload dist/*

# ---------------------------------------------------------------------------
# Documentation
# ---------------------------------------------------------------------------

docs:
	$(UV) run --extra dev mkdocs build --strict

docs-serve:
	$(UV) run --extra dev mkdocs serve

docs-deploy:
	$(UV) run --extra dev mkdocs gh-deploy --remote-branch docs --force

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean:
	$(UV) run python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in ['dist','site','htmlcov','.pytest_cache','.ruff_cache']]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('*.egg-info')]"

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

help:
	@$(UV) run python -c "\
targets = [\
  ('install',      'Install production dependencies only'),\
  ('install-dev',  'Install all dev dependencies'),\
  ('lint',         'Run ruff linter (check only)'),\
  ('format',       'Auto-format and fix lint issues with ruff'),\
  ('type-check',   'Run ty type checker'),\
  ('test',         'Run test suite'),\
  ('test-cov',     'Run tests with coverage report'),\
  ('build',        'Build wheel and sdist distributions'),\
  ('publish',      'Build and upload to PyPI via twine'),\
  ('docs',         'Build static documentation site'),\
  ('docs-serve',   'Serve docs locally at http://127.0.0.1:8000'),\
  ('docs-deploy',  'Deploy docs to the docs branch (GitHub Pages)'),\
  ('clean',        'Remove build artifacts and caches'),\
];\
print('\nUsage: make <target>\n');\
[print(f'  {t:<16} {d}') for t, d in targets];\
print()\
"
