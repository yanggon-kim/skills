# Reference Example: Adding DAE Scoreboard Bypass to GPGPU-Sim

This document captures lessons from implementing Decoupled Access-Execute (DAE) scoreboard bypass in GPGPU-Sim, a cycle-level GPU simulator. It serves as a concrete reference for the general skill in `../SKILL.md`, complementing the Vortex sparse TCU example with a **software simulator** perspective (vs. RTL hardware).

## Feature Summary

**What:** Add a per-warp DAE scoreboard bypass mechanism that allows warps to continue issuing instructions past load-dependency stalls, overlapping dependent memory accesses that would otherwise serialize. This models a hardware DAE unit where an Access Processor (AP) runs ahead of the Execute Processor (EP).

**Layers touched:** Cycle-level simulator only (6 C++ source files), plus benchmark configs and test programs.

**Key insight:** GPGPU-Sim's functional model executes loads at issue time and writes correct values to the register file immediately. The scoreboard/timing model only tracks *when* data becomes available. Therefore, bypassing the scoreboard is both correct (functional values already available) and simple (no shadow registers needed).

---

## Phase 1: Explore — Key Discoveries

### Simulator Architecture (Relevant Subsystems)

| Subsystem | Files | Role |
|-----------|-------|------|
| Scheduler | `shader.cc` (scheduler_unit::cycle) | Issues instructions from warps, checks scoreboard |
| Scoreboard | `scoreboard.{h,cc}` | Tracks pending register writes, detects RAW/WAW hazards |
| Memory pipeline | `shader.cc` (ldst_unit) | Handles load/store execution, cache access, writeback |
| Instruction model | `abstract_hardware_model.h` | warp_inst_t class with registers, opcodes, flags |
| Config | `gpu-sim.cc` | Runtime option registration and parsing |

### Critical Discovery: Static Instruction Templates

GPGPU-Sim decodes PTX instructions once and stores them as **static templates** — one instance per unique PC. The scheduler receives `const warp_inst_t*` pointers to these templates. When an instruction is issued, it is **copied** to a pipeline register (`**pipe_reg = *next_inst`). Only the pipeline register copy is per-instance; the template is shared across all warps, all threads, all time.

This means: **never modify fields on the template pointer.** Any modification via `const_cast` permanently alters the template for all future executions. Per-instance flags must be set on the pipeline register copy after the copy is made.

### Critical Discovery: Three Load Completion Paths

Loads in GPGPU-Sim can complete through three different code paths:

1. **Normal writeback** (`ldst_unit::writeback()`, via `m_next_wb`) — most common path
2. **L1 cache hit shortcut** — loads that hit in the L1 latency queue complete without going through the full writeback
3. **Dispatch register fast-complete** — loads that complete immediately (e.g., hits in already-available cache lines) at dispatch time

Any per-load accounting (counters, flags, reference counts) must be handled on ALL three paths. Missing any one causes resource leaks.

### Critical Discovery: Memory Sub-Access Splitting

