# code-history

Traces the git history of specific code and explains the intent behind each change — when it was added, modified, or removed, and why.

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

## When to use

- Understand how a function or file evolved over time
- Find which commit or PR introduced, changed, or removed a piece of code
- Investigate the motivation behind each revision

## Usage

```
# By function name
/code-history ensure_valid_state

# By code pattern
/code-history "user['type'] == 'ADMIN'"

# By file path
/code-history src/auth/services.py
```

## Output

A timeline table — date, author, commit, PR, and change per entry. Each entry states the change type (added / modified / deleted), the intent (feature / bugfix / refactor), and a before/after summary.

## Notes

- Read-only — never modifies code.
- Links commits to their PRs when the `gh` CLI is available.
