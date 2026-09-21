---
name: subagent-driven-development
description: Execute a multi-task implementation plan with separate implementer, specification reviewer, and quality reviewer agents in the current Codex session.
---

# Subagent-driven development

This workflow requests delegation for substantial, bounded implementation tasks. Use the
Codex subagent tools exposed in the current session; their names and schemas vary by client.
Preserve the parent's model unless the user or applicable instructions specify an override.

## Per-task cycle

1. Read the plan and extract the task requirements, paths, dependencies, and acceptance criteria.
2. Fill `implementer-prompt.md` and spawn an implementer with a self-contained task message.
   Define its editable paths, shared-resource limits, and whether commits are authorized.
3. Answer questions using known context; ask the user only about unresolved material choices.
4. Inspect the actual changes and test evidence. Give `spec-reviewer-prompt.md` plus the task
   requirements to a separate reviewer. Reviewers inspect code; they do not edit it.
5. Resolve specification findings, then dispatch the quality review using
   `code-quality-reviewer-prompt.md` and the installed `requesting-code-review` template.
6. Route actionable findings back to the implementer and verify the fixes. Mark the task done
   only after both reviews pass or explicitly report any unresolved limitation.
7. Continue with the next task. At the end, verify the integrated result against the plan.

Use a fresh agent for an independent new task; continue the same agent for corrections to its
current task. Do not assume a new agent has prior conversation or persistent private memory.
Pass the required context or explicit files to read. Track agent identifiers for follow-ups
and wait for actual completion before consuming dependent results.

Do not run implementers concurrently in overlapping files or a shared Git index. Serialize
GPU/FPGA measurements on a shared device. Parallel review/read-only investigations can run
when their results are independent. Respect the host's available concurrency slots.

If subagents are unavailable, use a local implementation/specification/quality pass in order
and disclose that these are not independent agent reviews. Continue useful authorized work.

Use `using-git-worktrees` when isolation is needed, `writing-plans` for plan structure,
`test-driven-development` for meaningful behavior tests, and `finishing-a-development-branch`
when the user requested integration. These are installed skill names, not agent types.
