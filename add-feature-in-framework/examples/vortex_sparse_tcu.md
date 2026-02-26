# Reference Example: Adding 2:4 Structured Sparsity to the Vortex GPGPU Tensor Core

This document captures lessons from a real multi-layer feature addition to the Vortex RISC-V GPGPU. It serves as a concrete reference for the general skill in `../SKILL.md`. Each section maps to a phase in the 6-phase process.

## Feature Summary

**What:** Add hardware 2:4 structured sparsity support to Vortex's tensor core unit (TCU). In every 4 consecutive elements of matrix A, exactly 2 are pruned (set to zero). This halves the computation by skipping zero elements, using metadata to select the correct elements from matrix B.

**Layers touched:** RTL hardware (5 SystemVerilog modules), instruction decoder, micro-op sequencer, kernel API, host driver, test program, build system configuration.

**Configs:** 3 data types (int8/int32, fp16/fp32, int4/int32) x 2 thread counts (NT=8, NT=32) x multiple matrix sizes.

---

## Phase 1: Explore — What Was Discovered

### Framework Layers

| Layer | Directory | Technology |
|-------|-----------|------------|
| Hardware RTL | `hw/rtl/` (tcu/ subdirectory) | SystemVerilog |
| Cycle-approximate simulator | `sim/simx/` | C++ |
| Kernel API | `kernel/include/` | C headers (vx_tensor.h, vx_sparsity.h) |
| Host runtime driver | `runtime/` (simx, rtlsim, opae) | C++ |
| Test programs | `tests/regression/` | C++ (main.cpp, kernel.cpp) |
| Build system | Makefiles + `configure` script | Make + shell |

### Build System Traps Discovered

**Test runner overrides manual builds:** The `blackbox.sh` test runner rebuilds RTL with its own `CONFIGS` variable, silently overriding any manual `make -C runtime/rtlsim` build. A manual build with `TCU_ITYPE_BITS=16` was overwritten when `blackbox.sh` used its default (no `TCU_ITYPE_BITS` -> default of 8).

**Hidden config dependency:** The RTL flag `TCU_ITYPE_BITS` controls the internal data ratio (`I_RATIO`). Without it, the hardware defaults to `ITYPE_BITS=8`. This works for int8 (the common config) but silently produces wrong results for fp16 (needs 16) and int4 (needs 4). This wasn't documented anywhere — it was discovered through debugging a fp16 test failure.

**Clean build scope:** Switching data types requires `make -C runtime/rtlsim clean` (RTL layer) AND `make -C tests/regression/test_name clean` (test layer). Missing either one causes stale binary mismatches.

**Submodule drift:** The `third_party/cvfpu` floating-point unit submodule occasionally drifted from its expected commit, causing unrelated build errors. Fix: `git submodule update -- third_party/cvfpu`.

### Config Flag Propagation Map

```
Flag: TCU_ITYPE_BITS (controls data type width in hardware)
├── RTL build:      -DTCU_ITYPE_BITS=8     ✓ (CRITICAL — defaults to 8 if missing)
├── Simulator:      (not needed)            ✓
├── Runtime:        (not needed)            ✓
├── Test build:     -DITYPE=int8            ✓ (different flag name, same concept)
└── blackbox.sh:    CONFIGS must include it  ✗ ← MISSING by default, caused fp16 failure

Flag: NUM_THREADS (thread count per warp)
├── RTL build:      -DNUM_THREADS=8         ✓
├── Simulator:      (auto-detected)         ✓
├── Test build:     (auto-detected)         ✓
└── blackbox.sh:    --threads=8             ✓
```

---

## Phase 3: Plan — Hand-Computing Parameters

Before implementing NT=32 support, parameters were hand-computed for both NT=8 and NT=32:

```
Parameter              NT=8     NT=32     Same?
---------------------  -----    -----     -----
tile_cap               64       256
xtileM                 8        16
xtileN                 8        16
xtileK                 8        16
tcM                    4        8
tcN                    2        4
tcK                    2        4
m_steps                2        2         ✓
n_steps                4        4         ✓
k_steps                4        4         ✓
a_sub_blocks           1        1         ✓
b_sub_blocks           2        2         ✓
NRA                    8        8         ✓
NRB                    8        8         ✓
NRC                    8        8         ✓
TCU_UOPS               32       32        ✓
```

All control-flow parameters (m_steps, n_steps, k_steps, register counts, micro-op count) were **identical**. Only data dimensions (tcM, tcN, tcK, tile sizes) changed. This correctly predicted that NT=32 would work without code changes — confirmed by testing.

---

## Phase 4: Implement — Bugs Encountered

Each bug maps to a pattern from the Bug Pattern Catalog in `../SKILL.md`.

