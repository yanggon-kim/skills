# Step 6B — Orthogonal Combinations of Validated Survivors

## Purpose

Phase 6A validated which individual ideas produce speedup. Phase 6B asks: do any *pairs* (or larger groups) of validated survivors *amplify* each other when combined? If yes, the combination becomes a new candidate paper.

The purpose is **speedup amplification**, not novelty. Two orthogonal levers should compound: solving two distinct bottlenecks at once produces a bigger end-to-end win than either lever alone.

## The canonical precedent — Mesorasi (Zhu MICRO 2020)

Mesorasi paired an *algorithmic* lever (delayed-aggregation operator commutation, `F(A(x)) ≈ A(F(x))`) with a *hardware* lever (small NPU extension for neighbor-search) to compound up to **3.6× / 6.7× speedup** — substantially beyond either lever alone. Even though Mesorasi is not GPU-only, the pattern (algorithmic + architectural composition) is exactly what Phase 6B aims to reproduce.

When in doubt about whether a combination is worth attempting, ask: "if these two ideas address distinct bottlenecks, would they compound the way Mesorasi's two levers compounded?"

## Inputs

- `final_solution_candidates.md` after Phase 6A — must have all individual entries at terminal status.
- `03_solutions/03_solutions.json` — for the original `root_cause_it_targets` and `proposed_mechanism` fields (used in orthogonality checking).
- `05_implementations/sw_*` and `05_implementations/hw_*` — the surviving implementations.

## Procedure

### Phase 6B.1 — Identify orthogonal pairs (and triples)

Run `scripts/find_orthogonal_pairs.py`. It reads `03_solutions.json` and the `survived` subset of `final_solution_candidates.md`, then identifies pairs (and triples, if applicable) where:

- The `root_cause_it_targets` fields don't overlap (each idea attacks a different bottleneck).
- The `proposed_mechanism` fields don't overlap (each idea uses a different implementation lever).

Two ideas attacking the *same* root cause are not orthogonal — they're competing alternatives, not compounding levers. Two ideas using the *same* mechanism are also not orthogonal.

Output: a list of candidate combination tuples printed to stdout, plus written to `05_implementations/_orthogonality_report.md` for review.

### Phase 6B.2 — Implement each combination

For each candidate combination (e.g. `(sw_02, hw_03)`):

1. **Append a ledger entry** with `status: in_progress`, `combination_of: [sw_02, hw_03]`, `implementation_dir: 05_implementations/combined_sw02_hw03/`. Run `scripts/update_solution_ledger.py combine sw_02 hw_03`.
2. **Create the directory** `05_implementations/combined_<id_a>_<id_b>/`.
3. **Compose the implementations.** The combined implementation runs *both* levers together — typically the SW idea's kernel changes layered atop the HW idea's GPGPU-Sim modifications. Resolve any interactions (e.g. if both ideas modify shared memory layout, decide a coherent layout that satisfies both).
4. **Run evaluation** in the appropriate environment (real GPU if both ideas are SW; GPGPU-Sim if any idea is HW; for mixed SW+HW, GPGPU-Sim with the modified config).
5. **Apply the combination-specific give-up criterion** (next subsection).

### Phase 6B.3 — Combination-specific give-up criterion

A combination is kept **only if** its measured speedup *exceeds* the strongest constituent's individual speedup.

- If `combined_sw02_hw03` measures 2.5× and `hw_03` alone measured 2.4× and `sw_02` alone measured 1.5×, the combination's amplification (2.5 / 2.4 = 1.04×) is too marginal — drop it. The individual papers stand on their own.
- If `combined_sw02_hw03` measures 4.1× vs `hw_03`'s 2.4× and `sw_02`'s 1.5×, the combination amplifies (4.1 / 2.4 = 1.7×) — keep it.

Use a clear threshold (e.g. 1.2× over the strongest constituent) when the workload's noise floor is large; otherwise even a meaningful amplification is hard to interpret.

When dropped, populate `reason_for_status` with the diagnostic — e.g. `"constituents not truly orthogonal in practice; combined speedup matches hw_03 alone (2.5 / 2.4 = 1.04x amplification)."`

When kept, set `status: combined-from-X-and-Y` and reserve a `final_paper_id` for Step 8 (e.g. `paper_combined_sw02_hw03`).

### Phase 6B.4 — Triples and higher-order

If three or more orthogonal survivors exist, exhaustively try the triple combination too. The give-up criterion extends: a triple is kept only if its speedup exceeds the best *constituent pair* (not just the best individual). This guards against a triple that's only marginally better than a successful pair.

### Checkpoint at end of Phase 6B

When all orthogonal candidate combinations have terminal status:

- `final_solution_candidates.md` has the final list of N papers (count of `survived` + `combined-from-…` entries).
- Each surviving entry has `final_paper_id` set.
- Run `scripts/update_progress.py 6 done` (Step 6 as a whole — both phases).

Hand back to the user. They review the surviving set; this is the last chance to add/remove before evaluation and writing.

## Output state at end of Phase 6B

- `05_implementations/combined_*/` directories for each surviving combination.
- `final_solution_candidates.md` with N entries (survived individuals + survived combinations), each with `final_paper_id`.
- `PROGRESS.md` Step 6 marked `done`.

A reader of `final_solution_candidates.md` should be able to predict exactly which `07_paper/paper_<id>/` directories Step 8 will produce.

## Common pitfalls

- **Combining ideas that target the same root cause.** That's not orthogonal — that's competition. Use `find_orthogonal_pairs.py` rigorously.
- **Skipping the amplification check.** A combination that doesn't amplify is two papers, not one. The user may still want it as a paper if it's a unified narrative, but the default is: don't bundle.
- **Implementing combinations before all individuals are terminal.** Re-read the ordering invariant from Step 6A — it's load-bearing.
- **Forcing a combination because it would be neat.** Reviewers see through this. The Mesorasi precedent works because both levers genuinely compound — without that, the combination paper is weaker than the two individual papers.
