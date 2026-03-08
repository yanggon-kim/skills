# Diagnostic Techniques for Observing Intermediate Values

When the final output is wrong but you need to see what happens inside the computation, use these techniques. Each has trade-offs — choose based on your environment's constraints.

## 1. Debug Buffer Pattern (Most Reliable)

Allocate extra memory in your test, have the code write intermediate values to it, read them back after execution.

```
Setup:
1. Allocate debug_buffer[N] on host
2. Pass debug_buffer address to kernel/test code
3. At instrumentation points, write: debug_buf[idx] = value
4. After execution, download and inspect debug_buffer

Strengths:
- Non-intrusive to computation timing
- Works on any platform (simulator, hardware, embedded)
- Can capture as many values as buffer allows

Weaknesses:
- Requires modifying the test code
- Buffer address must be passed through the interface
- Memory writes may affect cache behavior
```

## 2. Zero-Input Tests (Best First Test)

Feed zeros (or other trivially-verifiable constants) as input. This eliminates entire subsystems in one test.

```
Logic:
- If input A = 0, and output = A * B + C, then output should = C
- If output != C, something other than the multiply is wrong
- If output = C, the multiply path is fine — the bug is in how A's values are selected/routed

Strengths:
- No code modification needed (just change host data)
- Eliminates data-path vs control-path in one test
- Fast to run

When to use:
- As the FIRST diagnostic test in Round 1
- Whenever you need to isolate "is the data wrong or is the routing wrong?"
```

## 3. Known-Pattern Tests

Use inputs with trivially predictable outputs:

| Pattern | Use Case |
|---------|----------|
| All zeros | Isolate data path from control path |
| All ones | Check accumulation logic |
| Identity matrix | Verify no transformation applied |
| Single non-zero | Trace exactly one element through the pipeline |
| Alternating (0101/1010) | Check bit-level routing and byte-enable |
| Sequential (0,1,2,3...) | Map output positions back to input sources |

## 4. CSR / Performance Counter Reads

Reading hardware counters or status registers exposes internal state without a debug buffer.

```
Caution: CSR reads take cycles and can perturb timing.

Mitigation strategies:
- Insert NOP/fence instructions before and after the read
- Run the same test WITH and WITHOUT reads to confirm behavior unchanged
- If behavior changes with reads → bug is timing-sensitive (useful information!)

Validation test:
1. Run test normally → record result
2. Add CSR reads → record result
3. If results differ → reads are intrusive, use debug buffer instead
4. If results match → reads are safe, proceed
```

## 5. Bisection Tests

If computation has N sequential steps, check output after N/2 to narrow where corruption enters.

```
Method:
1. Run full computation (N steps) → wrong output at step N
2. Dump intermediate result after step N/2
3. If correct at N/2 → bug is in steps N/2+1 to N
4. If wrong at N/2 → bug is in steps 1 to N/2
5. Repeat: check N/4 or 3N/4 accordingly

Works for:
- Iterative computations (K-loop in matrix multiply)
- Pipeline stages (check output of stage 3 vs stage 6)
- Multi-phase algorithms (sort → filter → aggregate)
```

## 6. Differential Testing (Cross-Platform)

Run the same test on both platforms, compare intermediate values at matching points.

```
Method:
1. Add identical debug buffer writes on both platforms
2. Run on platform A (passing) → save intermediate values
3. Run on platform B (failing) → save intermediate values
4. Diff the two → first divergence point reveals where the bug is

Key insight:
The FIRST difference is the bug location.
Later differences are cascading effects.
```

## 7. Reproducibility Tests

Run the same failing test multiple times and analyze variation.

| Observation | Implication |
|-------------|-------------|
| Same errors every run | Deterministic logic bug |
| Error count varies, positions fixed | Borderline timing issue |
| Error count AND positions vary | Race condition or timing-dependent bug |
| Errors correlate with temperature/time | Physical/environmental issue |

## Choosing Your First Test

```
Start here:
                    ┌─ Zero-input test
                    │  (eliminates data vs control path)
                    │
Bug observed ───────┤
                    │
                    ├─ Run 3-5 times
                    │  (deterministic vs timing-dependent)
                    │
                    └─ Minimal failing vs maximal passing
                       (find the boundary)

These three tests, run first, typically eliminate 50%+ of hypotheses.
```
