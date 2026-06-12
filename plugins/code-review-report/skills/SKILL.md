---
name: code-review-report
version: 0.1.0
category: development
description: Turn code changes into a single-file HTML code review report that pairs the diff with context a diff can't show — design decisions, rejected alternatives, tradeoffs, unfinished work — plus prioritized review points. Use when preparing for review after finishing a sizable change, refactor, or feature, or whenever the user asks for a review report, change report, or an HTML summary of their changes.
---

# Code Review Report

Build a single-file HTML report a reviewer reads before digging through the raw diff. A diff shows what changed; it doesn't show why, what was rejected, or what's still missing. Filling that gap with the context accumulated in this conversation is what separates this from a diff viewer.

## 1. Collect the change

Check the change with `git status` and `git diff`. Default scope: current branch vs the default branch, plus the uncommitted working tree.

- `git diff <base>...HEAD` (committed), `git diff HEAD` (uncommitted)
- Untracked files don't appear in diffs — find them with `git status` and read them directly.

If the scope is mixed or contains unrelated changes, ask the user. Exclude unrelated changes or mark them separately.

## 2. Collect the working context

Gather from this conversation the things a diff never records:

- What was changed and why
- Design decisions and their reasons, rejected alternatives, tradeoffs
- Unfinished work and next steps
- Concerns raised and reversals made along the way

If the conversation lacks this (e.g., the skill was invoked fresh), reconstruct from `git log`, commit messages, PRs, and related docs. If still empty, ask the user.

## 3. Extract review points

Inject the changed code plus the working context into subagents and collect suspicious spots as P1–P3 findings. Read `references/review-perspectives.md` for the perspective list and the subagent prompt skeleton. The context injection is the point — without it you only get surface-level remarks, not findings like spec mismatches or contradictions between decisions. For large changes, run one subagent per perspective in parallel.

## 4. Write the HTML

Start from `assets/template.html`. Follow `references/report-structure.md` for sections and `references/style-guide.md` for visual rules. Two things are non-negotiable:

- Syntax highlighting on code blocks (add `language-*` classes)
- Bidirectional anchors between change details and the review checklist

Write the report in the language the user works in: translate the template's headings and set `<html lang>`. Keep code as-is. Before finalizing, run the self-check at the end of `references/report-structure.md`.

## 5. Finalize

1. Save to the project root as `<task-slug>-review-report.html` (kebab-case task name).
2. Inline the vendored highlight.js — replaces the template's placeholder, keeps the report self-contained and offline-friendly:
   `python3 <skill-dir>/scripts/inline_hljs.py <report-path>`
3. Open it for the user: `open <report-path>` (macOS), `xdg-open` (Linux), `start` (Windows).

## Principles

- State tradeoffs, limitations, and unfinished work plainly.
- Every change gets a "why", not just a "what".
- Quote code; show before→after where possible.
- Hierarchy through typography and spacing, not color.
