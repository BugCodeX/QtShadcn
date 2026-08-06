# Release Guide

QtShadcn uses PyPI as the public package distribution channel. GitHub Releases are for release notes and tags; package artifacts are built by GitHub Actions and published to PyPI.

## One-Time PyPI Setup

Configure PyPI Trusted Publishing before the first PyPI release.

| PyPI field | Value |
| --- | --- |
| Project | `qtshadcn` |
| Owner | `BugCodeX` |
| Repository | `QtShadcn` |
| Workflow | `publish-pypi.yml` |
| Environment | `pypi` |

The workflow uses GitHub Actions OIDC, so no PyPI API token should be stored in repository secrets for the default release path.

## Release Steps

1. Confirm `pyproject.toml` contains the version you want to publish.
2. Push a tag named `vMAJOR.MINOR.PATCH`, for example `v0.0.6`, for future releases.
3. Inspect the `python-package-distributions` workflow artifact if needed.
4. Confirm the `pypi` environment approval and PyPI publish completed successfully.
5. Create or update the GitHub Release with notes only.

For an already-pushed tag such as `v0.0.6`, run `Publish to PyPI` manually from GitHub Actions after Trusted Publishing is configured. The workflow also supports manual dispatch for this first PyPI publication.

Do not attach `.whl` or `.tar.gz` files to GitHub Releases once PyPI publishing is active.

Once the PyPI publish succeeds for the current release, any existing wheel and source distribution assets from earlier releases may be removed from GitHub Releases.

# QtShadcn v0.0.11

## What's New

- Refactored gallery into a modular package with a theme editor.
- Added `QProgressBar` styling with shadcn progress semantics, including determinate, indeterminate, thin, and disabled states.
- Added a `QProgressBar` gallery page demonstrating all supported states.

## Verification

```bash
pip install qtshadcn==0.0.11
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

## Fallback Only

Use Twine only if Trusted Publishing is unavailable and you intentionally choose a manual fallback:

```bash
make build
uv run --extra dev twine upload dist/*
```
