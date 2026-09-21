---
name: finishing-a-development-branch
description: Finish verified development work by performing the requested merge, pull request, branch preservation, or cleanup. Use when branch integration or disposition is part of the user’s task.
---

# Finishing a development branch

Verify the relevant checks and inspect the diff before integration. Record existing unrelated
failures separately; do not claim they passed. Determine the target branch from repository
configuration or the user's instructions, not an assumed `main`.

Follow the integration choice already authorized. If none was requested, report the current
branch and reviewable changes; offer merge, PR, preservation, or discard only when a choice is
needed to finish the user's task. Do not repeatedly ask for an action already authorized.

## Local merge

Check the target worktree and uncommitted state. Fetch when needed and merge using the
repository's policy. Verify the integrated result before deleting the feature branch. Never
switch branches in a way that loses user changes. Keep a worktree that is still needed.

## Push and pull request

Stage only intended files and commit when authorized. Push to the intended remote/branch.
Use the available GitHub integration or `gh` as appropriate. With `gh`, write the exact PR body
to a temporary file and use `--body-file`; describe the final behavior and validation. Prefer
a draft unless the user or repository workflow requests otherwise. Preserve the branch and
worktree for review revisions.

## Preserve or discard

For preservation, report branch, worktree, and uncommitted work. Do not clean them up.
For discard, show exactly which commits/files/worktree would be removed and obtain missing
explicit authorization. Never discard unrelated work or interpret a request for review as
permission to delete. Use Git worktree management rather than recursively removing directories.

Clean up a temporary worktree only after a completed merge or authorized discard and only when
it contains no needed changes/jobs. A PR alone is not a reason to remove its worktree.
