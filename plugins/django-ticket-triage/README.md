# django-ticket-triage

Analyzes a Django Trac ticket and produces a triage recommendation report — duplicate search, related PRs, forum discussions, and source-code analysis.

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

## When to use

- Triaging tickets as a Django contributor
- Assessing a ticket's validity, duplicates, and related discussions
- Writing a triage report for a new or existing ticket

## Usage

```
/django-ticket-triage 36812
```

## How it works

1. Fetches ticket info, history, and comments from Trac.
2. Searches Trac for duplicates by keyword, error message, and component.
3. Finds GitHub PRs referencing the ticket.
4. Checks the Django Forum for related threads.
5. Locates the affected source code and checks test coverage.
6. Assesses validity against bug/feature checklists.
7. Recommends a triage stage (Unreviewed, Accepted, Ready for checkin, etc.).

## Output

The full report is saved to `triage-reports/<ticket_id>.md`.

## Requirements

- `python3` (standard library only)
- `gh` CLI (authenticated)
- Django source checkout (`git clone https://github.com/django/django.git`)
