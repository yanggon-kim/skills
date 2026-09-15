# Context layers — what goes where

Agents load context in layers. Put each kind of content in the one layer where it is read at the
right moment, and nowhere else. Duplicated rules drift apart; overloaded always-loaded files cost
every session context it does not need.

## The layers

| layer | holds | read by | when |
|---|---|---|---|
| this skill | the generic rules, templates, procedure, scripts | main and owners | on demand |
| `<project>/CLAUDE.md` | main's role, the owner table, the remotes-and-writers table, the resource cap, project-wide decisions | main | every session |
| `.claude/agents/<name>-owner.md` | one owner's identity, scope and exclusions, on-start, rules unique to its root, when-done | that owner | at spawn |
| `<root>/ONBOARDING.md` | **stable facts**: what the root is, layout, commands, git and writers, existing guidance, traps | that owner | at spawn |
| `<root>/HANDOFF.md` | **changing state**: status, key numbers with sources, recent decisions, open issues, next steps, interfaces | that owner; main for detail | at spawn; when main needs detail |
| owner agent memory | lessons and gotchas learned in that root | that owner | at spawn |
| main's memory | why decisions were taken; the user's standing preferences | main | every session |
| `*.history.md` archives | superseded or dated material moved out of a live file | nobody automatically | only when someone looks |

Rules of thumb:
- A rule that applies to every project → this skill. A fact about this project → the project.
- A fact that stays true → `ONBOARDING.md`. A fact that will change next week → `HANDOFF.md`.
- *What* was decided → `HANDOFF.md` or `CLAUDE.md`. *Why* it was decided → memory.
- The project's own existing docs (README, a pre-existing `CLAUDE.md` in the sub-project) are
  pointed at from `ONBOARDING.md`, never restated.

## Size budgets

| file | budget | when it grows past it |
|---|---|---|
| project `CLAUDE.md` | ≤ 80 lines | move reference detail to `ONBOARDING.md` files or this skill; history to `CLAUDE.history.md` |
| owner agent file | ≤ 50 lines | the extra is usually state (→ `HANDOFF.md`) or stable facts (→ `ONBOARDING.md`) |
| `HANDOFF.md` "Recent decisions" | newest ~10 entries | older entries → `HANDOFF.history.md` |
| `HANDOFF.md` "Key numbers" | one block, the current one | superseded blocks → `HANDOFF.history.md` with their label |

## Archives

- Name: `CLAUDE.history.md`, `HANDOFF.history.md`, `<file>.history.md` beside the live file; the agent
  directory shares one `.claude/agents/_HISTORY.md`.
- An archive opens with one line saying what it is and where the live file is, then entries oldest
  first.
- **Move, never delete.** Every number or decision that leaves a live file must be findable in
  exactly one other place.
- Archives are inert: no agent loads them unless it is looking for history.

## Writing live files

- No dates inside live rules; a rule carries its reason, not its birthday. Dates belong in decisions
  and archives.
- No hard-coded model names or session URLs; say "the attribution the harness provides".
- No logs in `HANDOFF.md`; it is state. The commit message is the change record.
- When a pending item resolves, close it in the same pass — a stale "pending" misleads the next spawn.
