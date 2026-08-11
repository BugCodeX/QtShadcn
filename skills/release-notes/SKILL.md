---
name: release-notes
description: "Trigger: release, release notes, changelog, tag, version. Run the QtShadcn release process: draft notes, verify version, create tag and GitHub Release."
license: Apache-2.0
metadata:
  author: "BugCodeX"
  version: "1.1"
  category: project_specific
  scope: [root]
  auto_invoke:
    - "Creating or updating release notes"
    - "Generating a changelog or version tag"
    - "Preparing a QtShadcn release"
---

## Activation Contract

Apply this skill when preparing, drafting, or publishing a QtShadcn version release.

## Hard Rules

- Read commits since the previous tag: `git log --oneline <prev>...<next>`.
- Group commits by conventional type — never dump a raw commit list.
- Omit `chore` and `ci` from user-facing sections unless they affect the public API.
- Use plain, clear language — this is read by library consumers, not contributors.
- **Omit empty sections entirely** — never write "No fixes in this release" or similar.
- Always include a Verification section with the commands to validate the release.
- Version format: `vMAJOR.MINOR.PATCH` (semver).
- NEVER create a tag or GitHub Release without explicit user approval.

## Decision Gates

| Situation | Action |
| --- | --- |
| User only asked for draft notes | Generate notes; do not create tag or release. |
| User asked to publish the release | Pause and request explicit approval before `git tag` or `gh release create`. |
| README.md or docs are stale for this release | Update them in a separate commit before the release tag when possible. |

## Execution Steps

1. Read commits since the previous tag and group them by conventional type.
2. Check whether `README.md` or docs need updating for this release. If so, update them in a separate commit before the release tag when possible.
3. Verify `pyproject.toml` version matches the intended tag (e.g., `0.0.17` for `v0.0.17`) and that `qtshadcn/__init__.py` hardcodes the same version in `__version__`.
4. Pause for explicit user approval before creating the tag or release.
5. Create an annotated local tag: `git tag -a vX.Y.Z -m "QtShadcn vX.Y.Z"`.
6. Push the relevant branch and tag: `git push origin <branch>` then `git push origin vX.Y.Z`.
7. Update `CHANGELOG.md` by prepending a new section for `vX.Y.Z` with the same content used for the release notes.
8. Create the GitHub Release page: `gh release create vX.Y.Z --title "QtShadcn vX.Y.Z" --notes-file <file>`.
8. Always include the Verification section in the release notes.

## Output Format

```markdown
# QtShadcn vX.Y.Z

## What's New
<!-- feat commits: new capabilities the user gains -->
- Short description of the feature

## Changes
<!-- refactor, perf, style, build commits with user impact -->
- Short description of the change

## Fixes
<!-- fix commits -->
- Short description of the fix

## Verification
<!-- always include — commands to validate this release works -->
\`\`\`bash
pip install qtshadcn==X.Y.Z
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
\`\`\`
```

## Section Rules

| Section | Include | Omit |
| --- | --- | --- |
| What's New | `feat` commits | Internal refactors with no API change |
| Changes | `refactor`, `perf`, `style`, `build` with user impact | Pure internal restructuring |
| Fixes | `fix` commits | Typo fixes in comments or docs |
| Verification | Always present | Nothing — this section is mandatory |

## Examples

```markdown
# QtShadcn v0.0.3

## What's New
- Added `QToolButton` styling support

## Verification
\`\`\`bash
pip install qtshadcn==0.0.3
python -c "import qtshadcn; print(qtshadcn.__version__)"
make test
\`\`\`
```

## Anti-patterns

```markdown
# BAD — raw commit dump
- 1fe7498 chore: bump version to 0.0.3
- 0aeeaac feat: add QToolButton styling support

# BAD — empty section filler
## Fixes
- No fixes in this release

# BAD — missing Verification section
## Fixes
- resolve rendering bug
(end of notes)

# BAD — vague entries
- Various improvements
- Bug fixes
```
