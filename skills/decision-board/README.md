# decision-board

Puts several comparable one-of-N choices on a single HTML board with previews side by side, so you pick them all in one sitting instead of scrolling a chat thread. Returns your picks as JSON the agent applies.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install decision-board@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill decision-board
```

## When to use

- Several one-of-N choices that share the same shape (label, optional cost, preview)
- Seeing each option's preview side by side helps the call — a sentence wouldn't
- One person, one sitting — not async multi-stakeholder review

## Usage

The agent builds the board and opens it at `http://localhost:7117`. You:

1. Review each decision — every option's preview is visible, so you read the rationale before picking.
2. Pick one option per decision (or flag `hold` for follow-up).
3. Submit — or Cancel / ESC to abort.

The agent then reads your picks and applies them (files a PR, updates a doc, etc.).

## Requirements

- `python3` (standard library only)

## Notes

- Selections auto-save in the browser — a refresh won't lose work.
- The skill never edits your repo; the agent does that after reading your picks.
