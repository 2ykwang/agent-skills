# write-pr

Analyzes git diff and commit history to draft a PR title and description that matches the project's conventions.

## When to use

- About to open a PR and need a well-structured title and description
- Too many changes to summarize manually
- Want the PR to match the project's existing PR template and title style

## Usage

```
# Analyze changes against the default base branch (auto-detected)
/write-pr

# Specify a base branch
/write-pr develop
```

## Output example

**Title**
```
feat(auth): add OAuth2 login support
```

**PR Body**
```markdown
## Summary
Adds OAuth2-based social login with Google and GitHub providers...

## Changes
- Implement OAuth2 auth flow (`src/auth/oauth.py`)
- Add per-provider callback handlers
- ...

## Test Plan
- [ ] Verify Google login works end-to-end
- [ ] ...
```

## How it works

1. Auto-detects the base branch (or uses the one you specify).
2. Finds `.github/PULL_REQUEST_TEMPLATE.md` and preserves its structure.
3. Analyzes merged PR titles to match the project's naming convention.
4. Focuses on **why** the change was made, not just what files changed.

## Notes

- Read-only — does not create a PR or push anything.
- Copy the output and paste it when creating your PR.

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
