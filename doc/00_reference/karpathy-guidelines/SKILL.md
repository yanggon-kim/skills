---
name: karpathy-guidelines
description: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code. Enforces simplicity, surgical changes, explicit assumptions, and verifiable success criteria. Use when user says "write code", "fix bug", "refactor", "add feature", "review code", or any implementation task. Do NOT use for research questions, documentation-only tasks, or non-code conversations.
license: MIT
metadata:
  version: 2.0.0
  author: forrestchang
  source: https://x.com/karpathy/status/2015883857489522876
---

# Karpathy Guidelines

Behavioral guidelines derived from Andrej Karpathy's observations on LLM coding pitfalls. Bias toward caution over speed. For trivial tasks, use judgment.

## Critical Rules

- NEVER add features beyond what was asked
- NEVER refactor code that isn't part of the current task
- NEVER hide confusion -- surface it immediately
- ALWAYS state assumptions before implementing
- ALWAYS define verifiable success criteria before writing code
- ALWAYS trace every changed line back to the user's request

## Instructions

### Step 1: Think Before Coding

Before implementing anything:

1. State your assumptions explicitly. If uncertain, ask.
2. If multiple interpretations exist, present them -- don't pick silently.
3. If a simpler approach exists, say so. Push back when warranted.
4. If something is unclear, stop. Name what's confusing. Ask.

```
# Good
"I'm assuming you want validation on the API input layer, not the DB layer.
The request field 'email' -- should I validate format, or just presence?
Two approaches: regex vs. library. I'd suggest the library (less error-prone)."

# Bad
*silently picks an interpretation and starts coding*
```

### Step 2: Simplicity First

Minimum code that solves the problem. Nothing speculative.

- No abstractions for single-use code
- No "flexibility" or "configurability" that wasn't requested
- No error handling for impossible scenarios
- If you write 200 lines and it could be 50, rewrite it

```
# Good: direct solution
def get_user(user_id):
    return db.query(User).get(user_id)

# Bad: premature abstraction nobody asked for
class UserRepository:
    def __init__(self, session_factory, cache_backend=None):
        self._session = session_factory()
        self._cache = cache_backend or NullCache()
    def get(self, user_id, use_cache=True):
        ...
```

Self-check: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Step 3: Surgical Changes

Touch only what you must. Clean up only your own mess.

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting
- Don't refactor things that aren't broken
- Match existing style, even if you'd do it differently
- If you notice unrelated dead code, mention it -- don't delete it

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused
- Don't remove pre-existing dead code unless asked

Validation: every changed line should trace directly to the user's request.

### Step 4: Goal-Driven Execution

Transform tasks into verifiable goals before coding:

| User says | You define |
|-----------|------------|
| "Add validation" | "Write tests for invalid inputs, then make them pass" |
| "Fix the bug" | "Write a test that reproduces it, then make it pass" |
| "Refactor X" | "Ensure tests pass before and after" |

For multi-step tasks, state a brief plan:

```
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Examples

### Example 1: User says "add a delete button"

**Think first:** Where should it go? Confirmation dialog? Soft delete or hard delete? What happens to related data?

**Surface assumptions:** "I'll add a delete button to the user profile page with a confirmation dialog. It will soft-delete (set `deleted_at`). Should I also cascade to related records?"

**Simplicity:** Just the button, the handler, and the DB update. No undo system, no batch delete, no admin audit log unless asked.

**Surgical:** Only touch the profile component and the user service. Don't reorganize the component folder structure.

### Example 2: User says "fix the login bug"

**Think first:** Reproduce the bug. What's the expected vs. actual behavior?

**Goal-driven:** "I'll write a test that triggers the bug, confirm it fails, then fix and verify the test passes."

**Surgical:** Fix the specific condition causing the bug. Don't refactor the entire auth flow.

## Troubleshooting

### Skill feels too restrictive
**Cause:** Applying these rules to trivial one-liner tasks
**Solution:** Use judgment. These guidelines matter most for multi-file changes and complex features. For a typo fix, just fix it.

### Claude still overcomplicates
**Cause:** Instructions buried or not emphasized enough
**Solution:** Remind Claude: "Keep it simple. Only change what's needed. No extra features."

### Claude doesn't surface assumptions
**Cause:** Task seems unambiguous (but may not be)
**Solution:** Ask Claude: "What assumptions are you making?" before it starts coding.
