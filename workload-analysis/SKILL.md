---
name: workload-analysis
description: Profile GPU workloads, identify bottlenecks with quantitative evidence, and produce research-quality reports. Use when the user asks to "profile GPU workload", "analyze GPU bottleneck", "run nsys", "run ncu", "roofline analysis", "kernel profiling", or discusses CUDA kernel performance, occupancy, or inference latency. Do NOT use for general Python profiling (cProfile), CPU-only workloads, or ML training hyperparameter tuning.
metadata:
  version: 4.1.0
  author: yanggon
---

# GPU Workload Analysis

## Codex execution

Resolve bundled paths relative to this skill's directory from the installed catalog. Invoke scripts by their full paths with the working directory set to the user's project (or research workspace for tracker updates). Write results there, not into the skill. Use the tools actually exposed by the current Codex client.


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

### Step 5: Instruction-Level Analysis

1. Extract SASS/PTX for bottleneck kernels identified in Step 4
2. Annotate the hot loop: map each SASS instruction to its high-level operation
3. Identify kernel phases (setup, main loop, reduction, epilogue)
4. Trace register dependency chains through the hot loop
5. Map SASS instructions to NCU stall categories (Long Scoreboard ← LDG, etc.)
6. Compute instruction mix statistics (compute-to-memory ratio)

CRITICAL: Complete this step BEFORE root cause analysis. The dependency chains and stall mappings are the concrete evidence that root cause chains build on.

Reference: `references/instruction-level-analysis.md`, `references/tool-reference.md`

### Step 5.5: Kernel SASS Forensics (Optional Deep-Dive)

Run between Step 5 and Step 6 when the dominant-time kernel deserves research-grade scrutiny — the workload's headline kernel will be reported on, you want to *understand* it (not just bound it), or you need stall/latency evidence at instruction granularity to back a root-cause claim.

**When to skip**: launch-bound workloads (kernel runtime < kernel-launch overhead), trivially memory-bound kernels where DRAM saturation is already the answer, or workloads where Step 5's dependency-chain analysis already pinpoints the bottleneck.

The phase produces a per-kernel `kernel_sass_analysis.md` artefact. Sub-tasks:

1. **Identify target kernel + mangled symbol** from Step 4's ncu output (full kernel name including template specialisation).
2. **Dump SASS for the runtime architecture**:
   ```
   cuobjdump --list-text <library.so>          # find the symbol
   cuobjdump --dump-sass -arch=sm_<XXX> --function <MANGLED> <library.so> > k.sass
   ```
   For custom-compiled kernels, point at the binary or .cubin instead of a vendor library.
3. **Build TWO instruction-count tables** with `scripts/build_inst_inventory.py`:
   - **Total kernel inventory** — every opcode categorised by pipe family (LSU split into Load / Store / Atomic; FMA / ALU / Shuffle / XU / Uniform / Branch / Reduce).
   - **Inner-loop inventory** — same categorisation filtered to the SASS PC range that executes most frequently per warp. Identify the inner loop by enumerating backward `BRA` instructions (long-span = real outer loop; short-span = bisection / spin / barrier wait).
4. **Decompile the kernel into C-like pseudocode** with annotated phases (setup → main loop → reduction → epilogue) and SASS PC ranges per phase. Identify the algorithm class (merge-path / row-split / persistent-CTA / wave-warp / tile-based GEMM / flash-attention / etc.) — `references/kernel-sass-forensics.md` §7 has structural fingerprints for common patterns.
5. **Map each instruction class to ncu pipe metrics**: `pipe_lsu`, `pipe_fma`, `pipe_alu`, `pipe_xu`, `pipe_cbu`, `pipe_adu`, `pipe_fp16`. Reference table in `references/kernel-sass-forensics.md` §8.
6. **Apportion `pipe_lsu_active_pct` into Load% / Store% / Atomic%** using per-op LSU request counts (`l1tex__t_requests_pipe_lsu_mem_*_op_*.sum`). Writes count `op_st + op_red + op_atom` (cuSPARSE-style kernels write via `RED.E.ADD`, not `STG`, on boundary rows). The updated `scripts/parse_ncu_results.py` emits this in the JSON's `pipe_lsu_split` block.
7. **Static-vs-dynamic cross-check** with `scripts/crosscheck_sass.py`: explain why static SASS counts predict the *direction* of pipe utilisation but not the *magnitude* (predication, looped vs unrolled execution counts, per-pipe peak issue rates, per-instruction issue cost).
8. **Map ncu warp-stall reasons to instruction classes** (table in `references/kernel-sass-forensics.md` §11):
   - `long_scoreboard`  ← global LDG dependent chain
   - `short_scoreboard` ← shared LDS dependent chain
   - `mio_throttle`     ← LSU pipe overflow (too many in-flight LDGs)
   - `lg_throttle`      ← address-calc / shared-mem bank conflict
   - `barrier`          ← `BAR.SYNC`, `WARPSYNC.COLLECTIVE`
   - `wait`             ← fixed-latency ops (transcendental, integer divide)
