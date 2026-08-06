#!/usr/bin/env python3
"""Set up AI skills for QtShadcn development.

Configures AI coding assistants that follow the agentskills.io standard:
- Claude Code: .claude/skills/ symlink + CLAUDE.md symlink
- Gemini CLI: .gemini/skills/ symlink + GEMINI.md symlink
- Codex (OpenAI): .codex/skills/ symlink + AGENTS.md
- GitHub Copilot: .github/skills/ symlink + .github/copilot-instructions.md symlink
- OpenCode: .opencode/skills/ directory link
- Native: .agents/skills/ directory link (uses AGENTS.md)
- Cursor: .cursor/skills/ directory link (uses AGENTS.md)
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import questionary
import typer
from rich.console import Console

app = typer.Typer(
    help="Configure AI coding assistants for QtShadcn development.",
    add_completion=False,
)
console = Console()

GITIGNORE_HEADER = "# AI Coding assistants assets"
AI_ASSISTANTS = [
    ("claude", "Claude Code", ".claude/skills/ + CLAUDE.md"),
    ("gemini", "Gemini CLI", ".gemini/skills/ + GEMINI.md"),
    ("codex", "Codex (OpenAI)", ".codex/skills/ + AGENTS.md"),
    ("copilot", "GitHub Copilot", ".github/skills/ + .github/copilot-instructions.md"),
    ("opencode", "OpenCode", ".opencode/skills/ + AGENTS.md"),
    ("native", "Native", ".agents/skills/ + AGENTS.md"),
    ("cursor", "Cursor", ".cursor/skills/ + AGENTS.md"),
]


def get_repo_root() -> Path:
    """Return the repository root (parent of the skills directory)."""
    return Path(__file__).resolve().parent.parent


def get_skills_source() -> Path:
    """Return the path to the skills source directory."""
    return Path(__file__).resolve().parent


def count_skills(source: Path) -> int:
    """Count SKILL.md files up to depth two inside the skills directory."""
    count = 0
    for path in source.rglob("SKILL.md"):
        rel = path.relative_to(source)
        if len(rel.parts) <= 2:
            count += 1
    return count


def is_windows_junction(path: Path) -> bool:
    """Return True if *path* is a Windows directory junction or reparse point."""
    if sys.platform != "win32" or not path.is_dir():
        return False
    try:
        attrs = os.lstat(path).st_file_attributes
    except (OSError, AttributeError):
        return False
    # FILE_ATTRIBUTE_REPARSE_POINT = 0x400
    return bool(attrs & 0x400)


def add_to_gitignore(repo_root: Path, pattern: str) -> None:
    """Add *pattern* to the root .gitignore if it is not already present."""
    gitignore = repo_root / ".gitignore"
    if not gitignore.exists():
        gitignore.touch()

    lines = {line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()}
    if pattern in lines:
        return

    with gitignore.open("a", encoding="utf-8") as fh:
        if GITIGNORE_HEADER not in lines:
            fh.write(f"\n\n{GITIGNORE_HEADER}\n")
        fh.write(f"{pattern}\n")

    console.print(f"[green]  [OK] Added {pattern} to .gitignore[/green]")


def backup_path(path: Path) -> Path:
    """Return a non-existing backup path with a Unix timestamp suffix."""
    timestamp = int(datetime.now().timestamp())
    candidate = path.parent / f"{path.name}.backup.{timestamp}"
    while candidate.exists():
        timestamp += 1
        candidate = path.parent / f"{path.name}.backup.{timestamp}"
    return candidate


def remove_or_backup(path: Path) -> None:
    """Remove a symlink/junction or rename a real file/directory to a backup."""
    if not path.exists() and not path.is_symlink():
        return

    if path.is_symlink():
        path.unlink()
        return

    if is_windows_junction(path):
        os.rmdir(path)
        return

    backup = backup_path(path)
    path.rename(backup)


def create_windows_junction(source: Path, target: Path) -> None:
    """Create a Windows directory junction from *target* to *source*."""
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(target), str(source)],
        check=True,
        shell=False,
    )


def create_link(
    source: Path,
    target: Path,
    *,
    is_directory: bool,
    created: set[Path] | None = None,
) -> None:
    """Create a symlink or, on Windows, a directory junction for directories.

    If *created* is provided, a target that was already created in this run is
    skipped to avoid duplicate work for shared paths.
    """
    if created is not None and target in created:
        console.print(f"[blue]  [SKIP] Already created {target}[/blue]")
        return

    remove_or_backup(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    if sys.platform == "win32" and is_directory:
        create_windows_junction(source, target)
    else:
        os.symlink(source, target, target_is_directory=is_directory)

    if created is not None:
        created.add(target)


def create_file_link(source: Path, target: Path) -> None:
    """Create a file symlink, falling back to a hardlink on Windows if needed."""
    remove_or_backup(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    try:
        os.symlink(source, target, target_is_directory=False)
    except OSError:
        if sys.platform != "win32":
            raise
        resolved = (target.parent / source).resolve()
        if not resolved.exists():
            raise
        os.link(resolved, target)


def link_agents_md(repo_root: Path, target_name: str) -> int:
    """Create *target_name* symlinks next to every AGENTS.md in the repo."""
    count = 0
    for agents_file in repo_root.rglob("AGENTS.md"):
        if ".git" in agents_file.parts or "node_modules" in agents_file.parts:
            continue

        target = agents_file.parent / target_name
        try:
            create_file_link(agents_file, target)
            count += 1
        except OSError as exc:
            console.print(f"[red]  [FAIL] Failed to link {target}: {exc}[/red]")

    console.print(f"[green]  [OK] Linked {count} AGENTS.md -> {target_name}[/green]")
    return count


def setup_claude(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure Claude Code skills and CLAUDE.md links."""
    target = repo_root / ".claude" / "skills"
    add_to_gitignore(repo_root, ".claude/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .claude/skills -> skills/[/green]")
    add_to_gitignore(repo_root, "CLAUDE.md")
    link_agents_md(repo_root, "CLAUDE.md")


