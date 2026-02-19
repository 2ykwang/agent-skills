#!/usr/bin/env python3
"""Generate plugins/ directory and marketplace.json from skills/ source."""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
SKILLS_DIR = ROOT / "skills"
PLUGINS_DIR = ROOT / "plugins"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"

MARKETPLACE_META = {
    "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
    "name": "2ykwang-agent-skills",
    "description": "Skills for AI coding agents",
    "owner": {"name": "2ykwang", "url": "https://github.com/2ykwang"},
}

PLUGIN_AUTHOR = {"name": "2ykwang", "url": "https://github.com/2ykwang"}
PLUGIN_REPO = "https://github.com/2ykwang/agent-skills"


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


def generate_plugin_json(name: str, description: str, version: str) -> dict:
    return {
        "name": name,
        "version": version,
        "description": description,
        "author": PLUGIN_AUTHOR,
        "repository": PLUGIN_REPO,
        "homepage": f"{PLUGIN_REPO}/tree/main/skills/{name}",
        "license": "MIT",
    }


def generate_readme(name: str, description: str, requires: str = "") -> str:
    requires_section = ""
    if requires:
        requires_section = f"""
## Requires

- {requires}
"""
    return f"""# {name}

{description}
{requires_section}
## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install {name}@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill {name}
```

---

> Auto-generated from [skills/{name}](../../skills/{name}).
"""


def main():
    if PLUGINS_DIR.exists():
        shutil.rmtree(PLUGINS_DIR)
    PLUGINS_DIR.mkdir()

    marketplace_plugins = []

    for skill_path in sorted(SKILLS_DIR.iterdir()):
        if not skill_path.is_dir() or skill_path.name.startswith("."):
            continue
        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            continue

        fm = parse_frontmatter(skill_md)
        name = fm.get("name", skill_path.name)
        description = fm.get("description", f"Agent skill: {name}")
        version = fm.get("version", "0.0.1")
        category = fm.get("category", "productivity")

        plugin_path = PLUGINS_DIR / name

        # .claude-plugin/plugin.json
        pj_dir = plugin_path / ".claude-plugin"
        pj_dir.mkdir(parents=True)
        (pj_dir / "plugin.json").write_text(
            json.dumps(generate_plugin_json(name, description, version), indent=2)
            + "\n"
        )

        # Copy skills/<name>/* → plugins/<name>/skills/
        plugin_skills_dir = plugin_path / "skills"
        plugin_skills_dir.mkdir()
        for item in skill_path.iterdir():
            dest = plugin_skills_dir / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

        # README.md
        requires = fm.get("requires", "")
        (plugin_path / "README.md").write_text(
            generate_readme(name, description, requires)
        )

        marketplace_plugins.append(
            {
                "name": name,
                "source": f"./plugins/{name}",
                "description": description,
                "version": version,
                "category": category,
            }
        )

        print(f"  {name}")

    marketplace = {**MARKETPLACE_META, "plugins": marketplace_plugins}
    MARKETPLACE.parent.mkdir(exist_ok=True)
    MARKETPLACE.write_text(json.dumps(marketplace, indent=2) + "\n")

    print(f"\nGenerated {len(marketplace_plugins)} plugins + marketplace.json")


if __name__ == "__main__":
    main()
