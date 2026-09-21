---
name: writing-skills
description: Create, update, or validate reusable Codex skills, including their triggers, supporting resources, and realistic workflow checks.
---

# Writing Codex skills

Use the installed `skill-creator` skill when available; these notes cover maintaining this
collection. A skill teaches useful task-specific decisions and workflows, not a replacement
for user intent or the host's tool and permission contracts.

## Authoring

- Use a directory with `SKILL.md`, YAML `name` and `description`, and only the supporting
  scripts, references, assets, or templates that the workflow needs.
- Use lowercase hyphenated names of at most 64 characters. Keep descriptions concise, within
  1,024 characters, with a clear capability, trigger, and any meaningful scope boundary.
- Preserve supported metadata such as `metadata` and `license`. Do not claim only two fields
  are allowed or treat skill metadata as a way to grant runtime permissions.
- Resolve supporting files relative to the loaded skill, and write artifacts to the user's
  project. Keep scripts' working-directory assumptions explicit.
- Use available Codex tools by capability. Do not assume an agent tool, memory service,
  plugin, or reviewer type exists. Define a local fallback when it is useful.
- Keep procedural detail in references only when it is conditional or substantial. Load it
  when relevant. Avoid repeated authority language and blanket rules for unrelated tasks.
- User instructions and existing authorization take precedence over default workflow gates.

## Discovery and distribution

Codex CLI/IDE users can invoke `$skill-name`; matching descriptions also support automatic
selection. Install local project skills in `.agents/skills/` or user skills in
`~/.agents/skills/`. This collection's `scripts/install_codex.py` creates symlinks to each
skill. Do not publish, push, or install globally unless within the requested scope.

`agents/openai.yaml` is optional UI/dependency metadata. It is not a subagent definition;
custom agents use TOML under `.codex/agents/` or `~/.codex/agents/`.

## Validation

1. Check frontmatter, unique names, local links, and script paths. Use the installed
   `skill-creator/scripts/quick_validate.py` when available, plus this collection's validator.
2. Exercise changed scripts in temporary workspaces, including an actual success path and a
   meaningful failure path. Use assertions about results, not copies of implementation text.
3. Check realistic prompts for correct triggering, needed context, output paths, and completion.
   For complex delegation workflows, an independent behavioral evaluation may be useful when
   available and authorized; see `testing-skills-with-subagents.md`.
4. Fix demonstrated issues and report what was and was not exercised. Do not delete existing
   work merely because a test was written after it.

For behavioral test examples see `examples/AGENTS_MD_TESTING.md`. For diagrams only when they
help explain a decision, use `graphviz-conventions.dot` and `render-graphs.js`.

Official references:
- https://learn.chatgpt.com/docs/build-skills
- https://learn.chatgpt.com/docs/agent-configuration/agents-md
- https://learn.chatgpt.com/docs/agent-configuration/subagents
