---
name: main-agent-workspace
description: Set up, extend, or audit a Codex workspace with a coordinating main agent and an owner agent for each sub-project. Use for owner routing, onboarding an existing repository, adding a sub-project, or diagnosing owner scope and directory access.
---

# Main-agent workspace for Codex

The interactive parent coordinates; each registered sub-project has one owner. The parent
routes changes under an owner's root to that owner. Delegated owners follow their own task
and agent definition, not the parent's coordinator-only restriction. Keep ownership boundaries
explicit; they are workflow rules, not filesystem sandboxes.

This skill requests delegation for registered owners when the client exposes subagent tools.
If named custom agents are unavailable, read the owner's TOML definition and pass its
`developer_instructions` in the task brief to an available general-purpose subagent. If no
subagents exist, report that limitation and use a local ownership pass when the user permits it.

## Paths and prerequisites

Resolve `scripts/`, `assets/`, and `references/` relative to this skill's installed directory.
Run helpers by their full paths with the project directory as an argument. Do not write outputs
inside the installed skill. `check_setup.py` needs Python 3.11+, or Python 3.10 with `tomli`.

## Detect the state

Run `python3 <skill-dir>/scripts/inventory.py <project-dir>`. It reports Git repositories,
existing guidance, owner files, and nesting without writing files.

- Empty directory or codebase without owners: set up the base.
- Existing `AGENTS.md` owner table or `.codex/agents/` owner files: audit first.
- User names a root to add: follow `references/add-subproject.md` after checking the base.

## Set up the base

1. Create or merge `<project>/AGENTS.md` using `assets/AGENTS.md.tmpl`. Preserve existing
   instructions; keep the owner and remotes tables empty until a root is registered.
2. Create `<project>/scripts/start-main.sh` from `assets/start-main.sh.tmpl`, executable,
   with an empty `SUBPROJECTS` array. It runs `codex` and passes `--add-dir` for registered roots.
3. Report candidate sub-projects from the inventory; register only roots within the user's
   requested scope. Do not invent owners or add private memory files in Codex's internal storage.

Start with `scripts/start-main.sh`; resume with `scripts/start-main.sh resume --last` or
`resume <session-id>`. The launcher does not override global permissions or model settings.

## Add a sub-project

Follow `references/add-subproject.md`: verify access, survey into `ONBOARDING.md`, resolve
unknown scope/writers, create `.codex/agents/<name>-owner.toml`, seed `HANDOFF.md`, update the
registries, validate, and exercise a read-only owner task when spawning is available.

Custom agent files use `name`, `description`, and `developer_instructions`; optional
`model_reasoning_effort = "high"` sets effort. Omit `model` to inherit instead of writing
`model = "inherit"`. Preserve the user's model choices. Confirm custom-agent availability in
this client; restart a session if new definitions have not appeared.

## Audit and operation

Run `python3 <skill-dir>/scripts/check_setup.py <project-dir>`. It cross-checks `AGENTS.md`,
`.codex/agents/*.toml`, the launcher, and remotes; checks scope exclusions and required state
files; and reports unresolved placeholders and malformed agent definitions.

Read only the relevant reference:
- `references/operating-model.md`: routing, task briefs, agent lifecycle, resource ownership.
- `references/git-model.md`: shared indexes, remotes, external writers, commit/push scope.
- `references/context-layers.md`: persistent project facts and task state.

Respect prior authorization; do not repeatedly ask the user to approve already-specified
roots or routine setup. Pause for genuinely missing scope decisions and requested checkpoints.
