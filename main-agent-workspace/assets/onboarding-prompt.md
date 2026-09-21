# Onboarding survey prompt

Give this prompt, with `<ROOT>` replaced by the absolute path, either to a Codex session opened in
the project (preferred when the project has its own `AGENTS.md`, memory or history) or to a
survey agent spawned by main. It may write only ONBOARDING.md. If its sandbox is read-only, return the document text for main to save.

---

Inspect the project at `<ROOT>` without modifying its source and write `<ROOT>/ONBOARDING.md`, so that a new agent can
take ownership of this project without any other context. Do not modify, create, delete, build or
commit anything else. Cite file paths as evidence for every claim; where you infer rather than read,
say so.

Write these sections:

1. **Identity** — what the project is for, in two or three sentences, and what it is not for.
2. **Layout** — top-level directories and what each holds. Flag generated output, large data, and
   vendored or third-party trees that must not be read wholesale or edited.
3. **Build, test, run** — the exact commands, the directory each runs from, what each needs
   (toolchain, environment, hardware), and roughly how long each takes. Mark commands you could not
   confirm from the files.
4. **Git** — every repository under `<ROOT>` (including nested repositories and submodules): its
   remotes, which remote is a personal fork and which is an upstream that must never be pushed, the
   branch in use, uncommitted changes, and **every writer** of each remote you can find evidence for
   (the user, CI, an editor that syncs to git, other clones).
5. **Existing guidance** — `AGENTS.md`, READMEs, design docs, contribution guides, memory: list each
   with one line on what it covers. Point at them; do not restate them.
6. **Conventions and traps** — naming rules, provenance rules for results, things that break
   silently, slow or expensive operations, anything a newcomer would get wrong.
7. **Current state** — work in progress, recent activity, open issues, uncommitted or unpushed work.
8. **Proposed owner scope** — what an owner of this root should own; what it must exclude (nested
   roots, shared data, generated trees); which paths outside `<ROOT>` it will need to read; whether
   it shares a git repository with anything else.
9. **Open questions** — what you could not determine from the files and a human must answer.

Keep it factual and dense; no preamble. When the file is written, report its path and the open
questions in no more than ten lines.

---

After the survey, main keeps `ONBOARDING.md` out of the project's git by default by adding it (and
`HANDOFF.md`) to `<repo>/.git/info/exclude`, unless the user asks to commit them.
