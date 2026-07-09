# Questionnaire format

Throw pivot-targeted questions as a text questionnaire. Don't use a tool like AskUserQuestion — for portability. Outside Claude Code (other agents, plain chat) those tools aren't available. A text questionnaire works everywhere, and fixing the format keeps it readable and consistent.

## Two question classes — don't mix them, check both

This skill judges "worth building, and how much." That needs two kinds of questions.

### A. Design pivots — decide "what to build"

Facts where a different answer flips the whole technical direction. This axis decides what the candidates are. Domain-specific, so find them per request.

### B. Evidence of need — decides "whether it's worth building at all"

Facts that answer "don't build it" by measurement, not vibe. Design pivots alone won't surface these. SKILL.md's "doubt the premise first" is realized through this class. The four axes below reuse across domains:

1. Frequency: how often does this problem occur (cadence).
2. Pain cost: the time, mistakes, and cost the current workaround actually charges.
3. Blast radius: how many are blocked, who's customer-facing.
4. Prior attempts: was it tried with existing tools, and why did that fail?

Skipping B leaves the "don't build it" call weak and unsupported. For a big plan, throw a few A and a few B together.

## Text questionnaire format

Write each question as a number, a one-line question, and options a/b/c below it. Rules:

1. Tag each question `[A design pivot]` or `[B evidence of need]` so it's clear what it measures.
2. Attach a one-line implication to each option (where the design goes). Label-only options can't be chosen.
3. For questions where several may apply, say "select all that apply."
4. **End every questionnaire noting the user can answer freely if no option fits.** Options are a starting point, not a fence.

Below is a domain-agnostic skeleton. Fill the angle brackets with the request's domain:

```
[A design pivot]
1. <question that splits the whole design>?
   a. <option> (<where this sends the design>)
   b. <option> (<implication>)
   c. <option> (<implication>)

[B evidence of need] select all that apply
2. <question measuring the limit/pain of the current way>?
   a. <limit candidate>
   b. <limit candidate>
   c. <limit candidate>

* If none fit, write your own.
```

## Always with a tentative

Don't block — ask with a tentative recommendation that states its assumptions. People respond more precisely to a concrete tentative than an abstract question. Let them answer or correct. The number of questions scales with the pivots at stake. Zero if trivial.
