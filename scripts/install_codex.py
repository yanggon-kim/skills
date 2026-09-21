#!/usr/bin/env python3
"""Install this collection as project or per-user Codex skill symlinks."""

import argparse
import os
from pathlib import Path
import sys

from codex_catalog import catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--project", type=Path, help="Project root; install into its .agents/skills")
    scope.add_argument("--user", action="store_true", help="Install into ~/.agents/skills")
    parser.add_argument("--dry-run", action="store_true", help="Validate destinations without writing")
    args = parser.parse_args()
    if args.project is not None and not args.project.expanduser().is_dir():
        parser.error("--project must name an existing directory")
    root = args.project.expanduser().resolve() if args.project is not None else Path.home()
    destination = root / ".agents" / "skills"
    try:
        entries = catalog()
        pending = []
        # Check every collision before creating anything. Never replace someone else's skill.
        for name, source in entries.items():
            target = destination / name
            if target.is_symlink() and target.resolve() == source.resolve():
                continue
            if target.exists() or target.is_symlink():
                raise ValueError(f"Refusing to overwrite {target}; choose a different checkout or resolve the collision manually")
            pending.append((target, source))
        if not args.dry_run:
            destination.mkdir(parents=True, exist_ok=True)
            for target, source in pending:
                target.symlink_to(os.path.relpath(source, destination), target_is_directory=True)
        action = "Would install" if args.dry_run else "Installed"
        print(f"{action} {len(pending)} links; {len(entries) - len(pending)} already current; {len(entries)} skills total")
        print(f"Destination: {destination}")
        print("Keep this checkout on the codex branch; links follow its working files.")
        print("Use /skills or $skill-name in Codex CLI/IDE. Restart if the catalog has not refreshed.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
