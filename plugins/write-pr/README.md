# write-pr

Analyzes the git diff and commit history to draft a PR title and description that matches the project's conventions.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install write-pr@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill write-pr
```

## When to use

- About to open a PR and need a well-structured title and description
- Too many changes to summarize by hand
- Want the PR to match the project's existing template and title style

## Usage

```
# Against the default base branch (auto-detected)
/write-pr

# Against a specific base branch
/write-pr develop
```

## How it works

1. Auto-detects the base branch (or uses the one you specify).
2. Finds `.github/PULL_REQUEST_TEMPLATE.md` and preserves its structure.
3. Matches the project's naming convention from merged PR titles.
4. Focuses on **why** the change was made, not just what files changed.

## Output

A ready-to-paste PR title and body — a conventional-commit-style title (e.g. `feat(auth): add OAuth2 login support`) and a description following the project's template (Summary / Changes / Test Plan).

## Notes

- Read-only — does not create a PR or push anything. Copy the output when opening your PR.
