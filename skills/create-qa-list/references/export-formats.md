# Export formats

## Cases JSON (you author it, the script consumes it)

Write the approved cases to a single JSON file. The script reads it and renders CSV and/or HTML. Authoring JSON instead of writing CSV/HTML by hand takes formatting out of your hands so it stays consistent.

```json
{
  "title": "Coupon & Points QA",
  "subtitle": "VIP-only coupons / order points (optional)",
  "columns": ["TC_ID", "Category", "Scenario", "Preconditions", "Steps", "Expected Result", "Priority"],
  "cases": [
    {
      "TC_ID": "TC-001",
      "Category": "Visibility",
      "Scenario": "Only VIP-grade accounts see the exclusive coupon",
      "Preconditions": "VIP-grade account",
      "Steps": "1. Open the coupon box",
      "Expected Result": "The exclusive coupon appears in the list",
      "Priority": "P1"
    }
  ]
}
```

Rules:
- `columns` sets the column order. Every object in `cases` must have exactly those keys — if any row is missing a key the script errors out (a useful consistency check).
- Multi-step `Steps` / `Expected Result`: put `\n` between steps. CSV keeps it in one cell; HTML renders the line breaks.
- `title` is required, `subtitle` is optional.

## Choosing a format (ask in Step 4)

| Format | Fits when |
|--------|-----------|
| **CSV** | The QA team imports into a test-management tool, Google Sheets, or Excel. Simple, editable, diffable. |
| **HTML** | A readable, shareable report — grouped by category, color priority badges, a summary header, a filter box, and a **Download CSV button** that exports the same rows from inside the report. Good to hand straight to a tester or paste into a doc. |
| **Both** | HTML to read + CSV to import/track. A common default for real hand-off. Note: HTML alone can produce the CSV via its button, so "HTML only" is enough when you don't need a CSV file right now. |

## Running the script

```bash
python3 scripts/build_export.py cases.json --format both --out ./qa_output
```

- `--format` : `csv` | `html` | `both`
- `--out` : output directory (created if missing). The filename is the slugified title.
- If unsure, run `python3 scripts/build_export.py --help` first.

The HTML is a self-contained single file (inline CSS/JS, no network) built from `assets/testcase_template.html` — it opens anywhere and is safe to send as a mail attachment.

## After running — verify

Open the output and run the Build verification from SKILL.md. The script only guarantees *format* consistency; it can't judge which row leaked a code symbol or whether an expected result is observable. That judgment is yours.
