# code-review-report

Turns your changes into a single-file HTML report that pairs the diff with the context a diff can't show — why each change was made, rejected alternatives, tradeoffs, unfinished work — plus prioritized review points.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install code-review-report@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill code-review-report
```

## When to use

- Preparing for review after a sizable change, refactor, or feature
- Want reviewers to see the reasoning behind changes, not just the diff
- Need a shareable, self-contained HTML summary of what changed

## Usage

```
/code-review-report
```

Best run in the conversation where the change was made — that's where the "why" lives. Default scope is the current branch vs. the default branch, plus uncommitted work.

## How it works

1. Collects the change — committed diff, uncommitted work, and untracked files.
2. Gathers the context a diff never records — decisions, rejected alternatives, tradeoffs, unfinished work.
3. Extracts prioritized (P1–P3) review points.
4. Writes a self-contained HTML report and opens it.

## Output

A single HTML file (`<task>-review-report.html`) in the project root: syntax-highlighted diff, the context behind each change, and a P1–P3 review checklist with links between each change and its review points. Self-contained and offline-friendly.

## Requirements

- `git`
- `python3` (standard library only)

## Notes

- Read-only on your code — only writes the HTML report.
