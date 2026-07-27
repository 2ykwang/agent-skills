#!/usr/bin/env python3
"""Stage selected hunks of a file non-interactively.

`git add -p` is interactive and unusable in agent environments. This script
lists the unstaged hunks of a file and stages only the selected ones by
building a partial patch and applying it to the index.

Usage:
    stage_hunks.py list <file>
    stage_hunks.py stage <file> <hunk_no> [<hunk_no> ...]

Hunk numbers are 1-based and come from `list`. After staging a subset, the
remaining hunks are renumbered on the next `list` (the unstaged diff shrinks).
"""

import subprocess
import sys
from typing import NoReturn


def fail(message: str) -> NoReturn:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def unstaged_diff(path: str) -> str:
    result = subprocess.run(["git", "diff", "--", path], capture_output=True, text=True)
    if result.returncode != 0:
        fail(result.stderr.strip() or "git diff failed")
    return result.stdout


def split_hunks(diff_text: str) -> tuple[list[str], list[list[str]]]:
    """Split a single-file diff into (header lines, list of hunk line-lists)."""
    header: list[str] = []
    hunks: list[list[str]] = []
    current: list[str] | None = None
    for line in diff_text.splitlines(keepends=True):
        if line.startswith("@@"):
            if current is not None:
                hunks.append(current)
            current = [line]
        elif current is not None:
            current.append(line)
        else:
            header.append(line)
    if current is not None:
        hunks.append(current)
    return header, hunks


def summarize(hunk: list[str]) -> str:
    added = sum(1 for line in hunk[1:] if line.startswith("+"))
    removed = sum(1 for line in hunk[1:] if line.startswith("-"))
    first_change = next(
        (line.strip() for line in hunk[1:] if line.startswith(("+", "-"))),
        "",
    )
    location = hunk[0].strip()
    return f"{location}  (+{added}/-{removed})  {first_change[:80]}"


def load(path: str) -> tuple[list[str], list[list[str]]]:
    diff_text = unstaged_diff(path)
    if not diff_text:
        fail(f"no unstaged changes in {path} (untracked file? stage it whole with `git add`)")
    header_text = "".join(diff_text.splitlines(keepends=True)[:10])
    if "Binary files" in header_text:
        fail("binary file - stage it whole with `git add`")
    if "rename from" in header_text:
        fail("rename detected - stage it whole with `git add`")
    return split_hunks(diff_text)


def cmd_list(path: str) -> None:
    _, hunks = load(path)
    for number, hunk in enumerate(hunks, start=1):
        print(f"{number}: {summarize(hunk)}")


def cmd_stage(path: str, numbers: list[str]) -> None:
    header, hunks = load(path)
    try:
        selected = sorted({int(n) for n in numbers})
    except ValueError:
        fail(f"hunk numbers must be integers: {numbers}")
    invalid = [n for n in selected if not 1 <= n <= len(hunks)]
    if invalid:
        fail(f"hunk number out of range {invalid} (file has {len(hunks)} hunks)")

    patch = "".join(header) + "".join("".join(hunks[n - 1]) for n in selected)
    result = subprocess.run(["git", "apply", "--cached", "-"], input=patch, capture_output=True, text=True)
    if result.returncode != 0:
        fail(f"git apply --cached failed:\n{result.stderr}")
    print(f"staged hunk {selected} of {path}")


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "list":
        cmd_list(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "stage":
        cmd_stage(sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
