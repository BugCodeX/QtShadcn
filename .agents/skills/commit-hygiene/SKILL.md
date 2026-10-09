---
name: commit-hygiene
description: "Trigger: commit, git commit, conventional commit, branch cleanup. Enforce conventional commits and publishing approval for QtShadcn."
license: Apache-2.0
metadata:
  author: "BugCodeX"
  version: "1.1"
  category: generic
  scope: [root]
  auto_invoke:
    - "Creating or amending a git commit"
    - "Writing a conventional commit message"
    - "Cleaning up or reorganizing branches"
    - "Pushing commits, tags, or GitHub releases"
---

## Activation Contract

Apply this skill on any commit creation, commit message review, branch cleanup, or publishing operation in the QtShadcn project.

## Hard Rules

- NEVER add `Co-Authored-By` or any AI attribution trailers.
- One logical change per commit — no "add X and fix Y and update docs".
- Use imperative mood: "add" not "added", "fix" not "fixed".
- Keep subject line ≤ 72 characters.
- Reference issue numbers when relevant: `feat: add border-radius scale to tokens (#12)`.
- Add a body separated by a blank line when the commit needs explanation.
- Use `type!: description` for breaking changes — the `!` signals a semver MAJOR bump.
- NEVER run `git push`, `git tag`, or `gh release create` without explicit user approval.

## Decision Gates

| Situation | Action |
| --- | --- |
| Commit only touches local repo | Apply conventional-commit rules and proceed. |
| Operation publishes code (push, tag, release, `gh release create`) | STOP. Ask the user for explicit approval before running any command. |

## Execution Steps

1. Validate the commit message against the conventional-commit regex.
2. If the message references multiple unrelated concerns, split the change.
3. Before any publishing command, pause and request explicit user approval.
4. Return the final commit message or the exact commands to run.

## Output Contract

Return:

- The validated commit message, or
- The exact commands to execute and the approval status when publishing.

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
| --- | --- |
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
feat!: remove deprecated apply_theme()/get_theme() wrappers
fix: handle missing token fallback in QSS output
refactor: extract token resolver to separate method
docs: document token naming convention
chore: update uv.lock after dependency bump
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
