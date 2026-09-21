<!-- The block below is a task brief, not an executable tool call. Fill it, then pass its prompt through the exposed Codex subagent interface. -->

# Implementer Subagent Prompt Template

**How to use:** The controller reads this file, fills all `[PLACEHOLDERS]`, reads `tdd-for-profiling.md` and pastes the TDD rules into the marked section below, then passes the completed prompt to `the available Codex subagent tool, with the filled prompt as its task message`. The subagent does NOT read skill files — it receives everything inline.

```text
Codex subagent task (adapt these fields to the exposed tool):
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

    If code already exists, preserve it and add a meaningful validation check; do not delete user work to enforce test order.

    ## Your Job

    1. Implement exactly what the task specifies
    2. Write validation checks first (TDD)
    3. Verify implementation works
    4. Commit only if the task brief authorizes it; otherwise leave a reviewable diff
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

---

## Step 5.5 dispatch addendum (Kernel SASS Forensics)

When dispatching for Step 5.5 specifically, fill in these additional placeholders inside the prompt's "Context" and "Task Description" sections:

```
## Step 5.5 inputs

- TARGET_KERNEL_SHORT: [e.g. csrmv_v3_kernel — the short name reported by ncu]
- TARGET_KERNEL_SYMBOL: [the full mangled symbol from `cuobjdump --list-text`,
                        e.g. _ZN8cusparse15csrmv_v3_kernelISt17integral_constantI...]
- GPU_ARCH: [e.g. sm_120 — must match the runtime GPU's compute capability]
- LIBRARY_PATH: [e.g. /usr/local/cuda/lib64/libcusparse.so.X.Y.Z for vendor
                kernels, or path to compiled .so / .cubin for custom kernels]
- NCU_REPORT: [path to .ncu-rep file from Step 4]
- INNER_LOOP_PC_RANGE: [optional, e.g. 0x0240-0x1300 — leave empty to discover
                       via backward-BRA enumeration in this task]
- OUTPUT_DIR: [e.g. <project>/analysis/ — directory for the synthesis doc and
              archived SASS dumps]

## Step 5.5 deliverables

Produce these files (paths relative to OUTPUT_DIR):

  <kernel>_<arch>.sass                 - raw cuobjdump dump (archive)
  <kernel>_<arch>_inst_inventory.csv   - total-kernel inventory
  <kernel>_<arch>_inner_inventory.csv  - inner-loop inventory (after BRA enum)
  static_vs_dynamic_crosscheck.md      - output of crosscheck_sass.py
  kernel_sass_analysis.md              - synthesis doc, 13-section template
                                         per references/kernel-sass-forensics.md
                                         (cite kernel_sass_analysis.md from
                                          01_suitesparse_spmv/analysis/ as the
                                          gold-standard reference)

## Step 5.5 method

Use these scripts in this order:

  1. cuobjdump --list-text LIBRARY_PATH | grep <kernel-name> | grep <arch>
     -> confirm the symbol matches TARGET_KERNEL_SYMBOL
  2. cuobjdump --dump-sass -arch=GPU_ARCH --function TARGET_KERNEL_SYMBOL \\
        LIBRARY_PATH > OUTPUT_DIR/<kernel>_<arch>.sass
  3. python scripts/build_inst_inventory.py <kernel>.sass --csv \\
        > <kernel>_<arch>_inst_inventory.csv
     (also emit the markdown form for the synthesis doc)
  4. Enumerate backward BRAs in the SASS to identify inner-loop PC range
     (see references/kernel-sass-forensics.md §3 for the recipe).
  5. python scripts/build_inst_inventory.py <kernel>.sass \\
        --inner-loop-range 0xPC_lo-0xPC_hi --csv \\
        > <kernel>_<arch>_inner_inventory.csv
  6. python scripts/parse_ncu_results.py NCU_REPORT \\
        --target-kernel TARGET_KERNEL_SHORT \\
        --output OUTPUT_DIR/ncu_<kernel>.json
  7. python scripts/crosscheck_sass.py \\
        --inventory <kernel>_<arch>_inst_inventory.csv \\
        --ncu-json OUTPUT_DIR/ncu_<kernel>.json \\
        --target-kernel TARGET_KERNEL_SHORT \\
        --single-run --gpu-arch GPU_ARCH \\
        > static_vs_dynamic_crosscheck.md
  8. Synthesise kernel_sass_analysis.md with the 13-section template from
     references/kernel-sass-forensics.md, populated with the data from steps
     3-7. Decompiled C-like pseudocode (§6) is the most-cited section —
     spend time on the phase walkthrough with annotated PC ranges.

## Step 5.5 validation

Before reporting complete, verify:

  - inventory CSV total instruction count matches `wc -l <kernel>.sass / 2` (±1).
  - inner-loop inventory has < total inventory (filter actually applied).
  - parse_ncu_results.py output JSON contains pipe_lsu_split with
    load_pct + write_pct ≈ pipe_utilization.lsu_active_pct.
  - crosscheck_sass.py output has both static counts and dynamic ncu rows.
  - kernel_sass_analysis.md has all 13 sections from
    references/kernel-sass-forensics.md.
  - The algorithm identification in §3 matches one of the patterns in §7
    of references/kernel-sass-forensics.md (or you have explicit evidence
    for a new pattern).
```

