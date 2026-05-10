# Tool Reference Card

Quick-reference commands for all profiling tools. Copy-paste ready.

## System Info

```bash
# GPU details:
nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap,clocks.gr --format=csv

# Watch GPU utilization in real-time:
watch -n 0.5 nvidia-smi

# CUDA version:
nvcc --version

# GPU properties from Python:
python -c "
import torch
p = torch.cuda.get_device_properties(0)
print(f'Name: {p.name}')
print(f'Compute Capability: {p.major}.{p.minor}')
print(f'SMs: {p.multi_processor_count}')
print(f'Memory: {p.total_memory/1e9:.1f} GB')
print(f'CUDA: {torch.version.cuda}')
print(f'PyTorch: {torch.__version__}')
"
```

## PyTorch Profiler

```python
from torch.profiler import profile, ProfilerActivity

# Profile:
with profile(
    activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
    record_shapes=True,
    with_stack=True,
    profile_memory=True,
) as prof:
    with torch.inference_mode():
        output = model(input)

# Quick kernel table:
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=30))

# Chrome trace (view in chrome://tracing or ui.perfetto.dev):
prof.export_chrome_trace("traces/trace.json")

# Memory stats:
torch.cuda.max_memory_allocated() / 1e6   # Peak MB
torch.cuda.memory_allocated() / 1e6       # Current MB
torch.cuda.reset_peak_memory_stats()      # Reset tracking
```

## NSight Systems (nsys)

```bash
# Profile with CUDA + NVTX tracing:
nsys profile -o profiles/output --trace=cuda,nvtx,osrt -f true \
    python script.py

# View all stats:
nsys stats profiles/output.nsys-rep

# CUDA kernel summary:
nsys stats --report cuda_gpu_kern_sum profiles/output.nsys-rep

# NVTX range summary:
nsys stats --report nvtx_sum profiles/output.nsys-rep

# Open in GUI:
nsys-ui profiles/output.nsys-rep
```

## NSight Compute (ncu)

```bash
# Profile specific NVTX range (RECOMMENDED — limits scope):
ncu --set full --nvtx --nvtx-include "phase_name/" \
    --profile-from-start off -o profiles/output -f \
    python script.py

# Profile specific kernel names:
ncu --set full -k "regex:gemm|cutlass" -c 5 \
    -o profiles/output -f python script.py

# Skip first N kernels, capture M:
ncu --set full -s 700 -c 10 -o profiles/output -f python script.py

# Profile all kernels (SLOW — use sparingly):
ncu --set full -o profiles/output -f python script.py

# Export as CSV for scripted analysis:
ncu --import profiles/output.ncu-rep --csv --page details > output.csv

# Open in GUI:
ncu-ui profiles/output.ncu-rep
```

### ncu Metric Sets

| Flag | Speed | Use Case |
|------|-------|----------|
| `--set basic` | Fast | Quick check (duration, throughput) |
| `--set roofline` | Medium | Roofline analysis (SM + memory throughput) |
| `--set full` | Slow | Everything (occupancy, stalls, IPC) — for research |

## CUDA Timing (Python)

```python
# Correct GPU timing:
start = torch.cuda.Event(enable_timing=True)
end = torch.cuda.Event(enable_timing=True)
start.record()
# ... GPU work ...
end.record()
torch.cuda.synchronize()
elapsed_ms = start.elapsed_time(end)

# NVTX markers:
torch.cuda.nvtx.range_push("phase_name")
# ... GPU work ...
torch.cuda.nvtx.range_pop()

# cudaProfiler control (for ncu --profile-from-start off):
torch.cuda.cudart().cudaProfilerStart()
# ... profiled work ...
torch.cuda.cudart().cudaProfilerStop()
```

## Compiled Instruction Extraction

```bash
# Extract SASS (machine instructions) from binary or .cubin:
cuobjdump -sass ./executable > kernel.sass

# Extract PTX (virtual ISA) from binary:
cuobjdump -ptx ./executable > kernel.ptx

# Extract resource usage (registers, shared mem, stack per kernel):
cuobjdump -res-usage ./executable

# List all kernel symbols (find mangled names):
cuobjdump -symbols ./executable

# List ELF sections:
cuobjdump -lelf ./executable

# Demangle C++ kernel names:
echo "_ZN7cutlass..." | c++filt
cuobjdump -symbols ./executable | c++filt

# Extract SASS for a specific kernel function:
cuobjdump -sass -fun "kernel_name" ./executable

# Advanced disassembly with control flow graph:
cuobjdump -xelf all ./executable
nvdisasm -g -sf kernel.sm_89.cubin > kernel_cfg.sass

# Extract from library .so (cuSPARSE, cuBLAS):
cuobjdump -symbols /usr/local/cuda-12.0/lib64/libcusparse.so | c++filt | grep -i "spmv"
cuobjdump -sass -fun "kernel_name" /usr/local/cuda-12.0/lib64/libcusparse.so
```

For the full instruction-level analysis methodology, see `references/instruction-level-analysis.md`.

## File Formats

| Extension | Tool | View With |
|-----------|------|-----------|
| `.nsys-rep` | nsys | `nsys-ui`, `nsys stats` |
| `.ncu-rep` | ncu | `ncu-ui`, `ncu --import ... --csv` |
| `.json` (Chrome trace) | PyTorch Profiler | `chrome://tracing`, `ui.perfetto.dev` |