### Bug 1: Config Flag Not Propagated (Pattern #1)

**What happened:** The RTL flag `TCU_ITYPE_BITS` was not passed to the RTL build command. The hardware defaulted to `ITYPE_BITS=8`, which produced `I_RATIO=4`. For int8, this was correct. For fp16 (`ITYPE_BITS=16`, needs `I_RATIO=2`), the hardware used the wrong ratio, selecting wrong B-column elements.

**How discovered:** int8 tests all passed. fp16 tests failed with systematic data errors.

**Fix:** Added `-DTCU_ITYPE_BITS=N` to every RTL build command, including inside `blackbox.sh` when it rebuilds RTL.

**Lesson:** When a feature works for one type but fails for another, suspect a config flag that defaults to the working type's value.

### Bug 2: State Not Reset Between Invocations (Pattern #2)

**What happened:** The micro-op counter in `VX_tcu_uops.sv` was initialized at module reset but not reset when a new `mma_sync` call began. For int8 (tileK=32, K=32), only one `mma_sync` call was needed per K-loop — the counter started at 0 and worked. For fp16 (tileK=16, K=32), two calls were needed — the second call started with the counter at 32 instead of 0, producing wrong register offsets.

**How discovered:** int8 passed, fp16 failed. Trace analysis showed the counter continuing from 32 instead of restarting at 0.

**Fix:** Added `counter <= 0` in the `~busy && start` path of the state machine.

**Lesson:** Whenever a feature works for one iteration but fails for multiple iterations, check every stateful element for missing reset logic.

### Bug 3: Silent Data Corruption (Pattern #3)

**What happened:** After switching from int4 testing to int8 testing, the RTL was rebuilt with `TCU_ITYPE_BITS=8` but the test binary was still the int4 version (not cleaned). The test compiled, ran to completion, and reported "Found 64 / 64 errors! FAILED!" — 100% wrong outputs, but no crash.

**How discovered:** Noticed the test was using int4 arguments with int8 RTL after inspecting the build state.

**Fix:** Added `make clean` for the test layer before every type switch.

**Lesson:** When ALL outputs are wrong (not just some), suspect a type/config mismatch between layers before debugging algorithm logic.

### Bug 4: Accidental Pass at Small Config (Pattern #4)

**What happened:** The `meta_store` instruction software computed `meta_cols` using `wmma_config_t<NT>` with fp32 defaults instead of the actual input type. For NT=8, this produced `meta_cols=0` — no `meta_store` instructions were emitted, so the SRAM kept its initialization data, which happened to be the correct alternating pattern. For NT=32, `meta_cols=2` (wrong, should be 8 for int8), and the SRAM was corrupted with wrong stride values.

**How discovered:** NT=8 passed all tests. NT=32 failed with data errors. Investigation revealed NT=8 was passing only because no `meta_store` was emitted.

**Fix:** Computed `rtl_i_ratio` and `num_cols` directly from the input type's bit width instead of using the default config.

**Lesson:** When a test passes at one config but fails at another, the smaller config may be passing accidentally. The larger config is revealing a real bug.

### Bug 5: Sub-Element Unit Confusion (Pattern #5)

**What happened:** `cfg::tileK` is in register-element units. For int4, `sizeof(int4)=1` byte (which holds 2 int4 elements), so register-element units differ from actual element units by a factor of 2. The CPU reference model's metadata mask calculation used `tileK` directly, producing masks at half the correct positions for int4.

**How discovered:** int8 and fp16 tests passed. int4 tests failed with wrong metadata patterns.

**Fix:** Scaled `tileK` by the sub-byte packing factor (`sizeof(register_type) / sizeof(element_type)`) in the mask calculation.

**Lesson:** When sub-byte types fail but byte-sized types pass, audit every size/stride variable for unit confusion.

### Bug 6: Combinational Signal Instability

**What happened:** The `is_sparse` control signal in `VX_tcu_uops.sv` was initially derived combinationally from the instruction opcode. Since the micro-op sequence takes many cycles, a subsequent instruction could change the opcode field, potentially flipping `is_sparse` mid-operation.

**How discovered:** During code review while implementing the separate sparse instruction encoding.

**Fix:** Latched `is_sparse` as a register when the `start` signal is asserted. The latched value is used throughout the multi-cycle operation.

**Lesson:** In RTL, any control signal that governs a multi-cycle operation must be latched at the start. Never use a combinational input directly if it can change during the operation.

---

## Phase 5: Verify — Results

### Test Matrix

| Dimension | Values |
|-----------|--------|
| Data types | int8/int32, fp16/fp32, int4/int32 |
| Thread counts | NT=8, NT=32 |
| Modes | Dense (baseline), Sparse (feature) |
| Sizes | Minimum tile-aligned, 2x minimum |

