---
name: writing-plans
description: Write an actionable implementation plan for a multi-step change with known requirements. Use for planning requests or changes that need an explicit dependency and verification sequence.
---

# Writing implementation plans

Read the relevant project instructions and existing code, then write a plan scaled to the
change. Resolve consequential unknowns; do not ask again about decisions already supplied.

A useful plan states:
- Goal, non-goals, constraints, and any unresolved decisions.
- Architecture and the existing interfaces the change affects.
- Ordered tasks, concrete file paths, dependencies, and acceptance criteria.
- Verification commands and expected behavior; record hardware or tool limitations.

Use `docs/plans/YYYY-MM-DD-<feature>.md` unless the user or repository specifies another path.
Do not create a worktree merely to write a plan. Use `using-git-worktrees` when isolation is
needed for implementation and the current workspace does not already provide it.

Example plan header:

```markdown
# Feature implementation plan

For Codex: follow the installed `executing-plans` skill for execution when relevant.

Goal: ...
Architecture: ...
Constraints: ...

## Task 1: ...
Files: ...
Change: ...
Verify: command and observable expected behavior
```

Make tasks independently verifiable where possible. Include code only when it resolves a
specific ambiguity; avoid prescribing every keystroke or a commit for every small action.
Use `test-driven-development` for behavior changes where a regression test is useful.

If the user requested planning only, return the plan without implementation. If implementation
is already authorized and no material decision is missing, continue using the plan. Record
explicit user checkpoints and honor them; do not invent a new approval gate at every task.
