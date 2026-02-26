# Pitfalls & Lessons Learned

These are real problems encountered during GPU workload profiling projects on this machine. Check here before debugging.

## Environment Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| flash-attn build fails | `No module named 'torch'` | Use `--no-build-isolation` flag |
| flash-attn build fails | `No module named 'wheel'` | `pip install wheel` first, then retry |
| torch CUDA mismatch | `CUDA error: no kernel image` | Ensure torch CUDA version matches system nvcc version |
| Model class not found | `KeyError: 'model_type'` or similar | Import the model's registration module before `AutoModel.from_pretrained()` |
| Insufficient disk space | flash-attn compilation fails silently | Need ~5 GB temp space for flash-attn compilation |
| Wrong Python version | Import errors, syntax errors | Check model's required Python version in pyproject.toml |
| Dependency conflicts | Version incompatibilities | Use `pip install --no-deps -e <repo>` then add deps manually |

## Profiling Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| GPU timing is wrong | CPU time != GPU time | Use `torch.cuda.synchronize()` or CUDA events, NEVER `time.time()` |
| First run is slow | 2-5x slower than subsequent runs | Always warm up 3+ iterations before measuring |
| nsys `--force-overwrite` fails | Option parsing error | Use `-f true` instead |
| nsys `--cuda-memory-usage` fails | Ambiguous option error | Remove the flag entirely |
| ncu is extremely slow | Hours for full model inference | Use `--nvtx-include` to profile specific phases only |
| ncu `--set full` on all kernels | Takes forever, fills disk | Use `-s N -c M` to skip first N kernels, capture only M |
| NCU occupancy shows 0% | Missing data in CSV export | Use `--set full` instead of `--set roofline` |
| NCU permission denied | `ERR_NVGPUCTRPERM` | Run `sudo sh -c 'echo 1 > /proc/sys/kernel/perf_event_paranoid'` |
| PyTorch profiler adds overhead | Profiled run is slower than normal | Profile separately from timing measurements; don't combine |
| Profile file is huge | .ncu-rep is 1 GB+ | Filter kernels more aggressively with -c, -k, or --nvtx-include |

## Data Structure Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| Collated dict has extra nesting | `KeyError: 'input_ids'` | Check dict structure — may need `data["inputs"]` not `data` |
| GPU properties API typo | `AttributeError: total_mem` | Use `.total_memory` (not `.total_mem`) |
| NCU CSV parsing fails | Columns misaligned | Use Python `csv.DictReader`, never manual column splitting (kernel names contain commas) |
| Tensor dtype mismatch | Silent wrong results or errors | Ensure all inputs match model dtype (bf16/fp16/fp32) |
| Model input format wrong | Cryptic shape errors | Print expected input shapes from model's forward method signature first |

## Analysis Pitfalls

| Problem | Symptom | Solution |
|---------|---------|----------|
| Roofline looks wrong | All points on the same line | Check if you're using the right peak compute (tensor core vs non-tensor) |
| Arithmetic intensity estimate off | Points don't match NCU data | Use NCU's reported SM throughput / memory throughput to cross-check |
| Kernel names are mangled | Can't identify which kernel is which | Use NVTX markers + `--nvtx-include` to isolate phases |
| Matplotlib fails headless | `TclError: no display` | Use `matplotlib.use('Agg')` at the top of plotting scripts |

## General Advice

1. **Always validate the workload runs before profiling** — one clean inference first
2. **Keep profiling scripts minimal** — strip out everything except the code path you want to measure
3. **Profile files can be huge** (100 MB - 1 GB for NCU) — don't commit them to git
4. **ncu may require elevated permissions** — check `/proc/sys/kernel/perf_event_paranoid`
5. **Chrome traces from PyTorch Profiler** are the fastest debugging tool — open in `chrome://tracing` or `ui.perfetto.dev`
6. **nsys GUI** (`nsys-ui`) is excellent for visual timeline analysis but requires a display
7. **When in doubt, check `nsys --help` and `ncu --help`** — flag names vary across versions
