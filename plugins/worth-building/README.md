# worth-building

Decide how elaborate to build something — simple vs. robust — and get back a concrete, PoC-shaped proposal at that level. Not over-engineered, not under-built: right-sized. The output is a proposal you can start from ("build it in this shape, this was left out, raise it when you see this signal"), not a grade.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install worth-building@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill worth-building
```

## When to use

- Weighing effort on something you're about to build — script, feature, system, doc, automation
- "Quick or proper?", "MVP vs. real product", "is this over-engineering?", "how much architecture here?"
- You suspect the request might not be worth building at all, and want that answered by evidence, not vibe

Not limited to software. If you already know the exact shape and just need it built, skip this — it's for the sizing decision, not the implementation.

## Usage

```
# Explicit — pass what you're deciding about
/worth-building should I build a config system for 3 env vars?

# Or it fires from context when you're weighing effort, no invocation needed
```

## How it works

1. **One principle:** default to the lowest rung that holds. Cost is asymmetric — simple→robust is cheap to bolt on later, robust→simple is expensive to rip out.
2. **Stakes gate** sizes the response: reversible → short proposal; expensive/irreversible → full candidate analysis.
3. **Forcing constraints** (input validation, data-loss handling, security, accessibility, explicit asks) are never right-sized away.
4. Output stops at **shape**, not design — no specific tool names, commands, or step-by-step build procedure. That's the next step.

## Output

Low-stakes → a short proposal (no table):

> **Right-sized shape:** Don't. One config module that reads the 3 env vars at startup.
> **Why:** Three values have no complexity for a system to earn. Layered overrides and hot-reload are speculative.
> **Non-negotiable constraint:** the API key fails fast at startup if missing (trust-boundary input).
> **Cut:** schema-validation library — add if entries pass ~10 or validation repeats.

High-stakes (data migration, public API, customer-facing) → the full path: a candidate comparison table, recommendation, PoC direction, a deliberately-cut list, and upgrade triggers.

## Notes

- Answers in your language; matches the proposal to how you talk.
- Push back for the fuller version and it builds that — the default is a default, not a rule.
