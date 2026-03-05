# Question Strategy by Dimension

Pick the dimension with the **lowest clarity score**. Ask ONE question from the templates below, filling placeholders with specific codebase elements from `exploration_{name}.md`.

## Question Framing

Every question must include brief context so the user understands what you're asking about and why it matters. Users often haven't worked in every corner of their codebase — especially in large projects with many contributors. Before the question itself, include:

1. **What the element does** — A 1-2 sentence plain-language explanation of the file, class, or pattern you're referencing. Avoid jargon; describe the behavior a user would observe or the role it plays in the system.
2. **Why it matters for the feature** — How this element connects to what they want to build, or why the choice you're asking about has consequences they should care about.

This serves two purposes: it helps users give informed answers even when they're not experts in that part of the code, and it makes your reasoning transparent so they can correct you if your understanding is wrong.

**Example — without framing (bad):**
> `MCPServerAdapter.call_tool()`, `MCPClientManager.call_tool()`, and `ToolRegistry.call()` are the three dispatch paths. Which should the caching layer intercept?

**Example — with framing (good):**
> The codebase dispatches tool calls through three separate paths: `MCPServerAdapter.call_tool()` handles requests coming from external Claude Code clients with security checks, `MCPClientManager.call_tool()` sends requests out to external MCP servers with retry logic, and `ToolRegistry.call()` runs tools directly in-process with no network overhead. Caching at different layers would have different tradeoffs — should the cache intercept all three, or just one?

## Tie-Breaking Rule

When multiple dimensions share the lowest score, prioritize by weight: **Goal (35%) > Constraint (25%) = Criteria (25%) > Context (15%)**. If Constraint and Criteria tie at the same score, alternate between them across turns.

---

## Goal Clarity (weight: 35%)

1. "I see `{ExistingType}` in `{file}`. Should the new feature extend this, or is it a separate concern?"
2. "What specific behavior change should a user observe after this feature is implemented?"
3. "Walk me through the ideal interaction: a user does X, and the system responds with Y — what are X and Y concretely?"

---

## Constraint Clarity (weight: 25%)

1. "The codebase uses `{pattern}`. Must the new feature follow this pattern, or can it diverge?"
2. "Are there performance bounds? The current `{endpoint}` handles N req/s — does this need to match?"
3. "`{dependency}` is already in the project. Should the feature use it, or is a different library acceptable?"

---

## Success Criteria (weight: 25%)

1. "How would you test that this works? Can you describe one concrete scenario (Given/When/Then)?"
2. "What's the simplest case where this feature adds value?"
3. "If this feature shipped with a bug, what would the user report? Describe the failure scenario."

---

## Context Clarity (weight: 15%)

1. "I traced `{similar_feature}` through `{file1}` → `{file2}` → `{file3}`. Is the new feature expected to follow the same path?"
2. "Which existing integration points should this feature hook into?"
3. "`{module}` already handles `{related_concern}`. Should the new feature live there or in a new module?"

---

## Question Rules

- **Fill every placeholder.** Never ask a question with `{unfilled}` placeholders — substitute real file names, types, and patterns.
- **Frame every question with context.** Explain what the codebase element does and why the answer matters before asking. See "Question Framing" above.
- **One question per turn.** Never combine questions or ask multi-part questions.
- **No preambles.** Go straight to the context and question — no "Great answer!" or "That makes sense!".
- **No generic fallbacks.** If none of the templates fit, craft a question that still references specific codebase elements. Never ask "What are your requirements?" or "Any constraints?".
