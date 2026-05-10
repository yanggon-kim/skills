# Step 6A — Individual Implementations First

## Purpose

Implement and evaluate every individual idea from `03_solutions/03_solutions.json`. Drop those that don't show speedup after **faithful** implementation. The result is a vetted set of validated individual solutions, captured in `final_solution_candidates.md`.

Phase 6A must complete fully before Phase 6B begins — combinations of invalidated individuals are wasted effort.

## Inputs

- `03_solutions/03_solutions.json` — the brainstorm.
- `04_simulation_setup/` — GPGPU-Sim baseline (for HW ideas) and `build_plan.md`.
- `gpu_spec.json` — for SW ideas evaluated on the real GPU.

## Procedure

### Phase 6A.1 — Initialize `final_solution_candidates.md`

If it doesn't exist yet, create from the template at `assets/templates/final_solution_candidates_template.md`. The file's schema:

```markdown
# Final Solution Candidates

| id | status | from_brainstorm_id / combination_of | reason_for_status | implementation_dir | final_paper_id |
|----|--------|--------------------------------------|-------------------|--------------------|----------------|
```

Use `scripts/update_solution_ledger.py` to mutate the file rather than free-form Edit calls.

### Phase 6A.2 — Implement each idea

For each entry in `03_solutions.json`:

1. **Create the implementation directory.** `05_implementations/<id>/` (e.g. `05_implementations/sw_01/`, `05_implementations/hw_03/`).
2. **Append a ledger entry** with `status: in_progress`, `from_brainstorm_id: <id>`, `implementation_dir: 05_implementations/<id>/`. Run `scripts/update_solution_ledger.py append <id> in_progress 05_implementations/<id>/`.
3. **Implement.**
   - **For SW ideas:** rewrite the GPU kernel (CUDA/HIP) per the `proposed_mechanism` field. Keep semantics unchanged — the correctness-preserving rule from Step 4 still binds.
   - **For HW ideas:** modify GPGPU-Sim source per `04_simulation_setup/build_plan.md`. If a custom PTX-to-PTX compiler shim is needed for new instructions, build it under `05_implementations/<id>/compiler/`.
4. **Faithful implementation = the give-up criterion.** Implementation bugs, compile errors, or partial implementations are NOT grounds for giving up. Fix them first. Only after the implementation runs end-to-end and shows correct functional output may you evaluate for speedup.
5. **Run evaluation.**
   - SW ideas: real GPU, same workload as Step 2. Compare wall-clock / kernel time / energy with the Step 2 baseline.
   - HW ideas: GPGPU-Sim with the modified configuration. Compare against the Step 5 baseline simulator run.
6. **Decide status.**
   - **Speedup observed (≥ ~5% over baseline, or whatever the field considers significant for the workload):** flip ledger to `status: survived` with the measured speedup recorded in `reason_for_status` (e.g. `1.34x speedup on bootstrapping`).
   - **No speedup or slowdown:** flip ledger to `status: dropped` with `reason_for_status: "implemented faithfully but no speedup; <brief diagnostic>"`. Investigate *why* it failed — note whether the issue is fundamental (the cause-targeting was wrong) or implementation-specific (an alternative would help). Capture the investigation in `05_implementations/<id>/postmortem.md` so a future iteration can revisit.

### Phase 6A.3 — Track on PROGRESS.md

PROGRESS.md status for Step 6 sits at `in-progress` while Phase 6A runs. Each idea's terminal state should appear in `final_solution_candidates.md`, not in `PROGRESS.md`. When **every** idea has terminal status, mark Phase 6A done in PROGRESS.md (`scripts/update_progress.py 6A done`).

### Implementation order within Phase 6A

Follow `04_simulation_setup/build_plan.md` complexity ordering: **low-cost SW ideas first**, then medium-cost SW, then HW ideas in cost order. Reasoning:

- SW ideas are faster to implement and validate; they ground the speedup baseline.
- A surprising SW success may reframe the HW design space (a HW idea targeting a cause that SW already partially addressed becomes less attractive).
- HW ideas with simulator-core changes are highest-cost; do them when the build_plan has been validated.

If two ideas have a dependency (`dependencies_on_other_ideas` populated), implement the dependency first.

### Checkpoint after each idea (or batch)

For long-running Phase 6A, checkpoint to the user after each idea's terminal status — they may want to redirect the rest of the queue based on early findings. Don't grind through all 10 ideas silently.

## Output state at end of Phase 6A

- `05_implementations/sw_*` and `05_implementations/hw_*` directories, each with:
  - the implementation source
  - an `eval/` subfolder with timing/profile output
  - a `postmortem.md` if the idea was dropped
- `final_solution_candidates.md` with one entry per individual idea, each at terminal status.
- `PROGRESS.md` with Phase 6A marked done.

**Combination entries (`combined-from-…`) MUST NOT exist yet** — they belong to Phase 6B.

## Common pitfalls

- **Giving up too early.** A SIGSEGV in the modified GPGPU-Sim source is an implementation issue; fix it before declaring the idea dead. The give-up criterion only triggers when faithful implementation produces no speedup.
- **Skipping the postmortem.** When an idea is dropped, the *reason* is data — future Step 4 brainstorms (or follow-up papers) may want to revisit.
- **Letting status linger at `in_progress`.** If an idea is genuinely stuck, escalate to the user rather than leaving it open.
- **Starting Phase 6B before all individuals are terminal.** The descriptor's ordering invariant exists because combinations of dropped ideas are wasted effort; respect it.
