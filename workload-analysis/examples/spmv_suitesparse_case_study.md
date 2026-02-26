# Case Study: SpMV on SuiteSparse Matrices (RTX 4070 Ti SUPER)

> Real-world SpMV profiling with the SuiteSparse Matrix Collection.
> Conducted across two rounds: first with synthetic random matrices, then with research-grade SuiteSparse matrices.
> The original analysis lives at `/home/vortex/dir_yanggon/02_SpMV_SpMM/` (directories `00_synthetic_spmv/` and `01_suitesparse_spmv/`).
> Use this as a reference when repeating the analysis on a different GPU. Adapt freely.

## Workload

**SpMV (y = A * x)**: Sparse CSR matrix times dense vector, via `torch.sparse.mm` (cuSPARSE `csrmv_v3_kernel` backend).

- Algorithm: CSR SpMV
- Data type: FP32
- Backend: PyTorch `torch.sparse.mm` which dispatches to cuSPARSE
- Kernel: `csrmv_v3_kernel` (block=128, 40 regs/thread on SuiteSparse, 48 on small synthetic)

## Benchmark Suite

**SuiteSparse Matrix Collection** (https://sparse.tamu.edu/), the standard benchmark for sparse linear algebra research.

Six matrices covering diverse domains and sparsity patterns:

| Matrix | Group | Rows | NNZ | Avg NNZ/row | Domain | Pattern |
|--------|-------|------|-----|-------------|--------|---------|
| cant | Williams | 62K | 4.0M | 64.2 | FEM cantilever | Regular banded, symmetric |
| pwtk | Boeing | 218K | 11.6M | 53.4 | Pressurized wind tunnel | Regular banded, symmetric |
| webbase-1M | Williams | 1.0M | 3.1M | 3.1 | Web graph | Power-law, highly irregular |
| ldoor | GHS_psdef | 952K | 46.5M | 48.9 | Large door structure | Regular banded, symmetric |
| circuit5M | Freescale | 5.6M | 59.5M | 10.7 | Circuit simulation | Irregular, diagonal-heavy |
| cage15 | vanHeukelum | 5.2M | 99.2M | 19.2 | DNA electrophoresis | Structured, near-diagonal |

**Why these matrices**: They span 3 orders of magnitude in size (62K-5.6M rows), cover regular (FEM) vs. irregular (web/circuit) sparsity, and are all widely cited in the literature. The contrast between regular FEM meshes and power-law web graphs is important for understanding secondary bottleneck effects.

**Download approach used** (direct HTTP, not ssgetpy — more reliable):
```bash
# Direct download from TAMU
for matrix in cant pwtk webbase-1M ldoor circuit5M cage15; do
    # Look up the group name on https://sparse.tamu.edu/ first
    wget "https://suitesparse-collection-website.herokuapp.com/MM/{GROUP}/${matrix}.tar.gz"
    tar xzf "${matrix}.tar.gz"
done
```

**Gotcha**: The herokuapp URL sometimes redirects HTTPS->HTTP on S3, causing 404. Fallback to `http://sparse-files.engr.tamu.edu/MM/{GROUP}/{name}.tar.gz` if this happens. Also verify group names (e.g., `cant` is `Williams`, not `FIDAP`).

**Loading into PyTorch**:
```python
import scipy.io, scipy.sparse, torch, numpy as np

mat = scipy.io.mmread("cage15/cage15.mtx")
csr = scipy.sparse.csr_matrix(mat)
M, N = csr.shape

# Convert to PyTorch sparse_csr_tensor on GPU (float32)
crow = torch.tensor(csr.indptr, dtype=torch.int32, device="cuda")
col = torch.tensor(csr.indices, dtype=torch.int32, device="cuda")
val = torch.tensor(csr.data.astype(np.float32), dtype=torch.float32, device="cuda")
A_gpu = torch.sparse_csr_tensor(crow, col, val, size=(M, N), device="cuda")

x = torch.randn(N, 1, dtype=torch.float32, device="cuda")
y = A_gpu @ x  # dispatches to cuSPARSE csrmv_v3_kernel
```

## How It Ran

### Profiling Pipeline

Three-stage profiling, each with its own script:

1. **Sweep timing** (`profile_suitesparse_spmv.py --mode sweep`)
   - Profiles all 6 matrices sequentially
   - 5 warmup + 20 measured iterations per matrix
   - CUDA event timing (never `time.time()`)
   - NVTX range per matrix for nsys visibility
   - Outputs: `analysis/suitesparse_spmv_results.json`

2. **nsys trace** (via `run_nsys_profile.sh`)
   ```bash
   nsys profile -o profiles/suitesparse_nsys --trace=cuda,nvtx,osrt -f true \
       python scripts/profile_suitesparse_spmv.py --mode sweep
   ```
   - Full application timeline with kernel-level visibility

3. **ncu deep dive** (via `run_ncu_profile.sh`)
   ```bash
   # Per-matrix, filtered to SpMV kernel
   ncu --set full \
       -k "regex:csrmv|csr_partition" \
       --launch-count 3 \
       --force-overwrite \
       -o profiles/suitesparse_ncu_${mat} \
       python scripts/ncu_profile_suitesparse.py --matrix ${mat}
   ```
   - Ran on 3 representative matrices: **cant** (small/regular), **webbase-1M** (irregular), **ldoor** (large/regular)
   - `ncu_profile_suitesparse.py` uses `cudaProfilerStart/Stop` to bracket one measured iteration

**Gotcha: ncu kernel name filtering**. Use `--kernel-name-base demangled` with `--kernel-name "regex:csrmv"` (not the literal C++ mangled name). Without `demangled`, kernel name matching is unreliable across CUDA versions.

**Gotcha: cuobjdump for SASS extraction**. When extracting SASS for root cause analysis, first list symbols with `cuobjdump -symbols binary.o`, then use the full mangled name with `-fun`. Don't guess the mangled name.

### Analysis & Visualization Pipeline

After profiling:

4. **Export ncu CSV** (`export_ncu_csv.sh`)
   ```bash
   ncu --import profiles/suitesparse_ncu_cant.ncu-rep --csv > profiles/suitesparse_ncu_cant.csv
   ```

5. **Parse ncu** (`parse_ncu_suitesparse.py`) — Extracts per-kernel metrics from CSV: occupancy, stalls, throughput, registers, grid size

6. **Analyze** (`analyze_suitesparse.py`) — Combines timing + ncu data, computes roofline points, classifies bottlenecks, outputs `analysis/suitesparse_analysis.json`

7. **Visualize** (3 separate plot scripts):
   - `plot_roofline_suitesparse.py` — Roofline with SuiteSparse + synthetic comparison
   - `plot_comparison.py` — Side-by-side occupancy, stalls, bandwidth vs synthetic
   - `plot_kernel_metrics.py` — Four-panel per-kernel deep dive

8. **Report** — Written manually as `analysis/report.md` combining all evidence

## Key Metrics Focused On

These are the metrics that matter most for SpMV analysis. Ordered by importance:

### Primary (determines the story)

| Metric | Why | How to Get |
|--------|-----|-----------|
| Arithmetic Intensity (FLOP/byte) | Determines memory-bound vs compute-bound classification | `2*NNZ / bytes_moved` where bytes = NNZ*(4+4) + (M+1)*4 + N*4 + M*4 for FP32/int32 |
| Effective Bandwidth (GB/s) | Shows how well you utilize memory | `bytes_moved / time` |
| % Peak Bandwidth | Normalizes across GPUs — the single most important cross-GPU comparison metric | `effective_BW / GPU_peak_BW * 100` |
| Long Scoreboard Stall % | Proves memory latency is the dominant bottleneck | ncu: `smsp__warps_issue_stalled_long_scoreboard_per_warp_active` |

### Secondary (explains the why)

| Metric | Why | How to Get |
|--------|-----|-----------|
| Achieved Occupancy | Shows if GPU has enough warps to hide latency | ncu: `sm__warps_active.avg.pct_of_peak_sustained_active` |
| Grid Size (blocks) | Determines if matrix is large enough to fill the GPU | ncu: `launch__grid_size` |
| Blocks per SM | `grid_size / num_SMs` — below 12 means underutilization | Computed |
| Registers per Thread | Sets the occupancy ceiling | ncu: `launch__registers_per_thread` |
| IPC (active) | Instruction throughput per active cycle | ncu: `smsp__inst_executed.avg.per_cycle_active` |
| L2 Hit Rate | Explains >100% DRAM BW (L2 cache effect) | ncu: `lts__t_sector_hit_rate.pct` |
| Barrier Stall % | Reveals load imbalance from irregular sparsity | ncu: `smsp__warps_issue_stalled_barrier_per_warp_active` |

### What to Watch For

- **% Peak BW > 100%**: Not an error. Means the matrix fits in L2 cache. The `bytes_moved` formula assumes all reads come from DRAM, but L2 serves them faster. Document this, don't "fix" it.
- **Occupancy near 100% but still slow**: This is the key SpMV insight. High occupancy doesn't mean high performance — the warps are all stalled on memory. Report both metrics together.
- **IPC varies with sparsity pattern**: Regular FEM meshes (cant, ldoor) get IPC 0.82-0.85. Irregular graphs (webbase-1M) drop to 0.63 due to load imbalance.

## Report Structure That Worked

The final report (`analysis/report.md`) used this structure:

1. **Executive Summary** — One paragraph: what was profiled, on what GPU, key finding in one sentence
2. **Methodology** — GPU specs table, matrix selection rationale, profiling tool chain
3. **Matrix Characteristics** — Table of all matrices with rows, NNZ, domain, pattern
4. **Performance Results** — Timing table (time, BW, GFLOPS, AI, %peakBW), NCU kernel analysis table, roofline plot
5. **Bottleneck Analysis** — Memory-bound proof, sparsity pattern effects on secondary stalls, grid size vs occupancy
6. **Comparison** (synthetic vs real) — Side-by-side table of all metrics, what changed vs what stayed the same
7. **Conclusions** — Numbered findings (7 in our case)
8. **References** — SuiteSparse citation, NVIDIA docs, roofline paper

### The Central Argument

The strongest finding from this analysis was distinguishing **two failure modes** of SpMV:

- **Small matrices (synthetic)**: GPU is **idle** — 88.7% of scheduler cycles have no eligible warp, because the grid (164 blocks / 66 SMs) doesn't fill the SMs. The bottleneck appears to be parallelism.
- **Large matrices (SuiteSparse)**: GPU is **fully occupied but stalled** — 93-98% occupancy, but 74-84% of active cycles are long scoreboard stalls. The bottleneck is the dependent load chain.

Both are memory-latency-driven, but the expressions are completely different. The dependent load chain `col_indices[j] -> x[col_indices[j]]` (proven via PTX/SASS extraction) persists regardless of matrix size.

### Implications for DAE (the research angle)

- At 89-96% bandwidth utilization, SpMV on current GPUs (RTX 4070 Ti SUPER, 672 GB/s) is **bandwidth-bound** — DAE won't help here because the pipe is already full
- On future GPUs with higher BW (B200: 8 TB/s), Little's Law analysis shows SpMV becomes **latency-bound** (not enough outstanding requests to saturate BW) — DAE becomes valuable
- Little's Law: `required_outstanding_bytes = peak_BW * DRAM_latency`. At 8 TB/s and ~400ns, the GPU needs ~3.2 GB in flight — more than current warp counts can generate

## Adapting for a Different GPU

When re-running this analysis on H100/A100/B200:

1. **Update GPU specs** in the profiling script: `GPU_PEAK_BW_GBs` and `GPU_PEAK_FP32_TFLOPS`
2. **The same matrices should work** — they're GPU-agnostic. The largest (cage15: 99.2M NNZ) needs ~1.2 GB, well within any datacenter GPU's memory
3. **Expect different occupancy/stall profiles** — different SM counts, register files, L2 cache sizes will shift secondary metrics
4. **The primary finding (memory-bound, long scoreboard) will likely persist** — the dependent load chain is algorithmic, not hardware-specific
5. **% Peak BW is the key cross-GPU comparison** — normalize all bandwidth numbers to each GPU's peak
6. **Run Little's Law analysis** with the new GPU's specs to determine if the workload is bandwidth-bound or latency-bound on that architecture
7. **ncu command syntax may differ** across CUDA toolkit versions — always verify `ncu --version` and check that kernel name filtering works

### GPU Specs for Comparison

| GPU | SMs | Peak BW (GB/s) | Peak FP32 (TFLOPS) | L2 Cache | Notes |
|-----|-----|----------------|---------------------|----------|-------|
| RTX 4070 Ti SUPER | 66 | 672 | 22.0 | 48 MB | Ada Lovelace, CC 8.9 |
| A100 SXM | 108 | 2,039 | 19.5 | 40 MB | Ampere, CC 8.0 |
| H100 SXM | 132 | 3,350 | 67.0 | 50 MB | Hopper, CC 9.0 |
| H200 SXM | 132 | 4,800 | 67.0 | 50 MB | Hopper + HBM3e |
| B200 SXM | 192 | 8,000 | 180.0 | 128 MB | Blackwell, CC 10.0 |

### Little's Law Quick Check

```python
def check_latency_vs_bw_bound(peak_bw_gbs, num_sms, max_warps_per_sm=48,
                                bytes_per_warp_request=128, dram_latency_ns=400):
    """Quick check: can this GPU saturate its BW with warp-level parallelism?"""
    required_bytes_in_flight = peak_bw_gbs * 1e9 * dram_latency_ns * 1e-9
    max_bytes_in_flight = num_sms * max_warps_per_sm * bytes_per_warp_request
    saturation_ratio = max_bytes_in_flight / required_bytes_in_flight
    return {
        "required_bytes_in_flight_MB": required_bytes_in_flight / 1e6,
        "max_bytes_in_flight_MB": max_bytes_in_flight / 1e6,
        "saturation_ratio": round(saturation_ratio, 2),
        "regime": "bandwidth-bound" if saturation_ratio >= 1.0 else "latency-bound",
    }

# Examples:
# RTX 4070 Ti SUPER: ratio=1.50 -> bandwidth-bound
# A100:              ratio=1.34 -> bandwidth-bound (barely)
# H100:              ratio=1.21 -> bandwidth-bound (marginal)
# B200:              ratio=0.58 -> LATENCY-BOUND (DAE helps here!)
```

## Scripts Inventory

All scripts at `01_suitesparse_spmv/scripts/`:

| Script | Purpose | Key Details |
|--------|---------|-------------|
| `profile_suitesparse_spmv.py` | Main timing profiler | CUDATimer, sweep/single modes, 5 warmup + 20 measured |
| `ncu_profile_suitesparse.py` | NCU-targeted profiling | cudaProfilerStart/Stop, 1 measured iteration |
| `validate_matrices.py` | Verify downloaded matrices | Check dimensions, NNZ, dtype after download |
| `parse_ncu_suitesparse.py` | Parse NCU CSV output | Extracts occupancy, stalls, throughput per kernel |
| `analyze_suitesparse.py` | Comprehensive analysis | Combines timing + ncu, roofline points, classification |
| `plot_roofline_suitesparse.py` | Roofline plot | Includes comparison with synthetic data |
| `plot_comparison.py` | Cross-study comparison plots | Occupancy, stalls, bandwidth: SuiteSparse vs synthetic |
| `plot_kernel_metrics.py` | Four-panel kernel metrics | Grid size, occupancy, stalls, throughput per matrix |
| `run_nsys_profile.sh` | nsys wrapper | Traces cuda,nvtx,osrt |
| `run_ncu_profile.sh` | ncu wrapper | `--set full`, regex kernel filter, per-matrix |
| `export_ncu_csv.sh` | Export ncu-rep to CSV | For programmatic parsing |
