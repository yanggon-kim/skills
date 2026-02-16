# Phase 6: Measure Performance (If Applicable)

## Goal

Quantify the feature's performance impact by comparing baseline (without feature) against the new implementation (with feature). Report results to the user with analysis.

## When to Use This Phase

- The feature's motivation includes performance improvement
- The user wants to know the overhead of a new functionality feature
- The user explicitly asks for a performance comparison

Skip this phase if the feature is purely functional and the user doesn't need performance data.

## Step-by-Step Process

### 1. Define the Performance Metric

Choose the right metric based on the feature's goal:

| Goal | Primary Metric | Secondary Metric |
|------|---------------|-----------------|
| Reduce computation time | Cycle count | Instruction count |
| Reduce memory bandwidth | Bytes transferred | Cache miss rate |
| Improve throughput | Operations per second | Utilization % |
| Reduce latency | Cycle count for critical path | Pipeline stalls |
| Reduce area/resources | LUT count, register count | Critical path delay |

### 2. Define the Benchmark Configurations

Choose configurations that show the feature's impact across different scenarios:

- **Varying sizes:** Small (overhead-dominated), medium (balanced), large (compute-dominated)
- **Varying data types:** Different types may benefit differently
- **Varying parameters:** The feature may interact with thread count, core count, etc.

### 3. Measure Baseline (Without Feature)

Run the baseline version (dense mode, feature disabled, original code path):

```
For each benchmark config:
    1. Build with baseline configuration
    2. Run the benchmark
    3. Record: total cycles, instructions, and any feature-specific metrics
```

### 4. Measure With Feature

Run the same benchmarks with the new feature enabled:

```
For each benchmark config:
    1. Build with feature-enabled configuration
    2. Run the benchmark
    3. Record: same metrics as baseline
```

### 5. Isolate Feature-Specific Cycles (Optional but Valuable)

Total cycle count includes overhead from thread management, memory access, synchronization, etc. To measure the feature's direct impact, isolate just the feature-related portion:

**Using hardware cycle counters (recommended for simulators and RTL):**
- Read the cycle counter CSR before the feature-related code section
- Read it again after
- The difference is the feature-specific cycles

**Using trace analysis:**
- Enable debug trace
- Filter for feature-specific operations in the trace log
- Count cycles between first and last feature operation

