# Adding a sub-project

The procedure main follows when the user says **"add `<path>` as sub-project `<name>`"**, or asks to
bring an existing repository or directory under an owner. Five steps; do them in order and tell the
user where each one stands. If the project has no `CLAUDE.md` owner table yet, run the base setup
(SKILL.md, Mode 1) first.

Choose `<name>` as a short kebab-case word (`sim`, `paper`, `site`); the owner becomes
`<name>-owner`.

---

## Step 1 — Give main access to the directory

A subagent can reach only what its parent session can, so the path must be accessible to **main**
before the owner is ever spawned.

| method | scope | use it when |
|---|---|---|
| `/add-dir <absolute path>` typed in the running session | this session only | onboarding right now |
| a line in `scripts/start-main.sh` → `--add-dir` | every session started with the launcher | always, so the next session has it |
| `permissions.additionalDirectories` in a settings file | every session, silently | only if the user prefers settings; access is then less visible |

**Do both of the first two.** Tell the user to type `/add-dir <path>` now (main cannot run it for
them), and add the path to the `SUBPROJECTS` list in `scripts/start-main.sh`, one line with a comment
naming the sub-project and its owner:

```bash
SUBPROJECTS=(
  "/abs/path/to/project"   # <name> (owner: <name>-owner)
)
```

A path *inside* the main project directory is already reachable; list it anyway so the launcher
doubles as the registry of roots.

Confirm access before moving on: read one file from the path.

---

## Step 2 — Survey the project into its own `ONBOARDING.md`

`ONBOARDING.md` is written **inside the sub-project's root**. It holds the stable facts a new owner
needs to take over without further context: identity, layout, commands, git and writers, existing
guidance, traps, and a proposed scope. The prompt is `assets/onboarding-prompt.md`.

**Where to run the survey:**

- **A Claude session opened in that project** — the default whenever the project has its own
  `CLAUDE.md`, memory, or a history of work, because that session already knows it. Print the prompt
  from `assets/onboarding-prompt.md` for the user to paste there, and ask them to tell you when
  `ONBOARDING.md` exists.
- **From main**, with a read-only agent given the same prompt — when the project has no history of
  its own (a fresh clone, a directory of scripts). Do not let that agent edit anything but
  `ONBOARDING.md`.
- **By main itself**, reading the files directly — for a small root (a few dozen files), or when
  spawning is unavailable. The survey is read-only either way; what matters is that every claim
  comes from a file and unknowns go to "open questions" rather than being guessed.

**Keep the survey out of the project's git by default.** `ONBOARDING.md` and `HANDOFF.md` describe the
agent system, not the project, and other people may use the repository. Add both to
`<repo>/.git/info/exclude` (local, untracked, never pushed). Commit them only if the user asks.

---

## Step 3 — Review with the user

Summarize `ONBOARDING.md` in a few lines and ask the user to confirm or correct:

- **Scope** — what the owner owns.
- **Exclusions** — nested roots belonging to another owner, shared data, generated trees.
- **Writers** — every writer of each git remote (people, CI, a document editor that syncs to git,
  another clone). This decides the git rules in step 4.
- **Model and effort** for the owner (default `inherit` / `high`).
- The survey's **open questions**.

Nothing is registered until the user confirms.

---

## Step 4 — Register the owner

1. **Agent file.** Copy `assets/owner.md.tmpl` to `<project>/.claude/agents/<name>-owner.md`. Fill
   every `<PLACEHOLDER>`, including the description's "NOT …" clause naming what other owners hold.
   Keep it under 50 lines. New agent files are picked up by a running session within seconds — wait
   for the notice rather than asking for a restart.
2. **HANDOFF.md.** Create `<root>/HANDOFF.md` from `assets/HANDOFF.md.tmpl`. Seed "Current status"
   and "Open issues" from the survey's current-state section; mark the rest `<TBD by owner>`.
   `ONBOARDING.md` keeps the stable facts; `HANDOFF.md` keeps the changing state.
3. **`CLAUDE.md` owner table.** Add the row: owner · root · what it owns · what it excludes · notes.
4. **`CLAUDE.md` remotes table.** For each git repository under the root: the remote to push, the
   remote never to push (an upstream), the branch, the writers, and the one committing agent.
5. **Nesting.** If the new root is inside another owner's root, add the exclusion to **both** agent
   files and to both table rows. If another root is inside the new one, do the same in reverse.
6. **External writers.** If anyone besides the owner writes the remote (a person, CI, a syncing
   editor), add that repository's pull-before-edit rule to the owner file (see `git-model.md`).

---

## Step 5 — Verify

1. Run `python3 scripts/check_setup.py <project dir>` and fix every error it reports.
2. Spawn the new owner with a trivial read-only task, e.g. *"Read your ONBOARDING.md and HANDOFF.md
   and summarize your root's state in five lines. Change nothing."* A sensible answer from a fresh
   spawn proves it onboards from its files alone.
3. Tell the user the owner is live, how to route work to it, and the launcher line that keeps its
   access in future sessions.

---

## Nested or overlapping roots

Prefer disjoint roots. When a sub-project must live inside another's tree (a document inside a code
repository, a dataset directory inside a simulator repository), register the inner one as its own
sub-project and write the exclusion into both owner files. If the two share a git index, their
owners never run in parallel on work that commits; see `git-model.md`.

## Removing or retiring an owner

Record the date and reason in the commit message, delete the agent file, remove its rows from both tables and its launcher line, and leave `ONBOARDING.md` and
`HANDOFF.md` in the root for whoever takes the work next.
