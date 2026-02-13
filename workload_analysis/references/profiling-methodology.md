# Profiling Methodology

Three tools at increasing depth. Always use them in this order.

## 1. GPU-Synchronized Timing (Prerequisite)

**NEVER use `time.time()` for GPU operations.** CPU and GPU execute asynchronously.

```python
import torch

class CUDATimer:
    """GPU-synchronized timer using CUDA events."""
    def __init__(self):
        self.start_event = torch.cuda.Event(enable_timing=True)
        self.end_event = torch.cuda.Event(enable_timing=True)

    def start(self):
        self.start_event.record()

    def stop(self):
        self.end_event.record()
        torch.cuda.synchronize()  # CRITICAL: wait for GPU
        return self.start_event.elapsed_time(self.end_event)  # ms
```

### Phase-Level Timing with Context Manager

```python
from contextlib import contextmanager
import numpy as np

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

    def summary(self):
        total = sum(np.mean(t) for t in self.records.values())
        for name, times in sorted(self.records.items(), key=lambda x: -np.mean(x[1])):
            avg = np.mean(times)
            pct = 100 * avg / total if total > 0 else 0
            print(f"  {name:<40} {avg:>10.3f} ms  ({pct:>5.1f}%)")
        print(f"  {'TOTAL':<40} {total:>10.3f} ms")
        return {name: {"avg_ms": float(np.mean(t)), "std_ms": float(np.std(t))}
                for name, t in self.records.items()}
```

## 2. NVTX Markers

NVTX ranges let NSight tools identify your custom phases. Add these BEFORE profiling.

```python
# Basic usage:
torch.cuda.nvtx.range_push("phase_name")
# ... GPU work ...
torch.cuda.nvtx.range_pop()

# Nested (for sub-phases):
torch.cuda.nvtx.range_push("outer_phase")
for i in range(N):
    torch.cuda.nvtx.range_push(f"iteration_{i}")
    # ... work ...
    torch.cuda.nvtx.range_pop()
torch.cuda.nvtx.range_pop()
```

## 3. Warmup (Essential)

```python
# ALWAYS warm up before profiling. First run includes:
# - CUDA context initialization
# - JIT compilation (torch.compile, cuDNN autotuner)
# - Memory allocator warmup
# - cuBLAS handle creation

NUM_WARMUP = 3
for _ in range(NUM_WARMUP):
    with torch.inference_mode():
        _ = model(dummy_input)
torch.cuda.synchronize()

# NOW start profiling
```

## 4. Tool 1: PyTorch Profiler (Fast, Always First)

```python
from torch.profiler import profile, ProfilerActivity

with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    with_stack=True,
    profile_memory=True,
) as prof:
    with torch.inference_mode():
        output = model(dummy_input)

# Export Chrome trace (view in chrome://tracing or ui.perfetto.dev)
prof.export_chrome_trace("traces/trace.json")

# Print top CUDA kernels by total GPU time
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=30))
```

**What this tells you:**
- Which CUDA kernels consume the most time
- CPU vs GPU time breakdown
- Memory allocation patterns
- Chrome trace gives a visual timeline

## 5. Tool 2: NSight Systems (nsys) — Timeline

### Basic Command

```bash
nsys profile \
    -o profiles/workload_nsys \
    --trace=cuda,nvtx,osrt \
    -f true \
    python scripts/profile_workload.py --mode single-step --num-runs 1 --num-warmup 3
```

**Key flags:**
- `-o <path>`: output file (without .nsys-rep extension)
- `--trace=cuda,nvtx,osrt`: capture CUDA API + NVTX markers + OS runtime
- `-f true`: force overwrite existing profile

### Extract Statistics

```bash
# CUDA kernel summary:
nsys stats --report cuda_gpu_kern_sum profiles/workload_nsys.nsys-rep

# NVTX range timing:
nsys stats --report nvtx_sum profiles/workload_nsys.nsys-rep

# All stats:
nsys stats profiles/workload_nsys.nsys-rep
```

