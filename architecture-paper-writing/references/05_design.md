# Design-section style guide — how the reference papers introduce a mechanism (governs §4)

Part of the architecture-paper-writing skill. Governs: the design section. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

Read in full (`pdftotext`, 2026-09-06, ligatures normalized): **[M]** Mesorasi (MICRO'20, Zhu) §IV Delayed-Aggregation Algorithm ≈ 1,010
words / §V Architectural Support ≈ 1,810 · **[TC]** Tensor Casting (HPCA'21, Rhu) §IV ≈ 2,700 · **[SS]** SmartSAGE (ISCA'22, Rhu) §4 ≈ 2,240 ·
**[PVF]** Low-Latency Proactive Continuous Vision (PACT'20, Zhu) §3 ≈ 1,250 / §4 ≈ 2,100 · **[LazyDP]** (ASPLOS'24, Rhu) §5 ≈ 2,220 ·
**[CAL]** Characterization of DL for 3D Point Cloud Analytics (IEEE CAL'21) has no design section and is excluded. This file governs §4
(Design) only; the abstract is `03_abstract.md`, §1 `04_introduction.md`, §5/§6 `06_methodology_evaluation.md`,
§8 `07_conclusion.md`, and the sentence-level contract for every section `01_sentence_style.md` (fact / number / forward
reference; no praise, no suspense, no question). Every rule carries a sentence quoted verbatim from a named paper; each quote was grepped in
the PDF text before it was printed here. **Read `08_design_section_lessons.md` with this file**: it records the mistakes the SPLEX §4 passes made
against these rules (2026-09-05 → 09-07) with the user's corrections quoted, the first-time-reader test, and a pre-commit checklist.

---

## A. The move order for a named mechanism (the one rule the five papers share)

**name → one-sentence definition (0–10 words after the name) → why it is valid → what it buys → figure / pseudo-code → implementation →
cost, once, with a forward pointer.** Nobody elaborates before defining. The eight instances, with the gap between the name and its
defining clause:

1. [M] §IV-A, 4 words: "The central idea is to delay aggregation until after feature computation so that features are extracted on
   individual input points rather than on aggregated neighbors." Then the payoff before the validity argument: "Delayed-aggregation has
   two benefits." — and only then, under the run-in head **Delayed-Aggregation**, "The key insight is that feature extraction (F) is
   approximately distributive over aggregation (A)." followed by Equ. 2 and its gloss "Fundamentally, Equ. 2 holds because the MLP in
   F is approximately distributive over subtraction in A."
2. [TC] §IV opener, 0 words: "At the heart of our proposal is our novel Tensor Casting algorithm which "casts" the gradient
   expand-coalesce primitive into a tensor gather-reduce operator." The coined term gets its abbreviation in the same paragraph:
   "Tensor casted (henceforth referred to as T.Casted)".
3. [TC] §IV-A, validity first, then the definition: "**Key observations.** An important observation behind our Tensor Casting algorithm
   is that coalescing gradients is functionally equivalent to conducting reductions among the target gradients." → "Figure 7 provides
   a high-level overview of the effect of Tensor Casting" → Algorithm 2 → **Implementation.** → **Merits.**
4. [SS] §4.1, the announced two-pass form: "takes a bottom-up approach" — the overview names direct I/O and I/O command coalescing
   under **Hardware.** / **Software.**, and §4.3 defines each under its own head ("**I/O command coalescing.** As detailed in
   Section 4.2, …"). Naming before defining is allowed only when the section says it is doing so.
5. [PVF] §3.1, 9 words: "The key idea of the predictive execution model is to allow the vision computation stage to operate
   speculatively on predicted future frames before the sensing and imaging stages generate the actual frames." Then "We illustrate
   the new predictive execution model in Fig. 4", then the two components: "First, the frame predictor predicts future frames to
   enable speculation."
6. [PVF] §3.3, the definition triple, one sentence per term: "Overall, there are three types of frames as Fig. 5 shows. Precise frames
   are frames that are generated from the sensor and ISP, and are used to predict future frames by the frame predictor."
7. [LazyDP] §5.1, the name inside its own definition with the correctness caveat in the same sentence: "An important observation
   behind LazyDP is that delaying the noise update process (which we refer to as lazy noise update) of DP-SGD can significantly
   improve computational efficiency while still ensuring that the privacy of final training outcome (i.e., the trained RecSys model)
   is not affected."
8. [LazyDP] §5.2.2, residual problem → name → 0-word definition → theorem → plain-English gloss: "We present our aggregated noise
   sampling (ANS) algorithm, which leverages the mathematical property of normally distributed random variables to substantially
   reduce the number of noise sampling." → Theorem 5.1 → "In effect, what this theorem implies is that we can replace the summation
   of multiple independently sampled Gaussian noise into a single Gaussian noise sampled from a normal distribution with a larger
   variance."

## B. Section anatomy

1. **A roadmap sentence opens the section** (47–143 words, forward pointers to every subsection): [PVF] "Sec. 4.2 will describe our
   offline-online collaboratively scheme"; [SS] "takes a bottom-up approach".
2. **Run-in bold heads carry the structure, ending with a period and running into the sentence**: [TC] **Key observations.** /
   **Implementation.** / **Merits.** / **Design principle.** / **Overhead.**; [SS] **Hardware.** / **Software.** / **Direct I/O.** /
   **I/O command coalescing.** / **NVMe compatibility and system integration.**; [PVF] one component per head — **Frame Predictor**,
   **Checking Logic**; [M] **Delayed-Aggregation**, **Walk-Through**, **Work Flow**. A head is the mechanism's name or the move's name,
   never a slogan; the key-idea sentence stands in roman under it.
3. **The key-idea sentence is roman prose, one per section**: [M] "The key insight is that feature extraction (F) is approximately
   distributive over aggregation (A)."; [SS] "Figure 10 illustrates the key intuition behind SmartSAGE ISP neighbor sampling
   operator."; [TC] "the key innovation of our proposal is the utilization of the expressive power of the tensor ga[ther-reduce]".
4. **Equation or pseudo-code, then a plain-English gloss that does the work**: [LazyDP] "In effect, what this theorem implies is that
   we can replace …"; [M] "Fundamentally, Equ. 2 holds because …".
5. **A "Consider …" worked example anchored on a figure**: [LazyDP] "Consider the embedding vector update that happens on the 4th
   iteration in Figure 7(c)."; [TC] "We use Figure 8 as a driving example"; [M] "Walk-Through We use the first module in PointNet++
   as an example to walk through the new algorithm."
6. **A correctness paragraph closes every speculative or approximate mechanism** (§C of the never-list): [SS] "fully compatible with
   existing CSD architectures"; [PVF] a whole §4.4 for mis-predictions; [LazyDP] the caveat in the definition sentence.
7. **Subsections close on one sentence of payoff or handoff**: [M] "This design optimization greatly reduces the area overhead
   (Sec. VII-A)."; [M] "We now describe the AU augmentation in NPU in detail."; [LazyDP] "In the following subsection, we detail the
   implementation of our lazy noise update and aggregated noise sampling algorithm."
8. **Optional 70–90-word "Putting everything together" closer**, naming one innovation and one figure and adding one new framing claim:
   [TC] §IV-D "Putting Everything Together"; [LazyDP] "Putting everything together," ending "It is important to note that ANS builds on
   top of LazyDP's ability to postpone noise sampling and noisy gradient update operations".

**One paragraph per agenda.** A mechanism introduction is two or three paragraphs — definition and
validity; the interface; cost and deadline — not one paragraph that runs all three together and not four
that split a single agenda. A paragraph break marks a change of agenda; if the agenda has not changed, the
break is noise. *(author feedback on the eval runs)*
**Say what a component does, not what it does not.** "The engine executes the policy's swap list" — never
"The engine never decides what to move; that decision is the policy's". A negated role ("never decides", "does
not choose") is written-language padding; the positive statement of each part's role carries the same
division of labour in fewer words. *(author feedback)*

## C. Arguing a choice: alternative, then reason, in 2–4 sentences

The alternative is real and usually cited, the reason is one property, and the paragraph stops. [M] "One might be tempted to reuse the
NPU's global buffer for the PFT buffer to save chip area. … However, physically sharing the two SRAM structures is difficult, mainly
because of their different design requirements."; [M] "One straightforward strategy is the row-major partitioning, where the PFT buffer
holds only a few rows of the PFT. … Instead, our design partitions the PFT column-wise"; [M] "Alternatively, an SoC could use a dedicated
neighbor search engine (NSE) [31], [59]. We use the GPU because it is prevalent in today's SoCs"; [LazyDP] "A naive implementation of the
HistoryTable will be to simply count the number of delayed noise updates each embedding vector is pending"; [PVF] "Unfortunately, this
optimization formulation is non-convex … Instead, we use a lightweight greedy algorithm that works well in practice."; [PVF] "we
empirically find that this simple mechanism performs well in practice". At most one bold-question head per section, reserved for the
single most contestable choice: [SS] "Why choose firmware-based (and not FPGA-based) CSDs for ISP?" (six sentences, the longest defense
in the corpus). A declined alternative is conceded, not attacked: [M] "We leave it to future work to explore this optimization".

## D. Costs stated in place, once, with a forward pointer

The paragraph that introduces a mechanism states its overhead — an absolute figure plus a ratio to something known, or a qualitative
clause with the pointer — and never a mini-evaluation. [M] "which could be as large as 0.75 MB in some networks (e.g., DGCNN). Since the
PFT buffer adds area overhead, we would like to minimize its size." → "We later quantify this resource vs. energy trade-off (Sec. VII-F)";
[TC] "**Overhead.** As we detail in Section VI, the overhead of copying the index array is negligible as its size is only in the order
of several MBs"; [PVF] "It takes about tens of microseconds to execute on a micro-controller"; [PVF] "As we will quantify in Sec. 6.8,
the mis-prediction penalty is low." Design parameters (0.75 MB, 81 M MACs, 32 ranks) are the only numbers a design section prints
besides one headline pointer.

**Unit first, then the system.** A cost or a cap is stated at the smallest unit it is defined on and carried to
the level the reader cares about in the same sentence — per swap → per sequence per layer per step → per stack —
so the arithmetic is on the page and a reviewer can check it. An evaluative adjective ("loose", "small") is
replaced by the two quantities it compares.

## E. Diction table (design sections only; counts per paper M / TC / SS / PVF / LazyDP)

| phrase | M | TC | SS | PVF | LazyDP | use in §4 |
|---|---|---|---|---|---|---|
| `i.e.,` / `e.g.,` | 4 / 4 | 7 / 2 | 3 / 7 | 6 / 7 | 4 / 5 | freely |
| `The key idea / insight / intuition / innovation is` | 1 | 2 | 1 | 1 | – | once per section |
| `An important observation … / key observation` | 1 | 2 | 1 | – | 4 | opens a validity move |
| `First, … Second, …` | 3 | 2 | 1 | 4 | 1 | payoffs and rules |
| `However,` / `Instead,` / `In contrast` | 4 / 1 / 2 | – | 1 / – / – | 5 / 2 / 1 | 5 / 1 / 1 | the alternative-then-reason turn |
| `we propose` / `our proposal` / `we present` | 1 | 2 / 7 | – | 5 | 3 / 2 | design acts only |
| `which we refer to as` / `henceforth referred to as` / `which we dub` | – | 1 | 1 | 1 | 1 | coin a term once |
| `Note that` / `Recall that` / `as discussed in Section N` | 2 / – / – | 1 / 1 / 3 | – / 1 / 2 | 2 / – / 1 | 2 / 1 / 1 | cross-reference, never restate |
| `Figure N illustrates / shows / provides` | 5 | 3 | 2 | 2 | 2 | figure second, claim first |
| `Consider …` / `For instance,` | – / 1 | – | – | 1 / 2 | 1 / – | the worked example |
| `Overall,` / `Consequently,` / `Thus,` | – / – / 4 | 1 / 3 / – | – / 1 / 2 | 3 / – / 1 | 1 / 1 / – | closers |
| `One might be tempted to` / `One straightforward strategy` / `A naive implementation` | 3 | – | 1 | 1 | 1 | the alternative |
| `More concretely,` / `Specifically,` | – / 1 | 1 / – | 1 / – | – / 1 | – / 1 | after the definition sentence |

## F. Tone

Definition-first, present tense, future only in forward pointers ("Sec. 4.2 will describe", "As we will quantify in Sec. 6.8" [PVF]).
"We" is used for design acts — "we propose", "we observe", "we use", "we empirically find", "we leave" — and passive voice for the
mechanism's behavior. Abstraction descends monotonically: idea → algorithm (equation or pseudo-code) → software → hardware structures →
per-structure decisions; [SS] inverts to hardware-then-software and says so ("takes a bottom-up approach"). Motivation is reached only
by pointer — [M] "As shown in Sec. IV-C, aggregation becomes a bottleneck"; [TC] "Recall that Tensor Casting can transform" — never
restated. Every subsection ends on a payoff or a handoff, never on a parameter. Sentence length: [M] and [PVF] ≈ 18–19 words, one idea
each; [TC] / [SS] / [LazyDP] ≈ 22–26 words with the justification folded into a "because / as / which" clause of the claim sentence.

## G. Compression habits (how a paragraph becomes a sentence)

1. **One definition sentence replaces a paragraph** — [PVF]'s three frame types are three sentences.
2. **Coin the term once** ("henceforth referred to as T.Casted" [TC], "aggregated noise sampling (ANS)" [LazyDP]) and never re-explain.
3. **Captions carry parameters**: [TC]'s Table I holds every memory parameter so no sentence lists them; [M]'s Fig. 14 caption holds the
   banking rationale and the body only names the structure.
4. **Pseudo-code carries the policy; prose names it by line**: [LazyDP] "Line 1-2 introduces the HistoryTable", "Line 3-5 introduces
   the InputQueue", "Line 6-27 explains the key operations undertaken during the main training loop."; [PVF] "Algorithm 1 describes
   the pseudo-code."
5. **One justification per choice, then stop** (§C: never more than ≈ 120 words).
6. **A workflow is one paragraph of prose** — [M] "Work Flow" packs the dataflow into six sentences — unless the steps map to circled
   figure markers, in which case it is an enumerated list ([SS] §4.2's (1)–(5)).
7. **Cost once, in place, with the pointer** (§D).
8. **Cross-reference instead of re-motivating** ("As detailed in Section 4.2" [SS]).
9. **Run-in heads are free structure**: [TC] fits nine topics into §IV without a numbered sub-subsection.
10. **Gloss the formalism immediately** ("In effect, what this theorem implies is" [LazyDP]) and let the gloss carry the argument.

## H. Never-list (0 occurrences in the five design sections)

Never elaborate before defining. Never re-motivate (the closest is "As shown in Sec. IV-C"). Never argue at length against a strawman —
rejected alternatives are real, cited designs and get 1–3 sentences. Never quote evaluation results beyond one headline pointer with its
section. Never hide a cost — every section states one overhead of its own proposal in the mechanism's paragraph ([M] devotes §IV-C to a
bottleneck its own algorithm creates). Never leave a correctness hole open. Never open a subsection with background — subsections open
with the definition, a key observation, or the residual problem of the previous subsection. Never hedge or self-congratulate in the body;
superlatives live only in the one key-idea sentence. Never a "Critically, this means" / "the only moment" / "a second effect that" preamble
before a fact — state the fact.

## Worked example (SPLEX, ASPLOS submission)

Mapping to the SPLEX §4.2 (*Migration Engine Design*, 2026-09-06) and the guards as run:

| run-in head (old → new) | reference move | first sentence = definition, then |
|---|---|---|
| *Key insight: rename, not map.* → **Re-indexing.** | A1, A7, B3, B6 | "Re-indexing keeps the hot entries of layer ℓ at indices [0, N_ℓ) …" → validity (attention is invariant to the order of the past; RoPE at insertion; the index map) → mechanism (the swap of i and j; Figure 6) → consequence pointer (§6.2 perplexity) |
| *Policy in software, mechanism in hardware.* → **Policy and mechanism.** | A5, C, D | "The placement policy (Algorithm 1) runs as GPU software up to the shortlist and as engine firmware from pairing on …" → why (the kernel already holds the top-2048 indices; the controller alternative in one sentence) → payoff with the numbers (25 swaps, 8 %, 0.951, < 0.5 %, §6.3) → what the base die does not hold |
| **Migration engine.** (unchanged) | A2, B4, D, G4 | the block and its SRAM (64 / 32 / 128 KB, 424 KB, §6.1) → descriptor (16 B, an entry) → region table defined before its GPUDirect lineage → swap path → compaction (285 → 390 GB/s) → two rules, each defined in its first clause → *round zero* defined in its first clause |
| *GPU–migration-engine interface.* → **GPU–engine interface.** | A2, B6 | "The migration protocol is a queue pair over the GPUDirect RDMA path …" → mechanics (fence + doorbell, one store per layer per step, completion word, no SM, AMD/ROCm) |
| **Work flow.** (unchanged) | B5, G6 | ①–⑦ keyed to Figure 5 as one paragraph; the closer = the one-step deadline with its pointer |

Guards as run on the SPLEX §4.2 before every commit: §4.2 prose ≤ 1,120 words, target ≈ 1,000 (`wc42.py`: floats, the algorithm and comments stripped,
macros removed, punctuation-only tokens dropped; report per head before / after) · the plan's must-keep list greps with the same value
(`mustkeep42.py`) · no new number · every `\ref` / `\cite` of the previous text present · the first sentence under every head defines the
mechanism it names · `Critically` / `only moment` / `second effect that` / `A two-tier memory normally` → 0 · `\TBD` 0 · "runtime" as a
noun 0 · "attention kernel" count unchanged (1 in §4.2) · Figure 6 / Algorithm 1 / Figure 7 / Table 2 sources untouched · the sentence
test of `01_sentence_style.md` on every sentence.

## Guard classes

Run on the design section's source before every commit; the SPLEX instantiation is the guard paragraph above.

- **Prose budget:** the section's prose stays within its word cap, measured by a counter that strips floats, the algorithm
  and its comments, macros and punctuation-only tokens, and reports per run-in head before / after.
- **Must-keep list:** every sentence on the plan's must-keep list greps with the same value.
- **No new number:** the pass introduces no number the previous text did not carry.
- **Cross-references:** every `\ref` / `\cite` of the previous text is present.
- **Definition first:** the first sentence under every run-in head defines the mechanism it names (§A).
- **Preambles:** every retired preamble phrase → 0 (§H: "Critically, this means", "the only moment", "a second effect that",
  and whatever the lessons file adds).
- **Placeholders and banned vocabulary:** every draft placeholder macro 0; every word on the paper's banned list 0.
- **Term counts:** the count of each reserved term is unchanged from the previous text.
- **Floats untouched:** the sources of the section's figures, algorithm and tables are untouched by a prose pass.
- **Sentence test:** `01_sentence_style.md` on every sentence.
