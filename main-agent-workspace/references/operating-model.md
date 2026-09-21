# Operating model

## Roles and routing

The interactive parent coordinates registered owners. An owner implements within its assigned
root, reads other roots as permitted, and reports changes needed elsewhere. The parent can
answer from existing evidence without spawning; changes under a registered root go to its owner.
Do not run two writers for one root. Scope is an instruction boundary, not a technical sandbox.

This workflow requests delegation using the current Codex subagent interface. Supply the
owner's TOML instructions when a named role cannot be selected. If no delegation is available,
report that limitation before claiming the owner system is operational; local work can continue
within whatever scope the user authorizes.

## Task brief and agent lifecycle

Pass the goal, absolute root, initial files to read, existing decisions, editable/excluded paths,
resource limits, acceptance criteria, Git permissions, and report format. A new owner does not
need the entire conversation if ONBOARDING.md and HANDOFF.md contain the required facts.
Use a fresh spawn for an independent task; follow up with the existing agent for corrections or
answers in its current task. Track agent IDs; do not rely on assumptions about notification text,
hot reload, or private memory. Report about 15 lines with evidence paths and unresolved issues.

Serialize commits to a shared Git index and profiling on a shared device. Independent read-only
investigations may run concurrently within the host's slot and machine-resource limits. Cross-owner
work returns to main for ordering and routing; this is an ownership policy, not a claim that
Codex agents cannot technically spawn other agents.

## Long-running work

Use the execution tool's persistent sessions for ongoing commands; record the session/job ID,
log, working directory, configuration, and expected completion artifact. When work must survive
a session exit, use a suitable persistent runner such as tmux with durable logs and an exit-status
file. Plain `command &` is not a guarantee that a job survives the tool or shell lifetime.

An owner may hand monitoring to main explicitly. Main continues with useful independent work,
then checks progress at reasonable intervals, collects the exit status and artifacts, and routes
follow-up work. Keep user updates meaningful. End before completion only when the user requests
launch-only work, a checkpoint is reached, or a real blocker requires input. Never label a running
build or an unverified artifact as finished.

## State and authorization

Write partial results early to HANDOFF.md. Preserve provenance of numbers and links to logs.
Use existing user authorization without asking again for routine steps. Ask for material unknowns,
changes outside scope, and unapproved external actions; follow the host's runtime permission policy.
Owners commit or push only if their task brief authorizes it. Read `git-model.md` for shared indexes
and other writers. Models inherit by default; change model choices only on the user's instruction.
