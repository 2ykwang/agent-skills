**English** | [한국어](README.ko.md)

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

Three parts:

1. **Timeline table** — date, author, commit, PR, and the change per entry. Each entry states the change type (added / modified / refactored / moved / deleted / restored) and its intent (bug fix / feature / refactoring / performance / cleanup / migration).
2. **Detailed analysis** — for each significant change: a before/after summary, the intent behind it, and what changed in behavior or interface.
3. **Insights** — the evolution arc, and concrete issues visible in the history: reverted changes, the same area patched repeatedly, commit messages that don't match their diff. Only when the history actually supports them.

## Requirements

- `git`
- `gh` CLI — optional. Without it, PR links come from commit messages alone.

## Notes

- Read-only — never modifies code.
- Above ~30 matching commits, the scope narrows (by file or date) and the truncation is stated in the output.
- Not a replacement for `git blame` on a single line, or `git show` on one commit — this is for tracing a change across its whole history.
