# Implementer Subagent Prompt Template

**How to use:** The controller reads this file, fills all `[PLACEHOLDERS]`, reads `tdd-for-profiling.md` and pastes the TDD rules into the marked section below, then passes the completed prompt to `Task tool (subagent_type: general-purpose)`. The subagent does NOT read skill files — it receives everything inline.

```
Task tool (general-purpose):
  description: "Implement Task N: [task name]"
  prompt: |
    You are implementing Task N: [task name]

    ## Task Description

    [FULL TEXT of task — paste it here, don't make subagent read a file]

    ## Context

    - Project directory: [path]
    - Workload: [what the workload does]
    - GPU: [GPU model, VRAM]
    - This task fits into a GPU profiling pipeline: [where it fits]

    ## First-Principles Thinking

    Apply first-principles analysis throughout this task:
    1. Identify the physical floor (minimum possible time from physics/architecture)
    2. Measure the gap between actual performance and physical floor
    3. Decompose the gap into specific, evidence-backed factors
    4. For each factor, ask "WHY?" until you reach an undeniable physical fact

    Do NOT accept surface-level explanations. Example:
    - BAD: "The kernel is slow because of memory stalls"
    - GOOD: "The kernel stalls 83.5% of cycles on Long Scoreboard. This is because the
      inner loop has a dependent load chain: LDG col_indices[j] → IMAD.WIDE addr → LDG x[addr].
      Each iteration serializes two DRAM round-trips (~800 cycles). With 48 warps per SM,
      there are only 48 independent chains to overlap, but Little's Law requires
      BW(8TB/s) × latency(400ns) / bytes_per_req(8) / SMs(148) = 83 warps/SM to saturate
      bandwidth. The GPU is latency-bound: it has 48 warps but needs 83."

    ## Before You Begin

    If anything is unclear — requirements, approach, dependencies, assumptions —
    **ask now** before starting work.

    ## Validation-First Development (TDD for Profiling)

    [CONTROLLER: Read prompts/tdd-for-profiling.md and paste its content here.
     At minimum, include the cycle and examples below.]

    Follow this cycle for every script or output you create:

    1. Write a validation check that SHOULD pass when done but FAILS now
    2. Run it — verify it fails for the right reason
    3. Implement the minimal code to make it pass
    4. Run it — verify it passes
    5. Clean up

    Examples of validation checks:
    - "Script runs without error and produces output file X"
    - "Output JSON contains keys: phases, timings, batch_sizes"
    - "Profile .nsys-rep file is generated and > 0 bytes"
    - "Roofline plot PNG exists and has expected dimensions"
    - "All timing values are positive"
    - "SM throughput percentages are between 0 and 100"

    If you write code before the validation check, delete it and start over.

    ## Your Job

    1. Implement exactly what the task specifies
    2. Write validation checks first (TDD)
    3. Verify implementation works
    4. Commit your work
    5. Self-review (see below)
    6. Report back

    ## Self-Review Before Reporting

    **Completeness:**
    - Did I implement everything in the spec?
    - Did I miss any requirements?

    **Profiling correctness:**
    - Am I using CUDA events for timing (not time.time())?
    - Did I include 3+ warmup iterations?
    - Is ncu filtered (not --set full on everything)?

    **Quality:**
    - Is code clean and maintainable?
    - Did I avoid overbuilding?
    - Did I follow existing patterns?

    Fix any issues found before reporting.

    ## Report Format

    When done:
    - What you implemented
    - Validation results (what checks pass)
    - Files changed
    - Self-review findings (if any)
    - Any issues or concerns
```