### Final Results: 21/21 PASSED

| Type | Mode | NT | Size | Result |
|------|------|-----|------|--------|
| int8/int32 | Dense | 8 | 8x8x32 | PASS |
| int8/int32 | Sparse | 8 | 8x8x32 | PASS |
| int8/int32 | Sparse | 32 | 16x16x64 | PASS |
| fp16/fp32 | Dense | 8 | 8x8x32 | PASS |
| fp16/fp32 | Sparse | 8 | 8x8x32 | PASS |
| fp16/fp32 | Sparse | 32 | 16x16x32 | PASS |
| int4/int32 | Dense | 8 | 8x8x32 | PASS |
| int4/int32 | Sparse | 8 | 8x8x32 | PASS |
| int4/int32 | Sparse | 32 | 16x16x64 | PASS |
| ... | ... | ... | ... | PASS |

### Regression: Dense Mode Unbroken

The original dense TCU path (`mma_sync`, funct3=0) was verified alongside sparse (`mma_struct_sparse_sync`, funct3=1). An early implementation accidentally modified the dense B-loading path, which was caught by including dense mode in every test sweep.

---

## Phase 6: Performance — Measurements

### Cycle Counter Implementation

Hardware cycle counters (RISC-V `MCYCLE` CSR at address 0xB00) were read before and after the K-loop (which contains `load_metadata`, `load_A`, `load_B`, `mma_sync`). This isolated the tensor core computation from thread management, fragment initialization, and result verification. The implementation touched 6 files (3 per test program x 2 test programs for dense and sparse):

- `common.h`: Added `uint64_t tcu_cycles_addr` field to kernel argument struct
- `kernel.cpp`: Added `csr_read(0xB00)` before/after K-loop, writes delta to cycle buffer
- `main.cpp`: Allocates device cycle buffer, reads back after execution, prints max across blocks

### Amdahl's Law in Practice

The sparse TCU halves K-loop iterations (2:4 sparsity compresses A by 50%). Measuring both total cycles and K-loop-only cycles revealed:

| Matrix Size | K-loop % of Total | K-loop Speedup | Total Speedup | Amdahl Predicted |
|-------------|-------------------|----------------|---------------|------------------|
| 8x8x32     | 5.2%              | 25%            | 4.5%          | ~1.3%            |
| 16x16x64   | 10.2%             | 41%            | 10.6%         | ~4.2%            |
| 64x64x128  | 22.0%             | 65%            | 31.4%         | ~14.3%           |

**Key insights:**
- At small sizes, the K-loop is only 5% of total execution — even a 25% speedup barely moves the total
- At large sizes, the K-loop grows to 22% — the 65% K-loop speedup produces 31% total speedup
- Speedup increases with problem size because the compute fraction grows while fixed overhead stays constant
- Actual total speedup exceeds Amdahl's prediction because the feature also reduces memory traffic (fewer B-matrix loads), which speeds up non-K-loop portions

### Fixed Overhead

The `meta_store` instruction adds one-time metadata loading cost:

| Component | Cycles | % of Total (small) | % of Total (large) |
|-----------|--------|--------------------|--------------------|
| Metadata loading overhead | ~361 | 1.6% | 0.67% |
| Compute savings (halved K iterations) | ~1000-4000 | 4.3% | 4.2% |
| Net benefit | positive | 2.7% | 3.5% |

The fixed overhead is amortized over larger problems and becomes negligible (<1%) at production sizes.

### Dense vs Sparse Summary

| Config | Dense Cycles | Sparse Cycles | Speedup |
|--------|-------------|---------------|---------|
| NT=8 m8n8k32 (int8) | 23107 | 22105 | 4.3% |
| NT=8 m16n16k64 (int8) | 46021 | 43726 | 5.0% |
| NT=32 m16n16k64 (int8) | 56257 | 53881 | 4.2% |

---

## Bug-to-Pattern Summary

| Bug | Pattern | How Discovered |
|-----|---------|---------------|
| `TCU_ITYPE_BITS` not passed to RTL build | #1 Config flag not propagated | fp16 failed; int8 passed because default matched |
| Micro-op counter not reset between K-loop iterations | #2 State not reset | fp16 needed 2 iterations; int8 needed only 1 |
| RTL built for int8, test binary built for int4 | #3 Silent data corruption | Config switch without clean build |
| NT=8 `meta_store` passed accidentally (meta_cols=0) | #4 Works for small, fails for large | NT=32 exposed: meta_cols=2 instead of 8 |
| int4 tileK in register-element units, not element units | #5 Sub-element unit confusion | int4 failed while int8/fp16 passed |
| `is_sparse` as combinational wire during multi-cycle op | Combinational instability | Code review during implementation |
