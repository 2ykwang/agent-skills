# quick-pr

Split a minor change from your current work into a separate worktree and open a PR — without leaving your branch.

## When to use

- A small fix (typo, config, lint rule) is mixed into a larger feature branch
- Want to ship a trivial change immediately without polluting the current PR
- Need to split out an unrelated edit without the stash/checkout/branch ceremony

## Usage

```
# Split a specific file's diff into a PR
/quick-pr .eslintrc.json

# Describe the change — the skill makes the edit in the worktree
/quick-pr "update Node version from 18 to 20 in CI config"

# Interactive — the skill asks what to split out
/quick-pr
```

## How it works

1. **Determine scope** — file diff or description-based edit.
2. **Pick branch + commit** — 5 candidates each, you choose.
3. **Worktree** — isolated from your current branch, based on latest main.
4. **Apply + PR** — commit, push, open PR with the project's template.
5. **Clean up** — verify the PR, then optionally remove the worktree.

Every step is interactive. Nothing is pushed without your confirmation.

## Notes

- Requires Claude Code (`EnterWorktree`, `ExitWorktree`, `AskUserQuestion`).
- Requires `gh` CLI for PR creation.
- Not read-only — pushes code and creates PRs. Always confirms before external actions.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install quick-pr@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill quick-pr
```
