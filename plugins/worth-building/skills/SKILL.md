---
name: worth-building
version: 0.1.0
category: productivity
description: 'Decide how elaborate to build something (simple vs. robust) and return a concrete, PoC-shaped proposal at that level — not over- or under-engineered, but right-sized. Use whenever someone is building something and the investment level is unclear: "quick or proper?", "MVP vs. real product", "is this over-engineering?", "how should I approach X?", "quick script vs. robust system", "how much architecture?", "how much do I build here?". Fires even without "poc" or "right-size" — any time effort and complexity of what to build are being weighed.'
argument-hint: "<what you're building or the decision to size>"
---

# worth-building

Pick the right level of elaboration for what the user wants to build, then return a concrete proposal for how to solve it at that level. Use it for build decisions broadly — scripts, features, systems, docs, automation. Not limited to software.

The output is a **proposal, not a verdict.** "Level 2 of 3" is useless to anyone. What's useful: "build it in this shape, this was deliberately left out, raise it when you see this signal."

Input comes from `$ARGUMENTS` when invoked explicitly, or from the surrounding conversation.

## One principle

**Default to the lowest rung that holds. You don't prepare for complexity up front — you earn your way up to it.**

This is the default, not one option among many, because the cost is asymmetric. Going simple→robust later is cheap: you bolt it on. Going robust→simple is expensive: you rip it out, you don't get the time back (sunk cost), and you discover the code was overfit to requirements that never arrived. When in doubt, the lower rung is the cheaper mistake.

Complexity earns a rung up only two ways: **earned** (the simple version measurably falls short) or **forced** (a hard constraint makes low investment irresponsible). Forcing constraints are non-negotiable and never "right-sized" away: input validation at trust boundaries, error handling that prevents data loss, security, accessibility basics, and anything the user explicitly asked for.

## Steps

### 1. Understand the problem; ask to fill what's missing

Extract from the request and its context:
- **who** it's for, **what problem** it solves
- what "done / works" actually means here
- hard **constraints** (deadline, existing stack, security/data/compliance boundaries)
- how **reversible** this decision is, and how bad it is if wrong

**Find the design-splitting pivots first.** Name the 2-3 domain-specific facts where a different answer flips the whole technical direction (for payments: does the PSP support idempotency; for a calendar digest: shared calendar or personal aggregation). Generic axes (stakes, reversibility) only rank candidates — the pivots decide what the candidates even are. The skill can't list domain pivots for you. You find them with domain knowledge on every request.

If a pivot is empty and you can't fill it by inference, **ask. Only pivot-targeted questions, no generic details.** The number of questions scales with the pivots at stake, not a fixed cap (zero for trivial decisions, several for a big plan). Don't block — ask **alongside a tentative proposal with stated assumptions**, so the user answers or corrects. People respond more precisely to a concrete tentative than an abstract question. If nothing decision-critical is missing, skip the questions. For format and question classes see `references/questionnaire.md`.

**Doubt the premise first.** Sometimes the right-sized answer is "don't build it, the real problem is X." If the request solves the wrong problem, or the source/data isn't trustworthy (e.g. an elaborate bot on stale docs just launders old info as confident output), name that before sizing the build. No level of effort is the answer on a bad premise. Realize this premise-doubt through **evidence-of-need** questions (frequency, pain cost, blast radius, whether existing tools were tried), so "don't build it" is answered by measurement, not vibe. Design pivots (what to build) and evidence of need (whether it's worth building at all) are different classes. Both in `references/questionnaire.md`.

### 2. Stakes gate — this sizes the effort

This skill's failure mode is bolting five paragraphs and a trade-off table onto a decision that ends in one line. **Scale effort to stakes (risk and cost-of-reversal).** This gate sets that size and stops over-analysis.

Reversible and cheap to change later? → go **short proposal**: one-line recommendation + a few how-to lines + one or two lines of what's-cut/triggers. Skip candidate generation (4) and the trade-off table (5). If it's genuinely trivial and one line does it, one line.

