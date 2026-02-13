# Case Study: GR00T N1.6 VLA Model Profiling

> This is a real example of the workload analysis skill applied to a Vision-Language-Action (VLA) model.
> The full project is at `/home/vortex/dir_yanggon/01_VLA/`.
> Use this as a reference for how a complete profiling session looks end-to-end.

## Workload

**NVIDIA GR00T N1.6** — a 3.3B parameter VLA model for robot control.

Architecture:
- **Backbone**: Eagle 2.5 VLM (~3B params) — processes images + language
- **Action Head**: DiT (Diffusion Transformer, ~300M params) — generates robot actions via iterative denoising

Inference flow: Image + Language -> Backbone -> VLM embeddings -> DiT (4 denoising steps) -> Robot actions

## Environment Setup

```
Python 3.10.12
PyTorch 2.7.1 (CUDA 13.0)
flash-attn 2.7.4.post1
transformers 4.51.3
GPU: RTX 4070 Ti SUPER (16 GB, Ada Lovelace)
```

Key dependency pain point: `flash-attn` required `pip install wheel` first, then `pip install flash-attn==2.7.4.post1 --no-build-isolation`.

## Architecture Analysis Results

| Component | Parameters | Memory (BF16) |
|-----------|-----------|---------------|
| Backbone (Eagle VLM) | 3,042M | ~5.7 GB |
| Action Head (DiT) | 319M | ~0.6 GB |
| TOTAL | 3,361M | ~6.3 GB |

DiT dimensions: 1536 hidden dim, 32 attention heads x 48 head dim, 32 transformer layers, 4 denoising steps.

## Profiling Results (Batch Size = 1)

### Phase Breakdown

| Phase | Time (ms) | % of Total |
|-------|----------|------------|
| Backbone (Eagle VLM) | 19.0 | 35% |
| DiT denoising (4 steps) | 34.6 | 64% |
| Input preparation | 0.6 | 1% |
| Feature encoding | 0.13 | <1% |
| **TOTAL** | **54.3** | **100%** |

Each DiT denoising step: ~8.5 ms (uniform across all 4 steps).

### Batch Size Scaling

| Batch | Total (ms) | Backbone | DiT | Peak Memory |
|-------|-----------|----------|-----|-------------|
| 1 | 54.3 | 19.0 | 34.6 | 7,200 MB |
| 2 | 61.9 | 26.2 | 34.8 | 7,800 MB |
| 4 | 85.9 | 39.1 | 45.6 | 9,100 MB |
| 8 | 139.7 | 67.5 | 70.4 | 11,800 MB |

Key finding: DiT latency barely changes from BS=1 to BS=2 (34.6 -> 34.8 ms), proving it's severely underutilizing the GPU.

### NCU Deep Analysis (DiT Denoising Step 0)

| Metric | Weighted Average |
|--------|-----------------|
| SM Throughput | 12.4% |
| Memory Throughput | 23.1% |
| Achieved Occupancy | 8.2% |
| Theoretical Occupancy | 50.0% |
| Warps/SM | 3.9 (max: 48) |
| L2 Hit Rate | 72.3% |

**Bottleneck classification**: 63.6% of GPU time is in MEMORY-BOUND kernels.

### Kernel Category Breakdown

| Category | % of GPU Time |
|----------|--------------|
| GEMM/MatMul | 69.3% |
| Elementwise | 15.9% |
| Flash Attention | 2.4% |
| LayerNorm | 3.5% |
| Other | 8.9% |

### Warp Stall Analysis

| Stall Reason | Weighted % |
|-------------|-----------|
| Long Scoreboard (memory) | 28.5% |
| Wait | 18.3% |
| Not Selected | 15.2% |
| Short Scoreboard (compute) | 12.1% |
| Math Pipe Throttle | 8.7% |

## Root Cause Analysis

1. **Very short sequence length** (51 tokens = 1 state + 16 action + 34 VLM context) makes GEMM matrices too small to fill the GPU's 66 SMs
2. **Weight-dominated memory access** — at batch=1, each DiT step reads ~600 MB of weights but processes only ~100 KB of activations
3. **High kernel launch overhead** — 739 kernels per denoising step, avg 9.8 us each, with ~5 us launch overhead per kernel = 51% of compute time wasted
4. **Low occupancy** — 8.2% achieved vs 50% theoretical, because small matrices don't generate enough warps

## Key Visualizations Generated

All at `/home/vortex/dir_yanggon/01_VLA/analysis/`:
- `groot_roofline.png` — Roofline plot showing all phases below the roofline
- `groot_timeline.png` — Execution timeline, SM utilization, batch scaling
- `groot_kernel_breakdown.png` — Kernel category pie chart + duration distribution
- `groot_bottleneck_analysis.md` — Full written analysis

## Scripts Used

All at `/home/vortex/dir_yanggon/01_VLA/scripts/`:
- `profile_groot.py` — Main profiling script (modes: single-step, batch-sweep, temporal, arch-analysis)
- `ncu_profile_groot.py` — NCU-targeted profiling with NVTX markers
- `parse_ncu_results.py` — NCU CSV parser with kernel categorization
- `parse_ncu_detailed.py` — Detailed occupancy, stalls, GEMM/attention breakdown
- `plot_roofline.py` — Roofline plot with all VLA phases
- `plot_timeline.py` — Timeline, SM utilization, batch comparison, kernel breakdown
- `run_nsys_profile.sh` — nsys wrapper (modes: single, temporal, batch)
- `run_ncu_profile.sh` — ncu wrapper (modes: all, backbone, dit, denoise_step)
