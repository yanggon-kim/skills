# First-Principles Analysis Framework

## Core Principle

Stop accepting profiler metrics at face value. Decompose every bottleneck to the most basic physical facts: memory latency (ns), bandwidth (bytes/s), compute throughput (FLOP/s), instruction dependencies.

The goal is to reason from undeniable physical constraints upward, not from surface-level symptoms downward. This is analogous to Elon Musk's "materials cost" reasoning for rockets: "A rocket is made of aluminum, titanium, copper, and carbon fiber. What is the raw material cost? ~2% of the typical price. Therefore, the rocket is ~98% optimization opportunity."

For GPU workloads: "This kernel must move X bytes and compute Y FLOPs. The hardware can deliver Z bytes/s and W FLOP/s. The physical minimum time is max(X/Z, Y/W). Everything above that minimum is optimization opportunity."

---

## The Framework (3 Steps)

### Step 1: Identify the Physical Floor

Compute the absolute minimum execution time from physics and architecture.

**For memory-bound kernels (most sparse kernels):**
```
physical_floor = total_bytes_moved / peak_memory_bandwidth
```

**For compute-bound kernels (dense GEMM, convolutions):**
```
physical_floor = total_FLOPs / peak_compute_throughput
```

**For mixed workloads:**
```
physical_floor = max(bytes / peak_BW, FLOPs / peak_compute)
```

This is the "materials cost" — the irreducible minimum that no amount of optimization can beat.

**Example — SpMV on RTX 4070 Ti SUPER:**
```
Matrix: cage15 (5.15M rows, 99.2M NNZ, CSR format)
Data to move:
  - values[]:     99.2M * 8 bytes (float64) = 793.6 MB
  - col_indices[]: 99.2M * 4 bytes (int32)  = 396.8 MB
  - row_ptr[]:    5.15M * 4 bytes (int32)   = 20.6 MB
  - x[] (input):  ~99.2M * 8 bytes (reads)  = 793.6 MB (worst case, no cache)
  - y[] (output): 5.15M * 8 bytes (float64) = 41.2 MB
  Total minimum: ~2,045 MB

Peak BW: 672 GB/s

Physical floor = 2,045 MB / 672 GB/s = 3.04 ms
```

### Step 2: Measure the Gap

Compare actual execution time to the physical floor.

```
gap = actual_time - physical_floor
gap_ratio = actual_time / physical_floor
```

- **gap_ratio < 1.5x**: Excellent — kernel is near-optimal
- **gap_ratio 1.5x-3x**: Good — moderate optimization opportunity
- **gap_ratio 3x-10x**: Significant — substantial overhead from software/configuration
- **gap_ratio > 10x**: Problem — likely a fundamental issue (wrong algorithm, misconfiguration, insufficient parallelism)

**Example — SpMV continued:**
```
Actual time (measured): 15.2 ms
Physical floor:          3.04 ms
Gap ratio:               5.0x

Interpretation: The kernel achieves only 20% of peak bandwidth.
There is 12.16 ms of "optimization opportunity."
```

### Step 3: Decompose the Gap

Identify the specific hardware/software factors that cause each portion of the gap. Use compiled evidence (PTX, SASS, ncu metrics) — not guesswork.

**Common gap factors for GPU kernels:**

| Factor | How to Detect | How to Quantify |
|--------|--------------|-----------------|
| Insufficient parallelism (grid too small) | `grid_size / num_SMs < 4` | Occupancy gap from grid saturation |
| Dependent load chains | PTX/SASS shows `LDG → IMAD → LDG` sequence | Cycles per chain × chain count |
| Poor cache utilization | ncu L2 hit rate < 50% for random access | Effective BW vs peak BW |
| Register pressure limiting occupancy | `nvcc --ptxas-options=-v` shows high reg count | Occupancy calculator: regs/thread → blocks/SM |
| Shared memory limiting occupancy | Shared mem per block close to SM limit | Occupancy calculator |
| Branch divergence | ncu warp efficiency < 80% | Divergent instructions / total instructions |
| Instruction overhead (index math) | SASS shows many IMAD/SHF before each LDG | Non-memory instructions / total instructions |
| Memory coalescing failures | ncu sectors/request > 1 | Extra transactions × latency |

**Example — SpMV gap decomposition:**
```
Total gap: 12.16 ms (5.0x above floor)

Factor 1: Grid too small (M=5.15M, block=256, grid=20,117)
  - 20,117 blocks / 66 SMs = 305 blocks/SM over kernel lifetime
  - But only ~4.6 blocks/SM active at once (register-limited)
  - Occupancy: 4.6 * 256 / 2048 = 57% → NOT the primary bottleneck
  - Contribution: ~0.5 ms

Factor 2: Dependent load chain (the primary bottleneck)
  - Inner loop in SASS: LDG col_idx[j] → IMAD.WIDE addr → LDG x[addr]
  - Each iteration serializes 2 DRAM round-trips (~400ns each)
  - With 57% occupancy → 29 warps/SM, but need ~83 to saturate BW
  - Little's Law deficit: need 83 warps, have 29 → 35% BW utilization
  - Contribution: ~8.0 ms

Factor 3: Random x[col] access (poor L2 cache hit rate)
  - col_indices are irregular → x[] access is scattered
  - L2 hit rate: 23% (measured by ncu)
  - Effective BW for x[] reads: much lower than peak
  - Contribution: ~3.66 ms
```

