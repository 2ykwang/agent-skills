---
name: decision-board
description: Generate an interactive HTML wizard from a JSON spec when the user has many discrete decisions to make and wants to compare options visually. Each decision becomes a single-screen card with current state, options (with recommended badges), live preview of the chosen option, free-form notes, and rationale toggle. The user steps through decisions in the browser, choices auto-save to localStorage, then exports JSON/Markdown back into the conversation. Use this skill whenever the user has 5+ choice items, mentions "decision sheet", "interactive choices", "options to compare", "pick through these", or asks to turn a list of trade-offs / proposals / audit findings into something they can review visually. Domain-agnostic — works for UX writing audits, architecture decisions, library selection, refactor plans, policy options, design reviews, anything where N items × M options need human judgment.
---

# Decision Board

Generate a single-file interactive HTML wizard from a structured spec. The user steps through decisions one screen at a time, picks options, leaves notes, then exports the result. You then act on the result — write the policy doc, file the PRs, update configs, whatever the decisions imply.

This skill is just for the visualization + collection step. The thinking (extracting decisions, defining options, judging trade-offs) happens before. The acting (applying choices) happens after. The wizard only handles "user looks at N decisions, picks M times".

## When this is the right tool

A decision board is overkill for 1-3 decisions — just ask the user inline. It's underbuilt for collaborative async review by many people — use a Notion / Linear / Google doc for that. The sweet spot is:

- **One person, one sitting** — solo decision-making, not async multi-stakeholder
- **5 to ~30 items** — fewer than 5 is faster as a chat, more than 30 needs filtering or chunking
- **Each decision has comparable structure** — same shape (current state, options, costs). If decisions are wildly different shapes, prose is better.
- **Visual comparison helps** — the trade-off is hard to grasp in one line, the user wants to *see* before/after or hovering between options

If those conditions don't hold, push back: suggest inline Q&A or a different format instead of building a wizard the user won't enjoy.

## Workflow

### Step 1 — Build the spec

The user typically arrives with the decisions already identified (in conversation, in a markdown audit, in their head). Convert that material into a `spec.json` matching the schema below. Keep `current_example` and `options[].preview` rich — they're what makes the wizard worth using over a plain table. If the user hasn't given you previews, ask them or draft them yourself.

The spec is plain JSON. Keep it human-editable so the user can tweak it without re-running you.

### Step 2 — Run serve.py

One command renders the wizard, opens the browser, and exposes a Submit endpoint. When the user clicks Submit the JSON result is written to disk — no copy/paste step needed.

```bash
python "${SKILL_DIR}/scripts/serve.py" path/to/spec.json
# → opens http://localhost:7117 in the browser
# → user decides and clicks Submit
# → writes path/to/spec.<timestamp>.result.json next to the spec
# → press Ctrl+C in the terminal when you're done
```

`serve.py` is stdlib-only (`http.server`), no third-party packages. Common flags:

