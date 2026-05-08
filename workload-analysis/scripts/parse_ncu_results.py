#!/usr/bin/env python3
"""
Parse NCU report and extract key metrics for workload analysis.

Reads the .ncu-rep file directly via `ncu --import` and parses two pages:

  - details page:  per-kernel sectional metrics (occupancy, throughput,
                   stall reasons, IPC, BW utilisation).
  - raw page:      per-kernel raw counters including pipe utilisation
                   (sm__inst_executed_pipe_*) and per-op LSU request
                   counts (l1tex__t_requests_pipe_lsu_mem_*_op_*).

Together these let us emit a `pipe_utilization` block per kernel + a
`pipe_lsu_split` block (Load / Store / Atomic apportionment of LSU%) —
the inputs Step 5.5's static-vs-dynamic cross-check needs.

Usage:
  # Bottleneck-survey mode (top-20 kernels, kernel-categorisation report):
  python scripts/parse_ncu_results.py profiles/workload.ncu-rep

  # With a custom label:
  python scripts/parse_ncu_results.py profiles/workload.ncu-rep my_phase

  # Step-5.5 mode — focus on a single kernel and emit pipe_lsu_split:
  python scripts/parse_ncu_results.py profiles/workload.ncu-rep \\
      --target-kernel csrmv_v3_kernel \\
      --output analysis/ncu_<kernel>.json

Output: analysis/ncu_analysis_<label>.json (default) or the path given to
        --output. The JSON includes a top-level `top_20_kernels` array
        (bottleneck survey) and, when `--target-kernel` is given, a
        `<kernel_short_name>` key with the pipe-utilisation + LSU-split
        blocks needed by `crosscheck_sass.py`.
"""

import argparse
import csv
import io
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


# ---------------------------------------------------------------------------
# Raw-page metric mappings (Step 5.5 inputs)
# ---------------------------------------------------------------------------

# Per-pipe utilisation (% of peak issue rate per active or per elapsed cycle).
# `_active`  : averaged over cycles when the SM was issue-active.
# `_elapsed` : averaged over wall-clock kernel duration.
RAW_PIPE_COLUMNS = {
    "sm__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_active":   "lsu_active_pct",
    "sm__inst_executed_pipe_fma.avg.pct_of_peak_sustained_active":   "fma_active_pct",
    "sm__inst_executed_pipe_alu.avg.pct_of_peak_sustained_active":   "alu_active_pct",
    "sm__inst_executed_pipe_xu.avg.pct_of_peak_sustained_active":    "xu_active_pct",
    "sm__inst_executed_pipe_adu.avg.pct_of_peak_sustained_active":   "adu_active_pct",
    "sm__inst_executed_pipe_cbu.avg.pct_of_peak_sustained_active":   "cbu_active_pct",
    "sm__inst_executed_pipe_fp16.avg.pct_of_peak_sustained_active":  "fp16_active_pct",
    "sm__inst_executed_pipe_lsu.avg.pct_of_peak_sustained_elapsed":  "lsu_elapsed_pct",
    "sm__inst_executed_pipe_fma.avg.pct_of_peak_sustained_elapsed":  "fma_elapsed_pct",
    "sm__inst_executed_pipe_alu.avg.pct_of_peak_sustained_elapsed":  "alu_elapsed_pct",
    "sm__inst_executed_pipe_xu.avg.pct_of_peak_sustained_elapsed":   "xu_elapsed_pct",
}

