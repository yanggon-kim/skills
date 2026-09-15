Part of the architecture-paper-writing skill. Governs: the conclusion. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

# Conclusion style guide — the five moves of the six reference conclusions

Read in full (`pdftotext`, 2026-09-05): **[M]** Mesorasi (MICRO'20, Zhu) §IX, 78 words / 5 sentences ·
**[TC]** Tensor Casting (HPCA'21, Rhu) §VII, 108 / 5 · **[SS]** SmartSAGE (ISCA'22, Rhu) 81 / 3 · **[PVF]**
Low-Latency Proactive Continuous Vision (PACT'20, Zhu) 81 / 5 · **[LazyDP]** (ASPLOS'24, Rhu) 71 / 3 ·
**[CAL]** Characterization of DL for 3D Point Cloud Analytics (IEEE CAL'21, Rhu) §6 "Conclussion" [sic],
115 / 4, preceded by a §5 *Future Directions* of 178 words — the letter's device, not a design paper's
(see move 5). This file governs the conclusion (§8 in the layout below) only: the abstract's seven moves are `03_abstract.md`, the
introduction's eight-move arc `04_introduction.md` (§8 is the abstract's arc replayed after the
evidence: claim, key idea, what was done, one number, outlook), the sentence-level contract
`01_sentence_style.md`. Every rule carries a sentence quoted verbatim from a named paper; where the
2026-09-05 plan's reading differed from the page, the page wins and the difference is noted.

Shape: 3–5 sentences, 71–115 words, one paragraph; no citation, no section reference, no symbol; at most
one number cluster ([TC] "1.9 − 21×" — the other five print none). House target: 90–110 words.

---

## A. The five moves, in this order

**1. Opening — the domain with its outlook, or "This paper proposes NAME, a/an X co-design that …".**
- [M] "With the explosion of 3D sensing devices (e.g., LiDAR, stereo cameras), point cloud algorithms
  present exciting opportunities to transform the perception ability of future intelligent machines."
- [PVF] "Long frame latency is detrimental to real-time vision systems."
- [LazyDP] "This paper proposes LazyDP, our algorithm-software co-design that provides scalable and
  high-performance private RecSys training."
- [TC] "This paper proposes Tensor Casting, an algorithm-architecture co-design for training
  recommendation models."
- [SS] "In this work, we investigate the viability of utilizing NVMe SSDs to overcome the memory capacity
  limitations of current, in-memory processing GNN training systems."

**2. The claim of the paper in one sentence** — what it argues or what is unique about it.
- [M] "Mesorasi takes a systematic step toward efficient point cloud processing."
- [PVF] "This paper argues that the sequential execution model is the culprit of the long latency."
- [TC] "Unlike recent prior literature focusing on the inference part of this emerging ML workload, the
  unique contribution of our study is the exploration of this application on the training side of things."
- [TC] closes on the "first" claim, scoped: "To the best of our knowledge, Tensor Casting is the first
  that quantitatively explores architectural solutions tailored for training recommendation models." —
  the precedent for one "first" in a conclusion (not in the plan's reading; ours puts it in the claim
  sentence, scoped to the organization, the substrate credited to the vendors in the same sentence).

**3. "The key to NAME is …" — the idea in one plain sentence**, its mechanism after a verb, no symbol.
- [M] "The key to Mesorasi is the delayed-aggregation primitive that decouples neighbor search with
  feature computation and significantly reduces the overall workload."
- [PVF] "The key to PVF is to break the sequential execution between vision front-end and back-end."
- [SS] and [LazyDP] have no key sentence; their mechanism rides in move 4 ("via our lazy noise update and
  aggregated noise sampling optimizations").

**4. What was done, in the paper's order — "We first …, we then …" — with the one number.** Present
tense on every page, also for the work already done (the plan's "past or present perfect" is corrected).
- [TC] "We first provide a detailed, quantitative analysis on training recommendation models,
  root-causing several system-level bottlenecks such as gradient expand-coalesce. We then implement and
  demonstrate the benefits of Tensor Casting on real systems, showing that Tensor Casting achieves
  1.9 − 21× speedup than state-of-the-art approaches."
- [LazyDP] "We first characterize real world RecSys models and uncover several critical performance
  bottlenecks such as the compute-limited noise sampling and memory-limited noisy gradient update
  operations. LazyDP successfully addresses these two bottlenecks via our lazy noise update and
  aggregated noise sampling optimizations, providing substantial performance speedup while ensuring
  mathematically equivalent, differentially private RecSys models to be trained."
- [SS] "By intelligently offloading the data intensive frontend data preparation stage of GNN training,
  SmartSAGE significantly resolves the bottlenecks of the baseline SSD-centric training system,
  achieving significant performance improvements."
- [PVF] "We present an efficient implementation of PVF by leveraging the heterogeneities in mobile SoCs
  and exploiting the error-tolerance nature of vision applications."

**5. Outlook — the potential beyond this paper, one sentence, the only future tense.**
- [M] "Hardware support maximizes the effectiveness of delayed-aggregation. The potential gain is even
  greater in future SoCs where neighbor search is accelerated."
- [SS] closes its abstract, not its conclusion, on "opening up opportunities for ML practitioners to
  train large GNN datasets without being hampered by the physical limitations of main memory size."
- [CAL] "Future work is to develop accelerated computing solutions for end-to-end point cloud analytics
  using a near-memory processing based solution that best utilizes the key findings of our study." Its
  §5 *Future Directions* ("One promising future direction of this work is to explore the efficacy of
  near-memory processing (NMP) solutions …"; "We leave the development of accelerated computing solutions
  for data preparation as future work.") is a characterization letter's close. A design paper states the
  potential its own facts support — [M]'s form — never a future-work list (the user declined a §8
  future-work clause, 2026-09-05).

Order variants: [PVF] proposes (1) before the key (3) and ends on the implementation (4); [M] runs the
outlook twice; [TC] ends on the claim (2, "first"); [SS] and [LazyDP] have no move 3 and no number;
[CAL] has no move 3. The moves are common to all six, and none ends on a citation or a section reference.

---

## B. Diction table (phrase → paper → house use in the conclusion; the third column's examples are SPLEX's)

| phrase | paper | our use |
|---|---|---|
| "This paper proposes NAME, a/an X co-design" | [LazyDP], [TC] | not the opener — ours opens on the substrate (move 1, [M]/[PVF] form) |
| "This paper argues that", "the unique contribution of our study is" | [PVF], [TC] | move 2 as a declarative: "**SPLEX** is the first to organize that vendor substrate into a KV-cache tier" |
| "To the best of our knowledge, NAME is the first that" | [TC] | "first" once, no "to the best of our knowledge" |
| "takes a systematic step toward" | [M] | not used (praise without a fact — `01_sentence_style.md` §2) |
| "The key to NAME is" | [M], [PVF] | verbatim frame, move 3 |
| "We first …, We then …" | [TC], [LazyDP] | "We characterize … and build the tier on them" — no "we first", "first" is spent on the claim |
| "showing that NAME achieves 1.9 − 21× speedup than state-of-the-art approaches" | [TC] | "lowers TPOT up to 21.2× against host offload" — the baseline named |
| "while ensuring mathematically equivalent" | [LazyDP] | "within 0.1 % of an infinite-HBM oracle" |
| "significantly / substantial / successfully / intelligently" | [M], [SS], [LazyDP] | not used; the number stands where the adverb would |
| "The potential gain is even greater in future SoCs where" | [M] | move 5 as a fact of the substrate: "Capacity and bandwidth grow with the stack count, not the host link" |
| "opening up opportunities for" | [SS] (abstract) | "open to other placements" |
| "Future work is to …", "We leave … as future work" | [CAL] | not used |

## C. Tone

Present tense throughout — the claim, the key, and the work done ("We first characterize", "We then
implement and demonstrate"); the outlook alone may look forward ("The potential gain is even greater
in future SoCs"). One paragraph, flat and factual: no new fact, no citation, no section reference, no
symbol, no question. The one mild pull sits in the opening ("exciting opportunities") or the outlook
and nowhere else. The system's name recurs as itself (Mesorasi ×2, PVF ×3, Tensor Casting ×4, LazyDP
×2, SmartSAGE ×2), never as a synonym. The number, if any, arrives with its baseline in the
what-was-done sentence, never as the opener. Nothing is restated from the abstract word for word: [M]'s
abstract says delayed-aggregation "exploit[s] the approximately distributive property", its conclusion
that it "decouples neighbor search with feature computation" — the same idea in different words, and
§8 says the tier in words the abstract and §1 ¶6 did not use.

## D. Worked example (SPLEX, ASPLOS submission)

Mapping of the SPLEX §8 (`sections/08-conclusion.tex`, 2026-09-05) onto the five moves.

| move | our sentence (opening words) | facts, each a copy of §2–§4 / §6 |
|---|---|---|
| 1 + 2 | "Custom HBM arrives with LPDDR behind every stack; **SPLEX** is the first to organize that vendor substrate into a KV-cache tier." (user: open on the rise of custom HBM) | §2.4 (LPDDR behind the base die), Figure 5's caption ("everything else is the vendor substrate"); "first" once |
| 3 | "The key to **SPLEX** is that sparse attention exposes the statistics placement needs: hot entries are re-indexed to each layer's low indices, and a base-die engine keeps them there under a fixed swap budget." | §3.3, §4.2 (re-index, engine, budget) |
| 4 | "We characterize how DeepSeek-V3.2's selections persist and concentrate over a decode and build the tier on them." (user: describe our own characterization, not others' limit "beyond lag 1"; **no result clause — the user removed "up to 21.2× … within 0.1 %": no specific result in the conclusion**, unlike [TC]) | §3.3 prints V3.2 only (the three models sit in §6) |
| 5 | "As custom HBM matures, every stack a GPU adds brings its own extension, and **SPLEX** opens that memory-side expansion as new design territory." (the user's sentence) | §3.1 / §4.1 ("far-tier capacity and bandwidth grow with the number of stacks") |

The SPLEX guards, as run on `sections/08-conclusion.tex` before every commit: `\TBD` 0 · "first" exactly once · `\cite` 0 · `\ref` 0 ·
no result number (user, 2026-09-05: the results stay in §6 and the abstract) · 85–115 words (counter: macros and cites stripped,
punctuation-only tokens dropped) · no "novel", "significantly", "substantial", "successfully", "to the best of our knowledge", "future
work" · no "cross-layer", no "runtime" as a noun · no "?" · no symbol ($h$, $f_{\mathrm{avail}}$, $B$, $k$) · every number greps in
`sections/06-evaluation.tex` with the same value · the outlook sentence claims nothing §3/§4/§6 do not print · vocabulary per the
paper's role list (the kernel nominates, the base-die engine decides and moves, the serving framework commits; "hardware–software",
never "cross-layer") · the sentence test of `01_sentence_style.md` on every sentence.

## E. Guard classes (run on the conclusion source before every commit)

1. **Placeholders** — the placeholder macro (`\TBD` or the paper's equivalent) → 0.
2. **"first" exactly once**, and no "to the best of our knowledge" beside it.
3. **No citations, no section references** — `\cite` 0, `\ref` 0.
4. **Result numbers** — either none (the house decision: results stay in §Eval and the abstract) or at most one cluster, with its baseline
   named; every number that does appear greps in the evaluation section with the same value.
5. **Word band with the counter named** — macros and cites stripped, punctuation-only tokens dropped.
6. **Banned words** — "novel", "significantly", "substantial", "successfully", "to the best of our knowledge", "future work", and the
   paper's own forbidden terms → 0.
7. **No question mark, no symbol** — no "?" and no math-mode symbol in the paragraph.
8. **The outlook claims nothing the body does not print** — every clause of move 5 traces to a section that states it as a fact.
9. **Vocabulary per the paper's role list** — the same agent does the same verb in the conclusion as in the design section.
10. **The sentence test** of `01_sentence_style.md` on every sentence.
