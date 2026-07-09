# quick-pr

Splits a minor change from your current work into a separate worktree and opens a PR — without leaving your branch, and without the stash/checkout/branch/push ceremony.

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

## When to use

- Mid-feature, you spot an unrelated small fix — a typo, stale config, a missing lint rule
- You want it shipped as its own PR without interrupting your current branch

## Usage

```
# From a file's current diff
/quick-pr .eslintrc.json

# From a description
/quick-pr "update Node version from 18 to 20 in CI config"

# Infer scope from context
/quick-pr
```

## How it works

1. **Determine scope** — a file's diff or a description-based edit.
2. **Pick branch + commit** — candidates offered, you choose.
3. **Worktree** — isolated from your current branch, based on latest main.
4. **Apply + PR** — commit, push, open a PR with the project's template.
5. **Clean up** — verify the PR, then optionally remove the worktree.

Every step is interactive; nothing is pushed without your confirmation.

## Requirements

- Claude Code (uses `EnterWorktree`, `ExitWorktree`, `AskUserQuestion`)
- `gh` CLI
- Git repository with a remote
