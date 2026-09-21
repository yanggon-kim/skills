---
name: dispatching-parallel-agents
description: Delegate independent investigations or tasks to parallel Codex agents when they can proceed without overlapping writes, shared-resource contention, or sequential dependencies.
---

# Dispatching parallel agents

This workflow requests subagents for independent work where parallel investigation improves
turnaround. Identify concrete bounded tasks before spawning; keep useful coordination or
integration work for the main agent.

1. Group the work by independent problem domain. Related failures may need one investigation.
2. Give each agent the goal, evidence, absolute paths, allowed edits, acceptance criteria,
   resource limits, and expected report. Use the available Codex subagent tool, not shell
   pseudocode or an assumed plugin-specific agent type.
3. Track returned agent identifiers. Send answers and follow-ups through the exposed messaging
   tools. Reuse an agent for its current task and start a fresh one for unrelated work.
4. Wait for the results needed by integration; inspect changes and reconcile overlapping claims.
5. Run the appropriate integrated verification and report both results and remaining uncertainty.

Example tasks:
- Investigate three failures in one test file; explain the cause and propose a patch.
- Trace a separate subsystem's batch-completion behavior; change only its assigned files.
- Review the resulting patch for a specific regression without editing anything.

Do not parallelize edits to the same files, commits to a shared index, or performance runs on
one GPU/FPGA. Use isolated worktrees or non-overlapping ownership when parallel writes are
necessary. Bound concurrency to the current host's slots and the user's resource limits.
If agents are unavailable, execute the tasks sequentially and disclose the change in method.
