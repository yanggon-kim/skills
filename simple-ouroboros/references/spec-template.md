# Specification Template

Write the spec as a single markdown file: `spec_{codebase_name}_{YYYY-MM-DD}.md`

Fill every section. If information is missing, write what you know and flag gaps in Section 10.

---

## Section 1: Goal

State the specific behavior change this feature introduces, referencing existing code.

**Fill guidance:**
- One paragraph, 2-4 sentences
- Must name the specific files/modules that will change
- Must describe the before-and-after behavior
- Pull directly from Goal Clarity evidence in the transcript

**Example:**
> Add Redis-backed session caching to the authentication module (`src/auth/session.py`). Currently, sessions are stored in an in-memory dictionary that is lost on restart. After this change, sessions will persist across server restarts with a configurable TTL (default 30 minutes).

---

## Section 2: Target Codebase Summary

Summarize the codebase structure relevant to this feature. Pull from `exploration_{name}.md`.

**Fill guidance:**
- Layers present (with key directories)
- Entry points relevant to the feature
- Tech stack / frameworks / key dependencies
- 5-10 lines max — just enough context for an implementer

---

## Section 3: Technical Constraints

List all constraints gathered during the interview. Each must be traceable to a specific Q&A turn.

**Fill guidance:**
- Numbered list
- Each constraint references the turn where it was established: `(Turn N)`
- Include both explicit constraints (user stated) and implicit constraints (from codebase conventions)
- If a constraint was inferred from code, cite the file

**Example:**
> 1. No database schema changes — existing `SessionDataclass` must be reused (Turn 2)
> 2. TTL must be configurable via environment variable, following pattern in `src/config.py` (Turn 3)
> 3. Must use `redis-py` — already in `requirements.txt` (inferred from codebase)

---

## Section 4: Acceptance Criteria

Numbered, testable criteria in Given/When/Then format.

**Fill guidance:**
- Minimum 3 criteria
- Each must be independently testable
- Cover: happy path, edge case, error case
- Pull from Success Criteria evidence in the transcript

**Example:**
> 1. **Given** a user logs in successfully, **When** the server restarts, **Then** the session is still valid when the user makes the next request.
> 2. **Given** a session is cached, **When** the TTL expires, **Then** the session is removed and the user must re-authenticate.
> 3. **Given** Redis is unavailable, **When** a user logs in, **Then** the system falls back to in-memory storage and logs a warning.

---

## Section 5: Architecture & Integration Points

Describe how the feature fits into the existing architecture.

**Fill guidance:**
- Which layers are affected
- Files to modify (with brief description of changes)
- New files to create (with purpose)
- Integration points: which existing functions/classes will call or be called by the new code
- Diagram if it helps (ASCII is fine)

---

## Section 6: Existing Feature Analogies

Identify the closest existing feature and trace how it works. Then describe how this feature differs.

**Fill guidance:**
- Name the analogous feature
- Trace it through the relevant files (entry point → core logic → persistence → tests)
- List similarities and differences
- This helps the implementer follow established patterns

**Example:**
> **Closest analogy:** The existing `CacheMiddleware` in `src/middleware/cache.py` already wraps Redis calls for API response caching.
> - Entry: `middleware/cache.py:CacheMiddleware.__call__` → `cache/redis_client.py:get/set` → `config.py:CACHE_TTL`
> - **Same:** Uses `redis-py`, reads TTL from config, has fallback logic
> - **Different:** Sessions need per-user keys (not per-URL), need serialization of `SessionDataclass`, need explicit invalidation on logout

---

## Section 7: Config & Build Integration

Document any configuration or build system changes needed.

**Fill guidance:**
- New environment variables or config flags
- Changes to `requirements.txt`, `pyproject.toml`, `package.json`, etc.
- New CLI flags or startup arguments
- Migration steps if any

---

## Section 8: Implementation Guidance

Ordered steps the implementer should follow. Reference specific files and functions.

**Fill guidance:**
- Numbered steps in recommended implementation order
- Each step names the file(s) and function(s) to create or modify
- Include the "why" for ordering (e.g., "step 2 depends on the interface defined in step 1")
- Keep it guidance, not pseudocode — the implementer will make detailed decisions

---

## Section 9: Testing Strategy

Describe how to test the feature, following the codebase's existing test conventions.

**Fill guidance:**
- Unit tests: what to mock, what to test in isolation
- Integration tests: which components to wire together
- Test file locations (following existing conventions)
- Key test scenarios beyond the acceptance criteria
- Any test infrastructure needed (fixtures, factories, test doubles)

---

## Section 10: Open Questions

List anything that remains unresolved.

**Fill guidance:**
- Any ambiguity dimension still below 0.8 clarity — explain what's missing
- Decisions deferred by the user ("I'll figure it out during implementation")
- Risks or unknowns discovered during exploration
- If spec was generated early (user said "done"/"skip" with ambiguity > 0.2), add a warning:

> **Early exit warning:** This spec was generated at ambiguity {score} (threshold is 0.2). The following dimensions need further clarification before implementation:
> - {dimension}: {what's missing}

If no open questions remain, write: "No open questions. All dimensions scored >= 0.8 clarity."