def setup_gemini(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure Gemini CLI skills and GEMINI.md links."""
    target = repo_root / ".gemini" / "skills"
    add_to_gitignore(repo_root, ".gemini/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .gemini/skills -> skills/[/green]")
    add_to_gitignore(repo_root, "GEMINI.md")
    link_agents_md(repo_root, "GEMINI.md")


def setup_codex(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure Codex (OpenAI) skills. Codex uses AGENTS.md natively."""
    target = repo_root / ".codex" / "skills"
    add_to_gitignore(repo_root, ".codex/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .codex/skills -> skills/[/green]")
    console.print("[green]  [OK] Codex uses AGENTS.md natively[/green]")


def setup_copilot(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure GitHub Copilot skills and instructions via a symlink to AGENTS.md."""
    target = repo_root / ".github" / "skills"
    add_to_gitignore(repo_root, ".github/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .github/skills -> skills/[/green]")

    agents_file = repo_root / "AGENTS.md"
    if not agents_file.is_file():
        return

    target = repo_root / ".github" / "copilot-instructions.md"
    add_to_gitignore(repo_root, ".github/copilot-instructions.md")
    create_file_link(Path("../AGENTS.md"), target)
    console.print("[green]  [OK] AGENTS.md -> .github/copilot-instructions.md[/green]")


def setup_opencode(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure OpenCode skills directory link (uses AGENTS.md)."""
    target = repo_root / ".opencode" / "skills"
    add_to_gitignore(repo_root, ".opencode/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .opencode/skills -> skills/[/green]")
    console.print("[green]  [OK] OpenCode uses AGENTS.md natively[/green]")


def setup_native(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure Native skills directory link (uses AGENTS.md)."""
    target = repo_root / ".agents" / "skills"
    add_to_gitignore(repo_root, ".agents/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .agents/skills -> skills/[/green]")
    console.print("[green]  [OK] Native uses AGENTS.md natively[/green]")


def setup_cursor(repo_root: Path, skills_source: Path, created: set[Path]) -> None:
    """Configure Cursor skills directory link."""
    target = repo_root / ".cursor" / "skills"
    add_to_gitignore(repo_root, ".cursor/skills")
    create_link(skills_source, target, is_directory=True, created=created)
    console.print("[green]  [OK] .cursor/skills -> skills/[/green]")


def show_interactive_menu() -> list[str]:
    """Show a multi-select checkbox menu for each assistant."""
    choices = [
        questionary.Choice(
            title=f"{label}: {detail}",
            value=key,
            checked=False,
        )
        for key, label, detail in AI_ASSISTANTS
    ]
    selected = questionary.checkbox(
        "Select AI assistants to configure:",
        choices=choices,
        instruction="Use space to toggle, enter to confirm",
    ).ask()

    return selected if selected is not None else []


def run_setup(
    repo_root: Path,
    skills_source: Path,
    selected: dict[str, bool],
    skill_count: int,
) -> None:
    """Run the selected setup steps and print a summary."""
    chosen = [key for key, flag in selected.items() if flag]
    total = len(chosen)
    if total == 0:
        console.print("[yellow]No AI assistants selected. Nothing to do.[/yellow]")
        return

    created: set[Path] = set()
    step = 1
    if selected["claude"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up Claude Code...[/yellow]")
        setup_claude(repo_root, skills_source, created)
        step += 1
    if selected["gemini"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up Gemini CLI...[/yellow]")
        setup_gemini(repo_root, skills_source, created)
        step += 1
    if selected["codex"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up Codex (OpenAI)...[/yellow]")
        setup_codex(repo_root, skills_source, created)
        step += 1
    if selected["copilot"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up GitHub Copilot...[/yellow]")
        setup_copilot(repo_root, skills_source, created)
        step += 1
    if selected["opencode"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up OpenCode...[/yellow]")
        setup_opencode(repo_root, skills_source, created)
        step += 1
    if selected["native"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up Native...[/yellow]")
        setup_native(repo_root, skills_source, created)
        step += 1
    if selected["cursor"]:
        console.print(f"\n[yellow][{step}/{total}] Setting up Cursor...[/yellow]")
        setup_cursor(repo_root, skills_source, created)

    console.print(f"\n[green][DONE] Successfully configured {skill_count} AI skills![/green]\n")
    console.print("Configured:")
    for key, label, detail in AI_ASSISTANTS:
        if selected[key]:
            console.print(f"  - {label}: {detail}")

    console.print("\n[blue]Note: Restart your AI assistant to load the skills.[/blue]")
    console.print(
        "[blue]      AGENTS.md is the source of truth - changes are reflected automatically via symlinks.[/blue]"
    )


@app.command()
def main(
    all: bool = typer.Option(False, "--all", help="Configure all AI assistants"),
    claude: bool = typer.Option(False, "--claude", help="Configure Claude Code"),
    gemini: bool = typer.Option(False, "--gemini", help="Configure Gemini CLI"),
    codex: bool = typer.Option(False, "--codex", help="Configure Codex (OpenAI)"),
    copilot: bool = typer.Option(False, "--copilot", help="Configure GitHub Copilot"),
    opencode: bool = typer.Option(False, "--opencode", help="Configure OpenCode"),
    native: bool = typer.Option(False, "--native", help="Configure Native assistants"),
    cursor: bool = typer.Option(False, "--cursor", help="Configure Cursor"),
) -> Any:
    """Configure AI coding assistants for QtShadcn development."""
    repo_root = get_repo_root()
    skills_source = get_skills_source()
    skill_count = count_skills(skills_source)

    console.print("QtShadcn AI Skills Setup", style="bold")
    console.print("=" * 28)

    if skill_count == 0:
        console.print(f"[red]No skills found in {skills_source}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Found {skill_count} skills to configure[/blue]\n")

    selected = {
        "claude": claude,
        "gemini": gemini,
        "codex": codex,
        "copilot": copilot,
        "opencode": opencode,
        "native": native,
        "cursor": cursor,
    }

    if all:
        selected = dict.fromkeys(selected, True)
    elif not any(selected.values()):
        selected_keys = show_interactive_menu()
        selected = {key: key in selected_keys for key, _label, _detail in AI_ASSISTANTS}

    run_setup(repo_root, skills_source, selected, skill_count)
    return None


if __name__ == "__main__":
    app()
