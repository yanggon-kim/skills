# Analysis & Visualization

## 0. First-Principles Analysis Framework

Before diving into profiling data, establish the physical baseline.

### Physical Floor Calculation

Compute the absolute minimum execution time from hardware constraints:

```python
def compute_physical_floor(total_bytes, total_flops, peak_bw_gbs, peak_tflops):
    """
    Compute the theoretical minimum execution time.

    This is the "materials cost" — no optimization can beat this.

    Args:
        total_bytes: Total data that MUST be moved (bytes)
        total_flops: Total compute that MUST be done (FLOPs)
        peak_bw_gbs: Peak memory bandwidth (GB/s)
        peak_tflops: Peak compute throughput (TFLOPS)

    Returns:
        dict with floor times and classification
    """
    mem_floor_ms = (total_bytes / 1e9) / peak_bw_gbs * 1000
    compute_floor_ms = (total_flops / 1e12) / peak_tflops * 1000
    physical_floor_ms = max(mem_floor_ms, compute_floor_ms)

    classification = "memory-bound" if mem_floor_ms > compute_floor_ms else "compute-bound"

    return {
        "memory_floor_ms": mem_floor_ms,
        "compute_floor_ms": compute_floor_ms,
        "physical_floor_ms": physical_floor_ms,
        "classification": classification,
        "arithmetic_intensity": total_flops / total_bytes,
    }
```

### Gap Decomposition

After profiling, measure how far the actual execution is from the floor:

```python
def analyze_gap(actual_ms, physical_floor_ms):
    """
    Quantify the optimization opportunity.

    gap_ratio < 1.5x: Near-optimal
    gap_ratio 1.5-3x: Moderate opportunity
    gap_ratio 3-10x: Significant overhead
    gap_ratio > 10x: Fundamental issue
    """
    gap_ms = actual_ms - physical_floor_ms
    gap_ratio = actual_ms / physical_floor_ms
    efficiency = physical_floor_ms / actual_ms * 100

    return {
        "gap_ms": gap_ms,
        "gap_ratio": gap_ratio,
        "efficiency_pct": efficiency,
    }
```

### Little's Law Application

Determine if a kernel is latency-bound or bandwidth-bound:

```python
def littles_law_check(peak_bw_gbs, dram_latency_ns, bytes_per_request,
                      num_sms, actual_warps_per_sm):
    """
    Check if there are enough warps to saturate memory bandwidth.

    Required_outstanding_bytes = Peak_BW × DRAM_Latency
    """
    required_bytes = peak_bw_gbs * 1e9 * dram_latency_ns * 1e-9  # bytes
    required_per_sm = required_bytes / num_sms
    required_requests_per_sm = required_per_sm / bytes_per_request
    # Each warp can have ~1 outstanding request at a time
    required_warps = required_requests_per_sm

    is_latency_bound = actual_warps_per_sm < required_warps

    return {
        "required_outstanding_bytes": required_bytes,
        "required_warps_per_sm": required_warps,
        "actual_warps_per_sm": actual_warps_per_sm,
        "is_latency_bound": is_latency_bound,
        "warp_deficit": max(0, required_warps - actual_warps_per_sm),
    }
```

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | First-Principles Alternative |
|-------------|---------|------|
| "Slow because of register pressure" | Register count alone doesn't determine performance | Compute occupancy budget: regs → blocks/SM → warps/SM. Then check if grid even saturates that. |
| "High memory stalls" | This is a symptom, not a cause | Follow the chain: stalls → why? → dependent loads → why? → data structure requires indirection |
| "Low SM utilization" | Doesn't say why | Check grid saturation first, then occupancy limits, then warp scheduling |
| "Try different block sizes" | Random tuning without understanding | Compute physical floor first, decompose the gap, then target the largest factor |

For the complete framework with worked examples, see `references/first-principles-analysis.md`.

---

## 1. Architecture Analysis