A single load instruction generates multiple memory sub-accesses (one per cache line touched by the warp's active threads). Each sub-access returns independently. GPGPU-Sim tracks this with `m_pending_writes` — a reference count that decrements per sub-access and triggers "instruction complete" when it reaches zero.

Per-instruction accounting must trigger on the "instruction complete" event, NOT on each sub-access return.

---

## Phase 3: Plan — Implementation Strategy

### Step Decomposition

| Step | What | Verification |
|------|------|-------------|
| 1. Config flags | Add `-gpgpu_dae_enabled`, `-gpgpu_dae_fifo_depth` | Build succeeds |
| 2. Scoreboard state | Per-warp DAE load counter, bypass eligibility | Build succeeds |
| 3. Instruction flag | `m_dae_bypassed` on `warp_inst_t` | Build succeeds |
| 4. Scheduler bypass | Bypass scoreboard when collision is on long-op registers | vectorAdd unchanged |
| 5. Writeback tracking | Decrement DAE counter on load completion | No assertion failures |
| 6. Statistics | `gpgpu_dae_bypasses_total/loads` | Stats print correctly |
| 7. Benchmark configs | QV100/B200-like with DAE on/off | Configs parse without error |
| 8. Baseline regression | DAE=off cycles match pre-modification | Exact cycle match |
| 9. DAE benchmarks | SpMV and streaming with DAE on | Speedup observed |
| 10. Results | Document and analyze | Report written |

### Key Design Decision: Where to Set `m_dae_bypassed`

The `dae_bypassed` flag must be per-instance (per pipeline register copy), not per-template. This means the flag cannot be set on the `const warp_inst_t* pI` pointer in the scheduler — it must be set AFTER the instruction is copied to the pipeline register in `issue_warp()`.

Solution: Add `bool dae_bypassed = false` parameter to `issue_warp()`. Inside `issue_warp()`, after `**pipe_reg = *next_inst`, set `(*pipe_reg)->m_dae_bypassed = dae_bypassed`.

---

## Phase 4: Implement — Bugs Encountered

### Bug 1: WAW Assertion in `reserveRegister` (Pattern 9: Bypass Creates New Hazards)

**Symptom:** `abort()` in `Scoreboard::reserveRegister()` — "Error: trying to reserve an already reserved register."

**Root cause:** The scoreboard bypass allows a new loop iteration to issue a load to register R5 while a previous iteration's load to R5 is still pending. The scoreboard's `reserveRegister` asserts that R5 is not already in the reserved set.

**Discovery:** First run with DAE enabled on SpMV. Crash within ~100 cycles.

**Fix:** When `gpgpu_dae_enabled`, skip the insert and return early instead of aborting. Safe because `m_pending_writes` reference counting in `ldst_unit` handles writeback correctness independently of the scoreboard's set membership.

```cpp
void Scoreboard::reserveRegister(unsigned wid, unsigned regnum) {
  if (reg_table[wid].find(regnum) != reg_table[wid].end()) {
    if (m_config->gpgpu_dae_enabled) {
      return;  // WAW expected with DAE bypass
    }
    abort();  // Original assertion for non-DAE mode
  }
  reg_table[wid].insert(regnum);
}
```

**Pattern:** Before bypassing a safety mechanism, enumerate every hazard it prevents and add explicit handling.

### Bug 2: Static Instruction Template Corruption (Pattern 6: Shared/Static Object Mutation)

**Symptom:** After a few hundred cycles, ALL instructions (not just DAE-bypassed ones) had `m_dae_bypassed = true`. DAE statistics counted millions of bypasses when only thousands should occur.

**Root cause:** The original code set `const_cast<warp_inst_t*>(pI)->m_dae_bypassed = true` in the scheduler. But `pI` points to the static decoded PTX instruction template shared across all uses of that PC. Setting the flag on the template permanently marked that instruction as DAE-bypassed for ALL future executions.

**Discovery:** DAE bypass statistics were orders of magnitude too high. Tracing revealed the flag was set on instructions that never went through the DAE code path.

**Fix:** Removed `const_cast`. Added `bool dae_bypassed = false` parameter to `issue_warp()`. The flag is set on the pipeline register copy inside `issue_warp()` after `**pipe_reg = *next_inst`. Updated all 7 call sites to pass the `dae_bypass` variable.

**Pattern:** The `const` qualifier on a pointer is a warning sign — the pointed-to object is likely shared. Never circumvent it with `const_cast` for per-instance state.

### Bug 3: Unbalanced `daeDecrementLoad` (Patterns 7+8: Multiple Release Paths + One-to-Many Mapping)

**Symptom:** `assert(m_dae_load_count[wid] > 0)` failed in `daeDecrementLoad` — the counter went below zero.

**Root cause (One-to-Many):** The initial fix placed `daeDecrementLoad` at the top of `ldst_unit::writeback()`, which runs per memory sub-access. A single load instruction generates multiple sub-accesses, each triggering a decrement — but only one increment was done at issue time.

**Fix (One-to-Many):** Moved `daeDecrementLoad` inside the `if (insn_completed)` block, which fires only when ALL sub-accesses for the instruction have completed (`m_pending_writes` reaches 0).

**Root cause (Multiple Paths):** Even after fixing the one-to-many issue, loads completing through the L1 cache hit path and the dispatch_reg fast-complete path were missing decrements.

**Fix (Multiple Paths):** Added `daeDecrementLoad` calls on all three completion paths:
1. `ldst_unit::writeback()` inside `if (insn_completed)` — normal path
2. L1 cache hit path — after `l1_insn_completed` tracking
3. `dispatch_reg` fast-complete — after `warp_inst_complete()`

**Pattern:** Two patterns compounded: (1) per-sub-access vs. per-instruction confusion, (2) three separate completion paths for the same resource.

---

## Phase 5: Verify — Code Review Findings

After all runtime bugs were fixed, a code review caught additional issues:

### Review Fix 1: `pendingOnLongOp` Correctness

**Original:** Returned `true` if ANY colliding register was a long-op (memory load).

**Problem:** Unsafe for instructions with mixed dependencies — some registers pending on loads, others pending on ALU operations. Bypassing for a mixed case means the ALU-dependent input hasn't been computed yet.

**Fix:** Changed to return `true` only if ALL colliding registers are in `longopregs`. If any collision is NOT a long-op, returns `false` (unsafe to bypass).

### Review Fix 2: Missing Decrement Paths (caught statically)

The code review identified the L1 hit and dispatch_reg paths as missing `daeDecrementLoad` before a runtime failure exposed them. This validates the "list ALL completion paths" principle from the patterns catalog.

---

## Phase 6: Performance — Results and Analysis

### Benchmark Results (SpMV, CSR format, 2048 rows, 32 NNZ/row)

| Config | Baseline (cycles) | DAE (cycles) | Speedup | Scoreboard Stall Reduction |
|--------|-------------------|-------------|---------|---------------------------|
| QV100 (80 SMs, 32 ch) | 27,695 | 26,651 | 1.039x | 96.7% (687,486 → 22,469) |
| B200-like (80 SMs, 16 ch) | 29,168 | 26,688 | 1.093x | 96.9% (731,803 → 22,469) |

### Bottleneck Shift Analysis

| Stall Type | QV100 Baseline | QV100 + DAE | Change |
|-----------|---------------|-------------|--------|
| Scoreboard stalls | 687,486 | 22,469 | **-96.7%** |
| Pipeline stalls | 5,618 | 633,840 | **+11,282%** |
| Idle cycles | 11,420 | 15,095 | +32% |
| **Total cycles** | **27,695** | **26,651** | **-3.8%** |

DAE eliminates 97% of scoreboard stalls but only reduces total cycles by 3.8-9.3%. The stall breakdown reveals why: scoreboard stalls convert to pipeline stalls. The memory subsystem (L1D cache ports, MSHRs, interconnect) cannot absorb the increased request rate from DAE. Instructions stall waiting for pipeline resources instead of waiting for data dependencies.

**Implication:** The scoreboard bypass is effective — it does its job. But the benefit is capped by memory subsystem bandwidth. A real DAE hardware implementation would need larger MSHR budgets, higher L1D cache bandwidth, or dedicated DAE cache ports to realize the full theoretical speedup.

### Parameter Sensitivity Sweep (FIFO Depth)

| FIFO Depth | QV100 Cycles | B200-like Cycles |
|-----------|-------------|-----------------|
| 2 | 26,651 | 26,612 |
| 4 | 26,651 | 26,688 |
| 8 | 26,651 | 26,688 |
| 16 | 26,651 | 26,688 |
| 32 | 26,651 | 26,688 |

**Completely flat.** The FIFO depth parameter has zero impact because the memory subsystem throttles DAE load issuance long before the FIFO fills. Only 8 load bypasses occur on QV100 (vs. minimum FIFO depth of 2).

**Hardware design implication:** A FIFO depth of 2-4 entries per warp is sufficient for this workload, requiring ~256-512 bytes SRAM per SM — vs. 16 KB proposed in the architecture report for depth=32. The flat curve proves that memory subsystem bandwidth, not FIFO capacity, is the binding constraint.

### Connection to Architecture Report Predictions

The architecture report predicted 1.8-2.4x speedup assuming:
1. Perfect AP/EP overlap
2. No memory subsystem contention

The simulation achieved 1.04-1.09x, revealing that assumption (2) is the primary limiter. The 3.9-9.3% speedup represents the benefit achievable with the *existing* memory subsystem — a lower bound on DAE benefit.

---

## Bug-to-Pattern Summary

| Bug | Pattern | Key Lesson |
|-----|---------|------------|
| WAW assertion in reserveRegister | #9: Bypass creates new hazards | Enumerate all hazards a mechanism prevents before bypassing it |
| Static instruction template corruption | #6: Shared/static object mutation | Never modify through `const` pointers; set flags on copies |
| Over-decrement from sub-accesses | #8: One-to-many operation mapping | Place accounting at "operation complete", not per-sub-operation |
| Missing decrements on L1/dispatch paths | #7: Multiple resource release paths | Search for ALL completion paths; review catches what testing misses |
| pendingOnLongOp ANY→ALL logic error | (Design review) | "Any" vs "all" semantics matter for safety checks |
