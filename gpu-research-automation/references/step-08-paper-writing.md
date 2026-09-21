# Step 8 — Paper Writing

## Purpose

Produce **N papers** in PDF form, one per surviving entry in `final_solution_candidates.md`. Each paper is self-contained: its own ACM template copy, its own figures, its own bibliography, and its own PDF. Authors are blank (you fill them in before submission). Length target: 12 body pages + references.

The paper structure follows `references/paper_structure_template.md` (Material 1) — the 8-section canonical layout. The methodology / framing follows `references/research_methodology.md` (Material 2).

## Inputs

- `final_solution_candidates.md` — the N surviving entries with their `final_paper_id` set.
- `06_evaluation/<id>/` — figures and tables for each surviving solution.
- `01_workload_analysis/01_workload_analysis.md` — the §3 content for each paper.
- `02_related_work/02_related_work.json` — for §2 / Related Work in each paper.
- `03_solutions/03_solutions.json` and `final_solution_candidates.md` — for §5 design decisions.
- `references/acm-template/` — the ACM proceedings LaTeX template (acmart.cls).
- `references/paper_structure_template.md` — Material 1.
- `references/research_methodology.md` — Material 2.

## Procedure

### Phase 8.1 — Determine N and the paper IDs

Read `final_solution_candidates.md`. Let **N** = the count of entries with `status: survived` or `status: combined-from-…`. Each entry's `final_paper_id` field names the paper directory.

Example after Phase 6B:

| id | status | final_paper_id |
|----|--------|----------------|
| sw_02 | survived | paper_sw02 |
| hw_03 | survived | paper_hw03 |
| hw_05 | survived | paper_hw05 |
| combined_hw03_hw05 | combined-from-hw03-and-hw05 | paper_combined_hw03_hw05 |

→ N = 4.

### Phase 8.2 — Per-paper directory layout

For each surviving entry, create `07_paper/<final_paper_id>/`:

```
07_paper/<final_paper_id>/
├── (ACM template files copied from references/acm-template/)
│   ├── acmart.cls
│   ├── ACM-Reference-Format.bst
│   ├── sample-base.bib
│   └── ...
├── paper.tex                         # main LaTeX source (renamed from sample-sigconf.tex)
├── refs.bib                          # paper-specific bibliography
├── figs/                             # paper-specific figures (copied from 06_evaluation/<id>/figs/)
└── paper.pdf                         # final output (after compile_paper.sh)
```

Use `cp -r references/acm-template/* 07_paper/<final_paper_id>/` to seed each paper with a fresh template, then rename `sample-sigconf.tex` → `paper.tex`.

### Phase 8.3 — Write the paper body

Each paper follows the canonical 8-section flow from `paper_structure_template.md`:

1. **Introduction** (~1.0–1.5 pages) — start with the industrial-importance hook from `00_target_workload/00_target_workload.md`. Don't rewrite Material 1's §1 guidance; follow it. Final paragraph names the proposed system and lists 4 contribution bullets, one of which is *always* the workload characterization.
2. **Background** (~0.5–1.5 pages) — the minimum primer needed to read §3. Compress aggressively.
3. **Workload Characterization / Motivation** (~2.0–3.0 pages — the load-bearing section) — port the contents of `01_workload_analysis.md` here, with both the §3.1 stage breakdown and the §3.2 counter-level root cause. Material 2 §3 is the discipline doc.
4. **Key Insight / Design Principle** (~1 paragraph) — one box translating the §3 root cause into the architectural lever.
5. **Design / Architecture** (~2.0–3.0 pages) — the proposed mechanism from `03_solutions.json` (or, for combination papers, the merged design from `05_implementations/combined_*/`). Tag each subsection with the §3 finding it addresses (Material 1 §5 distinctive trait).
6. **Implementation / Methodology** (~0.5–1.0 page) — simulator setup, RTL synthesis (if applicable), real-hardware setup, baselines, workload set.
7. **Evaluation** (~2.5–3.5 pages) — start with the **counter re-measurement plot** (per-paper Figure 17 equivalent), then the speedup plot, then ablation, then sensitivity. Material 1 §7 distinctive trait + Material 2 §6 (closing the loop).
8. **Related Work + Conclusion** (~0.5–1.0 page) — compact. Use entries from `02_related_work.json` grouped by axis (algorithmic vs architectural) rather than chronologically.