# Per-op LSU request counts. Used to apportion aggregate LSU% across
# Load / Store / Atomic sub-shares. `op_red` and `op_atom` count as writes
# (cuSPARSE-style kernels write y/C via RED.E.ADD on boundary rows).
RAW_OP_COUNT_COLUMNS = {
    "l1tex__t_requests_pipe_lsu_mem_global_op_ld.sum":         "global_ld",
    "l1tex__t_requests_pipe_lsu_mem_global_op_st.sum":         "global_st",
    "l1tex__t_requests_pipe_lsu_mem_global_op_red.sum":        "global_red",
    "l1tex__t_requests_pipe_lsu_mem_global_op_atom.sum":       "global_atom",
    "l1tex__t_requests_pipe_lsu_mem_local_op_ld.sum":          "local_ld",
    "l1tex__t_requests_pipe_lsu_mem_local_op_st.sum":          "local_st",
    "l1tex__data_pipe_lsu_wavefronts_mem_shared_op_ld.sum":    "shared_ld",
    "l1tex__data_pipe_lsu_wavefronts_mem_shared_op_st.sum":    "shared_st",
    "l1tex__data_pipe_lsu_wavefronts_mem_shared_op_atom.sum":  "shared_atom",
}


def parse_numeric(value_str):
    """Parse a numeric value from NCU CSV (handles commas / units / blanks)."""
    if value_str is None or value_str.strip() == "":
        return None
    s = value_str.strip().replace(",", "").rstrip("%")
    try:
        return float(s)
    except ValueError:
        return None


def compute_lsu_split(lsu_active_pct, op_counts):
    """Apportion aggregate LSU% across Load / Store / Atomic by request count.

    Returns a dict with load_pct / write_pct / atomic_pct (each a share of
    LSU%) plus per-memory-space breakdown and the underlying counts.

    Writes count `op_st + op_red + op_atom` together: cuSPARSE-style kernels
    write y/C via `RED.E.ADD` (op_red), not `STG`, when output rows can
    overlap across CTAs. Counting only `op_st` underreports writes by 50-95%
    on dense-row matrices.
    """
    if lsu_active_pct is None or not op_counts:
        return None

    g_ld    = op_counts.get("global_ld", 0)   or 0
    g_st    = op_counts.get("global_st", 0)   or 0
    g_red   = op_counts.get("global_red", 0)  or 0
    g_atom  = op_counts.get("global_atom", 0) or 0
    l_ld    = op_counts.get("local_ld", 0)    or 0
    l_st    = op_counts.get("local_st", 0)    or 0
    s_ld    = op_counts.get("shared_ld", 0)   or 0
    s_st    = op_counts.get("shared_st", 0)   or 0
    s_atom  = op_counts.get("shared_atom", 0) or 0

    loads_global   = g_ld
    loads_local    = l_ld
    loads_shared   = s_ld
    stores_global  = g_st
    stores_local   = l_st
    stores_shared  = s_st
    atomics_global = g_red + g_atom
    atomics_shared = s_atom

    loads_total   = loads_global + loads_local + loads_shared
    stores_total  = stores_global + stores_local + stores_shared
    atomics_total = atomics_global + atomics_shared
    writes_total  = stores_total + atomics_total
    grand_total   = loads_total + writes_total
    if grand_total <= 0:
        return None

    def share(n):
        return lsu_active_pct * n / grand_total if grand_total > 0 else 0.0

    return {
        "load_pct":          round(share(loads_total), 2),
        "write_pct":         round(share(writes_total), 2),   # store + atomic
        "store_pct":         round(share(stores_total), 2),
        "atomic_pct":        round(share(atomics_total), 2),
        "load_global_pct":   round(share(loads_global), 2),
        "load_local_pct":    round(share(loads_local), 2),
        "load_shared_pct":   round(share(loads_shared), 2),
        "store_global_pct":  round(share(stores_global), 2),
        "store_shared_pct":  round(share(stores_shared), 2),
        "atomic_global_pct": round(share(atomics_global), 2),
        "atomic_shared_pct": round(share(atomics_shared), 2),
        "load_to_write_ratio": round(loads_total / max(1, writes_total), 2),
        "op_request_counts": {
            "global_ld": int(g_ld), "global_st": int(g_st),
            "global_red": int(g_red), "global_atom": int(g_atom),
            "local_ld": int(l_ld), "local_st": int(l_st),
            "shared_ld": int(s_ld), "shared_st": int(s_st),
            "shared_atom": int(s_atom),
        },
        "_note": ("writes = op_st + op_red + op_atom (cuSPARSE-style kernels "
                  "write y/C via RED.E.ADD on boundary rows; counting only "
                  "op_st underreports writes)"),
    }


