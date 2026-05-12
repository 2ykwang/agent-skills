# decision-board

**When the agent needs the user to pick among many similar one-of-N choices, a chat thread is the wrong medium.** Options scroll past as they appear; previews can't sit side-by-side; the user can't scan all of them before clicking one. This skill puts every option on a single HTML page with previews always visible, captures the user's picks (with optional `hold` flags and per-decision notes), and returns the result as a JSON file the agent can apply directly.

## When to use

- You have **multiple `one-of-N` choices** that share the same option shape (label, optional cost, preview).
- **Seeing each option's preview side-by-side** helps the choice — a single sentence wouldn't capture it.
- One person, one sitting — not async multi-stakeholder review.
- Domain-agnostic: engineering trade-offs, copy or design audits, policy or process calls, action-item triage.

If the items don't share a structure, or the choice fits in one inline sentence, prose / a single inline question is faster.

## Usage

```bash
python "${CLAUDE_SKILL_DIR}/scripts/serve.py" path/to/spec.json
```

Opens `http://localhost:7117`. The user makes picks and clicks Submit (or Cancel / ESC). The server writes the result to disk and exits.

Two flags worth knowing (`--help` for the rest):
- `--output PATH` — pin the result path (default is timestamped).
- `--static PATH` — write a standalone HTML file and exit instead of serving.

## How it works

```
┌─────────────┐     spec.json     ┌─────────────┐
│  agent      │ ────────────────► │  serve.py   │
└─────────────┘                   └──────┬──────┘
       ▲                                 │ renders + serves
       │                                 ▼
       │                          ┌─────────────┐
       │ result.json + exit code  │   browser   │ ◄── user picks
       └──────────────────────────┤   (board)   │
                                  └─────────────┘
```

1. **Agent builds a `spec.json`** — title + list of decisions, each with options.
2. **`serve.py` validates the spec and starts an HTTP server** on `localhost:7117`. It prints `RESULT_PATH=…` and `PORT=…` on stdout so the agent knows where to read the result and which port the browser should hit.
3. **The browser opens the board.** The user sees all decisions in a sidebar, picks options (each option's preview is always visible — the user reads the rationale *before* picking), and either Submits or Cancels.
4. **The server exits** with a code that tells the agent how the session ended (see `references/result-handling.md`):
   - `0` Submit → `result.json` written
   - `125` Cancel (button or ESC)
   - `124` Heartbeat timeout (browser gone for ~60s)
   - `130` Ctrl+C in the terminal
   - `1` Spec failed validation
5. **The agent reads `result.json`** (only on exit 0) and applies the picks — files a PR, updates a doc, writes the recap email, whatever the decisions imply.

## Spec at a glance

```json
{
  "title": "What to ship this sprint",
  "decisions": [
    {
      "id": "auth-flow",
      "title": "Auth refactor approach",
      "context": "```python\n# current: synchronous, blocking\n```",
      "options": [
        { "key": "a", "label": "Keep current", "cost": "0", "recommended": true },
        { "key": "b", "label": "Migrate to async", "cost": "~2d", "reversibility": "hard" }
      ],
      "rationale": "Throughput vs complexity trade-off."
    }
  ]
}
```

All string fields are markdown. Block markdown (headings, lists, fenced code, ` ```diff `) works inside `context` / `preview` / `rationale`. Inline markdown (`**bold**`, `*em*`, `` `code` ``) works everywhere.

Full schema and field semantics live in [`SKILL.md`](SKILL.md). Agent-side handling for every exit code, partial submits, and `hold` semantics live in [`references/result-handling.md`](references/result-handling.md).

## Result

```json
{
  "title": "...",
  "submitted_at": "2026-05-11T08:10:33Z",
  "decisions": {
    "auth-flow": { "choice": "b", "comment": "" }
  },
  "meta": { "counts": { "decided": 1, "hold": 0, "undecided": 0 } }
}
```

- `choice` is an option `key`, `"hold"`, or `null`.
- `null` means the user submitted without picking — the agent should surface unresolved items, not silently default.
- `hold` means flagged for follow-up.

## Notes

- Stdlib-only Python — no third-party dependencies.
- Self-contained HTML — Google Fonts is the only external resource.
- Selections auto-save to `localStorage` keyed on title + decision ids, so refreshing the tab preserves work and changing the spec invalidates stale state.
- The skill never edits files in the user's repo — the agent does that, after reading the result.
