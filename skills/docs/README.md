# docs

Writes and maintains code documentation using `[symbol](file-path)` reference pointers instead of inline code blocks, so docs stay resilient to code changes.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install docs@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill docs
```

## When to use

- Document the design intent behind a newly implemented feature
- Record architectural decisions for the project
- Check whether existing docs are still in sync with the codebase

## Usage

```
# Write a document on a topic
/docs write "auth flow design"

# Write with a specific code path for context
/docs write "payment module architecture" src/payment/

# Check all docs for broken refs, stale content, orphan files
/docs check
```

## How it works

**write** — checks for an existing doc on the same topic first (and offers to update it instead of duplicating), reads the code path you gave it or the current conversation for context, picks a category from the folders already there — proposing a new one if nothing fits — writes `docs/generated/<category>/<slug>.md`, and updates `INDEX.md`.

**check** — reads every generated doc's frontmatter and reports four things:

| Check | What it flags |
|---|---|
| Stale | `updated` older than 90 days |
| Broken code refs | a path in `code_refs` that no longer exists in the project |
| Broken doc links | a slug in `related` with no matching document |
| Orphans | a document not linked from `INDEX.md` |

## Output

Documents carry frontmatter — `title`, `category`, `created`, `updated`, `code_refs`, `related` — so `check` can verify them later. The body records design intent, with `[symbol](file-path)` links pointing at the code instead of pasted snippets.

`/docs` with no subcommand prints the usage summary and stops.

## Notes

- On first run it asks before creating `docs/generated/` and its `INDEX.md`.
- Documents are organized by category under `docs/generated/`.
- Manually written docs outside `docs/generated/` are never modified.
