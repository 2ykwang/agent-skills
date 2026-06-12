# Review perspectives and the subagent prompt

## Picking perspectives

Pick the perspectives that match the nature of the change — not all of them. First cover the mandatory ones from the mapping below, then add others based on what the change actually touches.

**Mandatory perspectives by change type** (don't skip these; the rest are optional):

| If the change touches | Always include |
|-----------------------|----------------|
| DB schema, migrations | migration/compat, correctness |
| auth, permissions, access to others' resources | security/authz |
| transactions, concurrent writes, locks | concurrency |
| external API request/response contracts | migration/compat |
| new business logic | correctness, tests, spec fit |
| pure refactor (no behavior change) | naming/readability, tests (behavior preserved) |

**What each perspective looks for:**

| Perspective | What to look for |
|-------------|------------------|
| Correctness | missing conditions and branches, off-by-one, wrong assumptions, contradictory state |
| Concurrency / transactions | race conditions, transaction boundaries, row locking (e.g., `SELECT … FOR UPDATE`), idempotency |
| Security / authz | missing auth checks, IDOR (accessing others' resources), input validation, internals leaking through error messages |
| Spec fit | does the code match the spec and requirements, missed requirements, misreadings |
| Naming / readability | names match the domain, separation of concerns, dead code, duplication |
| Tests | regression coverage, edge and negative cases, assertions that actually assert |
| Performance | N+1 queries, needless iteration, large-data handling |
| Migration / compat | applying to an empty DB, backward compatibility, external API contract changes |
| Error handling / edges | null and empty data, boundary values, behavior on failure |

## Subagent prompt skeleton

Give each subagent a prompt shaped like this. **Context injection is the point** — without it you only get surface-level remarks.

```
[project / working directory]

## Working context (collected from the conversation — complete, nothing omitted)
- What was done and why: ...
- Key design decisions and reasons, rejected alternatives, tradeoffs: ...
- Unfinished work / next steps: ...
- Concerns the user raised: ...

## How to inspect the change
- git -C <dir> diff <base>...HEAD   (committed)
- git -C <dir> diff HEAD            (uncommitted)
- New files — read directly: <list>

## Perspectives to review (only the applicable ones)
<perspectives picked from the tables above + concrete questions per perspective>

## Output
Each finding gets a P1–P3 priority. Per finding:
- What's wrong or suspicious (concrete scenario)
- Code evidence (file:line)
- One of: "problem" / "no problem (reason)" / "needs checking"
Mark speculation as speculation. Pay special attention to places where the
working context and the code disagree.
```

## Merging results

For large changes, run one subagent per perspective in parallel. Collect the results, dedupe, sort by priority, and load them into the report's review checklist.
