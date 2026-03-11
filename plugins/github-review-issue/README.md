# github-review-issue

Analyze a GitHub issue and provide a structured summary with next-action assessment.

## When to use

- Understanding what an issue is about before working on it
- Summarizing a long issue thread with many comments
- Assessing what action is needed to move an issue forward

## Usage

```
/github-review-issue 123
/github-review-issue https://github.com/owner/repo/issues/123
```

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install github-review-issue@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill github-review-issue
```
