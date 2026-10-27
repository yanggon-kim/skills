#!/usr/bin/env python3
"""Check that a paper's outline.md and its LaTeX source list the same paragraphs in the same order.

Outline entries are lines of the form `- **[<id>]** ...`; source anchors are lines `% P:<id>`.
The .tex files are walked from the main file, following \\input / \\include in order.

Usage: check_outline.py outline.md main.tex
Exit 0 with one summary line when the lists match; exit 1 with the differences otherwise.
"""
import re
import sys
from pathlib import Path

ENTRY = re.compile(r"^\s*-\s+\*\*\[([a-z0-9][a-z0-9-]*)\]\*\*")
ANCHOR = re.compile(r"^\s*%\s*P:([a-z0-9][a-z0-9-]*)\s*$")
INPUT = re.compile(r"^[^%]*\\(?:input|include)\{([^}]+)\}")


def outline_ids(path):
    return [m.group(1) for line in path.read_text().splitlines() if (m := ENTRY.match(line))]


def tex_ids(path, seen=None):
    seen = seen if seen is not None else set()
    path = path if path.suffix == ".tex" else path.with_suffix(".tex")
    if path in seen or not path.exists():
        return []
    seen.add(path)
    ids = []
    for line in path.read_text().splitlines():
        if m := ANCHOR.match(line):
            ids.append(m.group(1))
        elif m := INPUT.match(line):
            ids += tex_ids(ROOT / m.group(1), seen)
    return ids


def dups(ids):
    return sorted({i for i in ids if ids.count(i) > 1})


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    outline, main = Path(sys.argv[1]), Path(sys.argv[2])
    ROOT = main.parent
    o, t = outline_ids(outline), tex_ids(main)
    errors = []
    for name, ids in (("outline", o), ("tex", t)):
        if d := dups(ids):
            errors.append(f"duplicate ids in {name}: {', '.join(d)}")
    if only := [i for i in o if i not in t]:
        errors.append(f"in outline, no anchor in tex: {', '.join(only)}")
    if only := [i for i in t if i not in o]:
        errors.append(f"anchored in tex, no outline entry: {', '.join(only)}")
    common_o = [i for i in o if i in set(t)]
    common_t = [i for i in t if i in set(o)]
    if common_o != common_t:
        k = next((n for n, (a, b) in enumerate(zip(common_o, common_t)) if a != b), None)
        if k is not None:
            errors.append(f"order differs at entry {k + 1}: outline has {common_o[k]}, tex has {common_t[k]}")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"check_outline: {len(o)} paragraphs, outline and tex agree")
