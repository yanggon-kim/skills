#!/usr/bin/env python3
"""update_progress.py — atomic edit to PROGRESS.md.

Usage:
  update_progress.py <step> <status> [artifact_path] [note]

  <step>     One of: 1, 2, 3, 4, 5, 6, 6A, 6B, 7, 8
  <status>   One of: pending, in-progress, blocked, done
  artifact_path   Optional path to the step's output artifact
  note            Optional one-line free-text note

Operates on $PWD/PROGRESS.md (the workspace root).

The PROGRESS.md format is a strict markdown table; this script parses, mutates,
and rewrites it atomically (write to .tmp, then rename) so partial writes can't
corrupt it.
"""

from __future__ import annotations

import datetime as _dt
import os
import re
import sys
from pathlib import Path


VALID_STEPS = {"1", "2", "3", "4", "5", "6", "6A", "6B", "7", "8"}
VALID_STATUSES = {"pending", "in-progress", "blocked", "done"}


def main() -> int:
    if len(sys.argv) < 3 or len(sys.argv) > 5:
        print(__doc__.strip(), file=sys.stderr)
        return 1

    step = sys.argv[1]
    status = sys.argv[2]
    artifact = sys.argv[3] if len(sys.argv) > 3 else ""
    note = sys.argv[4] if len(sys.argv) > 4 else ""

    if step not in VALID_STEPS:
        print(f"error: invalid step '{step}'. Must be one of {sorted(VALID_STEPS)}.", file=sys.stderr)
        return 2
    if status not in VALID_STATUSES:
        print(f"error: invalid status '{status}'. Must be one of {sorted(VALID_STATUSES)}.", file=sys.stderr)
        return 2

    progress_path = Path("PROGRESS.md")
    if not progress_path.exists():
        print(f"error: PROGRESS.md not found in {Path.cwd()}. Run init_workspace.sh first.", file=sys.stderr)
        return 3

    content = progress_path.read_text()

    # Find the row for this step. Step rows look like:
    # | 1 | Target Workload Search | pending |  |  |
    pattern = re.compile(
        rf"^(\| *{re.escape(step)} *\| *[^|]+\|) *([^|]*)\| *([^|]*)\| *([^|]*?) *\|$",
        re.MULTILINE,
    )

    match = pattern.search(content)
    if not match:
        print(f"error: could not find step '{step}' row in PROGRESS.md.", file=sys.stderr)
        print("       Check that the file matches the template (8 step rows in a markdown table).", file=sys.stderr)
        return 4

    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    note_with_timestamp = f"{note} ({timestamp})" if note else f"updated {timestamp}"

    new_row = f"{match.group(1)} {status} | {artifact} | {note_with_timestamp} |"
    new_content = content[:match.start()] + new_row + content[match.end():]

    # Atomic write.
    tmp = progress_path.with_suffix(".md.tmp")
    tmp.write_text(new_content)
    os.replace(tmp, progress_path)

    print(f"step {step}: {status}" + (f" → {artifact}" if artifact else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
