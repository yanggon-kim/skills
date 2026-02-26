#!/usr/bin/env python3
"""
GPU Workload Profiling Script (Generalized Template)
=====================================================
Comprehensive profiling of any GPU workload for hardware architecture research.

Profiles:
  - Per-phase execution breakdown
  - Memory allocation breakdown
  - Multi-configuration sweep (batch sizes, input dimensions)
  - PyTorch Profiler trace + kernel table export

Usage:
  python scripts/profile_workload.py --mode full
  python scripts/profile_workload.py --mode single-step --batch-size 1
  python scripts/profile_workload.py --mode batch-sweep
  python scripts/profile_workload.py --mode arch-analysis

ADAPT THIS SCRIPT:
  1. Modify load_model_and_inputs() to load YOUR model
  2. Modify run_inference_phased() to break YOUR model into profiled phases
  3. Adjust batch sizes and configurations in BATCH_SIZES
"""

import argparse
import gc
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import torch
import torch.cuda

# ============================================================================
# Configuration — ADAPT THESE
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "analysis"
TRACE_DIR = PROJECT_ROOT / "traces"
PROFILE_DIR = PROJECT_ROOT / "profiles"

for d in [OUTPUT_DIR, TRACE_DIR, PROFILE_DIR]:
    d.mkdir(exist_ok=True)

BATCH_SIZES = [1, 2, 4, 8]  # Adjust per your workload and GPU memory


# ============================================================================
# Utilities (reusable across all workloads)
# ============================================================================

class CUDATimer:
    """GPU-synchronized timer using CUDA events."""
    def __init__(self):
        self.start_event = torch.cuda.Event(enable_timing=True)
        self.end_event = torch.cuda.Event(enable_timing=True)

    def start(self):
        self.start_event.record()

    def stop(self):
        self.end_event.record()
        torch.cuda.synchronize()
        return self.start_event.elapsed_time(self.end_event)


class PhaseTimer:
    """Collect timing statistics for named phases."""
    def __init__(self):
        self.records = {}

    @contextmanager
    def phase(self, name):
        timer = CUDATimer()
        timer.start()
        yield
        elapsed = timer.stop()
        self.records.setdefault(name, []).append(elapsed)

    def summary(self):
        lines = []
        total = 0
        for name, times in self.records.items():
            avg = np.mean(times)
            std = np.std(times)
            total += avg
            lines.append((name, avg, std, len(times)))

        lines.sort(key=lambda x: x[1], reverse=True)

        print(f"\n{'=' * 80}")
        print(f"{'Phase':<40} {'Avg (ms)':>10} {'Std (ms)':>10} {'Count':>6} {'%':>7}")
        print(f"{'-' * 80}")
        for name, avg, std, count in lines:
            pct = 100 * avg / total if total > 0 else 0
            print(f"  {name:<38} {avg:>10.3f} {std:>10.3f} {count:>6} {pct:>6.1f}%")
        print(f"{'-' * 80}")
        print(f"  {'TOTAL':<38} {total:>10.3f}")
        print(f"{'=' * 80}")

        return {name: {"avg_ms": float(np.mean(times)), "std_ms": float(np.std(times)),
                       "count": len(times), "pct": float(100 * np.mean(times) / total) if total > 0 else 0}
                for name, times in self.records.items()}


def get_gpu_memory():
    return {
        "allocated_MB": torch.cuda.memory_allocated() / 1e6,
        "reserved_MB": torch.cuda.memory_reserved() / 1e6,
        "max_allocated_MB": torch.cuda.max_memory_allocated() / 1e6,
        "max_reserved_MB": torch.cuda.max_memory_reserved() / 1e6,
    }


def reset_memory_stats():
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()


def print_system_info():
    print(f"{'=' * 80}")
    print("SYSTEM INFO")
    print(f"{'=' * 80}")
    print(f"  PyTorch: {torch.__version__}")
    print(f"  CUDA: {torch.version.cuda}")
    gpu_props = torch.cuda.get_device_properties(0)
    print(f"  GPU: {gpu_props.name}")
    print(f"  GPU Memory: {gpu_props.total_memory / 1e9:.1f} GB")
    print(f"  SMs: {gpu_props.multi_processor_count}")


