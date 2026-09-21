---
name: gpu-research-automation
description: Run or resume end-to-end GPU architecture research, from workload selection and profiling through related work, simulator implementation, evaluation, and ACM papers. Use for GPU research projects targeting ISCA, MICRO, HPCA, or similar venues. For profiling alone, use workload-analysis.
metadata:
  version: 1.0.0
  author: yanggon
---

# GPU Research Automation

## Codex execution

Resolve bundled paths relative to this skill's directory from the installed catalog. Invoke scripts by their full paths with the working directory set to the user's project (or research workspace for tracker updates). Write results there, not into the skill. Use the tools actually exposed by the current Codex client.


This skill drives a complete GPU computer-architecture research project from a one-line workload prompt to N publishable ACM papers. The workflow is phased: every step produces an artifact and records its evidence. Honor checkpoints the user requests. A single-step request ends after that step; authorization for an end-to-end run permits continuing through completed phases without asking again. Pause for material unresolved research choices, missing access, or changes outside the authorized scope.

The methodology is the one distilled from Minsoo Rhu's (KAIST VIA Lab) and Yuhao Zhu's (Univ. of Rochester / Horizon Lab) corpus: industry-grounded workload selection, counter-driven root-cause analysis, solutions disciplined to be one-to-one responses to those root causes, and evaluation that re-measures the same counters under the proposed system to close the loop. Three reference materials anchor the discipline:

- **Material 1 — `references/paper_structure_template.md`**: the canonical 8-section paper layout and what each section must contain.
- **Material 2 — `references/research_methodology.md`**: the analytical lens (workload selection, quantitative-first definition, counter→property pairing, solution-by-targeting-the-cause, 12 named methodological inventions).
- **Material 3 — the installed `workload-analysis` skill (`../workload-analysis/SKILL.md` in this collection)**: the deployed workload-analysis skill, used in Step 2 with four augmentations layered on top.

Load the installed `workload-analysis` skill when Step 2 needs it; if missing, install it from this collection before profiling. Read the relevant sections of all three before producing any artifact whose §3 claims, §5 design decisions, or §7 evaluation plots are at stake. Don't skim — these materials encode multiple years of how-this-line-of-research-actually-works.

## Workspace conventions

When the user kicks off a new project, create a workspace under **the current working directory** (`$PWD`), not under any fixed path inside the skill itself. Different projects can live in different parent directories; a researcher can park a recommendation-systems project in `~/proj/recsys/` and a homomorphic-encryption project in `~/proj/fhe/` without collision.

Workspace layout (per invocation):

```
$PWD/02_projects/<workload-slug>_<YYMMDD>/
├── PROGRESS.md                        # top-level step-status tracker
├── final_solution_candidates.md       # surviving solutions / combinations → final paper count N
├── gpu_spec.json                      # auto-detected from nvidia-smi
├── 00_target_workload/00_target_workload.md
├── 01_workload_analysis/01_workload_analysis.md   (+ profiling artifacts)
├── 02_related_work/02_related_work.json
├── 03_solutions/03_solutions.json
├── 04_simulation_setup/                # GPGPU-Sim configs + reproduction
├── 05_implementations/
│   ├── sw_idea_01/  ...                # Phase 6A sibling subfolders
│   ├── hw_idea_01/  ...
│   └── combined_<ids>/                 # Phase 6B (only after 6A is done)
├── 06_evaluation/                      # plots, tables
└── 07_paper/                           # one subdirectory per surviving solution
    ├── paper_<id1>/                    # ACM template + figs/ + paper.pdf
    ├── paper_<id2>/
    └── ...
```

Use `scripts/init_workspace.sh <workload-slug>` to bootstrap a fresh workspace. It creates the directory tree, populates the two top-level trackers from `assets/templates/`, and runs `scripts/detect_gpu.py` to write `gpu_spec.json`.

## The two top-level trackers

