## Installation

- **Skills CLI**: `npx skills add 2ykwang/agent-skills`
- **Plugin Marketplace**: `claude plugin marketplace add 2ykwang/agent-skills`

---

| Skill | |
|---|---|
| [code-history](skills/code-history) | Trace git history of specific code — find when functions, patterns, or files were added, modified, or removed, and explain the intent behind each change. |
| | `npx skills add 2ykwang/agent-skills --skill code-history` |
| | `claude plugin install code-history@2ykwang-agent-skills` |
| [docs](skills/docs) | Code documentation agent — write/update docs with /docs write, check status with /docs check. Minimal code blocks, reference pointer based. |
| | `npx skills add 2ykwang/agent-skills --skill docs` |
| | `claude plugin install docs@2ykwang-agent-skills` |
| [github-review-check-duplicate](skills/github-review-check-duplicate) | Check if a GitHub issue is a duplicate and find related issues and PRs. |
| | `npx skills add 2ykwang/agent-skills --skill github-review-check-duplicate` |
| | `claude plugin install github-review-check-duplicate@2ykwang-agent-skills` |
| [github-review-issue](skills/github-review-issue) | Analyze a GitHub issue and provide a structured summary with next-action assessment. |
| | `npx skills add 2ykwang/agent-skills --skill github-review-issue` |
| | `claude plugin install github-review-issue@2ykwang-agent-skills` |
| [github-review-pr](skills/github-review-pr) | Analyze a GitHub pull request and produce a review report covering changes, review status, and code quality. |
| | `npx skills add 2ykwang/agent-skills --skill github-review-pr` |
| | `claude plugin install github-review-pr@2ykwang-agent-skills` |
| [django-ticket-triage](skills/django-ticket-triage) | Analyze a Django Trac ticket and produce a triage recommendation report. |
| | `npx skills add 2ykwang/agent-skills --skill django-ticket-triage` |
| | `claude plugin install django-ticket-triage@2ykwang-agent-skills` |
| [html-visual](skills/html-visual) | Generate interactive single-file HTML visualizations — UI mockups, ERDs, flowcharts, data charts. |
| | `npx skills add 2ykwang/agent-skills --skill html-visual` |
| | `claude plugin install html-visual@2ykwang-agent-skills` |
| [ralph-loop-template](skills/ralph-loop-template) | Generate Ralph Loop iteration checklists from plan files. Creates `PROMPT-*.md` files ready for `/ralph-loop`. |
| | `npx skills add 2ykwang/agent-skills --skill ralph-loop-template` |
| | `claude plugin install ralph-loop-template@2ykwang-agent-skills` |
| [write-pr](skills/write-pr) | Analyzes git diff and commit history to write PR title and description based on the project's PR template. |
| | `npx skills add 2ykwang/agent-skills --skill write-pr` |
| | `claude plugin install write-pr@2ykwang-agent-skills` |

---
