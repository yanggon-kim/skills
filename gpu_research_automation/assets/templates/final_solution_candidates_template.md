# Final Solution Candidates

Running ledger of which solutions ultimately survive to become papers. Step 4 produces an *initial brainstorm* of N₀ candidate ideas in `03_solutions/03_solutions.json`. Through Step 6 some are dropped, some survive, and new entries are added whenever orthogonal survivors are combined. This file records that survival fate continuously.

The **count of `survived` + `combined-from-…` entries equals N**, the number of papers produced at Step 8.

Mutate via `scripts/update_solution_ledger.py`.

## Schema

| Field | Meaning |
|-------|---------|
| `id` | Surviving entry's identifier (e.g. `sw_02`, `hw_03`, `combined_sw02_hw03`). |
| `status` | One of `in_progress`, `survived`, `dropped`, `combined-from-X-and-Y`. |
| `from_brainstorm_id / combination_of` | For individuals: original `03_solutions.json` id. For combinations: `combination_of: [id_a, id_b]`. |
| `reason_for_status` | Free text. Populated when `status: dropped` (e.g. "implemented faithfully but no speedup"). |
| `implementation_dir` | Path under `05_implementations/`. |
| `final_paper_id` | The `paper_<id>` it will become at Step 8. |

## Ordering invariant

Combination entries (`combined-from-…`) **never** appear before all individual entries have terminal status (`survived` or `dropped`). Phase 6A must complete before Phase 6B.

## Ledger

| id | status | from_brainstorm_id / combination_of | reason_for_status | implementation_dir | final_paper_id |
|----|--------|--------------------------------------|-------------------|--------------------|----------------|
