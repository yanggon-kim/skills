#!/usr/bin/env python3
"""Read-only inventory of a directory for the main-agent-workspace skill.

Reports: git repositories (nested ones and submodules included) with remotes, branch and
uncommitted-change count; which repositories nest inside others; existing agent-system files
(CLAUDE.md, .claude/agents, ONBOARDING.md, HANDOFF.md); top-level entries with sizes; and the
suggested skill mode. Changes nothing.

Usage: inventory.py <dir> [--max-depth N] [--json]
"""
import argparse, json, os, subprocess, sys

SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", ".mypy_cache",
        ".pytest_cache", ".cache", "dist", "site-packages"}


def git(repo, *args):
    try:
        r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=20)
        return r.stdout.strip() if r.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def find_repos(root, max_depth):
    repos = []
    root = os.path.abspath(root)
    base_depth = root.rstrip(os.sep).count(os.sep)
    for cur, dirs, files in os.walk(root):
        depth = cur.rstrip(os.sep).count(os.sep) - base_depth
        if ".git" in dirs or ".git" in files:
            repos.append(cur)
        dirs[:] = [d for d in dirs if d not in SKIP and not d.startswith(".")] if depth < max_depth else []
    return repos


def repo_info(path):
    remotes = {}
    for line in git(path, "remote", "-v").splitlines():
        parts = line.split()
        if len(parts) >= 2:
            remotes[parts[0]] = parts[1]
    status = git(path, "status", "--porcelain")
    submodules = []
    gm = os.path.join(path, ".gitmodules")
    if os.path.isfile(gm):
        for line in open(gm, errors="replace"):
            if line.strip().startswith("path"):
                submodules.append(line.split("=", 1)[1].strip())
    return {
        "path": path,
        "branch": git(path, "branch", "--show-current") or "(detached or none)",
        "remotes": remotes,
        "uncommitted": len(status.splitlines()) if status else 0,
        "submodules": submodules,
        "markers": markers(path),
    }


def markers(path):
    m = []
    for name in ("CLAUDE.md", "ONBOARDING.md", "HANDOFF.md"):
        if os.path.isfile(os.path.join(path, name)):
            m.append(name)
    agents = os.path.join(path, ".claude", "agents")
    if os.path.isdir(agents):
        n = len([f for f in os.listdir(agents) if f.endswith(".md") and not f.startswith("_")])
        m.append(f".claude/agents ({n} owner files)")
    if any(f.lower().startswith("readme") for f in os.listdir(path)):
        m.append("README")
    return m


def size_of(path):
    try:
        r = subprocess.run(["du", "-sh", "--exclude=.git", path], capture_output=True, text=True, timeout=20)
        return r.stdout.split()[0] if r.returncode == 0 and r.stdout else "?"
    except (OSError, subprocess.TimeoutExpired):
        return "?"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir")
    ap.add_argument("--max-depth", type=int, default=4, help="directory depth to search for repositories (default 4)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    a = ap.parse_args()

    root = os.path.abspath(a.dir)
    if not os.path.isdir(root):
        sys.exit(f"not a directory: {root}")

    entries = sorted(e for e in os.listdir(root) if not e.startswith(".") or e == ".claude")
    top = [{"name": e, "type": "dir" if os.path.isdir(os.path.join(root, e)) else "file",
            "size": size_of(os.path.join(root, e))} for e in entries]
    repos = [repo_info(p) for p in find_repos(root, a.max_depth)]
    nesting = [(inner["path"], outer["path"]) for inner in repos for outer in repos
               if inner["path"] != outer["path"] and inner["path"].startswith(outer["path"] + os.sep)]
    root_markers = markers(root)

    has_setup = os.path.isdir(os.path.join(root, ".claude", "agents")) or (
        os.path.isfile(os.path.join(root, "CLAUDE.md"))
        and "| owner |" in open(os.path.join(root, "CLAUDE.md"), errors="replace").read())
    code_like = [t for t in top if t["name"] not in (".claude", "CLAUDE.md")]
    if has_setup:
        mode = "Audit (an owner table or owner agent files already exist)"
    elif not code_like:
        mode = "Set up the base (empty directory)"
    else:
        mode = "Set up the base, then report candidate sub-projects (existing codebase, no main-agent structure)"

    report = {"root": root, "suggested_mode": mode, "root_markers": root_markers,
              "top_level": top, "repositories": repos, "nesting": nesting}
    if a.json:
        print(json.dumps(report, indent=2))
        return

    print(f"# Inventory of `{root}`\n")
    print(f"**Suggested mode:** {mode}\n")
    print(f"**Agent-system files at the root:** {', '.join(root_markers) or 'none'}\n")
    print("## Top level\n\n| entry | type | size |\n|---|---|---|")
    for t in top:
        print(f"| `{t['name']}` | {t['type']} | {t['size']} |")
    print(f"\n## Git repositories ({len(repos)})\n")
    if not repos:
        print("None found within depth", a.max_depth)
    for r in repos:
        rel = os.path.relpath(r["path"], root)
        print(f"### `{rel}`")
        print(f"- branch: `{r['branch']}` · uncommitted changes: {r['uncommitted']}")
        if r["remotes"]:
            for name, url in r["remotes"].items():
                print(f"- remote `{name}`: {url}")
        else:
            print("- no remotes")
        if r["submodules"]:
            print(f"- submodules: {', '.join(r['submodules'])}")
        if r["markers"]:
            print(f"- has: {', '.join(r['markers'])}")
        print()
    if nesting:
        print("## Nesting (inner inside outer)\n")
        for inner, outer in nesting:
            print(f"- `{os.path.relpath(inner, root)}` inside `{os.path.relpath(outer, root)}`")
        print("\nNested repositories become separate sub-projects with exclusions in both owner files.")
    print("\n*Writers (people, CI, syncing editors) cannot be seen from files alone — ask the user.*")


if __name__ == "__main__":
    main()
