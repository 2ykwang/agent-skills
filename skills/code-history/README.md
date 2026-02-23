# code-history

Traces the git history of specific code and explains the intent behind each change.

## When to use

- Understand how a function or method evolved over time
- Find which commit/PR introduced, modified, or removed a piece of code
- Investigate why code changed and what motivated each revision
- Spot patterns like repeated patches to the same area

## Usage

```
# Trace by function name
/code-history ensure_valid_state

# Trace by code pattern
/code-history "user['type'] == 'ADMIN'"

# Trace by file path
/code-history src/auth/services.py
```

## Output

A timeline table with detailed analysis per change:

| # | Date | Author | Commit | PR | Change |
|---|------|--------|--------|----|--------|
| 1 | 2024-03-15 | alice | `abc1234` | #42 Auth refactor | Added — initial implementation |
| 2 | 2024-05-20 | bob | `def5678` | #87 Fix validation | Modified — added input check |

Each entry includes change type (Added/Modified/Deleted), intent (feature/bugfix/refactor), and before/after diff summary.

## Notes

- Read-only — never modifies code.
- Automatically links commits to PRs when `gh` CLI is available.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install code-history@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill code-history
```
