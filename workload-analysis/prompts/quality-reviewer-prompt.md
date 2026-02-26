# Code Quality Reviewer Prompt Template

**How to use:** The controller reads this file, fills all `[PLACEHOLDERS]`, then passes the completed prompt to `Task tool (subagent_type: general-purpose)`. Only dispatch AFTER spec compliance review passes.

```
Task tool (general-purpose):
  description: "Review code quality for Task N"
  prompt: |
    You are reviewing the code quality of a GPU profiling implementation.
    Spec compliance has already been verified — your job is quality only.

    ## Task Context

    [Brief description of what was implemented]

    ## Files to Review

    [List of files changed, with full paths]

    ## Your Job

    Read the actual code in every file listed above. Do NOT trust summaries.
    Evaluate against these criteria:

    **Code Quality:**
    - Clean, readable, maintainable
    - No unnecessary complexity or overbuilding
    - Follows existing codebase patterns
    - No magic numbers without explanation
    - Error handling where appropriate (but not excessive)
    - Variable and function names are clear and accurate

    **Profiling Correctness:**
    - CUDA synchronization correct (events, not wall clock)
    - Warmup iterations before measurement (3+ minimum)
    - Multiple iterations for statistical validity
    - ncu not over-profiling (filtered by NVTX or kernel name)
    - Output data in machine-readable format (JSON for data, Markdown for reports)
    - Scripts separate profiles, traces, and analysis into different directories

    **Data Integrity:**
    - Metrics make physical sense (SM% ≤ 100, memory throughput ≤ bandwidth)
    - Classifications are evidence-based (memory-bound vs compute-bound)
    - Roofline positions consistent with profiled metrics
    - No hardcoded GPU specs — use lookup or parameterize

    ## Report Format

    **Strengths**: [what's done well]

    **Issues** (categorize by severity):
    - Critical: [blocks correctness — must fix]
    - Important: [significant quality concern — should fix]
    - Minor: [style/preference — optional fix]

    For each issue, include file path and line number.

    **Verdict**: ✅ Approved / ❌ Needs fixes [list what must be fixed]
```
