# write-pr

Analyzes the git diff and commit history to draft a PR title and description that matches the project's conventions.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install write-pr@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill write-pr
```

## When to use

- About to open a PR and need a well-structured title and description
- Too many changes to summarize by hand
- Want the PR to match the project's existing template and title style

## Usage

```
# Against the default base branch (auto-detected)
/write-pr

# Against a specific base branch
/write-pr develop
```

## How it works

1. Auto-detects the base branch (or uses the one you specify).
2. Reads the commits and the diff. Large changes (over 20 files or 500 changed lines) aren't read in full — it picks the heaviest file per directory and reads those instead.
3. Finds the project's PR template — `.github/PULL_REQUEST_TEMPLATE.md` and the usual alternatives — and preserves its structure exactly, including HTML comments in sections it can't fill (Screenshots, Related Issues).
4. Matches the project's title convention from merged PR titles (`gh pr list`), falling back to recent commit messages.
5. Focuses on **why** the change was made, not just what files changed, and flags breaking changes, new dependencies, and structural changes explicitly.

## Output

A ready-to-paste PR title and body.

- **Title** — follows whatever convention the project already uses. When that convention is mixed or unclear, you get 2–3 labeled candidates instead of one, and Conventional Commits (e.g. `feat(auth): add OAuth2 login support`) is the fallback.
- **Body** — the project's template filled in. With no template found: Summary / Changes / Test Plan.
- A footer line with the base ← current branch, commit count, and files changed.

## Notes

- Read-only — does not create a PR or push anything. Copy the output when opening your PR.
