# [WORKLOAD NAME] — GPU Workload Analysis Report

**Date**: YYYY-MM-DD
**GPU**: [GPU name, VRAM, architecture]
**Workload**: [Brief description]
**Framework**: PyTorch [version], CUDA [version]

---

## 1. Executive Summary

[1-2 paragraph summary of key findings. State the main bottleneck, root cause, and top optimization opportunity.]

---

## 2. Workload Description

- **What it does**: [Brief algorithm description]
- **Model size**: [Parameter count, weight memory]
- **Computational phases**: [List the major phases]
- **Input format**: [Input shapes, dtypes]

---

## 3. Environment

| Component | Version |
|-----------|---------|
| Python | |
| PyTorch | |
| CUDA (nvcc) | |
| GPU | |
| Driver | |
| Key packages | |

---

## 4. Architecture Analysis

### Parameter Breakdown

| Component | Parameters | Memory (BF16) |
|-----------|-----------|---------------|
| [Phase 1] | | |
| [Phase 2] | | |
| **TOTAL** | | |

### FLOPS Estimate

- Total FLOPs per inference: [X GFLOP]
- Arithmetic intensity: [X FLOP/byte]
- GPU ridge point: [X FLOP/byte]
- Classification: [MEMORY-BOUND / COMPUTE-BOUND]

---

## 5. Profiling Results

### Phase Breakdown (Batch Size = 1)

| Phase | Avg Time (ms) | Std (ms) | % of Total |
|-------|--------------|----------|------------|
| [Phase 1] | | | |
| [Phase 2] | | | |
| **TOTAL** | | | |

### Batch Size Scaling

| Batch | Total (ms) | [Phase 1] (ms) | [Phase 2] (ms) | Peak Memory (MB) |
|-------|-----------|----------------|----------------|-------------------|
| 1 | | | | |
| 2 | | | | |
| 4 | | | | |
| 8 | | | | |

---

## 6. Kernel Analysis (from NCU)

### Top 10 Kernels by GPU Time

| # | Kernel | Category | Duration | SM% | Mem% | Occupancy |
|---|--------|----------|----------|-----|------|-----------|
| 1 | | | | | | |

### Kernel Category Distribution

| Category | Count | % of GPU Time |
|----------|-------|--------------|
| GEMM/MatMul | | |
| Flash Attention | | |
| Elementwise | | |
| LayerNorm | | |
| Other | | |

### Bottleneck Classification

| Classification | % of GPU Time |
|---------------|--------------|
| Memory-bound | |
| Compute-bound | |
| Balanced | |

### Warp Stall Analysis

| Stall Reason | Weighted % |
|-------------|-----------|
| Long Scoreboard (memory) | |
| Short Scoreboard (compute) | |
| Wait | |
| Not Selected | |
| Barrier | |
| Math Pipe Throttle | |

---

## 6.5. Instruction-Level Analysis

### Kernel Identification

| Kernel | Symbol | Registers/Thread | Shared Mem | Grid Size | Block Size |
|--------|--------|------------------:|-----------:|----------:|-----------:|
| [Bottleneck kernel] | [demangled name] | | | | |

### Annotated SASS (Hot Loop)

```
// === Hot Loop: addresses 0xNNNN - 0xNNNN ===
// [Paste annotated SASS here with inline comments explaining each instruction]
// Example:
// /*0150*/  LDG.E R6, [R10] ;           // Load col_indices[j] → DRAM ~400 cycles
// /*0160*/  IMAD.WIDE R12, R6, 0x4, R8 ; // addr = base + col_idx * 4 (waits for R6)
// /*0170*/  LDG.E R14, [R12] ;           // Load x[col_indices[j]] → DRAM ~400 cycles (DEPENDENT)
// /*0180*/  FFMA R16, R14, R18, R16 ;    // acc += val * x[col] (waits for R14)
```

### Dependency Chain

```
[ASCII pipeline diagram showing critical path through the hot loop]

Cycle:  0    100   200   300   400   500   600   700   800
        |-----|-----|-----|-----|-----|-----|-----|-----|
Warp:   [LDG col[j].............]
                                 [IMAD addr]
                                  [LDG x[col[j]]............]
                                                            [FFMA]
Critical path: ~NNN cycles per iteration (N serial DRAM round-trips)
```

### Instruction-to-Stall Mapping

| SASS Instruction (Hot Loop) | NCU Stall Category | Contribution | Mechanism |
|----------------------------|--------------------:|-------------|-----------|
| `LDG.E Rn, [Rm]` (1st load) | Long Scoreboard | [X]% | DRAM latency ~400 cycles |
| `LDG.E Rn, [Rm]` (dependent) | Long Scoreboard | [Y]% | Serialized after address computation |
| `SHFL.BFLY Rn, Rm, ...` | Short Scoreboard | [Z]% | Cross-lane latency ~20 cycles |
| `IMAD.WIDE / LEA` | Wait | [W]% | Waiting for source register from LDG |

### Instruction Mix

