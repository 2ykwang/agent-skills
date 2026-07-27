**English** | [한국어](README.ko.md)

# commit-fixup

Absorbs uncommitted edits into the existing commits each one belongs to, using fixup commits and an autosquash rebase. Shows the mapping for approval first, and leaves a backup branch to fall back to.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install commit-fixup@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill commit-fixup
```

## When to use

- Review feedback produced edits that each belong in an earlier commit on the branch
- Polishing after the fact left changes scattered across commits you've already made
- You want clean history before opening a PR, without hand-driving an interactive rebase

Not for reordering commits already in history, and not for splitting an existing commit apart.

## Usage

```
/commit-fixup
```

## How it works

1. **Safety checks** — stops on a pushed branch, merge commits in range, or git older than 2.44.
2. **Mapping** — for each modified file, finds the commit in the branch that touched it last. That rule is what keeps the rebase conflict-free.
3. **Confirmation** — shows the mapping table and asks before rewriting anything. Unmapped files get their own decision.
4. **Execute** — one fixup commit per target, a backup branch, then `git rebase --autosquash`.
5. **Verify** — diffs the backup against HEAD (must be empty), checks for leftover `fixup!` commits, and runs the test suite if there is one.

Never force-pushes. On a rebase conflict it aborts immediately and reports, since a conflict means the mapping was wrong.

## Requirements

- Git 2.44+ (non-interactive `rebase --autosquash`)
- A branch with commits ahead of its base
