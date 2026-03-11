# github-review-check-duplicate

Check if a GitHub issue is a duplicate and find related issues and PRs.

## When to use

- A new issue is filed and needs duplicate checking before triage
- Searching for existing issues or PRs related to a specific issue
- Deciding whether to close an issue as a duplicate

## Usage

```
/github-review-check-duplicate 789
/github-review-check-duplicate https://github.com/owner/repo/issues/789
```

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install github-review-check-duplicate@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill github-review-check-duplicate
```
