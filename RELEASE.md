# Release Guide

This guide is for maintainers who publish new QtShadcn releases.

---

## Distribution

Python distributions are published to [PyPI](https://pypi.org/project/qtshadcn/). GitHub Releases are used for release notes and tags only; wheel and source distribution files should not be attached there once PyPI publishing is active.

---

## PyPI Trusted Publishing

Configure PyPI Trusted Publishing before the first release:

| PyPI field | Value |
| --- | --- |
| Project | `qtshadcn` |
| Owner | `BugCodeX` |
| Repository | `QtShadcn` |
| Workflow | `publish-pypi.yml` |
| Environment | `pypi` |

---

## Release Checklist

1. Confirm the version in `pyproject.toml` matches the next semver release.
2. Push a tag named `vMAJOR.MINOR.PATCH` for future releases.
3. Let `.github/workflows/publish-pypi.yml` build and publish the wheel and sdist to PyPI.
4. For an already-pushed tag such as `v0.0.6`, run the workflow manually from GitHub Actions after Trusted Publishing is configured.
5. Use GitHub Releases for notes and tags, not `.whl` or `.tar.gz` assets.

Once the PyPI publish succeeds for the current release, remove any existing wheel and source distribution assets from earlier GitHub Releases.

---

## Manual Fallback

Local Twine upload should be treated as an explicit fallback only, not the default release path:

```bash
make build
uv run --extra dev twine upload dist/*
```
