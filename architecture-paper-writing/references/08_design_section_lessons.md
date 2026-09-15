Part of the architecture-paper-writing skill. Governs: the design section (and any mechanism paragraph elsewhere). Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

# Design-section lessons — the mistakes the §4 passes made and how the user corrected them

Read before writing or editing any design text (§4, and any paragraph elsewhere that explains a mechanism). Every example below is a
real before → after from the SPLEX §4.1 / §4.2 / §4.3 rounds of 2026-09-05 → 2026-09-07 (quoted from that draft's change maps,
where the full maps live) — each pair is labelled *(SPLEX example)*. This file is the companion of `05_design.md` (the reference papers'
moves A–I); the other guides are `03_abstract.md`, `04_introduction.md`, `06_methodology_evaluation.md`,
`07_conclusion.md`, and the sentence-level contract for every section is `01_sentence_style.md`.

---

## 1. The reader test (the user's standard)

Imagine a first-time reader who does not know the design. Every sentence must be explainable to that reader with a concrete example; if
you cannot give the example, the sentence is under-specified — it names a thing it never defined, or compresses a causal chain the
reader has not seen. Two questions the user asked exposed the gaps in the region-table passage, three rounds after it was "done"
*(SPLEX example)*:

- **"What does 'GPUDirect RDMA's answer' mean?"** — the passage said "We adopt GPUDirect RDMA's answer for a NIC without a GPU page table:
  the driver pins the buffer and registers its physical location; the device computes addresses itself." The answer was never stated.
  Fix: "the driver pins the buffer and hands the device a list of the physical pages it occupies, and the device computes
  each address from that list as page index plus offset within the page."
