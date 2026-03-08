# Worked Example: Vortex FPGA LUTRAM Byte-Enable Bug

This documents a real root-cause investigation that found and fixed a LUTRAM byte-enable corruption bug in the Vortex GPGPU sparse tensor core. It demonstrates the hypothesis-round methodology in practice.

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Initial Facts](#initial-facts)
3. [Key Insight That Focused The Investigation](#key-insight)
4. [Round 1: Hypotheses](#round-1-hypotheses)
5. [Round 1: Diagnostic Tests](#round-1-diagnostic-tests)
6. [Round 1: Results & Analysis](#round-1-results)
7. [Root Cause](#root-cause)
8. [Fix & Verification](#fix--verification)
9. [Lessons Learned](#lessons-learned)

---

## Problem Statement

INT8/INT4 sparse tensor core operations FAIL on FPGA (Alveo U55C) when matrix dimensions M,N >= 32, but PASS on RTLsim (Verilator cycle-accurate simulator). FP16 sparse PASSES on both platforms. ALL dense operations PASS on both platforms.

The system: Vortex RISC-V GPGPU with a configurable tensor core unit (TCU) supporting 2:4 structured sparsity. The TCU stores sparsity metadata in an SRAM (VX_tcu_meta.sv) and uses it to select which B-matrix columns to use during computation.

## Initial Facts

These observations formed the foundation for all hypotheses:

1. **Platform-specific**: RTLsim passes all tests. FPGA fails INT8/INT4 sparse at M,N>=32.
2. **Type-dependent**: FP16 sparse passes on FPGA. INT8 and INT4 sparse fail.
3. **Size-dependent**: M,N<=16 passes on FPGA even for INT8/INT4. M,N>=32 fails.
4. **Dense unaffected**: All dense operations pass on both platforms.
5. **Error count varies**: INT8 shows 4-28 errors out of 1024 elements. INT4 shows 6-77 errors.
6. **Error count varies between runs**: Not exactly the same errors each time → possible timing sensitivity.
7. **v3 baseline passes**: An older design with separate meta_store and mma_sync instructions passes all FPGA tests.

## Key Insight That Focused The Investigation

The critical differentiator between FP16, INT8, and INT4 is `meta_cols`:

| Type | meta_cols | Description |
|------|-----------|-------------|
| FP16 | 1 | Single meta_store write per K-tile |
| INT8 | 2 | Two sequential meta_store writes per K-tile |
| INT4 | 4 | Four sequential meta_store writes per K-tile |

**FP16 works because it writes metadata once. INT8/INT4 fail because they write multiple columns sequentially to the same SRAM address.**

This single observation narrowed the investigation from "something is wrong with sparse" to "something is wrong with multi-column metadata writes."

## Round 1: Hypotheses

| # | Hypothesis | Rationale | Status |
|---|-----------|-----------|--------|
| H1 | Back-to-back LUTRAM partial writes corrupt data | FP16: 1 write OK; INT8: 2 sequential writes with different byte-enables → LUTRAM may not handle this | **CONFIRMED** |
| H2 | meta_thread_offset combinational path glitches on FPGA | ctr=0 always works; ctr>=1 uses combinational offset that may have FPGA timing issues | ELIMINATED |
| H3 | Multi-block warp reuse leaves stale metadata in columns 1+ | Column 0 overwritten correctly (like FP16), but columns 1+ retain stale data from previous blocks | ELIMINATED |
| H4 | FEDP pipeline corrupted by garbage during meta_store uops | Each meta_store pushes garbage through DSP pipeline; 2+ pushes may corrupt state | ELIMINATED |
| H5 | Phase transition timing differs for multi-uop meta phase | FP16 transitions at ctr=0, INT8 at ctr=1 → different FPGA timing | ELIMINATED |
| H6 | VX_tcu_sel reads wrong metadata bits from SRAM columns 1+ | If column 1+ data is stale/wrong, the B-column selection logic selects wrong elements | Subsumed by H1 |
| H7 | Register file read conflict on consecutive counter values | Back-to-back reads of same float register (f14) on FPGA | ELIMINATED |
| H8 | VX_dp_ram WRENW>1 write-enable OR logic glitches on FPGA | The WRENW partial-write pattern in VX_dp_ram may not synthesize correctly for FPGA LUTRAM | **Same as H1** |
| H9 | INT4 META_REG1 (f15) not loaded correctly | Only INT4 uses f15 (ctr>=2); if f15 wrong, columns 2-3 get wrong data | ELIMINATED |
| H10 | Error positions correlate with metadata column indices | Mapping errors to TC_M rows would reveal which columns are corrupted | **CONFIRMED pattern** |

## Round 1: Diagnostic Tests

### T5: Zero-A Matrix Test (highest priority — eliminates entire subsystems)

**Why this test first**: If all A-matrix values are zero, the output must be zero regardless of metadata. If FPGA produces non-zero output with zero A, then metadata is corrupting the B-column selection (data path issue). If output is zero, then the data path is fine and the computation uses wrong metadata values (metadata content issue).

**Method**: After generating the compressed A matrix and metadata on the host, zero out all A values while keeping metadata unchanged. Upload and run.

**Result**: ALL ZEROS on FPGA. Test PASSED.

**Conclusion**:
- ELIMINATED H4 (FEDP pipeline corruption) — DSP pipeline produces correct results
- ELIMINATED H6 partially — B-column selection logic itself is fine
- CONFIRMED that the issue is in metadata content, not in how metadata is used
- The wrong values in normal tests come from incorrect metadata causing wrong B elements to be accumulated

### T1: Error Position Analysis

**Method**: Run INT8 32x32x64 on FPGA, capture all error positions, map each (row, col) to:
- Block ID: (row/tileM, col/tileN)
- Sub-tile position: (row%tcM, col%tcN) where tcM=4, tcN=2
- step_m and step_k indices that produced this element

**Result**:
- Errors at sub_m positions 0-1 (metadata from column 0) but NOT at sub_m positions 2-3 (metadata from column 1)
- Wait — this is backwards from what H1 predicts (H1 says last column survives, others corrupted)
- Actually: column 0 is written first, column 1 is written second. Column 1 (last written) is correct. Column 0 (first written) is corrupted. **This matches H1 exactly.**

**Conclusion**: Error positions correlate with non-last metadata columns. H1 strengthened. H10 confirmed.

### T2: Single-Block Large-K Test

**Method**: Run INT8 8x8x2048 (1 block, many K-tiles, no warp reuse)

**Result**: PASSED (0 errors)

**Conclusion**: ELIMINATED H3 (warp reuse). The bug doesn't require multiple blocks or warp reuse. BUT 8x8 has M<=16 which only uses 1 block anyway. Need to retest with a case that has meta_cols>1 and single block... Actually, 8x8 with INT8 has meta_cols=2, so if this passes, the bug requires something about M,N>=32 specifically. Upon deeper analysis: 8x8 with INT8 uses tileM=8, so M=8 → 1 m-block. The per-warp metadata SRAM is partitioned by step_m × step_k. With only 1 block assigned per warp, there's no address contention — each warp writes metadata once and uses it.

### T3: Multiple Runs of Same Config

**Method**: Run INT8 32x32x64 on FPGA 5 times, record error positions each time.

**Result**: Error count varies (4, 8, 12, 6, 10). Error POSITIONS change between runs. Some positions fail in all runs, others are intermittent.

**Conclusion**: The failure has a **timing component**. This strongly suggests a hardware race condition (H1/H8) rather than a logic error (H2/H5/H9 — which would be deterministic).

## Round 1: Results

### What we proved:
1. **Metadata content is wrong** (zero-A test eliminates FEDP/data-path issues)
2. **Error positions correlate with non-last metadata columns** (first-written columns lost)
3. **Failures are non-deterministic** (timing-sensitive, pointing to hardware race)
4. **Bug needs M,N>=32** (multiple blocks sharing warps, metadata rewritten per block)

### Root Cause Identified: H1/H8 Confirmed

The VX_dp_ram instances in VX_tcu_meta.sv use `WRENW=NUM_COLS` (partial byte-enable writes). On FPGA, these map to LUTRAM with byte-enable ports. When two consecutive writes target the same address with different byte-enables:

```
Cycle N:   addr=warp_0, wren=01, data=col0_data  (write column 0)
Cycle N+1: addr=warp_0, wren=10, data=col1_data  (write column 1)
```

The LUTRAM implementation corrupts the first write — only the last column survives. This is because the FPGA LUTRAM byte-enable implementation does a **read-modify-write** internally, and back-to-back writes to the same address don't allow the first write to complete before the second read-modify-write begins.

**Why FP16 works**: meta_cols=1, so WRENW=1. No partial writes — the single write succeeds.

**Why RTLsim works**: Verilator simulates the behavioral RTL correctly. The `for (i=0; i<WRENW; i++) if (wren[i]) ram[addr][i] = wdata[i]` pattern works perfectly in simulation.

**Why small sizes pass**: With M,N<=16, each warp processes one block. Metadata is written once and used. No back-to-back writes to the same address happen because there's no warp reuse.

**Why error count varies**: The corruption depends on exact timing of when writes commit in the LUTRAM's internal pipeline. Clock jitter, temperature, and routing delays cause run-to-run variation.

## Fix & Verification

**Fix**: Split the single VX_dp_ram per bank (with WRENW=NUM_COLS) into NUM_COLS individual VX_dp_ram instances (each with WRENW=1). Each column gets its own independent RAM — no partial writes needed.

```systemverilog
// BEFORE (broken on FPGA):
VX_dp_ram #(.DATAW(META_BLOCK_WIDTH), .WRENW(NUM_COLS)) single_ram (...);

// AFTER (per-column split):
for (genvar c = 0; c < NUM_COLS; ++c) begin : g_col
    wire col_wr = init_active ? bank_wr : (bank_wr && col_wren[c]);
    VX_dp_ram #(.DATAW(32), .WRENW(1)) meta_col_ram (...);
end
```

**Verification**:
- New FPGA bitstream built (build_col_split_1c): 3h 2m, WNS=+0.003ns (timing MET)
- Cost: +82 LUTs (0.006%), same BRAM/DSP/FF count
- ALL previously failing INT8/INT4 sparse tests PASSED (sizes up to 128x128x512)
- ALL previously passing tests still PASS (regression clean)
- Comprehensive sweep: 60 data points (20 sizes x 3 types), all INT8/INT4 PASSED

## Lessons Learned

### Investigation methodology
1. **Start with zero-input tests** — they eliminate entire subsystems in one test
2. **Map error positions to architecture** — positional patterns reveal which hardware component is at fault
3. **Run the same test multiple times** — deterministic vs non-deterministic failures point to different bug classes
4. **The key differentiator between passing and failing configs is the first clue** — FP16 (meta_cols=1) passing while INT8 (meta_cols=2) fails immediately pointed to multi-column writes

### FPGA-specific lessons
5. **RTLsim passing is necessary but not sufficient** — behavioral simulation can't catch LUTRAM implementation bugs
6. **FPGA LUTRAM with multi-bit write-enable (WRENW>1) is unreliable for back-to-back partial writes** — always split into per-column instances (WRENW=1)
7. **Timing-dependent failures (varying error count between runs) suggest hardware race conditions** — not logic bugs
8. **Small changes in resource utilization (+82 LUTs) can fix fundamental correctness issues** — don't over-optimize for area

### General debugging lessons
9. **Breadth before depth** — 10 hypotheses per round prevents tunnel vision
10. **The context file is everything** — it survived context compression, conversation restarts, and multi-day investigation
