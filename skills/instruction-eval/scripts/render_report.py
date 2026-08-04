#!/usr/bin/env python3
"""Render A/B results into a single HTML report.

The report holds two kinds of content and separates them visually.

- Automatic: condition metadata, prompt text, answer text, metrics and deltas, run
  anomalies. All of it comes from runs/ and summary.json. Transcribing by hand only
  introduces errors.
- LLM: what changed, the claim, interpretation of answer differences, metric
  interpretation, conclusion. Injected via --insights JSON. Marked "not written"
  when absent.

Answers are long, so showing them all at once is unreadable. Pick one prompt and one
rep, and only that pair is shown in two columns.
"""

import argparse
import html
import json
from pathlib import Path


INSIGHT_FIELDS = {
    "title": "report title",
    "change": "what changed",
    "arms": "labels for the baseline/variant arms",
    "claim": "the claim about what changes",
    "conclusion": "conclusion",
}


LABELS = {"duration_ms": "duration", "num_turns": "turns", "output_tokens": "output tokens"}


def build_rows(results: dict) -> list[dict]:
    """One row per metric in the table. Delta direction is color only, no good/bad call.

    Sets overlap when the two arms' observed ranges intersect. Overlap means each arm
    falls inside the other's own spread, so the median delta can't be read as an effect.
    """
    rows = []
    for pid, arms in results.items():
        for key, label in LABELS.items():
            a, b = arms["baseline"][key], arms["variant"][key]
            fmt = (lambda v: f"{v / 1000:.1f}s") if key == "duration_ms" else (lambda v: f"{v:,.0f}")

            def span(s, fmt=fmt):
                return "-" if s["min"] is None else f"{fmt(s['min'])} ~ {fmt(s['max'])}"

            pct = None if not a["med"] or b["med"] is None else (b["med"] - a["med"]) / a["med"] * 100
            rows.append({
                "pid": pid,
                "label": label,
                "a": "-" if a["med"] is None else fmt(a["med"]),
                "b": "-" if b["med"] is None else fmt(b["med"]),
                "aSpan": span(a),
                "bSpan": span(b),
                "delta": "-" if pct is None else f"{pct:+.0f}%",
                "dir": "" if pct is None or abs(pct) < 1 else ("up" if pct > 0 else "down"),
                "overlap": bool(None not in (a["min"], b["min"]) and a["min"] <= b["max"] and b["min"] <= a["max"]),
            })
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description="Render A/B results into an HTML report")
    ap.add_argument("--work", required=True, help="directory run_ab.py wrote results to")
    ap.add_argument("--insights", default=None, help="LLM-written interpretation JSON")
    ap.add_argument("--out", default=None, help="output path (default: <work>/report.html)")
    args = ap.parse_args()

    work = Path(args.work).resolve()
    summary = json.loads((work / "summary.json").read_text())
    insights = json.loads(Path(args.insights).read_text()) if args.insights else {}

    runs: dict[str, dict[str, list]] = {}
    for f in sorted((work / "runs").glob("*.json")):
        r = json.loads(f.read_text())
        runs.setdefault(r["prompt_id"], {}).setdefault(r["arm"], []).append(r)
    for arms in runs.values():
        for reps in arms.values():
            reps.sort(key=lambda r: r["rep"])

    anomalies = [
        f"{pid} / {arm}: {s['errors']} errors, {s['denials']} permission denials"
        for pid, arms in summary["results"].items()
        for arm, s in arms.items()
        if s["errors"] or s["denials"]
    ]

    data = {
        "meta": summary["meta"],
        "prompts": summary["prompts"],
        "runs": runs,
        "rows": build_rows(summary["results"]),
        "anomalies": anomalies,
        "insights": insights,
    }
    # A </script> inside an answer cuts the inline script short and breaks the page.
    # Agent answers carrying HTML fragments isn't rare, so escape it.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    # Keeping the template in a separate file isn't taste, it's bug prevention. Inside
    # a Python string, Python eats one level of backslashes from the HTML/CSS/JS, so
    # regexes and newline escapes break silently. Python's syntax check won't catch it
    # and the page just comes out empty.
    scripts = Path(__file__).parent
    template = (scripts / "report_template.html").read_text()
    markdown_it = (scripts / "vendor" / "markdown-it.umd.min.js").read_text()
    if "</script" in markdown_it.lower():
        raise ValueError("vendored markdown-it bundle contains an unsafe </script sequence")

    out = Path(args.out) if args.out else work / "report.html"
    out.write_text(
        template.replace("__MARKDOWN_IT__", markdown_it)
        .replace("__DATA__", payload)
        .replace("__TITLE__", html.escape(insights.get("title") or "Condition A/B"))
    )

    missing = [name for key, name in INSIGHT_FIELDS.items() if not insights.get(key)]
    print(f"Report: {out}")
    if missing:
        print(f"Not written by LLM: {', '.join(missing)}. Fill in via --insights and re-render.")


if __name__ == "__main__":
    main()
