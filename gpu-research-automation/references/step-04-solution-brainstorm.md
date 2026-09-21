# Step 4 — Solution Brainstorming

## Purpose

Generate an exhaustive list of candidate accelerations addressing the root causes from Step 2. Output is `03_solutions/03_solutions.json`, the *initial brainstorm*. (`final_solution_candidates.md` — the running ledger of which ideas survive — does not exist yet; it is created in Step 6 as ideas are implemented.)

## Inputs

- `01_workload_analysis/01_workload_analysis.md` — root causes with §10-invention tags.
- `02_related_work/02_related_work.json` + `synthesis.md` — what's already been done.
- `references/research_methodology.md` §4 (solution-by-targeting-the-cause) and §10 (named methodological inventions).

## Procedure

### Brainstorm exhaustively first, prune later

For each root cause from Step 2:

1. Walk the §10 named-methodology inventory of Material 2. For each invention, ask: "could this address the cause?" Don't prune on quality yet — we want a wide net.
2. Ask: "has prior work (`02_related_work.json`) already targeted this cause for GPUs?" If yes, ideas in that direction must be *meaningfully different* — different analysis or different mechanism.
3. Generate at least 3–5 candidate ideas per root cause, split by category (SW vs HW).

The goal is a non-trivial list — the example "around 3 software + 5 hardware" in the descriptor is heuristic, not a target. Brainstorm wide, then prune duplicates and obvious non-starters.

### Two categories

#### 1. Software-Based Approaches — *correctness-preserving only*

Software-Based ideas in this skill must **not** change the algorithm's mathematical semantics or, for neural-network workloads, the trained model's behavior. The reason is cost: any change that alters semantics requires regression tests to prove correctness, and for neural networks this means **full re-training** — prohibitively expensive in compute and time. The Software-Based path's value is *fast time-to-paper*: no re-training, no accuracy-vs-baseline argument, just an implementation-level optimization measured for speedup.

**In-scope software optimizations** include (non-exhaustively):

- Loop-unrolling depth and inner-loop restructuring
- Software / hardware prefetching, async-copy scheduling
- Memory-access-pattern restructuring (coalescing, swizzling, layout transforms that preserve element identity)
- Tiling, double-buffering, and pipeline staging
- Kernel fusion and scheduling
- Deferring or overlapping computation phases (work decomposition that doesn't change the result)
- Better warp / block / grid launch parameters and occupancy tuning

**Out of scope for the Software-Based path** (move these to Hardware-Based or to Step 6 combinations instead):

- Operator commutation (e.g. swapping `F(A(x))` ↔ `A(F(x))` à la Mesorasi) — this changes math even if approximately equivalent.
- Quantization, sparsification, or pruning of weights / activations.
- Approximate algorithms with an accuracy budget (those need re-training to recover accuracy).
- Any change requiring a model checkpoint to be re-fit.

If a brainstormed software idea requires changing algorithm semantics, **recategorize it**: either move it to the Hardware-Based path (algorithm-architecture co-design with explicit retraining as part of the contribution) or keep it for Step 6 as a combination ingredient.

#### 2. Hardware-Based Approaches

Add new extensions to the GPU or improve inefficient parts of the existing GPU design. Implemented and evaluated in GPGPU-Sim (Step 5+). May include new instructions, new modules, modifications to existing modules, or a custom simple PTX-to-PTX compiler for inserting new instructions. Algorithmic changes (operator commutation, quantization, etc.) are allowed in this path because the path inherently involves implementation effort — adding a retraining step is incremental cost.

### Output schema — `03_solutions/03_solutions.json`

```json
{
  "metadata": {
    "brainstorm_date": "2026-05-10",
    "rooted_in_workload_analysis": "01_workload_analysis/01_workload_analysis.md",
    "informed_by_related_work": "02_related_work/02_related_work.json"
  },
  "solutions": [
    {
      "id": "sw_01",
      "category": "sw",
      "title": "Async-prefetched key-switching tables",
      "root_cause_it_targets": "DRAM gather pattern in CKKS bootstrapping (Bottleneck #1 in 01_workload_analysis.md)",
      "proposed_mechanism": "Issue async copy of next-iteration's key-switching table into shared memory while current iteration's compute runs.",
      "novelty_axis": "different-solution-same-analysis",
      "expected_effect": "Hide DRAM latency behind compute; ~1.3-1.8x speedup expected on bootstrapping kernel.",
      "implementation_cost_estimate": "low — kernel rewrite, no semantic changes",
      "dependencies_on_other_ideas": []
    },
    {
      "id": "hw_03",
      "category": "hw",
      "title": "On-chip NTT-friendly butterfly unit",
      "root_cause_it_targets": "Low arithmetic intensity of NTT at high moduli (Bottleneck #2)",
      "proposed_mechanism": "Add a dedicated radix-N butterfly datapath inside the SM with chained MAD/MOD ops.",
      "novelty_axis": "different-solution-same-analysis",
      "expected_effect": "Increase per-cycle NTT throughput by ~4x without changing memory subsystem.",
      "implementation_cost_estimate": "high — new datapath, GPGPU-Sim model + RTL-equivalent design",
      "dependencies_on_other_ideas": []
    }
  ]
}
```

### Field semantics

- **`id`** — short tag (`sw_NN` or `hw_NN`); used as directory name in Step 6 (`05_implementations/sw_01/`).
- **`category`** — `sw` or `hw`.
- **`root_cause_it_targets`** — explicit reference to a finding in `01_workload_analysis.md` (use the bottleneck number / counter name). This is the field Step 6's orthogonality test reads.
- **`proposed_mechanism`** — how the cause is removed or amortized. The other field Step 6 reads for orthogonality.
- **`novelty_axis`** — `different-analysis` (we frame the cause differently than prior work) or `different-solution-same-analysis` (analysis matches prior work, mechanism differs).
- **`dependencies_on_other_ideas`** — for ideas that only make sense atop another (e.g. a HW idea that requires a SW idea's data layout); used in Step 6 to schedule implementation order.

### Pruning rules before saving

After exhaustive brainstorm, drop:

- Duplicates (same `root_cause_it_targets` + `proposed_mechanism`).
- Ideas that match a paper in `02_related_work.json` exactly with no novelty axis.
- SW ideas that fail the correctness-preserving rule and can't be sensibly recategorized.

Note dropped ideas at the end of the JSON in a `dropped` array with reasons — useful when the user reviews and may want to revive one.

### Checkpoint

Update `PROGRESS.md` via `scripts/update_progress.py 4 done 03_solutions/03_solutions.json` and apply the checkpoint policy in `SKILL.md`. Expose the brainstorm for review and incorporate any user edits before dependent work; continue if authorized. Often the user has domain insight — accept their edits.

## Common pitfalls

- **Brainstorm too narrow.** If only 2–3 ideas survived from a workload with 4 root causes, the brainstorm was lazy. Re-run by walking *every* §10 invention against *every* root cause.
- **SW path with operator commutation.** Operator commutation is in the Hardware-Based path or Step 6 combinations — not in the Software path, because it changes semantics. The descriptor is firm on this; respect it.
- **No `root_cause_it_targets` linkage.** An idea that doesn't trace to a §3 finding is scope creep — drop it.
- **Pre-pruning at brainstorm time.** Capture wild ideas; let the user prune. The cost of writing one extra JSON entry is low; the cost of a missed contribution is high.
