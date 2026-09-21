---
name: using-superpowers
description: Use when choosing among this collection’s development workflows or when the user asks how to use its skills.
---

# Using the development skills in Codex

Select skills by the task and the installed catalog descriptions. Read a relevant skill's
`SKILL.md` before following it; resolve its supporting files relative to that skill directory.
The directory name is not a plugin namespace. Explicit CLI/IDE invocation uses `$skill-name`.

- Unclear product behavior: `brainstorming` or `spec-specific-socratic`.
- Multi-step implementation: `writing-plans`, then `executing-plans`.
- Independent implementation/review tasks: `subagent-driven-development`.
- Independent investigations: `dispatching-parallel-agents`.
- Unexpected behavior: `systematic-debugging`; stubborn cross-platform bugs:
  `bug-investigation-with-hypothesis-round`.
- Before reporting completion: apply `verification-before-completion` when useful.

Use only relevant workflows. A small, clear task does not require the entire chain. Do not
load every skill at conversation start. User instructions and existing authorization take
precedence over a skill's default process. A request for analysis does not authorize edits.

Use the actual tools exposed by the current Codex client. Planning can use its plan tool
or a Markdown checklist. Delegation uses its subagent interface when available, with bounded
tasks, explicit paths, and a report contract. If unavailable, perform the work sequentially
and state the limitation; do not claim independent review occurred.
