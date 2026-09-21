---
name: requesting-code-review
description: Review a completed change against its requirements and assess correctness, regressions, and test coverage; use a separate Codex reviewer when independent review is requested or materially useful.
---

# Requesting code review

Review the actual change against the requested behavior. Use a separate Codex subagent for
substantial independent review when available; this workflow requests that delegation. For a
small change or unavailable delegation, review locally and identify it as a local review.

1. Establish scope: requirements, modified paths, and base/head revisions if committed.
   For uncommitted work include staged and unstaged diffs and relevant untracked files;
   `HEAD~1..HEAD` alone may not contain the work.
2. Fill `code-reviewer.md` with the requirements and scope. Pass the filled prompt through
   the available subagent interface. Do not assume a `code-reviewer` agent type is installed.
3. Ask the reviewer to inspect files without editing, prioritize actionable bugs and test gaps,
   and return file/line evidence, impact, and verification limits.
4. Verify findings. Fix actual blockers, recheck affected behavior, and record remaining issues.
   Disagree with evidence when a proposed change is unnecessary or incorrect.

In `subagent-driven-development`, perform specification review before quality review. Preserve
that sequence when it is the selected workflow; do not impose multiple reviews on every typo.
A local review request does not authorize posting GitHub comments or publishing changes.
