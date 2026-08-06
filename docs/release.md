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

# QtShadcn v0.0.12

## What's New

- `QProgressBar` styling now matches the shadcn/ui Progress component: a thin 4px track with a rounded primary indicator.

## Fixes

- Fixed QProgressBar default styling so the track is thin and the text is no longer rendered inside the bar.
- Fixed the gallery page to show labels and percentages outside the progress bar, matching shadcn layout.

## Verification

```bash
pip install qtshadcn==0.0.12
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.13

## What's New

- Added `QSlider` styling with shadcn/ui Slider semantics, including horizontal, vertical, hover, focus, and disabled states.
- Added a `QSlider` gallery page demonstrating horizontal, vertical, and disabled slider variants.

## Notes

- The focus ring is rendered via `outline`, which is best-effort across Qt platforms.
- Multi-thumb range sliders are not supported by native `QSlider` and remain out of scope.

## Verification

```bash
pip install qtshadcn==0.0.13
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.15

## What's New

- `QSlider` thumb is now rendered as a generated SVG circle, producing a perfect circle regardless of the theme radius.
- The `QSlider` thumb fill matches the primary color of the filled track for a cohesive shadcn/ui look.
- Expanded the `QSlider` gallery page with horizontal, vertical, tick, disabled, and live-value variants.

## Changes

- Refactored base widget styles for `QPushButton`, `QToolButton`, `QLineEdit`, `QTextEdit`, `QComboBox`, and `QCheckBox` for cleaner, more compact QSS output.
- Increased the dark-mode `spacing` token to `8px` for more open dark layouts.

## Verification

```bash
pip install qtshadcn==0.0.15
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.14

## Fixes

- Fixed `QSlider` handle rendering to be a perfect circle using a token-derived `border-radius` and margin.

## Verification

```bash
pip install qtshadcn==0.0.14
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```
