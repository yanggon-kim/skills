# Workload Analysis Checklist

Use this checklist to track progress through a profiling session.

## Phase 0: Select Benchmarks
- [ ] Identify publicly available benchmark suites for this workload domain
- [ ] Consult `references/benchmark-suites.md` for recommended suites
- [ ] Prefer established, citable suites (SuiteSparse, SNAP, MLPerf, etc.)
- [ ] Download benchmark data with documented, reproducible commands
- [ ] Verify benchmark data loads correctly (check dimensions, NNZ, checksums)
- [ ] Note citation info (BibTeX) for the report
- [ ] Select multiple datasets to show results aren't input-specific

## Phase 1: Understand the Workload
- [ ] Read the workload description / paper / source code
- [ ] Identify major computational phases (encoder, decoder, attention, etc.)
- [ ] Note the expected input shapes, batch sizes, sequence lengths
- [ ] Identify if it uses special kernels (flash attention, custom CUDA ops)

## Phase 2: Find and Download Implementation
- [ ] Find official / best public implementation (GitHub, HuggingFace)
- [ ] Clone the repository
- [ ] Download model weights if applicable
- [ ] Read the installation instructions and note dependencies

## Phase 3: Set Up Environment
- [ ] Create Python virtual environment
- [ ] Install PyTorch with correct CUDA version (verify with `nvcc --version`)
- [ ] Install model dependencies (use `--no-deps` for the model package)
- [ ] Install flash-attn if needed (use `--no-build-isolation`)
- [ ] Verify `nsys --version` and `ncu --version` work
- [ ] Run one inference to confirm the workload executes correctly
- [ ] Note all package versions for reproducibility

## Phase 4: Architecture Analysis
- [ ] Count parameters per component
- [ ] Estimate memory footprint (weights + activations)
- [ ] Estimate FLOPS per phase (linear layers, attention, FFN)
- [ ] Compute arithmetic intensity and compare to GPU ridge point

## Phase 4.5: First-Principles Floor Estimation
- [ ] Compute minimum data movement (bytes) — list every array/tensor that MUST be read/written
- [ ] Compute minimum compute (FLOPs) — count arithmetic operations
- [ ] Calculate theoretical minimum time: max(bytes / peak_BW, FLOPs / peak_compute)
- [ ] Apply Little's Law: required outstanding requests = peak_BW × DRAM_latency / bytes_per_request
- [ ] Determine required warps/SM to saturate bandwidth
- [ ] Document this as the "physical floor" baseline for gap analysis later
- [ ] Classify workload as memory-bound or compute-bound from first principles

## Phase 5: Add Instrumentation
- [ ] Add NVTX markers to each inference phase
- [ ] Implement CUDATimer-based timing (NOT time.time())
- [ ] Add warmup loop (3+ iterations minimum)
- [ ] Create profiling script with modes: single-step, batch-sweep, arch-analysis

## Phase 6: Run PyTorch Profiler
- [ ] Export Chrome trace (.json)
- [ ] Print top 30 CUDA kernels by time
- [ ] Open Chrome trace in `chrome://tracing` or `ui.perfetto.dev` for visual inspection
- [ ] Note the dominant kernel types and their timing

## Phase 7: Run NSight Systems (nsys)
- [ ] Run: `nsys profile -o profiles/output --trace=cuda,nvtx -f true python script.py`
- [ ] Extract kernel summary: `nsys stats --report cuda_gpu_kern_sum profiles/output.nsys-rep`
- [ ] Extract NVTX summary: `nsys stats --report nvtx_sum profiles/output.nsys-rep`
- [ ] Check for unexpected memory copies or idle gaps in the timeline

## Phase 8: Run NSight Compute (ncu) — Selective
- [ ] Identify which phase(s) to deep-dive (from PyTorch Profiler / nsys results)
- [ ] Run ncu with NVTX filtering on the target phase
- [ ] Export CSV: `ncu --import profile.ncu-rep --csv --page details > output.csv`
- [ ] Parse results with `parse_ncu_results.py` and `parse_ncu_detailed.py`
- [ ] Note SM throughput, memory throughput, occupancy, warp stalls per kernel

## Phase 9: Multi-Configuration Sweep
- [ ] Profile with batch sizes: 1, 2, 4, 8 (or until OOM)
- [ ] Profile with different input sizes if applicable
- [ ] Note how latency and memory scale with each config
- [ ] Identify which phases scale well and which don't

## Phase 9.25: Instruction-Level Analysis
- [ ] Identify bottleneck kernel(s) from Phase 8/9 profiling results
- [ ] Extract SASS: `cuobjdump -sass ./executable > kernel.sass`
- [ ] Extract resource usage: `cuobjdump -res-usage ./executable`
- [ ] Demangle kernel names: `cuobjdump -symbols ./executable | c++filt`
- [ ] Annotate the hot loop: map each SASS instruction to high-level operation
- [ ] Identify kernel phases (setup, main loop, reduction, epilogue)
- [ ] Trace register dependency chain through hot loop (def-use analysis)
- [ ] Draw ASCII pipeline diagram showing critical path latency
- [ ] Map SASS instructions to NCU stall categories (LDG → Long Scoreboard, etc.)
- [ ] Compute instruction mix statistics (count instruction classes, compute-to-memory ratio)
- [ ] Verify dependency chain length matches theoretical prediction
- [ ] Document all findings — these feed directly into root cause analysis

Reference: `references/instruction-level-analysis.md`

## Phase 9.5: Root Cause Deep-Dive
- [ ] Take the #1 bottleneck from profiling analysis
- [ ] Follow the symptom → cause chain (ask "WHY?" at least 3 times)
- [ ] Use instruction-level evidence from Phase 9.25 (dependency chains, stall mappings, instruction mix)
- [ ] Extract additional compiled evidence if needed (PTX with `nvcc -ptx`)
- [ ] Verify each claim in the causal chain with quantitative data from ncu
- [ ] Compute occupancy budget: regs/thread → blocks/SM → warps/SM
- [ ] Check grid saturation: grid_size / num_SMs → is the GPU fully loaded?
- [ ] Apply Little's Law: are there enough warps to saturate bandwidth?
- [ ] Find the longest dependent load chain in PTX/SASS
- [ ] Document the complete causal chain with proof (symptom → evidence → root cause)
- [ ] Quantify how much of the gap each root cause explains

## Phase 10: Analysis and Visualization
- [ ] Classify kernels: memory-bound vs compute-bound vs balanced
- [ ] Compute phase breakdown (% of total time per phase)
- [ ] Generate roofline plot
- [ ] Generate execution timeline
- [ ] Generate kernel category pie chart
- [ ] Generate batch size scaling bar chart
- [ ] Write bottleneck analysis with root causes
- [ ] Propose specific optimizations

## Phase 11: Report
- [ ] Write main profiling results report (Markdown)
- [ ] Include all figures (roofline, timeline, kernel breakdown)
- [ ] Include quantitative evidence for every claim
- [ ] List proposed optimizations with expected impact
- [ ] Save all raw data as JSON for future reference
