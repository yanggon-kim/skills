# The six reference papers — what each is the reference for, and where to open it

Part of the architecture-paper-writing skill. The guides `references/00`–`09` quote these six papers by tag; this
index says what each paper is cited *for*, which guides cite it, and the printed page range of every section, so a
reader opens the right pages instead of scanning.

## The page-number trap (read before citing any page)

**Rule: a page's printed number is a boundary marker in `pdftotext` output, and which boundary depends on the
venue's layout.** Five of the six — [M], [TC], [SS], [PVF], [LazyDP] — are proceedings papers that print the page
number in the **footer**, so in `pdftotext` (with or without `-layout`) the number marker **terminates** the page
it belongs to: the text *above* the marker is that page. IEEE CAL ([CAL]) prints the page number in the
**header**, so its marker **starts** the page: the text *below* the marker is that page. Reading one convention
as the other puts every page citation off by one — it happened once in these guides, and the fix cost a full
re-read. That is why the guides cite **per-section page ranges** rather than single pages, and why the ranges
below were computed by splitting the text on form feeds (one per PDF page) and reading the marker under the
rule above, never by searching for the number in the text.

The PDF-page → printed-page offset of each file: [M] +1036 · [TC] +234 · [SS] +931 · [PVF] +328 · [CAL] +105 ·
[LazyDP] +615 (PDF page 1 of `mesorasi-micro20.pdf` is printed page 1037, and so on).

---

## [M] `mesorasi-micro20.pdf`

- **Mesorasi: Architecture Support for Point Cloud Analytics via Delayed-Aggregation.** Yu Feng, Boyuan Tian,
  Tiancheng Xu, Paul Whatmough, Yuhao Zhu. MICRO 2020, pp. 1037–1050 (14 pages, 564 KB). Footer page numbers.
- **The reference for:** the top-down walk-through move (a design section that walks its own figure entry by
  entry); the closing `Summary.` practice at the end of a motivation section, chosen over italic takeaways; the
  variant-naming form (`Mesorasi-SW` / `Mesorasi-HW`, bold name + one-line role); and the highest "Figure N
  shows" density of the six (17 in §Eval) — the model for figure-anchored evaluation prose.
- **Cited by guides:** 02, 03, 04, 05, 06, 07, 09.

| section | printed pages |
|---|---|
| Abstract | 1037 |
| §I Introduction | 1037–1038 |
| §II Background | 1038 |
| §III Motivation (III-A architecture 1038; III-B Performance Characterizations 1039–1041; *Summary* 1041) | 1038–1041 |
| §IV Delayed-Aggregation Algorithm (IV-C Bottleneck Analysis 1042–1043) — the design, part 1 | 1041–1043 |
| §V Architectural Support (V-A Overall Design 1043) — the design, part 2 | 1043–1045 |
| §VI Experimental Setup | 1045–1046 |
| §VII Evaluation (VII-A Area 1046 · VII-B Accuracy 1046 · VII-C GPU 1046–1047 · VII-D Speedup/Energy 1047–1048 · VII-E NSE 1048 · VII-F Sensitivity 1048) | 1046–1048 |
| §VIII Related Work | 1048–1049 |
| §IX Conclusion | 1049 |
| References | 1049–1050 |

## [TC] `tensor-casting-hpca21.pdf`

- **Tensor Casting: Co-Designing Algorithm-Architecture for Personalized Recommendation Training.** Youngeun
  Kwon, Yunjae Lee, Minsoo Rhu. HPCA 2021, pp. 235–248 (14 pages, 1.3 MB). Footer page numbers.
- **The reference for:** the driving-example framing (one concrete example carried from background through
  design); the "the unique contribution of our study is" conclusion precedent; "first" said exactly once
  ("To the best of our knowledge, Tensor Casting is the first that …"); and the abstract's diction.
- **Cited by guides:** 02, 03, 04, 05, 06, 07, 09.

