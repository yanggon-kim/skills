---
name: workload-analysis
description: Use when the user asks to "workload analysis", "profile GPU workload", "analyze GPU bottleneck", "run nsys", "run ncu", "roofline analysis", "kernel profiling", or discusses GPU performance profiling, CUDA kernel bottlenecks, or inference latency optimization.
version: 3.0.0
tools: Read, Glob, Grep, Bash, Edit, Write
---

# GPU Workload Analysis

Profile any GPU workload, identify bottlenecks with quantitative evidence, and produce research-quality reports.

## When to Use

- User asks to profile or analyze a GPU workload
- User wants to understand GPU bottlenecks, occupancy, or roofline position
- Task involves PyTorch Profiler, NSight Systems, or NSight Compute

## Machine Info

Verify at runtime with commands in `references/tool-reference.md`. Key specs at skill creation:
- **GPU**: RTX 4070 Ti SUPER (16 GB, Ada Lovelace, CC 8.9)
- **CUDA**: 13.0, **nsys**: 2025.3.2, **ncu**: 2025.3.1.0
- **Peaks**: BF16 44.1 TFLOPS, Mem BW 672 GB/s, 66 SMs, Ridge ~65.6 FLOP/byte

## Workflow

This skill uses **subagent-driven execution** with **validation-first development**.

### Phase 1: Plan

0. **Benchmark Selection** — Before writing any profiling code, search for publicly available benchmark suites that match the user's workload. Prefer established, citable benchmarks over synthetic/generated data. Consult `references/benchmark-suites.md`.
1. Understand the workload (read code/paper, identify phases, estimate FLOPS)
2. **First-Principles Floor Estimation** — Before profiling, compute the theoretical minimum execution time from physical constraints (data movement / peak BW, compute / peak FLOPS). This sets the "materials cost" baseline. See `references/first-principles-analysis.md`.
3. Break the work into independent tasks (typically: benchmark selection, env setup, instrumentation, profiling, analysis, root cause deep-dive, report)
4. Create task list using TaskCreate for all tasks

**References**: `references/analysis-and-visualization.md`, `references/environment-setup.md`, `references/benchmark-suites.md`, `references/first-principles-analysis.md`

### Phase 2: Execute — Subagent per Task

**How to dispatch subagents:** For each prompt template in `prompts/`, the controller must:
1. Read the template file from this skill directory
2. Fill in all `[PLACEHOLDERS]` with actual values
3. Read `prompts/tdd-for-profiling.md` and inline the TDD rules into the implementer prompt
4. Pass the completed prompt to the Task tool (subagent_type: general-purpose)

The subagent receives the full prompt text — it does NOT read skill files itself.

For each task, repeat this cycle:

```
1. Dispatch implementer subagent    → read & fill prompts/implementer-prompt.md
   - Inline TDD rules from          → prompts/tdd-for-profiling.md
   - Implementer self-reviews before reporting back

2. Dispatch spec reviewer           → read & fill prompts/spec-reviewer-prompt.md
   - Reads actual code, does NOT trust implementer's report
   - ❌ Issues found → implementer fixes → re-review
   - ✅ Spec compliant → proceed

3. Dispatch quality reviewer        → read & fill prompts/quality-reviewer-prompt.md
   - Checks code quality, profiling correctness, data integrity
   - ❌ Issues found → implementer fixes → re-review
   - ✅ Approved → mark task complete (TaskUpdate), next task
```

After the profiling task completes, add a **Root Cause Analysis** task that:
1. Takes the top bottleneck from profiling results
2. Follows the symptom → cause chain to the physical root cause
3. Uses compiled evidence (PTX/SASS/ncu) when appropriate
4. Applies first-principles decomposition

**Reference**: `references/root-cause-analysis.md`, `references/first-principles-analysis.md`

**Never**: skip reviews, proceed with unfixed issues, dispatch parallel implementers, start quality review before spec review passes.

### Phase 3: Final Review

After all tasks complete:
1. Dispatch final quality reviewer across entire implementation
2. Verify all outputs exist (report, plots, raw data)
3. Present results to user

## Tasks to Dispatch

These are the typical tasks for a profiling project. Adapt as needed.

### Task 0: Benchmark Selection
- Identify publicly available benchmark suites for this workload domain
- Prefer established, citable suites (SuiteSparse, SNAP, MLPerf, etc.)
- Download benchmark data with documented, reproducible commands
- Verify data loads correctly, note citation info for the report
- **Ref**: `references/benchmark-suites.md`

### Task 1: Environment Setup
- Create venv, install PyTorch + CUDA, install workload dependencies
- Verify nsys/ncu available, verify workload runs on GPU
- **Ref**: `references/environment-setup.md`, `references/pitfalls.md`

### Task 2: Instrument and Profile
- Add NVTX markers, implement CUDATimer (never `time.time()`)
- Run 3+ warmup iterations, then profile with PyTorch Profiler, nsys, ncu
- Profile multiple configurations (batch sizes, input dims)
- **Ref**: `references/profiling-methodology.md`, `references/tool-reference.md`
- **Scripts**: `scripts/profile_workload.py`, `scripts/ncu_profile_workload.py`, `scripts/run_nsys_profile.sh`, `scripts/run_ncu_profile.sh`

