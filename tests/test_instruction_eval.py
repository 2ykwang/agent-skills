"""Regression tests for instruction-eval's self-contained HTML report."""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "instruction-eval"
RENDERER = SKILL / "scripts" / "render_report.py"
MARKDOWN_IT = SKILL / "scripts" / "vendor" / "markdown-it.umd.min.js"


def render_markdown(source: str) -> str:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node is required to test the vendored browser bundle")
    script = (
        "const markdownit = require(process.argv[1]);"
        "const md = markdownit({html:false,linkify:false,typographer:false});"
        "process.stdout.write(md.render(process.argv[2]));"
    )
    return subprocess.run(
        [node, "-e", script, str(MARKDOWN_IT), source],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


class TestVendoredMarkdownIt(unittest.TestCase):
    def test_variable_fences_and_language_names(self):
        source = """````markdown
```python
print('한글')
```
````

```objective-c
// 한글
```

```c++
// 한글
```
"""
        rendered = render_markdown(source)

        self.assertIn('<code class="language-markdown">```python', rendered)
        self.assertIn("print('한글')", rendered)
        self.assertIn('<code class="language-objective-c">// 한글', rendered)
        self.assertIn('<code class="language-c++">// 한글', rendered)

    def test_raw_html_and_unsafe_links_stay_inert(self):
        rendered = render_markdown(
            '<img src=x onerror="alert(1)">\n\n[bad](javascript:alert(1))'
        )

        self.assertIn("&lt;img", rendered)
        self.assertNotIn("<img", rendered)
        self.assertNotIn('href="javascript:', rendered)


class TestReportRenderer(unittest.TestCase):
    def test_report_embeds_markdown_it_without_control_characters(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            (work / "runs").mkdir()
            result = {
                "arm": "baseline",
                "prompt_id": "code",
                "rep": 0,
                "duration_ms": 1000,
                "num_turns": 1,
                "output_tokens": 10,
                "denials": 0,
                "is_error": False,
                "result": "```python\nprint('한글')\n```",
            }
            for arm in ("baseline", "variant"):
                record = {**result, "arm": arm}
                (work / "runs" / f"code__{arm}__0.json").write_text(
                    json.dumps(record, ensure_ascii=False)
                )

            metric = {"med": 1, "min": 1, "max": 1}
            arm_results = {
                "duration_ms": metric,
                "num_turns": metric,
                "output_tokens": metric,
                "n": 1,
                "errors": 0,
                "denials": 0,
            }
            summary = {
                "meta": {
                    "n": 1,
                    "runs": 2,
                    "model": "test",
                    "baseline_dir": "/baseline",
                    "variant_dir": "/variant",
                },
                "prompts": [
                    {"id": "code", "kind": "on-target", "prompt": "한글 확인"}
                ],
                "results": {
                    "code": {
                        "baseline": arm_results,
                        "variant": arm_results,
                    }
                },
            }
            (work / "summary.json").write_text(
                json.dumps(summary, ensure_ascii=False)
            )

            subprocess.run(
                [sys.executable, str(RENDERER), "--work", str(work)],
                check=True,
                capture_output=True,
                text=True,
            )
            report = (work / "report.html").read_bytes()

        self.assertNotIn(b"\x00", report)
        self.assertNotIn(b"__MARKDOWN_IT__", report)
        self.assertNotIn(b"<script src=", report)
        self.assertIn(b"globalThis.markdownit", report)
        self.assertIn("한글 확인".encode(), report)


if __name__ == "__main__":
    unittest.main()
