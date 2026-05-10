# PROGRESS — <workload-slug> (started <YYMMDD>)

This file is the source of truth for "what step are we on". The skill reads it on every invocation. Update via `scripts/update_progress.py <step> <status> [artifact_path] [note]`.

| step | title | status | artifact | note |
|------|-------|--------|----------|------|
| 1 | Target Workload Search | pending |  |  |
| 2 | Workload Analysis (augmented) | pending |  |  |
| 3 | Related Research Search | pending |  |  |
| 4 | Solution Brainstorming | pending |  |  |
| 5 | Simulation Setup | pending |  |  |
| 6A | Individual Implementations | pending |  |  |
| 6B | Orthogonal Combinations | pending |  |  |
| 6 | Solution Design (overall — set done after 6A and 6B both done) | pending |  |  |
| 7 | Evaluation | pending |  |  |
| 8 | Paper Writing | pending |  |  |

## Status legend

- **pending** — not started.
- **in-progress** — agent or user is actively working on this step.
- **blocked** — needs user input or external resolution (e.g. Step 5 missing-feature escalation).
- **done** — artifact produced, user has reviewed (or explicitly skipped review).

## Checkpoint convention

After each step is marked `done`, the skill stops and reports a summary back to the user. The user reviews the artifact, may edit it, then explicitly says to continue. Never run multiple steps in one invocation.

## Notes column

Free-text — typically a timestamp, but can hold short user-supplied directives ("user prefers OpenFHE over Microsoft SEAL") that the next step should respect.