Expensive or hard to reverse (data migration, public API shape, a dependency you'll carry for years, customer-facing)? → run the full path below (candidates + axes).

The point: the gate decides **which machine to run**, not "how long the output is." A low-stakes build question still needs a how-to. Laying out a 3-candidate table for it is the overkill.

### 3. Anchor on the minimum validating form

Nail down the **smallest thing** that actually validates the idea or solves the immediate problem. That's the anchor. Every candidate is measured by "does it reach there, and how far past it does it go."

### 4. Generate 2-3 candidate shapes

**Candidates follow the dominant pivot from step 1.** The generic "throwaway/minimal/robust" ladder is only a fallback when the domain won't resolve. If the pivot is "does the PSP support idempotency," candidates split on that axis (idempotent→DB retry / not→add a reconciliation check / high throughput→queue). Stop at three. Generating more candidates is itself over-analysis.

### 5. Weigh on fixed axes

Score each candidate on these axes. The axes themselves are the point, not a number:

| Axis | Why it's decisive |
|------|----------------|
| Build cost | what you pay now |
| **Cost to reverse** | the asymmetry from 'one principle'. Usually the decisive axis |
| Requirement certainty | validated need → can go up. Speculative → stay low |
| Blast radius if wrong | data loss / security / trust boundary → covers all the above and **forces a higher rung** |
| Maintenance drag | the tax complexity keeps charging after it's built |

### 6. Pick the lowest rung that holds

Apply the principle. Among the candidates that clear the anchor and satisfy the forcing constraints, pick the least elaborate. If you go above the floor, name the specific evidence or constraint that earned it — not a vibe.

## Output format

Keep it tight. Low-stakes (step 2) → **short proposal** only: one-line recommendation + a few how-to lines + one or two lines of cut/triggers. Drop the candidate table. High-stakes full path → use the whole shape below:

```
## Candidate comparison (high-stakes full path only; drop the table for low-stakes)
| Candidate | Build cost | Cost to reverse | Req. certainty | Blast radius | Maintenance |
(Score 2-3 candidates on the step-5 axes. This table is the basis for step 6's "lowest rung" pick.)

## Recommendation
- **Right-sized shape:** <approach, one line>
- **Why this level:** <which rung, what holds it there, evidence or constraint>

## How to build it (PoC)
<Just enough to orient. No implementation detail (tool names, commands, code, step-by-step) — see below.>

## Deliberately cut
- <item>: add when <trigger> arrives

## Upgrade triggers
- <observable signal> → raise to <next shape>
```

The "how to build it" section is what the user actually wanted — a proposal that gives a starting direction, not an abstract grade. But **stop there: approach and non-negotiable constraints only.** Detailed implementation (specific tool names, commands, code, step-by-step build procedure) is outside this skill. Right-sizing is a judgment, not a design; ballooning into full design conflicts with this skill's own anti-over-analysis principle. Ask yourself: does the PoC name a specific tool or a sequential build step? → it leaked into design, keep only the shape.

The "deliberately cut" and "upgrade triggers" sections make right-sizing safe: they turn "didn't build X" from a hidden gap into an intended decision with a trigger attached.

## Example

One low-stakes example here. The other two worked examples — high-stakes data (full path), and non-software doc/process — are in `references/examples.md`. All three show how the same shape (a startable plan + a triggered skip + one forcing constraint) comes out across different domains.

**Request:** "I manage 3 env vars — should I build a config management system?"

> **Right-sized shape:** Don't. One small config module that reads the 3 env vars at startup is enough.
> **Why:** Three values have no complexity for a system to earn. Layered overrides and hot-reload are speculative.
> **Non-negotiable constraint:** the API key fails fast at startup if missing (trust-boundary input).
> **Cut:** schema-validation library — add if entries pass ~10 or validation repeats.

Reversible decision, so the gate ended it as a short proposal. Note it **says only the shape — "one config module" — and stops.** The moment specific functions/libraries/line-level code appear (subclass `pydantic.BaseSettings`, parse with `int(os.getenv(...))`), that's design, not shape. The build is the next step.

## Notes

- Answer in the user's language. Match the proposal to how the user talks.
- If the user pushes back and wants the fuller version, build it. Don't re-argue the principle. The default is a default, not a rule.
