---
name: verification-before-completion
description: Verify relevant outputs before claiming a change, build, test, or research result is complete. Use when preparing completion reports or assessing delegated work.
---

# Verification before completion

Match every completion claim to evidence from the final state of the work.

1. Identify what would demonstrate the requested behavior: a test, build, inspection,
   measured output, or artifact check appropriate to the change.
2. Run the relevant check and inspect its exit status and substantive output. A launched
   process is not a successful build; an existing file may be a stale artifact.
3. Compare the evidence to the acceptance criteria. Distinguish passed, failed, and not run.
4. Inspect delegated changes and evidence rather than accepting an agent's success summary.
5. Report what changed, what was verified, and any remaining limitations.

Reuse valid checks on unchanged state. Repeat when subsequent edits, failures, or unresolved
concerns invalidate the evidence; do not rerun an expensive FPGA build merely to repeat a
status message. Do not add tests that only mirror a trivial edit.

| Claim | Required evidence |
|---|---|
| Tests pass | Relevant test result and exit status on final code |
| Build succeeds | Completed build, exit status, expected outputs |
| Bug fixed | Original failure no longer reproduces; useful regression coverage |
| Profiling result | Saved measurements, configuration, and tool provenance |
| Agent task complete | Actual diff/artifacts satisfy the task |
| Requirements met | Acceptance criteria checked, gaps stated |

A linter does not prove a build passes, and a synthetic fixture does not prove hardware works.
Do not claim an unrun check passed. Preserve existing work when reproducing a failure.
