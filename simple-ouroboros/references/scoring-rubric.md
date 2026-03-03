# Ambiguity Scoring Rubric

## Formula

```
ambiguity = 1.0 - (goal * 0.35 + constraint * 0.25 + criteria * 0.25 + context * 0.15)
```

Threshold: `<= 0.2` means ready for spec generation.

## Dimensions

### Goal Clarity (weight: 35%)

| Score | Anchor | Example |
|-------|--------|---------|
| 0.25 | Vague intent | "some caching", "make it faster", "add auth" |
| 0.50 | Named technology or approach | "Redis caching", "JWT authentication" |
| 0.75 | Technology + scope + location | "Redis caching for sessions in `auth/` module, replacing in-memory dict" |
| 1.00 | Fully specified behavior | Specific files + exact behavior change + performance target + edge cases named |

### Constraint Clarity (weight: 25%)

| Score | Anchor | Example |
|-------|--------|---------|
| 0.25 | No constraints or only vibes | "be fast", "keep it clean" |
| 0.50 | One concrete constraint | "no schema changes", "must use existing ORM" |
| 0.75 | Multiple constraints, bounded | "TTL <= 30s, use existing `SessionDataclass`, no new dependencies" |
| 1.00 | All constraints bounded and traceable | Every constraint references specific code, with clear pass/fail criteria |

### Success Criteria Clarity (weight: 25%)

| Score | Anchor | Example |
|-------|--------|---------|
| 0.25 | Vague outcome | "it works", "users can log in" |
| 0.50 | Named outcome with some specifics | "sessions persist across restarts" |
| 0.75 | Testable scenario described | Concrete test case with setup, action, and expected result |
| 1.00 | Numbered Given/When/Then list | Multiple acceptance criteria, each independently testable |

### Context Clarity (weight: 15%)

| Score | Anchor | Example |
|-------|--------|---------|
| 0.25 | Codebase directory identified only | "it's in `src/`" |
| 0.50 | Key files and patterns found | Entry points, config files, main abstractions identified |
| 0.75 | Integration points traced | How the feature connects to existing code, which layers are affected |
| 1.00 | Analogous feature traced end-to-end | A similar existing feature mapped through all layers, with differences noted |

## Anti-Bias Rules

These rules prevent score inflation. Apply them strictly.

1. **Score from scratch every turn.** Do not carry forward previous scores. Re-evaluate all evidence from the full transcript.

2. **0.8+ requires concrete specifics.** The user must have named specific files, types, functions, or patterns. General statements like "the auth module" do not qualify — it must be "the `authenticate()` function in `auth/middleware.py`".

3. **"I'll figure it out during implementation" does NOT resolve ambiguity.** If the user defers a decision, that dimension stays at its current score or drops.

4. **Absence of constraints is not constraint clarity.** If the user says "no constraints", score 0.50 at best — real projects always have constraints. Probe deeper.

5. **"It should just work" is not a success criterion.** Score 0.25 for criteria clarity. Push for Given/When/Then.

6. **Exploration alone does not raise Context Clarity above 0.50.** The user must confirm or clarify integration points for higher scores.

7. **When in doubt, round down.** A dimension that might be 0.60 or 0.70 should be scored 0.60.

## Clarification Triggers

Any dimension below `0.80` clarity should trigger a follow-up question targeting that dimension. Prioritize the dimension with the lowest score.

When multiple dimensions tie for lowest, prioritize in weight order: Goal > Constraint = Criteria > Context.