This separation reveals how much of the total time the feature actually affects, which determines the theoretical maximum speedup (Amdahl's law).

**Concrete implementation pattern for hardware cycle counters:**

The pattern requires changes in 3 files per test program (host, kernel, shared header):

```
1. Shared header: Add a field to the kernel argument struct for the cycle buffer address
2. Kernel: Read cycle counter before/after the feature-specific code section,
   write the delta to the buffer indexed by block_id
3. Host: Allocate a device buffer for cycle counts, pass its address to the kernel,
   read back after execution, report the max across all blocks
```

This gives you per-block cycle counts for just the feature-related computation, excluding thread spawn, memory allocation, result verification, and other overhead.

**Why max across blocks?** In a parallel execution, the total time is limited by the slowest block. The maximum cycle count across all blocks represents the actual feature execution time.

### 6. Build Comparison Tables

Present results in a clear format:

```markdown
## Performance Comparison: [Feature Name]

### Total Cycles
| Config | Baseline | With Feature | Speedup |
|--------|----------|-------------|---------|
| ...    | ...      | ...         | X.X%    |

### Feature-Specific Cycles (if measured)
| Config | Baseline | With Feature | Speedup | % of Total |
|--------|----------|-------------|---------|------------|
| ...    | ...      | ...         | X.X%    | X.X%       |
```

### 7. Analyze and Report Insights

Don't just present numbers — explain what they mean:

**Speedup trends:**
- Does speedup grow with problem size? (Feature benefit amortizes fixed overhead)
- Does speedup vary with data type? (Feature may benefit some types more than others)
- Does speedup vary with thread count? (Parallelism effects)

**Overhead analysis:**
- What is the feature's fixed overhead? (Setup cost, metadata loading, etc.)
- At what problem size does the feature break even?
- What fraction of total time does the feature-related code occupy?

**Amdahl's law in practice:**
- If the feature speeds up X% of total execution by 2x, the maximum total speedup is 1/(1-X+X/2)
- This explains why a large feature-specific speedup can translate to a modest total speedup
- The feature's value typically increases with problem size because the compute fraction grows while fixed overhead stays constant

**Fixed overhead analysis:**

Some features add one-time setup cost (e.g., loading metadata, initializing hardware state). Track this separately:

| Component | Cycles | % of Total (small) | % of Total (large) |
|-----------|--------|--------------------|--------------------|
| Feature overhead | [measured] | [high at small sizes] | [negligible at large sizes] |
| Feature benefit | [measured] | [may be < overhead] | [dominates overhead] |
| Net benefit | [computed] | [may be negative] | [positive] |

The fixed overhead is amortized over larger problems. If the overhead exceeds the benefit at small sizes, document the break-even point.

**Bottleneck shift analysis:**

Removing one bottleneck often reveals the next. A feature that eliminates 90%+ of a particular stall type may only yield single-digit total speedup because a different stall type grows to fill the gap. This is NOT a failure — it tells you what to optimize next.

To detect bottleneck shifts:
1. Measure MULTIPLE stall/wait categories in both baseline and feature runs (not just the one you're targeting)
2. Build a stall breakdown table:

| Stall Type | Baseline | With Feature | Change |
|-----------|----------|-------------|--------|
| Target stalls (e.g., dependency) | [large] | [small] | -90%+ |
| Secondary stalls (e.g., resource contention) | [small] | [large] | +N× |
| Idle cycles | [moderate] | [moderate] | ±small |
| **Total cycles** | **[baseline]** | **[improved]** | **-X%** |

When target stalls drop dramatically but total improvement is modest, the secondary stall category reveals the *next* bottleneck. The feature is working (target stalls are eliminated), but a different resource constraint limits the benefit.

**Implications for future work:** The stall breakdown tells the user what to optimize next. Report this explicitly — it's as valuable as the speedup number itself.

**Parameter sensitivity sweep:**

When a feature has a tunable parameter (buffer size, queue depth, window size, cache capacity), sweep it to find the binding constraint:

| Parameter Value | Performance Metric | Change from Max |
|----------------|-------------------|-----------------|
| min | [value] | ±X% |
| 2× min | [value] | ±Y% |
| 4× min | [value] | ±Z% |
| 8× min | [value] | ±0% |
| max | [value] | 0% (reference) |

**Flat sensitivity = the parameter is NOT the bottleneck.** Something else is limiting performance. This has direct design implications: if the smallest value performs identically to the largest, the resource budget for this parameter can be minimal.

**Non-flat sensitivity = the parameter IS (or was) the bottleneck.** The feature's benefit grows with the parameter until it saturates, revealing the "knee" where further increases give diminishing returns. Design for the knee point — values beyond it waste resources.

Always report sensitivity results — they separate "the feature works" from "the feature is the right size."

For a concrete example with real Amdahl's law numbers, cycle counter implementation details, and fixed overhead analysis, see `../examples/vortex_sparse_tcu.md` — Phase 6 section.
For a concrete example of bottleneck shift analysis and parameter sensitivity sweep with real data, see `../examples/gpgpusim_dae.md` — Phase 6 section.

**Report template:**

```markdown
## Performance Analysis: [Feature Name]

### Key Findings
- [Most important result: "Feature provides X% total speedup at large sizes"]
- [Scaling behavior: "Speedup grows from X% to Y% as size increases"]
- [Overhead: "Feature adds Z cycles of fixed overhead per invocation"]

### Detailed Results
[Comparison tables from step 6]

### Analysis
- [Explain speedup trends]
- [Explain overhead]
- [Amdahl's law analysis if relevant]
- [Recommendations: when to use the feature vs. when baseline is better]
```

## Automating Performance Sweeps

For reproducibility, write a benchmark script:

```bash
#!/bin/bash
# Performance sweep script
RESULTS="results.csv"
echo "Mode,Config,Size,Cycles,Instructions" > $RESULTS

for MODE in baseline feature; do
    build_for_mode $MODE
    for CONFIG in config1 config2 config3; do
        build_test $CONFIG
        for SIZE in small medium large; do
            run_benchmark $MODE $CONFIG $SIZE >> $RESULTS
        done
    done
done
```

Save the script alongside the results for future re-use.

## Checklist

- [ ] Performance metric defined
- [ ] Baseline measurements collected
- [ ] Feature measurements collected
- [ ] Feature-specific cycles isolated (if applicable)
- [ ] Comparison table built
- [ ] Analysis and insights written
- [ ] Results reported to the user
- [ ] Benchmark script saved for re-use
