# How an architecture paper is written — read before any writing pass

Part of the architecture-paper-writing skill. Governs: the reading order across every section. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

Purpose: the paper is written against a fixed set of contracts distilled from six reference papers and from the user's
corrections across every pass of an earlier ASPLOS draft (SPLEX). This directory holds all of them. Read the files for the task
at hand before touching a section's source.

## Hierarchy

1. **Cross-cutting contracts** — apply to every sentence and every section: `01_sentence_style.md`, `02_structure_and_figures.md`.
2. **Per-section guides, in paper order** — the moves, diction and never-lists of the reference papers' corresponding sections:
   `03_abstract.md` → `04_introduction.md` → `09_motivation_and_characterization.md` (the motivating half of Background, and Motivation & Observation) →
   `05_design.md` → `06_methodology_evaluation.md` → `07_conclusion.md`.
3. **Lessons** — what went wrong when the guides were applied and how the user corrected it: `08_design_section_lessons.md`
   (the design section) and `11_writing_lessons.md` (every section, one rule per entry). The mechanics of an edit that must
   survive a build — numbers, floats, page limits, references — are `10_production_and_verification.md`.

A guide states rules with a sentence quoted verbatim from a named reference paper; a lessons file states rules with a before → after
quoted from an earlier draft. When the two disagree, the lessons file is the later word.

## Reading order per task

| task | read, in this order |
|---|---|
| any edit, any section | `01` first — the sentence test on every changed sentence |
| any sentence that cites prior work | `12` — placement decides what each reference is held responsible for |
| abstract | `01` → `03` → `04` §A (the abstract is the introduction's arc in miniature) |
| Introduction | `01` → `02` §1–2 → `04` |
| Background / Motivation & Observation | `01` → `02` §1–2 (the narrative spine, L1) → `09` (the section anatomy, the six paragraph skeletons, the number-density and design-implication caps; the reader test in `09` §I runs before the commit) |
| Design (any mechanism paragraph anywhere) | `01` → `02` §1 → `05` → `08` (the checklist in `08` §4 runs before the commit) → `11` |
| Methodology / Evaluation | `01` → `02` §1–2 → `06` |
| Related Work | `01` → `02` §1–2 → `12` (category-level citation grouping); every claim about prior work gets a row in the paper's fact-check table |
| Conclusion | `01` → `03` → `07` |
| a figure, a caption, a table's look | `02` §3 (F1–F7, the LazyDP visual system) → the header of the figure's generator script |

## One line per file — what it settles

- `01_sentence_style.md` — the sentence-level contract: a sentence earns its place with a fact, a number or a necessary forward reference;
  the species to delete (drum-roll, praise, meta, restatement, personification), what to keep, and the direct-claim-colon-facts merge.
- `02_structure_and_figures.md` — the narrative spine and section anatomy learned from the five papers (§1–2) and the figure
  system adopted from LazyDP (§3, F1–F7: luminance ramp, sky-blue for what the system adds, red only for marks, four spines, no hatches).
- `03_abstract.md` — the seven moves of the six reference abstracts, the diction table, the ≤ 200-word target.
- `04_introduction.md` — the eight-move arc of the six introductions (landscape opening, claim-first paragraphs, the contribution list).
- `05_design.md` — the move order for a named mechanism (name → definition → validity → payoff → figure → implementation → cost),
  the section anatomy, alternative-then-reason, costs in place, the diction table, the never-list, and the worked design-section mapping with its guard classes.
- `06_methodology_evaluation.md` — the anatomy and diction of §Method / §Eval: message before audit trail, table facts never repeated,
  purpose-and-comparison openers, one headline number per subsection.
- `07_conclusion.md` — the five moves of the six conclusions: claim, key idea, what was done, one number, outlook; no result clause.
- `09_motivation_and_characterization.md` — the anatomy of a characterization section ([CAL] is nothing else, so it is the archetype):
  the opening that declares vehicle and sweep, the six measurement-paragraph skeletons, the one-number-in-three density, where a design
  implication is allowed (at most one per subsection, last), how a counterexample and a negative result are printed, the frequency-ranked
  measurement vocabulary and the words the six never use, the caption contract, and the five-role reader test for a characterization paragraph.
- `08_design_section_lessons.md` — the first-time-reader test, nine principles with the design passes' before → after quotes, the sentence
  habits that failed, and the ten-line pre-commit checklist.
- `10_production_and_verification.md` — how much checking an edit needs, where every number must come from, how floats actually move,
  how to prove a page is what the build says it is.
- `12_citation_placement.md` — where a citation goes inside a sentence: entity at its name, claim at the smallest clause,
  one group per category or example; the LaTeX tie and line-breaking consequences of moving one.
- `11_writing_lessons.md` — the author's corrections on the rendered page, one rule per entry (rule, why, example); the later word
  when it disagrees with a per-section guide.

## The reference papers (the PDFs live in `references/papers/`, indexed in `references/papers/INDEX.md`)

Two sets, one superset of the other:

- **Set A — structure and lessons (`02` §1–2, five papers):** [M] Mesorasi, MICRO 2020 (`references/papers/mesorasi-micro20.pdf`) ·
  [TC] Tensor Casting, HPCA 2021 (`references/papers/tensor-casting-hpca21.pdf`) ·
  [SS] SmartSAGE, ISCA 2022 (`references/papers/smartsage-isca22.pdf`) · [PVF] Low-Latency Proactive Continuous Vision, PACT 2020
  (`references/papers/low-latency-proactive-vision-pact20.pdf`) ·
  [CAL] Characterization and Analysis of Deep Learning for 3D Point Cloud Analytics, IEEE CAL 2021
  (`references/papers/characterization-3d-point-cloud-cal21.pdf`).
- **Set B — the per-section guides (`03`–`07`, `09`) and the figure system (`02` §3), six papers:** Set A plus [LazyDP] LazyDP, ASPLOS 2024
  (`references/papers/lazydp-asplos24.pdf`); CAL has no design section and is excluded from `05`, and is conversely the archetype of `09` — the whole paper is a
  characterization. The figure system comes from LazyDP alone.

Every quote in `03`–`07` and `09` was grepped in the PDF text (`pdftotext`) before it was printed; where an earlier plan's quote differed from
the page, the page wins and the difference is noted in the guide.
