# Question Strategy by Dimension

Pick the dimension with the **lowest clarity score**. Ask ONE question from the templates below, filling placeholders with specific codebase elements from `exploration_{name}.md`.

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
- **One question per turn.** Never combine questions or ask multi-part questions.
- **No preambles.** Go straight to the question — no "Great answer!" or "That makes sense!".
- **No generic fallbacks.** If none of the templates fit, craft a question that still references specific codebase elements. Never ask "What are your requirements?" or "Any constraints?".
