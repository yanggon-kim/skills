#!/usr/bin/env python3
"""find_orthogonal_pairs.py — identify orthogonal pairs among Phase 6A survivors.

Reads:
  $PWD/03_solutions/03_solutions.json  — for root_cause_it_targets and proposed_mechanism
  $PWD/final_solution_candidates.md    — for which ideas have status: survived

Outputs to stdout (and writes 05_implementations/_orthogonality_report.md):
  A list of (id_a, id_b) pairs (and optionally triples) where:
    - Both are survived
    - Their root_cause_it_targets fields don't overlap
    - Their proposed_mechanism fields don't overlap

Two ideas are orthogonal when they attack different bottlenecks via different
levers — see step-06b-combinations.md.
"""

from __future__ import annotations

import itertools
import json
import re
import sys
from pathlib import Path


def parse_ledger(path: Path):
    """Return list of dicts for survived entries only."""
    survived = []
    for line in path.read_text().splitlines():
        if not line.startswith("| ") or line.startswith("| id |") or line.startswith("|--"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 8:
            continue
        if parts[2] == "survived":
            survived.append({"id": parts[1], "linkage": parts[3]})
    return survived


def load_solutions(path: Path):
    """Return dict id -> solution object from 03_solutions.json."""
    data = json.loads(path.read_text())
    sols = data.get("solutions", []) if isinstance(data, dict) else data
    return {s["id"]: s for s in sols}


def tokens_from(text: str):
    """Lower-case word set, treating dashes/slashes as separators. Loose orthogonality test."""
    return set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))


def overlap(a: str, b: str) -> bool:
    """Return True if a and b share content beyond stopwords."""
    ta = tokens_from(a)
    tb = tokens_from(b)
    # Filter out tiny common tokens that don't carry meaning.
    stop = {"the", "a", "an", "of", "in", "on", "to", "for", "with", "and", "or",
            "is", "are", "by", "via", "at", "as", "be", "this", "that", "we", "our"}
    ta -= stop
    tb -= stop
    return len(ta & tb) > 0


def main() -> int:
    sols_path = Path("03_solutions/03_solutions.json")
    ledger_path = Path("final_solution_candidates.md")
    if not sols_path.exists():
        print(f"error: {sols_path} not found.", file=sys.stderr)
        return 2
    if not ledger_path.exists():
        print(f"error: {ledger_path} not found.", file=sys.stderr)
        return 2

    survived = parse_ledger(ledger_path)
    if len(survived) < 2:
        print("Fewer than 2 survived entries — no pairs possible.")
        return 0

    sols = load_solutions(sols_path)
    survived_ids = [s["id"] for s in survived]
    missing = [sid for sid in survived_ids if sid not in sols]
    if missing:
        print(f"warning: survived ids not found in 03_solutions.json: {missing}", file=sys.stderr)
        print("         (possibly entries hand-added by the user; orthogonality skipped for them)", file=sys.stderr)
        survived_ids = [sid for sid in survived_ids if sid in sols]

    pairs = []
    for a, b in itertools.combinations(survived_ids, 2):
        sa, sb = sols[a], sols[b]
        rca, rcb = sa.get("root_cause_it_targets", ""), sb.get("root_cause_it_targets", "")
        ma, mb = sa.get("proposed_mechanism", ""), sb.get("proposed_mechanism", "")
        if not overlap(rca, rcb) and not overlap(ma, mb):
            pairs.append((a, b))

    triples = []
    for a, b, c in itertools.combinations(survived_ids, 3):
        if (a, b) in pairs and (a, c) in pairs and (b, c) in pairs:
            triples.append((a, b, c))

    # Print and persist.
    report_lines = ["# Orthogonality report\n", f"Survived ideas: {survived_ids}\n", "## Orthogonal pairs\n"]
    if pairs:
        for a, b in pairs:
            line = f"- ({a}, {b})"
            print(line)
            report_lines.append(line)
    else:
        report_lines.append("(none — no orthogonal pairs found)")
        print("(none)")
    if triples:
        report_lines.append("\n## Orthogonal triples\n")
        for trip in triples:
            line = f"- ({', '.join(trip)})"
            print(line)
            report_lines.append(line)

    out = Path("05_implementations/_orthogonality_report.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(report_lines) + "\n")
    print(f"\nReport saved → {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
