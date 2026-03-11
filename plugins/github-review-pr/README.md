# github-review-pr

Analyze a GitHub pull request and produce a review report covering changes, review status, and code quality.

## When to use

- Reviewing a PR before approving or requesting changes
- Getting a quick overview of a large PR
- Summarizing review status and unresolved comments

## Usage

```
/github-review-pr 456
/github-review-pr https://github.com/owner/repo/pull/456
```

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install github-review-pr@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill github-review-pr
```
