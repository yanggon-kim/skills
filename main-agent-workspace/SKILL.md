---
name: main-agent-workspace
description: Sets up and grows a project run by one main agent that delegates each sub-project to its own owner subagent — the main-agent contract in CLAUDE.md, an owner registry, a launcher that grants directory access, and a step-by-step procedure for adding an existing repository or directory as a sub-project (add-dir, an ONBOARDING.md survey written inside that project, the owner agent file, HANDOFF.md). Works on an empty directory or on a live codebase, and audits a setup that already exists. Use it whenever the user wants a main agent with sub-agents or owner agents, asks to split a project across several agents, says "add this repo as a sub-project", "onboard this project", "make an owner for this directory", "set up delegation", or asks why an owner cannot see a directory — even if the words main agent or subagent are never used.
---

# Main-agent workspace

One **main agent** coordinates; each **sub-project** belongs to exactly one **owner subagent** that
edits only its own root. Main routes work, writes the task brief, reads short reports, and relays
results — it never edits inside a registered root. The structure exists because a single session
editing several codebases mixes contexts and produces commits that sweep up other work.

This skill sets up the **frame, not the contents**. The base setup registers no owners and knows
nothing about the domain; owners are added one at a time, after setup, with the procedure in
`references/add-subproject.md`.

**Where things live.** Everything generic — the rules, the templates, the procedure, the scripts —
stays in this skill and is read from here. The project receives only facts about itself: its
`CLAUDE.md`, its launcher, one agent file per owner, and an `ONBOARDING.md` and `HANDOFF.md` at each
sub-project root. Do not copy this skill's references into the project; owners read them from the
installed skill, so a rule improved here is improved everywhere.

## First, detect the state

Run `python3 scripts/inventory.py <project dir>` (read-only). It reports git repositories, remotes,
nesting, and whether a `CLAUDE.md`, `.claude/agents/`, `ONBOARDING.md` or `HANDOFF.md` already
exists. Then pick the mode:

| what the directory holds | mode |
|---|---|
| nothing, or no codebase yet | **Set up the base** |
| a codebase but no main-agent structure | **Set up the base**, then offer candidate sub-projects |
| a `CLAUDE.md` with an owner table, or owner agent files | **Audit**, then add sub-projects as asked |
| the user names a path to add | **Add a sub-project** (run the base setup first if it is missing) |

## Mode 1 — Set up the base

Write exactly two files into the project, plus one memory note. Nothing else.

1. **`CLAUDE.md`** from `assets/CLAUDE.md.tmpl`: the main agent's role, the delegation rules in
   brief, an **empty** owner table, an **empty** remotes-and-writers table, a resource-cap line.
   - If a `CLAUDE.md` already exists, **do not overwrite it.** Show the user what it contains, move
     its content under a heading in the new file or into `CLAUDE.history.md` with their agreement,
     and keep the result under the budget in `references/context-layers.md`.
2. **`scripts/start-main.sh`** from `assets/start-main.sh.tmpl`, executable, with an **empty**
   `SUBPROJECTS` list. It launches the main session with `--add-dir` for every registered root.
3. **A memory note** in *main's own* memory (the session's memory directory, not the project),
   recording that this project runs in main-agent mode and why — so a later session starts in the
   right role. If the session has no memory tool, print the line for the user to keep instead, and
   say so.

On an existing codebase, finish by reporting the **candidate** sub-projects the inventory found —
one line each: path, what it appears to be, its remote, other likely writers — and **create no
owners**. The user chooses which to onboard.

Then tell the user, in two lines: start main with `scripts/start-main.sh` (append `--resume` to
continue a session), and add the first sub-project with "add `<path>` as sub-project `<name>`".

## Mode 2 — Add a sub-project

Follow `references/add-subproject.md` step by step; it is the heart of this skill. In short:

1. **Directory access** — `/add-dir` now, plus a line in the launcher for every later session.
2. **Survey** — an `ONBOARDING.md` written *inside* the sub-project from
   `assets/onboarding-prompt.md`: run in a session opened in that project when it has its own
   `CLAUDE.md` or history, otherwise from main with a read-only agent.
3. **Review** — the proposed scope, exclusions and writers, confirmed by the user.
4. **Register** — the owner agent file from `assets/owner.md.tmpl`, `HANDOFF.md` from
   `assets/HANDOFF.md.tmpl`, and a row in each of `CLAUDE.md`'s tables.
5. **Verify** — `python3 scripts/check_setup.py <project dir>`, then a fresh spawn of the new owner
   on a trivial read-only task.

## Mode 3 — Audit

Run `python3 scripts/check_setup.py <project dir>`. It cross-checks the four registries that must
agree — the owner table, `.claude/agents/`, the launcher, the remotes table — and reports missing
`ONBOARDING.md` / `HANDOFF.md`, nested roots without exclusions, repositories with no recorded
writer, and files over budget. Report findings; fix only what the user approves.

## Running the system day to day

`references/operating-model.md` is the rulebook main and every owner follow: routing, the spawn
brief, one task per fresh spawn, read-across/edit-within, report shape, background jobs, and the
limits of the model. `references/git-model.md` covers who may write which remote, shared git
indexes, external writers, and nested repositories. `references/context-layers.md` says what goes
in `CLAUDE.md`, `ONBOARDING.md`, `HANDOFF.md`, memory and archives, with size budgets.

Open the one that matches the question; none of them needs to be read in full to start.
