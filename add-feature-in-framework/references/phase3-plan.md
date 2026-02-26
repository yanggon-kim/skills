# Phase 3: Plan the Implementation

## Goal

Create a concrete, step-by-step implementation plan where each step is independently verifiable. Get user approval before implementing.

## Why This Phase Exists

Multi-layer features fail when you try to implement everything at once. If you change hardware, software, and tests simultaneously and it doesn't work, you cannot tell which layer has the bug. A step-by-step plan with verification at each step makes debugging tractable.

## Step-by-Step Process

### 1. Decompose the Feature into Ordered Steps

Break the feature into steps that follow this principle:

> **Each step should produce a build-and-testable state.**

Good decomposition:
- Step 1: Add the instruction encoding (builds, but instruction is a no-op)
- Step 2: Add the hardware module (builds, instruction now does something)
- Step 3: Add the kernel API (builds, software can issue the instruction)
- Step 4: Add the test (builds, test exercises the whole path)

Bad decomposition:
- Step 1: Implement everything across all layers (can't isolate bugs)

### 2. Order Steps by Dependency

Typical ordering for multi-layer features:

```
Bottom-up (recommended for hardware features):
  1. Hardware/Simulator layer (new module, new datapath)
  2. Instruction encoding / decoder layer
  3. Kernel API / intrinsics
  4. Host driver changes
  5. Test program
  6. Build system integration

Top-down (recommended for software features):
  1. API / interface design
  2. Host driver changes
  3. Kernel implementation
  4. Simulator / hardware changes
  5. Test program
  6. Build system integration
```

Choose the order that lets you verify each step earliest.

### 3. For Each Step, Define the Verification

Every step needs a concrete way to check it worked:

| Step | Verification Method |
|------|-------------------|
| Add new source file | Build succeeds (no compile errors, no lint errors) |
| Add instruction encoding | Disassemble test binary — new instruction appears |
| Add hardware module | RTL builds with Verilator/VCS — no lint errors |
| Add kernel API function | Compile test program — new API compiles |
| Add test program | Run test — PASSED output |
| End-to-end integration | Run full test suite across all configs |

### 4. Write the Implementation Plan Document

Create a persistent document:

```markdown
# Implementation Plan: [Feature Name]

## Overview
[1-sentence summary of what will be implemented]

## Prerequisites
[What must be true before starting: framework builds, baseline tests pass]

## Steps

### Step 1: [Short Title]
- **What:** [What changes in this step]
- **Files:** [List of files to create/modify]
- **Verify:** [How to verify this step works]
- **Configs:** [Any build flags or configuration needed]

### Step 2: [Short Title]
- **What:** [What changes in this step]
- **Files:** [List of files to create/modify]
- **Verify:** [How to verify this step works]
- **Configs:** [Any build flags or configuration needed]

[... repeat for each step ...]

### Step N: Full Integration Test
- **What:** Run all configurations
- **Files:** [Test scripts, if any]
- **Verify:** [Full test matrix — all configs pass]

## Risk Items
- [Anything that might go wrong]
- [Layer interactions that are tricky]
- [Config combinations that are easy to get wrong]

## Open Questions for User
- [Anything needing user input before starting]
```

### 5. Present to the User and Get Approval

Present the plan to the user. Be explicit:

> "Here is the implementation plan. I will implement step-by-step, verifying each step before proceeding. May I proceed, or would you like to adjust anything?"

Common user feedback:
- **Reorder steps:** User may prefer a different order based on their priorities
- **Add steps:** User may want additional verification points
- **Remove steps:** User may want to skip certain steps for speed
- **Scope change:** User may realize the feature needs more or less than originally planned

Update the plan document to reflect any changes.

## Pre-Implementation Analysis

Before writing the plan, do two analyses that save enormous debugging time later:

### Hand-Compute Parameters for Multiple Configs

If the feature is parametric (works across data types, thread counts, sizes), manually compute the key parameters for at least two different configurations. Write them side by side:

```
Parameter              Config A   Config B   Same?
─────────────────────  ─────────  ─────────  ─────
[control param 1]      X          X          ✓
[control param 2]      X          X          ✓
[data param 1]         X          Y          (different but handled)
[data param 2]         X          Y          (different but handled)
```

**Why this matters:** If all control-flow parameters (loop counts, register indices, state machine transitions) are identical across configs, the feature will likely work for all configs without code changes — just different data dimensions. If any control-flow parameter differs, that's where bugs will appear, and your plan should include explicit testing for those configs.

For a concrete example of this technique correctly predicting that a new config would work without code changes, see `../examples/vortex_sparse_tcu.md` — Phase 3 section.

### Config Sensitivity Analysis

Classify every parameter as **config-sensitive** or **config-invariant**:

- **Config-invariant:** Same value regardless of configuration. These are safe — test once, they work everywhere.
- **Config-sensitive:** Changes with configuration. These need testing for every config, and are where bugs hide.

For config-sensitive parameters, ask: "What happens at the extreme values?" The minimum and maximum values of each parameter are where bugs are most likely.

## Plan Evolution

The plan is a living document. During Phase 4 (implementation), you may discover:
- A step needs to be split into sub-steps
- A new step is needed that wasn't anticipated
- The order needs to change due to a discovered dependency

When this happens:
1. Stop implementing
2. Update the plan document
3. Briefly inform the user of the change and why
4. Get approval to continue
5. Resume implementing

## Checklist Before Moving to Phase 4

- [ ] Is every step independently verifiable?
- [ ] Have you identified all files that need to change?
- [ ] Have you defined the verification method for each step?
- [ ] Have you hand-computed parameters for at least two configurations?
- [ ] Have you identified which parameters are config-sensitive vs config-invariant?
- [ ] Is the plan document written and saved?
- [ ] Has the user approved the plan?