### Parameter Counting

```python
def analyze_architecture(model):
    """Count parameters per component."""
    total = 0
    for name, module in model.named_children():
        params = sum(p.numel() for p in module.parameters())
        total += params
        print(f"  {name}: {params/1e6:.2f}M params")
    print(f"  TOTAL: {total/1e6:.2f}M params")

    weight_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"  Weight memory: {weight_bytes / 1e9:.2f} GB")
    return total
```

### FLOPS Estimation

For transformer-based models:

```python
# Linear layer: 2 * M * N * K FLOPs
# Self-attention: 4 * seq^2 * dim * 2
# Cross-attention: 4 * seq_q * seq_kv * dim * 2
# FFN: 2 * 4 * dim^2 * seq * 2 (typical 4x expansion)

# Arithmetic intensity = total FLOPs / total bytes read
# Compare to ridge point = peak_TFLOPS / peak_BW_GB_s

# RTX 4070 Ti SUPER:
peak_compute = 44.1e12     # BF16 TFLOPS
peak_bw = 672e9            # Memory bandwidth bytes/s
ridge_point = peak_compute / peak_bw  # ~65.6 FLOP/byte

# If arithmetic intensity < ridge_point --> memory-bound
# If arithmetic intensity > ridge_point --> compute-bound
```

### Memory Footprint

```python
def get_gpu_memory():
    """Get GPU memory stats."""
    return {
        "allocated_MB": torch.cuda.memory_allocated() / 1e6,
        "reserved_MB": torch.cuda.memory_reserved() / 1e6,
        "max_allocated_MB": torch.cuda.max_memory_allocated() / 1e6,
        "max_reserved_MB": torch.cuda.max_memory_reserved() / 1e6,
    }

# Reset before measuring:
import gc
gc.collect()
torch.cuda.empty_cache()
torch.cuda.reset_peak_memory_stats()
```

## 2. Kernel Categorization

Categorize CUDA kernels by name patterns:

```python
def categorize_kernel(name):
    name_lower = name.lower()
    if any(k in name_lower for k in ['gemm', 'cutlass', 'cublas', 'matmul', 'wmma']):
        return 'GEMM/MatMul'
    elif any(k in name_lower for k in ['flash', 'fmha', 'attention', 'sdpa']):
        return 'Flash Attention'
    elif any(k in name_lower for k in ['elementwise', 'vectorized', 'pointwise']):
        return 'Elementwise'
    elif any(k in name_lower for k in ['layer_norm', 'rms_norm', 'batch_norm', 'layernorm']):
        return 'LayerNorm/RMSNorm'
    elif any(k in name_lower for k in ['gelu', 'silu', 'activation', 'relu']):
        return 'Activation'
    elif any(k in name_lower for k in ['reduce', 'softmax', 'sum']):
        return 'Reduction'
    elif any(k in name_lower for k in ['memcpy', 'memset', 'copy']):
        return 'Memory Copy'
    elif any(k in name_lower for k in ['index', 'scatter', 'gather']):
        return 'Index/Scatter/Gather'
    else:
        return 'Other'
```

## 3. Roofline Plot

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plot_roofline(peak_tflops, peak_bw_gbs, data_points, gpu_name, output_path):
    """
    Generate roofline plot.

    data_points: list of dicts with keys:
        name, arithmetic_intensity, throughput_gflops, marker, color
    """
    ridge_point = peak_tflops * 1e3 / peak_bw_gbs

    oi_range = np.logspace(-1, 3, 500)
    roofline = np.minimum(peak_tflops * 1e3, peak_bw_gbs * oi_range)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.loglog(oi_range, roofline, 'k-', linewidth=2.5, label='Roofline')
    ax.axvline(x=ridge_point, color='gray', linestyle=':', alpha=0.5,
               label=f'Ridge point ({ridge_point:.1f} FLOP/byte)')
    ax.axhline(y=peak_tflops * 1e3, color='gray', linestyle='--', alpha=0.3)

    for dp in data_points:
        ax.scatter(dp['arithmetic_intensity'], dp['throughput_gflops'],
                   marker=dp.get('marker', 'o'), s=200,
                   c=dp.get('color', 'red'), edgecolors='black', linewidth=1.5,
                   zorder=5, label=dp['name'])

    ax.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=12)
    ax.set_ylabel('Throughput (GFLOP/s)', fontsize=12)
    ax.set_title(f'Roofline Analysis — {gpu_name}', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, which='both', alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"Roofline saved to: {output_path}")
