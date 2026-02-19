# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Skills for AI coding agents. Each skill lives under `skills/`. The `plugins/` directory and `marketplace.json` are auto-generated.

## Commands

```bash
just generate      # Generate plugins/ and marketplace.json from skills/
just validate      # Validate skill structure
just test          # Run script tests (unittest, no dependencies)
just check         # Run all pre-commit hooks
just version-bump  # Bump patch version for changed skills (edits SKILL.md frontmatter)
```

## Skill Structure (source)

```
skills/<name>/
├── SKILL.md           # Skill definition (YAML frontmatter + body)
└── references/        # Optional supporting docs (read at runtime by the skill)
```

## Generated Output (do not edit manually)

```
plugins/<name>/
├── .claude-plugin/
│   └── plugin.json       # Generated from SKILL.md frontmatter
├── skills/               # Copied from skills/<name>/
│   ├── SKILL.md
│   └── references/
└── README.md             # Generated with install commands
```

`.claude-plugin/marketplace.json` is also generated.

## Adding a New Skill

1. `/add-skill <skill-name>` — scaffolds `skills/<name>/`, generates plugins, updates README
2. Edit `skills/<name>/SKILL.md` — replace TODO content
3. `just generate && just validate`

## Validation Rules

`scripts/validate.py` checks:

- Each `skills/<name>/SKILL.md` has frontmatter fields: `name`, `description`, `version` (semver), `category`
- Skill folder names are kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`)

Runs automatically via pre-push hook.

## SKILL.md Format

```markdown
---
name: skill-name
version: 0.0.1
category: development
description: One sentence — what it does and when to trigger it.
argument-hint: "<argument>"
---

## Instructions

Use $ARGUMENTS to reference user input.
```

## Versioning

Edit `version` in `skills/<name>/SKILL.md` frontmatter. Run `just generate` to propagate to plugin.json and marketplace.json.

`just version-bump` auto-detects changed skills via git diff and bumps their patch version.

## Testing

When modifying `scripts/validate.py`, update `tests/test_scripts.py` as well.
New check logic → add a corresponding test case. Verify with `just test`.

## Conventions

- Folder names: kebab-case
- One `SKILL.md` per skill
- Categories: `development`, `design-frontend`, `productivity`, `integrations`, `media`
