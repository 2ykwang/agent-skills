# github-create-issue

File a GitHub issue maintainers can actually act on — verified, not a duplicate, follows repo conventions (template/label/prefix), and previewed before publishing. Use when reporting a known problem.

## When to use

- The user has already identified a problem and asks to file an issue
- NOT for diagnosing or finding bugs in code

## Requirements

- `gh` CLI (authenticated via `gh auth login`)
- Git repository with a GitHub remote

## Usage

The skill is triggered automatically by intent. To invoke explicitly:

```
/github-create-issue
```

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install github-create-issue@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill github-create-issue
```
