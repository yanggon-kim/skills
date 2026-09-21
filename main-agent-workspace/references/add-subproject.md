# Add a sub-project

Use the scope already supplied by the user. Ask only for consequential unknowns, such as
which root to own, excluded nested repositories, remote writers, or a model preference.
Choose a lowercase hyphenated name; its owner is `<name>-owner`.

## 1. Verify access

Read a file in the proposed root. Register the absolute root in the launcher's `SUBPROJECTS`
array. For workspace-limited sessions, `codex --add-dir <root>` adds a writable directory at
launch; use the client's exposed permission control for a running session, or restart through
the launcher. Do not instruct the user to run a Claude-only slash command. Full-access sessions
already have filesystem access subject to OS/host policy; adding a launcher entry is a registry
update and is not a reason to request the same permission again. Access does not automatically
load another project's instructions: explicitly read applicable guidance for the assigned root.

## 2. Survey

Use `assets/onboarding-prompt.md` to survey the root into `<root>/ONBOARDING.md`. Prefer the
available Codex subagent interface with the supplied prompt and evidence paths. A read-only
reviewer can return the document text for the parent to save; do not ask a sandboxed read-only
agent to write a file. If no subagents are available, main may perform this initial survey.
A separate user session is optional when it has context unavailable in project files.

Preserve existing guidance, including legacy CLAUDE.md where relevant as background. For Codex,
AGENTS.md and the current user's instructions govern the workflow. Never assume history or
private agent memory was transferred automatically.

Keep `ONBOARDING.md` and `HANDOFF.md` untracked by default, unless the user requests versioned
state. Resolve the exclude file with `git -C <root> rev-parse --git-path info/exclude` rather
than assuming `.git` is a directory; worktrees and submodules can use a `.git` pointer file.

## 3. Resolve scope

Summarize ownership, exclusions, shared Git indexes, remote writers, resource caps, and open
questions. Use choices already authorized. Obtain missing material decisions before registering
an ambiguous owner; do not require a redundant approval for a fully specified onboarding task.

## 4. Register

- Fill `assets/owner.toml.tmpl` into `.codex/agents/<name>-owner.toml`. Escape TOML string values
  correctly (especially quotes and Windows paths), and validate the rendered file. Leave model
  unset to inherit unless the user specifies one. `memory: project` is not part of this format.
- Seed `HANDOFF.md` from its template with current state, running jobs, and next steps.
- Add the owner/root/exclusions row to `AGENTS.md` and each repository's remotes/writers row.
- Add nested-root exclusions to the outer owner's instructions and registry. Avoid parallel
  writers sharing one Git index. Add the external-writers protocol when applicable.
- Confirm the current client sees the definition; restart if necessary. Do not promise hot
  reload timing. When named roles are unavailable, pass the TOML instructions to a regular
  Codex subagent explicitly and identify it by the owner name in the task brief.

## 5. Verify

Run `<skill-dir>/scripts/check_setup.py <project-dir>`. Resolve reported setup errors, then
spawn a read-only owner task: read the guidance, ONBOARDING.md, and HANDOFF.md, and summarize
scope and current state without changes. If spawning is unavailable, report that the registry
was validated but the live owner check was not run.

To retire an owner, archive its instructions outside `.codex/agents/` (so they cannot be
loaded as a live role), remove its definition/registry/launcher entries, and preserve state
files for its successor. Do this only within the user's requested scope.
