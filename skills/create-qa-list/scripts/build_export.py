#!/usr/bin/env python3
"""Render a QA test-case list (cases JSON) to CSV and/or a self-contained HTML report.

Usage:
    python build_export.py cases.json --format both --out ./qa_output

The cases JSON schema is documented in references/export-formats.md. This script
owns all formatting so the deliverable stays consistent across runs; the caller
only authors the cases. Standard library only.
"""

import argparse
import csv
import html
import json
import re
import sys
from pathlib import Path


# HTML report depends on these by name: groups by Category, badges/sorts/counts Priority,
# labels rows by TC_ID. Missing any of them renders "undefined".
REQUIRED_COLUMNS = ("TC_ID", "Category", "Priority")
VALID_PRIORITIES = ("P1", "P2", "P3")
DEFAULT_TITLE = "QA Test Cases"


def load_cases(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "title" not in data or "cases" not in data:
        sys.exit("error: JSON must have 'title' and 'cases'")
    columns = data.get("columns")
    if not columns:
        sys.exit("error: JSON must list 'columns' (the column order)")

    missing_cols = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing_cols:
        sys.exit(f"error: columns must include {missing_cols} (the HTML report depends on them)")

    for i, row in enumerate(data["cases"]):
        _validate_row(i, row, columns)
    return data


def _validate_row(index: int, row: dict, columns: list[str]) -> None:
    """Reject a row that would make the CSV and HTML diverge or render broken."""
    case_id = row.get("TC_ID", "?")
    missing = [c for c in columns if c not in row]
    if missing:
        sys.exit(f"error: case #{index + 1} ({case_id}) missing columns: {missing}")
    # Cells must be scalar text; a list/dict/bool serializes differently in CSV vs HTML.
    # bool is a subclass of int, so reject it explicitly before the int/float allow.
    for c in columns:
        if isinstance(row[c], bool) or not isinstance(row[c], (str, int, float)):
            sys.exit(f"error: case #{index + 1} ({case_id}) column '{c}' must be text/number")
    # Off-list Priority (P0, urgent, ...) renders an unstyled badge and sorts to the front.
    if row["Priority"] not in VALID_PRIORITIES:
        sys.exit(f"error: case #{index + 1} ({case_id}) Priority must be {'/'.join(VALID_PRIORITIES)}")


def slugify(title: str) -> str:
    # \w already matches Unicode letters, so keep word chars and hyphen only.
    slug = re.sub(r"\s+", "_", title.strip())
    slug = re.sub(r"[^\w-]", "", slug)
    return slug or "qa_testcases"


def write_csv(data: dict, out_path: Path) -> None:
    columns = data["columns"]
    # utf-8-sig: Excel needs a BOM to detect UTF-8 (matters for non-ASCII cells).
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        for row in data["cases"]:
            writer.writerow([row[c] for c in columns])


def write_html(data: dict, template_path: Path, out_path: Path) -> None:
    template = template_path.read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False)
    # Encode <, >, & as \uXXXX so a cell value can't break out of the inline <script>
    # (e.g. a literal "</script>") or inject markup. Standard safe-embedding technique.
    payload = payload.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    # Escape the title — it lands in <title> as raw markup (h1/subtitle are set via JS textContent).
    html_out = template.replace("__TITLE__", html.escape(data.get("title", DEFAULT_TITLE))).replace(
        "__DATA_JSON__", payload
    )
    out_path.write_text(html_out, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render QA cases JSON to CSV and/or HTML.")
    parser.add_argument("cases_json", help="path to the cases JSON file")
    parser.add_argument("--format", choices=["csv", "html", "both"], default="both")
    parser.add_argument("--out", default=".", help="output directory (created if missing)")
    args = parser.parse_args()

    cases_path = Path(args.cases_json)
    if not cases_path.exists():
        sys.exit(f"error: {cases_path} not found")

    data = load_cases(cases_path)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = slugify(data["title"])

    written = []
    if args.format in ("csv", "both"):
        csv_path = out_dir / f"{slug}.csv"
        write_csv(data, csv_path)
        written.append(csv_path)
    if args.format in ("html", "both"):
        template_path = Path(__file__).resolve().parent.parent / "assets" / "testcase_template.html"
        if not template_path.exists():
            sys.exit(f"error: template not found at {template_path}")
        html_path = out_dir / f"{slug}.html"
        write_html(data, template_path, html_path)
        written.append(html_path)

    print(f"wrote {len(data['cases'])} cases:")
    for p in written:
        print(f"  {p}")


if __name__ == "__main__":
    main()
