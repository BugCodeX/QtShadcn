---
name: commit-hygiene
description: "Trigger: commit, git commit, conventional commit, branch cleanup, commit message. Enforce conventional commits and clean history for QtShadcn."
license: Apache-2.0
metadata:
  author: BugCodeX
  version: "1.0"
---

# Activation Contract

Apply this skill on any commit creation, commit message review, or branch cleanup in the QtShadcn project.

## Hard Rules

- NEVER add `Co-Authored-By` or any AI attribution trailers
- One logical change per commit — no "add X and fix Y and update docs"
- Use imperative mood: "add" not "added", "fix" not "fixed"
- Keep subject line ≤ 72 characters
- Reference issue numbers when relevant: `feat: add border-radius scale to tokens (#12)`
- Add a body separated by a blank line when the commit needs explanation
- Use `type!: description` for breaking changes — the `!` signals a semver MAJOR bump

## Format

```text
type: description
```

Validated by regex:

```text
^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)!?: .+
```

## Valid Types

| Type | Use For |
| ------ | --------- |
| feat | New feature or behavior |
| fix | Bug fix |
| docs | Documentation only |
| chore | Maintenance, dependencies, tooling |
| refactor | Restructuring without behavior change |
| test | Adding or fixing tests |
| ci | CI/CD pipeline changes |
| style | Formatting, whitespace, no logic change |
| perf | Performance improvement |
| build | Build system, Makefile, pyproject changes |
| revert | Reverting a previous commit |

## Examples

```text
feat: add border-radius scale to design tokens
feat: add dark mode theme variant
feat!: rename apply_theme() to load_theme() — breaking API change
fix: handle missing token fallback in QSS output
fix: resolve widget rendering on high-DPI displays
refactor: extract token resolver to separate method
test: add unit tests for missing token fallback
docs: document token naming convention
chore: update uv.lock after dependency bump
build: add coverage target to Makefile
```

## Anti-patterns

```text
# BAD — vague
update stuff

# BAD — AI attribution
feat: add feature

Co-Authored-By: Claude <claude@anthropic.com>

# BAD — multiple concerns
feat: add token scale and fix parser bug and update docs

# BAD — past tense
fix: fixed the missing token fallback
```
