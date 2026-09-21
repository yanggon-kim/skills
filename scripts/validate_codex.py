#!/usr/bin/env python3
"""Validate metadata, local Markdown links, Python syntax, and shell syntax."""

import ast
from pathlib import Path
import re
import subprocess
import sys

from codex_catalog import ROOT, catalog


def main():
    errors = []
    try:
        entries = catalog()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    # The explicit catalog prevents examples and archival documents becoming skills.
    actual = {p.resolve() for p in ROOT.rglob("SKILL.md") if ".git" not in p.parts
              and ".agents" not in p.parts}
    expected = {(p / "SKILL.md").resolve() for p in entries.values()}
    if actual != expected:
        errors.append(f"Uncatalogued or missing skill entrypoints: {actual ^ expected}")
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in path.parts for part in (".git", ".agents", "__pycache__", "legacy", "acm-template")):
            continue
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except SyntaxError as exc:
                errors.append(str(exc))
        if path.suffix == ".sh" or path.name.endswith(".sh.tmpl"):
            result = subprocess.run(["bash", "-n", str(path)], capture_output=True, text=True)
            if result.returncode:
                errors.append(result.stderr)
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8")
            for link in re.findall(r"(?<!!)\[[^\]\n]*\]\(([^)\s]+)\)", text):
                link = link.split("#", 1)[0]
                if not link or "://" in link or link.startswith(("/", "mailto:")):
                    continue
                if not (path.parent / link).exists():
                    errors.append(f"Broken relative link: {path.relative_to(ROOT)} -> {link}")
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1
    print(f"Validated {len(entries)} unique Codex skills, local Markdown links, Python syntax, and shell syntax.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
