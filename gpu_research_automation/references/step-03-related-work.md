# Step 3 — Related Research Search

## Purpose

Survey the GPU-acceleration literature for the target workload. The output is `02_related_work.json`, a structured corpus that informs Step 4's brainstorm (so we don't propose what's already been done) and Step 8's Related Work section.

## Inputs

- `00_target_workload/00_target_workload.md` — names the workload and target (algorithm, benchmark).
- `01_workload_analysis/01_workload_analysis.md` — the bottleneck framing; we want to know how prior work has framed the same workload.

## Procedure

### Inclusion rule

- **Any downloadable paper** counts (peer-reviewed, arXiv, workshop, technical report, thesis — all fine if the PDF is obtainable).
- **System-papers that use GPUs alongside other accelerators** (CPUs, PIM, FPGAs, NPUs) are **in scope**, but the focus stays on GPU acceleration. Strict GPU-only papers should be the majority of the corpus.
- **Exclude** papers that use the same workload name but target a fundamentally different scale (e.g. "homomorphic encryption" papers about MPC protocol design without any HW/system content).

### Search strategy

1. Google Scholar searches: `<workload> GPU acceleration`, `<workload> CUDA`, `<workload> ISCA OR MICRO OR HPCA OR ASPLOS`.
2. ACM Digital Library / IEEE Xplore by venue — ISCA, MICRO, HPCA, ASPLOS, PACT for the last ~5 years.
3. arXiv listing under `cs.AR` (architecture) and `cs.DC` (distributed computing) cross-referenced with workload keywords.
4. Author homepages of researchers known for the workload (the Step 1 industry-relevance section often names them).
5. Citations of seminal papers (e.g. for FHE: BTS, ARK, F1, CraterLake).

For each paper found, attempt PDF acquisition — arXiv URL first, then publisher landing page, then author website. Failing all that, capture abstract-only data.

### Per-paper schema

Write `02_related_work/02_related_work.json` as an array of objects with these fields:

```json
{
  "title": "BTS: An Accelerator for Bootstrappable Fully Homomorphic Encryption",
  "authors": "S Kim; J Kim; MJ Kim; W Jung; J Kim; M Rhu; JH Ahn",
  "venue": "ISCA",
  "year": 2022,
  "url": "https://arxiv.org/abs/2112.15479",
  "pdf_status": "downloaded" | "abstract-only",
  "defined_bottleneck": "Bootstrapping dominates HE inference (>99% of cycles); current GPUs cannot saturate the high-degree NTT throughput required.",
  "root_cause_analysis": "NTT operations have low arithmetic intensity at the modulus sizes used in CKKS; GPU memory hierarchy is mismatched to the recurring read patterns of bootstrapping.",
  "targeting_strategy": "Custom accelerator with dedicated NTT pipelines and on-chip key-switching memory; algorithm-level scheduling to overlap stages.",
  "solution_methodology": "ASIC-class accelerator design + microarchitecture co-design + analytical modeling of NTT throughput.",
  "benchmarks": {
    "algorithms": ["CKKS", "BFV"],
    "datasets": ["standard CKKS parameter sets", "encrypted ResNet inference"],
    "methodology": "End-to-end bootstrapping latency measured against GPU baseline (V100)."
  },
  "mean_speedup": 5.5,
  "max_speedup": 9.6,
  "platform": "ASIC",
  "gpu_focused": false,
  "notes": "GPU baseline only; not GPU-acceleration but informs HE bottleneck framing."
}
```

`platform` is one of `GPU`, `ASIC`, `FPGA`, `PIM`, `CPU`, `mixed`. `gpu_focused: true` means the paper *targets* GPUs (vs uses them as a baseline). Both flags help Step 4 figure out which root causes have already been addressed *for GPUs specifically*.

### Sufficient corpus size

Aim for **≥10 papers** with full PDF retrieval, plus as many abstract-only entries as you find. If the workload is niche (small literature), document that explicitly in the JSON via a top-level metadata key:

```json
{
  "metadata": {
    "search_completion_date": "2026-05-10",
    "total_candidates_examined": 47,
    "included_full_pdf": 12,
    "included_abstract_only": 6,
    "excluded": "29 papers — wrong scale, MPC-only, etc."
  },
  "papers": [ ... ]
}
```

### Pre-Step-4 synthesis (in the same artifact)

After the JSON, write a short companion `02_related_work/synthesis.md` (250–400 words) that answers:

- Which root causes from `01_workload_analysis.md` have been targeted by prior GPU work? (group papers by the bottleneck they attacked).
- What's *missing* — bottlenecks the literature hasn't addressed for GPUs, or framings the literature got wrong.
- What's the speedup bar to beat? (max reported GPU-acceleration number.)

This synthesis pre-prunes Step 4's brainstorm by surfacing the genuinely-unaddressed gaps.

### Checkpoint

Update `PROGRESS.md` via `scripts/update_progress.py 3 done 02_related_work/02_related_work.json` and stop.

## Acquisition tactics (drawn from a prior corpus job)

We have prior experience acquiring 78 papers' worth of related-work data for Rhu/Zhu's groups. The tactic that worked:

- arXiv URLs from the start whenever available (~10–20% of papers).
- Author lab pages for the rest (often have author-hosted preprints).
- Google Scholar "All versions" → tech-report PDFs.
- Last resort: WebFetch the publisher landing page for the abstract.

For batch acquisition, use parallel agents (one per ~15-paper batch) to do the search-and-download work concurrently. Each agent writes per-paper summary markdown files alongside the JSON entries.

## Common pitfalls

- **Including only ISCA/MICRO/HPCA/ASPLOS.** Workshop / arXiv preprints often surface more recent state-of-the-art, especially for fast-moving workloads (LLM serving, neural rendering). Cast wider initially, then prune.
- **Skipping the synthesis step.** A raw JSON of papers is hard for Step 4 to act on; the synthesis names which gaps remain.
- **Counting non-GPU papers as "GPU work".** The `gpu_focused` flag matters — Step 4 brainstorms ideas in the GPU-acceleration design space, so counting BTS (an ASIC paper) as already-targeting-GPUs would suppress legitimate Step 4 ideas.
