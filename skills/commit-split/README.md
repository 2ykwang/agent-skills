**English** | [한국어](README.ko.md)

# commit-split

Splits uncommitted changes into commits by context, down to hunk level when one file holds two contexts. You don't sort the diff into groups yourself, and the split is verified lossless afterwards.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install commit-split@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill commit-split
```

## When to use

- Uncommitted work has piled up across several topics — a feature, a bugfix, a config tweak
- You want atomic commits but don't want to sort the diff into groups yourself
- Two unrelated changes ended up in the same file and need to land in different commits

Not for rewriting history that's already committed, and not for a single-topic change one commit covers.

## Usage

```
/commit-split
```

## How it works

1. **Read state** — records the starting HEAD and a `git patch-id` fingerprint of the full diff.
2. **Analyze** — reads the diff itself, not filenames, to find logical units and files holding two contexts.
3. **Propose** — a plan table with draft messages in the repo's own convention, plus coarser/finer alternatives.
4. **Confirm** — you pick the granularity and adjust boundaries.
5. **Execute** — stages per group, down to individual hunks where a file is split.
6. **Verify** — compares the patch-id against the fingerprint to prove no content changed.

Only `add` and `commit` are ever run — no push, reset, stash, or checkout. If anything goes wrong, it stops and reports instead of trying to recover, and the working tree is never touched.

## Requirements

- Git repository with uncommitted changes
- `python3` (for hunk-level staging)
