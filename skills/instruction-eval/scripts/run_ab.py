#!/usr/bin/env python3
"""Run the same prompts n times in each of two directories and collect the results.

This script doesn't know what differs between the two conditions or how they were
built. It takes two directories, runs them, and collects metrics. Constructing the
conditions is a case-by-case judgment call, so the caller does it.

Only output_tokens, num_turns and duration_ms are usable for comparison. The rest
are dominated by prompt caching.

- input_tokens: nearly all input is absorbed by the cache, so what's left is a
  residue of cache-hit patterns.
- cost_usd: cache writes are expensive, reads are cheap. Cache-hit patterns depend
  on run timing, so cost can move opposite to actual work. Recorded only.
"""

import argparse
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


METRICS = ["duration_ms", "num_turns", "output_tokens"]


def run_one(work: Path, arm: str, cwd: Path, pid: str, prompt: str, rep: int, model: str) -> dict:
    proc = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", model],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=900,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = {"is_error": True, "result": proc.stdout[:500] + "\n--STDERR--\n" + proc.stderr[:500]}

    rec = {
        "arm": arm,
        "prompt_id": pid,
        "rep": rep,
        "duration_ms": data.get("duration_ms"),
        "num_turns": data.get("num_turns"),
        "output_tokens": (data.get("usage") or {}).get("output_tokens"),
        "cost_usd": data.get("total_cost_usd"),
        "denials": len(data.get("permission_denials") or []),
        "is_error": data.get("is_error"),
        "result": data.get("result", ""),
    }
    out = work / "runs" / f"{pid}__{arm}__{rep}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, ensure_ascii=False, indent=1))
    print(f"[{pid}] {arm} rep{rep}: {rec['duration_ms']}ms turns={rec['num_turns']}", flush=True)
    return rec


def median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    mid = len(xs) // 2
    return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2


def summarize(records: list[dict]) -> dict:
    """Median and observed range per prompt x arm.

    Medians alone aren't enough. Agent runs swing hard even under identical
    conditions, and the gap between two arms' medians is often smaller than each
    arm's own spread. When that happens the delta is noise, not an effect. Keep min
    and max so the reader can tell.
    """
    out = {}
    for pid in sorted({r["prompt_id"] for r in records}):
        out[pid] = {}
        for arm in ("baseline", "variant"):
            rows = [r for r in records if r["prompt_id"] == pid and r["arm"] == arm]
            stats = {}
            for k in METRICS:
                vals = [r[k] for r in rows if r[k] is not None]
                stats[k] = {"med": median(vals), "min": min(vals, default=None), "max": max(vals, default=None)}
            out[pid][arm] = stats | {
                "n": len(rows),
                "errors": sum(1 for r in rows if r["is_error"]),
                "denials": sum(r["denials"] for r in rows),
            }
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Run the same prompts in two directories and compare")
    ap.add_argument("--baseline", required=True, help="directory holding the before condition")
    ap.add_argument("--variant", required=True, help="directory holding the after condition")
    ap.add_argument("--prompts", required=True, help="prompts JSON file")
    ap.add_argument("--work", required=True, help="directory to write results to")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--model", required=True, help="current session model ID")
    args = ap.parse_args()

    work = Path(args.work).resolve()
    dirs = {"baseline": Path(args.baseline).resolve(), "variant": Path(args.variant).resolve()}
    prompts = json.loads(Path(args.prompts).read_text())
    shutil.rmtree(work / "runs", ignore_errors=True)

    # Run in parallel. Sequentially, the arm that finishes first builds a prompt
    # cache the later one reuses, systematically lowering its duration_ms.
    jobs = [
        (work, arm, dirs[arm], p["id"], p["prompt"], rep, args.model)
        for p in prompts
        for rep in range(args.n)
        for arm in dirs
    ]
    # Total runs grow as n x prompts x 2. Without printing it up front there's no way
    # to gauge how long this will take.
    print(f"{len(jobs)} runs total ({len(prompts)} prompts x n={args.n} x 2 arms), 6 in parallel", flush=True)
    with ThreadPoolExecutor(max_workers=6) as ex:
        records = list(ex.map(lambda a: run_one(*a), jobs))

    summary = {
        "meta": {
            "n": args.n,
            "runs": len(jobs),
            "model": args.model,
            "baseline_dir": str(dirs["baseline"]),
            "variant_dir": str(dirs["variant"]),
        },
        "prompts": prompts,
        "results": summarize(records),
    }
    (work / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"\nResults: {work}/runs, {work}/summary.json\nNext: build the HTML report with render_report.py.")


if __name__ == "__main__":
    main()
