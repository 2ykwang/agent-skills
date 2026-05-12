# Result recovery — agent-side handling

How the agent should interpret what `serve.py` returns, and what to do in the edge cases. SKILL.md keeps the schema brief; this file is the reference for everything that can go wrong.

## Exit code matrix

The server prints `RESULT_PATH=…` (and `PORT=…`) on stdout, then runs. The exit code tells you how the session ended.

| Exit | Cause | `result.json` | What you should do |
|---:|---|---|---|
| **0** | User clicked Submit | written | Read the file, apply the picks. See "Partial submit" below for `null` choices. |
| **1** | Spec failed validation at startup | not written | Fix the spec (the error message on stderr names the offending decision/option) and retry. |
| **124** | Heartbeat timeout — the browser stopped pinging for ~60s (tab closed, browser crashed, network died) | not written | Tell the user "I lost contact with the board, want to try again?" Don't invent picks. |
| **125** | User clicked Cancel or pressed ESC | not written | The user explicitly said no. Acknowledge it, ask what they want instead. Don't push back into the same board without their request. |
| **130** | Ctrl+C in the terminal | not written | Treat the same as 125 — an explicit abort. |

**`0` is the only outcome where `result.json` exists.** Don't read the file for any other exit code; it won't be there.

## Partial submit (exit 0 with `null` choices)

A `Submit` can include `null` entries — the user clicked Submit before deciding everything. Treat the result like this:

```json
{
  "decisions": {
    "1": { "choice": "a",    "comment": "" },
    "2": { "choice": "hold", "comment": "need legal review" },
    "3": { "choice": null,   "comment": "" }
  },
  "meta": { "counts": { "decided": 1, "hold": 1, "undecided": 1 } }
}
```

Recommended handling:

- **`choice` is an option key (`"a"`, `"b"`, …)** — the picked option. Proceed.
- **`choice` is `"hold"`** — the user explicitly wants to revisit. Track this as a follow-up, don't drop it. Apply nothing for this decision yet; ask the user how to circle back (file an issue, add to a TODO list, schedule a check-in).
- **`choice` is `null`** — the user did not pick. Do NOT silently treat this as "default to recommended". Surface the unresolved decisions to the user and ask:
  - "Do you want to leave these undecided?"
  - "Should I re-render the board with just these items?"
  - "Should I pick the recommended option for each?"

`meta.counts` gives you a quick summary without iterating — useful for "you have 3 undecided" messages.

## `hold` vs `null`

These look similar but mean different things:

- **`hold`** carries **intent** — the user pressed Hold-for-follow-up. There should be a future action.
- **`null`** carries **absence** — the user submitted before choosing. No intent recorded. The comment field may or may not have context.

Don't collapse them into one bucket. If a comment is present on a `null` entry, read it; the user may have explained why.

## When no `result.json` is written

For exit codes 124 / 125 / 130, the file does not exist. The agent must:

1. Not pretend the board returned picks.
2. Not silently re-launch the board (the user just cancelled it).
3. Briefly tell the user what happened (`"You cancelled"`, `"The board disconnected"`) and ask what they want to do next.

If the user wants to retry, you can re-launch — but always after they confirm.

## Concurrent boards

Each `serve.py` process owns one spec and one port. Don't try to:

- run two boards on the same port (the second will fail or fall back to a random port; the agent might not see which port took)
- share state between two boards via localStorage (different specs get different storage keys by design — see SKILL.md)

If the user needs two parallel decisions sessions, run two separate `serve.py` processes with different `--port` values and different `--output` paths, and parse each `RESULT_PATH` independently.

## Reading the result file robustly

```python
import json, subprocess, sys

proc = subprocess.run(["python3", "serve.py", spec_path, "--no-open"],
                      capture_output=True, text=True)

if proc.returncode != 0:
    # 124 / 125 / 130: the user did not submit. Surface to the user.
    return None

# Parse the first stdout line to find the result path.
first = proc.stdout.splitlines()[0]
assert first.startswith("RESULT_PATH=")
result_path = first.removeprefix("RESULT_PATH=")

with open(result_path) as f:
    result = json.load(f)

# result["decisions"] is a dict keyed by string id.
# result["meta"]["counts"] is a quick summary.
```

This pattern handles all five exit codes correctly — anything ≠ 0 short-circuits before touching the file.