### Task 3: Parse and Analyze
- Parse profiling outputs, classify kernels (memory-bound vs compute-bound)
- Compute phase breakdown, identify bottlenecks with evidence
- **Ref**: `references/analysis-and-visualization.md`
- **Scripts**: `scripts/parse_ncu_results.py`, `scripts/parse_ncu_detailed.py`

### Task 3.5: Root Cause Deep-Dive
- Take the #1 bottleneck from analysis results
- Follow the symptom → cause chain (ask "WHY?" at least 3 times)
- Extract compiled evidence if needed (PTX/SASS/register counts)
- Verify each claim with quantitative data
- Apply first-principles decomposition (physical floor, gap, factors)
- **Ref**: `references/root-cause-analysis.md`, `references/first-principles-analysis.md`

### Task 4: Visualize and Report
- Generate roofline plot, execution timeline, kernel breakdown
- Include first-principles gap analysis (physical floor vs actual, gap decomposition)
- Include benchmark credibility section (which suite, citation, comparison to literature)
- Write report with findings and proposed optimizations
- **Scripts**: `scripts/plot_roofline.py`, `scripts/plot_timeline.py`
- **Template**: `assets/report_template.md`

## Rules

- NEVER use `time.time()` for GPU timing — use CUDA events
- ALWAYS run 3+ warmup iterations before profiling
- NEVER profile all kernels with ncu `--set full` — filter by NVTX or kernel name
- ALWAYS verify the workload runs correctly before profiling
- Separate scripts, profiles (.nsys-rep, .ncu-rep), and analysis outputs into different directories
- Check `references/pitfalls.md` before troubleshooting
- Analysis MUST include: phase breakdown, bottleneck identification, root cause, quantitative metrics
- ALWAYS prefer publicly available, citable benchmark suites over synthetic/generated data
- ALWAYS compute the theoretical minimum (physical floor) before analyzing profiling results
- ALWAYS follow bottleneck symptoms to root causes with compiled evidence — never stop at surface metrics

## Output Structure

```
project_root/
├── venv/                  # Python virtual environment
├── models/                # Source code and weights
├── scripts/               # Profiling scripts (from skill templates)
├── profiles/              # Binary profiles (.nsys-rep, .ncu-rep)
├── traces/                # Chrome trace JSON files
└── analysis/              # Reports, plots, raw JSON data
```

See `assets/project_structure.md` for full layout.

## File Inventory

### `prompts/` — Subagent prompt templates

| File | Purpose |
|------|---------|
| `prompts/implementer-prompt.md` | Dispatch implementer subagent for each task |
| `prompts/spec-reviewer-prompt.md` | Verify implementation matches spec |
| `prompts/quality-reviewer-prompt.md` | Review code quality and profiling correctness |
| `prompts/tdd-for-profiling.md` | TDD rules adapted for profiling scripts |

### `references/` — Detailed documentation (load as-needed)

| File | Purpose |
|------|---------|
| `references/environment-setup.md` | Env setup, PyTorch/CUDA, flash-attn, tool verification |
| `references/profiling-methodology.md` | CUDATimer, NVTX, warmup, PyTorch Profiler, nsys, ncu |
| `references/analysis-and-visualization.md` | Architecture analysis, FLOPS, roofline, timeline, categorization |
| `references/pitfalls.md` | 30+ pitfalls with symptoms and solutions |
| `references/tool-reference.md` | Copy-paste command reference for all tools |
| `references/benchmark-suites.md` | Benchmark suite catalog by domain, with citations and download instructions |
| `references/first-principles-analysis.md` | First-principles thinking methodology for GPU bottleneck analysis |
| `references/root-cause-analysis.md` | Systematic root cause analysis with symptom→cause chains and compiled evidence |

### `scripts/` — Ready-to-adapt profiling scripts

| File | Purpose |
|------|---------|
| `scripts/profile_workload.py` | Main profiling: CUDATimer, PhaseTimer, traces, batch sweep |
| `scripts/ncu_profile_workload.py` | NCU-targeted: NVTX markers, cudaProfilerStart/Stop |
| `scripts/parse_ncu_results.py` | Parse .ncu-rep → kernel summary, category breakdown |
| `scripts/parse_ncu_detailed.py` | Deep NCU: occupancy, warp stalls, GEMM breakdown |
| `scripts/plot_roofline.py` | Roofline plot with GPU specs lookup |
| `scripts/plot_timeline.py` | Timeline, batch comparison, kernel pie chart |
| `scripts/run_nsys_profile.sh` | nsys wrapper (modes: single, batch, custom) |
| `scripts/run_ncu_profile.sh` | ncu wrapper (strategies: nvtx, top, kernel, all) |

### `examples/` and `assets/`

| File | Purpose |
|------|---------|
| `examples/vla_case_study.md` | GR00T N1.6 VLA profiling — complete worked example |
| `examples/spmv_suitesparse_case_study.md` | SpMV on SuiteSparse matrices — benchmark selection, metrics, cross-GPU comparison approach |
| `assets/project_structure.md` | Directory structure template |
| `assets/profiling_checklist.md` | 40-item step-by-step checklist |
| `assets/report_template.md` | Markdown report template |
| `GPU_WORKLOAD_PROFILING_GUIDE.md` | Original source guide |