- `--port N` — alternate port (default 7117). The script kills any prior holder of the port at startup; if that fails it falls back to an OS-assigned port.
- `--output PATH` — pin the result path (default uses a timestamp so multiple runs don't overwrite each other).
- `--no-open` — don't auto-open the browser.
- `--static board.html` — skip the server entirely and write a single self-contained HTML file. Use this only when the user wants to share the wizard, archive it, or open it offline; the file has no Submit button — they'll need to use the Copy Markdown / Copy JSON buttons and paste back.

`SKILL_DIR` is the directory this SKILL.md lives in.

### Step 3 — User makes the decisions

The wizard is keyboard-friendly: `←` / `→` to navigate, `1`-`9` to pick options, `h` to hold, `k` to skip, `r` toggles reasoning, `?` shows shortcuts. Selections auto-save to localStorage (per spec title) so closing the tab doesn't lose work. The footer offers **Copy Markdown**, **Copy JSON**, and — only when the page is served over HTTP — a **Submit** button that POSTs to `/api/submit`.

### Step 4 — Receive the result

- **Server mode (default):** read the file at `--output` (or whatever timestamp path was printed at startup). The Submit endpoint already wrote it. Once the user tells you they clicked Submit, parse the JSON and act on it.
- **Static mode (`--static`):** the user pastes Markdown or JSON back into chat. Parse from there.

Either way, each decision in the result is one of:
- a chosen option key (`"a"`, `"b"`, ...)
- `"hold"` — flagged for follow-up
- `"skip"` — explicitly skipped
- `null` — undecided

…plus an optional `comment` string the user typed in the notes field.

Then do the actual work the decisions imply. Don't just acknowledge the choices — apply them.

## Spec schema

```json
{
  "title": "string (required) — top header",
  "subtitle": "string (optional) — one-line context",
  "categories": ["wording", "format", "policy"],  // optional — enables the filter bar
  "decisions": [
    {
      "id": 1,                          // required, must be unique within the spec
      "title": "string (required)",
      "summary": "string (optional) — one-line gist shown above current state",
      "category": "string (optional) — must match categories[] if used",
      "current_example": "HTML string (optional) — rendered in the 'before' box",
      "options": [
        {
          "key": "a",                   // required, single letter or short token
          "label": "HTML string (required) — what the option means",
          "cost": "string (optional) — '4 lines / 4 files' style estimate",
          "recommended": true,          // optional — adds a badge
          "preview": "HTML string (optional) — rendered when this option is picked"
        }
      ],
      "rationale": "HTML string (optional) — shown under 'show reasoning' toggle"
    }
  ]
}
```

**Why HTML strings for examples and previews:** the spec author often wants monospace boxes, colored diffs, multi-line ASCII mock-ups. Trying to escape that into JSON-safe markdown is painful, and the wizard already runs in a browser. Just write `<pre>` with `<span class="hl-add">+ new</span>` / `<span class="hl-del">- old</span>` / `<span class="hl-note">comment</span>` for diff-style highlighting. The template ships these classes.

`serve.py` rejects anything obviously malformed up front (missing `id`, `title`, or `options`; non-unique ids; categories listed but unused). Other validation is loose — keep it permissive, the user is the only consumer.

See `references/spec_minimal.json` for a 3-decision example you can show users to get them started.

## Templates and assets

- `assets/wizard_template.html` — the renderer. Don't edit per-skill-invocation. If the user wants a different layout (table, cards, split view), that's a different skill or a future addition.
- `scripts/serve.py` — single entry point. Validates the spec, renders, serves, and optionally writes a static file.
- `references/spec_minimal.json` — minimal valid spec for reference.

## Common patterns

**User's input is unstructured prose / a markdown audit.** Read it, extract decisions, draft a spec, show them the spec for approval before rendering. Don't render and hope.

**User wants to add decisions later.** They edit `spec.json` — `serve.py` re-renders on every page reload, so they just refresh the tab. localStorage keys off the spec title, so adding decisions preserves prior choices. Renaming the title resets.

**Categories matter for >15 decisions.** Add a `categories` array. The filter bar appears automatically. Without categories the bar is hidden.

**Some decisions have no obvious recommendation.** Just omit `recommended: true` from all options. The wizard handles it gracefully — no badge appears, the user has to actively choose.

**Preview is too complex for HTML in JSON.** Write it as a separate file and reference it with a `<<<file:preview-1a.html>>>` token inside the spec. Pass `--preview-dir DIR` to `serve.py` (defaults to the spec's directory) and the token is replaced with the file contents at render time.

**Multiple boards open at the same time.** Each `serve.py` invocation kills any process holding its requested port at startup, then falls back to an OS-assigned port if the kill failed. Result paths default to a timestamped name (`spec.<YYYYMMDD-HHMMSS>.result.json`) so concurrent or repeated runs against the same spec don't clobber each other. Pin a path with `--output` if you need a stable name for follow-up work.

## What this skill explicitly does *not* do

- Multi-user / collaborative review — single localStorage, no sync
- Persistent server state — everything is client-side
- Decision dependencies (if A then B) — the user picks each independently
- Rich-text editing in notes — plain textarea
- Programmatic apply (the user always copies → pastes back)

If the user asks for any of those, that's a sign the tool doesn't fit. Suggest a different approach instead of stretching this one.
