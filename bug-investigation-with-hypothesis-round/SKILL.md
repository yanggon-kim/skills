---
name: bug-investigation-with-hypothesis-round
description: Systematic root-cause investigation for stubborn bugs using hypothesis-driven rounds with divide-and-conquer. Creates a persistent investigation context file, proposes 10 hypotheses per round based on observed facts, builds diagnostic tests, analyzes results, and iterates until root cause is found. Use when a bug passes on one platform but fails on another (simulator vs hardware, dev vs prod, one OS vs another), when errors appear only at certain input sizes or configurations, when the root cause is unknown and simple debugging has failed, or when the user says "investigate this bug", "find the root cause", "why does this fail on X but pass on Y", "debug this systematically", "root cause analysis", "this works in simulation but not on hardware". Do NOT use for simple bugs with obvious fixes, compilation errors, or typos.
---

# Hypothesis-Round Bug Investigation

Find root causes of stubborn bugs through empirical, hypothesis-driven rounds. Each round proposes 10 hypotheses, builds diagnostic tests, runs them, and narrows the search space. Continue until root cause is found — do not stop early.

## When to Use This Skill

This skill excels at bugs that resist conventional debugging:
- Platform-specific failures (passes on simulator, fails on hardware)
- Intermittent errors or non-deterministic failures
- Bugs that only appear at certain input sizes or configurations
- Discrepancies between environments (dev vs prod, OS A vs OS B)

## Workflow

```
1. Ask user where to save the investigation context file
2. Create context file with problem statement, facts, and constraints
3. Round N (repeat until root cause found):
   a. Write 10 hypotheses based on current facts
   b. Design diagnostic tests (prioritized by information gain)
   c. Build and run tests sequentially
   d. Analyze results, mark hypotheses CONFIRMED/ELIMINATED/NEEDS MORE DATA
   e. Update context file immediately after each action
4. Propose fix, verify it, document in context file
```

## Important

- Update the context file at every action, not just end-of-round. This file survives context compression and conversation restarts.
- Run tests sequentially on shared resources — parallel tests on the same device can corrupt each other's results.
- Take your time with analysis. Quality of hypothesis design matters more than speed. Each round should cut the hypothesis space significantly.

---

## Step 1: Create the Investigation Context File

Ask the user where to save it. Use naming convention: `YYMMDD-brief-description.md`

Write the initial file using this template:

```markdown
# [Bug Title] — Root-Cause Investigation

## Problem Statement
[What fails, where, when, with what inputs]

## Purpose
Find the definitive root cause through hypothesis-driven investigation.

## Rules
1. Do not stop until the root cause is found
2. Work round by round — 10 hypotheses per round
3. Every action and finding gets recorded in this file
4. Run tests sequentially on shared resources
5. Design tests that eliminate multiple hypotheses at once

## Known Facts
1. [Observed behavior — e.g., "Test X passes on platform A, fails on B"]
2. [e.g., "Small inputs pass, large inputs fail"]
3. [e.g., "Type A works but Type B doesn't — they differ in parameter X"]

## Environment and Constraints
- [Platform details, tool versions, build commands]
- [What CAN be changed vs what CANNOT be changed]

## Key Files
| File | Role |
|------|------|
| [path] | [description] |

## Platform Comparison Matrix
| Config | Platform A | Platform B | Notes |
|--------|-----------|-----------|-------|
| [config] | PASS/FAIL | PASS/FAIL | [detail] |

---

## Round 1: Hypotheses

| # | Hypothesis | Rationale (based on facts) | Test | Status |
|---|-----------|---------------------------|------|--------|
| H1 | ... | Fact 1, 3 | T1 | |
| H2-H10 | ... | ... | ... | |

## Round 1: Diagnostic Tests

### T1: [Test Name]
- **Tests hypotheses**: H1, H3
- **Method**: [specific steps]
- **Expected if true**: [prediction]
- **Expected if false**: [prediction]
- **Result**: [filled after running]
- **Conclusion**: [which hypotheses eliminated/confirmed]

## Round 1: Analysis
[Summary, updated facts, surviving hypotheses]

---
## Round 2: Hypotheses
[Refined based on Round 1]
```

---

## Step 2: Gather Facts

Before writing hypotheses, collect **observed behaviors** (not theories):

1. **Boundary identification**: Find the smallest failing case and largest passing case
2. **Cross-configuration comparison**: Which configs pass vs fail? What parameter differs?
3. **Reproducibility**: Is failure deterministic? Does error count/position change between runs?
4. **Error characterization**: Are errors random, patterned, or systematic? What are the wrong values?

Good: "Fails 3 of 5 runs with 4-28 errors at positions [list]"
Bad: "It sometimes fails"

---

## Step 3: Write 10 Hypotheses

Ten hypotheses per round — this forces breadth and prevents tunnel vision on a favorite theory.

