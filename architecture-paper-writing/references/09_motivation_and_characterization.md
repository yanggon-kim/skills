Part of the architecture-paper-writing skill. Governs: the motivation and workload-characterization sections. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

# Motivation / characterization style guide — how the six reference papers write a §Motivation, §Observation or §Characterization

Read before writing or editing §2's motivating paragraphs, §3 in whole or in part, and any paragraph elsewhere whose job is to
*report a measurement about the workload rather than about our design*.

**Sections read in full** (`pdftotext`, 2026-09-09; the word counts include figure captions, so the prose is 10--20 % lower). Every
quote below is cited by paper tag and subsection; the page of a quote is the page range of its subsection, given here once:

| tag | paper | the characterization section | pages | words |
|---|---|---|---|---|
| **[CAL]** | Characterization and Analysis of DL for 3D Point Cloud Analytics, IEEE CAL'21 (Rhu) | §2.2 *Key Challenges and Motivation*; **§4 *Characterization*** (§4.1 accuracy / §4.2 latency breakdown / §4.3 compute and memory efficiency) | 106–107; 108–109 | 310 + 1,180 |
| **[M]** | Mesorasi, MICRO'20 (Zhu) | §III *Motivation* (§III-A architecture, §III-B *Performance Characterizations* + *Summary*); §IV-C *Bottleneck Analysis* | 1038–1041; 1042–1043 | 1,430 + 210 |
| **[TC]** | Tensor Casting, HPCA'21 (Rhu) | §III *Workload Characterization* (§III-A breakdown, §III-B the isolated primitive) | 239–240 | 1,160 |
| **[SS]** | SmartSAGE, ISCA'22 (Rhu) | §3 *Motivation and Characterization* (§3.1 motivation, §3.2 in-memory, §3.3 SSD-centric) | 935–936 | 810 |
| **[PVF]** | Low-Latency Proactive Continuous Vision, PACT'20 (Zhu) | §2 (§2.1 *Latency Bottleneck*, §2.2 *Limitations of Optimizing Only Vision Algorithms*) | 329–330 | 990 |
| **[LazyDP]** | LazyDP, ASPLOS'24 (Rhu) | §4 *Workload Characterization on Private RecSys Training with DP-SGD* (§4.1/§4.2/§4.3) | 620–622 | 2,040 |

**[CAL] is the archetype for our §3** — the whole paper is a characterization — and is weighted heaviest below. Corpus for every count
in this file: the six sections above, 8,360 words.

