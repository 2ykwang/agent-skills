#!/usr/bin/env python3
"""Bump patch version for changed skills (edits SKILL.md frontmatter)."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"


def get_changed_skills() -> set[str]:
    """Detect skills with uncommitted changes via git.

    Excludes version-only changes in SKILL.md for idempotency.
    """
    lines: list[str] = []
    for cmd in (
        ["git", "diff", "--name-only"],
        ["git", "diff", "--cached", "--name-only"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        lines.extend(result.stdout.strip().splitlines())

    skills: set[str] = set()
    for f in lines:
        if not f:
            continue
        parts = Path(f).parts
        if len(parts) >= 2 and parts[0] == "skills":
            skills.add(parts[1])
    return skills


def bump_patch(version: str) -> str:
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def parse_frontmatter_version(text: str) -> str | None:
    """Extract version from SKILL.md frontmatter text."""
    if not text.startswith("---"):
        return None
    end = text.find("---", 3)
    if end == -1:
        return None
    for line in text[3:end].splitlines():
        if line.strip().startswith("version:"):
            _, _, val = line.partition(":")
            return val.strip()
    return None


def git_frontmatter_version(skill_md_path: Path) -> str | None:
    """Get the version from git HEAD. Returns None if not tracked."""
    rel = skill_md_path.relative_to(ROOT)
    result = subprocess.run(
        ["git", "show", f"HEAD:{rel}"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.returncode != 0:
        return None
    return parse_frontmatter_version(result.stdout)


def update_frontmatter_version(skill_md: Path, new_version: str) -> None:
    """Replace the version line in SKILL.md frontmatter."""
    text = skill_md.read_text()
    end = text.find("---", 3)
    header = text[: end + 3]
    body = text[end + 3 :]
    updated_header = re.sub(
        r"^version:\s*.*$", f"version: {new_version}", header, flags=re.MULTILINE
    )
    skill_md.write_text(updated_header + body)


def main() -> None:
    changed = get_changed_skills()
    if not changed:
        print("No changed skills detected.")
        return

    bumped = []

    for name in sorted(changed):
        skill_md = SKILLS_DIR / name / "SKILL.md"
        if not skill_md.exists():
            continue

        current = parse_frontmatter_version(skill_md.read_text())
        if not current:
            continue

        committed = git_frontmatter_version(skill_md)

        # Skip if already bumped (current version differs from HEAD)
        if committed and current != committed:
            print(f"  {name}: already bumped ({committed} -> {current}), skipping")
            continue

        new = bump_patch(current)
        update_frontmatter_version(skill_md, new)
        bumped.append((name, current, new))

    if bumped:
        for name, old, new in bumped:
            print(f"  {name}: {old} -> {new}")
    else:
        print("No skills to bump.")


if __name__ == "__main__":
    main()
