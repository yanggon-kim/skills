# Root Cause Analysis for GPU Bottlenecks

## Principle: Never Stop at the First Metric

Profiler metrics are **symptoms**, not **causes**. Every surface-level observation has a deeper explanation. Follow the chain until you reach an undeniable physical or architectural fact.

---

## Symptom → Cause Chain Methodology

Ask "WHY?" at least 3-5 times, until you reach a fact that cannot be decomposed further.

**Example — SpMV on a small matrix:**
```
Symptom:   "88.7% scheduler idle"
  WHY? →   "Only 10 warps active per SM"
  WHY? →   "Grid has 164 blocks across 66 SMs = 2.5 blocks/SM"
  WHY? →   "grid_dim = ceil(M / block_size) = ceil(4096 / 128) = 32 blocks"
  WHY? →   "M = 4096 rows — the problem size is too small for the GPU"
  ROOT CAUSE: Problem size (M=4096) generates insufficient parallelism
              to fill 66 SMs. This is a PROBLEM-LEVEL constraint, not
              a kernel-level inefficiency.
```

**Example — SpMV on a large matrix with poor bandwidth:**
```
Symptom:   "Achieved bandwidth = 134 GB/s (20% of peak 672 GB/s)"
  WHY? →   "Long Scoreboard stalls dominate (83.5% of stall cycles)"
  WHY? →   "Inner loop has dependent load chain: LDG col[j] → IMAD → LDG x[col[j]]"
  WHY? →   "CSR format requires indirect indexing: column index must be
            loaded before the corresponding x[] value can be addressed"
  ROOT CAUSE: CSR's indirect access pattern serializes two DRAM round-trips
              per nonzero element, limiting memory-level parallelism. This is
              inherent to the CSR data structure, not the kernel implementation.
```

---

## Compiled Evidence Techniques

> **For systematic instruction-level analysis** (SASS extraction, annotation, dependency chain tracing, instruction-to-stall mapping), see `references/instruction-level-analysis.md`. The techniques below are quick-reference commands; the instruction-level analysis reference provides the full methodology.

### 1. Generate PTX (Virtual ISA)

Shows the instruction-level dependency chain before hardware scheduling.

```bash
# From CUDA source
nvcc -ptx -arch=sm_89 kernel.cu -o kernel.ptx

# Key things to look for in PTX:
# - ld.global (global memory loads) — are they dependent on each other?
# - mad.lo / mul.lo (address computation) — between dependent loads?
# - Chains like: ld.global → mad → ld.global = dependent load chain
```

### 2. Generate SASS (Actual Machine Instructions)

Shows what the GPU actually executes after compiler optimization.

```bash
# From compiled binary
cuobjdump -sass executable > kernel.sass

# From .cubin
cuobjdump -sass kernel.cubin > kernel.sass

# Key things to look for in SASS:
# - LDG (global load) — count them, check dependencies
# - IMAD.WIDE (address computation) — between dependent LDGs?
# - STG (global store) — coalesced or scattered?
# - @P (predicated instructions) — sign of branch divergence
# - BAR (barriers) — synchronization overhead
```

### 3. Extract Register and Shared Memory Usage

```bash
# During compilation
nvcc --ptxas-options=-v kernel.cu 2>&1

# Output shows:
# ptxas info: Used N registers, M bytes smem, K bytes cmem[0]
# These numbers determine occupancy limits
```

### 4. NCU Occupancy Analysis

```bash
# Collect occupancy-related metrics
ncu --metrics \
  sm__warps_active.avg.pct_of_peak_sustained_active,\
  launch__occupancy_limit_blocks,\
  launch__occupancy_limit_registers,\
  launch__occupancy_limit_shared_mem,\
  launch__occupancy_limit_warps,\
  launch__registers_per_thread,\
  launch__block_size,\
  launch__grid_size \
  ./executable
```

### 5. Profile Library Kernels (cuSPARSE, cuBLAS)

Library kernels often have different grid/block configurations than custom kernels.

```bash
# Profile cuSPARSE SpMV to see its launch configuration
ncu --metrics \
  launch__grid_size,\
  launch__block_size,\
  launch__registers_per_thread \
  --kernel-name regex:"csrmv|spmv" \
  python spmv_script.py
```

---

## Key Analyses to Perform

### Analysis 1: Occupancy Budget

Determine what limits occupancy — is it registers, shared memory, block size, or grid size?

```
Given:
  regs_per_thread = 40
  block_size = 256
  shared_mem_per_block = 0
  SM specs: 65536 regs, 2048 threads, 100KB shared mem, 32 max blocks

Register limit:
  threads_per_SM = floor(65536 / 40) = 1638 → 51 warps → ~99% occupancy
  blocks_per_SM = floor(65536 / (40 * 256)) = floor(65536 / 10240) = 6

Block limit:
  blocks_per_SM = min(32, floor(2048 / 256)) = min(32, 8) = 8

Shared mem limit:
  blocks_per_SM = floor(102400 / shared_mem_per_block) = unlimited (0 smem used)

Effective blocks/SM from resources: min(6, 8, unlimited) = 6
Occupancy = 6 * 256 / 2048 = 75%

BUT: Does the grid even have 6 blocks per SM?
```

