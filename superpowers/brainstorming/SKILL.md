---
name: brainstorming
description: Clarify an underspecified feature or design and compare meaningful approaches before implementation. Use when the user requests ideation or consequential design choices remain unresolved.
---

# Brainstorming ideas into designs

Read the project context and relevant instructions first. Use the user's existing constraints
and decisions rather than asking for them again. A clear small change does not need a design
interview.

Ask concise questions about genuinely missing requirements, with code/project context and
why the answer changes the design. Prefer one focused question at a time; use the available
question interface when appropriate. Continue independent investigation while waiting.

For a consequential design choice, present plausible approaches, their tradeoffs, and a
recommendation. Describe the selected design's interfaces, data flow, failure behavior, and
verification. Do not force a fixed number of options when the evidence supports one.

Record a substantial design in `docs/plans/YYYY-MM-DD-<topic>-design.md` or the user's chosen
location. Keep unverified assumptions explicit. If design-only was requested, stop at the
design. If implementation is already authorized, continue once material decisions are resolved.
Use `writing-plans` for complex implementation and `using-git-worktrees` when isolation helps.
Commit or publish the design only within the authorized scope.
