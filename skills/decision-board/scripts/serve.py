#!/usr/bin/env python3
"""
Render and serve a decision-board wizard from a JSON spec.

Default mode is a tiny HTTP server with a Submit endpoint — the user makes
their picks in the browser, clicks Submit, and the JSON result is written
to disk. With ``--static`` the same renderer just writes a self-contained
HTML file (no server, no Submit, user copies the result back manually).

Usage:
    serve.py <spec.json>                            # serve at http://localhost:7117
    serve.py <spec.json> --port 8080                # different port
    serve.py <spec.json> --output result.json       # explicit result location
    serve.py <spec.json> --static board.html        # write a single HTML file and exit

Endpoints (server mode):
    GET  /                 → wizard HTML (re-rendered on each request)
    POST /api/submit       → save the JSON result
    POST /api/draft        → save in-progress draft
    GET  /api/result       → return last saved result, if any

Stop the server with Ctrl+C. Stdlib only, no third-party dependencies.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import signal
import subprocess
import sys
import time
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = SKILL_DIR / "assets" / "wizard_template.html"
SPEC_PLACEHOLDER = "/* SPEC_PLACEHOLDER */"
PREVIEW_FILE_PATTERN = re.compile(r"<<<file:([^>]+)>>>")
DEFAULT_PORT = 7117


# ---------------------------------------------------------------------------
# Spec load / validate / render (formerly build.py)
# ---------------------------------------------------------------------------

class SpecError(ValueError):
    """Raised when the spec fails validation."""


def load_spec(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SpecError(f"cannot read spec: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise SpecError(
            f"spec is not valid JSON ({exc.lineno}:{exc.colno}): {exc.msg}"
        ) from exc


def validate_spec(spec: dict[str, Any]) -> None:
    if not isinstance(spec, dict):
        raise SpecError("spec must be a JSON object")
    if not spec.get("title"):
        raise SpecError("spec.title is required")
    decisions = spec.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise SpecError("spec.decisions must be a non-empty array")

    seen_ids: set[Any] = set()
    declared_categories = spec.get("categories")
    used_categories: set[str] = set()

    for index, decision in enumerate(decisions):
        loc = f"decisions[{index}]"
        if not isinstance(decision, dict):
            raise SpecError(f"{loc} must be an object")
        if "id" not in decision:
            raise SpecError(f"{loc}.id is required")
        if decision["id"] in seen_ids:
            raise SpecError(f"{loc}.id={decision['id']!r} is not unique")
        seen_ids.add(decision["id"])
        if not decision.get("title"):
            raise SpecError(f"{loc}.title is required")
        options = decision.get("options")
        if not isinstance(options, list) or not options:
            raise SpecError(f"{loc}.options must be a non-empty array")
        seen_keys: set[str] = set()
        for opt_index, option in enumerate(options):
            opt_loc = f"{loc}.options[{opt_index}]"
            if not isinstance(option, dict):
                raise SpecError(f"{opt_loc} must be an object")
            key = option.get("key")
            if not key or not isinstance(key, str):
                raise SpecError(f"{opt_loc}.key is required (non-empty string)")
            if key in seen_keys:
                raise SpecError(
                    f"{opt_loc}.key={key!r} is not unique within this decision"
                )
            seen_keys.add(key)
            if not option.get("label"):
                raise SpecError(f"{opt_loc}.label is required")
        category = decision.get("category")
        if category:
            used_categories.add(category)

    if declared_categories is not None:
        if not isinstance(declared_categories, list):
            raise SpecError("spec.categories must be an array of strings")
        unused = used_categories - set(declared_categories)
        if unused:
            raise SpecError(
                "decisions reference categories not in spec.categories: "
                + ", ".join(sorted(unused))
            )


def inline_preview_files(spec: dict[str, Any], preview_dir: Path | None) -> None:
    if preview_dir is None:
        return

    def resolve(token_match: re.Match[str]) -> str:
        rel = token_match.group(1).strip()
        path = (preview_dir / rel).resolve()
        try:
            path.relative_to(preview_dir.resolve())
        except ValueError as exc:
            raise SpecError(f"preview file escapes preview-dir: {rel}") from exc
        if not path.is_file():
            raise SpecError(
                f"preview file not found: {rel} (looked under {preview_dir})"
            )
        return path.read_text(encoding="utf-8")

    def expand(value: Any) -> Any:
        if isinstance(value, str):
            return PREVIEW_FILE_PATTERN.sub(resolve, value)
        if isinstance(value, list):
            return [expand(item) for item in value]
        if isinstance(value, dict):
            return {k: expand(v) for k, v in value.items()}
        return value

    for decision in spec["decisions"]:
        for field in ("current_example", "rationale"):
            if field in decision:
                decision[field] = expand(decision[field])
        for option in decision["options"]:
            if "preview" in option:
                option["preview"] = expand(option["preview"])


def render_html_from_spec(spec_path: Path, preview_dir: Path | None) -> str:
    spec = load_spec(spec_path)
    validate_spec(spec)

    if "<<<file:" in spec_path.read_text(encoding="utf-8"):
        chosen = preview_dir or spec_path.parent
        inline_preview_files(spec, chosen)

    if not TEMPLATE_PATH.is_file():
        raise SpecError(f"template not found: {TEMPLATE_PATH}")

    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if SPEC_PLACEHOLDER not in template:
        raise SpecError(
            f"template missing the {SPEC_PLACEHOLDER!r} marker — was it edited?"
        )
    payload = json.dumps(spec, ensure_ascii=False, indent=2)
    return template.replace(SPEC_PLACEHOLDER, f"const SPEC = {payload};")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

def kill_port(port: int) -> None:
    """Best-effort: free a port held by a previous run."""
    try:
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True, text=True, timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return
    for pid_str in result.stdout.strip().splitlines():
        pid_str = pid_str.strip()
        if not pid_str:
            continue
        try:
            os.kill(int(pid_str), signal.SIGTERM)
        except (ProcessLookupError, ValueError):
            continue
    if result.stdout.strip():
        time.sleep(0.4)


class BoardHandler(BaseHTTPRequestHandler):
    """Serves the wizard and accepts submit POSTs."""

    def __init__(
        self,
        spec_path: Path,
        preview_dir: Path | None,
        result_path: Path,
        draft_path: Path,
        *args,
        **kwargs,
    ):
        self.spec_path = spec_path
        self.preview_dir = preview_dir
        self.result_path = result_path
        self.draft_path = draft_path
        super().__init__(*args, **kwargs)

    def _send_json(self, status: int, payload: dict | bytes) -> None:
        body = (
            payload
            if isinstance(payload, bytes)
            else json.dumps(payload, ensure_ascii=False).encode("utf-8")
        )
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length))

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            try:
                html = render_html_from_spec(self.spec_path, self.preview_dir)
            except (SpecError, OSError) as exc:
                self.send_error(500, f"Spec error: {exc}")
                return
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == "/api/result":
            if self.result_path.exists():
                self._send_json(200, self.result_path.read_bytes())
            else:
                self._send_json(404, {"error": "no result saved yet"})
            return

        if self.path == "/api/draft":
            if self.draft_path.exists():
                self._send_json(200, self.draft_path.read_bytes())
            else:
                self._send_json(404, {"error": "no draft saved yet"})
            return

        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path not in ("/api/submit", "/api/draft"):
            self.send_error(404)
            return

        try:
            data = self._read_json_body()
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": f"invalid JSON: {exc}"})
            return

        if not isinstance(data, dict):
            self._send_json(400, {"error": "expected a JSON object"})
            return

        target = self.result_path if self.path == "/api/submit" else self.draft_path
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            self._send_json(500, {"error": f"write failed: {exc}"})
            return

        self._send_json(200, {"ok": True, "saved_to": str(target)})

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _timestamped_default(spec_path: Path, suffix: str) -> Path:
    """Build a default result/draft path that won't collide across runs."""
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = spec_path.stem
    return spec_path.with_name(f"{stem}.{stamp}.{suffix}.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render and serve a decision-board wizard from a JSON spec.",
    )
    parser.add_argument("spec", type=Path, help="Path to the JSON spec")
    parser.add_argument(
        "--port", "-p", type=int, default=DEFAULT_PORT,
        help=f"Server port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Where to save the submitted result. "
        "Default: <spec-stem>.<timestamp>.result.json next to the spec.",
    )
    parser.add_argument(
        "--draft", type=Path, default=None,
        help="Where to auto-save in-progress drafts. "
        "Default: <spec-stem>.<timestamp>.draft.json next to the spec.",
    )
    parser.add_argument(
        "--preview-dir", type=Path, default=None,
        help="Directory for <<<file:...>>> preview tokens (default: spec's directory).",
    )
    parser.add_argument(
        "--no-open", action="store_true",
        help="Do not open the browser automatically.",
    )
    parser.add_argument(
        "--static", "-s", type=Path, default=None,
        help="Skip the server. Render the wizard to this HTML path and exit. "
        "Useful when the page needs to be shared, archived, or opened offline.",
    )
    args = parser.parse_args(argv)

    if not args.spec.is_file():
        print(f"error: spec not found: {args.spec}", file=sys.stderr)
        return 2

    # Validate the spec up front so we fail before opening a port or writing a file
    try:
        spec = load_spec(args.spec)
        validate_spec(spec)
    except SpecError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # ---- static mode ------------------------------------------------------
    if args.static is not None:
        try:
            html = render_html_from_spec(args.spec, args.preview_dir)
        except SpecError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        args.static.parent.mkdir(parents=True, exist_ok=True)
        args.static.write_text(html, encoding="utf-8")
        print(f"wrote {args.static}")
        return 0

    # ---- server mode ------------------------------------------------------
    result_path = args.output or _timestamped_default(args.spec, "result")
    draft_path = args.draft or _timestamped_default(args.spec, "draft")

    kill_port(args.port)
    handler = partial(BoardHandler, args.spec, args.preview_dir, result_path, draft_path)
    try:
        server = HTTPServer(("127.0.0.1", args.port), handler)
        port = args.port
    except OSError:
        server = HTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]

    url = f"http://localhost:{port}"
    print()
    print("  Decision Board")
    print("  ─────────────────────────────────")
    print(f"  URL:    {url}")
    print(f"  Spec:   {args.spec}")
    print(f"  Result: {result_path}")
    print(f"  Draft:  {draft_path}")
    print()
    print("  Decide in the browser, click Submit, then Ctrl+C here.")
    print()

    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("  Stopped.")
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
