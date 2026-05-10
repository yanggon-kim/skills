# Step 2 — Workload Analysis (augmented)

## Purpose

Profile the target workload from Step 1 on the locally-attached GPU and identify the bottleneck at counter level. This step is the methodological heart of the entire project — `paper_structure_template.md` §3 (Workload Characterization) is the load-bearing section of the eventual paper, and *this* step produces what will become §3.

## Inputs

- `00_target_workload/00_target_workload.md` (Step 1 artifact) — names the (algorithm, benchmark, dataset) tuple to profile.
- `gpu_spec.json` — the GPU's name, compute capability, peak FLOPS, peak bandwidth.
- Read access to:
  - `references/workload-analysis/` — the deployed workload-analysis skill (Material 3).
  - `references/paper_structure_template.md` — Material 1, esp. §3.
  - `references/research_methodology.md` — Material 2, esp. §3 (counter-driven root cause) and §10 (methodological inventions).

## Procedure

### Phase 2.1 — Run the deployed workload-analysis skill (Material 3)

`references/workload-analysis/SKILL.md` defines a 5+ step profiling pipeline with nsys, ncu, and SASS-level analysis. **Follow it literally** — don't reinvent. The relevant references inside that skill:

- `references/workload-analysis/references/environment-setup.md`
- `references/workload-analysis/references/profiling-methodology.md`
- `references/workload-analysis/references/tool-reference.md`
- `references/workload-analysis/references/instruction-level-analysis.md`
- `references/workload-analysis/references/root-cause-analysis.md`
- `references/workload-analysis/references/first-principles-analysis.md`

And its scripts:

- `references/workload-analysis/scripts/profile_workload.py`
- `references/workload-analysis/scripts/ncu_profile_workload.py`
- `references/workload-analysis/scripts/run_nsys_profile.sh`
- `references/workload-analysis/scripts/run_ncu_profile.sh`
- `references/workload-analysis/scripts/parse_ncu_results.py`

The skill's output is conventionally a `report.md` plus profiling artifacts. Write all of those into `01_workload_analysis/`.

### Phase 2.2 — Apply the four augmentations

The deployed workload-analysis skill is excellent at *profiling* but doesn't enforce the framing discipline that distinguishes Rhu/Zhu papers. Layer these four augmentations on top before declaring Step 2 done:

#### (a) Industry-importance hook in the report's introduction

Open `01_workload_analysis.md` with a paragraph (drawn from `00_target_workload.md`) that names a deployed system and a metric — *not* an academic-area survey. See Material 1 §1 "What makes their version distinctive".

#### (b) Counter + property pairing for every bottleneck

Every named bottleneck must be reported as **both** a hardware-counter value (Nsight Compute counter, simulator stat) **and** a named architectural property — never just "memory-bound." Examples from Material 2 §3:

- Bad: "memory-bound" (a class, not a cause).
- Good: "DRAM throughput at 78% of peak with achieved arithmetic intensity 0.4 op/byte vs the device's 12 op/byte ridge — workload is in the BW-bound regime of the roofline because the dominant access pattern is sparse gather with no spatial locality."

When in doubt, write each §3 paragraph as alternating *measurement* / *interpretation* sentences (Material 2 §5).

#### (c) ≥3 scale points where available

The dominant-stage finding must hold across ≥3 model sizes / batch sizes / input dimensions. This guards against "the bottleneck moves at scale" reviewer attacks. (See Material 2 §2.) If the workload doesn't admit 3 scale axes, document the limitation honestly.

#### (d) Tag findings against the §10 named-methodology inventory

Material 2 §10 lists 12 named methodological inventions (approximate-distributive operator commutation, sacrifice-the-unimportant-in-place, walk-the-memory-hierarchy quantification, etc.). For each root cause identified, tag which §10 invention(s) the eventual solution might pattern-match against. This pre-prunes Step 4's brainstorm.

Example tag block at the end of `01_workload_analysis.md`:

```markdown
## Methodology tags (§10 of research_methodology.md)
- Bottleneck #1 (DRAM bandwidth saturated by sparse gathers) → potentially addressable by:
  - §10.1 Approximate-distributive operator commutation (if `F(A(x)) ≈ A(F(x))` reorders gathers vs reductions)
  - §10.11 Walk-the-memory-hierarchy quantification (if internal BW headroom exists at deeper DRAM levels)
- Bottleneck #2 (TLB pressure) → potentially addressable by:
  - §10 unnamed but classic — custom MMU à la NeuMMU
```

### Phase 2.3 — Write the artifact

Final artifact: `01_workload_analysis/01_workload_analysis.md`. Co-locate profiling raw outputs (nsys-rep, ncu-rep, parsed CSVs, plots) in the same directory. The file's structure mirrors the eventual §3 of the paper:

```markdown
# Workload Analysis: <workload name>

## 1. Industry-importance hook
<one paragraph from Step 1 framing why this workload matters>

## 2. Profiling setup
- GPU: <from gpu_spec.json>
- Workload: <(algorithm, benchmark, dataset) from Step 1>
- Scale points: <list>
- Tools: nsys X.Y.Z, ncu A.B.C
- Reproducibility: <command lines, seeds>

## 3. Stage breakdown
<stacked-bar plot + per-stage % numbers, swept across scale points>

## 4. Counter-level root cause (per dominant stage)
### Stage X (P% of latency)
**Measurement:** <counter values from ncu>
**Interpretation:** <named architectural property>
**Roofline placement (if BW-vs-compute):** <achieved AI vs ridge>

## 5. Methodology tags
<§10 invention candidates per bottleneck — pre-feeds Step 4>
```

### Phase 2.4 — Checkpoint

Update `PROGRESS.md` via `scripts/update_progress.py 2 done 01_workload_analysis/01_workload_analysis.md` and stop. Hand back to the user for review of the bottleneck story before Step 3 starts.

## Common pitfalls

- **Skipping the augmentations.** A bare profiling report is not a Step 2 artifact. The four augmentations are what turn it into the foundation of a paper.
- **Reporting "memory-bound" without a counter.** That's a class, not a cause. Always pair.
- **One scale point.** Reviewers will ask "what about at production batch size?" Have the answer pre-baked.
- **No reproducibility.** Future Steps 4–6 will need to re-run the workload to validate proposed solutions; if the setup isn't reproducible, the rest of the project stalls.
