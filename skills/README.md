# AI Agent Skills

This directory contains **Agent Skills** following the [Agent Skills open standard](https://agentskills.io). Skills provide domain-specific patterns, conventions, and guardrails that help AI coding assistants (Claude Code, OpenCode, Cursor, etc.) understand project-specific requirements for QtShadcn.

## What Are Skills?

[Agent Skills](https://agentskills.io) is an open standard format for extending AI agent capabilities with specialized knowledge. Originally developed by Anthropic and released as an open standard, it is now adopted by multiple agent products.

Skills teach AI assistants how to perform specific tasks. When an AI loads a skill, it gains context about:

- Critical rules (what to always/never do)
- Code patterns and conventions
- Project-specific workflows
- References to detailed documentation

## Setup

Run the setup script to configure skills for all supported AI coding assistants:

```bash
make setup-skills
```

Or directly with Python:

```bash
uv run python skills/setup.py
```

This creates symlinks or directory junctions so each tool finds skills in its expected location:

| Tool | Created by setup |
|------|------------------|
| Claude Code | `.claude/skills/` and `CLAUDE.md` |
| Gemini CLI | `.gemini/skills/` and `GEMINI.md` |
| Codex (OpenAI) | `.codex/skills/` (uses `AGENTS.md` natively) |
| GitHub Copilot | `.github/skills/` and `.github/copilot-instructions.md` |
| OpenCode | `.opencode/skills/` (uses `AGENTS.md` natively) |
| Native / Antigravity | `.agents/skills/` (uses `AGENTS.md` natively) |
| Cursor | `.cursor/skills/` (uses `AGENTS.md` natively) |

After running setup, restart your AI coding assistant to load the skills.

## How to Use Skills

Skills are automatically discovered by the AI agent when the repository is opened in a supported assistant. To manually load a skill during a session:

```text
Read skills/{skill-name}/SKILL.md
```

## Available Skills

### Generic Skills (Any Project)

Reusable patterns for common technologies and workflows:

| Skill | Description |
|-------|-------------|
| `commit-hygiene` | Conventional commits and clean history |
| `pytest` | Python pytest patterns, fixtures, mocking, markers |
| `skill-creator` | Create new AI agent skills |
| `skill-improver` | Audit and upgrade existing skills |

### QtShadcn Specific Skills

Patterns tailored for QtShadcn development:

| Skill | Description |
|-------|-------------|
| `release-notes` | Generate structured release notes for QtShadcn versions |
| `skill-sync` | Sync skill metadata to `AGENTS.md` Available Skills sections |

## Directory Structure

```text
skills/
├── {skill-name}/
│   ├── SKILL.md              # Required - main instruction and metadata
│   ├── assets/               # Optional - templates, schemas, resources
│   ├── references/           # Optional - links to local docs
│   └── scripts/              # Optional - executable helpers
└── README.md                 # This file
```

## Why Auto-invoke Sections?

**Problem**: AI assistants do not reliably auto-invoke skills even when the `Trigger:` in the skill description matches the user's request. They treat skill suggestions as background noise and fall back to their default approach.

**Solution**: The root `AGENTS.md` contains an **Auto-invoke Skills** section that explicitly commands the AI: "When performing X action, ALWAYS invoke Y skill FIRST." This forces the AI to load the correct skill before acting.

**Automation**: Instead of manually maintaining these sections, run `skill-sync` after creating or modifying a skill:

```bash
uv run python skills/skill-sync/assets/sync.py
```

This reads `metadata.category`, `metadata.scope`, and `metadata.auto_invoke` from each `SKILL.md` and regenerates the Available Skills and Auto-invoke tables in the corresponding `AGENTS.md` files.

## Creating New Skills

Use the `skill-creator` skill for guidance:

```text
Read skills/skill-creator/SKILL.md
```

### Quick Checklist

1. Create directory: `skills/{skill-name}/`
2. Add `SKILL.md` with required frontmatter (`name`, `description`, `license`, `metadata`)
3. Add `metadata.category` (`generic` or `project_specific`)
4. Add `metadata.scope` (e.g., `[root]`)
5. Add `metadata.auto_invoke` with trigger actions
6. Keep content concise (recommended under 500 lines)
7. Reference existing docs instead of duplicating them
8. Run `uv run python skills/skill-sync/assets/sync.py` to update `AGENTS.md`

## Design Principles

- **Concise**: Only include what the AI does not already know
- **Progressive disclosure**: Point to detailed docs, do not duplicate
- **Critical rules first**: Lead with ALWAYS/NEVER patterns
- **Minimal examples**: Show patterns, not tutorials
- **Runtime instructions**: Skills are commands for the AI, not human documentation

## Resources

- [Agent Skills Standard](https://agentskills.io) - Open standard specification
- [Agent Skills GitHub](https://github.com/anthropics/skills) - Example skills
- [Claude Code Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Skill authoring guide
- [QtShadcn AGENTS.md](../AGENTS.md) - AI agent general rules and auto-invoke table
