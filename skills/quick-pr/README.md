# quick-pr

Split a minor change from your current work into a separate worktree and open a PR — without leaving your branch.

## Why

You're deep in a feature branch and notice something unrelated that needs fixing: a typo in docs, a stale config value, a missing lint rule. It takes 10 seconds to fix, but the git ceremony around it — stash, checkout main, pull, branch, commit, push, PR, switch back — takes 5 minutes and breaks your flow.

`quick-pr` handles that ceremony for you. Fix it, split it out, ship it.

## Usage

```
/quick-pr .eslintrc.json
/quick-pr "add missing env variable to .env.example"
/quick-pr
```

## Examples

### Fix a typo while reviewing code

You're reviewing a service module and spot a typo in a docstring.

```
/quick-pr src/services/auth.py
```

The skill shows the diff, you confirm, pick a branch name and commit message, and a PR is up in under a minute. You never left your feature branch.

### Update a CI config

The CI pipeline has a deprecated Node version. You know the fix — change one line — but it has nothing to do with your current ticket.

```
/quick-pr "update Node version from 18 to 20 in CI config"
```

The skill creates a worktree, makes the edit, and opens the PR. Your working tree is untouched.

### Add a missing lint rule

You notice the linter isn't catching a pattern it should. Quick config change.

```
/quick-pr .ruff.toml
```

Diff extracted, PR opened. Done.

### Fix a broken link in docs

While grepping for something else, you find a dead link in the contributing guide.

```
/quick-pr "fix broken link in CONTRIBUTING.md"
```

The skill asks what the correct URL is, makes the change, and ships it.

### Remove a deprecated environment variable

An env variable was removed two releases ago but `.env.example` still lists it. No one's going to make a ticket for this.

```
/quick-pr .env.example
```

### Update a stale code comment

A comment says "calls the v1 endpoint" but the code was migrated to v2 months ago. Misleading for the next reader.

```
/quick-pr "update stale API version comment in payment module"
```

### Add a missing .gitignore entry

Your editor keeps generating `.idea/` files and someone forgot to gitignore it.

```
/quick-pr .gitignore
```

## How it works

1. **Determine scope** — file diff or description-based edit
2. **Pick branch + commit** — 5 candidates each, you choose
3. **Worktree** — isolated from your current branch, based on latest main
4. **Apply + PR** — commit, push, open PR with the project's template
5. **Clean up** — verify the PR, then optionally remove the worktree

Every step is interactive. Nothing is pushed without your confirmation.

## Requirements

- Claude Code (uses `EnterWorktree`, `ExitWorktree`, `AskUserQuestion`)
- `gh` CLI (for PR creation)
- Git repository with a remote
