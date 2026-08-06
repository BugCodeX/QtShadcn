#!/usr/bin/env python3
"""Sync skill metadata to AGENTS.md Available Skills sections.

This script reads the YAML frontmatter of every ``skills/*/SKILL.md`` file,
extracts ``metadata.category``, ``metadata.scope``, ``metadata.auto_invoke``,
and the skill ``description``, then regenerates the complete ``## Available
Skills`` section in the AGENTS.md files referenced by the configured scopes.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import typer
import yaml

APP_NAME = "skill-sync"

# Scope mapping: only root is currently used, but the dict is kept extensible
# for future scopes (e.g., "ui", "api", "docs").
SCOPE_TO_AGENTS: dict[str, str] = {
    "root": "AGENTS.md",
}

AVAILABLE_SKILLS_HEADER = "## Available Skills"
AVAILABLE_SKILLS_INTRO = "Use these skills for detailed patterns on-demand:"

GENERIC_SKILLS_HEADER = "### Generic Skills (Any Project)"
PROJECT_SPECIFIC_SKILLS_HEADER = "### QtShadcn Specific Skills"
AUTO_INVOKE_HEADER = "### Auto-invoke Skills"
AUTO_INVOKE_INTRO = (
    "When performing these actions, ALWAYS invoke the corresponding skill FIRST:"
)

app = typer.Typer(help="Sync skill metadata to AGENTS.md Available Skills sections.")


@dataclass
class SkillInfo:
    """Parsed skill metadata used to build the Available Skills section."""

    name: str
    description: str
    category: str
    scopes: list[str]
    actions: list[str]


@dataclass
class ScopeContent:
    """Tables generated for a single AGENTS.md scope."""

    generic_rows: list[tuple[str, str, str]]
    project_rows: list[tuple[str, str, str]]
    auto_invoke_rows: list[tuple[str, str]]


class SkillCategory:
    """Valid skill categories."""

    GENERIC = "generic"
    PROJECT_SPECIFIC = "project_specific"

    DEFAULT = GENERIC


class CategoryName:
    """Display names for category sections."""

    GENERIC = "Generic Skills (Any Project)"
    PROJECT_SPECIFIC = "QtShadcn Specific Skills"


def _find_repo_root() -> Path:
    """Return the repository root from the script location."""
    script_dir = Path(__file__).resolve().parent
    # assets/ -> skill-sync/ -> skills/ -> repo root
    return script_dir.parent.parent.parent


def _load_frontmatter(path: Path) -> dict[str, Any]:
    """Parse the YAML frontmatter from a SKILL.md file.

    Returns an empty dict if the file has no valid frontmatter.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}


def _normalize_string_or_list(value: Any) -> list[str]:
    """Convert a scalar string or a list of strings into a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None and str(item)]
    return []


def _sanitize_description(value: str) -> str:
    """Normalize a skill description for use in a markdown table cell.

    YAML frontmatter may contain newlines (e.g., folded blocks). Collapse them
    into a single space so the table row renders on one line.
    """
    return " ".join(line.strip() for line in value.replace("\r", "\n").split("\n")).strip()


def _collect_skills(repo_root: Path) -> list[SkillInfo]:
    """Parse all skills and return their metadata.

    Skills are sorted by name for deterministic output.
    """
    skills_dir = repo_root / "skills"
    skills: list[SkillInfo] = []

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        frontmatter = _load_frontmatter(skill_file)
        metadata = frontmatter.get("metadata") or {}

        skill_name = frontmatter.get("name") or skill_file.parent.name
        description = _sanitize_description(frontmatter.get("description") or "")
        category = str(metadata.get("category", SkillCategory.DEFAULT)).lower()
        scopes = _normalize_string_or_list(metadata.get("scope"))
        actions = _normalize_string_or_list(metadata.get("auto_invoke"))

        skills.append(
            SkillInfo(
                name=skill_name,
                description=description,
                category=category,
                scopes=scopes,
                actions=actions,
            )
        )

    skills.sort(key=lambda skill: skill.name.lower())
    return skills


def _build_skills_table(
    header: str,
    rows: list[tuple[str, str, str]],
) -> list[str]:
    """Build a markdown table for generic or project-specific skills."""
    lines = [
        header,
        "",
        "| Skill | Description | URL |",
        "|-------|-------------|-----|",
    ]

    for skill_name, description, url in rows:
        lines.append(f"| `{skill_name}` | {description} | {url} |")

    return lines


def _build_auto_invoke_table(
    header: str,
    intro: str,
    rows: list[tuple[str, str]],
) -> list[str]:
    """Build a markdown table for auto-invoke skills."""
    lines = [
        header,
        "",
        intro,
        "",
        "| Action | Skill |",
        "|--------|-------|",
    ]

    for action, skill_name in rows:
        lines.append(f"| {action} | `{skill_name}` |")

    return lines


def _build_available_skills_section(content: ScopeContent) -> str:
    """Build the complete ``## Available Skills`` markdown section."""
    lines: list[str] = [
        AVAILABLE_SKILLS_HEADER,
        "",
        AVAILABLE_SKILLS_INTRO,
        "",
    ]

    lines.extend(
        _build_skills_table(
            GENERIC_SKILLS_HEADER,
            content.generic_rows,
        )
    )
    lines.append("")

    lines.extend(
        _build_skills_table(
            PROJECT_SPECIFIC_SKILLS_HEADER,
            content.project_rows,
        )
    )
    lines.append("")

    lines.extend(
        _build_auto_invoke_table(
            AUTO_INVOKE_HEADER,
            AUTO_INVOKE_INTRO,
            content.auto_invoke_rows,
        )
    )

    return "\n".join(lines)


