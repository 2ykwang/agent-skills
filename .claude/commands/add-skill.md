---
description: Scaffold a new skill with validation, plugin generation, and README update.
argument-hint: "<skill-name>"
---

# Add Skill

Scaffold a new skill named `$ARGUMENTS`.

## Workflow

### 1. Validate Input

- Check `$ARGUMENTS` is kebab-case (`^[a-z0-9]+(-[a-z0-9]+)*$`). Stop with error if not.
- Check `skills/$ARGUMENTS/` does not already exist. Stop with error if it does.

### 2. Create Directory Structure

```
skills/<name>/
├── SKILL.md
└── README.md
```

### 3. Write SKILL.md

```markdown
---
name: <name>
version: 0.0.1
category: TODO
description: "TODO — one sentence describing what this skill does and when to trigger it."
argument-hint: "<argument>"
---

## Instructions

TODO
```

### 4. Ask User

Use AskUserQuestion:
1. **Category** — one of: `development`, `design-frontend`, `productivity`, `integrations`, `media`
2. **Description** — one sentence for the skill description

Update SKILL.md frontmatter with the user's answers.

### 5. Write README.md

Create `skills/<name>/README.md` with this structure:

```markdown
# <name>

<description from step 4>

## When to use

- TODO

## Usage

```
/skill-name <example>
```

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install <name>@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill <name>
```
```

### 6. Generate Plugins

Run `python3 scripts/generate_plugins.py`. This generates:
- `plugins/<name>/` directory with plugin.json, README.md, and copied skills
- Updated `.claude-plugin/marketplace.json`

### 7. Update README.md Skills Table

Find the table between the two `---` separators. Append 3-row block before the closing `---`:

```markdown
| [<name>](skills/<name>) | <description> |
| | `npx skills add 2ykwang/agent-skills --skill <name>` |
| | `claude plugin install <name>@2ykwang-agent-skills` |
```

### 8. Validate and Report

Run `python3 scripts/validate.py`. Show output.

Print summary:

```
Created skills/<name>/

Next steps:
  1. Edit skills/<name>/SKILL.md — replace TODOs
  2. Edit skills/<name>/README.md — add "When to use" and "Usage" examples
  3. just generate && just validate
```