# ---------------------------------------------------------------------------
# Details-page parsing (existing behaviour preserved)
# ---------------------------------------------------------------------------

def run_ncu_csv(report_path, page):
    """Run `ncu --import ... --csv --page <page>` and return CSV text."""
    result = subprocess.run(
        ["ncu", "--import", str(report_path), "--csv", "--page", page],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"Error running ncu (page={page}): {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout


def parse_details_page(report_path):
    """Parse details page → per-kernel-launch dict of metric name → value."""
    csv_text = run_ncu_csv(report_path, "details")
    reader = csv.DictReader(io.StringIO(csv_text))
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


def parse_raw_page(report_path):
    """Parse raw page → per-launch-id dict with pipes + op_counts.

    Raw page has one row per kernel launch; columns are raw metric names.
    """
    csv_text = run_ncu_csv(report_path, "raw")
    reader = csv.DictReader(io.StringIO(csv_text))
    launches = {}
    for row in reader:
        launch_id = row.get("ID", "").strip()
        if not launch_id:
            continue

        pipes = {}
        for raw_col, our_name in RAW_PIPE_COLUMNS.items():
            val = parse_numeric(row.get(raw_col, ""))
            if val is not None:
                pipes[our_name] = val

        op_counts = {}
        for raw_col, our_name in RAW_OP_COUNT_COLUMNS.items():
            val = parse_numeric(row.get(raw_col, ""))
            if val is not None:
                op_counts[our_name] = val

        launches[launch_id] = {"pipes": pipes, "op_counts": op_counts}
    return launches


def simplify_kernel_name(full_name):
    """Extract a short kernel name from a fully-mangled NCU kernel name."""
    # Common short-name patterns first
    for short in ("csrmv_v3_kernel", "csrmm_alg2_kernel", "csr_partition_kernel",
                  "sgemm", "hgemm", "gemm", "fmha", "flash_attn"):
        if short in full_name:
            return short
    # Fall back to the first identifier after `void` / template noise
    m = re.match(r"void\s+(?:.*>::)?([A-Za-z_][\w]*)", full_name)
    if m:
        return m.group(1)
    return full_name[:60]


def categorize_kernel(name):
    name_lower = name.lower()
    if any(k in name_lower for k in ['gemm', 'cutlass', 'cublas', 'matmul', 'wmma', 'wgmma']):
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
    elif any(k in name_lower for k in ['csrmv', 'csrmm', 'spmv', 'spmm', 'sparse']):
        return 'Sparse'
    else:
        return 'Other'


KEY_METRICS = [
    "SM Busy", "Compute (SM) Throughput", "Memory Throughput",
    "DRAM Throughput", "L2 Hit Rate", "L1/TEX Hit Rate",
    "Achieved Occupancy", "Theoretical Occupancy",
    "Achieved Active Warps Per SM", "SM Active Cycles",
    "Executed Ipc Active", "Executed Ipc Elapsed",
    "Mem Busy", "DRAM Utilization", "Duration",
    "Stall Wait", "Stall Barrier", "Stall Short Scoreboard",
    "Stall Long Scoreboard", "Stall Memory Dependency",
    "Stall Memory Throttle", "Stall Math Pipe Throttle",
    "Stall Not Selected", "Stall Misc",
]


def extract_per_kernel(details, raw_data):
    """Build per-kernel records combining details + raw."""
    results = []
    for kernel_key, metrics in details.items():
        kernel_id = kernel_key.split("_", 1)[0]
        kernel_name = kernel_key.split("_", 1)[1] if "_" in kernel_key else ""
        kernel_short = simplify_kernel_name(kernel_name)

        duration = metrics.get("Duration", {}).get("value", "0")
        try:
            duration_val = float(duration.replace(",", ""))
        except (ValueError, AttributeError):
            duration_val = 0
        duration_unit = metrics.get("Duration", {}).get("unit", "")

        entry = {
            "id": kernel_id,
            "kernel_full": kernel_name,
            "kernel": kernel_short,
            "category": categorize_kernel(kernel_name),
            "duration": duration_val,
            "duration_unit": duration_unit,
        }

        for metric in KEY_METRICS:
            if metric in metrics:
                val = parse_numeric(metrics[metric]["value"])
                if val is None:
                    val = metrics[metric]["value"]
                entry[metric] = val

        # Merge raw-page pipe / op-count data
        raw = raw_data.get(kernel_id, {})
        pipes = raw.get("pipes", {})
        op_counts = raw.get("op_counts", {})

        if pipes:
            entry["pipe_utilization"] = {k: round(v, 2) for k, v in pipes.items()}
            lsu = pipes.get("lsu_active_pct")
            fma = pipes.get("fma_active_pct")
            alu = pipes.get("alu_active_pct")
            xu = pipes.get("xu_active_pct", 0.0) or 0.0
            if lsu is not None and fma is not None and alu is not None:
                compute = fma + alu + xu
                total = lsu + compute
                entry["pipe_summary"] = {
                    "lsu_pct": round(lsu, 2),
                    "compute_pct": round(compute, 2),
                    "lsu_share_of_busy": round(lsu / total * 100, 2) if total > 0 else None,
                    "compute_share_of_busy": round(compute / total * 100, 2) if total > 0 else None,
                }

            split = compute_lsu_split(lsu, op_counts)
            if split is not None:
                entry["pipe_lsu_split"] = split

        results.append(entry)

    return results


def summarize_results(results, label=""):
    """Print top-20 + categories + bottleneck classification."""
    results_sorted = sorted(results, key=lambda x: x.get("duration", 0), reverse=True)
    total_duration = sum(r.get("duration", 0) for r in results_sorted)

    print(f"\n{'=' * 100}")
    print(f"NCU KERNEL ANALYSIS: {label}")
    print(f"{'=' * 100}")
    print(f"\nTotal kernels: {len(results_sorted)}")
    print(f"Total GPU time: {total_duration:.0f} {results_sorted[0].get('duration_unit', 'ns') if results_sorted else ''}")

    print(f"\n--- Top 20 Kernels by Duration ---")
    print(f"{'#':>3} {'Duration':>12} {'%':>6} {'SM%':>6} {'Mem%':>6} {'LSU%':>6} {'FMA%':>6} {'Occ':>5} {'Cat':<14} Kernel")
    print("-" * 110)

    for i, r in enumerate(results_sorted[:20]):
        dur = r.get("duration", 0)
        pct = 100 * dur / total_duration if total_duration > 0 else 0
        sm = r.get("Compute (SM) Throughput", r.get("SM Busy", "-"))
        mem = r.get("Memory Throughput", r.get("Mem Busy", "-"))
        occ = r.get("Achieved Occupancy", "-")
        pipes = r.get("pipe_utilization", {})
        lsu = pipes.get("lsu_active_pct", "-")
        fma = pipes.get("fma_active_pct", "-")

        sm_s = f"{sm:.1f}" if isinstance(sm, (int, float)) else str(sm)[:5]
        mem_s = f"{mem:.1f}" if isinstance(mem, (int, float)) else str(mem)[:5]
        lsu_s = f"{lsu:.1f}" if isinstance(lsu, (int, float)) else str(lsu)[:5]
        fma_s = f"{fma:.1f}" if isinstance(fma, (int, float)) else str(fma)[:5]
        occ_s = f"{occ:.1f}" if isinstance(occ, (int, float)) else str(occ)[:5]
        cat = r.get("category", "?")
        name = r.get("kernel", "")[:40]

        print(f"{i+1:>3} {dur:>10.0f}ns {pct:>5.1f}% {sm_s:>6} {mem_s:>6} {lsu_s:>6} {fma_s:>6} {occ_s:>5} {cat:<14} {name}")

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
    ap = argparse.ArgumentParser()
    ap.add_argument("report", type=Path,
                    help=".ncu-rep file to parse")
    ap.add_argument("label", nargs="?", default=None,
                    help="optional label for output JSON filename")
    ap.add_argument("--target-kernel", type=str, default=None,
                    help="emit a per-kernel block for this short kernel name "
                         "(e.g. csrmv_v3_kernel) — required by Step 5.5's "
                         "crosscheck_sass.py")
    ap.add_argument("--output", type=Path, default=None,
                    help="explicit output JSON path "
                         "(default: analysis/ncu_analysis_<label>.json)")
    args = ap.parse_args()

    report_path = args.report if args.report.is_absolute() else PROJECT_ROOT / args.report
    label = args.label or report_path.stem

    print(f"Parsing NCU report: {report_path}", file=sys.stderr)
    details = parse_details_page(report_path)
    raw = parse_raw_page(report_path)
    print(f"Found {len(details)} unique kernel invocations "
          f"({len(raw)} with raw-page entries)", file=sys.stderr)

    results = extract_per_kernel(details, raw)
    sorted_results = summarize_results(results, label)

    output_path = args.output or (PROJECT_ROOT / "analysis" / f"ncu_analysis_{label}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "report": str(report_path),
        "total_kernels": len(sorted_results),
        "total_duration_ns": sum(r.get("duration", 0) for r in sorted_results),
        "top_20_kernels": [
            {
                "kernel": r.get("kernel", "")[:100],
                "kernel_full": r.get("kernel_full", "")[:200],
                "category": r.get("category", ""),
                "duration_ns": r.get("duration", 0),
                "sm_throughput_pct": r.get("Compute (SM) Throughput"),
                "memory_throughput_pct": r.get("Memory Throughput"),
                "achieved_occupancy_pct": r.get("Achieved Occupancy"),
                "l2_hit_rate_pct": r.get("L2 Hit Rate"),
                "pipe_utilization": r.get("pipe_utilization"),
                "pipe_summary": r.get("pipe_summary"),
                "pipe_lsu_split": r.get("pipe_lsu_split"),
            }
            for r in sorted_results[:20]
        ],
    }

    # If --target-kernel was given, emit a focused per-kernel block at the
    # top level (keyed by short kernel name) so that crosscheck_sass.py can
    # consume it directly with --single-run.
    if args.target_kernel:
        # Pick the longest-running invocation whose short name OR full name
        # CONTAINS the target string. Custom kernels often have very long
        # parameter signatures; ncu's Kernel Name column truncates them and
        # `simplify_kernel_name` may not produce the user's short name
        # exactly, so substring match is more robust than exact equality.
        target = args.target_kernel
        matches = [r for r in sorted_results
                   if target in r.get("kernel", "") or
                      target in r.get("kernel_full", "")]
        if matches:
            kdata = matches[0]
            summary[args.target_kernel] = {
                "kernel_full": kdata.get("kernel_full", ""),
                "duration_ns": kdata.get("duration"),
                "sm_throughput_pct": kdata.get("Compute (SM) Throughput"),
                "memory_throughput_pct": kdata.get("Memory Throughput"),
                "achieved_occupancy_pct": kdata.get("Achieved Occupancy"),
                "ipc_active": kdata.get("Executed Ipc Active"),
                "pipe_utilization": kdata.get("pipe_utilization"),
                "pipe_summary": kdata.get("pipe_summary"),
                "pipe_lsu_split": kdata.get("pipe_lsu_split"),
            }
            print(f"\nTarget kernel '{args.target_kernel}' picked: "
                  f"id={kdata['id']}, duration={kdata.get('duration')}ns",
                  file=sys.stderr)
            if not summary[args.target_kernel]["pipe_lsu_split"]:
                print(f"WARNING: no pipe_lsu_split for {args.target_kernel} "
                      f"(per-op LSU counters missing from raw page; ensure "
                      f"the .ncu-rep was collected with --set full)",
                      file=sys.stderr)
        else:
            available = sorted({r.get("kernel") for r in sorted_results})
            print(f"WARNING: no kernel matched '{args.target_kernel}'. "
                  f"Available: {available}", file=sys.stderr)

    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSummary saved to: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
