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
