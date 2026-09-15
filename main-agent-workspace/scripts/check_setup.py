#!/usr/bin/env python3
"""Consistency check for a main-agent workspace.

Cross-checks the four registries that must agree — the owner table in CLAUDE.md, the owner agent
files in .claude/agents/, the SUBPROJECTS list in scripts/start-main.sh, and the remotes-and-writers
table in CLAUDE.md — and reports missing ONBOARDING.md / HANDOFF.md, nested roots without
exclusions, repositories with no recorded writer, unfilled placeholders, and files over budget.

Exit status: 0 when there are no errors (warnings allowed), 1 otherwise. Changes nothing.

Usage: check_setup.py <project dir>
"""
import os, re, subprocess, sys

CLAUDE_BUDGET, AGENT_BUDGET = 80, 50
PLACEHOLDER = re.compile(r"<[A-Z][A-Z0-9_]{2,}(?:[ ,:\u2014-][^>]*)?>")


def table_after(text, heading):
    """Rows of the first markdown table under '## <heading>' (header and separator removed)."""
    m = re.search(r"^##\s+" + re.escape(heading) + r"\s*$", text, re.M)
    if not m:
        return None
    rows = []
    for line in text[m.end():].splitlines():
        if line.startswith("## "):
            break
        if line.strip().startswith("|"):
            cells = [c.strip().strip("`").strip() for c in line.strip().strip("|").split("|")]
            rows.append(cells)
    return [r for r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]


def launcher_paths(path):
    if not os.path.isfile(path):
        return None
    text = open(path, errors="replace").read()
    m = re.search(r"SUBPROJECTS=\((.*?)\n\)", text, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        s = line.strip()
        if s.startswith("#"):
            continue
        q = re.match(r'"([^"]+)"', s)
        if q:
            out.append(os.path.abspath(q.group(1)))
    return out


def frontmatter(path):
    text = open(path, errors="replace").read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    fm = m.group(1) if m else ""
    name = re.search(r"^name:\s*(\S+)", fm, re.M)
    return {"name": name.group(1) if name else None, "has_description": "description:" in fm,
            "lines": text.count("\n") + 1, "text": text}


def repo_top(path):
    try:
        r = subprocess.run(["git", "-C", path, "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    proj = os.path.abspath(sys.argv[1])
    errors, warns = [], []
    E, W = errors.append, warns.append

    cpath = os.path.join(proj, "CLAUDE.md")
    if not os.path.isfile(cpath):
        print(f"ERROR  no CLAUDE.md in {proj} — run the base setup first")
        sys.exit(1)
    ctext = open(cpath, errors="replace").read()
    clines = ctext.count("\n") + 1
    if clines > CLAUDE_BUDGET:
        W(f"CLAUDE.md is {clines} lines (budget {CLAUDE_BUDGET}) — move detail to ONBOARDING.md files or an archive")
    for ph in sorted(set(PLACEHOLDER.findall(ctext))):
        W(f"CLAUDE.md still contains the placeholder {ph[:60]}")

    owners = table_after(ctext, "Owners")
    remotes = table_after(ctext, "Remotes and writers")
    if owners is None:
        E("CLAUDE.md has no '## Owners' table")
        owners = []
    if remotes is None:
        W("CLAUDE.md has no '## Remotes and writers' table")
        remotes = []

    agents_dir = os.path.join(proj, ".claude", "agents")
    agent_files = {}
    if os.path.isdir(agents_dir):
        for f in sorted(os.listdir(agents_dir)):
            if f.endswith(".md") and not f.startswith("_"):
                agent_files[f[:-3]] = frontmatter(os.path.join(agents_dir, f))

    launcher = launcher_paths(os.path.join(proj, "scripts", "start-main.sh"))
    if launcher is None:
        W("no scripts/start-main.sh — roots outside the project directory need it (or /add-dir each session)")
        launcher = []

    roots = {}
    for row in owners:
        if len(row) < 2 or not row[0]:
            continue
        owner, root = row[0], os.path.abspath(os.path.expanduser(row[1]))
        excludes = row[3] if len(row) > 3 else ""
        roots[owner] = (root, excludes)

        af = agent_files.get(owner)
        if af is None:
            E(f"owner '{owner}' is in the table but .claude/agents/{owner}.md does not exist")
        else:
            if af["name"] != owner:
                E(f".claude/agents/{owner}.md has frontmatter name '{af['name']}', expected '{owner}'")
            if not af["has_description"]:
                E(f".claude/agents/{owner}.md has no description — main cannot route to it")
            if af["lines"] > AGENT_BUDGET:
                W(f".claude/agents/{owner}.md is {af['lines']} lines (budget {AGENT_BUDGET})")
            for ph in sorted(set(PLACEHOLDER.findall(af["text"]))):
                W(f".claude/agents/{owner}.md still contains the placeholder {ph[:60]}")

        if not os.path.isdir(root):
            E(f"owner '{owner}': root {root} is not a directory")
            continue
        inside = root == proj or root.startswith(proj + os.sep)
        if not inside and root not in launcher:
            E(f"owner '{owner}': root {root} is outside the project and missing from scripts/start-main.sh")
        for doc in ("ONBOARDING.md", "HANDOFF.md"):
            if not os.path.isfile(os.path.join(root, doc)):
                W(f"owner '{owner}': {root}/{doc} is missing")

    for name in agent_files:
        if name not in roots:
            E(f".claude/agents/{name}.md exists but '{name}' is not in the CLAUDE.md owner table")
    listed = {r for r, _ in roots.values()}
    for p in launcher:
        if p not in listed:
            W(f"scripts/start-main.sh lists {p}, which is no owner's root")

    for a_owner, (a_root, _) in roots.items():
        for b_owner, (b_root, b_excl) in roots.items():
            if a_owner != b_owner and a_root.startswith(b_root + os.sep):
                rel = os.path.relpath(a_root, b_root)
                b_text = agent_files.get(b_owner, {}).get("text", "")
                if rel not in b_excl and a_root not in b_excl and rel not in b_text and a_root not in b_text:
                    W(f"'{a_owner}' root is nested in '{b_owner}' root, but {b_owner} does not exclude '{rel}'")

    remote_cells = " ".join(" ".join(r) for r in remotes)
    seen_tops = set()
    for owner, (root, _) in roots.items():
        top = repo_top(root) if os.path.isdir(root) else None
        if not top or top in seen_tops:
            continue
        seen_tops.add(top)
        rel = os.path.relpath(top, proj)
        if top not in remote_cells and rel not in remote_cells and os.path.basename(top) not in remote_cells:
            W(f"git repository {top} (under '{owner}') has no row in the remotes-and-writers table")

    for msg in errors:
        print("ERROR ", msg)
    for msg in warns:
        print("WARN  ", msg)
    n_owners = len(roots)
    print(f"\n{n_owners} owner(s) registered · {len(errors)} error(s) · {len(warns)} warning(s)")
    if not errors and not warns:
        print("All registries agree.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
