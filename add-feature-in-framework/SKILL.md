---
name: add-feature-in-framework
description: Structured 6-phase process for adding features to multi-layer frameworks (simulators, compilers, accelerators, processors). Use when user says "add instruction to RISC-V", "add module to accelerator", "extend gpgpu-sim", "add feature to gem5", "add new execution mode", or any task spanning hardware RTL, simulator, compiler, and test layers. Do NOT use for single-file bug fixes, documentation-only changes, or trivial config tweaks.
metadata:
  version: 2.0.0
  author: yanggon
---

# Add Feature in Framework

A structured process for adding new features to multi-layer systems (software, hardware RTL, simulators, compilers, test suites) where a single change touches multiple layers.

## Critical Rules

- NEVER implement without exploring the framework first (Phase 1)
- NEVER start coding without user-approved plan (Phase 3)
- NEVER move to the next step until the current step compiles and passes its test
- ALWAYS trace config flags through ALL layers before testing
- ALWAYS test with at least two config sizes (minimum and 2x minimum)
- ALWAYS check `references/bug-pattern-catalog.md` when debugging unexpected failures

## Instructions

### Phase 1: Explore the Framework

Build a working mental model before touching anything.

1. Identify all layers: software/API, kernel/runtime, simulator, hardware RTL, build system, tests
2. Build the framework from scratch -- confirm it compiles
3. Run existing tests to confirm it works
4. Trace one existing feature end-to-end across all layers
5. Write a framework understanding document

**Output:** Document describing structure, build process, key files, and existing feature flow.

Reference: `references/phase1-explore.md`

### Phase 2: Understand the Requirements

1. Ask user: specs via prompt or documentation?
2. Read and understand the specification
3. Understand motivation -- functionality only? Performance? Both?
4. Identify which layers need changes
5. Identify what you can compile/test and what you cannot

**Output:** Requirements document summarizing what, why, and affected layers.

Reference: `references/phase2-requirements.md`

### Phase 3: Plan the Implementation

1. Break the feature into ordered steps, each independently verifiable
2. For each step: list files to modify and expected behavior change
3. Identify test/verification method for each step
4. Present plan to user -- revise until approved

CRITICAL: Do not proceed to Phase 4 without user approval.

**Output:** Implementation plan document approved by user.

Reference: `references/phase3-plan.md`

### Phase 4: Implement Step-by-Step

For each step in the plan:

1. Implement one step
2. Build and verify (compile, lint, run test)
3. If it fails, debug and fix before moving on
4. If plan needs adjustment, discuss with user and update plan

**Output:** Working code changes across all affected layers.

Reference: `references/phase4-implement.md`

### Phase 5: Verify the Whole Design

1. Run the feature's own tests across all configurations (types, sizes, modes)
2. Run existing regression tests to ensure nothing is broken
3. If tests don't exist, write them
4. Report results to user

**Output:** Full test results showing pass/fail across all configurations.

Reference: `references/phase5-verify.md`

### Phase 6: Measure Performance (If Applicable)

1. Identify the key metric (cycles, throughput, latency, memory)
2. Run baseline measurements (without feature)
3. Run measurements with feature enabled
4. Build comparison tables
5. Analyze insights (speedup, overhead, Amdahl's law, bottleneck shifts)

**Output:** Performance comparison table with analysis.

Reference: `references/phase6-performance.md`

## Common Failure Modes

| Failure | Prevention |
|---------|------------|
| Implementing without understanding the framework | Phase 1 forces exploration first |
| Building the wrong thing | Phase 2 requires understanding motivation |
| Implementing everything at once, can't debug | Phase 4 enforces step-by-step verification |
| Feature works but breaks existing tests | Phase 5 runs regression |
| Config mismatch between layers | Phase 4 verification catches this |
| Works for small config, fails for large | Phase 5 tests the full config matrix |
| Feature reduces one stall but speedup is modest | Phase 6 bottleneck shift analysis |

For 9 detailed bug patterns with symptoms, root causes, and prevention strategies, see `references/bug-pattern-catalog.md`.

## Examples

- `examples/vortex_sparse_tcu.md` -- Adding 2:4 structured sparsity to a RISC-V GPGPU tensor core (RTL + software, 5 modules, 3 data types)
- `examples/gpgpusim_dae.md` -- Adding DAE scoreboard bypass to GPGPU-Sim (6 source files, scheduler + scoreboard + writeback)

## Troubleshooting

### Build succeeds but tests produce wrong results
**Cause:** Config mismatch between layers (bug pattern #3)
**Solution:** Verify ALL layers were built with matching flags. Check `references/bug-pattern-catalog.md` pattern 1 and 3.

### Feature works once but fails on repeated invocation
**Cause:** State not reset between invocations (bug pattern #2)
**Solution:** For every counter/accumulator/flag, verify it resets at invocation start, not just initialization.

### Phase 4 step passes but Phase 5 regression fails
**Cause:** Step test was too narrow (only tested one config)
**Solution:** Test each step with multiple configs. See bug pattern #4.

### All tests pass but performance gain is smaller than expected
**Cause:** Bottleneck shifted to another component (Amdahl's law)
**Solution:** Run Phase 6 analysis to identify the new bottleneck. Consider parameter sensitivity sweep.

## All Reference Files

- `references/phase1-explore.md` -- Detailed Phase 1 guidance
- `references/phase2-requirements.md` -- Detailed Phase 2 guidance
- `references/phase3-plan.md` -- Detailed Phase 3 guidance
- `references/phase4-implement.md` -- Detailed Phase 4 guidance
- `references/phase5-verify.md` -- Detailed Phase 5 guidance
- `references/phase6-performance.md` -- Detailed Phase 6 guidance
- `references/bug-pattern-catalog.md` -- 9 recurring bug patterns with prevention strategies