- **"What is a region table / slot / stride / page list?"** — the earlier text ("three bases per (sequence, layer) … plus slot × stride
  suffice"; "contiguity collapses that list to three bases") used all four as if known. Fix: the page list is defined by the sentence
  above; the table is named so it cannot be confused with RDMA's ("The migration engine's region table (about 32 KB) holds three bases per
  (sequence, layer) -- keys, hot latents, cold latents -- and address = base + slot × stride: a pinned, contiguous region needs one base,
  not a page list.").

The test is applied per sentence, by the user, on the rendered page. Apply it yourself first.

## 2. Nine principles

### (a) Define, then elaborate
- **Rule**: the first sentence under a head defines the mechanism it names; validity, payoff, figure, implementation and cost follow
  (`05_design.md` §A).
- **Mistake** *(SPLEX example)*: the head *Key insight: rename, not map.* argued for renaming eight lines before re-indexing was defined; the
  paragraph opened with a preamble — "A two-tier memory normally records where each object currently lives, and every access must consult
  that record. SPLEX keeps no such record, because the KV cache has a property that ordinary data does not:".
- **After**: head **Re-indexing.**, first sentence "Re-indexing keeps the hot entries of layer ℓ at indices [0, N_ℓ) and the
  cold ones at [N_ℓ, L), so an entry's tier is one comparison of its index against N_ℓ and no per-entry location record exists."
- **Check**: under every run-in head, does sentence 1 contain the name and its definition, and nothing before it?

### (b) Order by the reader's need
- **Rule**: concept → policy detail → the whole mechanism start to end (work flow, with the timeline figure) → hardware → interface.
- **Mistake** *(SPLEX example)*: the hardware paragraph (*Migration engine*) came third, before the reader had seen a step run end to end; the
  interface was a separate fifth head. Order before the fix: Re-indexing · Policy and mechanism · Migration engine · GPU–engine interface · Work flow.
- **After** (two rounds): Re-indexing · Policy and mechanism · Work flow (ending "Figure 7 shows the step as a timeline.
  Two rules keep the swaps off the GPU's critical path: …") · Migration engine and its interface toward the GPU.
- **Check**: could a reader who stops after each head explain what has been defined so far without a term from a later head?

### (c) Walk the artifact, don't point at it
- **Rule**: a figure or algorithm is walked on its own entries and lines (the reference papers' "Walk-Through", "Line 1-2 introduces …").
- **Mistake** *(SPLEX example)*: "(Figure 6)" and "(Algorithm 1)" were pointers; the prose gave the abstract swap "of i ≥ N_ℓ with j < N_ℓ" and named
  the policy split in two slogans, "Counting and nominating are GPU software" / "Pairing under the budget and moving are the base die's".
- **After**: "Figure 6 shows it on six entries with N_ℓ = 3: before, the three hot entries sit wherever they were appended --
  B at index 1, D and F at 3 and 5, beyond the threshold in LPDDR; the engine swaps entry 0 with 3 and 2 with 5, …"; Algorithm 1 walked
  by rendered line — line 2 decay λ = 0.95 "so recent, repeated selections score high and stale ones fade", line 4 candidates "which
  filters the one-off fifth of each selection (§3.3)", line 5 victims "so no hit is evicted", line 6 on the GPU, lines 7–11 on the engine
  — with why each rule works, and the GPU/engine split stated per line instead of in the two slogans.
- **Check**: every figure index and every algorithm line the artifact prints appears in the prose that cites it, with its reason.

### (d) A component is its role
- **Rule**: name a hardware block by what it does in the mechanism, then its size; a size alone is a parts list.
- **Mistake** *(SPLEX example)*: the definition-first plan (`05_design.md` §I) ordered the engine head "the block and its SRAM (64 / 32 / 128 KB,
  424 KB, §6.1) → descriptor (16 B, an entry) → region table …" — sizes first, a parts list; the user asked what each part does in a swap.
- **After** (tightened in a later round): the ring is the GPU's path in and carries the candidate and victim lists — "The ring
  carries commands and completions only: the engine moves entries between its own two tiers, never into or out of GPU memory. A
  descriptor is 16 B and names an entry, not an address: (sequence, layer, step, id, score)."; "The doorbell wakes the control core,
  which runs the firmware (Algorithm 1, lines 7--11) from its own SRAM and keeps one budget counter per layer"; "The staging buffer
  (128 KB) holds one entry of a swap while its partner is written into the slot it left: … A→stage, B→A's slot, stage→B's slot"; then
  "Together these cost 424 KB of SRAM and one microcontroller (§6.1)."
- **Check**: for each component, is there a clause "<component> <verb> <what> in a swap" before or beside its size?

### (e) Our mechanism first, familiar precedent last, citations only
- **Rule**: explain our mechanism step by step; close with one sentence that names the systems that already use the arrangement, with
  citations and no explanation of those systems. A *specific* borrowed mechanism is cited where it is used (the page list, in the
  region-table paragraph), not in the closing list.
- **Mistake** *(SPLEX example)*: the interface head opened on the precedent — "The migration protocol is a queue pair over the path GPUDirect RDMA opens
  between a GPU and a peer device: …" — and the engine head opened "The engine is a descriptor-driven DMA block with an SSD/NIC-class
  control core"; the reader met NVMe/RDMA vocabulary before our ring, doorbell and completion word.
- **After** (two rounds): mechanism paragraphs first, then "The arrangement is the one NVMe SSDs and RDMA NICs already use -- a
  descriptor-driven DMA block with a control core behind submission queues, doorbells and completion queues [nvme2026base] or queue pairs
  and completion queues [ibta2007ibav1] -- driven by the device-initiated doorbell of GPUDirect Async [agostini2017gpudirectasync]."
  `nvidia2025gpudirect` moved out of that sentence to the region table, the one place its page list is used.
- **Check**: no precedent name before our mechanism's own steps; the closing sentence has cites and no clause explaining a precedent;
  each specific borrowed mechanism is cited at its use.

### (f) State the problem before the borrowed solution
- **Rule**: goal → why it is a problem → "we adopt X's answer" (cite) → our instance, named distinctly → the one rule → what stays fixed.
- **Mistake** *(SPLEX example)*: the region table appeared as a fact with its lineage after it — "The region table (about 32 KB) turns an entry's name into
  an address: the driver allocates a sequence's cache once, pinned and contiguous, and registers its bases at admission, so three bases …
  Pinned buffers registered up front are the pattern of GPUDirect RDMA's page list; contiguity collapses that list to three bases."
- **After**: "A swap must locate its new-hot and new-cold entries; descriptors carry only names. We adopt GPUDirect RDMA's
  answer for a NIC without a GPU page table [nvidia2025gpudirect]: … The migration engine's region table (about 32 KB) holds … A swap
  exchanges contents, never regions; the table is written once, at admission." — its own paragraph, words 89 → 89.
- **Check**: does the paragraph's first sentence state what we need and why the plain design cannot do it?

### (g) Claim only what exists
- **Rule**: every named interface, number and property traces to a design doc, a frozen evaluation view or a verified citation; each
  removal or correction carries its evidence.
- **Mistakes and fixes** *(SPLEX example)*: the invented calls `splexPinRegion` / `splexSetHotBudget` / `splexReadTelemetry` (v3 → 2026-09-04, defined
  nowhere) deleted; §4.3 rewritten on the syssw digest only. "about 620\,KB of SRAM in total plus one microcontroller (§5)" → "424\,KB of
  SRAM in total plus one microcontroller (§6.1)" — 620 KB was the PTE budget of the rejected hardware-page-table alternative
  (`v5_migration_engine_uarch.md`), the engine's SRAM is 128 + 64 + 64 + 32 + 128 + 8 KB. "a hot region sized per layer" (§1, §3.3, §4.1,
  §4.3, Algorithm 1's note) → "one hot-region fraction for every layer" — ramulator-owner verified that every evaluated placement used one
  f = f_avail. The §6.3 hit pair 0.867 / 0.831, printed without its cell, retired for Table 4's GLM-5.2 128K b = 128 pair 0.928 / 0.889,
  each cell carrying model, context + b, room + f_avail.
- **Check**: for every name, number and property in the diff, write the file and line it comes from; if there is none, it is `\TBD{}` or gone.

### (h) Cut redundancy and pedantry, not content
- **Rule**: delete what a caption, a table, a later section or the reader's own inference already holds; do not delete a fact to meet a
  length target — the 80 % target yields when comprehension needs words back (the reader-first round grew §4.2 1,030 → 1,219 words with
  the user's approval); the page budget is handled separately, by float moves and by the user.
- **Mistakes and fixes** *(SPLEX example)*: "-- while the GPU executes the remaining layers --" (Figure 7's caption says it) and "Figure 7 shows the
  resulting overlap" → "(Figure 7)"; the argued-down strawman "Counting at the memory controller instead would be redundant and blind:"
  and, later, "; a memory controller sees 32 B lines, not 656 B entries, and would need tens of megabytes of counters for a 64K-token
  batch across 61 layers" (the user cut it whole); "Critically, this means a hot entry can be physically moved to a different index …"
  folded into the validity sentence; "The only moment the engine has more work than a step can hide is round zero: when a sequence
  finishes prefill, its hot region must be seeded." → "Round zero is the seeding of a new sequence's hot region after prefill:"; §4.3's
  placement paragraph deleted because pinning is Table 1's and the region table is §4.2's.
- **Check**: for each cut, name where the content still lives (caption, table, section) or state that it was a strawman or a drum-roll.

### (i) Verify every pass mechanically
- **Rule**: a pass ships with its numbers: must-keep grep (one regex per fact of the plan), the numeric-token multiset of the section
  unchanged unless the plan names the change, per-head word counts before → after (with the counter named, not bare `wc -w`), the
  faithful build's page map and body end, and a row in the paper's reference-verification table for every new citation.
- **Mistake** *(SPLEX example)*: the definition-first round reported 199 / 191 / 379 with one counter and the next round read the same text as
  193 / 188 / 371 with another; a count without its counter is not comparable. The plan's draft for the region-table paragraph was 17
  words over the user's cap — caught only by counting.
- **Check**: the change map lists must-keep N/N, numeric multiset, per-head counts with the counter named, the build map, audit rows.

## 3. Sentence-level habits that repeatedly failed *(SPLEX examples throughout)*

- **Elaboration before definition** — "Critically, this means a hot entry can be physically moved to a different index -- exchanged with a
  cold one -- and, as long as the framework's index map records the exchange, every later access is bit-for-bit the same computation."
  came before the reader knew what an index was. Fix: definition sentence first, then "An entry moved to another index therefore yields
  the same computation, which §6.2 confirms on three models."
- **Abstract nouns without an example** — "contiguity collapses that list to three bases" (what list? collapses how?). Fix: "a pinned,
  contiguous region needs one base, not a page list", after the page list is defined.
- **Pronouns with two referents** — "The staging buffer (128 KB) holds an entry in flight while its partner is written over its slot"
  (the second "its" = the entry or the partner). Fix: "holds one entry of a swap while its partner is written into the slot it left".
  Likewise "the GPU stream … waits on it, which the front end resolves" → "waits on that word, and the front end resolves the wait".
- **Literary transitions** — "§3.2 left open *which* latent entries deserve the room HBM has left; the selections themselves settle it."
  → "The selections decide which latent entries deserve the room HBM has left (§3.2)."; "so a hotness score must *decay* on roughly that
  horizon -- an undecayed count never forgets." → "so the hotness score must decay over tens of steps; a plain count would keep old
  entries hot forever." (an aphorism the sentence guide once kept; the user cut it in §3.3 on 2026-09-06 — a fact stated plainly beats
  the same fact as a phrase).
- **Citation lists that hide which system supplied which idea** — "with pinned, contiguous buffers as in GPUDirect RDMA's page list
  [nvidia2025gpudirect] and the device-initiated doorbell of GPUDirect Async [agostini2017gpudirectasync]" attributed contiguity to a
  page list, which has none. Fix: one cite per mechanism at the mechanism (page list → region-table paragraph; doorbell → precedent
  sentence; queues → NVMe, queue pairs → InfiniBand — the IB text never prints "doorbell", so doorbells are NVMe's only).

## 4. Pre-commit checklist

1. Under every run-in head, sentence 1 = name + definition; no preamble, no argument before it.
2. Every cited figure and algorithm is walked on its own entries and lines, with the reason each rule works.
3. Every hardware component has its role in the mechanism stated beside its size.
4. No precedent name before our mechanism's steps; the precedent sentence is last, citations only, no explanation of the precedent.
5. Every borrowed mechanism: problem stated first, "we adopt X's answer" with the cite at the use, our instance named distinctly.
6. Every name, number and property in the diff traces to a file and line (design doc, frozen view, verified citation) — else `\TBD{}`.
7. Must-keep grep N/N; the placeholder macro (`\TBD`) 0; "?" 0; the paper's forbidden words (for SPLEX: "runtime" as a noun, `Critically`,
   `only moment`, `second effect that`) 0 in the design section — `grep -niE '<word1>|<word2>|…' <design section source>`.
8. Per-head word counts before → after with the counter named; no growth past the user's cap without the user's approval.
9. Faithful build: 0 undefined, 0 `[?]`, bibtex 0 errors; page map and body end reported; floats moved only by source position.
10. Every new citation has a row in the paper's reference-verification table with the verbatim quote that prints the claim.
