---
name: workload-analysis
description: Profile GPU workloads, identify bottlenecks with quantitative evidence, and produce research-quality reports. Use when the user asks to "profile GPU workload", "analyze GPU bottleneck", "run nsys", "run ncu", "roofline analysis", "kernel profiling", or discusses CUDA kernel performance, occupancy, or inference latency. Do NOT use for general Python profiling (cProfile), CPU-only workloads, or ML training hyperparameter tuning.
metadata:
  version: 4.0.0
  author: yanggon
---

# GPU Workload Analysis

## Instructions

### Step 1: Understand the Workload

1. Read the user's code or paper. Identify computational phases and estimate FLOPS.
2. Search for publicly available, citable benchmarks matching the workload domain. Consult `references/benchmark-suites.md`.
3. Compute the theoretical minimum execution time (physical floor) from data movement / peak BW and compute / peak FLOPS. See `references/first-principles-analysis.md`.

### Step 2: Set Up Environment

1. Create venv, install PyTorch + CUDA, install workload dependencies
2. Verify nsys/ncu available, verify workload runs on GPU
3. Check `references/pitfalls.md` for known setup issues (flash-attn, CUDA version mismatches)

Reference: `references/environment-setup.md`

### Step 3: Instrument and Profile

1. Add NVTX markers to delineate phases
2. Implement CUDATimer for GPU timing -- NEVER use `time.time()`
3. Run 3+ warmup iterations, then profile with PyTorch Profiler, nsys, ncu
4. Profile multiple configurations (batch sizes, input dims)

CRITICAL: Never profile all kernels with ncu `--set full`. Filter by NVTX or kernel name.

Reference: `references/profiling-methodology.md`, `references/tool-reference.md`
Scripts: `scripts/profile_workload.py`, `scripts/ncu_profile_workload.py`, `scripts/run_nsys_profile.sh`, `scripts/run_ncu_profile.sh`

### Step 4: Parse and Analyze

1. Parse profiling outputs, classify kernels (memory-bound vs compute-bound)
2. Compute phase breakdown, identify bottlenecks with evidence
3. Compare measured performance against the physical floor from Step 1

Reference: `references/analysis-and-visualization.md`
Scripts: `scripts/parse_ncu_results.py`, `scripts/parse_ncu_detailed.py`

### Step 5: Root Cause Deep-Dive

1. Take the #1 bottleneck from analysis
2. Follow the symptom-to-cause chain -- ask "WHY?" at least 3 times
3. Extract compiled evidence if needed (PTX/SASS/register counts)
4. Verify each claim with quantitative data

Reference: `references/root-cause-analysis.md`, `references/first-principles-analysis.md`

### Step 6: Visualize and Report

1. Generate roofline plot, execution timeline, kernel breakdown
2. Include first-principles gap analysis (physical floor vs actual)
3. Include benchmark credibility section (which suite, citation)
4. Write report with findings and proposed optimizations

Scripts: `scripts/plot_roofline.py`, `scripts/plot_timeline.py`
Template: `assets/report_template.md`

## Execution Model

This skill uses **subagent-driven execution** with **validation-first development**.

### Dispatching Subagents

For each task in Steps 2-6:

1. Read the template from `prompts/` (implementer, spec-reviewer, or quality-reviewer)
2. Fill in all `[PLACEHOLDERS]` with actual values
3. Inline TDD rules from `prompts/tdd-for-profiling.md` into implementer prompts
4. Pass the completed prompt to the Task tool (subagent_type: general-purpose)

The subagent receives the full prompt text -- it does NOT read skill files itself.

### Review Cycle (per task)

```
1. Dispatch implementer      -> prompts/implementer-prompt.md
2. Dispatch spec reviewer    -> prompts/spec-reviewer-prompt.md
   Fail -> implementer fixes -> re-review
   Pass -> proceed
3. Dispatch quality reviewer -> prompts/quality-reviewer-prompt.md
   Fail -> implementer fixes -> re-review
   Pass -> mark task complete, next task
```

Never skip reviews. Never proceed with unfixed issues. Never dispatch parallel implementers.

## Machine Specs

Verify at runtime with commands in `references/tool-reference.md`. Specs at skill creation:
- **GPU**: RTX 4070 Ti SUPER (16 GB, Ada Lovelace, CC 8.9)
- **Peaks**: BF16 44.1 TFLOPS, Mem BW 672 GB/s, 66 SMs, Ridge ~65.6 FLOP/byte

## Output Structure

```
project_root/
├── venv/        # Python virtual environment
├── models/      # Source code and weights
├── scripts/     # Profiling scripts
├── profiles/    # Binary profiles (.nsys-rep, .ncu-rep)
├── traces/      # Chrome trace JSON files
└── analysis/    # Reports, plots, raw JSON data
```

## Rules

- NEVER use `time.time()` for GPU timing -- use CUDA events
- ALWAYS run 3+ warmup iterations before profiling
- NEVER profile all kernels with ncu `--set full` -- filter first
- ALWAYS compute the physical floor before analyzing profiling results
- ALWAYS follow bottleneck symptoms to root causes with compiled evidence
- ALWAYS prefer publicly available, citable benchmark suites over synthetic data

## Troubleshooting

### flash-attn build failure
**Cause:** Missing --no-build-isolation flag
**Solution:** `pip install flash-attn --no-build-isolation`

### GPU timing shows 0ms or negative
**Cause:** Using `time.time()` instead of CUDA events
**Solution:** Use `torch.cuda.Event(enable_timing=True)` with synchronization

### nsys fails with "option parsing failure"
**Cause:** Wrong flag syntax
**Solution:** Use `-f true` instead of `--force-overwrite`

### ncu runs forever
**Cause:** Profiling all kernels without filter
**Solution:** Add `--nvtx-include` or `--kernel-name` filter. See `references/tool-reference.md`.

For 30+ more pitfalls, consult `references/pitfalls.md`.

## Examples

See `examples/vla_case_study.md` for a complete GR00T N1.6 VLA profiling walkthrough, and `examples/spmv_suitesparse_case_study.md` for SpMV on SuiteSparse matrices.

## All Reference Files

- `references/environment-setup.md` -- PyTorch/CUDA, flash-attn, tool verification
- `references/profiling-methodology.md` -- CUDATimer, NVTX, warmup, nsys, ncu
- `references/analysis-and-visualization.md` -- Roofline, timeline, categorization
- `references/tool-reference.md` -- Copy-paste command reference
- `references/benchmark-suites.md` -- Benchmark catalog by domain with citations
- `references/first-principles-analysis.md` -- Physical floor estimation methodology
- `references/root-cause-analysis.md` -- Symptom-to-cause chains, compiled evidence
- `references/pitfalls.md` -- 30+ pitfalls with symptoms and solutions
- `references/gpu-workload-profiling-guide.md` -- Complete worked example (GR00T N1.6)
