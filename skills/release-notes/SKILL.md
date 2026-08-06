---
name: release-notes
description: "Trigger: release, release notes, changelog, tag, version, what's new. Generate structured release notes for QtShadcn versions."
license: Apache-2.0
metadata:
  author: "BugCodeX"
  version: "1.0"
  category: project_specific
  scope: [root]
  auto_invoke:
    - "Creating or updating release notes"
    - "Generating a changelog or version tag"
    - "Preparing a QtShadcn release"
---

## Activation Contract

Apply this skill when creating or updating release notes for any QtShadcn version tag.

## Hard Rules

- Read commits since the previous tag: `git log --oneline <prev>...<next>`
- Group commits by conventional type — never dump a raw commit list
- Omit `chore` and `ci` from user-facing sections unless they affect the public API
- Use plain, clear language — this is read by library consumers, not contributors
- **Omit empty sections entirely** — never write "No fixes in this release" or similar
- Always include a Verification section with the commands to validate the release
- Version format: `vMAJOR.MINOR.PATCH` (semver)

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
| --------- | --------- | ------ |
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