def _find_available_skills_span(text: str) -> tuple[int, int] | None:
    """Find the start and end indices of the ``## Available Skills`` section.

    The span ends just before the next top-level ``## `` heading, or at the end
    of the file if no such heading is found.
    """
    start = text.find(f"\n{AVAILABLE_SKILLS_HEADER}")
    if start == -1:
        start = text.find(AVAILABLE_SKILLS_HEADER)
    if start == -1:
        return None

    search_start = start + len(AVAILABLE_SKILLS_HEADER)
    next_heading = text.find("\n## ", search_start)
    end = len(text) if next_heading == -1 else next_heading + 1

    return start, end


def _update_agents(
    agents_path: Path,
    section: str,
    dry_run: bool,
    scope: str,
) -> bool:
    """Write the complete Available Skills section into the AGENTS.md file.

    If the section already exists it is replaced; otherwise it is appended to
    the end of the file.

    Returns ``True`` if the file was (or would be) modified.
    """
    if not agents_path.exists():
        typer.echo(f"Warning: No AGENTS.md found for scope '{scope}'", err=True)
        return False

    text = agents_path.read_text(encoding="utf-8")
    span = _find_available_skills_span(text)

    if span is not None:
        start, end = span
        new_text = text[:start] + section + text[end:]
        operation = "Updated"
    else:
        # Append the section at the end of the file.
        if not text.endswith("\n"):
            text += "\n"
        new_text = text + "\n" + section + "\n"
        operation = "Inserted"

    # Normalize to a single trailing newline for clean diffs.
    new_text = new_text.rstrip("\n") + "\n"

    if new_text == text:
        typer.echo(f"  {scope}: No changes needed")
        return False

    if dry_run:
        typer.echo(f"  [DRY RUN] {operation} section in {agents_path}:")
        typer.echo(section)
    else:
        agents_path.write_text(new_text, encoding="utf-8")
        typer.echo(f"  {operation} Available Skills section in {agents_path}")

    return True


def _group_by_scope(skills: list[SkillInfo]) -> dict[str, ScopeContent]:
    """Group skills by scope, preparing the tables for each AGENTS.md.

    Auto-invoke rows are sorted by action, then skill name. Generic and
    project-specific skill rows are sorted by skill name.
    """
    content_by_scope: dict[str, ScopeContent] = {}

    for skill in skills:
        for scope in skill.scopes:
            if scope not in SCOPE_TO_AGENTS:
                continue
            if scope not in content_by_scope:
                content_by_scope[scope] = ScopeContent(
                    generic_rows=[],
                    project_rows=[],
                    auto_invoke_rows=[],
                )

            content = content_by_scope[scope]
            url = f"[SKILL.md](skills/{skill.name}/SKILL.md)"
            row = (skill.name, skill.description, url)

            if skill.category == SkillCategory.PROJECT_SPECIFIC:
                content.project_rows.append(row)
            else:
                content.generic_rows.append(row)

            for action in skill.actions:
                content.auto_invoke_rows.append((action, skill.name))

    for content in content_by_scope.values():
        content.generic_rows.sort(key=lambda row: row[0].lower())
        content.project_rows.sort(key=lambda row: row[0].lower())
        content.auto_invoke_rows.sort(key=lambda row: (row[0].lower(), row[1].lower()))

    return content_by_scope


def _find_missing_metadata(repo_root: Path) -> list[tuple[str, str, str]]:
    """Return a list of skills missing ``scope`` or ``auto_invoke`` metadata.

    Each tuple contains ``(skill_name, missing_scope, missing_auto_invoke)``
    where the missing fields are empty strings when present.
    """
    skills = _collect_skills(repo_root)
    missing: list[tuple[str, str, str]] = []

    for skill in skills:
        if not skill.scopes or not skill.actions:
            missing_scope = "" if skill.scopes else "scope"
            missing_auto = "" if skill.actions else "auto_invoke"
            missing.append((skill.name, missing_scope, missing_auto))

    return missing


@app.command()
def sync(
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Show what would change without modifying files.",
    ),
    scope: str | None = typer.Option(
        None,
        "--scope",
        help="Only sync the specified scope. If omitted, all scopes are synced.",
    ),
) -> None:
    """Sync skill metadata to AGENTS.md Available Skills sections.

    When called without --scope, every scope that has at least one skill with
    metadata is synced to its configured AGENTS.md file.
    """
    repo_root = _find_repo_root()
    skills = _collect_skills(repo_root)
    content_by_scope = _group_by_scope(skills)

    if scope is not None and scope not in SCOPE_TO_AGENTS:
        typer.echo(f"Unknown scope: {scope}", err=True)
        raise typer.Exit(code=1)

    scopes_to_sync = [scope] if scope else list(content_by_scope.keys())

    if not scopes_to_sync:
        typer.echo("No skills with scope metadata found.")
        raise typer.Exit(code=0)

    typer.echo(f"{APP_NAME} - Updating AGENTS.md Available Skills sections")
    typer.echo("=" * 56)
    typer.echo("")

    for scope_name in scopes_to_sync:
        relative_path = SCOPE_TO_AGENTS[scope_name]
        agents_path = repo_root / relative_path
        content = content_by_scope[scope_name]
        section = _build_available_skills_section(content)
        _update_agents(agents_path, section, dry_run, scope_name)

    typer.echo("")
    typer.echo("Done!")
    typer.echo("")

    typer.echo("Skills missing sync metadata:")
    missing = _find_missing_metadata(repo_root)
    if not missing:
        typer.echo("  All skills have sync metadata")
    else:
        for skill_name, missing_scope, missing_auto in missing:
            parts = [label for label in (missing_scope, missing_auto) if label]
            typer.echo(f"  {skill_name} - missing: {', '.join(parts)}")


if __name__ == "__main__":
    app()