`PROGRESS.md` records, per step, the status (`pending` / `in-progress` / `blocked` / `done`), the artifact paths produced, and any user-supplied edits or feedback collected at each checkpoint. **Read it on every invocation** — it is the source of truth for "what step are we on". Update it through `scripts/update_progress.py` rather than manual file edits; the file's structure is rigid and the script keeps it consistent.

`final_solution_candidates.md` records the survival fate of every solution candidate: which were dropped (with reason), which survived, which were combined (and from what). It is empty until Step 6 begins, then grows continuously through Step 6 and Step 7. The number of `survived` + `combined-from-…` entries equals **N**, the number of papers produced at Step 8. Update it through `scripts/update_solution_ledger.py`.

A reader of these two files alone should be able to predict (a) where in the workflow the project is, and (b) which `07_paper/paper_<id>/` directories will eventually exist.

## Phased execution model

Within the scope authorized by the user, each step:

1. Reads `PROGRESS.md` to confirm the previous step is `done` and the current step is `pending`.
2. Reads any prior-step artifacts it depends on.
3. Runs the step procedure (see `references/step-NN-*.md`).
4. Writes the step's artifact to disk.
5. Updates `PROGRESS.md` (status: `done`, artifact path set).
6. Reports meaningful progress, then continues to the next authorized step unless a requested checkpoint or material blocker requires input.

Preserve PROGRESS.md across sessions and incorporate user edits before dependent work. A checkpoint records an artifact and review opportunity; it does not revoke authorization already given. Do not treat silence as approval for a new research direction.

## Resume UX

On invocation:

1. Run `ls $PWD/02_projects/` to detect existing projects.
2. If none — kick off a new one (ask user for workload name → `init_workspace.sh <slug>`).
3. If exactly one is in-progress — read its `PROGRESS.md` and resume when the user has requested continuation.
4. If multiple — list them with their slug, date, and "next pending step", then ask the user which to resume (or to start a new one).

Never silently pick when there are multiple in-progress projects. The user keeps each as a distinct research thread.

## The 8-step workflow at a glance

Each step has a dedicated detail file under `references/`. The summary below is the *menu*; do not try to execute a step from this summary alone — load the step-detail file before starting.

| Step | Title | Detail file | Artifact |
|------|-------|-------------|----------|
| 1 | Target Workload Search | `references/step-01-target-workload.md` | `00_target_workload/00_target_workload.md` |
| 2 | Workload Analysis (augmented) | `references/step-02-workload-analysis.md` | `01_workload_analysis/01_workload_analysis.md` + profiles |
| 3 | Related Research Search | `references/step-03-related-work.md` | `02_related_work/02_related_work.json` |
| 4 | Solution Brainstorming | `references/step-04-solution-brainstorm.md` | `03_solutions/03_solutions.json` |
| 5 | Simulation Setup | `references/step-05-simulation-setup.md` | `04_simulation_setup/` populated |
| 6A | Individual Implementations | `references/step-06a-individual.md` | `05_implementations/sw_idea_*` and `hw_idea_*` |
| 6B | Orthogonal Combinations | `references/step-06b-combinations.md` | `05_implementations/combined_*` |
| 7 | Evaluation | `references/step-07-evaluation.md` | `06_evaluation/` plots + tables |
| 8 | Paper Writing | `references/step-08-paper-writing.md` | N PDFs at `07_paper/paper_<id>/paper.pdf` |

### Step-by-step pointers

