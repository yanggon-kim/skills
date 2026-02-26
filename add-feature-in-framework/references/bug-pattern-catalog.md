# Bug Pattern Catalog

These patterns recur across frameworks. Learn to recognize them.

## 1. Config Flag Not Propagated to All Layers

**Symptom:** Feature works for the default config but silently produces wrong results for other configs.

**Root cause:** A compile-time flag (e.g., data type width, thread count) is passed to some layers but not all. The layer that didn't receive it uses a default value, which happens to be correct for one config but wrong for others.

**Prevention:** For every config flag, trace its path through ALL layers. Create a table:

```
Flag: [DATA_TYPE_WIDTH]
├── RTL build:     -DTYPE_BITS=8     ok
├── Simulator:     -DTYPE_BITS=8     ok
├── Runtime:       (not needed)      ok
├── Test build:    -DTYPE=int8       ok (different name, same info)
└── Test runner:   ???               MISSING
```

## 2. State Not Reset Between Invocations

**Symptom:** Feature works when called once per execution, but produces wrong results when called multiple times (e.g., in a loop).

**Root cause:** Internal state (counters, accumulators, flags) is initialized at module creation but not reset when the feature is invoked again. The first invocation works; subsequent invocations start from stale state.

**Prevention:** For every stateful element (counter, register, accumulator), verify: "Is this reset at the start of each invocation, or only at initialization?" Add explicit reset logic in the "start of new invocation" path.

## 3. Silent Data Corruption (No Crash, Wrong Results)

**Symptom:** The test compiles, runs to completion, but the output is wrong. No error messages, no crashes -- just incorrect data.

**Root cause:** Usually a config mismatch between layers. Each layer is internally consistent, but they disagree on a parameter (data type width, memory stride, tile size). The data flows through the pipeline and gets computed, but with the wrong interpretation.

**Why it's dangerous:** Unlike a crash or compile error, silent corruption looks like a logic bug. You can spend hours debugging the algorithm when the real problem is a mismatched build flag.

**Prevention:** Always verify that ALL layers were built with matching configs before debugging algorithm logic. When you see wrong-but-not-random data, suspect a config mismatch first.

## 4. Works for Small Config, Fails for Large Config

**Symptom:** Minimum-size tests pass, but tests with larger dimensions or different parameter values fail.

**Root cause:** Small configs may "accidentally" work due to:
- Parameters that happen to be zero (no iterations, no offset)
- Arrays that happen to not overflow because the index range is small
- Default values that happen to match the expected value for this config
- Code paths that aren't exercised because loop counts are 1

**Prevention:** Test with at least two config sizes: minimum and 2x minimum. If the feature involves data-dependent behavior, test with randomized data, not sequential or constant patterns.

## 5. Sub-Element Unit Confusion

**Symptom:** Feature works for standard element sizes (e.g., 8-bit, 16-bit) but fails for sub-byte types (e.g., 4-bit) or packed types.

**Root cause:** The code assumes element size equals register slot size. For sub-byte types, multiple elements pack into one register slot, so indices, strides, and counts need scaling factors. A "tile of 8 elements" may be 8 bytes for int8 but only 4 bytes for int4.

**Prevention:** When the feature touches data indexing, verify the unit of every size/stride/count variable: is it in elements, bytes, or register slots? Add explicit scaling for sub-element types.

## 6. Shared/Static Object Mutation

**Symptom:** Feature works correctly on first execution of a code path, but produces wrong behavior on all subsequent executions -- even without the feature active.

**Root cause:** Modifying a shared or static object through a pointer that appears per-instance. Frameworks often store decoded/parsed objects as static templates (one instance per unique key, shared across all uses). If you set a per-instance flag on the shared template, ALL future uses of that object see the flag -- permanently corrupting the template.

**Why it's dangerous:** The first execution looks correct. The corruption only manifests later, in unrelated code paths, making it appear as a completely different bug. A `const` qualifier on a pointer is a warning sign that the object shouldn't be modified.

**Prevention:** Never modify objects through `const` pointers or shared references. If you need per-instance state, set the flag on the *copy* of the object after it's been duplicated from the template. Trace the lifecycle of any object you plan to modify: is it shared across invocations? Is it a template that gets copied? Is it a singleton?

## 7. Multiple Resource Release Paths

**Symptom:** Resource leak or double-release assertion. A counter that should balance (increments = decrements) drifts over time, eventually triggering an assertion or resource exhaustion.

**Root cause:** A resource is acquired in one place but can be released through multiple code paths. If any release path is missed, the resource leaks. Common in any system where operations can complete through different mechanisms (e.g., fast path vs. slow path, hit vs. miss, normal vs. exceptional).

**Prevention:** When adding resource accounting (counters, reference counts, FIFO occupancy):
1. List ALL code paths where the resource can be released -- search for every place the operation "completes"
2. Add the release on every path
3. Add an assertion that the counter is non-negative after each decrement
4. Add a check at shutdown/teardown that all counters are zero

## 8. One-to-Many Operation Mapping

**Symptom:** Counter or accounting logic fires N times per high-level operation instead of once. Assertions about balanced increments/decrements fail because the decrement side runs more frequently than expected.

**Root cause:** A single high-level operation maps to multiple low-level operations (e.g., a request fans out to multiple sub-requests, a transaction splits into multiple packets, a batch operation iterates internally). If accounting code runs per low-level operation instead of per high-level operation, it over-counts.

**Prevention:** When adding per-operation accounting, find the "operation complete" signal -- the point where ALL sub-operations have finished -- and place the accounting there. Look for patterns like reference count reaching zero, completion callbacks, or "all done" flags. Do NOT place per-operation accounting in per-sub-operation loops.

## 9. Bypass Creates New Hazards

**Symptom:** Assertion or crash when the bypass mechanism encounters a situation the original ordering mechanism was preventing.

**Root cause:** Safety mechanisms (scoreboards, locks, fences, ordering queues, dependency trackers) exist to prevent specific hazards (data races, deadlocks, overflow, reordering violations). When you bypass the mechanism for performance, those hazards can now occur. The mechanism's existing error handling (assertions, aborts) will fire on conditions it assumed were impossible.

**Prevention:** Before implementing any bypass:
1. List every hazard the mechanism prevents (data hazards, deadlocks, overflows, ordering violations)
2. For each hazard, determine if it can occur under your bypass conditions
3. For each hazard that can occur, add explicit handling (e.g., skip redundant operations, use reference counting instead of set membership, add a "bypass active" flag that relaxes checks)
4. Test with workloads that exercise repeated access to the same resource