9. **Latency budget for the inner loop**: per-instruction cycle cost (LDG-DRAM ~400-500, LDG-L2 ~150-200, LDS ~30, FFMA/FADD/FMUL/IMAD ~4, SHFL ~5, RED.E.ADD atomic-contended). Sum dependent-chain instructions per inner-loop iteration; compare against ncu's `gpc__cycles_active.avg.per_warp`. The gap reveals how much latency the SM is actually hiding via warp-level parallelism.

**Outputs** under `<project>/analysis/`:
- `kernel_sass_analysis.md` (the synthesis doc — methodology + findings)
- `<kernel>_<arch>.sass` (raw cuobjdump dump, archived for reproducibility)
- `<kernel>_<arch>_inst_inventory.csv` (total + inner-loop tables)
- `static_vs_dynamic_crosscheck.md`

CRITICAL: feed the findings from Step 5.5 into Step 6's why-chain. The inner-loop instruction table + stall mapping + latency budget *are* the compiled evidence Step 6 needs.

Reference: `references/kernel-sass-forensics.md` (full methodology, 13 sections, with `01_suitesparse_spmv/analysis/kernel_sass_analysis.md` as the worked example)
Scripts: `scripts/build_inst_inventory.py`, `scripts/crosscheck_sass.py`, `scripts/parse_ncu_results.py` (emits `pipe_lsu_split`)

### Step 6: Root Cause Deep-Dive

1. Take the #1 bottleneck from analysis
2. Follow the symptom-to-cause chain -- ask "WHY?" at least 3 times
3. Use instruction-level evidence from Step 5 (dependency chains, stall mappings) and, when available, Step 5.5 (per-pipe utilisation, LSU load/store split, inner-loop latency budget)
4. Verify each claim with quantitative data

Reference: `references/root-cause-analysis.md`, `references/first-principles-analysis.md`, `references/instruction-level-analysis.md`, `references/kernel-sass-forensics.md`

### Step 7: Visualize and Report

1. Generate roofline plot, execution timeline, kernel breakdown
2. Include first-principles gap analysis (physical floor vs actual)
3. Include benchmark credibility section (which suite, citation)
4. Write report with findings and proposed optimizations

Scripts: `scripts/plot_roofline.py`, `scripts/plot_timeline.py`
Template: `assets/report_template.md`

## Execution Model

This skill uses **subagent-driven execution** with **validation-first development**.

### Dispatching Subagents

For each task in Steps 2-7:

1. Read the template from `prompts/` (implementer, spec-reviewer, or quality-reviewer)
2. Fill in all `[PLACEHOLDERS]` with actual values
3. Inline TDD rules from `prompts/tdd-for-profiling.md` into implementer prompts
4. Pass the completed prompt to the the available Codex subagent tool, with the filled prompt as its task message

The controller supplies the relevant prompt and profiling constraints. The subagent may read explicit supporting files when needed; do not assume it inherited this skill or prior conversation. This workflow requests delegation for substantial tasks. If subagents are unavailable, perform implementation, specification review, and quality review locally in order and disclose that independent review was unavailable.

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

Retain specification and quality checks. Scale review effort to the change; do not spawn several agents for a trivial edit. Resolve material findings before dependent work. Never dispatch overlapping implementers or concurrent measurements on the same GPU. Track agent IDs and wait for required results; preserve the parent model unless explicitly configured otherwise.

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
- ALWAYS extract SASS for bottleneck kernels before claiming root cause
- ALWAYS follow bottleneck symptoms to root causes with compiled evidence
- ALWAYS prefer publicly available, citable benchmark suites over synthetic data
- WHEN the dominant-bottleneck kernel will be reported on at research depth, run Step 5.5 (Kernel SASS Forensics) before Step 6 to produce the per-pipe utilisation, LSU load/store split, and inner-loop latency budget that the root-cause analysis consumes

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
- `references/instruction-level-analysis.md` -- SASS/PTX extraction, dependency chains, stall mapping (Step 5)
- `references/kernel-sass-forensics.md` -- Two-table instruction inventory, decompiled C-like pseudocode, LSU load/store split, pipe-to-instruction mapping, stall-reason-to-instruction-class mapping, per-instruction latency budget (Step 5.5)
- `references/root-cause-analysis.md` -- Symptom-to-cause chains, compiled evidence
- `references/pitfalls.md` -- 30+ pitfalls with symptoms and solutions
- `references/gpu-workload-profiling-guide.md` -- Complete worked example (GR00T N1.6)
