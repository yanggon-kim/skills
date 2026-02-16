---
name: add-feature-in-framework
description: Use when adding a new feature, instruction, module, or capability to an existing software or hardware framework such as a GPGPU, simulator, compiler, accelerator, or any multi-layer open-source project
---

# Add Feature in Framework

## Overview

A structured 6-phase process for adding new features to existing frameworks. Frameworks are multi-layer systems (software, hardware RTL, simulators, compilers, test suites) where a single feature change touches multiple layers. This skill prevents the most common failure mode: implementing changes in one layer without understanding the ripple effects across others.

## When to Use

- Adding a new instruction to a processor (e.g., RISC-V custom instruction)
- Adding a new hardware module to an accelerator (e.g., sparsity unit in a tensor core)
- Adding new functionality to a cycle-level simulator (e.g., gpgpu-sim, gem5)
- Extending a compiler or toolchain with new intrinsics
- Adding a new execution mode or optimization to an existing framework
- Any feature that spans multiple layers (hardware + software + tests)

## When NOT to Use

- Single-file bug fixes with obvious root cause
- Documentation-only changes
- Trivial config changes (use the framework's existing patterns)

## The 6 Phases

```
Phase 1: EXPLORE the framework
    ↓
Phase 2: UNDERSTAND the user's requirements
    ↓
Phase 3: PLAN the implementation (get user approval)
    ↓
Phase 4: IMPLEMENT step-by-step (verify each step, adjust plan if needed)
    ↓
Phase 5: VERIFY the whole design
    ↓
Phase 6: MEASURE performance (if applicable)
```

Each phase produces a persistent artifact (document or file) that you can reference at any time.

### Phase 1 — Explore the Framework

**Goal:** Build a working mental model of the framework before touching anything.

**Key actions:**
1. Identify all layers: software/API, kernel/runtime, simulator, hardware RTL, build system, tests
2. Find and read the build instructions — can you build it from scratch?
3. Find existing sample programs or tests — run them to confirm the framework is functional
4. Trace through one existing feature end-to-end across all layers
5. Write a framework understanding document and persist it for future reference

**Output:** A document describing the framework's structure, build process, key files, and how an existing feature flows through all layers.

**Details:** See `phase1_explore/explore.md`

### Phase 2 — Understand the Requirements

**Goal:** Fully understand what the user wants and why.

**Key actions:**
1. Ask the user: will they provide specs via prompt or documentation?
2. Read and understand the specification
3. Understand the motivation — functionality only? Performance improvement? Both?
4. Identify which layers need changes (software, hardware, simulator, tests, build system)
5. Identify what you can compile and test, and what you cannot

**Output:** A requirements document summarizing what, why, and which layers are affected.

**Details:** See `phase2_requirements/requirements.md`

### Phase 3 — Plan the Implementation

**Goal:** Create a step-by-step plan, get user approval before implementing.

**Key actions:**
1. Break the feature into ordered steps, each independently verifiable
2. For each step, list the files to modify and the expected behavior change
3. Identify the test or verification method for each step
4. Write the plan as a persistent document
5. Present the plan to the user — discuss and revise until approved

**Output:** An implementation plan document approved by the user.

**Details:** See `phase3_plan/plan.md`

### Phase 4 — Implement Step-by-Step

**Goal:** Implement incrementally, verifying each step before proceeding.

**Key actions:**
1. Implement one step from the plan
2. Build and verify that step works (compile, lint, run a test)
3. If the step fails, debug and fix before moving on
4. If the plan needs adjustment, discuss with the user and update the plan document
5. Repeat until all steps are complete

**Output:** Working code changes across all affected layers.

**Details:** See `phase4_implement/implement.md`

### Phase 5 — Verify the Whole Design

**Goal:** Confirm the complete feature works correctly and nothing is broken.

**Key actions:**
1. Run the feature's own tests across all configurations (types, sizes, modes)
2. Run existing regression tests to ensure nothing is broken
3. If tests don't exist, write them
4. Report results to the user

**Output:** Full test results showing pass/fail across all configurations.

**Details:** See `phase5_verify/verify.md`

### Phase 6 — Measure Performance (If Applicable)

**Goal:** Quantify the feature's impact and report to the user.

**Key actions:**
1. Understand what performance metric matters (cycles, throughput, latency, memory)
2. Run baseline measurements (without the feature)
3. Run measurements with the feature enabled
4. Build comparison tables
5. Analyze and report insights (speedup, overhead, Amdahl's law effects)

**Output:** Performance comparison table with analysis.

**Details:** See `phase6_performance/performance.md`

## Common Failure Modes

| Failure | Prevention |
|---------|------------|
| Implementing without understanding the framework | Phase 1 forces exploration first |
| Building the wrong thing | Phase 2 requires understanding motivation |
| Implementing everything at once, can't debug | Phase 4 enforces step-by-step with verification |
| Feature works but breaks existing tests | Phase 5 runs regression |
| Config mismatch between layers (e.g., RTL built for type A, test built for type B) | Phase 4 verification catches this; Phase 1 documents build system |
| Stale build artifacts from previous configs | Phase 1 documents clean-build requirements |
| Feature passes with one config, silently fails with another | Phase 5 tests the full config matrix, not just the "easy" config |
| Automated scripts override manual builds | Phase 1 documents which scripts rebuild which layers |
| Accidental pass hides real bug until larger config exposes it | Phase 5 tests beyond minimum size |
| Feature eliminates target stall but total speedup is modest | Phase 6 bottleneck shift analysis reveals the next bottleneck |
| Feature parameter (buffer size, FIFO depth) is over-provisioned | Phase 6 parameter sensitivity sweep finds the binding constraint |

## Bug Pattern Catalog

These patterns recur across frameworks. Learn to recognize them:

### 1. Config Flag Not Propagated to All Layers

**Symptom:** Feature works for the default config but silently produces wrong results for other configs.

**Root cause:** A compile-time flag (e.g., data type width, thread count) is passed to some layers but not all. The layer that didn't receive it uses a default value, which happens to be correct for one config but wrong for others.

**Prevention:** For every config flag, trace its path through ALL layers. Create a table:

```
Flag: [DATA_TYPE_WIDTH]
├── RTL build:     -DTYPE_BITS=8     ✓
├── Simulator:     -DTYPE_BITS=8     ✓
├── Runtime:       (not needed)      ✓
├── Test build:    -DTYPE=int8       ✓ (different name, same info)
└── Test runner:   ???               ✗ ← MISSING
```

### 2. State Not Reset Between Invocations

**Symptom:** Feature works when called once per execution, but produces wrong results when called multiple times (e.g., in a loop).

**Root cause:** Internal state (counters, accumulators, flags) is initialized at module creation but not reset when the feature is invoked again. The first invocation works; subsequent invocations start from stale state.

**Prevention:** For every stateful element (counter, register, accumulator), verify: "Is this reset at the start of each invocation, or only at initialization?" Add explicit reset logic in the "start of new invocation" path.

### 3. Silent Data Corruption (No Crash, Wrong Results)

**Symptom:** The test compiles, runs to completion, but the output is wrong. No error messages, no crashes — just incorrect data.

**Root cause:** Usually a config mismatch between layers. Each layer is internally consistent, but they disagree on a parameter (data type width, memory stride, tile size). The data flows through the pipeline and gets computed, but with the wrong interpretation.

**Why it's dangerous:** Unlike a crash or compile error, silent corruption looks like a logic bug. You can spend hours debugging the algorithm when the real problem is a mismatched build flag.

**Prevention:** Always verify that ALL layers were built with matching configs before debugging algorithm logic. When you see wrong-but-not-random data, suspect a config mismatch first.

### 4. Works for Small Config, Fails for Large Config

**Symptom:** Minimum-size tests pass, but tests with larger dimensions or different parameter values fail.

**Root cause:** Small configs may "accidentally" work due to:
- Parameters that happen to be zero (no iterations, no offset)
- Arrays that happen to not overflow because the index range is small
- Default values that happen to match the expected value for this config
- Code paths that aren't exercised because loop counts are 1

**Prevention:** Test with at least two config sizes: minimum and 2x minimum. If the feature involves data-dependent behavior, test with randomized data, not sequential or constant patterns.

### 5. Sub-Element Unit Confusion

**Symptom:** Feature works for standard element sizes (e.g., 8-bit, 16-bit) but fails for sub-byte types (e.g., 4-bit) or packed types.

**Root cause:** The code assumes element size equals register slot size. For sub-byte types, multiple elements pack into one register slot, so indices, strides, and counts need scaling factors. A "tile of 8 elements" may be 8 bytes for int8 but only 4 bytes for int4.

**Prevention:** When the feature touches data indexing, verify the unit of every size/stride/count variable: is it in elements, bytes, or register slots? Add explicit scaling for sub-element types.

### 6. Shared/Static Object Mutation

**Symptom:** Feature works correctly on first execution of a code path, but produces wrong behavior on all subsequent executions — even without the feature active.

**Root cause:** Modifying a shared or static object through a pointer that appears per-instance. Frameworks often store decoded/parsed objects as static templates (one instance per unique key, shared across all uses). If you set a per-instance flag on the shared template, ALL future uses of that object see the flag — permanently corrupting the template.

**Why it's dangerous:** The first execution looks correct. The corruption only manifests later, in unrelated code paths, making it appear as a completely different bug. A `const` qualifier on a pointer is a warning sign that the object shouldn't be modified.

**Prevention:** Never modify objects through `const` pointers or shared references. If you need per-instance state, set the flag on the *copy* of the object after it's been duplicated from the template. Trace the lifecycle of any object you plan to modify: is it shared across invocations? Is it a template that gets copied? Is it a singleton?

### 7. Multiple Resource Release Paths

**Symptom:** Resource leak or double-release assertion. A counter that should balance (increments = decrements) drifts over time, eventually triggering an assertion or resource exhaustion.

**Root cause:** A resource is acquired in one place but can be released through multiple code paths. If any release path is missed, the resource leaks. Common in any system where operations can complete through different mechanisms (e.g., fast path vs. slow path, hit vs. miss, normal vs. exceptional).

**Prevention:** When adding resource accounting (counters, reference counts, FIFO occupancy):
1. List ALL code paths where the resource can be released — search for every place the operation "completes"
2. Add the release on every path
3. Add an assertion that the counter is non-negative after each decrement
4. Add a check at shutdown/teardown that all counters are zero

### 8. One-to-Many Operation Mapping

**Symptom:** Counter or accounting logic fires N times per high-level operation instead of once. Assertions about balanced increments/decrements fail because the decrement side runs more frequently than expected.

**Root cause:** A single high-level operation maps to multiple low-level operations (e.g., a request fans out to multiple sub-requests, a transaction splits into multiple packets, a batch operation iterates internally). If accounting code runs per low-level operation instead of per high-level operation, it over-counts.

**Prevention:** When adding per-operation accounting, find the "operation complete" signal — the point where ALL sub-operations have finished — and place the accounting there. Look for patterns like reference count reaching zero, completion callbacks, or "all done" flags. Do NOT place per-operation accounting in per-sub-operation loops.

### 9. Bypass Creates New Hazards

**Symptom:** Assertion or crash when the bypass mechanism encounters a situation the original ordering mechanism was preventing.

**Root cause:** Safety mechanisms (scoreboards, locks, fences, ordering queues, dependency trackers) exist to prevent specific hazards (data races, deadlocks, overflow, reordering violations). When you bypass the mechanism for performance, those hazards can now occur. The mechanism's existing error handling (assertions, aborts) will fire on conditions it assumed were impossible.

**Prevention:** Before implementing any bypass:
1. List every hazard the mechanism prevents (data hazards, deadlocks, overflows, ordering violations)
2. For each hazard, determine if it can occur under your bypass conditions
3. For each hazard that can occur, add explicit handling (e.g., skip redundant operations, use reference counting instead of set membership, add a "bypass active" flag that relaxes checks)
4. Test with workloads that exercise repeated access to the same resource

## Reference Examples

Two reference examples show this process applied to real projects:

### Example 1: Vortex GPGPU Sparse Tensor Core (RTL + Software)
See `examples/vortex_sparse_tcu.md`. Adding 2:4 structured sparsity to a RISC-V GPGPU's tensor core — touching 5 RTL modules, the instruction decoder, kernel API, and test programs across 3 data types and 2 thread counts. Includes:
- Phase-by-phase outputs and discoveries
- 6 real bugs mapped to patterns 1-5 above
- Performance data with Amdahl's law analysis
- Config flag propagation maps

### Example 2: GPGPU-Sim DAE Scoreboard Bypass (Cycle-Level Simulator)
See `examples/gpgpusim_dae.md`. Adding Decoupled Access-Execute (DAE) scoreboard bypass to GPGPU-Sim — modifying 6 source files across the scheduler, scoreboard, writeback, and instruction model. Includes:
- 3 runtime bugs mapped to patterns 6-8 above (shared object mutation, multiple release paths, one-to-many mapping)
- 1 design bug mapped to pattern 9 (bypass creates WAW hazards)
- Bottleneck shift analysis (97% stall reduction → 4-9% speedup)
- Parameter sensitivity sweep proving memory subsystem is the binding constraint
