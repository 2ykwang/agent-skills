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

```
/decision-board
```

Usually the agent reaches for it on its own once several same-shaped choices pile up. Either way it extracts the decisions, shows you the draft spec for approval, then opens the board at `http://localhost:7117`. You:

1. Review each decision — every option's preview is visible, so you read the rationale before picking.
2. Pick one option per decision (or flag `hold` for follow-up).
3. Submit — or Cancel / ESC to abort.

The agent then reads your picks and applies them (files a PR, updates a doc, etc.). Cancel means no result file: the agent won't fall back to the recommended option, it asks you what to do instead.

Past ~15 decisions the board adds a category filter bar.

## Requirements

- `python3` (standard library only)

## Notes

- Selections auto-save in the browser — a refresh won't lose work. Editing the spec (adding, removing, or renaming a decision) resets the saved state on purpose.
- The port is configurable, and the board can also be written out as a standalone HTML file for offline sharing — that copy has no Submit button.
- The skill never edits your repo; the agent does that after reading your picks.
- One pick per decision. No multi-select, no weights, no dependencies between decisions, no multi-user review.
