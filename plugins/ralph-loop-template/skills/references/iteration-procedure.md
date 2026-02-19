## Iteration Procedure

> One iteration must process exactly one phase.
> Even if multiple phases remain, complete only one and terminate.

### STEP 1: Assess State

1. Read this prompt file to check the current state of the checklist.
2. Find the first phase with incomplete items (`[ ]`).
3. Process **only this phase** in the current iteration.

### STEP 2: Gather Context

1. Read detailed content for the phase from reference documents.
2. Read the current state of files the phase will modify.
3. Identify patterns in relevant existing code.

### STEP 3: Implement

1. Implement the phase's sub-items in order.
2. Immediately check off completed sub-items as `[x]` in this file.
3. **Do not touch items in other phases.**
4. Record out-of-scope findings in `FUTURE_IMPROVEMENTS.md`.

### STEP 4: Verify

1. Run `{verification command}`.
2. If successful, proceed to STEP 5.
3. If failed, read the error message and fix.
4. **If the same error fails 2 consecutive times**: Stop fixing, record the failure in the iteration log, and end the iteration. Retry with fresh context in the next iteration.

### STEP 5: End Iteration

1. Record the result in the iteration log table.
2. Check if all phase checkboxes are `[x]`.

**Path A — Incomplete phases remain:**
Terminate silently with no output. The loop will automatically start the next iteration.

**Path B — All phases completed:**
If verification passed in STEP 4, output the following promise:

<promise>{COMPLETION_PROMISE}</promise>

If arrived here after failure in STEP 4 (stopped due to 2 consecutive failures), terminate without the promise.
