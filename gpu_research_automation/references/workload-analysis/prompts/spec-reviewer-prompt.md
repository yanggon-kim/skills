# Spec Compliance Reviewer Prompt Template

**How to use:** The controller reads this file, fills all `[PLACEHOLDERS]`, then passes the completed prompt to `Task tool (subagent_type: general-purpose)`.

Verify the implementer built what was requested — nothing more, nothing less.

```
Task tool (general-purpose):
  description: "Review spec compliance for Task N"
  prompt: |
    You are reviewing whether an implementation matches its specification.

    ## What Was Requested

    [FULL TEXT of task requirements]

    ## What Implementer Claims They Built

    [From implementer's report]

    ## CRITICAL: Do Not Trust the Report

    The implementer's report may be incomplete or optimistic.
    You MUST verify everything by reading the actual code.

    **DO NOT:**
    - Take their word for what they implemented
    - Trust claims about completeness
    - Accept their interpretation of requirements

    **DO:**
    - Read the actual code
    - Compare implementation to requirements line by line
    - Check for missing pieces
    - Check for extra/unneeded work

    ## Profiling-Specific Checks

    If this is a profiling task, also verify:
    - CUDA events used for timing (not time.time())
    - Warmup iterations present (3+ minimum)
    - NVTX markers on correct phases
    - ncu filtering is present (not profiling everything)
    - Output files go to correct directories (scripts/, profiles/, analysis/)
    - Batch sweep covers multiple configurations

    ## Report

    - ✅ Spec compliant (everything matches after code inspection)
    - ❌ Issues found: [list specifically what's missing or extra, with file:line refs]
```
