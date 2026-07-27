---
name: commit-fixup
version: 0.0.1
category: development
description: "Absorb uncommitted working tree edits into the existing commits on the current branch where each change belongs (fixup commits + autosquash rebase). Use on requests like 'fold this into the original commit', 'clean up the commit history', 'squash the review fixes into their commits', 'fixup', 'amend into an existing commit', or when review feedback and polishing edits need to land in the right commit. Not for reordering commits already in history, and not for splitting a commit apart."
---

# commit-fixup

Absorb uncommitted changes into the existing commit each one should have been part of, leaving clean history.
Four stages: safety checks → mapping → scope confirmation → execution and verification.
This rewrites history, so don't skip any stage's checks.

## 1. Safety checks

```bash
git status --short                       # uncommitted changes
git merge-base HEAD origin/<default-branch>  # establish base (use the repo's default branch)
git log --oneline <base>..HEAD           # commits in scope
git branch -vv                           # upstream and push state
git log --merges --oneline <base>..HEAD  # merge commits in range
git --version
```

Tell the user before proceeding if any of these hit:

- **Branch already pushed → stop and ask.** Rebasing means a force-push afterwards, and only the user
  makes that call. Never run a force-push on your own.
- **Merge commits in range → stop.** The rebase flattens the merge structure.
- **git older than 2.44 → don't proceed.** That version lacks the non-interactive `git rebase --autosquash`
  this skill relies on. Say the git version is too old to automate this safely and point at an upgrade
  (macOS: `brew upgrade git`, Ubuntu: `apt upgrade git`).
- Untracked files are not absorption targets. Leave them alone.

## 2. Mapping: find the target commit for each changed file

For each modified file, find the commit in branch range that **touched it last**:

```bash
git log --oneline <base>..HEAD -- <file> | head -1
```

Why last-toucher: even when an earlier commit is the semantic owner, if a later commit also touched the
file, fixing up into the earlier one makes the rebase conflict. The last-toucher rule guarantees a
conflict-free, fully automatic rebase. It trades a little history aesthetics for safety — call out the
affected files in the mapping table.

Mapping results fall into three buckets:

- **Mapped**: a commit in the branch touched that file
- **Unmapped**: no commit touched it (new file, or a change to a file from outside the branch)
- One file's changes needing to split across several commits → references/edge-cases.md

## 3. Confirm scope (user confirmation required)

Identify the situation, **show the mapping table first**, then confirm via AskUserQuestion:

| Situation | Action |
|---|---|
| Everything mapped | Show the table, confirm you should proceed |
| Mixed (only some mapped) | Ask how to handle unmapped files: new separate commit / leave in working tree / stop |
| Nothing mapped, or 0–1 commits on the branch | **Nothing for this skill to do.** Say so and suggest a normal commit or a plain amend |

Absorption is history rewriting. Never execute without the table — the user's chance to review the
placement is what makes this workflow trustworthy. In an automated environment with no way to ask,
print the table and proceed only in the "everything mapped" case. Stop and report on mixed and unmapped cases.

## 4. Execute and verify

```bash
# Files heading for the same target commit go into one fixup commit
git add <files...> && git commit --fixup=<target-sha>
# ... repeat per target commit

# Recovery point: snapshot the current state, fixup commits included, as a backup branch.
# This is what lets the user find a recovery point with plain `git branch` long after the session ends.
git branch <branch>-fixup-backup   # append -2, -3 if the name is taken

git rebase --autosquash <base>

# Lossless check: output must be empty. Proof that content is unchanged and only placement moved.
git diff <branch>-fixup-backup HEAD

# Residue check: any leftover fixup! commit means it failed
git log --oneline <base>..HEAD
git status --short   # must be clean
```

- If the rebase conflicts, **run `git rebase --abort` immediately** and report. A conflict signals a
  mapping error, not something to resolve on the spot. Aborting returns to a safe state with the fixup
  commits sitting at the tip, so nothing is lost.
- Run the project's test suite once at the end if it has one.
- Don't delete the backup branch on your own. That call belongs to the user who reviewed the result.

## 5. Report

Always report with this template. Same information in the same place every time, so the user can spot
trouble by skimming the verification block.

~~~markdown
## Absorption complete

| Modified file | Absorbed into |
|---|---|
| <file> | <sha> <commit subject> |

**Final history** (<base>..HEAD)
```
<git log --oneline output>
```

**Verification**
- Lossless: <"backup and HEAD identical (empty diff)" or the failure>
- fixup residue: <"none" or the remaining commits>
- Working tree: <"clean" or remaining changes>
- Tests: <result, "n/a" when there's no suite>

**Recovery and cleanup**
- Backup branch: `<branch>-fixup-backup`
- If the result is wrong: `git reset --hard <branch>-fixup-backup`
- Once verified: `git branch -D <branch>-fixup-backup`
~~~

When you stop instead (unmappable, pushed branch, merge commits, conflict abort), skip this template and
report what stopped you, what state the repo is in now, and what the options are.
