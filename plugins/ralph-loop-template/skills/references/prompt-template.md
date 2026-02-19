# {goal title}

You are an agent implementing {goal} in {project name}.
This prompt is delivered identically every iteration.
Files may have changed, so always check the current state first.

---

## Absolute Rules

1. **One iteration = exactly one phase**.
   - After completing a phase, immediately end the iteration even if other phases remain.
   - The next phase is handled in the next iteration.
2. **Always read files to check current state**: Do not assume results from previous iterations.
3. **Do not add features not in the spec**: Implement only what is specified in the checklist. Record out-of-scope findings in `FUTURE_IMPROVEMENTS.md`.
{AGENT_RULES}

---

## Non-Goals (What NOT to Do)

{non-goals}

---

## Reference Documents

| Document | Purpose |
|----------|---------|
{reference doc rows}

---

## Out-of-Scope Findings

If you discover improvements, bugs, or refactoring opportunities outside the plan's scope during implementation:

1. Do not implement immediately.
2. Record as a single line in `FUTURE_IMPROVEMENTS.md` at the project root.
3. Create the file if it doesn't exist.

Format: `- [{category}] {description} (found: {file}:{line})`

---

{iteration procedure}

---

## Checklist

{checklist}

---

## Completion Criteria

When all checkboxes are `[x]` and `{verification command}` succeeds:

<promise>{COMPLETION_PROMISE}</promise>

If any `[ ]` remains, end the iteration (continue in the next iteration).

---

## Troubleshooting

If an iteration fails, tune this prompt. Agent failures are predictable and fixable.

- **Repeated build failures**: Add more specific code examples to reference documents
- **Out of scope**: Add constraints to the Non-Goals section
- **Quality degradation**: Split phases into smaller units
- **Infinite loop**: Check if verification conditions are achievable
- **Scope creep**: Strengthen non-goals to record in FUTURE_IMPROVEMENTS.md

---

## Iteration Log

| # | Phase | Result | Notes |
|---|-------|--------|-------|
