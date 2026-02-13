#!/usr/bin/env python3
"""
Generate roofline plot for GPU workload analysis.

Usage:
  # With a JSON data file:
  python scripts/plot_roofline.py --data analysis/kernel_data.json

  # With specific GPU:
  python scripts/plot_roofline.py --data analysis/kernel_data.json --gpu rtx4070ti_super

  # Demo mode (test with sample data):
  python scripts/plot_roofline.py --demo

Data JSON format:
  [
    {"name": "Phase A GEMM", "arithmetic_intensity": 120.5, "throughput_gflops": 25000,
     "marker": "o", "color": "#e74c3c"},
    {"name": "LayerNorm", "arithmetic_intensity": 2.3, "throughput_gflops": 800,
     "marker": "s", "color": "#3498db"}
  ]
"""

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "analysis"

# GPU specs lookup table
# Add your GPU here if it's not listed
GPU_SPECS = {
    "rtx4070ti_super": {"peak_tflops": 44.1, "peak_bw": 672, "name": "RTX 4070 Ti SUPER"},
    "rtx4090":         {"peak_tflops": 82.6, "peak_bw": 1008, "name": "RTX 4090"},
    "rtx3090":         {"peak_tflops": 35.6, "peak_bw": 936,  "name": "RTX 3090"},
    "a100_40gb":       {"peak_tflops": 312,  "peak_bw": 1555, "name": "A100 40GB"},
    "a100_80gb":       {"peak_tflops": 312,  "peak_bw": 2039, "name": "A100 80GB"},
    "h100_sxm":        {"peak_tflops": 989,  "peak_bw": 3350, "name": "H100 SXM"},
    "l40":             {"peak_tflops": 181,  "peak_bw": 864,  "name": "L40"},
}


def plot_roofline(peak_tflops, peak_bw_gbs, data_points, gpu_name, output_path):
    """Generate roofline plot."""
    ridge_point = peak_tflops * 1e3 / peak_bw_gbs

    oi_range = np.logspace(-1, 3, 500)
    roofline = np.minimum(peak_tflops * 1e3, peak_bw_gbs * oi_range)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Roofline curve
    ax.loglog(oi_range, roofline, 'k-', linewidth=2.5, label='Roofline')

    # Ridge point
    ax.axvline(x=ridge_point, color='gray', linestyle=':', alpha=0.6,
               label=f'Ridge point ({ridge_point:.1f} FLOP/byte)')

    # Peak compute line
    ax.axhline(y=peak_tflops * 1e3, color='gray', linestyle='--', alpha=0.3)
    ax.text(500, peak_tflops * 1e3 * 1.1, f'Peak: {peak_tflops} TFLOPS',
            fontsize=9, color='gray')

    # Region shading
    ax.fill_between(oi_range, 0.1, roofline, where=(oi_range < ridge_point),
                    alpha=0.08, color='blue')
    ax.fill_between(oi_range, 0.1, roofline, where=(oi_range >= ridge_point),
                    alpha=0.08, color='red')
    ax.text(ridge_point * 0.08, peak_tflops * 1e3 * 0.3, 'Memory\nBound',
            fontsize=14, color='blue', alpha=0.6, fontweight='bold')
    ax.text(ridge_point * 4, peak_tflops * 1e3 * 0.3, 'Compute\nBound',
            fontsize=14, color='red', alpha=0.6, fontweight='bold')

    # Data points
    for dp in data_points:
        marker = dp.get('marker', 'o')
        color = dp.get('color', '#e74c3c')
        ax.scatter(dp['arithmetic_intensity'], dp['throughput_gflops'],
                   marker=marker, s=200, c=color, edgecolors='black',
                   linewidth=1.5, zorder=5, label=dp['name'])

        # Efficiency annotation
        theoretical = min(peak_tflops * 1e3, peak_bw_gbs * dp['arithmetic_intensity'])
        eff = dp['throughput_gflops'] / theoretical * 100 if theoretical > 0 else 0
        ax.annotate(f'{eff:.0f}%',
                    (dp['arithmetic_intensity'], dp['throughput_gflops']),
                    textcoords='offset points', xytext=(10, 10), fontsize=9,
                    fontweight='bold', color=color)

    ax.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=12)
    ax.set_ylabel('Throughput (GFLOP/s)', fontsize=12)
    ax.set_title(f'Roofline Analysis — {gpu_name}', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(True, which='both', alpha=0.3)
    ax.set_ylim(bottom=0.1)

    # GPU info box
    textstr = (f'GPU: {gpu_name}\n'
               f'Peak BF16: {peak_tflops} TFLOPS\n'
               f'Peak BW: {peak_bw_gbs} GB/s\n'
               f'Ridge: {ridge_point:.1f} FLOP/byte')
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=8,
            verticalalignment='top', bbox=props)

    plt.tight_layout()
    OUTPUT_DIR.mkdir(exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)
    print(f"Roofline saved to: {output_path}")

    # Also save PDF
    pdf_path = output_path.with_suffix('.pdf')
    fig_copy, ax_copy = plt.subplots(figsize=(12, 8))
    # Re-plot for PDF (matplotlib reuse issue)
    plt.close(fig_copy)


def main():
    parser = argparse.ArgumentParser(description="Generate roofline plot")
    parser.add_argument("--data", help="JSON file with data points")
    parser.add_argument("--output", "-o", default=None, help="Output image path")
    parser.add_argument("--gpu", choices=list(GPU_SPECS.keys()), default="rtx4070ti_super",
                        help="GPU preset (default: rtx4070ti_super)")
    parser.add_argument("--peak-tflops", type=float, help="Override peak BF16 TFLOPS")
    parser.add_argument("--peak-bw", type=float, help="Override peak memory bandwidth (GB/s)")
    parser.add_argument("--demo", action="store_true", help="Use demo data")
    args = parser.parse_args()

    # GPU specs
    spec = GPU_SPECS[args.gpu]
    peak_tflops = args.peak_tflops or spec["peak_tflops"]
    peak_bw = args.peak_bw or spec["peak_bw"]
    gpu_name = spec["name"]

    # Data points
    if args.demo:
        data_points = [
            {"name": "GEMM (large)", "arithmetic_intensity": 120.5, "throughput_gflops": 25000, "marker": "o", "color": "#e74c3c"},
            {"name": "Flash Attention", "arithmetic_intensity": 45.0, "throughput_gflops": 18000, "marker": "^", "color": "#e67e22"},
            {"name": "LayerNorm", "arithmetic_intensity": 2.3, "throughput_gflops": 1200, "marker": "s", "color": "#27ae60"},
            {"name": "Elementwise", "arithmetic_intensity": 0.8, "throughput_gflops": 500, "marker": "D", "color": "#3498db"},
            {"name": "Softmax", "arithmetic_intensity": 3.5, "throughput_gflops": 2000, "marker": "v", "color": "#9b59b6"},
        ]
    elif args.data:
        with open(args.data) as f:
            data_points = json.load(f)
    else:
        data_points = []

    output_path = Path(args.output) if args.output else OUTPUT_DIR / "roofline.png"
    plot_roofline(peak_tflops, peak_bw, data_points, gpu_name, output_path)


if __name__ == "__main__":
    main()
