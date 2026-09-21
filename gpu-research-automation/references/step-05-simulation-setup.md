# Step 5 — Simulation Setup

## Purpose

Set up GPGPU-Sim such that it reproduces the dominant bottleneck and root-cause findings of Step 2. Without a faithful simulator baseline, hardware-based ideas in Step 6 cannot be evaluated credibly.

## Inputs

- `01_workload_analysis/01_workload_analysis.md` — the bottleneck story we want to reproduce.
- `gpu_spec.json` — peak FLOPS, peak BW, SM count, memory size of the real GPU profiled in Step 2.
- `03_solutions/03_solutions.json` — informs which simulator features each HW idea will need.

## Procedure

### Phase 5.1 — Configure GPGPU-Sim to match `gpu_spec.json`

GPGPU-Sim ships with reference configurations for V100, RTX 2080 Ti, RTX 3070, etc. Match:

- SM count, warp scheduler width, register file size, shared-mem capacity per SM.
- L1 / L2 cache sizes, replacement policy, MSHR depth.
- HBM/GDDR bandwidth, channel count, banks per channel.
- Compute throughput (FP32, FP16, tensor-core throughput) — set the throughput such that the *ratio* of peak compute / peak BW matches the real device.

Save the resulting config as `04_simulation_setup/<gpu_name>.config` (e.g. `RTX5080.config`). Document each non-default knob in `04_simulation_setup/config_rationale.md`.

### Phase 5.2 — Reproduce Step 2 on GPGPU-Sim

Run the same workload (or a kernel-isolated subset) under GPGPU-Sim. Compare:

- Stage breakdown (the §3.1 plot) — should produce the *same dominant-bottleneck ranking* as real silicon, with each stage's relative magnitude within ~20% (tolerance documented).
- Counter-level finding (the §3.2 root cause) — the simulator-equivalent counter (e.g. simulator's L2 hit rate, NoC injection rate) should align with the Nsight Compute counter from Step 2.

Write the comparison into `04_simulation_setup/baseline_validation.md`:

```markdown
## Baseline validation
| Stage / counter | Real (Step 2) | GPGPU-Sim | Δ | Within tolerance? |
|-----------------|---------------|-----------|---|---|
| Bootstrapping dominance | 73% of latency | 68% | -5pp | yes |
| L2 hit rate | 42% | 51% | +9pp | yes (sim caches model differs) |
| ... |
```

### Phase 5.3 — Missing-feature stance

When GPGPU-Sim does not model a feature that the real GPU uses, decide which of three cases applies *before* doing anything:

#### Case (i) — A close analog exists in GPGPU-Sim, and substituting it would not materially change the dominant-bottleneck story

Use the analog. Concrete example: the real GPU runs **WGMMA** (Hopper / Blackwell warp-group MMA), but GPGPU-Sim only has **WMMA**. Both are tensor-core matrix-multiply primitives, so for most workloads the dominant bottleneck (memory bandwidth, tensor-core occupancy, register pressure, etc.) won't shift meaningfully between them. WMMA is an acceptable compromise. Record the substitution and the *reason it preserves the bottleneck signal* in `04_simulation_setup/feature_substitutions.md`.

#### Case (ii) — The missing feature is genuinely new with no close analog

Implement that feature inside GPGPU-Sim rather than silently downgrading the baseline. The canonical example is **TMA** (Hopper async bulk tensor copy): there is no existing GPGPU-Sim primitive that approximates it, so the bottleneck story changes if you pretend it isn't there. Document the implementation in `04_simulation_setup/feature_implementations/<feature_name>/` and validate it against the real-hardware traces from Step 2. Keep the modifications as a clean diff against upstream GPGPU-Sim so they can be inspected.

#### Case (iii) — Genuinely new but implementation is infeasible at project scope

If implementing the feature inside GPGPU-Sim would take more effort than this project can afford (weeks of simulator-core changes, missing memory-system support, etc.), do not silently downgrade. Instead, surface the situation to the user with concrete alternatives — for example:

- Pick a different baseline GPU (an older generation whose features GPGPU-Sim already supports) and re-run Step 2 against it.
- Narrow the target workload to the subset whose bottleneck does *not* depend on the unsupported feature.
- Use a different simulator that does support the feature (Accel-Sim, ZSim variants).

The user picks one of these alternatives before Step 5 proceeds. **This is a checkpoint moment — the skill must not move on without an explicit user choice.**

### Phase 5.4 — Decide build artifact for Step 6

For each HW idea in `03_solutions.json`, list (in `04_simulation_setup/build_plan.md`):

- Which source files will need modification (cache model? execution unit? memory subsystem?)
- Whether it requires a custom PTX-to-PTX compiler shim for inserting new instructions
- Estimated complexity (low / medium / high)

This pre-feeds Phase 6A's implementation-order decisions.

### Checkpoint

Update `PROGRESS.md` via `scripts/update_progress.py 5 done 04_simulation_setup/` and apply the checkpoint policy in `SKILL.md`. Report baseline validation and substitutions; resolve material choices before Step 6A and continue when authorized.

## Common pitfalls

- **Treating simulator faithfully too loosely.** "It runs" is not the bar; the dominant-bottleneck *ranking* must match Step 2. If the simulator says compute-bound but real GPU says memory-bound, the rest of the project's evaluation is invalid.
- **Skipping config rationale.** Knobs you set without documenting will get reviewed-and-changed later, breaking reproducibility. Document every knob.
- **Silently downgrading on a missing feature.** Case (iii) is a checkpoint — escalate, don't skip. The user might be willing to switch baselines rather than accept a degraded sim.
- **Implementing a feature that doesn't matter.** Don't implement TMA if your bottleneck is at L1; the missing-feature work is only worth it when the feature touches the dominant bottleneck.
