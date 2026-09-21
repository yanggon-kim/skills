#!/usr/bin/env python3
"""update_solution_ledger.py — atomic edits to final_solution_candidates.md.

Actions:
  append <id> <status> <impl_dir>           Add a new individual entry
  flip <id> <new_status> [reason]           Change status of an existing entry
  combine <id_a> <id_b>                     Add a new combined entry (auto-id)
  set-paper-id <id> <final_paper_id>        Set the final_paper_id field
  list                                       Print the table

The file's structure:

    # Final Solution Candidates

    | id | status | from_brainstorm_id / combination_of | reason_for_status | implementation_dir | final_paper_id |
    |----|--------|--------------------------------------|-------------------|--------------------|----------------|
    | sw_01 | survived | sw_01 |  | 05_implementations/sw_01/ |  |
    | hw_03 | dropped  | hw_03 | implemented faithfully but no speedup | 05_implementations/hw_03/ |  |
    ...

Operates on $PWD/final_solution_candidates.md.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


VALID_STATUSES = {"in_progress", "survived", "dropped"}
COMBINED_PREFIX = "combined-from-"


def read_table(path: Path):
    content = path.read_text()
    lines = content.splitlines()
    head_idx = None
    for i, line in enumerate(lines):
        if line.startswith("| id |"):
            head_idx = i
            break
    if head_idx is None:
        raise SystemExit(f"error: could not find table header in {path}.")
    sep_idx = head_idx + 1
    body_start = sep_idx + 1
    body_end = len(lines)
    while body_end > body_start and not lines[body_end - 1].startswith("|"):
        body_end -= 1
    pre = lines[: body_start]
    rows = lines[body_start:body_end]
    post = lines[body_end:]
    return pre, rows, post, content


def parse_row(row: str):
    # Split on | and strip; expect 8 segments (leading/trailing empty + 6 fields).
    parts = [p.strip() for p in row.split("|")]
    if len(parts) < 8:
        return None
    return {
        "id": parts[1],
        "status": parts[2],
        "linkage": parts[3],
        "reason": parts[4],
        "impl_dir": parts[5],
        "paper_id": parts[6],
    }


def fmt_row(entry: dict) -> str:
    return (
        f"| {entry['id']} | {entry['status']} | {entry['linkage']} | "
        f"{entry['reason']} | {entry['impl_dir']} | {entry['paper_id']} |"
    )


def find_row(rows, _id):
    for i, r in enumerate(rows):
        parsed = parse_row(r)
        if parsed and parsed["id"] == _id:
            return i, parsed
    return None, None


def write_atomic(path: Path, lines):
    tmp = path.with_suffix(".md.tmp")
    tmp.write_text("\n".join(lines) + "\n")
    os.replace(tmp, path)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 1

    action = sys.argv[1]
    path = Path("final_solution_candidates.md")
    if not path.exists():
        print(f"error: {path} not found in {Path.cwd()}.", file=sys.stderr)
        return 2

    pre, rows, post, _ = read_table(path)

    if action == "list":
        for r in rows:
            print(r)
        return 0

    if action == "append":
        if len(sys.argv) != 5:
            print("usage: append <id> <status> <impl_dir>", file=sys.stderr)
            return 1
        _id, status, impl_dir = sys.argv[2], sys.argv[3], sys.argv[4]
        if status not in VALID_STATUSES:
            print(f"error: invalid status '{status}'.", file=sys.stderr)
            return 1
        # Refuse to duplicate.
        idx, _ = find_row(rows, _id)
        if idx is not None:
            print(f"error: id '{_id}' already exists.", file=sys.stderr)
            return 3
        entry = {
            "id": _id,
            "status": status,
            "linkage": _id,  # for individuals, linkage = brainstorm id
            "reason": "",
            "impl_dir": impl_dir,
            "paper_id": "",
        }
        rows.append(fmt_row(entry))

    elif action == "flip":
        if len(sys.argv) < 4:
            print("usage: flip <id> <new_status> [reason]", file=sys.stderr)
            return 1
        _id, new_status = sys.argv[2], sys.argv[3]
        reason = sys.argv[4] if len(sys.argv) > 4 else ""
        idx, parsed = find_row(rows, _id)
        if idx is None:
            print(f"error: id '{_id}' not found.", file=sys.stderr)
            return 3
        # Allow combined-from-X-and-Y as a status string too, beyond VALID_STATUSES.
        if new_status not in VALID_STATUSES and not new_status.startswith(COMBINED_PREFIX):
            print(f"error: invalid status '{new_status}'.", file=sys.stderr)
            return 1
        parsed["status"] = new_status
        if reason:
            parsed["reason"] = reason
        rows[idx] = fmt_row(parsed)

    elif action == "combine":
        if len(sys.argv) != 4:
            print("usage: combine <id_a> <id_b>", file=sys.stderr)
            return 1
        a, b = sys.argv[2], sys.argv[3]
        # Verify both individuals exist and are survived.
        for ind in (a, b):
            idx, parsed = find_row(rows, ind)
            if idx is None:
                print(f"error: constituent '{ind}' not found.", file=sys.stderr)
                return 3
            if parsed["status"] != "survived":
                print(f"error: constituent '{ind}' is not survived (current: {parsed['status']}).", file=sys.stderr)
                return 4
        combined_id = f"combined_{a}_{b}"
        idx, _ = find_row(rows, combined_id)
        if idx is not None:
            print(f"error: combined id '{combined_id}' already exists.", file=sys.stderr)
            return 3
        entry = {
            "id": combined_id,
            "status": "in_progress",
            "linkage": f"combination_of: [{a}, {b}]",
            "reason": "",
            "impl_dir": f"05_implementations/{combined_id}/",
            "paper_id": "",
        }
        rows.append(fmt_row(entry))

    elif action == "set-paper-id":
        if len(sys.argv) != 4:
            print("usage: set-paper-id <id> <final_paper_id>", file=sys.stderr)
            return 1
        _id, paper_id = sys.argv[2], sys.argv[3]
        idx, parsed = find_row(rows, _id)
        if idx is None:
            print(f"error: id '{_id}' not found.", file=sys.stderr)
            return 3
        parsed["paper_id"] = paper_id
        rows[idx] = fmt_row(parsed)

    else:
        print(f"error: unknown action '{action}'.", file=sys.stderr)
        return 1

    write_atomic(path, pre + rows + post)
    print(f"{action}: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
