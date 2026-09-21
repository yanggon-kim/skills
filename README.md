# Codex skills

The `codex` branch ports this collection to Codex. `main` retains the Claude Code
version. There are 24 installable skills: research, GPU/FPGA, paper writing,
workspace ownership, requirements, and development workflows.

## Install for a project

Use Python 3.10+ with the dependencies in `requirements-codex.txt` (prefer a venv):

```bash
python3 -m pip install -r requirements-codex.txt
python3 scripts/validate_codex.py
python3 scripts/install_codex.py --project /absolute/path/to/project --dry-run
python3 scripts/install_codex.py --project /absolute/path/to/project
```

This creates individual symlinks in `<project>/.agents/skills/`, including the
skills under `superpowers/` and `doc/00_reference/`. It refuses to overwrite
existing skills and can be rerun safely. All skills, including the research
pipeline's `workload-analysis` dependency, are installed together. To make the
collection available across projects, explicitly use `--user` instead of
`--project`; that installs into `~/.agents/skills/`.

Links follow this checkout's working files. Keep it on the `codex` branch; use
a separate clone/worktree for simultaneous Claude and Codex versions. Links are
relative to the installation directory and are local setup, not portable vendored
copies; do not commit them into another repository without an intentional layout.
To uninstall, remove only the links pointing to this checkout, leaving other
skills and the source repository intact.

Start Codex in the installed project and use `/skills` or invoke a skill such as
`$workload-analysis`, `$gpu-research-automation`, or `$main-agent-workspace`.
Restart if the catalog has not refreshed. Task descriptions also support automatic
skill selection. A skill's supporting resources are resolved from its installed
path; experiment outputs belong in the user's working project.

## What changed

- Codex tools and delegation replace Claude-specific tool calls and plugin namespaces.
- Workspace generation uses `AGENTS.md`, `.codex/agents/*.toml`, and `codex resume`.
- Owners use explicit `ONBOARDING.md`/`HANDOFF.md` state rather than assumed private memory.
- `gpu_research_automation` is now `gpu-research-automation`; its duplicate profiling
  skill was consolidated into the standalone `workload-analysis` directory.
- Existing authorization carries across workflow steps. Explicit review checkpoints
  and material unresolved choices still require user input.
- Long jobs require completion tracking; a launch alone does not complete the task.
- The historical Claude settings and authoring reference are in `doc/legacy/`.

Permissions belong to Codex configuration, not these skills. Installation does not
change `~/.codex/config.toml`, command rules, model settings, or plugin connections.
The Claude `enabledPlugins` settings do not install Codex plugins. The directory
`superpowers/` here contains standalone skills, not a registered plugin.

## Validate

```bash
python3 scripts/validate_codex.py
python3 -B -m unittest discover -s tests -v
```

Tests use temporary projects and a mock launcher executable. They check installation,
owner registration, invalid TOML, nested scopes, and start/resume argument handling.
They do not run GPU profiling, FPGA synthesis, or paper experiments.

Official references: [skills](https://learn.chatgpt.com/docs/build-skills),
[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), and
[custom agents](https://learn.chatgpt.com/docs/agent-configuration/subagents).
