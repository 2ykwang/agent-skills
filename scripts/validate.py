#!/usr/bin/env python3
"""Validate agent-skills repo structure: skills/ directory and SKILL.md frontmatter."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")

errors = []


def error(msg: str) -> None:
    errors.append(msg)
    print(f"  ERROR: {msg}", file=sys.stderr)


def parse_frontmatter(skill_md: Path) -> dict:
    """Extract YAML frontmatter fields from SKILL.md."""
    text = skill_md.read_text()
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    fields = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            val = val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in ('"', "'"):
                val = val[1:-1]
            fields[key.strip()] = val
    return fields


def validate_skills() -> None:
    print("Validating skills...")
    if not SKILLS_DIR.exists():
        error("skills/ directory not found")
        return

    for folder in sorted(SKILLS_DIR.iterdir()):
        if not folder.is_dir() or folder.name.startswith("."):
            continue

        name = folder.name
        if not KEBAB_RE.match(name):
            error(f"Skill folder '{name}' is not kebab-case")

        skill_md = folder / "SKILL.md"
        if not skill_md.exists():
            error(f"Skill '{name}': missing SKILL.md")
            continue

        fm = parse_frontmatter(skill_md)
        for field in ("name", "description", "version", "category"):
            if not fm.get(field):
                error(f"Skill '{name}': SKILL.md missing frontmatter field '{field}'")

        version = fm.get("version", "")
        if version and not SEMVER_RE.match(version):
            error(f"Skill '{name}': version '{version}' is not semantic (expected X.Y.Z)")


def main() -> None:
    validate_skills()

    if errors:
        print(f"\n{len(errors)} error(s) found.", file=sys.stderr)
        sys.exit(1)
    else:
        print("\nAll checks passed.")


if __name__ == "__main__":
    main()
