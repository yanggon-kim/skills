#!/usr/bin/env python3
"""
Parse NCU report and extract key metrics for workload analysis.

Usage:
  # From .ncu-rep file (requires ncu on PATH):
  python scripts/parse_ncu_results.py profiles/workload.ncu-rep

  # With a custom label:
  python scripts/parse_ncu_results.py profiles/workload.ncu-rep my_phase

Output: analysis/ncu_analysis_<label>.json
"""

import csv
import io
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def parse_ncu_report(report_path):
    """Parse NCU report CSV output into structured data."""
    result = subprocess.run(
        ["ncu", "--import", str(report_path), "--csv", "--page", "details"],
        capture_output=True, text=True, timeout=300
    )

    if result.returncode != 0:
        print(f"Error running ncu: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    reader = csv.DictReader(io.StringIO(result.stdout))

    kernels = defaultdict(lambda: defaultdict(dict))
    for row in reader:
        kernel_name = row.get("Kernel Name", "")
        kernel_id = row.get("ID", "")
        metric_name = row.get("Metric Name", "")
        metric_value = row.get("Metric Value", "")
        metric_unit = row.get("Metric Unit", "")
        section = row.get("Section Name", "")

        key = f"{kernel_id}_{kernel_name[:80]}"
        kernels[key][metric_name] = {
            "value": metric_value,
            "unit": metric_unit,
            "section": section,
        }

    return kernels


def categorize_kernel(name):
    """Categorize a kernel by its name."""
    name_lower = name.lower()
    if any(k in name_lower for k in ['gemm', 'cutlass', 'cublas', 'matmul', 'wmma']):
        return 'GEMM/MatMul'
    elif any(k in name_lower for k in ['flash', 'fmha', 'attention', 'sdpa']):
        return 'Flash Attention'
    elif any(k in name_lower for k in ['layer_norm', 'layernorm', 'rms_norm']):
        return 'LayerNorm/RMSNorm'
    elif any(k in name_lower for k in ['elementwise', 'vectorized', 'pointwise']):
        return 'Elementwise'
    elif any(k in name_lower for k in ['gelu', 'silu', 'activation', 'relu']):
        return 'Activation'
    elif any(k in name_lower for k in ['reduce', 'softmax', 'sum']):
        return 'Reduction'
    elif any(k in name_lower for k in ['copy', 'memcpy', 'memset']):
        return 'Memory Copy'
    elif any(k in name_lower for k in ['index', 'scatter', 'gather']):
        return 'Index/Scatter/Gather'
    else:
        return 'Other'


KEY_METRICS = [
    "SM Busy",
    "Compute (SM) Throughput",
    "Memory Throughput",
    "DRAM Throughput",
    "L2 Hit Rate",
    "L1/TEX Hit Rate",
    "Achieved Occupancy",
    "Theoretical Occupancy",
    "Achieved Active Warps Per SM",
    "SM Active Cycles",
    "Executed Ipc Active",
    "Executed Ipc Elapsed",
    "Mem Busy",
    "DRAM Utilization",
    "Duration",
    "Stall Wait",
    "Stall Barrier",
    "Stall Short Scoreboard",
    "Stall Long Scoreboard",
    "Stall Memory Dependency",
    "Stall Memory Throttle",
    "Stall Math Pipe Throttle",
    "Stall Not Selected",
    "Stall Misc",
]


def extract_key_metrics(kernels):
    """Extract important metrics for each kernel."""
    results = []
    for kernel_key, metrics in kernels.items():
        kernel_id = kernel_key.split("_")[0]
        kernel_name = "_".join(kernel_key.split("_")[1:])

        duration = metrics.get("Duration", {}).get("value", "0")
        try:
            duration_val = float(duration.replace(",", ""))
        except (ValueError, AttributeError):
            duration_val = 0
        duration_unit = metrics.get("Duration", {}).get("unit", "")

        entry = {
            "id": kernel_id,
            "kernel": kernel_name,
            "category": categorize_kernel(kernel_name),
            "duration": duration_val,
            "duration_unit": duration_unit,
        }

        for metric in KEY_METRICS:
            if metric in metrics:
                try:
                    val = float(metrics[metric]["value"].replace(",", "").replace("%", ""))
                except (ValueError, AttributeError):
                    val = metrics[metric]["value"]
                entry[metric] = val

        results.append(entry)

    return results


def summarize_results(results, label=""):
    """Print and return summary statistics."""
    results_sorted = sorted(results, key=lambda x: x.get("duration", 0), reverse=True)
    total_duration = sum(r.get("duration", 0) for r in results_sorted)

    print(f"\n{'=' * 100}")
    print(f"NCU KERNEL ANALYSIS: {label}")
    print(f"{'=' * 100}")
    print(f"\nTotal kernels: {len(results_sorted)}")
    print(f"Total GPU time: {total_duration:.0f} {results_sorted[0].get('duration_unit', 'ns') if results_sorted else ''}")

    # Top kernels
    print(f"\n--- Top 20 Kernels by Duration ---")
    print(f"{'#':>3} {'Duration':>12} {'%':>6} {'SM%':>6} {'Mem%':>6} {'Occ':>5} {'Cat':<16} {'Kernel Name'}")
    print("-" * 100)

    for i, r in enumerate(results_sorted[:20]):
        dur = r.get("duration", 0)
        pct = 100 * dur / total_duration if total_duration > 0 else 0
        sm = r.get("Compute (SM) Throughput", r.get("SM Busy", "-"))
        mem = r.get("Memory Throughput", r.get("Mem Busy", "-"))
        occ = r.get("Achieved Occupancy", "-")
        cat = r.get("category", "?")
        name = r.get("kernel", "")[:40]

        sm_s = f"{sm:.1f}" if isinstance(sm, (int, float)) else str(sm)[:5]
        mem_s = f"{mem:.1f}" if isinstance(mem, (int, float)) else str(mem)[:5]
        occ_s = f"{occ:.1f}" if isinstance(occ, (int, float)) else str(occ)[:5]

        print(f"{i+1:>3} {dur:>10.0f}ns {pct:>5.1f}% {sm_s:>6} {mem_s:>6} {occ_s:>5} {cat:<16} {name}")

    # Category breakdown
    categories = defaultdict(lambda: {"count": 0, "duration": 0})
    for r in results_sorted:
        cat = r.get("category", "Other")
        categories[cat]["count"] += 1
        categories[cat]["duration"] += r.get("duration", 0)

    print(f"\n--- Kernel Categories ---")
    print(f"{'Category':<25} {'Count':>6} {'Duration':>12} {'%':>7}")
    print("-" * 55)
    for cat, data in sorted(categories.items(), key=lambda x: x[1]["duration"], reverse=True):
        pct = 100 * data["duration"] / total_duration if total_duration > 0 else 0
        print(f"  {cat:<23} {data['count']:>6} {data['duration']:>10.0f}ns {pct:>6.1f}%")

    # Bottleneck classification
    print(f"\n--- Bottleneck Classification ---")
    mem_bound = comp_bound = balanced = 0
    for r in results_sorted:
        sm = r.get("Compute (SM) Throughput", 0)
        mem = r.get("Memory Throughput", 0)
        dur = r.get("duration", 0)
        if isinstance(sm, (int, float)) and isinstance(mem, (int, float)):
            if mem > sm * 1.5:
                mem_bound += dur
            elif sm > mem * 1.5:
                comp_bound += dur
            else:
                balanced += dur

    total_c = mem_bound + comp_bound + balanced
    if total_c > 0:
        print(f"  Memory-bound: {100*mem_bound/total_c:.1f}% of classified time")
        print(f"  Compute-bound: {100*comp_bound/total_c:.1f}% of classified time")
        print(f"  Balanced: {100*balanced/total_c:.1f}% of classified time")

    return results_sorted


def main():
    report_path = sys.argv[1] if len(sys.argv) > 1 else "profiles/workload.ncu-rep"
    label = sys.argv[2] if len(sys.argv) > 2 else Path(report_path).stem

    report_path = PROJECT_ROOT / report_path if not Path(report_path).is_absolute() else Path(report_path)

    print(f"Parsing NCU report: {report_path}")
    kernels = parse_ncu_report(report_path)
    print(f"Found {len(kernels)} unique kernel invocations")

    results = extract_key_metrics(kernels)
    sorted_results = summarize_results(results, label)

    output_path = PROJECT_ROOT / "analysis" / f"ncu_analysis_{label}.json"
    output_path.parent.mkdir(exist_ok=True)

    summary = {
        "total_kernels": len(sorted_results),
        "total_duration_ns": sum(r.get("duration", 0) for r in sorted_results),
        "top_20_kernels": [
            {
                "kernel": r.get("kernel", "")[:100],
                "category": r.get("category", ""),
                "duration_ns": r.get("duration", 0),
                "sm_throughput_pct": r.get("Compute (SM) Throughput", None),
                "memory_throughput_pct": r.get("Memory Throughput", None),
                "achieved_occupancy_pct": r.get("Achieved Occupancy", None),
                "l2_hit_rate_pct": r.get("L2 Hit Rate", None),
            }
            for r in sorted_results[:20]
        ],
    }

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to: {output_path}")


if __name__ == "__main__":
    main()