This file governs §3 (and §2's motivating half). Its companions: `01_sentence_style.md` (the sentence contract, every section),
`02_paper_structure_and_figures.md` §1–2 (the narrative spine, §3 lesson L1) and §3 (the figure system), `05_design.md` + `08_design_section_lessons.md`
(§4), `06_methodology_evaluation.md` (§5/§6), `03_abstract.md`, `04_introduction.md`, `07_conclusion.md`. **Every rule below carries a
sentence quoted verbatim from a named paper, cited by tag and subsection (pages in the table above); a rule without a quote
was left out.** Where a reference's
practice conflicts with one of our standing contracts, §H says which wins.

---

## A. Section anatomy

**A1. The section opens with a roadmap of its own subsections, each forward-tagged.** Six of six.
- [M] §III: "We first introduce the general flow of point cloud algorithms and identify key operators (Sec. III-A). We then
  characterize point cloud algorithms on today's hardware systems to understand the algorithmic and execution bottlenecks (Sec. III-B),
  which motivate the Mesorasi design."
- [PVF] §2: "This section introduces the bottleneck of continuous vision systems, and describes the insufficiency of existing
  optimizations."
- [LazyDP] §4: "This section takes a top-down approach in characterizing the computational challenges of training RecSys with DP-SGD."
- **Test:** the section's first paragraph names each subsection and what it settles, in order.

**A2. The opening paragraph also names the vehicle, the parameters and the sweep, and forward-tags the methodology section.** Six of six —
the measurement's conditions are declared before any number is printed.
- [TC] §III: "In this paper, we utilize the open-source deep learning recommendation model (DLRM) [41] as a vehicle to conduct a
  workload characterization study on training recommendations over CPU-only and CPU-GPU systems." … "Therefore, this paper assumes a default
  batch size of 2048 (the nominal batch size of DLRM) but sweeps this number from 1024 to 4096 to examine sensitivity. Section V further
  details our methodology."
- [M] §III-B: "To that end, we profile the performance of five popular point cloud networks on the mobile Pascal GPU on the Jetson
  TX2 development board [10], which is representative of state-of-the-art mobile computing platforms. Please refer to Sec. VI for a detailed
  experimental setup."
- [LazyDP] §4: "In order to demonstrate the effect embedding table size has on DP-SGD's training time, we scale down the size of this
  default model by reducing the number of embedding table entries, from 10x (9.6 GB) to 1000x (96 MB)."
- **Test:** before the section's first number, the reader can name the model, the platform, the swept parameter and where the full setup lives.

**A3. Subsection order is: does the thing matter → where the time goes → why it is slow.** Validity of the object first, breakdown second,
root cause third. [CAL] §4.1 *Effect of Noise on Downstream Task Accuracy* → §4.2 *Latency Breakdown* → §4.3 *Compute and Memory Efficiency*;
[SS] §3.1 *Motivation* → §3.2 *Data Preparation in In-Memory Training* → §3.3 *Data Preparation in SSD-centric Training*;
[LazyDP] §4.1 *Breakdown of End-to-End Training Time* → §4.2 *Analysis on the Model Update Stage* → §4.3 *Root-causing the Key Challenges*.
- **Never** open on the root cause. A reader who has not seen the breakdown cannot judge which cause is worth explaining.

**A4. Each subsection after the first opens by naming what the previous one established, then what this one adds.** The back-pointer is a
fact, not a summary of the writing.
- [CAL] §4.2: "Our characterization in Section 4.1 confirmed the critical role denoising filters play in guaranteeing robust
  algorithmic performance. Therefore, this subsection seeks to identify major performance bottlenecks in an end-to-end point cloud processing
  pipeline that includes the SOR filtering stage."
- [TC] §III-B: "As our characterization uncovered gradient expand-coalesce as causing a significant performance bottleneck, this
  subsection provides more detailed analysis on the important properties of this key primitive in relations to various recommendation training
  datasets and the data locality therein."
- [LazyDP] §4.2: "The previous subsection identified the model update stage as becoming a critical performance bottleneck in training
  private RecSys."

**A5. The section closes on a named target, not on a number and not on the design.** Five of six.
- [TC] §III-B: "Overall, our workload characterization on training recommendation models root-caused the backpropagation step of
  embedding layers, specifically the gradient expand-coalesce primitive, as a crucial system-level bottleneck."
- [M] §III-B Summary: "Today's point cloud algorithms extract local features of a point by aggregating the point with its neighbors.
  The aggregation happens before feature computation, which leads to two fundamental inefficiencies: • The two major performance bottlenecks,
  neighbor search and feature computation, are serialized. • Feature computation operates on aggregated neighbor points, leading to high
  memory and compute cost."
- [SS] §3.3: "Driven by our characterization, this paper explores an ISP based SSD-centric architecture for large-scale GNN training."
- **Imitate [M]'s Summary**: a short paragraph whose content is the two or three facts, each restated as a property of the workload.

**A6. Length.** 800–1,500 words of prose per characterization section is the reference band (CAL ≈ 900 prose, M §III-B ≈ 1,100, TC ≈ 950,
SS ≈ 750, PVF ≈ 800; LazyDP's 1,500 is the outlier and it is an ASPLOS full paper with a 2-page characterization). A section at the top of
the band while the body is over the page limit **grows only by replacement.**

---

## B. The paragraph skeletons

Every measurement paragraph in the corpus is one of these six. Name the skeleton before writing the paragraph; a paragraph that is none of
them is usually an argument in disguise.

**S1 — the measurement paragraph (the workhorse; [SS], [CAL], and the model for a measurement subsection):**
*what is measured and under which condition* → *the number* → *why it happens, in mechanism terms* → *what it forces*. Four sentences, one number
per sentence at most, the mechanism sentence never carrying a number of its own.
- [SS] §3.2, the whole skeleton in one paragraph: "Results show that neighbor sampling exhibits low caching efficiency with an average 62% last-level cache (LLC)
  miss rate." … "Interestingly, the off-chip memory bandwidth utilization is generally low despite such high memory intensity, consuming only an
  average 21% of 125 GB/sec maximum memory throughput. This is because each sampling operation only amounts to a fine-grained 8 byte read
  transaction, leading to severe underutilization of DRAM read throughput. Such characterization result implies that the neighbor sampling
  algorithm is severely memory latency limited, rather than throughput limited, providing guidelines on optimizing our SSD based training system."
- [CAL] §4.3, the same skeleton on the same finding one year earlier: "A key observation we make is that the memory-intensive
  gather/distant calculation/sorting all exhibit very low memory bandwidth utility. This is because the average data fetch size of these
  operators (e.g., 24 bytes for distance calculation) are far less than the minimum data access granularity of the processor-memory interface,
  substantially wasting DRAM bandwidth. Such results imply that these compute primitives are memory latency limited, rather than memory
  throughput limited, providing valuable insights on optimizing their system-level bottlenecks."
- **The closing move is always "X rather than Y", never "X, therefore build Z".** The implication names the *property*, and the design follows in
  a later section.

**S2 — the breakdown paragraph ([TC] §III-A, [LazyDP] §4.1, [CAL] §4.2):** *the figure shows a breakdown* → *First / Second / Third, each an
observation with its share* → *one component singled out and named the bottleneck*.
- [TC] §III-A: "Some key observations that can be made from this figure are as follows. First, there exists a noticeable performance gap
  between CPU-only and CPU-GPU, especially for MLP intensive RM3 and RM4, highlighting the significant role GPUs play in training
  recommendations." … "In particular, the gradient expand-coalesce takes up a substantial fraction of backpropagation's latency, causing a
  significant bottleneck."
- **Do not copy the First/Second/Third enumeration into §1** (our contract forbids it there) but it is the right form inside a breakdown paragraph
  where the facts are parallel and independent.

**S3 — the exception-first paragraph ([CAL] §4.2):** *name the workload that does not fit and dispose of it* → *the rule for the rest, with the
average* → *the implications, each anchored outside the paper*.
- [CAL] §4.2: "With the exception of PointRCNN (object detection), all benchmarks consume a non-negligible fraction of their runtime on
  stages outside the feature extraction and downstream task processing, i.e., data preparation." … "Unfortunately, as for the other three
  benchmarks, the data preparation stage followed by FPS dominates the overall runtime and accounts for an average of 72.5 percent of latency."
- The exception is not hidden and not apologised for; it is explained by mechanism ("other non-deep learning components (e.g., RoI pooling, NMS,
  others) consume significant processing cycles thus amortizing the overhead of SOR filters") and later turned into support for the class claim
  (§D3).

**S4 — the contrastive-limit paragraph ([PVF] §2.2; the shape of a prior-art-limit subsection):** *what prior work optimizes and when it works* → *the condition under
which it stops working* → *two measured cases, the favourable one printed first* → *a second axis* → *a scope sentence*.
- [PVF] §2.2: "Back-end optimizations are effective when the back-end dominates the frame latency. However, in many cases, depending on
  the complexity of the vision task and the image resolution, the front-end could contribute significantly to the frame latency, making the
  back-end optimizations ineffective."
- [PVF] §2.2: "A 2x vision stage latency reduction translates to only 9% frame latency reduction for tracking, much lower compared to
  the 62% reduction for detection." … "The latter spends significantly less time in the back-end, and thus gets improved only by 6% as compared
  to 49% observed on higher resolution inputs."
- **The rival's best case is measured and printed.** 62% and 49% are the numbers that make the 9% and 6% credible.

**S5 — the scaling paragraph ([LazyDP] §4.1, [M] §III-B *Memory Analysis*):** *what stays constant* → *what grows and in which variable* → *the
mechanism that makes it grow* → *an extrapolation, hedged and cited*.
- [LazyDP] §4.1: "In general, the training time of SGD remains almost constant regardless of the table size, so we only show a single
  SGD data point in Figure 3 for brevity. In contrast, all three DP-SGD designs experience an almost linear increase in latency as table size
  increases. The reason why DP-SGD experiences aggravated training performance is as follows."
- [LazyDP] §4.2: "so we can infer that these two bottlenecks will only get worse for future RecSys models with even larger table
  sizes [46, 67]".
- **Hedging is permitted only here**, and only with a citation attached (§C7).

**S6 — the headroom paragraph ([LazyDP] §4.3), the one that pre-empts "just optimize it":** *the baseline was tuned to its ceiling* → *a
microbenchmark that locates the ceiling* → *the baseline is already at X% of it* → *therefore the fix is not an implementation fix*.
- [LazyDP] §4.2: "We emphasize that, rather than utilizing PyTorch's built-in functions as-is for our characterization, we heavily
  optimize and tune the performance of this bottleneck stage to construct a strong, competitive baseline DP-SGD. More concretely, our optimized
  version of the model update stage is 8.2x faster than the baseline implementation using the original built-in PyTorch functions, reaching 81%
  of the maximum possible AVX performance achievable for this stage."
- [LazyDP] §4.3: "To better illustrate the compute-bound (noise sampling) and memory-bound (noisy gradient update) nature of model update
  stage, we design a microbenchmark that conducts (1) an AVX vector load from memory, (2) performs N consecutive AVX computations over the loaded
  vector, and then (3) writes back the resulting vector into memory using AVX store."
- [LazyDP] §4.3: "Overall, these results confirm that the noise sampling and noisy gradient update operators we utilize as our baseline
  DP-SGD(B,R,F) leave little performance left on the table because they already reach close to the optimal performance under the training
  system's available compute and memory throughput constraints."
- A calibrated synthetic sweep whose job is to locate the optimum a design can reach, not to report a run, is this figure. Say what it is (§F3).

---

## C. Sentence style

**C1. Shape.** Subject = the workload, the stage, the operator or the measured quantity — never the paper, never the reader, and (in §3) never our
system. Present tense for what is true of the workload, past tense only for what we did once ("we used publicly available training
datasets" [TC]). Active voice with an agentive "we" for construction ("we profile", "we design a microbenchmark", "we scale down"), and the
workload as agent for findings ("neighbor sampling exhibits low caching efficiency" [SS]).

**C2. Length.** Median sentence 19–34 words across the six (M and PVF 19, CAL 23, TC 28, SS 29, LazyDP 34); 90th percentile 31–56. The house target
sits at the Zhu end (19–24 median): the Rhu papers reach 34 by stacking subordinate clauses, which our sentence contract does not want.

**C3. Density.** **One sentence in three carries a number.** Measured on the corpus with citation brackets and figure/section numbers stripped:
CAL 37 %, M 36 %, TC 35 %, SS 33 %, PVF 32 %, LazyDP 50 %. Below ~30 % the section is an essay; above ~50 % the mechanism sentences have been
squeezed out and the reader cannot see why any number is what it is. **Test:** count the sentences of the paragraph and the ones with a number; the
ratio is between 1:3 and 1:2.

**C4. The number's place in the sentence.** Late, inside the clause that names the quantity, always with its unit and its comparison anchor.
- [SS] §3.2: "consuming only an average 21% of 125 GB/sec maximum memory throughput" — share, denominator and unit in one phrase.
- [CAL] §4.2: "accounts for an average of 72.5 percent of latency"; [M] §IV-C: "On average, the aggregation time increases from
  3% to 24%."
- Never a bare number and never a number as the subject. Parallel triples take "respectively": [CAL] §4.2: "53.9/23.6/0.8
  frames-per-second for classification/segmentation/detection, respectively"; "we observe an average of 55.6, 1.43, and 15.3 percent of execution
  time spent conducting gather, distant calculation, and sorting, respectively".

**C5. How a trend is stated.** Name the independent variable, then the shape, then the mechanism — never "grows quickly".
- [LazyDP] §4.1: "all three DP-SGD designs experience an almost linear increase in latency as table size increases".
- [M] §III-B: "The layer output usually exceeds 2 MB, and could be as large as 32 MB, much greater than a typical on-chip memory size in
  today's mobile GPUs or DNN accelerators." — a distribution is given as its two ends against a threshold the reader knows.
- [M] §III-B: "In PointNet++, over half occur in more than 30 neighborhoods; in DGCNN, over half occurs in 20 neighborhoods." — a
  distribution reported by a quantile, not by a mean.

**C6. How causation is asserted.** A "This is because" sentence, or a "because" clause after the number, and the cause is a *mechanism the reader can
check*, usually a size against a granularity or a capacity.
- [SS] §3.2: "This is because each sampling operation only amounts to a fine-grained 8 byte read transaction"; [CAL] §4.3: "the
  average data fetch size of these operators (e.g., 24 bytes for distance calculation) are far less than the minimum data access granularity of
  the processor-memory interface".
- [M] §IV-C: "Aggregation time increases mainly because aggregation involves irregular gather operations [30], which now operate on a
  much larger working set with delayed-aggregation. For instance, in PointNet++'s first module (Fig. 8), aggregation originally gathers from a
  12 KB matrix but now gathers from a 512 KB matrix, which is much larger than the L1 cache size (48 KB – 96 KB) in the mobile Pascal GPU on TX2."
  (The printed line carries a footnote marker after "96 KB"; it is dropped here, as is usual in quotation.)
- Frequency: "This is because" 5, plain causal "because" 13, "Consequently" 5, "Thus" 10, "leading to / leads to" 5 in 8,360 words. **One causal
  construction per measurement**; two in one paragraph reads as an argument.

**C7. How causation is hedged.** Only for extrapolation beyond the measured range, and then with a citation: [LazyDP] §4.2, "we can infer
that these two bottlenecks will only get worse for future RecSys models with even larger table sizes [46, 67]" (the corpus's single hedge).
A mechanism that holds by construction is asserted flat: [M] §III-B: "The large activation size is fundamental to point cloud algorithms.
This is because an input point usually belongs to many overlapped neighborhoods, and thus must be normalized to different values, one for each
neighborhood."

---

## D. Focus and discipline — keeping a characterization from becoming an advertisement

**D1. The design implication is capped, placed last, and stated as a property.** Own-system mentions inside the characterization section:
**TC 0, LazyDP 0, PVF 0, SS 1, M 2, CAL 0** (CAL names Mesorasi, which is prior work). Three of six papers characterize their workload for one to
two pages **without naming their own system once**.
- The permitted forms, in ascending strength: a property ("memory latency limited, rather than throughput limited" [SS], [CAL]); a requirement
  ("which calls out for system-level optimizations to address the limitations of frontend preprocessing steps" [CAL] §4.2); a one-clause
  forward reference at the very end of a paragraph ([M] §III-B: "Mesorasi's algorithm breaks this serialized execution chain, allowing F
  and N to be overlapped."); one section-closing sentence ([SS] §3.3, quoted in A5).
- **Test:** per subsection, at most one sentence names or forward-references our design, and it is the subsection's last sentence. Section-wide, at
  most two. If a paragraph needs two, the second belongs in §4.

**D2. The design is *not* the subject of the closing implication.** [LazyDP] §4.3's takeaway says "suggesting that alternative measures must be
devised to address the performance bottlenecks of private RecSys training" — an unnamed alternative, in a paper whose §5 is entirely about LazyDP.
Write the requirement; let §4 claim to meet it.

**D3. A measurement that does not support the thesis is printed first and explained, then reused.** Three patterns in the corpus:
- **The exception among workloads.** [CAL] §4.2 opens the paragraph with it (S3), explains it, and later converts it into support:
  "It is interesting to note that PointRCNN, which spends less than 6 percent of runtime on data preparation, still consumes significant compute
  cycles on gather and sorting operation, rendering these memory-limited operations a critical compute primitive in tackling the system-level
  bottlenecks of end-to-end point cloud inference." (Copy the move, not the words — see §H4.)
- **The prior technique that works.** [PVF] §2.2 prints the 62 % and 49 % where motion extrapolation succeeds before the 9 % and 6 % where
  it fails, and closes by conceding scope: "We propose to improve the latency and energy efficiency at the same time by breaking the sequential
  execution model. It is meant to complement, not replace, back-end optimizations to achieve greater latency and energy reductions."
- **The negative result about our own baseline.** [LazyDP] §4.3 (S6) measures that the baseline is already at 81 % of the compute ceiling and
  85.5 % of theoretical bandwidth — a result that removes an easy alternative rather than supporting the design. [M] §IV-C does the same
  against Mesorasi's own algorithm: "While delayed-aggregation reduces the compute costs and memory accesses, it also significantly increases the
  aggregation time."

**D4. The rival is named, credited and quantified before it is limited.** [TC] §III-A: "Interestingly however, MLPs account for only a small
fraction of overall training cycles under CPU-GPU (less than 1% for embedding limited RM1/RM2 and 24% for MLP limited RM3/RM4), rendering the
remaining embedding layers the most prominent performance bottleneck." [LazyDP] §4.1: "In other words, prior work on performance-efficient
DP-SGD (DP-SGD(F)), while effective in reducing DP-SGD(B)'s backpropagation latency to derive gradients, is not able to fundamentally address the
bottlenecks incurred in training the embedding tables with DP." — the limit is *scoped* ("not able to fundamentally address X"), never a dismissal.

**D5. The measurement is anchored to a requirement outside the paper wherever one exists.** [PVF] §2.1: "As a result, even if all three
stages individually operate in real time, e.g., 30 frames per second (FPS), the end-to-end per frame latency could add up to over 100 ms. Long
frame latency severely limits the applicability of vision-enabled systems. For instance, an autonomous vehicle needs to respond to an event within
100 ms as it can travel 2-3 meters during the interval. Similarly, a 100 ms rendering latency causes nausea and is intolerable to AR users [20]."
This is the alternative to [M]'s "clearly infeasible" (§H3): the number is judged against a cited external budget, not by an adverb.

**D6. A scope cut is announced with its reason, in place.** [LazyDP] Fig. 3 caption: "SGD's training time remains almost constant regardless
of the table size, so this figure only shows a single SGD data point under the default 96 GB for brevity." [CAL] §3: "we do not include the
voxel grid filter as well as the RANSAC filter as these filters are only optionally included under limited circumstances". A workload whose
statistics exist and are not printed needs the reason printed with the cut.

---

## E. Vocabulary

**E1. Frequency-ranked, over the 8,360-word corpus.** Counts are stems, all six sections combined.

| rank | stem | n | how it is used — quoted |
|---|---|---|---|
| 1 | **bottleneck** | 27 | the noun the whole section drives at; "causing a significant bottleneck" [TC §III-A], "root-cause its two most significant performance bottlenecks" [LazyDP §4.1] |
| 2 | **significant / significantly** | 23 | always beside a number, never instead of one: "consume significant processing cycles" [CAL], "significantly increases the aggregation time" [M §IV-C] |
| 3 | **limited** | 20 | the verdict form: "memory latency limited, rather than throughput limited" [SS, CAL]; "embedding limited RM1/RM2" [TC] |
| 4 | **characterize / characterization** | 19 | names the activity, in the roadmap and the close: "Driven by our characterization" [SS §3.3] |
| 5 | **utilization / utility** | 19 | the fraction-of-peak metric: "the off-chip memory bandwidth utilization is generally low" [SS §3.2] |
| 6 | **breakdown / break down** | 16 | "we show in Fig. 5a a breakdown of inference latency separated by major stages" [CAL §4.2] |
| 7 | **consume** | 14 | of time and of capacity: "consuming only an average 21% of 125 GB/sec" [SS] |
| 8 | **average** | 13 | the aggregation word; "an average 9.8x (maximum 19.6x) slowdown" [SS §3.3] |
| 9 | **exhibit** | 12 | the workload as subject of a property: "neighbor sampling exhibits low caching efficiency" [SS] |
| 10 | **observe / observation** | 12 | "A key observation we make is that…" [CAL §4.3]; "Some key observations that can be made from this figure are as follows." [TC §III-A] |
| 11 | **Thus / Consequently / Therefore** | 10 / 5 / 3 | one per causal step |
| 12 | **However** | 9 | the turn into the limit: "However, in many cases … making the back-end optimizations ineffective" [PVF §2.2] |
| 13 | **incur** | 7 | of cost: "incurs an average 60.8 percent degradation" [CAL §2.2] |
| 14 | **dominate** | 7 | "the data preparation stage followed by FPS dominates the overall runtime" [CAL §4.2] |
| 15 | **This is because** | 5 (+13 plain "because") | the mechanism sentence (§C6) |
| 16 | **root-cause** (verb) | 4 | reserved for the section's verdict: "root-caused the backpropagation step of embedding layers … as a crucial system-level bottleneck" [TC §III-B] |
| 17 | **fundamental / inherent** | 4 / 2 | only where a mechanism is given in the same paragraph: "The large activation size is fundamental to point cloud algorithms." [M §III-B] |
| 18 | **grows / proportional / scale** | 4 / 4 / 11 | the trend verbs (§C5) |
| 19 | **accounts for / account for** | 6 | share of a total: "accounts for an average of 72.5 percent of latency" [CAL §4.2] |
| 20 | **Overall,** | 8 | opens the closing verdict of a subsection or the section |
| 21 | **underscore / highlight / imply / confirm** | 2 / 2 / 2 / 2 | the implication verbs; "Such results imply that these compute primitives are memory latency limited" [CAL §4.3] |
| 22 | **Interestingly / Unfortunately / Critically / Note that** | 2 / 2 / 1 / 2 | one signpost adverb per subsection at most |

Also in use and worth stealing: **takes up** ("takes up a substantial fraction of backpropagation's latency" [TC]), **amounts to** ("only amounts to
a fine-grained 8 byte read transaction" [SS]), **translates to** ("A 2x vision stage latency reduction translates to only 9% frame latency
reduction" [PVF]), **render** ("rendering the remaining embedding layers the most prominent performance bottleneck" [TC]), **spent conducting**
[CAL], **wasting** ("substantially wasting DRAM bandwidth" [CAL]), **reach / reaching** ("reaching 81% of the maximum possible AVX performance"
[LazyDP]).

Verbs a draft may already carry that are consistent with the above: **is bound by**, **holds through**, **erodes**, **scales with**,
**dominates** (one use each in the SPLEX draft). Reach for the reference verbs before inventing one.

**E2. Words with 0 occurrences in 8,360 words of characterization — do not introduce them.**
`as expected` · `obviously` · `of course` · `arguably` · `we believe` · `novel` · `elegant` · `surprisingly` · `dramatic` · `huge` · `massive` ·
`poor` · `bad` · `orders of magnitude` (one "an order of magnitude", with the comparison printed) · `key takeaway` in prose (it appears 3 times, but
only as [LazyDP]'s typeset label — never inside a sentence) · any question mark outside [LazyDP] §4.3 (§H1) · `clearly` once, in [M], and we do not
copy it (§H3).

---

## F. Point-addressing patterns

**F1. How an observation is named — five devices, and which paper uses which.**

| device | who, how often | verdict for us |
|---|---|---|
| **Bold run-in head per observation** — *Time Distribution* / *Memory Analysis* / *Compute Cost* / *Summary* [M §III-B, 4 in ~1,400 words]; *Breakdown Per Stage.* / *Breakdown Per Operator.* [CAL §4.2, 2] | 2 of 6 | **adopt** — a `\paragraph{}` run-in head, and it costs no printed line beyond the run-in |
| **Numbered / enumerated observations inside one paragraph** — "First, … Second, … Third, … In particular, …" [TC §III-A] | 1 of 6 | adopt inside a breakdown paragraph only (S2); never as the section's skeleton, and never in §1 |
| **Italic `Key takeaways:` after every subsection** [LazyDP §4.1/4.2/4.3, 3 of 3] | 1 of 6 | **do not adopt** — see §H2 |
| **A single `Summary` paragraph closing the section** [M §III-B] | 1 of 6 | **adopt** |
| **No label at all, contrast carrying the structure** [PVF §2, SS §3.2] | 2 of 6 | fine for a short subsection |

There is **no "Observation 1:" numbering and no boxed summary anywhere in the corpus.** Do not invent one.

**The house's own sixth device, and it is the right one: a `\lead{}` run-in that states the finding.** The SPLEX §3.3 carries four
(*The latent hot set is small and skewed.* / *Hotness is temporal: a fast drop, then a slowly eroding
core.* / *Churn recycles within a small working set.* / *Hotness is semantic, not positional.*). It is [M]'s bold run-in with [LazyDP]'s
takeaway folded into it: the head is the claim, so the paragraph needs no closing restatement and costs no extra printed line. Keep it, and
keep each one a claim that the paragraph's own numbers settle — a head naming a topic ("Temporal behaviour.") throws the device away.

**F2. A figure is named in the sentence that reports its number, never in a bare parenthesis.** 78 figure references in 8,360 words — one per ~107
words, i.e. one or two per paragraph. The reference is the subject or the object of the reporting sentence:
- [CAL] §4.2: "We show in Fig. 5a a breakdown of inference latency separated by major stages of data preparation, feature extraction, and
  downstream task processing."
- [M] §III-B: "Fig. 4 shows the execution times of the five networks"; [M] §III-B: "Fig. 6 shows the distribution of the number of
  neighborhoods each point is in."
- [LazyDP] §4.2: "In Figure 5, we further break down the latency of the model update stage (red in Figure 3) into four parts".
- **Test:** every figure the section owns is named in prose at least once, in a sentence that also states what it shows; and every claim that rests
  on a figure names it in the same or the previous sentence.

**F3. The figure's construction is explained where the construction is not obvious.** [TC] §III-B: "To accurately reflect the locality
inherent in embedding gathers for our characterization, we used publicly available training datasets for recommendations which include Amazon
Review (Books) [4], MovieLens-20M [17], Alibaba's TaoBao UserBehavior dataset [3], and Criteo AI Labs Ad Kaggle [31] to generate the sparse index
IDs utilized for embedding table lookups." A sweep that is a synthetic process **calibrated** to measured statistics must carry that word in
the text or the caption, because the reader will otherwise read it as a trace.

**F4. Transition between observations = the previous finding restated as the reason for the next measurement** (§A4), or a mechanism sentence that
belongs to both. [CAL] §4.2: "As we root-caused data preparation as a crucial performance limiter, gauging potential acceleration
opportunities within this critical preprocessing stage is important." No "Next, we …", no "Having shown …".

**F5. Generalization from one workload to the class is a two-step move: example, then the figure that generalizes.**
- [M] §IV-C: "Using PointNet++ as an example, Fig. 11 compares the execution time distribution across the three operations (N, A, and F)
  with and without delayed-aggregation." then, one paragraph later, "Fig. 12 generalizes the conclusion across the five networks." and "The
  aggregation time consistently increases in all five networks."
- [LazyDP] §5.1: "Generalizing this behavior across the entire embedding table, we can infer that the number of (delayed) noise updates
  invoked …".
- **A class claim needs either the second figure or an explicit mechanism reason.** [M] §III-B takes the mechanism route: "The large
  activation size is fundamental to point cloud algorithms." A section that measures one workload must make its class claim a mechanism claim,
  never "and the other models behave the same" — that sentence would need the other workloads' curves in the figure.

---

**F0. Run-in heads are blunt, general findings; the measurement opens the sentence below.** The head is a
plain declarative with a concrete subject, a plain verb and the scale *in words* — "Hot entries stay hot for
hundreds of steps." — not the measurement itself. "Sixty-four consecutive steps touch 12 % of the pool" and
"The most recent 2,048 positions cover 0.47 of a selection" are too specific for a head: the reader meets the
number before the claim it supports. Write the general fact as the head and give the number in the first
sentence under it. Never an abstraction ("Recency is not the signal") or an evaluation ("The deadline is
loose") either — the head carries the finding, the sentence below carries its number. (Author feedback on the
eval runs, two rounds; the later word in `11_writing_lessons.md`.)

**F0b. Pace the numbers.** One or two new numbers per sentence, each followed by its description; a sentence
that introduces a number opens with it, so the reader takes numbers at an even pace. A long sentence that
chains a measurement, a derived total and a derived ratio ("7,700 entries, 12 % of the pool, while issuing
64 × 2,048 ≈ 131K selections, so ~17 per entry") is too much: split it, and drop the derived figures unless
one completes arithmetic already on the page. Derived numbers: at most one per paragraph.

**F0d. A series the figure carries is printed at its endpoints, not point by point.** When a figure plots a
curve (retention against lag, coverage against region size), the prose gives the two numbers that make the
claim — the first point and the far tail — and cites the panel for the shape: "0.79 at the next step and still
0.35 after 1,024 (Figure 4b)". Walking every point ("0.79 … 0.64 after 64 … 0.48 after 512 … 0.35 after
1,024") in prose is number-centred description that the reader cannot hold; the figure exists so the prose
does not have to. *(author feedback, third round)*

**F0e. A figure citation says what to see.** "Figure 4(a) shows that selection is concentrated" throws the
figure at the reader; the sentence names the thing to look at — the knee, the value at 10 %, the gap between
two curves — so the reader is led, not assumed to find it. Never assume the reader will extract the point
from the figure unaided. *(author feedback)*

**F0c. A paragraph may open on the familiar alternative.** When readers know the prior approach, opening
with its logic and its limit before the measurement — "The natural alternative to tracking selections is to
keep the most recent positions resident, as a sliding-window cache does." — is a good skeleton (S4 in §B):
it names what the reader would have done, then the number says why not.

## G. Figure and table coupling

**G1. What a characterization figure is asked to prove — one claim per figure, and the claim is in the text.** Fig. 5 [SS] proves *the access is
fine-grained, not bandwidth-hungry*; Fig. 5 [CAL] proves *the share of the time*; Fig. 6 [M] proves *the mechanism behind the activation size*;
Fig. 6 [LazyDP] proves *the baseline sits at the ceiling*. A figure that would prove two claims is split into (a)/(b) panels with one sentence each
([CAL] Fig. 5a/5b, [PVF] Fig. 2's two groups).

**G2. The caption carries the setup and the experimental delta; the finding stays in the prose.** The rule with its exceptions:
- Setup-only captions (the majority): [M] Fig. 4: "Latency of five point cloud networks on the Pascal GPU on TX2. Results are averaged over
  100 executions, and the error bars denote one standard deviation." [SS] Fig. 5: "The LLC miss rate (left) and DRAM bandwidth utilization
  (right) during the neighbor sampling stage with baseline in-memory processing training using PyG. We utilize Linux perf (caching) and Intel RDT
  utility (bandwidth) for our evaluation." [TC] Fig. 5: "Our experiment assumes each table is gathered 10 times, which is why the expanded
  gradient size is precisely 10x larger than the initial backpropagated gradients. Results are normalized to the size of the backpropagated gradient
  tensor. Random assumes a uniform random distribution in modeling the probability of embedding table lookups."
- **Exception 1 — a schematic, not a chart:** [CAL] Fig. 2 (the pipeline diagram): "As we detail in Section 4, the red-colored stages (the
  data preparation process followed by the FPS step) take up a significant fraction of execution time in an end-to-end point cloud inference,
  e.g., 5-80 percent of inference time for data preparation."
- **Exception 2 — the figure has exactly one point to make and the text makes it too:** [LazyDP] Fig. 6: "As depicted, our implementation of
  noise sampling (corresponding to the data point at N=101) exhibits a compute-bound behavior and reaches 81% of the maximum AVX performance."
  [M] Fig. 12: "Both absolute (left y-axis) and relative (right y-axis) aggregation times increase with delayed-aggregation."
- **Test:** if the caption states a finding, the same finding is in the prose, and the number is one of the section's own; a caption is never the only
  place a number appears — except a definitional byte size in a schematic's caption (a standing house exception).

**G3. Every number a caption prints is a generator number.** A house rule, not the references': a caption value must live in the figure
generator's number table with an assert, or in the paper's frozen data views. [CAL]'s "5-80 percent" range is the kind of caption number that is easy to write and impossible to re-derive later.

**G4. No table in a characterization section.** None of the six uses one: the workload table is in §Methodology ([CAL] Table 1).

---

## H. Where the references conflict with our contracts, and which wins

1. **Questions to the reader.** [LazyDP] §4.3: "a natural question arises: Can the two most bottlenecked stages, i.e., noise sampling and
   noisy gradient update, be optimized even further and remove their performance bottlenecks completely? Conversely, are noise sampling and noisy
   gradient update stages fundamental bottlenecks that require alternative measures to address their performance overheads?" — **our rule wins**
   (the house rule *No questions to the reader*; guard: `grep -n '?'` over every section source → 0). Write the S6 skeleton
   declaratively: state that the baseline was tuned to its ceiling, give the ceiling, give the fraction reached.
2. **Per-subsection italic takeaways.** [LazyDP]'s three `Key takeaways:` lines. **Our rule wins twice over:** `01_sentence_style.md` §2 deletes
   restatement-with-drums, and each label costs printed lines the body cannot afford. Keep [M]'s single closing `Summary.` — it is content, not a
   label, because it states facts the paragraphs did not state in that form.
3. **Adverbial verdicts.** [M] §III-B: "Fig. 4 shows the execution times of the five networks, which range from 71 ms to 5,200 ms, clearly
   infeasible for real-time deployment." — **our rules win** (`06_methodology_evaluation.md` §C bans "clearly" as evidence; `01_sentence_style.md`
   §2 bans self-characterization). Use [PVF]'s device instead: judge the number against a cited external budget (§D5).
4. **"It is interesting to note that …".** [CAL] §4.2. The *move* (reusing an exception as support) is right; the framing is
   meta-commentary, which `01_sentence_style.md` §2 deletes. Write the fact: "PointRCNN spends under 6 % of its runtime in data preparation and
   still …".
5. **Methodology inside the characterization.** [LazyDP] §4.2's "We emphasize that … we heavily optimize and tune …" and [TC] §III's batch-size
   choice sit inside the characterization; `06_methodology_evaluation.md` §F says the setup belongs to §Method. **Split the difference, and the
   reference wins on one point:** a measurement's *construction* stays in §3 when the number cannot be read without it (our §3.2's calibrated
   sweep, §3.3's decode length and layer count), while platform, versions and the roster stay in §5 with a forward tag (§A2).
6. **"up to N", "average N (maximum M)".** [SS] §3.3: "an average 9.8x (maximum 19.6x) slowdown". **Our rule wins**
   (`06_methodology_evaluation.md` §C): print both ends of the range.
7. **"compared to".** [PVF] §2.2 and 30 more uses across the six. **Our rule wins:** the draft's word is "against".
8. **Numbers with no frozen source.** No reference paper has this constraint; ours does. Every characterization number greps in the paper's
   frozen data views, a design doc or a verified citation, and the introduction copies the characterization section rather than the other way round.

---

## I. The reader test for a characterization paragraph

Hand the paragraph to a reader who **does not yet believe the claim and has not read §4**. Then:

**I1. The five-role test.** Every sentence plays exactly one of five roles, and the paragraph contains them in this order:
1. **Setup** — what is measured, on what, under which condition (and where the rest of the setup lives).
2. **Measurement** — the number, with unit and comparison anchor, naming its figure.
3. **Mechanism** — why the number is what it is, in terms the reader can check against a size, a granularity or a capacity.
4. **Consequence** — what the number forces, stated as a property of the workload ("X rather than Y"), not as a design.
5. **Scope** — the exception, the counter-case, or the limit of the claim.
A sentence that plays none of the five is decoration: delete it and stitch the neighbours (`01_sentence_style.md` §1). Roles 1, 3 and 5 may be
absent when an earlier paragraph supplied them; **role 2 without role 3 fails**, and so does role 4 without role 2.

**I2. Pass/fail checks — a paragraph fails if any is false.**
1. Its first sentence is a claim or a setup, not context and not a transition.
2. Between one third and one half of its sentences carry a number (§C3), and every number has a unit and something it is measured against.
3. Every number in it can be pointed to a frozen view, a design doc or a verified citation — file and line — and it greps with the same value
   wherever else the draft prints it.
4. Every figure it argues from is named in prose in the same or the previous sentence (§F2), and every figure of the section is named somewhere.
5. It contains at most one causal construction ("This is because" / "because" / "so") per measurement.
6. It contains at most one sentence that names or forward-references the system, and that sentence is last (§D1).
7. It contains no question mark, no "clearly / obviously / as expected / interesting to note", no adjective standing in for a number.
8. Its class claim, if any, rests on a second generalizing figure or on a stated mechanism — not on one workload (§F5).
9. Its counter-case, if the data has one, is in the paragraph and not in a footnote (§D3).
10. A reader who stops at the end of the paragraph can state the property in one sentence without using the name of our design.

**I3. Section-level checks (run before the commit).**
- The opening paragraph names each subsection and what it settles (§A1) and names the vehicle, the parameters and the sweep (§A2).
- Subsection order: does it matter → where the time or the capacity goes → why (§A3).
- Each subsection after the first opens on the previous one's finding (§A4).
- The section closes on a named target or a `Summary.` of facts, not on a number and not on the system (§A5).
- Own-system sentences in the whole section ≤ 2 (§D1): grep the system's name macro in the section source, discounting the captions of
  floats that belong to a later section — every prose hit is a paragraph's last sentence or the Summary; a section that passes must not gain one.
- `grep -n '?'` on the section source → 0 non-comment hits;
  `grep -niE "clearly|obviously|as expected|interesting to note|key takeaway|we believe|up to"` on the section source → 0.
- Prose word count 800–1,500 (§A6); the section grows only by replacement while the body is over the page limit.
- The faithful build's page map and body end are reported, and no float moved except by source position.

---

## J. Worked example (SPLEX, ASPLOS submission)

Mapping of the SPLEX §3 (`sections/03-motivation.tex`, as of `26_SPLEX` 4e3fcb5, 2026-09-09) onto the rules above.

| our unit | skeleton | what it must satisfy |
|---|---|---|
| §3 opening ¶ | A1 + A2 | already names the three subsections (`03-motivation.tex:4-13`); the vehicle and the sweep arrive per subsection instead — acceptable because each subsection has a different vehicle, but each must then declare its own (A2) |
| §3.1 *Capped vs. Scales* | **S4** (PVF §2.2) | prior art's shape stated, the condition it fails under, the two rates against the growth term; closes on the inversion, no SPLEX |
| §3.2 *Aggregate Bandwidth* (4 run-in heads) | **S1** per head, with **S6** on the sweep | F1 run-ins already right (the four `\paragraph{}` heads); the sweep's construction must read as calibrated-synthetic (F3) — Figure 3's sweep is a synthetic selection process **calibrated** to V3.2's measured overlap and top-10 % share; h* is a property, not a design target, until §4 |
| §3.2 *HBM is not empty* | **S3** | the f_avail figures are the counter-case to h* = 0.77 and are printed as such — this is the paragraph that keeps §3 honest |
| §3.3 *Hotness within the Hot Set* | **S1** ×3 around Figure 4 | closed to new data; the four `\lead{}` heads sit at `03-motivation.tex:181/203/213/222`; its class claim over three models must be a mechanism claim (F5: the selection is the model's own, the indexer keys and weights are read in full every step — "the other models behave the same" would need the GLM curves in Figure 4), and the GLM statistics stay unprinted with the reason (D6) |
| §3 *Summary.* | A5 + [M]'s two-bullet form in prose | facts only (`03-motivation.tex:229`: capacity → placement → h* → W and K are hot → what the design must reach); the last clause may name what the design must reach — that is the section's single strongest implication (D1) |

Other rules as they landed in SPLEX: D5's external budget is the KV footprint against the 192 GB of HBM and the shard, and the gather rate
against the decode step window. S6's headroom figure is §3.2's sweep — a synthetic ratio sweep calibrated to the measured selection
statistics, whose job is to locate the optimum a placement can reach, not to report a run. G4's float-map note: SPLEX keeps Table 1 in §4
and Table 2 in §5, and a §3 table would also break the float map. §3 sat at the top of the length band with the body over the page limit,
so it grew only by replacement. At 4e3fcb5, §3 had exactly one prose use of `\SYS`, in the Summary, and two in the `fig:overview` caption
that sits in the file for float placement; `grep -n '?' sections/03-motivation.tex` → 0 and the banned-word grep → 0 both passed, and the
guard for questions was `grep -n '?' sections/*.tex main.tex` → 0 (paper HANDOFF, *No questions to the reader*, user 2026-09-04).

## K. Guard classes (run before every commit of a motivation or characterization section)

1. **Own-system cap** — sentences naming or forward-referencing the system ≤ 1 per subsection (last sentence) and ≤ 2 section-wide,
   captions of later sections' floats discounted; grep the name macro in the section source.
2. **No question to the reader** — `grep -n '?'` on the section source → 0 non-comment hits.
3. **Banned words** — `clearly|obviously|as expected|interesting to note|key takeaway|we believe|up to` → 0; ranges print both ends.
4. **Number density** — one sentence in three carries a number (band 1:3 to 1:2); below ≈ 0.30 the section is an essay, above ≈ 0.50 the
   mechanism sentences are gone.
5. **Frozen source** — every number greps, with the same value, in the paper's frozen data views, a design doc or a verified citation, and
   wherever else the draft prints it.
6. **Figures named in prose** — every figure the section owns is named in a sentence that states what it shows.
7. **Shape** — roadmap opening (A1/A2), subsection order does-it-matter → breakdown → why (A3), back-pointer openings (A4), a closing
   `Summary.` of facts (A5).
8. **Length band** — 800–1,500 prose words with the counter named; growth only by replacement while the body is over the page limit.
9. **Build and floats** — the faithful build's page map and body end reported; no float moved except by source position.