### What nsys Tells You

- **Timeline**: which phases run when, are there idle gaps?
- **Kernel counts**: how many CUDA kernels per phase?
- **Top kernels**: which kernels consume the most GPU time?
- **NVTX ranges**: how long does each annotated phase take?
- **Memory copies**: are there unexpected host-to-device transfers?

### nsys Pitfalls

- `--force-overwrite true` may fail on some versions — use `-f true`
- `--cuda-memory-usage=true` can cause ambiguity errors — remove it if nsys complains

## 6. Tool 3: NSight Compute (ncu) — Deep Kernel Analysis

### IMPORTANT: ncu is VERY SLOW

ncu replays each kernel 17+ times to collect metrics. A 50ms inference can take **5-30 minutes** to profile.

### Strategies to Limit Scope

```bash
# Strategy 1: Profile only specific NVTX ranges (RECOMMENDED)
ncu --set full --nvtx --nvtx-include "phase_name/" \
    --profile-from-start off \
    -o profiles/workload_ncu_phase -f \
    python scripts/ncu_profile_workload.py

# Strategy 2: Skip first N kernels, capture only M kernels
ncu --set full -s 700 -c 10 \
    -o profiles/workload_ncu_top10 -f \
    python scripts/ncu_profile_workload.py

# Strategy 3: Filter by kernel name regex
ncu --set full -k "regex:gemm|cutlass" -c 5 \
    -o profiles/workload_ncu_gemm -f \
    python scripts/ncu_profile_workload.py
```

### Metric Sets

| Set | Speed | Contents |
|-----|-------|----------|
| `--set basic` | Fast | Duration, SM/memory throughput |
| `--set roofline` | Medium | + Roofline analysis data |
| `--set full` | Slow | + Occupancy, stalls, IPC (most detailed) |

For research, use `--set full` on representative kernels.

### cudaProfilerStart/Stop in Script

```python
# Tell NCU exactly when to start/stop:
torch.cuda.synchronize()
torch.cuda.cudart().cudaProfilerStart()
# ... profiled code (with NVTX markers) ...
torch.cuda.synchronize()
torch.cuda.cudart().cudaProfilerStop()
```

Use `--profile-from-start off` in the ncu command to honor these markers.

### Export as CSV for Programmatic Analysis

```bash
ncu --import profiles/workload.ncu-rep --csv --page details > ncu_output.csv
```

### Key NCU Metrics

| Metric Name | What It Tells You |
|-------------|-------------------|
| `Duration` | Kernel execution time (ns) |
| `Compute (SM) Throughput` | % of peak SM compute used |
| `Memory Throughput` | % of peak memory bandwidth used |
| `Achieved Occupancy` | % of max warps that are active |
| `Theoretical Occupancy` | Max possible occupancy given register/shared memory |
| `Achieved Active Warps Per SM` | Actual concurrent warps (max 48 on Ada) |
| `L2 Hit Rate` | Cache efficiency |
| `Executed Ipc Active` | Instructions per cycle when SM is active |
| `Stall Long Scoreboard` | % stalled waiting for memory (memory-bound indicator) |
| `Stall Short Scoreboard` | % stalled waiting for compute pipeline |
| `Stall Math Pipe Throttle` | % stalled because math pipes are full |
| `Stall Barrier` | % stalled at synchronization barriers |
| `Stall Not Selected` | % stalled because warp was not scheduled |

### Bottleneck Classification from NCU Data

```python
sm_throughput = metrics["Compute (SM) Throughput"]   # percentage
mem_throughput = metrics["Memory Throughput"]          # percentage

if mem_throughput > sm_throughput * 1.5:
    classification = "MEMORY-BOUND"
elif sm_throughput > mem_throughput * 1.5:
    classification = "COMPUTE-BOUND"
else:
    classification = "BALANCED"
```
