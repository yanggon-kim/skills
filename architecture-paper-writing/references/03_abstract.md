# Abstract style guide — the seven moves of the six reference abstracts

Part of the architecture-paper-writing skill. Governs: the abstract. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

Read in full (`pdftotext`, 2026-09-05): **[M]** Mesorasi (MICRO'20, Zhu) 196 words / 8 sentences ·
**[TC]** Tensor Casting (HPCA'21, Rhu) 128 / 6 · **[SS]** SmartSAGE (ISCA'22, Rhu) 230 / 8 · **[PVF]**
Low-Latency Proactive Continuous Vision (PACT'20, Zhu) 233 / 9 · **[LazyDP]** (ASPLOS'24, Rhu) 149 / 6 ·
**[CAL]** Characterization of DL for 3D Point Cloud Analytics (IEEE CAL'21, Rhu) 135 / 5. This file
governs the abstract only; the introduction's eight-move arc is `04_introduction.md` (the
abstract is that arc in miniature, A1–A7 there ↔ moves 1–7 here), and the sentence-level contract is
`01_sentence_style.md`. Every rule carries a sentence quoted verbatim from a named paper; where the
2026-09-05 plan's quote differed from the page, the page wins and the difference is noted.

Shape: 5–9 sentences, 128–233 words, one paragraph ([M] breaks it into two). Target: 170–200 words.

---

## A. The seven moves, in this order

**1. Domain sentence — wide, present tense, with the abstract's only mild pull.** The first sentence
names the field and why it matters now; it does not state the technical problem.
- [M] "Point cloud analytics is poised to become a key workload on battery-powered embedded and mobile
  platforms in a wide range of emerging application domains, such as autonomous driving, robotics, and
  augmented reality, where efficiency is paramount."
- [PVF] "Continuous vision is the cornerstone of a diverse range of intelligent applications found on
  emerging computing platforms such as autonomous machines and Augmented Reality glasses."
- [TC] "Personalized recommendations are one of the most widely deployed machine learning (ML) workload
  serviced from cloud datacenters." (the plan's "ML workloads" is a paraphrase; the page spells it out)
- [LazyDP] "Differential privacy (DP) is widely being employed in the industry as a practical standard
  for privacy protection."

**2. The gap or problem, signposted** (*Unfortunately / Despite / A critical issue*), stated as a fact
with its cause.
- [TC] "Unfortunately, little have been explored and understood regarding the training side of this
  emerging ML workload."
- [PVF] "A critical issue in today's continuous vision systems is their long end-to-end frame latency,
  which significantly impacts the system agility and user experience."
- [SS] "Despite its strengths, utilizing these algorithms in a production environment faces several
  challenges as the number of graph nodes and edges amount to several billions …"; then "Unfortunately,
  state-of-the-art ML frameworks employ an in-memory processing model which significantly hampers the
  productivity of ML practitioners as it mandates the overall working set to fit within DRAM capacity."

**3. "In this paper/work, we first … characterization …, root-causing X as …"** — the measurement and
its finding in one sentence, the finding often expanded by "Specifically,".
- [TC] "In this paper, we first perform a detailed workload characterization study on training
  recommendations, root-causing sparse embedding layer training as one of the most significant
  performance bottlenecks."
- [LazyDP] "In this work, we first present our detailed characterization of private RecSys training
  using DP-SGD, root-causing its several performance bottlenecks. Specifically, we identify DP-SGD's
  noise sampling and noisy gradient update stage to suffer from a severe compute and memory bandwidth
  limitation, respectively …"
- [PVF] "We find that the long latency is fundamentally caused by the serialized execution model of
  today's continuous vision pipeline, whose key stages … execute sequentially."
- [CAL] "In this paper, we conduct a detailed, end-to-end characterization on deep learning based
  point cloud analytics workload, root-causing the frontend data preparation stage as a significant
  performance limiter."

**4. "We then propose / Based on these findings, we propose NAME, a/an X co-design that …"** — the
system named once, with its one-line definition and the co-design split visible.
- [TC] "We then propose our algorithm-architecture co-design called Tensor Casting, which enables the
  development of a generic accelerator architecture for tensor gather-scatter …"
- [LazyDP] "Based on these findings, we propose LazyDP, an algorithm-software co-design that addresses
  the compute and memory challenges of training RecSys with DP-SGD."
- [SS] "We therefore develop SmartSAGE, our software/hardware co-design based on an in-storage
  processing (ISP) architecture." — reached through a second gap sentence: "Given the large performance
  gap between DRAM and SSD, however, blindly utilizing SSDs as a direct substitute for DRAM leads to
  significant performance loss."

**5. The key idea in one plain sentence**, optionally the two techniques in one more.
- [PVF] "Our key idea is a new proactive vision execution model that breaks the sequential execution of
  the vision pipeline. Specifically, we propose to allow the pipeline front-end (sensing and imaging) to
  predict future frames; the pipeline back-end (vision algorithms) then predictively operates on the
  future frames to reduce frame latency."
- [M] "Delayed-aggregation hides the performance bottlenecks and reduces the compute and memory
  redundancies by exploiting the approximately distributive property of key operations in point cloud
  algorithms."
- [PVF] "it enables multiple outstanding speculative frames by exploiting the hardware heterogeneities
  in mobile SoCs; it reduces the energy overhead of prediction by exploiting the error-resilient nature
  of vision algorithms."

**6. Results — baseline, condition, and the preserved property**, one cluster of numbers.
- [TC] "When prototyped on a real CPU-GPU system, Tensor Casting provides 1.9 − 21× improvements in
  training throughput compared to state-of-the-art approaches."
- [M] "Delayed-aggregation let point cloud algorithms achieve 1.6× speedup and 51.1% energy reduction
  on a mobile GPU while retaining the accuracy (-0.9% loss to 1.2% gains)."
- [PVF] "We show that PVF reduces the frame latency by up to 92% under the same energy."
- [LazyDP] "Compared to a state-of-the-art DP-SGD training system, we demonstrate that LazyDP provides
  an average 119× training throughput improvement while also ensuring mathematically equivalent,
  differentially private RecSys models to be trained."

**7. Optional close — the door it opens or the extra step.**
- [SS] "… opening up opportunities for ML practitioners to train large GNN datasets without being
  hampered by the physical limitations of main memory size."
- [M] "With additional hardware support, Mesorasi achieves up to 3.6× speedup."
- [CAL] "Through our findings, we discuss possible future directions to motivate continued research in
  this emerging application domain."

Order variants: [M] names the system in its second sentence ("This paper proposes Mesorasi, an
algorithm-architecture co-designed system that simultaneously improves …") before it characterizes;
[SS] runs move 2 twice and move 4 twice (SSDs, then SmartSAGE); [CAL], a characterization letter, has
no move 4–6. The moves themselves are common to all six, and none opens on the technical claim.

---

## B. Diction table (phrase → paper → our use)

| phrase | paper | use in the SPLEX abstract (example) |
|---|---|---|
| "is poised to become", "is the cornerstone of", "one of the most widely deployed" | [M], [PVF], [TC] | move 1: "LLM serving has moved to … and the KV cache dominates GPU memory" |
| "Unfortunately," | [TC], [SS] | move 2, on the host link |
| "In this paper/work, we first …, root-causing X as …" | [TC], [LazyDP], [CAL] | move 3 — "we first" dropped because "first" is spent on the tier ("root-causing placement as the limiter") |
| "Specifically," / "We find that" | [LazyDP], [PVF] | the colon after "limiter" carries the three findings |
| "Based on these findings, we propose NAME, a/an X co-design" | [LazyDP] | move 4, verbatim frame: "a hardware–software co-design in which …" |
| "We then propose our algorithm-architecture co-design called" | [TC] | not used (one proposal sentence) |
| "Our key idea is" | [PVF] | move 5, as a plain declarative ("Hot entries are re-indexed …") |
| "Compared to", "compared to state-of-the-art approaches" | [LazyDP], [TC] | move 6 opener: "Compared to PCIe and NVLink-C2C offload" |
| "while retaining / while also ensuring" | [M], [LazyDP] | "within 0.1 % of an infinite-HBM oracle" |
| "we demonstrate / we show that" | [LazyDP], [PVF] | not needed — the result sentence is declarative |
| "opening up opportunities" | [SS] | the close, if space allows (dropped at 200 words) |
| "state-of-the-art" | [TC], [SS], [LazyDP] | not used; baselines are named (PCIe, NVLink-C2C, HBM-only) |

## C. Tone

Present tense, confident declaratives, one paragraph. The system name appears once with its
definition ("LazyDP, an algorithm-software co-design that addresses …"); every later mention is "it"
or the name, never a synonym. No rhetorical question, no metaphor, no symbol the reader has not met
— none of the six prints a variable. Numbers arrive in one cluster at the end, each with its baseline
and unit ("1.9 − 21× … compared to state-of-the-art approaches"; "up to 92% under the same energy");
move 3 may hold a small cluster of characterization numbers when the paper's findings are numeric
(SPLEX: 89 % / 0.79 / 13 %). The mild pull lives in the domain sentence ("poised", "cornerstone") and
the close ("opening up") and nowhere else; the middle is flat and factual. Signposts ("Unfortunately",
"Specifically", "Based on these findings", "Compared to") open sentences, one per sentence at most.

## Worked example (SPLEX, ASPLOS submission)

Mapping to the SPLEX abstract (2026-09-05):

| move | SPLEX sentence (opening words) | facts, each a copy of §3 / §6 |
|---|---|---|
| 1 | "LLM serving has moved to long contexts, agentic use, and large batches, and the KV cache dominates GPU memory." | §1 ¶1 |
| 2 | "Unfortunately, prior systems offload it over a fixed, shared host link." | §1 ¶2 |
| 2′ | "Meanwhile, DeepSeek Sparse Attention (DSA) selects a small set of entries per step, and custom HBM's base die can carry 1.1 TB of LPDDR per GPU." | §1 ¶3–¶4, 1.1 TB (§6.3) |
| 3 | "We characterize DSA's selections and the two-tier gather, root-causing placement as the limiter: …" | 10 % → 89 % (§3.3), 0.79 (§3.3), 13 % below the optimum (§3.2) |
| 4 | "Based on these findings, we propose SPLEX, the first KV-cache tier on custom HBM with an LPDDR extension: a hardware–software co-design in which a selection-driven placement policy decides …, a base-die migration engine enforces … asynchronously under a fixed swap budget, and the serving framework commits them." | the three-role split (§4.1, §4.2); "first" once |
| 5 | "Hot entries are re-indexed to the low indices of each layer's cache; tier steering is one comparison." | §4.2 |
| 6 | "On eight GPUs SPLEX lowers TPOT 7.8–21.2× against PCIe offload, within 0.1 % of an infinite-HBM oracle at every cell but one; six SPLEX GPUs deliver 1.52–2.79× the HBM-only eight-GPU node's peak throughput at 0.79× the energy per token." *(the submitted wording; an earlier draft compared against a second host link and quoted 128K figures)* | §6.2, §6.3 |
| 7 | dropped for length (candidate: "GPU-only long-context serving scales with the stack count rather than the host link", §1 ¶4) | — |

Guards as run on the SPLEX abstract before every commit:

`\TBD` 0 · "cross-layer" 0 · "runtime" as a noun 0 · "first" exactly once · no `$h`, `f_avail`, `B =`,
`k`, `\times` outside a result · no "?" · no "we believe", "novel", "significantly" without a number ·
170–200 words (counter: macros and cites stripped, punctuation-only tokens dropped) · every number
greps in `sections/03-motivation.tex` or `06-evaluation.tex` with the same value · the `\keywords`
line untouched · vocabulary: the policy decides, the base-die engine enforces / moves, the serving
framework commits (never "the runtime decides"; "hardware–software", never "cross-layer", because
"layer" is a decoder layer everywhere in the paper).

## Guard classes

Run on the abstract's source before every commit; the SPLEX instantiation is the guard line above.

- **Placeholders:** every draft placeholder macro (`\TBD` or its equivalent) 0.
- **Banned vocabulary:** every word on the paper's banned list 0, and every agent named by its fixed verb from the
  paper's role list (never a synonym for a role; never a word that collides with a term the paper uses elsewhere).
- **Priority claim:** "first" exactly once.
- **Symbols and questions:** no variable the reader has not met (no `$h`, `f_avail`, `B =`, `k`, `\times` outside a result); no "?".
- **Hedges and unquantified praise:** no "we believe", "novel", "significantly" without a number.
- **Length:** within the target band (counter: macros and cites stripped, punctuation-only tokens dropped).
- **Numbers:** grep every number in the abstract against the motivation and evaluation sections' source; the same value must appear.
- **Metadata:** the `\keywords` line untouched.
- **Negated alternatives.** Grep the abstract for " not " / "rather than" / "instead of": a negation that names
  a quantity the reader has not met (a wire rate, a baseline's mechanism) is cut to the positive finding; the
  alternative is introduced in the motivation, where it can be argued. **The problem move is present** — one
  sentence says what the paper solves before the substrate or the system appears.
- **The opening names the problem the paper solves, not the technique prior work uses.** An abstract that
  opens on "sparse attention" when the paper solves the KV-cache capacity wall has led with the context
  of the rivals; sparse attention enters as the setting the prior approaches assume. *(author feedback)*
- **Every move is joined to the one before it.** "Unfortunately, …" carries the problem move well; the
  substrate/insight move that follows must connect to it ("A new substrate removes the link: …", "Custom
  HBM changes this: …"), not open cold on a new noun. A move that reads as an abrupt topic switch is a move
  without its connective. *(author feedback)*

## Move order, as the author corrected it (later word over §A where they differ)

The abstract opens on the problem the paper solves, in its setting (the KV cache outgrowing GPU memory in
long-context serving; offload bottlenecked by the host link). The **substrate may follow at once, but only as
"an alternative"** — one sentence saying what it offers — and it must be followed immediately by the
*requirement* it creates (exploiting that bandwidth means placing the right entries in scarce HBM), which is
what leads to the system. The system is then named in one sentence. **Sparse attention is introduced by the
characterization sentence** — naming the mechanism and the models, then the numbers — before any later
sentence leans on it; a phrase like "the sparse-attention gather's delivered bandwidth" dropped in before
that introduction is what the author called abrupt: the reader meets a modifier for a thing not yet
defined. Then the mechanism in two sentences, the method in one, the results, the significance.

What was wrong in the rejected draft: the substrate sentence was followed by a §3 *finding* ("placement
between the tiers sets the delivered bandwidth") instead of the requirement it creates, and sparse attention
appeared as a modifier before the characterization sentence introduced it. The KV-cache wall and sparse
attention are logically joined — the prior offload approaches are built on sparse attention — so the path
from the problem to the characterization must pass through that introduction, and the LPDDR extension
belongs on the solution side of the abstract, as the alternative that the system exploits.

The submitted abstract that follows this order, sentence by sentence *(SPLEX example)*:

1. As long-context, high-batch LLM serving pushes the KV cache beyond GPU memory capacity, existing offloading systems are bottlenecked by host-interconnect bandwidth.
2. Emerging custom HBM offers an alternative: its logic base die can attach each HBM stack to a stack-local LPDDR capacity tier whose aggregate bandwidth scales with the number of stacks.
3. Exploiting that bandwidth, however, requires placing the right KV entries in scarce HBM.
4. We present SPLEX, a hardware–software co-design for selection-driven KV-cache tiering on LPDDR-extended custom HBM.
5. Characterizing DeepSeek Sparse Attention over long-context decodes of DeepSeek-V3.2, GLM-5, and GLM-5.2, we find selections to be highly concentrated and persistent: on DeepSeek-V3.2, the hottest 10% of entries serve 89% of all selections, and an entry selected at one step is still selected with probability 0.64 after 64 steps and 0.35 after 1{,}024 steps.
6. SPLEX exploits this structure by maintaining a compact hot region in HBM: a GPU-side policy identifies repeatedly selected entries, and a base-die migration engine asynchronously swaps them with cold entries under a fixed traffic budget.
7. Re-indexing keeps hot entries at low cache indices, so tier selection reduces to a single range comparison and HBM row locality improves without adding per-entry translation to the load path.
8. Combining measured selection traces and GPU kernel profiles with cycle-level memory simulation, we evaluate SPLEX on DeepSeek-V3.2, GLM-5, and GLM-5.2.
9. SPLEX is $7.8$–$21.2\times$ faster than PCIe offload in time per output token, and approaches an infinite-HBM oracle whenever weights and indexer keys fit in HBM.
10. These results show that the structure of sparse-attention selections can turn stack-local capacity memory into an effective high-bandwidth tier for the KV cache.