Each hypothesis must:
- **Reference specific facts** that support it
- **Be falsifiable** — a concrete test can prove it wrong
- **Predict a specific outcome** — "if H is true, test X shows Y"
- **Be distinguishable** — different hypotheses predict different outcomes

Order by **expected information gain** — put tests that distinguish between the most hypotheses first. A single test that eliminates 5 hypotheses is more valuable than 5 tests that each eliminate 1.

For hypothesis sources across system layers, consult `references/hypothesis-sources.md`.

---

## Step 4: Design and Run Diagnostic Tests

Each test must be:
- **Targeted** — tests specific hypotheses, not "let's see what happens"
- **Observable** — produces concrete, comparable output
- **Minimal** — changes as little as possible from the known-good case
- **Reproducible** — exact command recorded for re-running

For strategies on observing intermediate values (debug buffers, zero-input tests, bisection), consult `references/diagnostic-techniques.md`.

### Test execution rules
- Run tests **one at a time** on shared resources
- Clean state between tests (rebuild, reset, clear caches)
- Record exact commands used
- If a test is flaky, run it 3-5 times and record all results

---

## Step 5: Analyze Results

For each hypothesis, compare test outcome against predictions:

- **ELIMINATED**: Results contradict hypothesis. Record which test and why.
- **CONFIRMED**: Results match prediction AND no simpler explanation exists. Seek a second confirming test from a different angle.
- **NEEDS MORE DATA**: Inconclusive. Design more targeted test for next round.
- **REFINED**: Partially right but needs modification. Write refined version.

Look for patterns in error data:
- **Positional**: Do errors cluster at specific indices? Map back to architecture.
- **Value**: Are wrong values random, off by a constant, or transformed?
- **Consistency**: Same positions every run, or varying?

Update context file immediately with results, conclusions, and new facts.

---

## Step 6: Iterate

Each round gets more specific:
- Round 1: "Is it data path or control path?"
- Round 2: "Is it write-address or write-data?"
- Round 3: "Is it byte-enable logic or address decode?"

### Root cause is found when you can:
1. **Predict** exactly which inputs fail and which pass
2. **Explain** why the bug manifests differently across configurations
3. **Propose a fix** that addresses the mechanism, not just the symptom
4. **Verify** the fix makes all failing tests pass without breaking passing tests

---

## Troubleshooting

### Investigation is stuck (no hypotheses eliminated)
- Design a **coarser** test: instead of testing one hypothesis, test a category (e.g., "is it in module A or module B?")
- Try a **zero-input test**: feed known-trivial input (zeros, identity) to isolate subsystems
- Run the **same test multiple times** — if results vary, the bug is timing-dependent (narrows to race conditions)
- Ask: what's the **single biggest difference** between passing and failing configs?

### Too many hypotheses survive each round
- Tests aren't discriminating enough — design tests where different hypotheses predict **opposite outcomes**
- Look for a **common upstream cause** that several hypotheses share

### Context file is getting too long
- Collapse completed rounds into a brief summary with key findings
- Keep the current round's details fully expanded
- Move raw test output to separate files, keep summaries in context file

### Instrumentation changes the bug behavior
- The bug is likely **timing-sensitive** (race condition, pipeline hazard)
- Try non-intrusive observation: check output values rather than intermediate state
- Use **known-input tests** (zeros, constants) that don't require instrumentation

---

## Example: A Round in Action

**Scenario**: Matrix multiply passes for 16x16 but fails for 32x32 on hardware. Simulator passes both.

**Fact gathering**:
- Fact 1: 16x16 PASS on both platforms
- Fact 2: 32x32 FAIL on hardware (12 wrong elements out of 1024), PASS on simulator
- Fact 3: Error count varies between runs (8-15 errors)
- Fact 4: Type A (1 metadata write) passes; Type B (2 metadata writes) fails

**Key insight from facts**: The differentiator is the number of sequential writes, not the data itself. This immediately narrows the search to the write mechanism.

**Highest-priority test**: Zero-input test (feed all zeros as input).
- If output is non-zero: data path corruption (writing wrong values)
- If output is zero: metadata content corruption (right path, wrong selector values)

**Result**: Output was all zeros. Eliminated 4 hypotheses about data path corruption in a single test. Investigation now focused on metadata write mechanism.

See `references/vortex-fpga-example.md` for the complete multi-round investigation that found a LUTRAM byte-enable bug using this methodology.

---

## Anti-Patterns

- **Shotgun debugging**: Changing random things hoping the bug disappears. Every change must be motivated by a hypothesis.
- **Confirmation bias**: Ignoring evidence against your favorite theory. The 10-hypothesis rule fights this.
- **Over-instrumenting**: Adding so much debug code that you change the behavior under test.
- **Fixing symptoms**: Adding workarounds without understanding why they work. These mask the real bug.
- **Skipping documentation**: If it's not in the context file, it didn't happen. Future rounds depend on past findings.