# ============================================================================
# ADAPT THIS SECTION: Model Loading
# ============================================================================

def load_model_and_inputs(batch_size=1):
    """
    Load your model and create dummy inputs.

    ADAPT THIS FUNCTION for your workload:
    - Replace the placeholder model with your actual model
    - Create dummy inputs matching your model's expected format
    - Return (model, dummy_inputs_dict)

    dummy_inputs_dict should be a dict that can be unpacked into model():
        output = model(**dummy_inputs_dict)
    """
    # === PLACEHOLDER — REPLACE WITH YOUR MODEL ===
    # Example: HuggingFace model
    # from transformers import AutoModel
    # model = AutoModel.from_pretrained("path/to/weights", trust_remote_code=True)
    # model.eval().to(device="cuda", dtype=torch.bfloat16)

    model = torch.nn.Sequential(
        torch.nn.Linear(512, 2048),
        torch.nn.GELU(),
        torch.nn.Linear(2048, 2048),
        torch.nn.GELU(),
        torch.nn.Linear(2048, 512),
    ).cuda().to(dtype=torch.bfloat16).eval()

    dummy_input = torch.randn(batch_size, 128, 512, device="cuda", dtype=torch.bfloat16)
    # === END PLACEHOLDER ===

    return model, dummy_input


# ============================================================================
# ADAPT THIS SECTION: Phased Inference with NVTX Markers
# ============================================================================

def run_inference(model, inputs, use_nvtx=False):
    """Run one inference pass. Override for complex models."""
    with torch.inference_mode():
        if use_nvtx:
            torch.cuda.nvtx.range_push("inference")

        output = model(inputs)

        if use_nvtx:
            torch.cuda.nvtx.range_pop()
    return output


def run_inference_phased(model, inputs, timer, use_nvtx=False):
    """
    Run inference with per-phase timing and NVTX markers.

    ADAPT THIS for your model's phases. Example phases:
    - prepare_input
    - encoder_forward
    - decoder_forward
    - postprocess
    """
    with torch.inference_mode():
        # === ADAPT: Split into your model's phases ===
        with timer.phase("forward"):
            if use_nvtx:
                torch.cuda.nvtx.range_push("forward")
            output = model(inputs)
            if use_nvtx:
                torch.cuda.nvtx.range_pop()
        # === END ADAPT ===
    return output


# ============================================================================
# Profiling Modes
# ============================================================================

def analyze_architecture(model):
    """Parameter count per component."""
    print(f"\n{'=' * 80}")
    print("ARCHITECTURE ANALYSIS")
    print(f"{'=' * 80}")

    results = {}
    total = 0
    for name, module in model.named_children():
        params = sum(p.numel() for p in module.parameters())
        total += params
        print(f"  {name}: {params/1e6:.2f}M params")
        results[name] = params

    print(f"  TOTAL: {total/1e6:.2f}M params")

    weight_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"  Weight memory: {weight_bytes / 1e6:.1f} MB ({weight_bytes / 1e9:.2f} GB)")
    results["_weight_bytes"] = weight_bytes

    return results


