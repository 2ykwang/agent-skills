#!/usr/bin/env python3
"""
Render and serve a decision-board board from a JSON spec.

Default mode opens a tiny HTTP server. The user picks options in the browser,
clicks Submit, and the server writes the result to disk and shuts itself down.
With ``--static`` the renderer just writes a self-contained HTML file (no server,
no Submit, user copies the result back manually — for sharing/archiving).

Usage:
    serve.py <spec.json>                            # serve at http://localhost:7117
    serve.py <spec.json> --port 8080                # different port
    serve.py <spec.json> --output result.json       # explicit result location
    serve.py <spec.json> --static board.html        # write a single HTML file and exit

Endpoints (server mode):
    GET  /                 → board HTML (re-rendered on each request)
    POST /api/submit       → save the JSON result, then shut down (exit 0)
    POST /api/cancel       → user-initiated abort, then shut down (exit 125)
    POST /api/heartbeat    → liveness ping; if missing for ~60s the server
                             shuts down on its own (exit 124)

Agent contract:
    On startup the first stdout line is ``RESULT_PATH=<absolute path>``. The
    server exits with one of: 0 (Submit), 1 (spec invalid), 124 (heartbeat
    timeout — browser gone), 125 (user Cancel), 130 (Ctrl+C). Only exit 0
    writes the result file. See references/result-handling.md for the full
    agent-side handling guide.

Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATE_PATH = SKILL_DIR / "assets" / "board_template.html"
SPEC_PLACEHOLDER = "/* SPEC_PLACEHOLDER */"
DEFAULT_PORT = 7117


# ---------------------------------------------------------------------------
# Spec load / validate / render
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


REVERSIBILITY_VALUES = {"easy", "hard"}


def validate_spec(spec: dict[str, Any]) -> None:
    """Validate the spec in place, coercing decision ids to strings."""
    if not isinstance(spec, dict):
        raise SpecError("spec must be a JSON object")
    if not spec.get("title"):
        raise SpecError("spec.title is required")
    decisions = spec.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        raise SpecError("spec.decisions must be a non-empty array")

    seen_ids: set[str] = set()
    declared_categories = spec.get("categories")
    used_categories: set[str] = set()

    for index, decision in enumerate(decisions):
        loc = f"decisions[{index}]"
        if not isinstance(decision, dict):
            raise SpecError(f"{loc} must be an object")
        title = decision.get("title")
        # locator used in error messages downstream — prefer human-readable title
        where = f"decision {title!r}" if title else f"{loc}"
        if "id" not in decision:
            raise SpecError(f"{where} is missing 'id'")
        # accept int or string id; coerce to string for result map alignment
        raw_id = decision["id"]
        if not isinstance(raw_id, (str, int)) or isinstance(raw_id, bool):
            raise SpecError(
                f"{where} has invalid id {raw_id!r}: must be a string or integer"
            )
        sid = str(raw_id)
        if not sid:
            raise SpecError(f"{where} has empty id")
        if sid in seen_ids:
            raise SpecError(f"{where} has duplicate id={sid!r}")
        seen_ids.add(sid)
        decision["id"] = sid  # coerce in place so downstream uses string consistently
        if not title:
            raise SpecError(f"{where} is missing 'title'")
        options = decision.get("options")
        if not isinstance(options, list) or not options:
            raise SpecError(f"{where} has no options")
        seen_keys: set[str] = set()
        for opt_index, option in enumerate(options):
            if not isinstance(option, dict):
                raise SpecError(
                    f"{where} option #{opt_index} must be an object"
                )
            key = option.get("key")
            if not key or not isinstance(key, str):
                raise SpecError(
                    f"{where} option #{opt_index} is missing a 'key' (non-empty string)"
                )
            opt_where = f"{where} option {key!r}"
            if key in seen_keys:
                raise SpecError(f"{opt_where} has duplicate key within this decision")
            seen_keys.add(key)
            if not option.get("label"):
                raise SpecError(f"{opt_where} is missing 'label'")
            reversibility = option.get("reversibility")
            if reversibility is not None and reversibility not in REVERSIBILITY_VALUES:
                raise SpecError(
                    f"{opt_where} has invalid reversibility {reversibility!r}: "
                    f"must be one of {sorted(REVERSIBILITY_VALUES)}"
                )
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


def render_html_from_spec(spec_path: Path) -> str:
    spec = load_spec(spec_path)
    validate_spec(spec)

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


class BoardHandler(BaseHTTPRequestHandler):
    """Serves the board and accepts the Submit POST."""

    # Exit codes used to communicate termination cause back to the agent.
    # See SKILL.md "Result schema" — these are part of the agent contract.
    EXIT_SUBMITTED = 0
    EXIT_HEARTBEAT_TIMEOUT = 124
    EXIT_USER_CANCELLED = 125

    def __init__(
        self,
        spec_path: Path,
        result_path: Path,
        state: dict,
        *args,
        **kwargs,
    ):
        self.spec_path = spec_path
        self.result_path = result_path
        # Shared state across handler instances: last heartbeat time + exit code.
        self._state = state
        super().__init__(*args, **kwargs)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
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
                html = render_html_from_spec(self.spec_path)
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

        self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/api/heartbeat":
            # Lightweight liveness ping from the browser. We don't read the
            # body — presence of the request is the signal. last_seen is used
            # by the watchdog thread to decide whether the client is gone.
            self._state["last_seen"] = time.time()
            self._send_json(200, {"ok": True})
            return

        if self.path == "/api/cancel":
            # Explicit user-initiated cancel (UI button or ESC). Distinct exit
            # code so the agent can tell "user said no" from "we lost contact"
            # or "user picked answers".
            self._send_json(200, {"ok": True, "cancelled": True})
            self._state["exit_code"] = self.EXIT_USER_CANCELLED
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return

        if self.path != "/api/submit":
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

        try:
            self.result_path.parent.mkdir(parents=True, exist_ok=True)
            self.result_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            self._send_json(500, {"error": f"write failed: {exc}"})
            return

        self._send_json(200, {"ok": True, "saved_to": str(self.result_path)})
        self._state["exit_code"] = self.EXIT_SUBMITTED
        # Shutdown must run in a separate thread — calling it from inside a
        # request handler would deadlock serve_forever().
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        return


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _timestamped_default(spec_path: Path) -> Path:
    stamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return spec_path.with_name(f"{spec_path.stem}.{stamp}.result.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render and serve a decision-board board from a JSON spec.",
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
        "--no-open", action="store_true",
        help="Do not open the browser automatically.",
    )
    parser.add_argument(
        "--static", "-s", type=Path, default=None,
        help="Skip the server. Render the board to this HTML path and exit.",
    )
    args = parser.parse_args(argv)

    if not args.spec.is_file():
        print(f"error: spec not found: {args.spec}", file=sys.stderr)
        return 2

    try:
        load_spec(args.spec)
        validate_spec(load_spec(args.spec))
    except SpecError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # ---- static mode ------------------------------------------------------
    if args.static is not None:
        try:
            html = render_html_from_spec(args.spec)
        except SpecError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        args.static.parent.mkdir(parents=True, exist_ok=True)
        args.static.write_text(html, encoding="utf-8")
        print(f"wrote {args.static}")
        return 0

    # ---- server mode ------------------------------------------------------
    result_path = (args.output or _timestamped_default(args.spec)).resolve()

    # Shared state across handler instances. The handler can write here;
    # the watchdog thread reads here. We bias toward "client is alive" so
    # the watchdog doesn't fire before the page even loads.
    state = {
        "last_seen": time.time(),
        "exit_code": None,  # set by Submit (0) or Cancel (125) handler
    }
    HEARTBEAT_TIMEOUT = 60  # seconds without a ping before assuming the
                            # browser is gone (background tabs throttle
                            # timers, so this is generous on purpose)

    kill_port(args.port)
    handler = partial(BoardHandler, args.spec, result_path, state)
    try:
        server = HTTPServer(("127.0.0.1", args.port), handler)
        port = args.port
    except OSError:
        server = HTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]
        print(
            f"warning: port {args.port} unavailable, bound to {port} instead",
            file=sys.stderr,
        )

    # Agent contract: first stdout line is machine-parseable so the invoking
    # agent can capture the result location without scraping pretty output.
    # Machine-parseable header: result location + bound port, in that order.
    # The port matters when 7117 was busy and we fell back to an OS-assigned
    # one — the calling agent needs to know which URL to point the user at.
    print(f"RESULT_PATH={result_path}", flush=True)
    print(f"PORT={port}", flush=True)

    url = f"http://localhost:{port}"
    print()
    print("  Decision Board")
    print("  ─────────────────────────────────")
    print(f"  URL:    {url}")
    print(f"  Spec:   {args.spec}")
    print(f"  Result: {result_path}")
    print()
    print("  Decide in the browser. Submit when done, Cancel to abort.")
    print("  Server auto-exits on Submit/Cancel/disconnect.")
    print()

    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    # Watchdog: if the browser stops sending heartbeats for too long, assume
    # it's gone (tab closed, browser crashed, network died) and shut down
    # with exit 124. This is the only way to release the agent that's
    # blocked on us if the client can't send an explicit cancel.
    def _watchdog():
        while True:
            time.sleep(5)
            if state["exit_code"] is not None:
                return  # already terminating via Submit or Cancel
            if time.time() - state["last_seen"] > HEARTBEAT_TIMEOUT:
                state["exit_code"] = 124
                threading.Thread(target=server.shutdown, daemon=True).start()
                return

    threading.Thread(target=_watchdog, daemon=True).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
        print("  Stopped (no submission).")
        server.server_close()
        return 130

    server.server_close()
    # exit_code is set by whichever path triggered shutdown: 0 (Submit),
    # 125 (Cancel), or 124 (heartbeat timeout).
    return state["exit_code"] if state["exit_code"] is not None else 0


if __name__ == "__main__":
    sys.exit(main())