---

## Little's Law Application

Little's Law is the key tool for determining if a kernel is latency-bound or bandwidth-bound.

```
Required_outstanding_bytes = Peak_BW × Memory_Latency
```

**For RTX 4070 Ti SUPER:**
```
Peak BW = 672 GB/s
DRAM latency ≈ 400 ns (typical for GDDR6X)

Required outstanding bytes = 672 GB/s × 400 ns = 268,800 bytes = 262.5 KB

Per SM: 262.5 KB / 66 SMs = 3.98 KB/SM
Per warp (assuming 128-byte cache line requests):
  3,980 bytes / 128 bytes = ~31 outstanding requests per SM

With 32 threads/warp and 1 request/thread, need ~31 warps per SM
to keep one outstanding request per warp.

But memory instructions are not every instruction — if only 1 in 4
instructions is a memory op, need 31 × 4 = 124 warps/SM.
Max warps/SM = 64 (2048 threads / 32 threads per warp).

Key insight: For kernels with dependent load chains (like SpMV),
the effective memory instruction rate is low, so you need MORE
warps to saturate bandwidth.
```

**Interpretation:**
- If `actual_warps/SM ≥ required_warps/SM` → **bandwidth-bound** (saturating BW)
- If `actual_warps/SM < required_warps/SM` → **latency-bound** (not enough parallelism to hide latency)

Most sparse kernels are **latency-bound** because:
1. Dependent load chains reduce memory-level parallelism per warp
2. Irregular access patterns cause cache misses (effectively increasing latency)
3. Grid size may not provide enough warps per SM

---

## Anti-Patterns (What NOT to Do)

### Anti-Pattern 1: Surface-Level Diagnosis

**BAD**: "The kernel is slow because of register pressure"

**GOOD**: "The kernel uses 40 regs/thread, allowing max 2048/40 = 51 threads/block, which gives floor(65536/40) = 1638 threads/SM = 51 warps/SM = 100% theoretical occupancy. The register count does NOT limit occupancy. The actual occupancy limiter is grid size: the kernel launches only 164 blocks across 66 SMs = 2.5 blocks/SM. With 256 threads/block, that's only 2.5 × 256 / 2048 = 31% occupancy."

### Anti-Pattern 2: Accepting Profiler Summaries

**BAD**: "NCU says the kernel is memory-bound with 88.7% scheduler idle. We should optimize memory access."

**GOOD**: "NCU reports 88.7% scheduler idle. Following the chain: idle scheduler → not enough warps to schedule → occupancy = 31% → grid has 164 blocks / 66 SMs = 2.5 blocks/SM → grid_dim = ceil(M/block_size) = ceil(4096/128) = 32 blocks (not 164, let me recheck). Root cause: M=4096 is too small — the problem doesn't generate enough parallel work to fill the GPU."

### Anti-Pattern 3: Ignoring the Physical Floor

**BAD**: "The kernel takes 15ms, which seems slow. Let's try different block sizes."

**GOOD**: "The physical floor is 3.04ms (2,045 MB / 672 GB/s). The kernel takes 15.2ms — a 5.0x gap. Before trying random optimizations, let's decompose this 12.16ms gap to understand where the time actually goes. Block size tuning might recover 0.5ms, but the dependent load chain accounts for 8ms."

### Anti-Pattern 4: Confusing Symptoms with Causes

**BAD**: "High Long Scoreboard stalls → we need to reduce memory latency"

**GOOD**: "High Long Scoreboard stalls are a SYMPTOM. The CAUSE is that each loop iteration serializes two dependent global loads (col_idx → address → value). You cannot 'reduce memory latency' — DRAM latency is fixed by physics. You CAN increase memory-level parallelism: (a) process multiple elements per thread, (b) use vectorized loads, (c) restructure the data layout to enable coalesced access."

---

## Template: First-Principles Bottleneck Report

```markdown
### First-Principles Analysis: [Kernel/Workload Name]

**Physical Floor:**
- Data movement: [X] bytes (breakdown: ...)
- Compute: [Y] FLOPs (breakdown: ...)
- Minimum time: max([X]/peak_BW, [Y]/peak_FLOPS) = [Z] ms
- Classification: [memory-bound / compute-bound]

**Actual Performance:**
- Measured time: [A] ms
- Gap ratio: [A/Z]x
- Achieved bandwidth: [B] GB/s ([B/peak_BW]% of peak)
- Achieved compute: [C] GFLOP/s ([C/peak_GFLOPS]% of peak)

**Gap Decomposition:**

| Factor | Evidence | Contribution |
|--------|----------|-------------|
| [Factor 1] | [ncu/SASS evidence] | [X] ms ([Y]% of gap) |
| [Factor 2] | [ncu/SASS evidence] | [X] ms ([Y]% of gap) |
| [Factor 3] | [ncu/SASS evidence] | [X] ms ([Y]% of gap) |

**Little's Law Check:**
- Required warps/SM to saturate BW: [N]
- Actual warps/SM: [M]
- Verdict: [latency-bound / bandwidth-bound]

**Root Cause:** [One sentence stating the fundamental reason]
```
