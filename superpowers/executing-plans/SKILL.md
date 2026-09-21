---
name: executing-plans
description: Execute a written implementation plan, track progress, verify each meaningful change, and honor any user-requested review checkpoints.
---

# Executing plans

1. Read the plan, applicable project instructions, and current repository state. Check that the
   plan still matches the user's latest request. Resolve material gaps before dependent work.
2. Track tasks using the available planning tool or a checklist in the plan document. Reuse
   an existing suitable branch/worktree; create isolation only when needed.
3. Implement in dependency order. Validate each meaningful behavior before building on it.
   Use exact test output, not expectations, to record passed/failed/not-run status.
4. Investigate failures within scope. Continue independent work while a clarification is
   pending. Ask only when blocked on a consequential choice or missing access/information.
5. Report progress at useful milestones. Pause at checkpoints the user requested, otherwise
   continue through the authorized plan rather than stopping every three tasks.
6. Inspect the final diff and run the appropriate final checks. Report changes, evidence,
   limitations, and remaining work. Use `finishing-a-development-branch` if integration is
   part of the request; do not create an unsolicited merge/push workflow.

Read `HANDOFF.md` or the plan's progress section after a restart. Record completed work and
remaining tasks before handing off. A launch of a background build is not a completed build.

For independent work, the user or an applicable skill can request delegation. Use
`subagent-driven-development` when its implementation/review loop suits the plan; otherwise
execute locally. Never invent a missing tool or claim a review you did not perform.
