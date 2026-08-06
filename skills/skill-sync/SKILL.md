---
name: skill-sync
description: >
  Syncs skill metadata to AGENTS.md Available Skills sections.
  Trigger: When updating skill metadata (metadata.scope/metadata.auto_invoke), regenerating Available Skills tables, or running ./skills/skill-sync/assets/sync.py (including --dry-run/--scope).
license: Apache-2.0
metadata:
  author: "BugCodeX"
  version: "1.0"
  category: project_specific
  scope: [root]
  auto_invoke:
    - "After creating/modifying a skill"
    - "Regenerate AGENTS.md Available Skills tables (sync.py)"
    - "Troubleshoot why a skill is missing from AGENTS.md"
allowed-tools: Read, Edit, Write, Glob, Grep, Bash
---

## Purpose

Keeps the ``AGENTS.md`` ``## Available Skills`` section in sync with skill metadata. When you create or modify a skill, run the sync script to regenerate the skill tables in the root ``AGENTS.md``.

## Required Skill Metadata

Each skill that should appear in the Available Skills section needs these fields in ``metadata``:

- ``category``: ``generic`` or ``project_specific``. Defaults to ``generic`` when omitted.
- ``scope``: list of scopes where the skill should be registered (e.g., ``[root]``).
- ``auto_invoke``: list of actions that trigger the skill automatically.

``auto_invoke`` can be either a single string **or** a list of actions:

```yaml
metadata:
  author: BugCodeX
  version: "1.0"
  category: generic                 # generic | project_specific
  scope: [root]                       # Currently only root is supported

  # Option A: single action
  auto_invoke: "Writing pytest tests"

  # Option B: multiple actions
  # auto_invoke:
  #   - "Writing pytest tests"
  #   - "Reviewing pytest coverage"
```

### Scope Values

| Scope | Updates |
| ------- | --------- |
| `root` | `AGENTS.md` (repo root) |

The mapping is extensible; future scopes (e.g., `ui`, `api`, `docs`) can be added by updating the `SCOPE_TO_AGENTS` dict in `assets/sync.py`.

Skills can have multiple scopes: `scope: [root]`

### Category Values

| Category | Table |
| ---------- | ------- |
| `generic` | ``### Generic Skills (Any Project)`` |
| `project_specific` | ``### QtShadcn Specific Skills`` |

When ``category`` is omitted, the skill defaults to ``generic``.

---

## Usage

### After Creating/Modifying a Skill

```bash
# Sync all scopes that have skills registered
python skills/skill-sync/assets/sync.py

# Sync only a specific scope
python skills/skill-sync/assets/sync.py --scope root

# Dry run (show what would change)
python skills/skill-sync/assets/sync.py --dry-run
```

Or use the POSIX wrapper:

```bash
./skills/skill-sync/assets/sync.sh
```

### What It Does

1. Reads all `skills/*/SKILL.md` files
2. Extracts `metadata.category`, `metadata.scope`, and `metadata.auto_invoke`
3. Groups skills by `scope` and builds the complete ``## Available Skills`` section for each scope:
   - ``### Generic Skills (Any Project)`` table
   - ``### QtShadcn Specific Skills`` table
   - ``### Auto-invoke Skills`` table
4. Replaces the entire ``## Available Skills`` section in each matching `AGENTS.md`

---

## Example

Given this skill metadata:

```yaml
# skills/pytest/SKILL.md
metadata:
  author: BugCodeX
  version: "1.0"
  category: generic
  scope: [root]
  auto_invoke: "Writing pytest tests"
```

The sync script generates in `AGENTS.md`:

```markdown
## Available Skills

Use these skills for detailed patterns on-demand:

### Generic Skills (Any Project)

| Skill | Description | URL |
|-------|-------------|-----|
| `pytest` | Trigger: pytest tests, pytest coverage, fixtures, mocking, markers, parametrize, test discovery. Write idiomatic Python pytest tests and test helpers. | [SKILL.md](skills/pytest/SKILL.md) |

### QtShadcn Specific Skills

| Skill | Description | URL |
|-------|-------------|-----|
| ... | ... | ... |

### Auto-invoke Skills

When performing these actions, ALWAYS invoke the corresponding skill FIRST:

| Action | Skill |
|--------|-------|
| Writing pytest tests | `pytest` |
```

---

## Commands

```bash
# Sync all scopes that have registered skills
python skills/skill-sync/assets/sync.py

# Dry run (show what would change for all scopes)
python skills/skill-sync/assets/sync.py --dry-run

# Sync only a specific scope
python skills/skill-sync/assets/sync.py --scope root
```

---

## Checklist After Modifying Skills

- [ ] Added `metadata.category` to new/modified skill (`generic` or `project_specific`)
- [ ] Added `metadata.scope` to new/modified skill
- [ ] Added `metadata.auto_invoke` with action description
- [ ] Ran `python skills/skill-sync/assets/sync.py`
- [ ] Verified `AGENTS.md` was updated correctly