```

**GPU specs to look up for your GPU:**
- Peak BF16/FP16 TFLOPS (tensor core)
- Peak memory bandwidth (GB/s)
- These determine the roofline shape

**For RTX 4070 Ti SUPER:** 44.1 TFLOPS BF16, 672 GB/s

## 4. Execution Timeline

```python
def plot_timeline(phase_data, batch_labels, output_path, title="Inference Timeline"):
    """
    Stacked bar chart for phase comparison across configurations.

    phase_data: dict of {phase_name: [ms_per_config...]}
    batch_labels: list of config labels (e.g., ["BS=1", "BS=2", "BS=4"])
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(batch_labels))
    bottom = [0] * len(batch_labels)
    colors = plt.cm.Set2(np.linspace(0, 1, len(phase_data)))

    for (name, values), color in zip(phase_data.items(), colors):
        ax.bar(x, values, bottom=bottom, label=name, color=color, edgecolor='black')
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_xticks(x)
    ax.set_xticklabels(batch_labels)
    ax.set_ylabel('Latency (ms)')
    ax.set_title(title, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
```

## 5. Kernel Category Breakdown (Pie Chart)

```python
def plot_kernel_breakdown(categories, output_path, title="Kernel Time Distribution"):
    """
    Pie chart of kernel categories.

    categories: dict of {category_name: percentage}
    """
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = plt.cm.Set1(np.linspace(0, 1, len(categories)))
    wedges, texts, autotexts = ax.pie(
        categories.values(), labels=categories.keys(),
        autopct='%1.1f%%', colors=colors,
        textprops={'fontsize': 9}, pctdistance=0.75
    )
    ax.set_title(title, fontsize=12, fontweight='bold')
    plt.tight_layout()
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
```

## 6. Key Outputs to Generate

| Output | Purpose |
|--------|---------|
| Roofline plot | Shows if workload is memory-bound or compute-bound |
| Execution timeline | Shows phase durations and serial bottlenecks |
| Kernel category breakdown (pie chart) | Which kernel types dominate (GEMM, attention, etc.) |
| Batch scaling chart | How latency changes with batch size / input size |
| SM utilization over time | Visual proof of GPU underutilization |
| Warp stall breakdown (bar chart) | What causes GPU pipeline stalls |
| Bottleneck report (markdown) | Quantitative analysis with proposed optimizations |

## 7. Bottleneck Report Content

A complete bottleneck report should include:

1. **Executive summary** — one-paragraph finding (e.g., "workload is memory-bound at batch=1 with 12% SM occupancy")
2. **Phase breakdown** — table of phase durations and percentages
3. **Top kernels** — table of top 10-20 kernels by GPU time
4. **Kernel category distribution** — pie chart with GEMM, attention, elementwise, etc.
5. **Bottleneck classification** — memory-bound vs compute-bound per kernel
6. **Occupancy analysis** — achieved vs theoretical, warps per SM
7. **Warp stall analysis** — which stall reasons dominate
8. **Roofline position** — where the workload sits relative to the hardware ceiling
9. **Batch size scaling** — how metrics change with different configs
10. **Root cause analysis** — WHY the bottleneck exists (small sequence, weight-dominated access, etc.)
11. **Proposed optimizations** — specific, actionable suggestions
