---
name: quick-pr
version: 0.0.2
category: productivity
description: "Split a minor change from the current work into a separate worktree and open a PR without interrupting your flow. Requires Claude Code (uses EnterWorktree, ExitWorktree, AskUserQuestion)."
argument-hint: "[file-path or change description]"
---

# Quick PR

Split an unrelated minor change (convention fix, typo, config tweak) from the current working tree into an independent PR — without leaving the current branch.

This is a Claude Code skill. It requires Claude Code built-in tools: `EnterWorktree`, `ExitWorktree`, and `AskUserQuestion`.

## Use this skill when

- A small fix (typo, lint, config) is mixed into a larger feature branch
- The user wants to ship a trivial change immediately without polluting the current PR
- The user says "quick PR", "split this out", or "ship this separately"

## Do not use this skill when

- The change is part of the current feature work
- The user only wants a PR description (use `/write-pr` instead)
- The change requires review or testing beyond a simple visual check

## Input

```text
$ARGUMENTS
```

**Argument interpretation:**
- File path (e.g., `src/config.py`) — extract the current diff for that file and apply it in the worktree
- Description text (e.g., `"fix typo in README"`) — make the edit directly in the worktree
- Empty — ask the user what to split out

## Tools

Fetch these tools via `ToolSearch` before use:

| Purpose | Tool |
|---------|------|
| Enter isolated worktree | `EnterWorktree` |
| Exit/remove worktree | `ExitWorktree` |
| Ask the user | `AskUserQuestion` |

## Procedure

### Step 1: Determine Change Scope

**File path arg:** Run `git diff HEAD -- <file>`, show the diff.
**Description arg:** Propose which files to modify and how.
**Empty arg:** Ask what to split out.

→ **Use `AskUserQuestion` to confirm the scope before continuing.**

### Step 2: Choose Branch Name and Commit Message

Check the project's commit style: `git log --oneline -10`.

Propose up to 5 candidates for each:
- **Branch:** kebab-case, prefix `fix/` `chore/` `docs/` `feat/`
- **Commit:** match dominant pattern (Conventional Commits, ticket prefix, etc.); default to Conventional Commits if unclear

→ **Use `AskUserQuestion` with the numbered options. User picks or writes their own.**

### Step 3: Choose Base Branch, Create Worktree, Apply Changes

```bash
git fetch origin
```

Detect the default branch as the recommended base:
```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null
```
Fallback: check which of `main`, `master`, `develop` exists.

Gather recent remote branches as additional candidates:
```bash
git for-each-ref --sort=-committerdate refs/remotes/ \
  --format='%(refname:short)' | grep -v HEAD | head -5
```

→ **Use `AskUserQuestion` to pick the base branch.** Present the detected default as the recommended option, followed by the recent branches. User can write their own. This base is reused as the PR target in Step 4.

Use `EnterWorktree` to create a worktree based on the chosen base branch. Then rename the branch:

```bash
git branch -m <chosen-branch-name>
```

**File-based mode:**
Before entering the worktree, note the original worktree path. After entering, copy the changed file from the original path:

```bash
cp <original-worktree-path>/<file> <current-worktree-path>/<file>
```

**Description-based mode:**
Make the edit directly in the worktree.

### Step 4: Commit, Push, Create PR

```bash
git add <changed-files>
git commit -m "<chosen-commit-message>"
```

→ **Use `AskUserQuestion` to confirm push.** On approval:
```bash
git push -u origin <branch-name>
```

Build the PR body inline (do not delegate to another skill):

1. Check templates in parallel:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `docs/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
   - `.github/PULL_REQUEST_TEMPLATE/` directory

2. **Template exists:** preserve structure exactly. Fill sections from the diff. Leave unfillable sections (Screenshots, Related Issues) with their original placeholders.

3. **No template:**
   ```markdown
   ## Summary
   <what and why — 1-3 sentences>

   ## Changes
   <bullet list of key changes>
   ```

4. PR title: match `gh pr list --state merged --limit 5 --json title 2>/dev/null`. Fallback to `git log --oneline -10`. Default to Conventional Commits if unclear.

→ **Use `AskUserQuestion` with the draft title + body + target branch (defaults to the base from Step 3). Do not run `gh pr create` until approved.**

```bash
gh pr create --base <target-branch> --title "<title>" --body "<body>"
```

### Step 5: Confirm and Clean Up

Show `PR created: <URL>`.

→ **Use `AskUserQuestion`: "Remove the worktree?"**
- **Yes** → `ExitWorktree` with `action: "remove"`, `discard_changes: true`
  (safe — the commit is already on origin from Step 4)
- **No** → `ExitWorktree` with `action: "keep"`
