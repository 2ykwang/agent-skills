# django-ticket-triage

Analyzes a Django Trac ticket and produces a triage recommendation report — including duplicate search, related PRs, forum discussions, and source code analysis.

## When to use

- Triaging tickets as a Django contributor
- Quickly assessing a ticket's validity, duplicates, and related discussions
- Writing a triage report for a new or existing ticket

## Usage

```
/django-ticket-triage 36812
```

## What it does

1. **Fetch ticket details** — pulls ticket info, history, and comments from Trac
2. **Search duplicates** — searches Trac by keywords, error messages, and component
3. **Find related PRs** — searches GitHub for PRs referencing the ticket
4. **Check forum discussions** — searches Django Forum for related threads
5. **Browse source code** — locates the problematic code and checks test coverage
6. **Assess validity** — evaluates against bug/feature checklists
7. **Recommend triage stage** — suggests Unreviewed, Accepted, Ready for checkin, etc.

The full report is saved to `triage-reports/<ticket_id>.md`.

## Requirements

- `python3` with `requests` package
- `gh` CLI (authenticated)
- Django source checkout (`git clone https://github.com/django/django.git`)

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install django-ticket-triage@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill django-ticket-triage
```
