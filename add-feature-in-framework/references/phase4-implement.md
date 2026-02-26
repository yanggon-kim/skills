# Phase 4: Implement Step-by-Step

## Goal

Implement the feature one step at a time, verifying each step before moving to the next. Adjust the plan when needed with user approval.

## Why This Phase Exists

Multi-layer bugs are extremely hard to debug. If you change 10 files across 4 layers at once and get a test failure, you have no idea which change caused it. By implementing and verifying one step at a time, you always know exactly which change broke things.

## The Implementation Loop

```
For each step in the plan:
    1. Read the step's specification from the plan document
    2. Implement the changes
    3. Build (compile, lint, synthesize)
    4. Verify (run the step's verification test)
    5. If PASS → move to next step
    6. If FAIL → debug, fix, re-verify (do NOT move on)
    7. If plan needs adjustment → update plan, get user approval, continue
```

## Key Principles

### Build After Every Change

Never accumulate changes across files without building. The build is your first line of defense:

- **Compile errors** tell you about syntax and type mismatches immediately
- **Lint errors** (e.g., Verilator warnings-as-errors) catch unused signals, width mismatches
- **Link errors** catch missing symbols and interface mismatches between layers

### Verify Before Moving On

Each step in the plan has a defined verification method. Run it. If it fails, you must fix it before moving to the next step. Reasons:

- Bugs compound: a bug in step 2 will cause mysterious failures in step 5
- Earlier bugs are easier to debug: you know exactly which change introduced them
- The user expects each step to work before you report progress

### Clean Builds When Switching Configurations

When the framework has multiple configurations (e.g., different data types, different core counts, different modes), switching configs often requires a clean build. Common pattern:

```
1. Clean the affected build artifacts
2. Rebuild with the new config flags
3. Rebuild the test program with matching config flags
4. Run the test
```

Failure to clean between config switches is one of the most common bugs: the old binary runs with the wrong RTL, producing mysterious mismatches.

### Adjust the Plan When Needed

During implementation, you will discover things you didn't anticipate:

- A step needs to be split because it's more complex than expected
- A new step is needed (e.g., a config flag that must be propagated)
- The order needs to change due to a discovered dependency
- A design decision needs to be revisited

When this happens:
1. **Stop implementing** — do not push through a plan that doesn't match reality
2. **Update the plan document** with the change and the reason
3. **Tell the user** briefly what changed and why
4. **Get approval** before continuing (can be a quick confirmation)
5. **Resume** from the updated plan

### Debug Systematically

When a step's verification fails:

1. **Check configuration FIRST:** Before debugging algorithm logic, verify that ALL layers were built with matching configs. Config mismatch is the #1 cause of mysterious test failures, and it looks like a logic bug.
2. **Isolate the layer:** Is the bug in hardware/simulator, kernel, host, or test?
3. **Add trace/debug output:** Enable debug logging, add print statements, read trace logs
4. **Compare against reference:** If a software reference exists, compare its output to the hardware/simulator output
5. **Check the interface:** Is the data format crossing between layers correct? (e.g., endianness, bit packing, stride calculations)

### Recognize Common Bug Patterns

These patterns appear repeatedly in multi-layer feature development. When debugging, check for them explicitly:

**Pattern: State not reset between invocations**

A hardware counter, accumulator, or flag is initialized at module reset but not re-initialized when the feature is invoked again. The first invocation works; the second starts from stale state.

*How to spot it:* The feature works when the test calls it once per execution, but fails when the test calls it in a loop or when the problem size requires multiple invocations.

*Fix:* Add explicit reset logic at the start of each invocation (e.g., "when `start` signal is asserted and the module is not busy, reset all counters to zero").

**Pattern: Silent data corruption from config mismatch**

Two layers are built with different config flags. Both compile successfully. The test runs to completion. But the output is wrong — not random garbage, but systematically incorrect values.

*How to spot it:* The output errors are structured (e.g., "64 out of 64 errors", not random failures). The test worked before with the same code, but you recently switched configs.

*Fix:* Clean and rebuild ALL layers with matching flags. Create a verification step that prints the active config from each layer at startup, so you can visually confirm they match.

**Pattern: Sub-byte type unit confusion**

When elements are smaller than a byte (e.g., 4-bit integers), multiple elements pack into a single register slot. Code that works for byte-sized types fails because it confuses "number of elements" with "number of register slots" or "number of bytes."

*How to spot it:* The feature works for int8, fp16, fp32 but fails for int4 or other sub-byte types. The error pattern suggests wrong strides or offsets.

*Fix:* Audit every size/stride/count variable: is it in elements, bytes, or register slots? Add explicit scaling by the packing factor (e.g., 2 int4 elements per byte).

**Pattern: Combinational signal instability in multi-cycle operations**

In hardware (RTL), a control signal derived combinationally from inputs may change while a multi-cycle operation is in progress, causing the operation to switch behavior mid-execution.

*How to spot it:* The feature works in simulation with simple testbenches but fails in full-system simulation where inputs can change at any time.