### Analysis 2: Grid Saturation

Even with high theoretical occupancy, a small grid means many SMs are idle.

```
grid_size = ceil(M / block_size)
blocks_per_SM = grid_size / num_SMs

If blocks_per_SM < 1: Many SMs are completely idle
If blocks_per_SM < 4: GPU is significantly underutilized
If blocks_per_SM >= 4: Grid saturation is probably not the bottleneck
```

### Analysis 3: Little's Law (Latency vs Bandwidth Bound)

```
required_outstanding_bytes = peak_BW * DRAM_latency
required_warps_per_SM = required_outstanding_bytes / (bytes_per_request * num_SMs)

# Adjust for instruction mix (not every instruction is a memory op)
memory_instruction_fraction = memory_instructions / total_instructions
adjusted_required_warps = required_warps_per_SM / memory_instruction_fraction

if actual_warps_per_SM >= adjusted_required_warps:
    verdict = "bandwidth-bound (enough warps to hide latency)"
else:
    verdict = "latency-bound (insufficient warps to saturate bandwidth)"
    deficit = adjusted_required_warps - actual_warps_per_SM
```

### Analysis 4: Dependency Chain Length

Find the longest chain of dependent instructions in the inner loop. For the full methodology (register def-use tracing, ASCII pipeline diagrams, MLP impact), see `references/instruction-level-analysis.md` Section 5.

```
# In SASS, look for chains like:
#   LDG R4, [R2]           # Load col_index (starts DRAM request)
#   # ... ~400 cycle wait ...
#   IMAD.WIDE R6, R4, 8, R8  # Compute address from col_index
#   LDG R10, [R6]          # Load x[col_index] (another DRAM request)
#   # ... ~400 cycle wait ...
#   DFMA R12, R10, R14, R12 # Accumulate

# This chain takes ~800 cycles per iteration.
# With W warps per SM, the SM can overlap W chains.
# Throughput = W iterations / 800 cycles = W/800 iterations per cycle
# Compare to peak: 1 iteration per ~4 cycles (if fully pipelined)
```

---

## Template for Root Cause Report

```markdown
## Root Cause Analysis: [Bottleneck Name]

### Symptom
[What the profiler shows — the surface-level metric]
- Metric: [exact value from ncu/nsys]
- Observed in: [which kernel(s)]

### Evidence Chain

| Step | Observation | Evidence Source |
|------|------------|----------------|
| 1 | [Surface symptom] | ncu: [metric name] = [value] |
| 2 | [WHY?] → [deeper observation] | ncu: [metric] / SASS: [instruction] |
| 3 | [WHY?] → [deeper still] | Launch config / PTX analysis |
| 4 | [WHY?] → [root cause] | Architecture spec / data structure |

### Root Cause
[One clear statement of the fundamental cause]

### Physical Proof
[Quantitative calculation proving this is the root cause]
- Expected impact: [how much time this root cause accounts for]
- Verification: [how to verify — e.g., change parameter and re-profile]

### Actionable Implications
- [What can be changed to address this root cause]
- [What CANNOT be changed (physical limits)]
```

---

## Common Root Cause Categories

### 1. Insufficient Parallelism
- **Symptom**: Low occupancy, idle SMs, high scheduler idle %
- **Root cause**: Problem size too small, or algorithm doesn't expose enough parallelism
- **Physical fact**: GPU has N SMs × M warps/SM = N×M concurrent warps needed

### 2. Memory-Level Parallelism Limited by Data Dependencies
- **Symptom**: High Long Scoreboard stalls, low achieved bandwidth
- **Root cause**: Dependent load chains in the inner loop (e.g., indirect indexing)
- **Physical fact**: DRAM latency is ~400ns, each dependent load adds ~400ns serially

### 3. Irregular Memory Access Patterns
- **Symptom**: Low L2 cache hit rate, high sectors/request, poor coalescing
- **Root cause**: Data structure causes scattered access (e.g., CSR column indices)
- **Physical fact**: Cache line is 128 bytes; scattered access wastes most of each line

### 4. Compute-Memory Imbalance
- **Symptom**: Kernel sits far below roofline on both axes
- **Root cause**: Arithmetic intensity doesn't match hardware balance point
- **Physical fact**: Ridge point = peak_FLOPS / peak_BW determines the crossover

### 5. Launch Overhead Dominance
- **Symptom**: Kernel duration << 10us, total time dominated by launch gaps
- **Root cause**: Kernel does too little work per launch
- **Physical fact**: Kernel launch overhead is ~5-10us on modern GPUs

### 6. Synchronization / Serialization
- **Symptom**: High barrier stalls, low SM utilization despite high occupancy
- **Root cause**: Excessive `__syncthreads()` or atomic operations
- **Physical fact**: Barrier requires ALL threads in block to reach the same point
