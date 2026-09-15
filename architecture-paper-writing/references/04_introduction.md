# Introduction style guide — the arc and the sentences of the six reference papers

Part of the architecture-paper-writing skill. Governs: the introduction (and the abstract's arc). Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

Read in full (`pdftotext`, 2026-09-05): **[M]** Mesorasi (MICRO'20, Zhu) · **[TC]** Tensor Casting
(HPCA'21, Rhu) · **[SS]** SmartSAGE (ISCA'22, Rhu) · **[PVF]** Low-Latency Proactive Continuous Vision
(PACT'20, Zhu) · **[LazyDP]** (ASPLOS'24, Rhu) · **[CAL]** Characterization of DL for 3D Point Cloud
Analytics (IEEE CAL'21, Rhu). This file governs §1 and the abstract only. The sentence-level contract
(what to delete, the merge pattern) is `01_sentence_style.md`; structure, figures and the §3–§6
lessons are `02_paper_structure_and_figures.md` — neither is repeated here. Every rule below carries a sentence quoted
verbatim from a named paper; where the 2026-09-05 plan's quote differed from the page, the page wins
and the correction is noted.

Length: the introductions run [M] 698 · [TC] 880 · [SS] 1,462 · [PVF] 1,039 · [LazyDP] ≈ 800 words;
[CAL], a four-page letter, 341. Target: ≤ 900 words including contributions (page budget 1.3 pages with
the overview figure).

---

## A. The arc — eight moves, in this order

**A1. Landscape opening.** The first paragraph starts with the domain, its growth, and named
deployments, then the property that matters; it does not state the technical problem.
- [M] "In recent years, we have seen the explosive rise of intelligent machines that operate on point
  clouds … For instance, Waymo's self-driving cars carry five LiDAR sensors … Augmented Reality (AR)
  development frameworks such as Google's ARCore enable processing point clouds for localization."
- [CAL] "Recently, we are witnessing an explosive adoption of point clouds … in numerous application
  domains such as autonomous driving, AR/VR, and graphics rendering."
- [SS] "GNNs have found significant success in the areas of e-commerce and advertisement … For
  instance, Pinterest's PinSAGE or Alibaba's AliGraph leverages GNNs to analyze … billions of
  user/item feature embeddings."
- [TC] "The enormous compute power machine learning (ML) accelerators … deliver allows practitioners
  to develop sophisticated and powerful deep neural network (DNN) algorithms … NVIDIA's Tensor Core,
  Google's TPU, Habana's Gaudi, Graphcore's IPU, and Cerebra's CS-1."
- [LazyDP] "With recent advances in deep neural networks (DNNs), hyperscalers leverage DNN-based
  recommender systems (RecSys) to power their ads recommendation service."
- [PVF] opens one level wider — "Domain specific architectures (DSA) provide more compute capability
  with lower energy consumption under the same silicon budget" — and narrows to "This paper focuses on
  the domain of continuous vision" within the same paragraph.
- SPLEX example: long contexts, agentic use, large batches — the named models and serving frameworks, then the
  KV cache as the property that matters.

**A2. The problem, stated as a fact with its cause**, in a sentence that opens with a signpost
(*Unfortunately / However / Critically / Despite*) or with the subject itself.
- [PVF] "Today's continuous vision system is bottlenecked by its long frame latency, which is
  fundamentally caused by its serialized execution model."
- [SS] "Unfortunately, current ML frameworks' in-memory processing model forces ML practitioners to
  tune the GNN training algorithm to fit within the several tens to hundreds of GBs of CPU memory."
- [CAL] "Despite the powerful and rich modality point cloud presents, the compute and memory access
  pattern of end-to-end point cloud analytics are fundamentally different than conventional [CNNs].
  Critically, unlike CNNs … point cloud analytics contain a diverse class of operators exhibiting
  highly sparse and irregular dataflow."
- [LazyDP] "The widespread adoption of RecSys, however, is raising serious concerns on protecting the
  privacy of users."

**A3. State of practice and its limit, with a number.** Prior systems are described by what they do,
in their own terms; the limit follows, quantified against a named baseline.
- [SS] "These data structures are mapped to user-space memory address via memory-mapped (mmap) file
  I/O, which allows the most recently accessed pages to be buffered inside the OS managed page cache
  … Unfortunately, our baseline SSD-centric training system is shown to benefit little from the
  locality-optimized OS page cache, … an average 9.8× slowdown vs. an oracular, in-memory processing
  based system."
- [PVF] "Many existing system optimizations such as pipelining and batching are designed to improve
  throughput (i.e., frame rate), but further exacerbate the frame latency." — the plan's quote dropped
  "(i.e., frame rate)". The number follows one paragraph later: "a typical embedded robot today has a
  200 ms responsive latency from event to command, in which 100 ms is attributed to the vision
  sub-system."
- [LazyDP] "These studies, however, primarily focused on computer vision or natural language
  processing, so there is a dearth of prior work providing a systematic evaluation of DP-SGD's
  computational challenges for RecSys."
- [CAL] states its predecessor's limit in §2.2, not §1: "While Mesorasi successfully addresses both …
  it overlooks the importance of the data preparation stage."

**A4. The paper's goal and proposal, named early, in one sentence.** "To this end, this paper …" is
the reference form; the system name appears here or one paragraph later.
- [SS] "To this end, this paper explores the feasibility of utilizing NAND flash-based non-volatile
  memory (NVM) solutions to address the memory 'capacity' bottlenecks of large-scale GNN training."
- [CAL] "To this end, the key objective of this study is to provide a detailed, end-to-end
  characterization on point cloud analytics, root-causing several crucial performance bottlenecks."
- [PVF] "This paper seeks to reduce the end-to-end latency of continuous vision tasks. Our key idea is
  to break the sequential execution chain."
- [M] names the system in its second paragraph, before the characterization: "We present Mesorasi,
  an algorithm-architecture co-designed system that simultaneously improves the performance and energy
  efficiency of point cloud algorithms without hurting the accuracy."
- [TC] / [LazyDP] "an important motivation and key contribution of our study is a detailed analysis
  and characterization of the training process of DNN-based recommendations."

**A5. Characterize → key observation.** The measurement is announced, then its finding, often as a
numbered pair.
- [M] "We start by understanding the characteristics of point cloud algorithms. … This leads to two
  fundamental inefficiencies. First, the three key steps … are serialized, leading to long critical
  path latency. … Second, feature computation operates on aggregated neighbor points, which are
  inherently redundant."
- [SS] "Our characterization reveals that GNN training's frontend input data preparation stage
  (Figure 1) is the most memory capacity intensive"; "reveals the following key observation: because
  data preparation exhibits fine-grained irregular parallelism, it becomes challenging for the page
  cache to reap locality benefits."
- [LazyDP] "Our characterization uncovers the following two critical system-level challenges of
  DP-SGD's noisy gradient update operation (Section 4.3)."

**A6. Proposal: the key idea in plain words, then the deployment boundary.**
- [M] "We propose delayed-aggregation, a new algorithmic primitive for building efficient point cloud
  networks. The key idea is to delay aggregation after feature computation by exploiting the
  approximately distributive property of feature computation over aggregation." Boundary: "Our
  hardware extensions are integrated into generic DNN accelerators without affecting the rest of a
  mobile Systems-on-a-Chip (SoC)."
- [TC] "Tensor Casting utilizes the current software stack as-is so another key advantage of our
  proposal is that it can be implemented purely in software."
- [PVF] "PVF extends today's mobile SoC only minimally."
- [LazyDP] "our proposal 'delays' the noise update process for the embeddings at a given training
  iteration" — one mechanism sentence per bullet, the section number in parentheses.

**A7. Headline results with the baseline named.** Ranges, the comparison, the cost.
- [M] "the delayed-aggregation algorithm alone without hardware support achieves 1.6× speedup and
  51.1% energy reduction while retaining the accuracy (-0.9% loss to 1.2% gains). … With 3.8% area
  overhead to the NPU (<0.05% of a typical SoC area), Mesorasi achieves up to 3.6× speedup."
- [PVF] "PVF is able to achieve up to 92% latency reduction under the same energy budget, or 60.3%
  energy reduction at same frame latency, all with negligible accuracy loss."
- [LazyDP] "Overall, LazyDP provides an average 119× training speedup over representative RecSys
  models while guaranteeing mathematically equivalent, differentially private RecSys models to be
  trained vs. baseline DP-SGD."
- [SS] "an average 3.5× (max 5.0×) vs. the baseline SSD-centric system"; [TC] "1.9 − 21× speedup when
  compared against the baseline CPU-centric systems."

**A8. Contributions.** "In summary, this paper makes the following contributions:" then three or
four bullets, each opening with a verb, one to three sentences.
- [M] "In summary, this paper makes the following contributions: • We comprehensively characterize
  the performance bottlenecks … • We propose delayed-aggregation … • We co-design hardware …"
- [PVF] "In summary, this paper makes four contributions: • We propose the proactive continuous vision
  execution model that predicts the vision front-end to reduce the end-to-end frame latency." (the
  plan's "the following contributions" is [M]'s wording, not [PVF]'s).
- [SS] "To summarize our key contributions: • We conduct a detailed characterization … • Driven by
  our characterization, we motivate and explore …"
- [LazyDP] uses bold mechanism leads instead ("• Lazy noise update. …"); [TC] and [CAL] end the
  introduction on the results with no bullet list. SPLEX follows [M].

The order varies by one move: [M] names the system (A4) before it characterizes (A5); [SS] runs
A5–A7 twice, under **Software.** and **Hardware.** run-ins. The eight moves themselves are common to
all six, and none opens on the technical claim.

---

## B. Sentence rules (in addition to `01_sentence_style.md`)

- **Subject first, verb early, one claim per sentence; the paragraph's first sentence is the claim and
  the rest is evidence.** [PVF] "The long frame latency is detrimental to vision-enabled embedded
  systems. For instance, a typical embedded robot today has a 200 ms responsive latency …"; [SS]
  "Unlike conventional DNNs … GNN training inherently contains a hybrid mix of both sparse and dense
  dataflows (Figure 1). More concretely, the frontend stages …"
- **Name the thing; no metaphor, no implication, no suspense.** [PVF] "The three major stages in a
  vision pipeline – sensing, imaging, and vision computation – process a frame sequentially, leading
  to high per-frame latencies." The reader is never asked to infer what a word stands for.
- **A signpost adverb opens the decisive sentence.** [M] "Critically, our algorithmic optimizations
  can directly benefit software running on commodity GPUs without hardware support."; [TC]
  "Interestingly, while it is challenging to define a generic TPU architecture …"; [TC] "Concretely,
  the backpropagation based training algorithm requires …"; [SS] "Unfortunately, …", "To this end,
  …", "More concretely, …", "As such, …"; [LazyDP] "Overall, LazyDP provides …". One per paragraph.
- **Every named artifact gets its defining clause the first time; i.e. / e.g. are used freely.**
  [CAL] "A point cloud is an unordered set of points within the 3D Cartesian space, each point being
  uniquely identified by its <x, y, z> coordinates"; [LazyDP] "DP-SGD (differentially private
  stochastic gradient descent), which is an extension to non-private SGD"; [SS] "the in-memory
  processing model (i.e., the target graph nodes/edges and its feature embedding tables must be
  stored inside main memory)".
- **Numbers carry a baseline and a unit, and the introduction prints only the headline ones.** [SS]
  "9.8× slowdown vs. an oracular, in-memory processing based system"; [M] "3.8% area overhead to the
  NPU (<0.05% of a typical SoC area)"; [PVF] "up to 50% of the total energy". No symbol the reader
  has not met: none of the six prints a variable in §1.
- **Mechanism at the abstract level: one key-idea sentence, the section number in parentheses.**
  [PVF] "we propose a new vision execution model where the vision front-end, i.e., the sensing and
  imaging stages, predicts future frames, and the vision computation stage operates proactively on
  predicted future frames."; [LazyDP] "(Section 5.2.1)" closes each mechanism bullet.
- **Prior work is described by what it does before its limit is stated; two or three named systems
  per point.** [SS] mmap page cache → "benefit little"; [LazyDP] the DP-SGD studies → "primarily
  focused on computer vision or natural language processing"; [TC] "Several recent work identified
  and addressed the performance bottlenecks caused by the tensor gather-and-reduce operation … A
  unique contribution of our characterization is the revelation of a new system-level bottleneck".
- **Enumerated pairs for challenges and findings.** [PVF] "PVF addresses two key challenges. First,
  … Second, …"; [TC] "The key innovation of our Tensor Casting is twofold. First, … Additionally, …".
- **Contribution bullets open "We characterize / We propose / We evaluate", ≤ 3 sentences, ≤ 40
  words** ([M]'s three bullets are 27, 42 and 30 words).

---

## Worked example (SPLEX, ASPLOS submission)

### Anti-patterns in the SPLEX §1 before the rewrite, with the fix applied

| anti-pattern (before) | why it fails the references | fix |
|---|---|---|
| Colon-chain opener: "LLM decode is memory-bound: each step streams the weights and the KV cache … once per batch, so serving systems batch requests continuously" | opens on the technical claim (A1 is violated; no paper does this) | landscape first: long contexts, agentic use, large batches with the named models and frameworks; the KV cache arrives as the property that matters |
| "The established relief is host memory" | metaphor the reader must decode (B: name the thing) | "Prior systems offload the KV cache to host memory." |
| "Used naively, the extension adds capacity but not bandwidth." | a participial hedge in front of the subject; the claim is implied | "The LPDDR extension expands capacity, but it does not guarantee bandwidth." |
| "This paper measures those statistics and builds the organization on them." | a flat announcement where the references place the paper's goal (A4) | "To this end, this paper characterizes the selection statistics of DSA models and builds the first KV-cache tier on LPDDR-extended custom HBM from them." |
| $h^\ast = 0.77$, $h = 0.90$, "$1{,}024 : 113.8$", "8--36 %" of the latents | symbols and section-level detail in §1 (B: headline numbers only) | "the optimal split, which balances the utilization of both tiers, keeps 77 % of the gathered entries in HBM"; the interleave "keeps 90 %" |
| ESS; HiSparse; GVR; SAC in one sentence | a survey, not a point (B: two or three systems, each by what it does) | ESS and HiSparse only, one clause each, then the shared limit (lag-1) |
| ¶5 and ¶6 as runs of numbers (204 and 176 words, two thirds of them figures) | the paragraph has no claim sentence; the reader cannot tell which number matters | claim first, three facts with one number each, "Critically," on the decisive one |
| "Which latents get that room must therefore come from the selection statistics" | implication in place of the statement | "Critically, which entries get that room is decided by the selection statistics that native sparse attention exposes, and no serving system measures them beyond lag 1." |
| Bold noun leads on the contributions ("Selection statistics beyond lag-1.") | [M]/[PVF]/[SS] bullets open with a verb | "We characterize … / We propose … / We evaluate …" |

---

### The SPLEX §1 — the move map and the guards as run

| ¶ | move | first sentence (must be a claim) | words |
|---|---|---|---|
| 1 | A1 | "LLM serving has moved to long contexts, agentic use, and large batches." | ≈ 90 |
| 2 | A2–A3 | "Prior systems offload the KV cache to host memory." | ≈ 70 |
| 3 | A3 | "Sparse attention has meanwhile become part of the model itself." | ≈ 130 |
| 4 | A1′ (the substrate) | "Custom HBM opens a second path to capacity, on the memory side." | ≈ 110 |
| 5 | A2 (the paper's problem) | "The LPDDR extension expands capacity, but it does not guarantee bandwidth." | ≈ 170 |
| 6 | A4–A7 | "To this end, this paper characterizes … and builds the first …" | ≈ 170 |
| — | A8 | "In summary, this paper makes the following contributions:" | 4 × ≤ 40 (model → characterize → propose → evaluate, the order of ¶5–¶6; since 2026-09-07) |

Guards as run on the SPLEX source: no "relief", "naively", `h^\ast`, `f_avail`, "B = 32"; no GVR / SAC / CXL;
`\TBD` 0; "cross-layer" 0; "runtime" as a noun 0; "first" exactly three times (¶6's tier sentence
"builds the first KV-cache tier on LPDDR-extended custom HBM", the leading "We build the first
cycle-level model of an LPDDR far tier behind an HBM base die" bullet, and the "We propose SPLEX,
the first KV-cache tier on custom HBM with an LPDDR extension" bullet — so no "First, … Second, …"
enumeration in §1; since 2026-09-07); every number greps in §3 or
§6 with the same value; vocabulary per the paper's role list (attention kernel nominates, base-die
engine decides and moves, serving framework commits).

## Guard classes

Run on the introduction's source before every commit; the SPLEX instantiation is the guard paragraph above.

- **Retired words:** every metaphor, hedge and symbol the anti-pattern table retired stays out; every system beyond
  the two or three named per point stays out.
- **Placeholders and banned vocabulary:** every draft placeholder macro 0; every word on the paper's banned list 0.
- **Priority claims:** "first" counted exactly — once per distinct first claim, in the sentence and the bullets that
  carry it — and no "First, … Second, …" enumeration competing with it in §1.
- **Numbers:** grep every number in §1 against the motivation and evaluation sections' source; the same value must appear.
- **Role vocabulary:** every agent named by its fixed verb from the paper's role list.
- **Move map:** each paragraph's first sentence is a claim, the paragraphs follow A1–A8, and the contribution bullets
  open with a verb at ≤ 40 words each.
