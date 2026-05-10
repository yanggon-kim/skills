# Step 7 — Evaluation

## Purpose

Produce evaluation artifacts — plots, tables, and quantitative comparisons — for each surviving solution in `final_solution_candidates.md`. The output of Step 7 is what Step 8 turns into per-paper figures.

The methodological discipline that distinguishes Rhu/Zhu papers' §7 sections from typical evaluations: **the first plot must re-measure the §3 root-cause counter under the proposed system**, demonstrating the diagnosed cause was actually eliminated, not just that latency went down for unrelated reasons.

## Inputs

- `final_solution_candidates.md` — the N surviving entries.
- `01_workload_analysis/01_workload_analysis.md` — the §3 root causes that must each get a re-measurement plot.
- `05_implementations/<id>/` — the implementations themselves.
- `04_simulation_setup/` — for HW evaluation in GPGPU-Sim.
- `references/research_methodology.md` §6 (Closing-the-loop in evaluation).
- `references/paper_structure_template.md` §7 (canonical evaluation section structure).

## Procedure

### Phase 7.1 — Per-solution evaluation directory

Create `06_evaluation/<id>/` for each surviving entry in `final_solution_candidates.md`. Inside each:

```
06_evaluation/<id>/
├── speedup.csv                      # raw timing data
├── counter_remeasurement.csv        # the §3-counter values before and after
├── ablation.csv                     # contribution-by-contribution effect
├── sensitivity.csv                  # one design parameter swept
└── figs/                            # generated plots
    ├── fig_speedup.pdf              # the "Figure 14" equivalent
    ├── fig_counter_<name>.pdf       # one per root cause — the "Figure 17" equivalents
    ├── fig_ablation.pdf
    └── fig_sensitivity.pdf
```

### Phase 7.2 — Speedup plot (the "Figure 14")

For SW ideas: real-GPU wall-clock comparison vs the Step 2 baseline. Multiple input sizes / batch sizes from Step 2's scale sweep — the speedup plot must show the win is robust across scale, not at one sweet spot.

For HW ideas: GPGPU-Sim cycle-count comparison vs the Step 5 baseline simulator run. Same scale sweep.

For combinations: two reference bars per scale point — the strongest-constituent and the baseline — plus the combination bar. Visually confirms amplification.

### Phase 7.3 — Counter re-measurement plots (the "Figure 17"s)

This is the load-bearing part. **For each root cause from `01_workload_analysis.md`, produce a plot showing the corresponding counter before and after the proposed solution.**

The canonical example is **Crescent** (Zhu, ISCA 2022 — see `references/paper_structure_template.md` §7 reference exemplars or `01_papers/01_zhu/2022_ISCA_Crescent.md` if available). Crescent's §3 identified SRAM bank conflicts (alongside non-streaming DRAM access) as a root cause of point-cloud-DNN slowdown. Its evaluation reports two distinct plots: **Figure 14** is the headline speedup (1.9× average, up to 3.1× over the baseline accelerator), and **Figure 17** *separately* shows that bank-conflict counts drop sharply after the proposed selective-bank-conflict-elision mechanism is applied.

The Figure-17-style plot is what makes the evaluation persuasive — it proves the **diagnosed cause** was actually eliminated, not just that latency went down for unrelated reasons.

If Step 2 identified 2 bottlenecks, Step 7 needs 2 counter re-measurement plots — one per cause.

### Phase 7.4 — Ablation

For each contribution within a single solution, produce a plot showing the effect of *adding only that contribution* against the baseline. If a solution has 3 sub-mechanisms (e.g. layout transform + scheduling change + new instruction), the ablation has 4 bars: baseline, +mech1, +mech1+mech2, +mech1+mech2+mech3.

The point of ablation is "every subcomponent earns its keep." If `+mech2` doesn't move the needle, mech2 is dead weight — push back to Step 6 to remove it before Step 8 starts.

### Phase 7.5 — Sensitivity sweep

Pick the most-critical design parameter (cache size, # of PEs, batch size, kernel block dim, etc.) and sweep it over a reasonable range. The plot answers "is the win robust around the proposed operating point, or does it depend on a single sweet spot?"

If the sensitivity plot reveals the win is fragile (e.g. only works at one cache size), that's a §7 finding that must appear in the paper — don't hide it.

### Phase 7.6 — Per-paper figure inventory

At minimum, every paper produced under Step 8 must include the following figures, generated under `06_evaluation/<id>/figs/` and copied into `07_paper/paper_<id>/figs/`:

- A **counter re-measurement plot** for *each* root cause from Step 2 (the "Figure 17" equivalents) — proves the diagnosed mechanism was eliminated.
- A **speedup plot** vs the baseline (the "Figure 14" equivalent) — the headline performance number.
- An **ablation plot** isolating each contribution from Step 6 — proves each subcomponent earns its keep.
- A **sensitivity sweep** for at least one critical design parameter — shows the win is robust, not a single sweet spot.

### Phase 7.7 — Auxiliary simulators (Ramulator, CACTI)

For components such as cache or DRAM where GPGPU-Sim's models are too coarse, integrate auxiliary simulators **only when needed**:

- **Ramulator** — for memory-subsystem details (DRAM bank conflicts, RAS/CAS timing, refresh overhead). Use when a HW idea touches the memory controller or DRAM scheduling.
- **CACTI** — for area / energy estimates of cache-class structures. Use when a HW idea adds or modifies an SRAM-based component and the paper claims energy benefits.

If a particular evaluation question doesn't require them, skip them. When required, integrate with GPGPU-Sim and document the integration in `06_evaluation/_aux_simulators.md`.

### Checkpoint

When every surviving solution has all four figure types, update `PROGRESS.md` via `scripts/update_progress.py 7 done` and stop. The user reviews the figure quality — this is the last gate before the paper PDF is built.

## Common pitfalls

- **Skipping the counter re-measurement.** This is the single most consequential evaluation discipline; a paper without it has an unverified causal story. See Material 2 §6.
- **Ablation by group instead of by contribution.** Group ablations ("with all proposed components" vs "without any") tell you nothing about which contribution earned its keep. Go one-at-a-time.
- **Sensitivity sweep over a parameter no one controls.** Pick a parameter that the *deployer* of your solution would actually tune (e.g. cache size in a future GPU, not a constant in your simulator config).
- **Hiding negative findings.** If the ablation shows mech2 didn't help, document it. Reviewers see the discrepancy between methods listed in §5 and effects in §7; transparency wins.