def profile_single(model, inputs, num_warmup=3, num_runs=10,
                    export_trace=True, use_nvtx=True, batch_size=1):
    """Profile a single configuration."""
    print(f"\n{'=' * 80}")
    print(f"PROFILING: batch_size={batch_size}, warmup={num_warmup}, runs={num_runs}")
    print(f"{'=' * 80}")

    # Warmup
    print(f"  Warming up ({num_warmup} iterations)...")
    for _ in range(num_warmup):
        run_inference(model, inputs)
    torch.cuda.synchronize()

    # Phase-level profiling
    timer = PhaseTimer()
    reset_memory_stats()

    for _ in range(num_runs):
        run_inference_phased(model, inputs, timer, use_nvtx=use_nvtx)

    mem = get_gpu_memory()
    print(f"\n  Memory: current={mem['allocated_MB']:.1f} MB, peak={mem['max_allocated_MB']:.1f} MB")

    timing_summary = timer.summary()

    # PyTorch Profiler trace
    if export_trace:
        print(f"\n  Exporting PyTorch profiler trace...")
        from torch.profiler import profile, ProfilerActivity

        with profile(
            activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
            record_shapes=True,
            with_stack=True,
            profile_memory=True,
        ) as prof:
            run_inference(model, inputs, use_nvtx=True)

        trace_path = str(TRACE_DIR / f"trace_bs{batch_size}.json")
        prof.export_chrome_trace(trace_path)
        print(f"  Trace saved to: {trace_path}")

        print(f"\n--- Top 30 CUDA kernels by total time ---")
        kernel_table = prof.key_averages().table(sort_by="cuda_time_total", row_limit=30)
        print(kernel_table)

        kernel_path = OUTPUT_DIR / f"kernel_summary_bs{batch_size}.txt"
        with open(kernel_path, "w") as f:
            f.write(prof.key_averages().table(sort_by="cuda_time_total", row_limit=100))
        print(f"  Kernel summary saved to: {kernel_path}")

    return timing_summary, mem


def profile_batch_sweep(model_loader_fn, num_warmup=3, num_runs=5):
    """Profile across different batch sizes."""
    print(f"\n{'=' * 80}")
    print("BATCH SIZE SWEEP")
    print(f"{'=' * 80}")

    results = {}
    for bs in BATCH_SIZES:
        print(f"\n--- Batch size: {bs} ---")
        try:
            reset_memory_stats()
            model, inputs = model_loader_fn(batch_size=bs)
            timing, mem = profile_single(
                model, inputs, num_warmup=num_warmup, num_runs=num_runs,
                export_trace=False, use_nvtx=False, batch_size=bs,
            )
            results[bs] = {"timing": timing, "memory": mem}
        except torch.cuda.OutOfMemoryError:
            print(f"  OOM at batch_size={bs}, stopping sweep")
            break
        except Exception as e:
            print(f"  Error at batch_size={bs}: {e}")
            break

    # Print comparison
    if results:
        print(f"\n{'=' * 80}")
        print("BATCH SIZE COMPARISON")
        print(f"{'=' * 80}")
        print(f"{'Batch':>6} {'Total (ms)':>12} {'Peak Mem (MB)':>14}")
        print(f"{'-' * 35}")
        for bs, data in results.items():
            total = sum(v["avg_ms"] for v in data["timing"].values())
            peak_mem = data["memory"]["max_allocated_MB"]
            print(f"  {bs:>4} {total:>12.2f} {peak_mem:>14.1f}")

    return results


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="GPU Workload Profiling")
    parser.add_argument("--mode", type=str, default="full",
                        choices=["full", "single-step", "batch-sweep", "arch-analysis"],
                        help="Profiling mode")
    parser.add_argument("--num-runs", type=int, default=10, help="Number of timed runs")
    parser.add_argument("--num-warmup", type=int, default=3, help="Number of warmup runs")
    parser.add_argument("--batch-size", type=int, default=1, help="Batch size (single-step mode)")
    args = parser.parse_args()

    print_system_info()

    all_results = {}

    if args.mode in ["full", "arch-analysis"]:
        model, inputs = load_model_and_inputs(batch_size=1)
        arch = analyze_architecture(model)
        all_results["architecture"] = {k: int(v) for k, v in arch.items()}

    if args.mode in ["full", "single-step"]:
        model, inputs = load_model_and_inputs(batch_size=args.batch_size)
        timing, mem = profile_single(
            model, inputs, num_warmup=args.num_warmup, num_runs=args.num_runs,
            batch_size=args.batch_size,
        )
        all_results["single_inference"] = {"timing": timing, "memory": mem}

    if args.mode in ["full", "batch-sweep"]:
        batch_results = profile_batch_sweep(load_model_and_inputs)
        all_results["batch_sweep"] = {
            str(k): {"timing": v["timing"], "memory": v["memory"]}
            for k, v in batch_results.items()
        }

    # Save results
    results_path = OUTPUT_DIR / f"profiling_results_{args.mode}.json"
    with open(results_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    main()