| section | printed pages |
|---|---|
| Abstract | 235 |
| §I Introduction | 235–236 |
| §II Background and Related Work (II-D Related Work 238) | 236–239 |
| §III Workload Characterization (III-A breakdown 239; III-B the isolated primitive 239–240) | 239–240 |
| §IV Tensor Casting — the design (IV-B Software Runtime 241; IV-C Architecture 242) | 240–244 |
| §V Methodology | 244–245 |
| §VI Evaluation (VI-A Latency Breakdown 245 · VI-B System-level 245 · VI-C Overheads/Energy/NMP 246 · VI-D Sensitivity 247) | 245–247 |
| §VII Conclusion | 247 |
| References | 247–248 |

## [SS] `smartsage-isca22.pdf`

- **SmartSAGE: Training Large-scale Graph Neural Networks using In-Storage Processing Architectures.** Yunjae
  Lee, Jinha Chung, Minsoo Rhu. ISCA 2022, pp. 932–945 (14 pages, 952 KB). Footer page numbers.
- **The reference for:** the key-intuition-figure move (one figure that carries the idea before the mechanism);
  the design-points / variants bullet list in §Methodology; the "Figure N summarizes" evaluation openers; and the
  "average N (maximum M)" result form — which the house rules override (print both ends of the range instead).
- **Cited by guides:** 02, 03, 04, 05, 06, 07, 09.

| section | printed pages |
|---|---|
| Abstract | 932 |
| §1 Introduction | 932–933 |
| §2 Background | 933–935 |
| §3 Motivation and Characterization (3.1 Motivation 935; 3.2 In-memory 935; 3.3 SSD-centric 936) | 935–936 |
| §4 SmartSAGE Architecture — the design (4.1 Overview 936; 4.2 In-storage acceleration 937; 4.3 Runtime and host 938) | 936–939 |
| §5 Methodology | 939–940 |
| §6 Evaluation (6.3 End-to-end 941 · 6.4 vs FPGA CSDs 941 · 6.6 Sensitivity 942) | 940–942 |
| §7 Related Work | 942–943 |
| §8 Conclusion | 943 |
| References | 943–945 |

## [PVF] `low-latency-proactive-vision-pact20.pdf`

- **Low-Latency Proactive Continuous Vision.** Yiming Gan, Yuxian Qiu, Lele Chen, Jingwen Leng, Yuhao Zhu.
  PACT 2020, pp. 329–342 (14 pages, 2.2 MB). Footer page numbers.
