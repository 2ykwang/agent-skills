---
name: commit-split
version: 0.0.1
category: development
description: "Split a pile of uncommitted changes into several context-scoped commits. Analyzes the diff first, proposes logical groups and a commit count, and once the user confirms the granularity, stages per file — down to hunks inside a single file when needed — and commits with messages matching the repo's convention. Use on requests like 'split this into commits', 'commit by context', 'atomic commits', 'how should I split these changes', or when uncommitted work mixes several topics (feature + bugfix + config). Not for rewriting already-committed history (rebase, fixup, squash), and not for a single-topic change one commit covers."
---

# commit-split

Split uncommitted changes into atomic, reviewable commits. Two things matter:
the user shouldn't have to classify contexts by hand (analysis and proposal are this skill's job),
and the result must be verifiable (prove not a single byte of code differs before and after the split).

Flow: **read state → analyze changes → propose a plan → user confirms → execute → verify losslessness**.
Don't ask the user to classify anything before proposing. Analyze first, present a plan, let the user adjust it.

## Step 0. Read state

```bash
git status --porcelain      # change list; staged/unstaged/untracked
git branch --show-current
git log --oneline -20       # learn the commit message convention
git rev-parse HEAD          # record the starting point (used for verification)
git diff HEAD | git patch-id --stable   # fingerprint of the original change (used for lossless verification)
```

Stop on: merge/rebase in progress, or conflicted files. Report the state and halt.

Watch out for:
- **Changes already staged** — tell the user. The split can't preserve the existing staging, so get
  agreement on "unstage everything and re-split the whole thing", then run `git restore --staged .`.
- **Untracked files** — include them in the plan table but mark them separately. If they look like
  build junk (logs, scratch files), suggest excluding them from the commits.

## Step 1. Analyze changes

Read the full `git diff HEAD` and the contents of untracked files, then identify logical units. Don't group
by filename — you have to read the diff to spot "two contexts mixed in one file", and spotting that is
the whole reason this skill exists.

Grouping rules, in priority order:
1. **Things that break apart** — a new function and its call sites, a signature change and its callers, an implementation and its tests go in one commit
2. **Different intent, different commit** — feature / bugfix / refactor / config / docs are separate
3. **Different domain, different commit** — unrelated modules stay apart even when the intent matches

When one file holds two contexts, mark it for hunk-level splitting.
Learn the commit message style from `git log` (prefix format, language, scope notation).

## Step 2. Propose a plan

Present the analysis as a table. Don't assert a commit count — give a **recommendation plus granularity alternatives**.

```
## Split plan (recommended: 3)

| # | Draft commit message | Target |
|---|---|---|
| 1 | feat(auth): add login attempt limit | auth/service.py, auth/tests/test_lockout.py |
| 2 | fix(payment): correct refund rounding | payment/service.py (hunks 1,3), payment/tests/... |
| 3 | chore: raise payment timeout | config/settings.py, payment/service.py (hunk 2) |

- Coarser (2): merge 2 and 3 as payment-related
- Finer (4): split the tests out of 1
```

For files that need hunk splitting, spell out in the table which hunk goes to which commit.

## Step 3. User confirms

Use AskUserQuestion when available. Ask everything in one shot:
- **Granularity**: recommended N / coarser / finer / custom (free text via Other)
- Only ask about message style when it's ambiguous (skip it when the repo convention is clear)

If the user adjusts the boundaries, update the plan table, show it again, then proceed.
In a non-interactive environment where no answer can be collected, say you're proceeding with the recommendation and proceed.

## Step 4. Execute

Stage and commit group by group, in plan order.

- **Whole files in one group**: `git add <files>`
- **Files needing a hunk split**: use the bundled script (`git add -p` is interactive and unusable here)

```bash
python3 scripts/stage_hunks.py list <file>            # list hunks with numbers
python3 scripts/stage_hunks.py stage <file> 1 3       # stage hunks 1 and 3 only
```

The script path is relative to this skill's directory. `list` only shows unstaged hunks, so after staging
some of them, a second `list` renumbers what's left — keep that in mind.

Use the confirmed draft as the commit message. If a pre-commit hook modifies files and fails (formatters),
re-add the modified content to that group and commit again.

Safety rules:
- This skill only runs add and commit. Never push, reset, stash, or checkout
- If something goes wrong mid-run, don't attempt automatic recovery — report the current state and stop
  (splitting never touches working tree files, so the code survives even in the worst case)

Undo guidance: to restore the starting state after a bad result or an interrupted run, the command is
`git reset --mixed <startHEAD>`. The commits unwind and the tree returns exactly to the pre-split
uncommitted state (nothing is lost — the file contents live in the commits). Don't run this yourself;
just include it, along with the starting HEAD, in failure reports and the final report.

## Step 5. Verify losslessness

Once the commits are in, prove it and report:

```bash
git status --porcelain                        # any leftover changes beyond the intended exclusions?
git diff <startHEAD> HEAD | git patch-id --stable   # does it match the fingerprint from Step 0?
git log --oneline <startHEAD>..HEAD           # did the commits land as planned?
```

A matching patch-id proves the change content is identical before and after the split. If some files were
deliberately left out of the commits, the patch-id will differ — in that case verify instead that the
leftover changes match the exclusion list exactly.

Fill in this template for the final report:

```
## Split complete (<N> commits)

| Commit | Message | Target |
|---|---|---|
| <7-char sha> | <commit message> | <files, noting hunk splits> |

- Lossless check: <"patch-id matches" or "leftover changes match the exclusion list">
- Excluded files: <list and reason, "none" if none>
- Undo: `git reset --mixed <starting HEAD>` (unwinds the commits back to the pre-split state)
```