*Fix:* Latch control signals as registers at the start of the operation. Use the latched value throughout the operation, not the live input.

**Pattern: Shared/static object mutation**

Frameworks often store decoded, parsed, or configured objects as static templates — one instance per unique key, shared across all uses. Setting a per-instance flag on the shared template (e.g., via `const_cast` in C++ or direct mutation of a cached object) corrupts ALL future uses of that template, even in unrelated contexts.

*How to spot it:* The feature works correctly on first execution, but subsequent executions behave as if the feature is always active (or always inactive). A `const` qualifier on a pointer or an object retrieved from a cache/map is a warning sign.

*Fix:* Never modify objects through `const` pointers or shared references. Set per-instance flags on the *copy* of the object after it's been duplicated from the template. If you need to pass per-instance state through an interface that only accepts the template, add a parameter to the function instead.

**Pattern: Multiple resource release paths**

When a resource is acquired in one place but can be released through multiple paths (fast path vs. slow path, hit vs. miss, normal vs. exceptional), missing any release path causes leaks.

*How to spot it:* A counter or resource grows without bound over time, eventually hitting an assertion or exhausting capacity. The leak is intermittent — it only occurs when the operation completes through the missed path.

*Fix:* Search for EVERY code path where the operation completes. Search for all places that call the "complete", "done", "finish", or "release" function for that operation type. Add the release on every path, not just the most common one.

**Pattern: One-to-many operation mapping**

A single high-level operation fans out to multiple low-level operations (sub-requests, packets, iterations). Per-operation accounting that runs in the per-sub-operation loop fires too many times.

*How to spot it:* A counter decrement assertion fires almost immediately. The decrement count far exceeds the increment count. Logging shows the accounting code running N times per increment.

*Fix:* Find the "all sub-operations complete" check (e.g., reference count reaching zero, completion flag, "all done" callback) and place accounting inside that condition, not in the per-sub-operation loop.

**Pattern: Bypass creates new hazards**

When you bypass a safety mechanism (dependency tracker, lock, fence, ordering queue) for performance, the hazards it was preventing can now occur. The mechanism's existing error handling (assertions, aborts) will fire on conditions it assumed were impossible.

*How to spot it:* Assertion failure in the mechanism you're bypassing, with a message about a resource already being in a certain state (e.g., "already reserved", "already locked", "duplicate entry").

*Fix:* Before implementing a bypass, enumerate every hazard the mechanism prevents. Add explicit handling for each: convert assertions to graceful handling (e.g., skip redundant operations), use reference counting instead of set membership, or add a "bypass active" flag that relaxes the checks.

For concrete examples of the first four patterns (RTL/hardware), see `../examples/vortex_sparse_tcu.md` — Phase 4 section.
For concrete examples of the latter four patterns (cycle-level simulator), see `../examples/gpgpusim_dae.md` — Phase 4 section.

## Cross-Layer Integration Tips

### Interface Contracts

When a feature spans layers, the interface between layers is the most bug-prone area. Define clear contracts:

- **Data format:** How is data packed? What is the byte order? What is the stride?
- **Instruction encoding:** What are the exact bit fields? (opcode, funct3, funct7, register fields)
- **Memory layout:** How is data laid out in memory? Row-major vs column-major? Padding?
- **Config propagation:** If a compile-time flag affects multiple layers, ALL layers must receive it

### One Config, All Layers

A single configuration (e.g., "int8 input type, 8 threads") must be consistently applied to ALL layers:

```
RTL build:       -DNUM_THREADS=8 -DITYPE_BITS=8
Test build:      -DNUM_THREADS=8 -DITYPE=int8
Runtime build:   -DNUM_THREADS=8
```

If any layer uses a different config, results will be wrong but the test may still compile and run — producing silent data corruption or mysterious mismatches.

### Config Propagation as an Explicit Step

If the feature introduces a new config flag (or depends on an existing one), treat config propagation as its own plan step with its own verification:

1. List every layer that needs the flag
2. Add the flag to each layer's build command
3. Verify by intentionally using two different config values — if the results change correctly, the flag is propagated. If results don't change, the flag is being ignored somewhere.

**The most insidious config bugs happen when a missing flag causes the layer to use a default value that happens to be correct for your current test config.** It passes now, but when you switch configs, it silently breaks. Always test with at least two config values.

### Build System Awareness

Many frameworks have automated build scripts that rebuild multiple layers. Know which layers get rebuilt and which don't:

- Does the test runner rebuild RTL? Or use the last-built RTL?
- Does changing a config flag trigger a full rebuild or just a partial rebuild?
- Are there cached artifacts that survive a `make clean`?
- **Do any scripts (CI, test runners, convenience wrappers) override your config flags with their own defaults?** This is a common trap: you carefully set flag X=16, but the test runner script ignores your setting and rebuilds with X=8.

## Checklist for Each Step

- [ ] Step changes implemented
- [ ] Build succeeds (no compile/lint errors)
- [ ] Step verification test passes
- [ ] No unintended side effects observed
- [ ] Plan document updated if any adjustments were made