- **The reference for:** the claim-first-then-figure evaluation form (the sentence states the result, the figure
  pointer comes second); judging a number against a cited external budget instead of an adverb (the 100 ms
  autonomous-vehicle and AR budgets); the prior-art-shape motivation skeleton (what prior work optimizes, when it
  stops working, the rival's best case printed first); and "This paper argues that".
- **Cited by guides:** 02, 03, 04, 05, 06, 07, 09.

| section | printed pages |
|---|---|
| Abstract | 329 |
| §1 Introduction | 329–330 |
| §2 Background and Motivation (2.1 Latency Bottleneck 330; 2.2 Limitations of Optimizing Only Vision Algorithms 331) | 330–331 |
| §3 Proactive Vision Execution Model — the design, part 1 | 331–333 |
| §4 PVF framework — the design, part 2 (4.2 Accuracy Control 333; 4.3 Runtime Scheduling 334) | 333–335 |
| §5 Experimental Methodology (5.2 Baselines 335; 5.3 Scenarios 336) | 335–336 |
| §6 Evaluation (6.1 Overheads 336 · 6.2 Accuracy 336 · 6.3/6.4 Latency 337 · 6.5 Mixed, 6.6 Energy, 6.7 Lower resolution, 6.8 Sensitivity 338) | 336–339 |
| §7 Limitation and Discussion | 339 |
| §8 Related Work | 339 |
| §9 Conclusion | 339 |
| Appendix A (latency derivation), Appendix B (measurements) | 340 |
| References | 340–342 |

## [CAL] `characterization-3d-point-cloud-cal21.pdf`

- **Characterization and Analysis of Deep Learning for 3D Point Cloud Analytics.** Bongjoon Hyun, Jiwon Lee,
  Minsoo Rhu. IEEE Computer Architecture Letters 20(2), 2021, pp. 106–109 (4 pages, 888 KB). **Header** page
  numbers — the one exception to the footer rule.
- **The reference for:** the archetype of a characterization section — four pages that are nothing but
  characterization (accuracy → latency breakdown → compute and memory efficiency); its workload table sits in
  §Methodology, which is why the house rule says "no table in a characterization section". **Excluded from the
  design guide** (it has no design section).
- **Cited by guides:** 02, 03, 04, 06, 07, 09 (not 05).

| section | printed pages |
|---|---|
| Abstract | 106 |
| §1 Introduction | 106 |
| §2 Background and Motivation (2.2 Key Challenges and Motivation 106–107) | 106–107 |
| §3 Methodology (Table 1, the workload table) | 107 |
| §4 Characterization (4.1 Effect of Noise on Accuracy 107; 4.2 Latency Breakdown 108; 4.3 Compute and Memory Efficiency 108–109) | 107–109 |
| §5 Future Directions | 109 |
| §6 Conclusion (printed "Conclussion") | 109 |
| References | 109 |

## [LazyDP] `lazydp-asplos24.pdf`

- **LazyDP: Co-Designing Algorithm-Software for Scalable Training of Differentially Private Recommendation
  Models.** Juntaek Lim, Youngeun Kwon, Ranggi Hwang, Kiwan Maeng, G. Edward Suh, Minsoo Rhu. ASPLOS 2024,
  pp. 616–630 (15 pages, 2.3 MB). Footer page numbers.
- **The reference for:** the single source of the figure / colour system (Fig. 9(b), p. 625: two arrow classes
  plus circled step numbers; Fig. 11, p. 626: the blue); the most-cited paper for breakdown-paragraph skeletons
  (§4.1–4.3); and the source of two practices the house rules reject — questions to the reader (§4.3) and the
  italic "Key takeaways:" lines after each characterization subsection.
- **Cited by guides:** 02, 03, 04, 05, 06, 07, 09.

| section | printed pages |
|---|---|
| Abstract | 616 |
| §1 Introduction | 616–617 |
| §2 Background (2.4 SGD vs DP-SGD 618; 2.5 Related Work 619) | 617–619 |
| §3 Threat Model | 619–620 |
| §4 Workload Characterization (4.1 Breakdown 620; 4.2 Model Update Stage 621; 4.3 Root-causing 621–622; "Key takeaways:" at 621, 621, 622) | 620–622 |
| §5 LazyDP — the design (5.1 Principles 622; 5.2 Implementation 623; 5.3 Software Architecture, Fig. 9, 625) | 622–625 |
| §6 Methodology | 625–626 |
| §7 Evaluation (7.1 Performance and Energy, Fig. 11, 626; 7.2 Overhead 626; 7.3 Sensitivity 627) | 626–628 |
| §8 Conclusion | 628 |
| References | 628–630 |

---

## Recomputing a range

```
pdftotext -layout references/papers/<file>.pdf - | python3 - <<'EOF'
import sys, re
pages = sys.stdin.read().split('\f')          # one entry per PDF page
for i, p in enumerate(pages, 1):
    ne = [l.strip() for l in p.split('\n') if l.strip()]
    if ne: print(i, 'first:', ne[0][:40], '| last:', ne[-1][:40])
EOF
```

Footer venues: the printed number is the *last* line of the page's entry (or just above the licence stamp);
header venue ([CAL]): it is the *first*. Add the offset above to a PDF page index to get the printed page.
