# Phase 5: Verify the Whole Design

## Goal

Confirm the complete feature works correctly across all configurations and that no existing functionality is broken.

## Why This Phase Exists

Phase 4 verified each step individually. Phase 5 verifies the whole feature end-to-end. Individual steps can pass but the full integration can fail due to:

- Interactions between steps that weren't tested in isolation
- Configuration combinations that weren't tested during development
- Existing features that the new code inadvertently broke

## Step-by-Step Process

### 1. Define the Test Matrix

Identify all configuration dimensions that the feature interacts with:

| Dimension | Values |
|-----------|--------|
| Data types | int8, fp16, int4, fp32, ... |
| Sizes | Small (minimum), medium, large |
| Modes | Dense, sparse, enabled, disabled |
| Thread counts | 8, 32, ... |
| Core counts | 1, 2, 4, ... |

The test matrix is the cross-product of relevant dimensions. Not all combinations need testing — identify which dimensions interact with the new feature.

### 2. Run Feature-Specific Tests

Run the new feature's tests across the full test matrix:

```
For each config in test matrix:
    1. Clean build all affected layers with this config
    2. Build the test program with matching config
    3. Run the test
    4. Record: PASS/FAIL, cycle count, any warnings
```

**Important:** Clean build between config switches. Stale artifacts from a previous config are a major source of false failures.

### 3. Run Regression Tests

Run ALL existing tests that exercise the area you modified. The goal is to catch unintended breakage:

- If you modified the instruction decoder, run tests for ALL instruction types
- If you modified the memory subsystem, run ALL memory tests
- If you modified the build system, rebuild ALL targets

Regression test strategy:
1. **Smoke test:** Run the most important existing tests first (fast feedback)
2. **Full regression:** Run the complete test suite for the affected area
3. **Unrelated regression:** Run a sample of tests from unrelated areas (sanity check)

### 4. Write New Tests If Needed

If the existing test suite doesn't cover the new feature adequately, write new tests:

- **Minimum functionality test:** Smallest possible input that exercises the feature
- **Configuration coverage test:** Test across all relevant config combinations
- **Edge case test:** Boundary values, zero inputs, maximum sizes
- **Negative test:** What happens when the feature is misconfigured or gets invalid input?

### 5. Automate the Test Sweep

For features with many configurations, write a test sweep script:

```bash
#!/bin/bash
# Example: sweep across types, modes, and sizes with clean builds
PASS=0; FAIL=0; TOTAL=0

for TYPE in config1 config2 config3; do
    # Clean ALL affected layers when switching types
    clean_rtl_layer
    clean_test_layer

    build_rtl_with_config $TYPE

    for MODE in baseline feature; do
        build_test_with_mode $TYPE $MODE

        for SIZE in small medium large; do
            TOTAL=$((TOTAL+1))
            echo "=== Test $TOTAL: $TYPE $MODE $SIZE ==="
            run_test $TYPE $MODE $SIZE
            if [ $? -eq 0 ]; then
                echo "PASS"
                PASS=$((PASS+1))
            else
                echo "FAIL"
                FAIL=$((FAIL+1))
            fi
        done
    done
done

echo ""
echo "================================="
echo "Summary: $PASS PASSED, $FAIL FAILED out of $TOTAL"
echo "================================="
```

**Critical details in the sweep script:**

- **Clean between type switches.** The `clean_rtl_layer` and `clean_test_layer` calls prevent stale artifacts from causing false failures.
- **Build RTL once per type, test once per mode.** RTL typically depends on type but not mode; tests depend on both. Structure the loops to minimize rebuilds.
- **Both modes in every sweep.** Always test the original mode (baseline) alongside the new mode (feature) to catch regressions.
- **Print each test as it runs.** If the sweep is interrupted (timeout, crash), you can see which tests completed and resume from where you left off.

This makes re-running verification easy after future changes.

### 6. Report Results to the User

Present results clearly:

```markdown
## Verification Results: [Feature Name]

### Feature Tests: [X/Y PASSED]
| Config | Size | Result |
|--------|------|--------|
| ...    | ...  | PASS   |

### Regression Tests: [X/Y PASSED]
| Test Suite | Result |
|-----------|--------|
| ...       | PASS   |

### Issues Found
- [List any failures and their root causes]
- [List any known limitations]
```

## The Accidental Pass Problem

One of the most dangerous verification failures is a test that **passes for the wrong reason**. Small configurations can accidentally pass because:

- A parameter computes to zero, causing a loop to be skipped entirely
- A default value happens to match the expected value for this particular config
- A code path isn't exercised because the problem size doesn't require it
- An initialization pattern happens to produce the correct output by coincidence

**Prevention strategy:**

1. **Always test with at least two sizes:** minimum tile-aligned size AND 2x that size. If the feature has a loop, the larger size forces multiple iterations.
2. **Test with randomized data, not sequential patterns.** Sequential data (1, 2, 3, ...) can produce correct-looking results by coincidence. Random data makes accidental correctness statistically impossible.
3. **When a smaller config passes but a larger config fails, suspect the smaller config of passing accidentally.** The larger config is revealing a real bug that the smaller config masks.

## Regression Testing the Original Mode

When adding a new mode (e.g., sparse mode alongside existing dense mode), you MUST verify the original mode still works:

- **Separate code paths require separate tests.** If you added a mux ("if sparse, use path A; else use path B"), test both paths.
- **Don't assume the original path is untouched.** Even "isolated" changes can affect shared state, shared build flags, or shared control logic.
- **Include the original mode in every test sweep.** A sweep of "3 types x feature + baseline x 2 thread counts" catches regressions that a feature-only sweep misses.

For concrete examples of accidental passes and regression catches, see `../examples/vortex_sparse_tcu.md` — Phase 5 section.

## Debugging Verification Failures

When a test fails during verification:

1. **Is it a stale build?** This is the #1 cause. Clean and rebuild ALL layers, re-run. If the test passes after a clean build, you found the problem.
2. **Is it a config mismatch?** Check that all layers were built with matching configs. Print the active config from each layer if possible.
3. **Did it work during Phase 4?** If yes, an interaction between steps may be the cause.
4. **Is it an accidental pass that's now being exposed?** A config change may reveal a bug that was always there but hidden by a smaller config.
5. **Is it a regression?** Run the failing test against the code BEFORE your changes.
6. **Enable debug trace:** Use the framework's debug/trace mode to get cycle-by-cycle or line-by-line visibility.

## Checklist Before Moving to Phase 6

- [ ] Feature tests pass across all configurations in the test matrix
- [ ] Regression tests pass — no existing functionality broken
- [ ] Results documented and reported to the user
- [ ] Any test failures are explained (root cause identified)
- [ ] Test sweep script is saved for future re-use
