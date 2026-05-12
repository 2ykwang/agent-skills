---
name: decision-board
version: 0.1.0
category: productivity
description: Render an interactive HTML board for the user to pick among multiple comparable options side-by-side at once — engineering trade-offs, copy audits, action-item triage, architecture decisions, policy calls. Returns the picks (and optional hold/note flags) as a JSON file the agent can apply.
---

# Decision Board

Render a single-file HTML board from a JSON spec, wait for the user to pick, read the result. Then apply the picks — write the doc, file the PRs, update configs, whatever the choices imply.

This skill only handles the picking step. Extracting decisions and judging trade-offs happens before; applying choices happens after.

## When to use this skill

The trigger is **structural fit, not domain and not count**. In order of importance:

1. **Same option shape across items.** Every item is `one-of-N` over options that share fields (label, optional cost / preview). If each item needs a custom shape, prose is better.
2. **Preview is worth seeing.** The user benefits from looking at each option's preview side-by-side rather than reading prose. If a single sentence captures the choice, inline Q&A is faster.
3. **One person, one sitting.** Solo decision-making, not async review.

Item count is the weakest signal — roughly 5–30 is the typical sweet spot, but a well-structured 4-item case can still earn the board while a 10-item bag of unrelated questions doesn't. **Fit beats count.**

If the structural fit doesn't hold, push back and suggest a different format.

## Workflow

The skill processes a session in five steps. Each step has a clear handoff — the agent owns 1, 2, 4, 5; the user owns 3.

### 1. Extract decisions from the user's material

The user usually arrives with unstructured material — a meeting recap, an audit document with conflicting paragraphs, a chat thread, a list in their head. Pull each decision out as a unit with four pieces:

- **What is being decided** (one-line title).
- **The current state or conflict** — actual code, the quoted paragraphs, the existing behavior. This becomes the decision's `context`.
- **The candidate options** — at least two, each with a short label and what changes if it's picked. This becomes `options[].label` + `options[].preview`.
- **What you'd recommend and why** — if the agent has an opinion, mark one option `recommended` and put the reasoning in `rationale`.

Skip this step only when the user already came with a structured list of decisions and options.

### 2. Build the spec

Convert the extracted decisions into a `spec.json`. See [`references/spec-format.md`](references/spec-format.md) for the full schema, field semantics, markdown grammar, and three end-to-end examples (engineering ADR, prose audit, operations triage).

Minimal shape — everything else is optional:

```json
{
  "title": "ADR-2026-05",
  "decisions": [
    {
      "id": "auth-storage",
      "title": "Where do we store the session?",
      "context": "Today we keep the token in localStorage…",
      "options": [
        {"key": "a", "label": "httpOnly cookie", "preview": "…"},
        {"key": "b", "label": "Keep localStorage", "preview": "…"}
      ],
      "recommended": "a",
      "rationale": "Cuts XSS exposure"
    }
  ]
}
```

Two length guidelines that determine whether the user can actually pick:

- **`context`** is the user's decision background, not just "the thing that's wrong". Aim for **5–15 lines of markdown** with the current behavior, conflicting documents or code, who's affected, and what assumption breaks. A 2-line citation leaves the user with no ground to pick from.
- **`options[].preview`** is the user's decision evidence, not a label. Aim for **5–15 lines of markdown** — the diff, the resulting code, the policy text in full, the call sites that change. If two options' previews would read the same way at a glance, the user can't pick from previews alone.

**Show the spec to the user and get approval before rendering.** A render miss costs page reload + localStorage cleanup; an approval miss is one chat message.

### 3. Run serve.py and wait for the user

The command **blocks until the user submits or cancels** — that's the intended invocation. The process's exit code is the signal back to the agent, not a user message.

```bash
python "${CLAUDE_SKILL_DIR}/scripts/serve.py" path/to/spec.json --output result.json
```

Invoke the script with whatever long-running-command pattern your host supports — a background process plus a completion notification, or a blocking subprocess call with a generous timeout. **Do not ask the user "let me know when you're done"; the process exit is the signal.** When the process exits, branch on the exit code (see the Result schema below) and read `result.json` only when it's 0.

> `serve.py` binds port 7117 by default and will `SIGTERM` any existing process holding that port. Use `--port N` to override.

The first two stdout lines are machine-parseable:

