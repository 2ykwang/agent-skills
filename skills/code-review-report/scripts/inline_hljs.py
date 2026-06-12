#!/usr/bin/env python3
"""Inline the vendored highlight.js into a generated report.

Replaces the template's INLINE_HLJS placeholder with the full library so the
report stays a single self-contained file (no CDN, works offline).

Usage: python3 inline_hljs.py <report.html>
"""
import sys
from pathlib import Path

PLACEHOLDER = "<script>/* INLINE_HLJS */</script>"


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: inline_hljs.py <report.html>")
    report = Path(sys.argv[1])
    html = report.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        sys.exit(f"placeholder not found in {report}: {PLACEHOLDER}")
    js = (Path(__file__).resolve().parent.parent / "assets" / "highlight.min.js").read_text(encoding="utf-8")
    report.write_text(html.replace(PLACEHOLDER, f"<script>{js}</script>", 1), encoding="utf-8")
    print(f"inlined highlight.js into {report}")


main()
