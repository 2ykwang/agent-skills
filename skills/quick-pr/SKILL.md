---
name: quick-pr
version: 0.0.1
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

This skill is interactive. Get user confirmation at each decision point.

### Step 1: Determine Change Scope

**If argument is a file path:**
- Run `git diff HEAD -- <file>` to get the current diff
- Show the diff to the user and ask: "Open a PR for this change?"

**If argument is a description:**
- Propose which files to modify and how
- Ask the user to confirm

**If argument is empty:**
- Use `AskUserQuestion` to ask what change to split out

### Step 2: Choose Branch Name and Commit Message

Based on the change, propose up to 5 candidates for each:

**Branch names:**
- Use appropriate prefix: `fix/`, `chore/`, `docs/`, `feat/`
- kebab-case

**Commit messages:**
- Check the project's commit style first: `git log --oneline -10`
- Match the dominant pattern (Conventional Commits, ticket prefix, etc.)
- If no clear pattern, default to Conventional Commits (`type: description`)

Present numbered options. User picks by number or writes their own.

### Step 3: Create Worktree and Apply Changes

```bash
git fetch origin
```

Determine the default branch:
```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null
```
Fallback: check which of `main`, `master`, `develop` exists.

Use `EnterWorktree` to create a worktree based on the default branch. Then rename the branch:

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

### Step 4: Commit, Push, and Create PR

```bash
git add <changed-files>
git commit -m "<chosen-commit-message>"
git push -u origin <branch-name>
```

**Write the PR body inline (do not delegate to another skill):**

1. Check for a PR template — read these paths in parallel:
   - `.github/PULL_REQUEST_TEMPLATE.md`
   - `.github/pull_request_template.md`
   - `docs/pull_request_template.md`
   - `PULL_REQUEST_TEMPLATE.md`
   - Also check `.github/PULL_REQUEST_TEMPLATE/` directory

2. **If a template exists:** preserve its structure exactly. Fill sections from the diff. Leave unfillable sections (Screenshots, Related Issues) as-is with their original placeholders.

3. **If no template exists:** use this minimal structure:
   ```markdown
   ## Summary
   <what and why — 1-3 sentences>

   ## Changes
   <bullet list of key changes>
   ```

4. For the PR title, match the style from `gh pr list --state merged --limit 5 --json title 2>/dev/null`. Fallback to `git log --oneline -10`. Default to Conventional Commits if unclear.

5. Show the draft title and body to the user. Apply any edits they request.

6. Create the PR:
   ```bash
   gh pr create --title "<title>" --body "<body>"
   ```

### Step 5: Confirm and Clean Up

Show the PR link:

```
PR created: <URL>
```

Then ask:

```
Remove the worktree?
```

- **Yes**: call `ExitWorktree` with `action: "remove"`
- **No**: call `ExitWorktree` with `action: "keep"`

## Constraints

- This skill modifies external state (git push, PR creation). Always confirm before pushing or creating the PR.
- Do not include `Co-Authored-By` in commits.
- Keep the entire flow conversational — never batch multiple steps without user checkpoints.
