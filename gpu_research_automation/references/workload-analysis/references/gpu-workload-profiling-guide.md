# GPU Workload Profiling Guide — A Toy Example for Claude Code Agents

> **What this is**: A step-by-step reference showing how a Claude Code agent set up an environment, loaded a large ML model (NVIDIA GR00T N1.6 VLA, 3.3B params), profiled it with PyTorch Profiler / NSight Systems / NSight Compute, analyzed bottlenecks, and generated publication-quality visualizations — all from the command line.
>
> **Use this as**: A template when you need to profile any GPU workload. Adapt the model-specific parts; the profiling methodology is general.

---

## Table of Contents

1. [Project Structure](#1-project-structure)
2. [Phase 1: Environment Setup](#2-phase-1-environment-setup)
3. [Phase 2: Model Download & Loading](#3-phase-2-model-download--loading)
4. [Phase 3: Architecture Analysis](#4-phase-3-architecture-analysis)
5. [Phase 4: PyTorch Profiler Profiling](#5-phase-4-pytorch-profiler-profiling)
6. [Phase 5: NSight Systems (nsys) Profiling](#6-phase-5-nsight-systems-nsys-profiling)
7. [Phase 6: NSight Compute (ncu) Deep Kernel Profiling](#7-phase-6-nsight-compute-ncu-deep-kernel-profiling)
8. [Phase 7: Analysis & Visualization](#8-phase-7-analysis--visualization)
9. [Pitfalls & Lessons Learned](#9-pitfalls--lessons-learned)
10. [Tool Reference Card](#10-tool-reference-card)

---

## 1. Project Structure

```
project_root/
├── vla_env/                    # Python virtual environment
├── models/
│   ├── Isaac-GR00T/            # Model source code (git clone)
│   └── weights/
│       └── groot-n1.6-3b/      # Downloaded model weights
├── scripts/
│   ├── profile_groot.py        # Main profiling script (PyTorch profiler + NVTX)
│   ├── ncu_profile_groot.py    # NCU-targeted profiling (minimal overhead)
│   ├── parse_ncu_results.py    # Parse NCU CSV → summary statistics
│   ├── parse_ncu_detailed.py   # Parse NCU CSV → occupancy, stalls, roofline
│   ├── plot_roofline.py        # Generate roofline plot
│   ├── plot_timeline.py        # Generate execution timeline
│   ├── run_nsys_profile.sh     # NSight Systems wrapper
│   └── run_ncu_profile.sh      # NSight Compute wrapper
├── profiles/                   # .nsys-rep and .ncu-rep binary profiles
├── traces/                     # Chrome trace JSON files
└── analysis/                   # Markdown reports, PNG/PDF figures, JSON data
```

**Key principle**: Keep profiling scripts, raw profiles, and analysis outputs in separate directories. Profile files can be huge (100MB-1GB for NCU).

---

## 2. Phase 1: Environment Setup

### 2.1 Create Virtual Environment

```bash
python3 -m venv /path/to/project/vla_env
source /path/to/project/vla_env/bin/activate
```

### 2.2 Install PyTorch with CUDA

```bash
# Check your CUDA version first
nvcc --version

# Install PyTorch matching your CUDA version
# For CUDA 12.4+:
pip install torch torchvision torchaudio

# Verify CUDA is available:
python -c "import torch; print(torch.cuda.is_available()); print(torch.version.cuda)"
```

### 2.3 Install Model-Specific Dependencies

```bash
# Clone the model repo
git clone https://github.com/NVIDIA/Isaac-GR00T.git models/Isaac-GR00T

# Install the package in editable mode (no deps to avoid conflicts)
pip install --no-deps -e models/Isaac-GR00T

# Install remaining dependencies from pyproject.toml
pip install transformers accelerate pillow numpy matplotlib
```

### 2.4 Install flash-attn (Common Pain Point)

flash-attn is a compiled CUDA extension. It frequently fails to build. The reliable approach:

```bash
# Step 1: Install wheel first (prevents "No module named 'wheel'" error)
pip install wheel

# Step 2: Install with --no-build-isolation (uses already-installed torch)
pip install flash-attn==2.7.4.post1 --no-build-isolation

# This compiles from source — takes 5-15 minutes. If it fails:
# - Check that nvcc version matches torch CUDA version
# - Ensure enough disk space for compilation (~5 GB temp)
# - Try: pip install flash-attn --no-build-isolation (latest version)
```

**PITFALL**: `pip install flash-attn` (without `--no-build-isolation`) will fail with `ModuleNotFoundError: No module named 'torch'` because build isolation creates a clean environment without torch.

### 2.5 Verify Profiling Tools

```bash
# NSight Systems (for timeline profiling)
nsys --version
# Expected: 2025.x.x or similar

# NSight Compute (for per-kernel metrics)
ncu --version
# Expected: 2025.x.x or similar

# If not found, install CUDA toolkit or find them at:
# /usr/local/cuda/bin/nsys
# /usr/local/cuda/bin/ncu
```

### 2.6 Environment Versions Used in This Example

| Tool | Version |
|------|---------|
| Python | 3.10.12 |
| PyTorch | 2.7.1 |
| CUDA (nvcc) | 13.0 |
| flash-attn | 2.7.4.post1 |
| transformers | 4.51.3 |
| NSight Compute | 2025.3.1.0 |
| NSight Systems | 2025.3.2 |
| GPU | RTX 4070 Ti SUPER (16 GB, Ada Lovelace) |
| Driver | 580.95.05 |

---

## 3. Phase 2: Model Download & Loading

### 3.1 Download Weights

```bash
# Using huggingface-cli (if model is on HuggingFace)
pip install huggingface-hub
huggingface-cli download nvidia/GR00T-N1.6-3B --local-dir models/weights/groot-n1.6-3b

# Or use Python:
# from huggingface_hub import snapshot_download
# snapshot_download("nvidia/GR00T-N1.6-3B", local_dir="models/weights/groot-n1.6-3b")
```

### 3.2 Load Model in Python

```python
import torch
import sys
sys.path.insert(0, "models/Isaac-GR00T")  # Add model repo to path

# IMPORTANT: Import model module to register custom model classes
import gr00t.model  # noqa — registers AutoModel classes

from transformers import AutoModel, AutoProcessor

# Load model
model = AutoModel.from_pretrained(
    "models/weights/groot-n1.6-3b",
    trust_remote_code=True  # Required for custom model classes
)
model.eval()
model.to(device="cuda", dtype=torch.bfloat16)

# Load processor (tokenizer + image processor)
processor = AutoProcessor.from_pretrained(
    "models/weights/groot-n1.6-3b",
    trust_remote_code=True
)
processor.eval()
```

**PITFALL**: The `import gr00t.model` line is critical. Without it, `AutoModel.from_pretrained()` won't know the custom model class and will fail with a cryptic error about unrecognized `model_type`.

### 3.3 Create Dummy Inputs

```python
import numpy as np
from gr00t.data.types import MessageType, VLAStepData
from gr00t.data.embodiment_tags import EmbodimentTag

embodiment_tag = EmbodimentTag("gr1")
modality_configs = processor.get_modality_configs()["gr1"]

# Build observation dict matching expected format
observation = {
    "video": {},
    "state": {},
    "language": {},
}

# Video inputs (random image as placeholder)
for key in modality_configs["video"].modality_keys:
    n_frames = len(modality_configs["video"].delta_indices)
    observation["video"][key] = np.random.randint(
        0, 255, size=(1, n_frames, 256, 256, 3), dtype=np.uint8
    )

# State inputs (random joint angles)
for key in modality_configs["state"].modality_keys:
    n_steps = len(modality_configs["state"].delta_indices)
    dim = 7  # Adjust per embodiment
    observation["state"][key] = np.random.randn(1, n_steps, dim).astype(np.float32)

# Language inputs
for key in modality_configs["language"].modality_keys:
    observation["language"][key] = [["pick up the object"]]

# Process through the pipeline
vla_data = VLAStepData(
    images=observation["video"],
    states=observation["state"],
    actions={},
    text=observation["language"][list(observation["language"].keys())[0]][0],
    embodiment=embodiment_tag,
)
messages = [{"type": MessageType.EPISODE_STEP.value, "content": vla_data}]
processed = [processor(messages)]
collated = processor.collator(processed)

# Cast to bfloat16
def to_bf16(x):
    if isinstance(x, torch.Tensor) and torch.is_floating_point(x):
        return x.to(dtype=torch.bfloat16)
    elif isinstance(x, dict):
        return {k: to_bf16(v) for k, v in x.items()}
    elif isinstance(x, list):
        return [to_bf16(v) for v in x]
    return x

collated = to_bf16(collated)

# Run inference
with torch.inference_mode():
    output = model.get_action(**collated)
```

**PITFALL**: The `collated` dict has structure `{"inputs": {...}}`. The top-level `model.get_action(**collated)` unpacks correctly, but if you call `model.prepare_input()` directly, you need `collated["inputs"]`, NOT `collated` itself. This caused a `KeyError: 'input_ids'` that was tricky to debug.

---

## 4. Phase 3: Architecture Analysis

### 4.1 Parameter Counting

```python
def analyze_architecture(model):
    """Count parameters per component."""
    total = 0
    for name, module in model.named_children():
        params = sum(p.numel() for p in module.parameters())
        total += params
        print(f"{name}: {params/1e6:.2f}M params")
    print(f"TOTAL: {total/1e6:.2f}M params")

    # Memory footprint
    weight_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"Weight memory: {weight_bytes / 1e9:.2f} GB")
```

### 4.2 FLOPS Estimation (Roofline Analysis)

```python
# For a transformer-based model, estimate FLOPS per inference:
# Linear layer: 2 × M × N × K FLOPs
# Self-attention: 4 × seq² × dim × 2
# Cross-attention: 4 × seq_q × seq_kv × dim × 2
# FFN: 2 × 4 × dim² × seq × 2 (typical 4x expansion)

# Arithmetic intensity = total FLOPs / total bytes read
# Compare to ridge point = peak_TFLOPS / peak_BW_GB/s

peak_compute = 44.1e12     # BF16 TFLOPS (check your GPU spec)
peak_bw = 672e9            # Memory bandwidth in bytes/s
ridge_point = peak_compute / peak_bw  # FLOP/byte

# If your arithmetic intensity < ridge point → memory-bound
# If your arithmetic intensity > ridge point → compute-bound
```

---

## 5. Phase 4: PyTorch Profiler Profiling

### 5.1 GPU-Synchronized Timing

**Do NOT use `time.time()` for GPU operations.** CPU and GPU run asynchronously. Use CUDA events:

```python
class CUDATimer:
    """GPU-synchronized timer using CUDA events."""
    def __init__(self):
        self.start_event = torch.cuda.Event(enable_timing=True)
        self.end_event = torch.cuda.Event(enable_timing=True)

    def start(self):
        self.start_event.record()

    def stop(self):
        self.end_event.record()
        torch.cuda.synchronize()  # CRITICAL: wait for GPU to finish
        return self.start_event.elapsed_time(self.end_event)  # Returns ms
```

### 5.2 Phase-Level Timing with Context Manager

```python
from contextlib import contextmanager

class PhaseTimer:
    def __init__(self):
        self.records = {}

    @contextmanager
    def phase(self, name):
        timer = CUDATimer()
        timer.start()
        yield
        elapsed = timer.stop()
        self.records.setdefault(name, []).append(elapsed)

# Usage:
timer = PhaseTimer()
with timer.phase("backbone_forward"):
    backbone_outputs = model.backbone(inputs)
with timer.phase("dit_forward"):
    dit_output = model.action_head(backbone_outputs, action_inputs)
```

### 5.3 NVTX Markers (for NSight Systems / NCU integration)

```python
# NVTX ranges let NSight tools identify your phases:
torch.cuda.nvtx.range_push("backbone_forward")
backbone_outputs = model.backbone(inputs)
torch.cuda.nvtx.range_pop()

torch.cuda.nvtx.range_push("dit_denoising_loop")
for t in range(4):
    torch.cuda.nvtx.range_push(f"denoise_step_{t}")
    # ... denoising step ...
    torch.cuda.nvtx.range_pop()
torch.cuda.nvtx.range_pop()
```

### 5.4 PyTorch Profiler Trace Export

```python
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    with_stack=True,
    profile_memory=True,
) as prof:
    with torch.inference_mode():
        output = model.get_action(**collated)

# Export Chrome trace (view in chrome://tracing or Perfetto)
prof.export_chrome_trace("traces/trace_bs1.json")

# Print top CUDA kernels by time
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=30))
```

### 5.5 Warmup Is Essential

```python
# ALWAYS warm up before profiling. First run includes:
# - CUDA context initialization
# - JIT compilation
# - Memory allocation
# - cuBLAS handle creation

NUM_WARMUP = 3
for _ in range(NUM_WARMUP):
    with torch.inference_mode():
        _ = model.get_action(**collated)
torch.cuda.synchronize()

# NOW start profiling
```

---

## 6. Phase 5: NSight Systems (nsys) Profiling

### 6.1 Basic nsys Command

```bash
nsys profile \
    -o profiles/model_nsys \
    --trace=cuda,nvtx,osrt \
    -f true \
    python scripts/profile_script.py --mode single-step --num-runs 1 --num-warmup 3
```

**Key flags**:
- `-o`: output file path (without .nsys-rep extension)
- `--trace=cuda,nvtx,osrt`: capture CUDA API + NVTX markers + OS runtime
- `-f true`: force overwrite existing profile

**PITFALL**: `--force-overwrite true` may cause an option parsing error on some nsys versions. Use `-f true` instead.

**PITFALL**: `--cuda-memory-usage=true` can cause ambiguity errors on some versions. Remove it if nsys complains.

### 6.2 Extract Kernel Statistics from nsys

```bash
# After profiling, extract CUDA kernel summary:
nsys stats --report cuda_gpu_kern_sum profiles/model_nsys.nsys-rep

# Extract NVTX ranges (to see phase timing):
nsys stats --report nvtx_sum profiles/model_nsys.nsys-rep

# Output all stats:
nsys stats profiles/model_nsys.nsys-rep
```

### 6.3 What nsys Tells You

- **Timeline**: Which phases run when, are there gaps?
- **Kernel counts**: How many CUDA kernels per phase?
- **Top kernels**: Which kernels consume the most time?
- **NVTX ranges**: How long does each annotated phase take?
- **Memory copies**: Are there unexpected host↔device transfers?

---

## 7. Phase 6: NSight Compute (ncu) Deep Kernel Profiling

### 7.1 Important: NCU is VERY SLOW

NCU replays each kernel 17+ times to collect metrics. A 50ms inference can take **5-30 minutes** to profile. Strategies:

```bash
# Strategy 1: Profile only specific NVTX ranges
ncu --set roofline --nvtx --nvtx-include "denoise_step_0/" \
    --profile-from-start off \
    -o profiles/model_ncu_step0 -f \
    python scripts/ncu_profiling_script.py

# Strategy 2: Skip first N kernels, capture only M kernels
ncu --set full -s 700 -c 10 \
    -o profiles/model_ncu_top10 -f \
    python scripts/ncu_profiling_script.py

# Strategy 3: Filter by kernel name
ncu --set full -k "regex:ampere|cutlass" -c 5 \
    -o profiles/model_ncu_gemm -f \
    python scripts/ncu_profiling_script.py
```

### 7.2 NCU Metric Sets

```bash
# --set basic    → Fast, minimal metrics
# --set roofline → Roofline analysis (memory throughput, compute throughput)
# --set full     → Everything including occupancy, stalls (slowest but most detailed)
```

For architecture research, you want `--set full` on representative kernels to get occupancy and warp stall data.

### 7.3 Use cudaProfilerStart/Stop in Your Script

```python
# Tell NCU exactly when to start/stop profiling:
torch.cuda.synchronize()
torch.cuda.cudart().cudaProfilerStart()

# ... your profiled code here ...

torch.cuda.synchronize()
torch.cuda.cudart().cudaProfilerStop()
```

Then use `--profile-from-start off` in the ncu command to honor these markers.

### 7.4 Parsing NCU Reports

```bash
# Export as CSV for programmatic analysis:
ncu --import profiles/model_ncu.ncu-rep --csv --page details > ncu_output.csv
```

Then parse with Python:

```python
import csv
import io
import subprocess
from collections import defaultdict

result = subprocess.run(
    ["ncu", "--import", "profiles/model.ncu-rep", "--csv", "--page", "details"],
    capture_output=True, text=True, timeout=300
)

reader = csv.DictReader(io.StringIO(result.stdout))
kernel_data = defaultdict(dict)

for row in reader:
    kid = row["ID"]
    metric = row["Metric Name"]
    value = row["Metric Value"]
    kernel_data[kid][metric] = value
```

### 7.5 Key NCU Metrics to Extract

| Metric Name | What It Tells You |
|-------------|-------------------|
| `Duration` | Kernel execution time (ns) |
| `Compute (SM) Throughput` | % of peak SM compute used |
| `Memory Throughput` | % of peak memory bandwidth used |
| `Achieved Occupancy` | % of max warps that are active |
| `Theoretical Occupancy` | Max possible occupancy given register/shared memory usage |
| `Achieved Active Warps Per SM` | Actual concurrent warps (out of 48 max on Ada) |
| `L2 Hit Rate` | Cache efficiency |
| `Executed Ipc Active` | Instructions per cycle when SM is active |
| `Stall Long Scoreboard` | % stalled waiting for memory (memory-bound indicator) |
| `Stall Short Scoreboard` | % stalled waiting for compute (compute pipeline) |
| `Stall Math Pipe Throttle` | % stalled because math pipes are full |

### 7.6 Bottleneck Classification from NCU Data

```python
# For each kernel:
sm_throughput = metrics["Compute (SM) Throughput"]  # percentage
mem_throughput = metrics["Memory Throughput"]         # percentage

if mem_throughput > sm_throughput * 1.5:
    classification = "MEMORY-BOUND"
elif sm_throughput > mem_throughput * 1.5:
    classification = "COMPUTE-BOUND"
else:
    classification = "BALANCED"
```

---

## 8. Phase 7: Analysis & Visualization

### 8.1 Roofline Plot

```python
import matplotlib.pyplot as plt
import numpy as np

# GPU specs (look these up for YOUR GPU)
PEAK_TFLOPS = 44.1       # BF16 tensor core TFLOPS
PEAK_BW_GBS = 672         # GB/s memory bandwidth
RIDGE_POINT = PEAK_TFLOPS * 1e3 / PEAK_BW_GBS  # FLOP/byte

oi_range = np.logspace(-1, 3, 500)
roofline = np.minimum(PEAK_TFLOPS * 1e3, PEAK_BW_GBS * oi_range)

fig, ax = plt.subplots(figsize=(10, 7))
ax.loglog(oi_range, roofline, 'k-', linewidth=2, label='Roofline')

# Plot your measured data points:
# (arithmetic_intensity, achieved_throughput_gflops)
ax.scatter(30.05, 0.306 * PEAK_TFLOPS * 1e3, s=200, c='red', label='DiT GEMM')
ax.set_xlabel('Arithmetic Intensity (FLOP/byte)')
ax.set_ylabel('Throughput (GFLOP/s)')
```

### 8.2 Execution Timeline

```python
# Stacked bar chart for batch size comparison:
batch_sizes = [1, 2, 4, 8]
backbone_ms = [19, 26, 39, 67]
dit_ms = [35, 35, 46, 70]

fig, ax = plt.subplots()
ax.bar(range(len(batch_sizes)), backbone_ms, label='Backbone')
ax.bar(range(len(batch_sizes)), dit_ms, bottom=backbone_ms, label='DiT')
ax.axhline(y=50, color='green', linestyle='--', label='Real-time target')
```

### 8.3 Key Outputs to Generate

| Output | Purpose |
|--------|---------|
| Roofline plot | Shows if workload is memory-bound or compute-bound |
| Execution timeline | Shows phase durations and serial bottlenecks |
| Kernel category breakdown | Which kernel types dominate (GEMM, attention, elementwise, etc.) |
| Batch scaling chart | How latency changes with batch size |
| SM utilization over time | Visual proof of GPU underutilization |

---

## 9. Pitfalls & Lessons Learned

### Environment Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| flash-attn build fails | `No module named 'torch'` | Use `--no-build-isolation` |
| flash-attn build fails | `No module named 'wheel'` | `pip install wheel` first, then retry |
| torch CUDA mismatch | `CUDA error: no kernel image` | Ensure torch CUDA version matches nvcc version |
| Model class not found | `KeyError: 'model_type'` | `import gr00t.model` before `AutoModel.from_pretrained` |

### Profiling Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| GPU timing is wrong | CPU time ≠ GPU time | Use `torch.cuda.synchronize()` or CUDA events, NOT `time.time()` |
| First run is slow | 2-5x slower than subsequent runs | Always warm up 3+ iterations before measuring |
| nsys `--force-overwrite` fails | Option parsing error | Use `-f true` instead |
| nsys `--cuda-memory-usage` fails | Ambiguous option error | Remove the flag |
| ncu is extremely slow | Hours for full inference | Use `--nvtx-include` to profile specific phases only |
| ncu `--set full` on all kernels | Takes forever | Use `-s N -c M` to skip N kernels and capture only M |
| NCU occupancy shows 0% | Missing data in CSV | Use `--set full` instead of `--set roofline` |
| PyTorch profiler overhead | Profiler itself adds latency | Profile separately from timing measurements |

### Data Structure Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| Collated dict structure | `KeyError: 'input_ids'` | `collated["inputs"]` not `collated` — the top level has an `"inputs"` key |
| `torch.cuda.get_device_properties` | `AttributeError: total_mem` | Use `.total_memory` (not `.total_mem`) |
| NCU CSV parsing | Columns misaligned | Use Python `csv.DictReader`, not manual column splitting (kernel names contain commas) |

---

## 10. Tool Reference Card

### PyTorch Profiler Commands

```python
# Quick kernel table:
prof.key_averages().table(sort_by="cuda_time_total", row_limit=30)

# Chrome trace (open in chrome://tracing or ui.perfetto.dev):
prof.export_chrome_trace("trace.json")

# Memory stats:
torch.cuda.max_memory_allocated() / 1e6  # Peak MB
torch.cuda.memory_allocated() / 1e6      # Current MB
torch.cuda.reset_peak_memory_stats()     # Reset tracking
```

### NSight Systems (nsys) Commands

```bash
# Profile:
nsys profile -o output --trace=cuda,nvtx -f true python script.py

# View stats:
nsys stats output.nsys-rep
nsys stats --report cuda_gpu_kern_sum output.nsys-rep
nsys stats --report nvtx_sum output.nsys-rep

# Open in GUI:
nsys-ui output.nsys-rep
```

### NSight Compute (ncu) Commands

```bash
# Profile all kernels (slow!):
ncu --set full -o output -f python script.py

# Profile specific NVTX range:
ncu --set full --nvtx --nvtx-include "phase_name/" --profile-from-start off \
    -o output -f python script.py

# Profile specific kernel names:
ncu --set full -k "regex:gemm|cutlass" -c 5 -o output -f python script.py

# Skip first N kernels, capture M:
ncu --set full -s 700 -c 10 -o output -f python script.py

# Export CSV:
ncu --import output.ncu-rep --csv --page details > output.csv

# Open in GUI:
ncu-ui output.ncu-rep
```

### GPU Info Commands

```bash
# GPU details:
nvidia-smi --query-gpu=name,memory.total,driver_version,clocks.gr --format=csv

# Watch GPU utilization in real-time:
watch -n 0.5 nvidia-smi

# Check CUDA version:
nvcc --version

# Check GPU properties from Python:
python -c "import torch; p = torch.cuda.get_device_properties(0); \
  print(f'Name: {p.name}'); \
  print(f'SMs: {p.multi_processor_count}'); \
  print(f'Memory: {p.total_memory/1e9:.1f} GB')"
```

---

## Quick-Start Checklist for New Profiling Projects

```
[ ] 1. Create venv, install torch with correct CUDA version
[ ] 2. Install model dependencies (watch for flash-attn!)
[ ] 3. Verify model loads and runs inference on GPU
[ ] 4. Count parameters per component
[ ] 5. Add NVTX markers to each phase of inference
[ ] 6. Time each phase with CUDATimer (warmup first!)
[ ] 7. Run PyTorch profiler → export Chrome trace + kernel table
[ ] 8. Run nsys → get timeline + kernel summary
[ ] 9. Run ncu on key phases → get occupancy + throughput + stalls
[ ] 10. Compute arithmetic intensity → build roofline plot
[ ] 11. Classify kernels: memory-bound vs compute-bound
[ ] 12. Identify top bottlenecks with quantitative evidence
[ ] 13. Generate publication-quality figures
[ ] 14. Write bottleneck analysis with proposed solutions
```
