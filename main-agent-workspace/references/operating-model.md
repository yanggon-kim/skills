# Operating model — how main and the owners work

The rules below are the ones that proved necessary in practice. Each carries the reason, because an
agent that knows why a rule exists applies it sensibly to a case the rule did not foresee.

## Roles

**Main agent.** The session the user talks to. It routes each request to the owner whose root the
work lives in, writes the task brief, takes the owner's report, reads the owner's `HANDOFF.md` only
when it needs detail, and relays the result. It forwards every "for `<owner>`:" item as a new task.
Main edits only outside registered roots (the project's own `CLAUDE.md`, launcher and agent files).

**Owner subagent.** One per sub-project, defined by `.claude/agents/<name>-owner.md`. It is the only
agent that edits files under its root. It starts from its `ONBOARDING.md`, `HANDOFF.md` and agent
memory, does one task, updates those files, and reports.

**The user.** Decides scope, approves pushes, and chooses each owner's model. Owners never assume
approval that main has not relayed from the user.

## The rules

1. **Main never edits inside a registered root — not even one line.**
   A one-line fix by main is exactly how contexts start to mix; the owner then finds its root
   changed by someone who did not update its `HANDOFF.md`.

2. **One task = one fresh spawn.**
   A task notification carries the instance's *original* spawn description, so an owner resumed for
   a second task reports under the first task's name for as long as it lives. Owners rebuild cheaply
   from `ONBOARDING.md` + `HANDOFF.md` + memory. Never run two instances of the same owner at once.
   *Exception:* continuing the *same* task (answering its question, giving it a result it waited
   for) is a resume, not a new spawn.

3. **Read across, edit within.**
   Any owner may read any sub-project. It edits only its root. A change another root needs is
   written into the report as "for `<owner>`: …", and main routes it.

4. **The brief is complete; the report is short.**
   The spawn prompt carries everything the owner needs: the goal, the paths, what to read first,
   what not to touch, what "done" means, and the report shape. The report is ≤ 15 lines: what
   changed, files, commits and pushes, blockers, "for `<owner>`:" items. Detail belongs in
   `HANDOFF.md`, which main opens only when it needs it — this keeps main's context for coordination.

5. **Owners of one shared git index commit sequentially, staging only their own paths.**
   A blanket `git add` sweeps another owner's files into the wrong commit. See `git-model.md`.

6. **One writer per git remote.**
   Two agents pushing the same remote produce diverging histories. Name the writer in the remotes
   table; everyone else reports.

7. **Pushes happen only on the user's approval; never force-push.**
   A push publishes; a force-push destroys history someone else may already have.

8. **Background jobs: start, note, hand back — do not poll.**
   An owner that loops "check progress, report, sleep" wakes main every few minutes with no new
   information. Start the job with a log under the root, write its state and restart command into
   `HANDOFF.md`, report, and end the turn; main watches the job (or the user tells main when it is
   done) and spawns or resumes the owner to collect the result.

9. **Write partial state early.**
   An owner can be stopped at any moment. Aggregated results that exist only in its context are lost
   when it is; a line in `HANDOFF.md` ("sweep complete, results at X, not yet aggregated") is not.

10. **Share machine resources explicitly.**
    Parallel owners each assume the machine is theirs. `CLAUDE.md` states one cap (cores, GPUs,
    memory) across *all* owners; a job that needs more is proposed with its finish-time trade-off.

11. **No settings or UI changes on a hypothesis.**
    A complaint about the terminal or the environment gets a proposal the user can test, not an edit
    to settings or the launcher based on a guess.

12. **Models per owner are the user's choice.**
    Each agent file sets `model` and `effort`; they change only on the user's instruction, because
    the user balances cost against what that owner usually does.

## Routing a request

1. Find the root the work lives in. If it spans two roots, split it: one task per owner, in the order
   the dependency requires (the owner that produces data before the owner that writes about it).
2. Owners of *disjoint* repositories may run in parallel. Owners that share a git index run one after
   another.
3. A question main can answer from a report or `HANDOFF.md` it already has needs no spawn.
4. If no owner fits, the work is either outside every root (main may do it) or a sign that a
   sub-project is missing — say so and offer to add it.

## The spawn brief

Give every owner the same shape, so nothing is left to inference:

- **Goal** — what the user asked for, in their words where it matters.
- **Context** — decisions already taken that the owner must not reopen; relevant results from other
  owners, quoted rather than summarized when a number is involved.
- **Paths** — the files to read first and the files expected to change.
- **Boundaries** — what not to touch; whether to commit, and whether to push (default: commit, do not
  push, unless the user said push).
- **Stop conditions** — when to stop and report instead of improvising (a failed check, a conflict
  with someone else's edit, a result outside the expected range).
- **Report shape** — the fields wanted, ≤ 15 lines.

## Known limits of the model

- **Owners cannot spawn owners.** Every cross-owner step routes through main, so a chain of three
  owners is three round trips. Plan the order up front.
- **A subagent reaches only the directories its parent session can.** A root outside the main
  directory must be added (`/add-dir`, or the launcher) before its owner is spawned.
- **Notifications are noisy when owners poll** — rule 8 exists for this.
- **A stopped owner leaves no summary** — rule 9 exists for this.