```
RESULT_PATH=/abs/path/to/spec.20260511-093000.result.json
PORT=7117
```

The `PORT` line matters when the requested port was busy and we fell back to an OS-assigned one — capture it if you need to surface the board URL to the user. Capture both, then wait for the process to exit. The exit code tells the agent how the session ended:

| Exit | Meaning | `result.json` | What the agent should do |
|---:|---|---|---|
| **0** | Submit clicked | written | read the result, apply the picks |
| **1** | spec invalid | not written | fix the spec, retry |
| **124** | heartbeat timeout (browser gone for ~60s+) | not written | tell the user we lost contact; offer to retry |
| **125** | user clicked Cancel (or ESC) | not written | the user said no — do not push back, ask if they want a different approach |
| **130** | user pressed Ctrl+C in the terminal | not written | treat the same as 125 (explicit abort) |

The agent contract: `0` is the only "we have picks" outcome. Everything else means no result file and the agent should explain to the user what happened.

Two flags worth knowing (`--help` for the rest):

- `--output PATH` — pin the result path. Default is timestamped so repeat runs don't overwrite.
- `--static PATH` — write a standalone HTML file and exit instead of serving. Use for offline sharing / archiving; the static file has no Submit button.

### 4. Branch on the exit code

When the process exits, the exit code tells the agent which path to take. The summary table above is the contract; the full reasoning per code (including partial-submit handling and `hold` semantics) lives in [`references/result-handling.md`](references/result-handling.md).

Four rules that hold across every exit code:

- Read `result.json` only when exit code is `0`. For 124 / 125 / 130 the file does not exist.
- Don't invent picks. If the user cancelled or disconnected, the agent acknowledges that and asks what to do next — it does not silently default to the recommended option.
- Don't ask the user "are you done?" The exit code is the signal.
- Exit-code branching overrides surrounding defaults. Exit 0 with an explicit `choice` is the user's confirmation — apply without an extra "shall I proceed?" prompt. Exit 124 / 125 / 130 and `null` choices are never replaced by `recommended` or any other fallback.

### 5. Apply the picks

For exit 0, read `result.json` and act on each decision. The shape:

```json
{
  "title": "ADR-2026-05",
  "submitted_at": "2026-05-12T09:30:00Z",
  "decisions": {
    "<decision-id>": {
      "choice": "a",
      "hold": false,
      "note": ""
    }
  }
}
```

`choice` is `null` when the user submitted without picking; `hold` flags a follow-up; `note` is plain text. Full semantics (partial submits, hold workflows) in [`references/result-handling.md`](references/result-handling.md).

The skill itself never edits the user's repo — applying the picks is the agent's job. Examples by domain:

- **Engineering decisions** → open the PR, edit the configs, run the migration, update the dependency.
- **Copy / design audits** → write the changes into the relevant files, draft the review comment, file the issues.
- **Operations / process** → write the recap email, file the follow-up tickets, schedule the deferred items, update the planning doc.
- **`hold` choices** → surface them as follow-ups (not silent), e.g. add to a TODO file or open tracking issues.
- **`null` choices** → surface to the user; do not treat as default. Ask whether to defer, re-run the board, or just leave undecided.

## Patterns

**Unstructured input.** Extract decisions, draft the spec, get approval, then render. Don't render and hope.

**Adding decisions later.** User edits `spec.json` and refreshes the tab. localStorage is keyed on the spec **title + decision ids**, so adding/removing/renaming a decision invalidates the key and starts fresh. Renaming an option `key` is also caught at restore time and resets that decision's choice (the stored value is no longer a valid option).

**>15 decisions.** Add a `categories` array. The filter bar appears automatically.

## Out of scope

- **Single pick per decision.** No multi-select, no weighted choices. If the user needs to pick two options or assign weights, use a survey tool — this skill models "one of N".
- **Multi-user sync / async collaboration.** Single localStorage, single Submit, no presence.
- **Persistent server state.** Everything client-side; the server exits on Submit.
- **Decision dependencies** (if A then B). Each decision is picked independently. Show dependencies in the `summary` text instead.
- **Rich-text notes.** The comment field is plain text.
- **Programmatic apply.** The agent reads the result and does the work — the board never edits the user's repo.

If the user asks for any of these, suggest a different tool. This skill is a single-session picking channel, not collaboration infrastructure.