- **Step 1** — web-search the workload's algorithms / benchmarks / datasets. Counts are flexible (≥3 of each is preferred but document what's available when fewer exist).
- **Step 2** — apply the deployed `workload-analysis` skill (in the installed `workload-analysis` skill (`../workload-analysis/SKILL.md` in this collection)) augmented with: (a) industry-importance hook in the intro, (b) every bottleneck reported as both a counter value *and* a named architectural property, (c) ≥3 scale points where available, (d) tag findings against the §10 named-methodology inventory of Material 2.
- **Step 3** — survey GPU-acceleration literature (system-papers using GPUs alongside other accelerators are in scope, but focus stays on GPU). JSON output with mean/max speedup, defined bottleneck, root-cause analysis, targeting strategy, methodology.
- **Step 4** — exhaustive brainstorm split into Software-Based (correctness-preserving only — implementation-level optimizations like loop-unrolling, prefetching, memory-access patterns; *no* operator commutation / quantization / pruning / approximate algorithms) and Hardware-Based. Output to JSON.
- **Step 5** — set up GPGPU-Sim baseline. Three-case missing-feature stance: (i) close analog exists → substitute (e.g. WGMMA → WMMA when bottleneck is preserved), (ii) genuinely new feature with no analog → implement (e.g. TMA), (iii) implementation infeasible → escalate to user with concrete alternatives.
- **Step 6A** — implement and evaluate every individual idea. Drop those that don't show speedup after faithful implementation.
- **Step 6B** — only after Phase 6A is fully complete: implement orthogonal combinations of survivors. Combination is kept only if its speedup *exceeds* the strongest constituent's. The Mesorasi (Zhu MICRO 2020) precedent is the canonical pattern: algorithmic + hardware levers compounding for ≥3.6× over either alone.
- **Step 7** — evaluate. The first plot of evaluation must re-measure the §3 root-cause counter under the proposed system (Crescent ISCA 2022 pattern: Figure 14 = speedup, Figure 17 = bank-conflict reduction). Auxiliary simulators (Ramulator, CACTI) only when needed.
- **Step 8** — write **N papers**, one per surviving entry in `final_solution_candidates.md`. Each `07_paper/paper_<id>/` is self-contained with its own ACM template copy, figures, and PDF. Authors blank, 12 body pages + references each.

## Closing-the-loop discipline (read every time §3 or §7 is being produced)

Material 2 is uncompromising on one point: every bottleneck claim must be re-measured under the proposed system, and the re-measurement plot must appear in §7. The Crescent paper (Zhu ISCA 2022, see `01_papers/01_zhu/2022_ISCA_Crescent.md` if available, else recall: bank-conflict reduction in Figure 17 paired with speedup in Figure 14) is the canonical exemplar. Any paper produced under Step 8 that lacks a "Figure 17" equivalent for each named root cause is incomplete — push back to Step 7 to generate it before building the PDF.

## Bundled scripts

Under `scripts/`:

- **`init_workspace.sh <workload-slug>`** — bootstrap `$PWD/02_projects/<slug>_<YYMMDD>/` with the full directory tree + the two top-level trackers + `gpu_spec.json`. Idempotent — refuses to clobber an existing dir.
- **`detect_gpu.py`** — emits `gpu_spec.json` from `nvidia-smi` (name, compute capability, memory, derived peaks). Used in Steps 2 and 5.
- **`update_progress.py <step> <status> [artifact]`** — atomic edit to PROGRESS.md.
- **`update_solution_ledger.py <action> [args]`** — atomic edits to final_solution_candidates.md (append, flip status, add combination).
- **`find_orthogonal_pairs.py`** — for Phase 6B; finds non-overlapping `root_cause_it_targets` × `proposed_mechanism` pairs from the surviving subset.
- **`compile_paper.sh <paper_dir>`** — wraps `latexmk -pdf` against the ACM template inside a paper directory.

Always prefer these scripts over rewriting their logic inline. They exist because the work is repetitive across the N papers and across invocations; deterministic helpers keep the trackers and the file system consistent.

## What success looks like

A complete invocation cycle produces:

- A populated workspace under `$PWD/02_projects/<slug>_<YYMMDD>/`.
- A `PROGRESS.md` that shows all 8 steps as `done`.
- A `final_solution_candidates.md` with N entries (`survived` + `combined-from-…`), each linked to a `07_paper/paper_<id>/`.
- N PDF papers at `07_paper/paper_<id>/paper.pdf`, each 12 body pages, ACM-formatted, blank author block, with the closing-the-loop §7 discipline visible in the figures.

Anything less than this is incomplete; report what's missing instead of glossing over it.
