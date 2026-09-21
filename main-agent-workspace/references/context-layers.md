# Context layers

| File | Purpose | Reader |
|---|---|---|
| Installed skill and references | Reusable workflow | Main and owners, on demand |
| Project `AGENTS.md` | Role distinction, owner/remote registries, resource cap | Applicable sessions |
| `.codex/agents/<owner>.toml` | Owner identity, instructions, model choice if explicit | Spawned owner |
| `<root>/ONBOARDING.md` | Stable layout, commands, interfaces, writers | Owner at task start |
| `<root>/HANDOFF.md` | Current state, evidence, jobs, next steps | Owner; main as needed |
| `<root>/HANDOFF.history.md` | Superseded decisions/results | On demand |

Do not assume Claude-style private per-owner memory. Store reusable project facts in
ONBOARDING.md and decisions/gotchas in HANDOFF.md or its archive, with the user's preferred
tracking policy. Codex-managed memories may exist, but do not read or modify its internal
memory databases as a prerequisite of this skill.

Codex loads AGENTS.md through its instruction hierarchy. Owner instructions must distinguish
an assigned implementing owner from the coordinating parent; do not apply the parent's
"delegate instead of editing" instruction to all descendants. Explicitly load guidance for
external assigned roots when it was not part of the inherited context.

Suggested budgets: AGENTS.md ~80 lines, agent instructions ~50 lines, roughly ten recent
HANDOFF decisions. These are maintainability warnings, not arbitrary blockers. Keep raw logs
in files linked from HANDOFF.md. Archive old evidence instead of silently deleting it.
Keep archives outside auto-discovered agent directories.
