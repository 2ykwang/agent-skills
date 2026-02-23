# docs

Writes and maintains code documentation using `[symbol](file-path)` reference pointers instead of inline code blocks, so docs stay resilient to code changes.

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

- **write** — Analyzes the relevant code path and generates a document under `docs/generated/<category>/`. Automatically updates `INDEX.md`.
- **check** — Scans all generated docs for broken code references, outdated content, and orphan documents. Reports findings.

## Notes

- Documents are organized by category under `docs/generated/`.
- Manually written docs outside `docs/generated/` are never modified.

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
