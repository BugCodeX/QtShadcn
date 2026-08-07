# QtShadcn v0.0.17

## What's New

- Added QSpinBox and QDoubleSpinBox styling support with themed step buttons and validation states.

## Fixes

- Installed `mkdocs-material` into the Read the Docs virtualenv to restore documentation builds.

## Verification

```bash
pip install qtshadcn==0.0.17
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```

# QtShadcn v0.0.16

## What's New

- Added an AI assistant skill management system for project-specific skills.
- Added a richer gallery overview page with component navigation.
- Added a gallery logo, copy XML button, and wider sidebar.
- Redesigned the gallery theme editor with tabs and color rows.

## Documentation

- Migrated documentation hosting to Read the Docs.
- Added `skills/README.md` with setup, usage, and authoring guidance.
- Restructured README and added `CONTRIBUTING.md` and `RELEASE.md` guides.
- Added logo assets for docs and README.
- Updated `AGENTS.md` with the current project structure.
- Updated README with logo and shields badges.
- Removed `release.md` and updated roadmap navigation.

## Verification

```bash
pip install qtshadcn==0.0.16
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
```