For **combination papers** (e.g. `paper_combined_hw03_hw05`), the paper's narrative arc is "two orthogonal levers compounding" — exemplified by Mesorasi (Zhu MICRO 2020). The §3 should acknowledge both root causes; §5 has two clearly delineated subsections (one per lever); §7 must include the speedup-amplification plot showing the combination beats either constituent alone.

### Phase 8.4 — Author block, length, figures

- **Authors:** leave the `\author{}` block blank. The user fills in author names + affiliations before submission.
- **Length:** 12 body pages + references. The acmart.cls SIGCONF format counts pages excluding references; aim for ≤12 body pages.
- **Figures:** per Step 7, every paper must include:
  - One counter re-measurement plot per root cause from Step 2.
  - One speedup plot.
  - One ablation plot.
  - One sensitivity-sweep plot.
  
  Copy all relevant figures from `06_evaluation/<id>/figs/` to `07_paper/<final_paper_id>/figs/`. Ensure each figure's caption is self-contained — readers shouldn't need the body to interpret it.

### Phase 8.5 — Build the PDF

Run `scripts/compile_paper.sh 07_paper/<final_paper_id>/` for each paper. The script wraps `latexmk -pdf -interaction=nonstopmode` against `paper.tex`. Output: `07_paper/<final_paper_id>/paper.pdf`.

If compilation fails, the script reports the error. Common issues:
- Missing `acmart.cls` — re-copy from `references/acm-template/`.
- Bibliography errors — check `refs.bib` formatting.
- Missing figure files — verify all `\includegraphics` paths point to `figs/` files that exist.

### Phase 8.6 — Verification

After all N PDFs are built:

```bash
ls 07_paper/*/paper.pdf | wc -l   # should equal N
```

Each PDF should:
- Open without errors.
- Be ≤12 body pages (excluding references). Check: `pdfinfo 07_paper/<id>/paper.pdf | grep Pages` minus the references count.
- Have a blank author block.
- Include all four required figure types.
- Have a §7 first plot that re-measures a §3 counter.

### Checkpoint

Update `PROGRESS.md` via `scripts/update_progress.py 8 done` and stop. Hand back to the user with:

- The list of `<final_paper_id>` directories.
- The PDF paths.
- A brief summary per paper: speedup achieved, root cause addressed, paper title (drafted).

The user fills in author names, makes any final edits, and submits.

## Each paper is self-contained

Don't share figures across papers — each `<final_paper_id>/figs/` has its own copies. Don't share `refs.bib` either — each paper may cite different prior work. Self-containedness lets the user submit each paper to a different venue if they choose.

## Common pitfalls

- **Reusing one ACM template directory across all papers.** Each paper needs its own copy; otherwise compilation conflicts arise (latex auxiliary files clash).
- **Generic introduction.** Each paper's §1 must lead with the *specific* industrial framing for the *specific* solution it proposes — even though all papers share the same workload, their hooks differ subtly (a SW paper's hook is "fast deploy" while a HW paper's hook is "future product").
- **Skipping the counter re-measurement plot in §7.** The single most important figure in the paper. If `06_evaluation/<id>/figs/` doesn't have it, push back to Step 7 before building the PDF.
- **Author block accidentally populated with placeholders.** Reviewers shouldn't see "John Doe, Some University." Truly blank — the LaTeX template's anonymous mode is fine.
- **One PDF for all surviving solutions.** That's a survey paper, not the per-solution paper structure the descriptor requires. N solutions = N PDFs.
