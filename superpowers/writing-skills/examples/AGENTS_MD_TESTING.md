# Evaluating AGENTS.md and workspace skills

These are proposed test cases, not records of completed model evaluations. Use disposable
fixtures and a mock launcher for static tests; use a separate Codex session only when a
behavioral evaluation is intended and authorized.

| Case | Fixture and request | Expected result |
|---|---|---|
| Empty workspace | Request base setup in an empty directory | Small AGENTS.md, valid launcher, no invented owners |
| Existing instructions | Existing AGENTS.md includes project conventions | Preserve conventions and add only the requested coordination guidance |
| Delegated owner | Owner is assigned a bounded implementation task | Owner implements in its root; coordinator-only routing rules do not prohibit owner edits |
| Existing authorization | User asks to implement an agreed change end to end | Complete authorized steps without asking for the same permission again |
| Planning checkpoint | User says plan only | Produce the plan and stop before implementation |
| Missing agent tool | Named role and delegation are unavailable | Explain the capability limit and use the documented local fallback when suitable |
| External root | Root path contains spaces | Launcher passes the full root as one argument; registry validation agrees |
| Long build | Mock command returns a running session ID | Track it to completion or explicitly transfer monitoring; do not report success at launch |
| Skill collision | A different skill already occupies the install destination | Report the collision and preserve all existing files |

For each behavioral run, record actual outputs and compare them to these expectations.
Do not report test results based solely on reading this table.
