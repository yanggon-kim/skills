#!/usr/bin/env python3
"""Validate a built deck's package.

Run:   <work>/venv/bin/python validate_deck.py DECK.pptx [--template TEMPLATE.pptx]

Uses the pptx skill's validate.py (XSD schemas, relationships, content types, slide checks) when it can be
found (PPTX_SKILL_DIR, else a search under ~/.claude/skills), baselined with --original against the brand
template so the template's own schema quirks do not count as the deck's. That skill is optional: without
it this script runs a minimal check instead (every XML part parses, every relationship target exists,
python-pptx opens the deck and every slide has a layout) and says so.
"""
import argparse
import glob
import os
import posixpath
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(os.path.dirname(HERE), "assets", "ucla", "Presentation-01-master.pptx")


def find_validator():
    cands = []
    if os.environ.get("PPTX_SKILL_DIR"):
        cands.append(os.path.join(os.environ["PPTX_SKILL_DIR"], "scripts", "office", "validate.py"))
    cands += glob.glob(os.path.expanduser("~/.claude/skills/**/pptx/scripts/office/validate.py"), recursive=True)
    return next((c for c in cands if os.path.isfile(c)), None)


def minimal(deck):
    from lxml import etree
    from pptx import Presentation
    problems = []
    with zipfile.ZipFile(deck) as z:
        names = set(z.namelist())
        for n in names:
            if n.endswith((".xml", ".rels")):
                try:
                    root = etree.fromstring(z.read(n))
                except etree.XMLSyntaxError as e:
                    problems.append(f"{n}: {e}")
                    continue
                if n.endswith(".rels"):
                    base = posixpath.dirname(posixpath.dirname(n))
                    for r in root:
                        if r.get("TargetMode") == "External":
                            continue
                        t = r.get("Target")
                        p = t.lstrip("/") if t.startswith("/") else posixpath.normpath(posixpath.join(base, t))
                        if p not in names:
                            problems.append(f"{n}: missing target {t}")
    prs = Presentation(deck)
    for i, s in enumerate(prs.slides, 1):
        if s.slide_layout is None:
            problems.append(f"slide {i}: no layout")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--template", default=TEMPLATE)
    a = ap.parse_args()
    v = find_validator()
    if v:
        args = [sys.executable, v, a.deck] + (["--original", a.template] if a.template and os.path.isfile(a.template) else [])
        r = subprocess.run(args, capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        print(f"validator: {v}")
        sys.exit(r.returncode)
    print("pptx skill validate.py not found: running the minimal package check only")
    problems = minimal(a.deck)
    for p in problems:
        print("FAIL", p)
    print("PASS (minimal)" if not problems else f"{len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
