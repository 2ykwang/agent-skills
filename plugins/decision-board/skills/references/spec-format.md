# Spec format

Everything you need to write a `spec.json` for `decision-board` — full schema, field semantics, markdown grammar, and three end-to-end examples across domains.

`SKILL.md` covers the workflow; this file is the reference the agent loads when actually building the spec.

## Schema

Every field is optional except `id` / `title` / `options[].key` / `options[].label`. The board renders whatever fields you provide; omit what doesn't fit your domain.

```json
{
  "title": "string (required)",
  "subtitle": "string (optional)",
  "categories": ["wording", "format"],
  "decisions": [
    {
      "id": 1,
      "title": "string (required)",
      "summary": "string (optional)",
      "category": "string (optional, must be in categories[])",
      "context": "string (optional)",
      "options": [
        {
          "key": "a",
          "label": "string (required)",
          "cost": "string (optional)",
          "reversibility": "easy | hard (optional, engineering-flavored)",
          "recommended": true,
          "preview": "string (optional)"
        }
      ],
      "rationale": "string (optional)"
    }
  ]
}
```

### Field semantics

- **`id`** — number or string; the server coerces it to a string for everything downstream (result map keys). `"id": 1` and `"id": "1"` are equivalent.
- **`context`** — the user's decision background. The board renders this above the options. See length guideline in `SKILL.md` Step 1.
- **`summary`** — one-line trade-off shown under the title. Useful when the title alone doesn't convey the tension.
- **`options[].cost`** — free string. Use the units that make sense for your domain (`work 0`, `~2d`, `risk hard`, `+1 dep`, `warmer tone`). Omit for domains where "cost" doesn't apply.
- **`options[].reversibility`** — `"easy"` or `"hard"`. Engineering-flavored — omit for non-engineering specs. Use when "we can change it later" vs "this locks us in" is the real axis.
- **`options[].recommended`** — boolean. At most one option per decision should be recommended.
- **`options[].preview`** — the decision evidence; see length guideline in `SKILL.md` Step 1.
- **`rationale`** — block markdown shown below the options. Use to explain *why* one option is recommended over the others.

The server validates: `id` presence and uniqueness, `title` presence, `options` non-empty, option `key` uniqueness within a decision, declared-but-unused categories, the `reversibility` enum. Everything else is permissive.

## Markdown grammar

All string fields are markdown.

- **Inline** (`title` / `summary` / `label` / `cost`): `**bold**`, `*em*`, `` `code` ``, `~~strike~~`.
- **Block** (`context` / `preview` / `rationale`): the inline tokens plus headings (`#`–`###`), bullet and numbered lists, blockquotes (`>`), fenced code blocks (` ```lang `), and a special ` ```diff ` mode that highlights `+`/`-` prefixed lines.
- **Inline HTML allowlist**: `<mark>`, `<ins>`, `<del>`, `<kbd>`. Anything else is escaped.

### Before / after — the same option, written each way

Don't write spec strings as escaped HTML — markdown is cleaner:

```
"label": "<b>requests</b> + manual retry",
"cost":  "<code>0 deps</code>; ~30 lines"
```
becomes
```
"label": "**`requests`** + manual retry",
"cost":  "`0 deps` · ~30 lines"
```

## Examples

Each example shows source material → the resulting `decisions[]` shape.

### Engineering — Architecture decision (ADR-style)

> Should `billing-worker` migrate to async or stay sync?

```json
{
  "id": "billing-async", "title": "billing-worker concurrency model",
  "context": "```python\ndef process(charge):  # sync, blocking\n    api.charge(charge)\n```",
  "options": [
    {
      "key": "a", "label": "Keep sync", "cost": "0 work", "reversibility": "easy",
      "preview": "No code change. Existing throughput stays at ~120 req/s under load test. The async migration remains an option but no current blockers get fixed."
    },
    {
      "key": "b", "label": "Migrate to `asyncio`",
      "cost": "rewrite 3 modules · ~2d", "reversibility": "hard",
      "preview": "```diff\n- def process(charge):\n-     api.charge(charge)\n+ async def process(charge):\n+     await api.charge(charge)\n```\n\nDownstream changes:\n- `billing_worker.py`: event-loop migration\n- replace `requests` with `httpx`\n- 12 call sites in `services/` need `await`\n- new dependency: `anyio` for the test harness"
    }
  ],
  "rationale": "## What we're optimizing for\n\nThroughput at the cost of code complexity, or the inverse."
}
```

### Prose / copy — UX writing audit

> Empty-state copy on the inbox screen.

```json
{
  "id": "inbox-empty", "title": "Inbox empty state",
  "context": "**Current:** *You have no messages.*",
  "options": [
    { "key": "a", "label": "Nothing here yet — when teammates write, it'll land here.",
      "cost": "warmer tone", "recommended": true },
    { "key": "b", "label": "No messages.", "cost": "terse" },
    { "key": "c", "label": "(no copy, illustration only)", "cost": "depends on art" }
  ]
}
```

### Operations / process — Meeting action triage

> "Spike a Slackbot integration" — what do we do with it?

```json
{
  "id": "slackbot-spike", "title": "Spike: Slackbot integration",
  "context": "Floated in Tuesday's standup; no owner yet.",
  "options": [
    { "key": "a", "label": "Do this week (assign owner today)", "recommended": true },
    { "key": "b", "label": "Defer 30 days — revisit at next planning" },
    { "key": "c", "label": "Drop entirely (won't pursue)" }
  ]
}
```
