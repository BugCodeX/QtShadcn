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

For an already-pushed tag such as `v0.0.5`, run `Publish to PyPI` manually from GitHub Actions after Trusted Publishing is configured. The workflow also supports manual dispatch for this first PyPI publication.

Do not attach `.whl` or `.tar.gz` files to GitHub Releases once PyPI publishing is active.

If the PyPI publish succeeds for `v0.0.5`, the existing wheel and source distribution assets can be removed from GitHub Releases.

## Fallback Only

Use Twine only if Trusted Publishing is unavailable and you intentionally choose a manual fallback:

```bash
make build
uv run --extra dev twine upload dist/*
```