| Instruction Class | Count | % of Hot Loop | Examples |
|------------------|------:|-------------:|---------|
| Global Load | | | LDG.E |
| Global Store | | | STG.E |
| FP Arithmetic | | | FFMA, FADD |
| Int Arithmetic | | | IMAD, IADD3, LEA |
| Warp Shuffle | | | SHFL.BFLY |
| Control Flow | | | BRA, ISETP, @P |
| Other | | | S2R, MOV, NOP |
| **Total** | | **100%** | |

Compute-to-memory ratio: [X] (compute ops / memory ops)

---

## 7. Roofline Analysis

![Roofline Plot](roofline.png)

[Describe where each phase sits on the roofline. Is it memory-bound or compute-bound? How far below the roofline?]

---

## 8. Root Cause Analysis (First-Principles)

### Bottleneck 1: [Name]

**Symptom → Cause Chain:**
```
[Surface metric] → WHY? → [deeper observation] → WHY? → [deeper still] → WHY? → [root cause]
```

| Step | Observation | Evidence Source |
|------|------------|----------------|
| 1 | [Surface symptom] | ncu: [metric] = [value] |
| 2 | [WHY?] → [deeper] | ncu: [metric] / SASS: [instruction] |
| 3 | [WHY?] → [deeper] | Launch config / architecture spec |
| 4 | [WHY?] → [root cause] | Physical constraint / data structure |

- **Root cause**: [One clear statement of the fundamental cause]
- **Physical proof**: [Quantitative calculation proving this is the root cause]
- **Impact**: [How much time it costs, what fraction of the gap]

### Bottleneck 2: [Name]

**Symptom → Cause Chain:**
```
[Surface metric] → WHY? → ... → [root cause]
```

- **Root cause**: [Why this bottleneck exists]
- **Physical proof**: [Quantitative evidence]
- **Impact**: [How much time it costs]

---

## 8.5. First-Principles Gap Analysis

### Physical Floor (Theoretical Minimum)

| Component | Value | Calculation |
|-----------|-------|-------------|
| Total data movement | [X] MB | [breakdown of arrays/tensors] |
| Total compute | [Y] GFLOP | [breakdown of operations] |
| Memory floor | [A] ms | [X] MB / [peak_BW] GB/s |
| Compute floor | [B] ms | [Y] GFLOP / [peak_TFLOPS] TFLOPS |
| **Physical floor** | **[max(A,B)] ms** | **[memory-bound / compute-bound]** |

### Gap Measurement

| Metric | Value |
|--------|-------|
| Physical floor | [Z] ms |
| Actual measured time | [W] ms |
| Gap | [W-Z] ms |
| Gap ratio | [W/Z]x |
| Hardware efficiency | [Z/W × 100]% |

### Gap Decomposition

| Factor | Evidence | Contribution | % of Gap |
|--------|----------|-------------|----------|
| [Factor 1: e.g., Insufficient parallelism] | [ncu/SASS evidence] | [X] ms | [Y]% |
| [Factor 2: e.g., Dependent load chain] | [ncu/SASS evidence] | [X] ms | [Y]% |
| [Factor 3: e.g., Poor cache utilization] | [ncu/SASS evidence] | [X] ms | [Y]% |
| **Total accounted** | | **[sum] ms** | **[sum]%** |

### Little's Law Check

- Required warps/SM to saturate BW: [N] (= peak_BW × DRAM_latency / bytes_per_req / num_SMs)
- Actual warps/SM: [M]
- Verdict: **[latency-bound / bandwidth-bound]**

---

## 9. Proposed Optimizations

| # | Optimization | Expected Impact | Difficulty | Details |
|---|-------------|----------------|------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## 9.5. Benchmark Credibility

### Benchmark Suite Used

- **Suite**: [e.g., SuiteSparse Matrix Collection]
- **Specific datasets**: [e.g., cage15, ldoor, webbase-1M]
- **Why this suite**: [e.g., Industry standard for sparse linear algebra, widely cited in published SpMV research]
- **Download method**: [e.g., `ssgetpy.search(name='cage15')` — see scripts/download_benchmarks.py]

### Citation

```bibtex
[BibTeX entry for the benchmark suite]
```

### Comparison to Published Literature

| Metric | This Analysis | [Published Paper 1] | [Published Paper 2] |
|--------|--------------|--------------------|--------------------|
| [Key metric 1] | [value] | [value] | [value] |
| [Key metric 2] | [value] | [value] | [value] |

[Note any differences in hardware, configuration, or methodology that affect comparison]

---

## 10. Visualizations

- Roofline plot: `analysis/[name]_roofline.png`
- Execution timeline: `analysis/[name]_timeline.png`
- Kernel breakdown: `analysis/[name]_kernel_breakdown.png`

---

## 11. Raw Data

- Timing results: `analysis/profiling_results_*.json`
- NCU analysis: `analysis/ncu_analysis_*.json`
- NCU detailed: `analysis/ncu_detailed_*.json`
- Chrome traces: `traces/trace_bs*.json`
- Kernel tables: `analysis/kernel_summary_bs*.txt`
