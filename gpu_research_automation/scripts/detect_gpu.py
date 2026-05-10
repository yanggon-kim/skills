#!/usr/bin/env python3
"""detect_gpu.py — emit gpu_spec.json from nvidia-smi.

Used by init_workspace.sh and re-runnable any time. Outputs JSON to stdout:

{
  "name": "NVIDIA GeForce RTX 5080",
  "compute_capability": "12.0",
  "memory_total_mib": 16384,
  "sm_count": 84,
  "peak_fp32_tflops": 56.3,
  "peak_bf16_tflops": 225.2,
  "peak_memory_bw_gbps": 960.0,
  "detected_at": "2026-05-10T14:23:11+09:00"
}

Some fields (peak FLOPS / BW) come from a small lookup table keyed on the GPU
name; if the GPU is unrecognized, those fields are null and the user must fill
them manually for Step 2 and Step 5.
"""

from __future__ import annotations

import datetime as _dt
import json
import re
import shutil
import subprocess
import sys


# Curated peaks for common GPUs. Sources: NVIDIA datasheets / whitepapers.
# Add entries as new GPUs become relevant; null = unknown, fill manually.
PEAKS = {
    # name match key                           fp32_tflops  bf16_tflops  bw_gbps
    "NVIDIA H100":                              ( 67.0,    989.0,        3000.0),
    "NVIDIA A100":                              ( 19.5,    312.0,        1555.0),
    "NVIDIA L40":                               ( 90.5,    181.0,        864.0),
    "NVIDIA RTX 6000":                          ( 91.1,    364.2,        960.0),
    "NVIDIA GeForce RTX 5080":                  ( 56.3,    225.2,        960.0),
    "NVIDIA GeForce RTX 5090":                  ( 104.8,   419.0,        1792.0),
    "NVIDIA GeForce RTX 4090":                  ( 82.6,    330.3,        1008.0),
    "NVIDIA GeForce RTX 4070 Ti SUPER":         ( 44.1,    176.4,        672.0),
    "NVIDIA GeForce RTX 4070":                  ( 29.1,    116.4,        504.0),
    "NVIDIA GeForce RTX 3090":                  ( 35.6,    142.3,        936.0),
    "NVIDIA GeForce RTX 3080":                  ( 29.8,    119.2,        760.0),
}


def lookup_peaks(name: str):
    """Match GPU name against PEAKS table; return (fp32, bf16, bw) or (None, None, None)."""
    for key, vals in PEAKS.items():
        if key in name:
            return vals
    return (None, None, None)


def main() -> int:
    if shutil.which("nvidia-smi") is None:
        print(json.dumps({"error": "nvidia-smi not found"}), file=sys.stderr)
        return 2

    # nvidia-smi query for the basics.
    result = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,compute_cap,memory.total",
            "--format=csv,noheader,nounits",
            "-i", "0",  # first GPU only; multi-GPU users can edit
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        print(json.dumps({"error": result.stderr.strip()}), file=sys.stderr)
        return result.returncode

    line = result.stdout.strip().split("\n")[0]
    parts = [p.strip() for p in line.split(",")]
    if len(parts) < 3:
        print(json.dumps({"error": f"unexpected nvidia-smi output: {line}"}), file=sys.stderr)
        return 3

    name = parts[0]
    compute_cap = parts[1]
    memory_mib = int(parts[2])

    # Try to read SM count via a second query.
    sm_count = None
    sm_result = subprocess.run(
        ["nvidia-smi", "--query-gpu=multiprocessor_count", "--format=csv,noheader,nounits", "-i", "0"],
        capture_output=True, text=True, check=False,
    )
    if sm_result.returncode == 0:
        try:
            sm_count = int(sm_result.stdout.strip().split("\n")[0])
        except (ValueError, IndexError):
            pass

    fp32, bf16, bw = lookup_peaks(name)

    spec = {
        "name": name,
        "compute_capability": compute_cap,
        "memory_total_mib": memory_mib,
        "sm_count": sm_count,
        "peak_fp32_tflops": fp32,
        "peak_bf16_tflops": bf16,
        "peak_memory_bw_gbps": bw,
        "detected_at": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    if fp32 is None:
        spec["peaks_status"] = (
            "GPU name not recognized in detect_gpu.py PEAKS table; "
            "fill peak_fp32_tflops / peak_bf16_tflops / peak_memory_bw_gbps manually "
            "from the device datasheet."
        )

    print(json.dumps(spec, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
