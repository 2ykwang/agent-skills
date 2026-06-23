---
name: create-qa-list
version: 0.0.1
category: productivity
description: Turn code, specs, a PR, or the current conversation into a QA test-case list a non-developer can read and run, exported as CSV, a shareable HTML report, or both. Trigger when the user wants QA test cases, a test plan, a QA checklist, or a test-case CSV/HTML (e.g. "write test cases for this", "make a QA list"). Output uses behavior-and-scenario language, never code symbols like function names or file paths. Not for writing or running automated test code (pytest/jest), code review, or test-strategy docs.
---

# create-qa-list

Build a QA test-case list a **non-developer QA tester** can read and run without opening the code — as CSV, HTML, or both.

## The two rules that govern everything

Every decision in this skill follows the two rules below. They pull in different directions (one is presentation, one is accuracy) and both must hold for every row.

**Rule 1 — The reader is a non-developer.** They run the product and watch what happens. They don't read code. So every case is written in behavior-and-scenario language — what the user does and what they see. Function names, file paths, table/column names, and code symbols never appear in the output. This rule drives the tone, the columns, and the verification steps.

**Rule 2 — Every case must match the code. Don't make things up.** A QA list that diverges from real behavior is worse than none: the tester tests behavior that doesn't exist, files bugs that aren't real, or marks a real bug as "pass". So every scenario and expected result must rest on something you actually verified (code, spec, this conversation). If you can't verify a behavior, do one of three things: read the code to confirm, ask the user, or drop the case. **Don't write a guessed expected result as if it were fact.** Flag any case resting on an unverified assumption as needs-confirmation instead of exporting it silently.

Together they are the skill's mission: *translate verified code behavior into language a non-developer can act on* — translate, but don't invent, and don't leak the code.

## Input can be anything

The user might give you: specs and planning docs, a URL, a PR/diff, pasted requirements, a one-line request, or just "make a QA list for what we built." **The current conversation is itself valid input** — if you've been building or discussing a feature, that context is the input.

The first job is to figure out *which feature/behavior* is the target. Infer from everything available first, then confirm — don't assume.

## Workflow — 4 steps, then Build

This is a **step-by-step** flow. Each step is a checkpoint: self-check that you have enough context, share what you have, and get the user's confirmation before spending effort on the next step. The point is to avoid building a 30-row deliverable on a wrong assumption. Don't skip steps, and don't dump every question at once.

Before each step, run the self-check questions in `references/context-checklist.md`. If you can't answer one, you're not ready to proceed — ask.

### Step 1 — Scope

Infer the target feature from code/spec/conversation. Then restate your understanding and confirm it. For decisions that narrow to a few answers (which feature, in/out areas, platform), present options and ask the user. Be specific — cite what you actually found. Example: "There are three payment methods (card, bank transfer, easy-pay) — should QA cover all three, or just the new easy-pay?"

At minimum, confirm: **what's in scope, what's explicitly out, and which platform/role** is the target.

### Step 2 — Categories & priority scheme

Before writing cases, agree on *how the list is grouped and graded*. That's what keeps 30 rows consistent. Propose:

- **The category set** — the feature areas cases group into (e.g. Input validation / Visibility conditions / Rewards / State transitions). Derive them from the scope; don't reach for a generic list.
- **Priority rules** — what counts as P1/P2/P3. Use the rubric in `references/consistency-guide.md`, but tune the examples to this feature and confirm. This matters — a list with loosely-assigned priorities won't be trusted.

Get agreement on both. This is the contract that keeps every later row consistent.

### Step 3 — Draft case list (titles only)

Now share a **lightweight outline**: per case, a TC_ID + Category + one-line scenario. No full columns yet. This is the cheapest moment to catch "you're missing case X" or "Y isn't worth testing." Group by category so gaps are visible. Ask for additions/removals/priority adjustments.

Iterate here until the outline is right. A missing case is far cheaper to fix as a title than as a full row.

### Step 4 — Export format

Ask the user: **CSV / HTML / both.** For when each fits, see `references/export-formats.md` (CSV = import into a test-management tool or sheet; HTML = a readable, shareable report with a built-in "Download CSV" button; both = hand-off + archive).

### Build

1. Expand the approved outline into full rows. First read `references/consistency-guide.md` and follow the column definitions and writing rules exactly. As you write each row, apply Rule 2: the expected result must reflect verified behavior, not a guess. Write the cases to `cases.json` in the working directory, and put the output under the working directory via `--out` (e.g. `qa_output/`) or a path the user specified (schema in `references/export-formats.md`).
2. Generate the deliverable with the bundled script — don't hand-write CSV or HTML:
   ```bash
   python3 scripts/build_export.py <cases.json> --format <csv|html|both> --out <dir>
   ```
   Run `--help` first if unsure. The script owns formatting (CSV escaping, HTML template), so the output stays consistent and you never re-derive it.
3. **Verify before declaring done** (this is a QA tool — hold your own output to a QA bar):
   - **Rule 2 check (accuracy):** Does every expected result match real code/spec behavior? Any row resting on a guess? Re-confirm from code or flag it to the user. This is the most important check — a wrong expected result sends QA chasing a non-bug.
   - **Rule 1 check (reader):** Open the output. Did any code symbol, function name, or file path leak into a cell? Rewrite that row in behavior language.
   - Are the columns identical across every row? Are priorities assigned per the agreed rubric?
   - Does every case have a concrete, observable expected result (not "works correctly")?
   - Cross-check against the Step 3 outline — are all approved cases present?
   Fix and re-run. Don't stop at the first generation.
4. **Tell the user how to open it.** Print the output path and an open command so they can view it immediately. Example: `open "<path>/<title>.html"`. If your environment can open it directly, do so.

## Reference files — read them when you reach the point

- `references/context-checklist.md` — self-check questions for each step. Read before Step 1.
- `references/consistency-guide.md` — column definitions, non-developer tone rules, category guidance, the priority rubric, good/bad row examples. Read before Build (skim the priority rubric before Step 2).
- `references/export-formats.md` — the cases JSON schema, the three export formats, and how to choose. Read at Step 4 / Build.

## Bundled resources

- `scripts/build_export.py` — renders the cases JSON to CSV and/or a styled HTML report. Standard library only.
- `assets/testcase_template.html` — the HTML report shell the script fills. Consistent, non-developer-friendly layout with a built-in "Download CSV" button.
- `assets/example_testcases.csv` — a writing example and format reference.
