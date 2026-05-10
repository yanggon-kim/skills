#!/usr/bin/env python3
"""
Detailed NCU metric extraction — occupancy, warp stalls, roofline data.

Usage:
  python scripts/parse_ncu_detailed.py profiles/workload.ncu-rep [label]

Output: analysis/ncu_detailed_<label>.json
"""

import csv
import io
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def parse_ncu_csv(report_path):
    """Parse NCU CSV into per-kernel metric dicts."""
    result = subprocess.run(
        ["ncu", "--import", str(report_path), "--csv", "--page", "details"],
        capture_output=True, text=True, timeout=300
    )

    reader = csv.DictReader(io.StringIO(result.stdout))
    kernel_data = defaultdict(dict)
    kernel_names = {}

    for row in reader:
        kid = row.get("ID", "")
        kname = row.get("Kernel Name", "")
        metric = row.get("Metric Name", "")
        value = row.get("Metric Value", "")
        unit = row.get("Metric Unit", "")
        kernel_names[kid] = kname
        kernel_data[kid][metric] = (value, unit)

    return kernel_data, kernel_names


def analyze_kernels(kernel_data, kernel_names, label=""):
    """Comprehensive analysis: occupancy, stalls, GEMM/attention breakdown."""
    print(f"\n{'=' * 110}")
    print(f"DETAILED NCU ANALYSIS: {label}")
    print(f"{'=' * 110}")

    records = []
    for kid in sorted(kernel_data.keys(), key=lambda x: int(x) if x.isdigit() else 0):
        m = kernel_data[kid]
        kname = kernel_names.get(kid, "?")

        def get_float(name):
            v, _ = m.get(name, ("0", ""))
            try:
                return float(v.replace(",", "").replace("%", ""))
            except Exception:
                return 0.0

        # Parse duration with unit awareness
        dur_val, dur_unit = m.get("Duration", ("0", ""))
        try:
            dur_ns = float(dur_val.replace(",", ""))
        except Exception:
            dur_ns = 0
        if "usecond" in dur_unit.lower() or "us" in dur_unit.lower():
            dur_ns *= 1000
        elif "msecond" in dur_unit.lower():
            dur_ns *= 1e6

        rec = {
            "id": kid,
            "name": kname[:100],
            "duration_ns": dur_ns,
            "sm_throughput": get_float("Compute (SM) Throughput"),
            "mem_throughput": get_float("Memory Throughput"),
            "dram_throughput": get_float("DRAM Throughput"),
            "achieved_occupancy": get_float("Achieved Occupancy"),
            "theoretical_occupancy": get_float("Theoretical Occupancy"),
            "achieved_warps_per_sm": get_float("Achieved Active Warps Per SM"),
            "l2_hit_rate": get_float("L2 Hit Rate"),
            "sm_busy": get_float("SM Busy"),
            "ipc_active": get_float("Executed Ipc Active"),
            "stall_barrier": get_float("Stall Barrier"),
            "stall_short_scoreboard": get_float("Stall Short Scoreboard"),
            "stall_long_scoreboard": get_float("Stall Long Scoreboard"),
            "stall_wait": get_float("Stall Wait"),
            "stall_not_selected": get_float("Stall Not Selected"),
            "stall_math_pipe": get_float("Stall Math Pipe Throttle"),
            "stall_mem_throttle": get_float("Stall Memory Throttle"),
        }
        records.append(rec)

    records.sort(key=lambda x: x["duration_ns"], reverse=True)
    total_ns = sum(r["duration_ns"] for r in records)

    print(f"\nTotal kernels: {len(records)}")
    print(f"Total time: {total_ns/1e3:.1f} us ({total_ns/1e6:.3f} ms)")

    # Top kernels with occupancy
    print(f"\n--- Top 25 Kernels ---")
    print(f"{'#':>3} {'Dur(us)':>8} {'%':>5} {'SM%':>5} {'Mem%':>5} {'Occ%':>5} {'ThOcc':>5} {'W/SM':>5} {'L2%':>5} {'Kernel'}")
    print("-" * 110)

    for i, r in enumerate(records[:25]):
        dur_us = r["duration_ns"] / 1e3
        pct = 100 * r["duration_ns"] / total_ns if total_ns > 0 else 0
        name = r["name"][:55]
        print(f"{i+1:>3} {dur_us:>7.1f} {pct:>5.1f} {r['sm_throughput']:>5.1f} {r['mem_throughput']:>5.1f} "
              f"{r['achieved_occupancy']:>5.1f} {r['theoretical_occupancy']:>5.1f} {r['achieved_warps_per_sm']:>5.1f} "
              f"{r['l2_hit_rate']:>5.1f} {name}")

    # Weighted averages
    print(f"\n--- Duration-Weighted Average Metrics ---")
    metric_keys = [
        ("sm_throughput", "SM Throughput (%)"),
        ("mem_throughput", "Memory Throughput (%)"),
        ("achieved_occupancy", "Achieved Occupancy (%)"),
        ("theoretical_occupancy", "Theoretical Occupancy (%)"),
        ("achieved_warps_per_sm", "Achieved Warps/SM"),
        ("l2_hit_rate", "L2 Cache Hit Rate (%)"),
        ("ipc_active", "IPC Active"),
    ]

    weighted_results = {}
    for key, label_str in metric_keys:
        vals = [(r[key], r["duration_ns"]) for r in records if r[key] > 0]
        if vals:
            tw = sum(w for _, w in vals)
            wavg = sum(v * w for v, w in vals) / tw if tw > 0 else 0
            weighted_results[key] = wavg
            print(f"  {label_str:<30}: {wavg:>6.2f}")

    # Warp stall breakdown
    print(f"\n--- Warp Stall Breakdown (duration-weighted) ---")
    stall_keys = [
        ("stall_long_scoreboard", "Long Scoreboard (memory)"),
        ("stall_short_scoreboard", "Short Scoreboard (compute)"),
        ("stall_wait", "Wait"),
        ("stall_not_selected", "Not Selected"),
        ("stall_barrier", "Barrier"),
        ("stall_math_pipe", "Math Pipe Throttle"),
        ("stall_mem_throttle", "Memory Throttle"),
    ]

    for key, label_str in stall_keys:
        vals = [(r[key], r["duration_ns"]) for r in records if r[key] > 0]
        if vals:
            tw = sum(w for _, w in vals)
            wavg = sum(v * w for v, w in vals) / tw if tw > 0 else 0
            print(f"  {label_str:<30}: {wavg:>6.2f}%")

    # Kernel launch analysis
    print(f"\n--- Kernel Launch Analysis ---")
    short = [r for r in records if r["duration_ns"] < 1000]
    medium = [r for r in records if 1000 <= r["duration_ns"] < 10000]
    long_ = [r for r in records if r["duration_ns"] >= 10000]
    print(f"  <1us kernels:   {len(short)} ({100*sum(r['duration_ns'] for r in short)/total_ns:.1f}% time)")
    print(f"  1-10us kernels: {len(medium)} ({100*sum(r['duration_ns'] for r in medium)/total_ns:.1f}% time)")
    print(f"  >10us kernels:  {len(long_)} ({100*sum(r['duration_ns'] for r in long_)/total_ns:.1f}% time)")
    print(f"  Avg kernel duration: {total_ns/len(records)/1e3:.2f} us")
    print(f"  Estimated launch overhead ({len(records)} x ~5us): {len(records)*5:.0f} us = {len(records)*5/1e3:.1f} ms")

    # Save
    output = {
        "summary": {
            "total_kernels": len(records),
            "total_time_us": total_ns / 1e3,
            "avg_kernel_duration_us": total_ns / len(records) / 1e3 if records else 0,
        },
        "weighted_metrics": weighted_results,
        "kernel_size_distribution": {
            "short_lt1us": {"count": len(short), "pct": 100*sum(r['duration_ns'] for r in short)/total_ns if total_ns else 0},
            "medium_1_10us": {"count": len(medium), "pct": 100*sum(r['duration_ns'] for r in medium)/total_ns if total_ns else 0},
            "long_gt10us": {"count": len(long_), "pct": 100*sum(r['duration_ns'] for r in long_)/total_ns if total_ns else 0},
        },
        "top_30_kernels": records[:30],
    }

    out_path = PROJECT_ROOT / "analysis" / f"ncu_detailed_{label}.json"
    out_path.parent.mkdir(exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nDetailed results saved to: {out_path}")


def main():
    report_path = sys.argv[1] if len(sys.argv) > 1 else "profiles/workload.ncu-rep"
    label = sys.argv[2] if len(sys.argv) > 2 else Path(report_path).stem

    report_path_full = PROJECT_ROOT / report_path if not Path(report_path).is_absolute() else Path(report_path)

    print(f"Parsing: {report_path_full}")
    kernel_data, kernel_names = parse_ncu_csv(report_path_full)
    analyze_kernels(kernel_data, kernel_names, label)


if __name__ == "__main__":
    main()
