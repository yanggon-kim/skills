# Git model — who writes what

Git is where parallel agents collide. These rules keep one project's history coherent when several
owners, the user, and outside tools all touch repositories.

## The remotes-and-writers table

`AGENTS.md` holds one row per repository:

| repository | remote to push | never push | branch | writers | committing agent |
|---|---|---|---|---|---|

- **remote to push** — often a personal fork (`myrepo`), not `origin`.
- **never push** — the upstream a fork was cloned from. A push there is public and irreversible.
- **writers** — every party that pushes: owners, the user, CI, an editor that syncs to git, another
  clone on another machine. Unlisted writers are how histories diverge.
- **committing agent** — exactly one agent commits and pushes this remote.

## Rules and their reasons

- **One committing agent per remote.** Two agents pushing one remote race and diverge. Others report
  the change they need.
- **Push only on the user's approval.** A task says "push", or the commit stays local. Batch pushes
  when several owners' commits go to one remote.
- **Never force-push; never rewrite pushed history.** Someone may already have fetched it. A wrong
  commit message stays.
- **Address repositories by absolute path: `git -C <abs path> …`.** An agent's working directory
  does not reliably persist between commands; a mis-aimed `cd` once turned a one-file commit into a
  275-file commit in the wrong repository.
- **Stage only your own paths: `git add <paths>`, never `git add -A` or `git add .`** in a repository
  another owner also writes.
- **Commit message:** a summary line, a body saying what changed and why, and any attribution trailers explicitly required by project policy. Do not invent trailers or hard-code a model name.

## A git index shared by several owners

When several owners' roots are directories of one repository (a document tree inside a code
repository, a data directory beside it):

1. The owners commit **sequentially**, never in parallel; main sets the order.
2. Each stages **only paths under its root**.
3. **One** owner — named in the table — pushes, once, after the others have committed.
4. A long-running job still writing into the tree is not staged; commit around it by path or wait.

## External writers

A repository the user or a tool also writes (an online editor syncing to git, CI committing
artifacts, the user's laptop):

1. **Before editing:** `git -C <repo> fetch`, check `HEAD..origin/<branch>`, `pull --rebase` if the
   other writer pushed, then **re-read** every file about to change.
2. **When a push is authorized, push after committing**, to shorten the window for a conflict. Otherwise leave the commit local and report it.
3. **A conflict involving the other writer's change is reported, not resolved.** The other writer's
   edit wins by default; show both sides and let the user decide.
4. The other writer's push may not reach git immediately (an editor syncs on demand). If "pull"
   finds nothing new, say so; do not guess at what they changed.

## Submodules

A submodule is its own repository with its own writer.

- Its owner commits and pushes inside it and reports the new hash.
- The **parent** repository's committing agent bumps the pointer: in the submodule `git fetch &&
  git checkout <hash>`; in the parent stage **only the gitlink**; commit "bump <submodule> to
  <hash> (<what changed>)". Pointer bumps are cheap to batch with the parent's next push.

## Sub-project files the agent system adds

`ONBOARDING.md` and `HANDOFF.md` describe the agent system, not the project. Keep them untracked by
default via the path returned by `git -C <repo> rev-parse --git-path info/exclude` (local only, never pushed; resolve relative output from the repository). Commit them only on the user's
request — useful for a private repository the user alone works in.
