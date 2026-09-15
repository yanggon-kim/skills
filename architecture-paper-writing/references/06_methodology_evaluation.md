Part of the architecture-paper-writing skill. Governs: the methodology and evaluation sections. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

# Methodology / evaluation style guide — the anatomy and diction of the six reference papers' §Method and §Eval

Read in full (`pdftotext`, 2026-09-05, ligatures normalized): **[M]** Mesorasi (MICRO'20, Zhu) §VI Experimental Setup ≈ 850 words /
§VII Evaluation ≈ 2,300 · **[TC]** Tensor Casting (HPCA'21, Rhu) §V Methodology ≈ 805 / §VI ≈ 1,150 · **[SS]** SmartSAGE (ISCA'22, Rhu)
§5 ≈ 373 / §6 ≈ 1,600 · **[PVF]** Low-Latency Proactive Continuous Vision (PACT'20, Zhu) §5 ≈ 900 / §6 ≈ 2,300 · **[LazyDP]**
(ASPLOS'24, Rhu) §6 ≈ 275 / §7 ≈ 1,600 · **[CAL]** Characterization of DL for 3D Point Cloud Analytics (IEEE CAL'21, Rhu) §3 ≈ 397 /
§4 ≈ 1,400. This file governs the methodology and evaluation sections (§5 and §6 in the layout below) only; the abstract is `03_abstract.md`, §1 `04_introduction.md`, §8
`07_conclusion.md`, and the sentence-level contract for every section `01_sentence_style.md` (fact / number / forward
reference; no praise, no suspense, no question). Every rule carries a sentence quoted verbatim from a named paper; each quote was
grepped in the PDF text before it was printed here.

---

## A. Methodology anatomy (275–900 words)

1. **Run-in bold heads in a fixed order — platform → simulator → software → workloads → baselines-and-variants → metrics.** [LazyDP]
   "**System configuration.** … **Software.** … **Benchmarks.**"; [M] "**Hardware Implementation** … **Experimental Methodology** …
   **Software Setup** … **Baseline** … **Variants**"; [TC] "**Evaluation framework.** … **System configuration.** … **Benchmarks.**";
   [SS] "**Hardware/software platform.** … **CSD platform.** … **Comparison to alternative training systems.** … **Dataset.**"
2. **The numbers live in a configuration table; prose carries only the one that matters.** [TC] Table I holds the DRAM rows and the text
   mentions one: "an aggregate of 819.2 GB/sec". [LazyDP] has no table and one dense sentence instead: "a server containing NVIDIA V100
   GPU (32 GB HBM2, 900 GB/sec bandwidth) and Intel Xeon E5-2698v4 CPU (256 GB of DDR4 DRAM, 68 GB/sec bandwidth) connected with
   PCIe 3.0 (16 GB/sec bandwidth)."
3. **Variants are a bullet of bold name + one-line role, or they open §Eval's first paragraph.** [M] "• Mesorasi-SW: delayed-aggregation
   without AU support." / "• Mesorasi-HW: delayed-aggregation with AU support."; [PVF] "FCFS, which improves BO by utilizing all the IP
   blocks available for vision computation but without prediction capabilities. Therefore, comparing PVF with FCFS will show the
   benefits of the proactive execution model." [TC] and [SS] name their design points in §Eval's opening sentence instead.
4. **Validation is one of three moves — measure the hardware, prove functional equivalence, or publish how much the tuned baseline beats
   the public one — never "within x % of hardware" alone.** [M] "We directly measure the GPU execution time as well as the kernel launch
   time."; [TC] "We thoroughly validate the functional equivalence between the baseline gradient expand-coalesce primitive and our
   proposed tensor casted gradient gather-reduce operator."; [TC] "our tuned version of gradient coalesce achieves 5.0 − 6.1× and
   6.7 − 12× higher performance than baseline PyTorch … for a conservative analysis"; [LazyDP] "achieving 13.4× higher performance than
   the built-in PyTorch implementations and reaching 81% of the ideal performance achievable"; [CAL] "8.2× (max 115×) faster than
   publicly available open-source implementation"; [PVF] borrows one: "we use ScaleSim [56], a RTL-validated DNN accelerator simulator".
5. **Every comparison point is forward-tagged to its subsection, so §Eval never re-introduces it.** [SS] "Samsung-Xilinx's SmartSSD [8]
   (Section 6.4)"; [SS] "In Section 6.6, we discuss the sensitivity of SmartSAGE when deviating from these default configurations."
6. **Metrics are defined once, in a subordinate clause.** [M] "We report the standard mean Intersection-over-Unit (mIoU) accuracy metric."
7. **Omissions and scope cuts are announced with their reason.** [LazyDP] "because DP-SGD(F) [13] consistently exhibited higher
   performance than DP-SGD(R) [40], we only show the results using DP-SGD(F) … for brevity"; [CAL] "we do not include the voxel grid
   filter as well as the RANSAC filter as these filters are only optionally included under limited circumstances"; [PVF] exiles the raw
   data: "Appendix B shows the measurement results that we use for parameterizing the simulator."

## B. Evaluation anatomy

1. **A roadmap sentence opens §Eval.** [M] "We first show Mesorasi adds little hardware overhead (Sec. VII-A) … followed by sensitivity
   studies (Sec. VII-F)."; [PVF] "We describe the experimental setup (Sec. 5.1), the baselines (Sec. 5.2), and the evaluation scenarios
   (Sec. 5.3)." (its §Method roadmap, the same device).
2. **Overhead and accuracy come before benefit.** [M] §VII-A Area Overhead → §VII-B Accuracy → §VII-C/D results; [PVF] §6.1 Overheads →
   §6.2 Accuracy Results → §6.3 latency.
3. **One paragraph per figure, one sentence per panel; evaluate the panel that matters.** [PVF] §6.6: "PVF shows the most significant
   energy savings when the front-end dominates … such as the scenario shown in Fig. 10b."
4. **First sentence = claim, figure pointer second** (the Zhu form; the Rhu papers open on the figure — "Figure 18 summarizes the
   effectiveness of SmartSAGE" [SS], "Figure 13 summarizes the end-to-end speedup" [TC] — and keep the verdict for the last sentence). We
   adopt claim-first, consistent with §1–§4: [M] "Mesorasi introduces only minimal area overhead … Fig. 18a and Fig. 18b show the speedup
   and the normalized energy consumption"; [M] "Overall, Mesorasi matches or out-performs the original algorithms."
5. **Numbers as range + average, or "average N× (maximum M×)".** [TC] "2.0 − 15× (average 6.9×) training throughput increase"; [TC]
   "1.1−9.5× latency reduction"; [SS] "an average 10.1× (maximum 12.6×) speedup"; [SS] "an average 4.4× (maximum 5.5×) speedup";
   [LazyDP] "provides 85 − 155× speedup"; [M] "boosts the speedup to 1.9× (up to 3.6×)".
6. **Triple comparisons in one sentence, "respectively".** [PVF] "PVF provides 85.6%, 85.6%, and 92.0% frame latency reduction compared
   to BO, FCFS, and Base, respectively."; [CAL] "53.9/23.6/0.8 frames-per-second for classification/segmentation/detection, respectively".
7. **Causality is one clause after the number, or a "This is because" sentence** (23 uses across the six; [M] 8, [LazyDP] 7, [PVF] 5).
   [M] "DGCNN (s) has the least speedup because it has the least aggregation time (Fig. 12)."; [PVF] "The improvement plateaus as K
   increases to 7. The reason is that by then the saved energy from switching off the front-end is not enough".
8. **Losses in the first clause, reframed in the second — never buried.** [SS] "still incurs an average 60% performance loss vs. the
   DRAM-only design point. Nonetheless, such DRAM-only architecture is an unbuildable, upper bound design point"; [PVF] "the PVF
   achieves only 6.7% further latency reduction over FCFS"; [LazyDP] "Nonetheless, LazyDP still provides significant benefits and
   achieves 16.7× speedup".
9. **Rivals are named and credited before they are beaten.** [SS] "Intel PMEM does much better than the baseline SSD(mmap)"; [LazyDP]
   "LazyDP only incurs 27% to 37% performance overhead over EANA while guaranteeing the same level of privacy".
10. **Paragraphs and subsections close on a verdict, never on a raw number.** [M] "This confirms that the improvements are mainly
    attributed to optimizing the MLPs in feature computation."; [SS] "Overall, the evaluation in this section highlights the effectiveness
    of SmartSAGE's software/hardware co-design"; [TC] "highlighting the robustness of Tensor Casting."
11. **"Note that" carries the fairness caveat.** [TC] "Note that Tensor Casting does not change the algorithmic nature of SGD training".
12. **Captions carry the experimental delta.** [SS] Fig. 16: "Results assume 12 concurrent workers as performance is at its highest with 12
    workers, for both baseline and SmartSAGE."
13. **A no-effect result is one sentence without a figure; an omitted study is announced.** [SS] "Results showed that the chosen
    mini-batch size have little effect on SmartSAGE's achieved speedup."; [SS] "omit the results due to space constraints"; [TC] "We omit
    the results for brevity."; [M] "Due to the page limit".

## C. Diction table (phrase → papers, count across the six papers → house use in §Method/§Eval; the third column's examples are SPLEX's)

| phrase | papers (count) | our use |
|---|---|---|
| "This is because" | [M] 8, [LazyDP] 7, [PVF] 5, [SS] 2, [CAL] 2 | one per paragraph at most; otherwise a "because" clause after the number |
| "Overall," | [PVF] 7, [M] 5, [SS] 4, [LazyDP] 3, [TC] 3, [CAL] 2 | the closing verdict of §6.2 and §6.3 |
| "up to" / "(up to N×)" | [M] 8, [SS] 5, [PVF] 5, [TC] 3 | ranges print both ends instead ("7.8--14.8×") |
| "average N× (maximum M×)" | [SS] 6, [LazyDP] 4, [CAL] 2, [TC] 2 | "1.52--3.68×" ranges over three models — an average would be a new number |
| "compared to" | [PVF] 15, [TC] 8, [SS] 7, [M] 7, [LazyDP] 4 | "against" (the draft's word since §3) |
| "Note that" | [M] 6, [TC] 5, [PVF] 5, [LazyDP] 2, [SS] 1 | the C2C fairness caveat is "even at the optimistic 219 GB/s" |
| "Consequently," / "As a result," | [TC] 7, [SS] 6, [LazyDP] 4, [CAL] 2 / [PVF] 4, [M] 3 | "so" inside the sentence |
| "Specifically," / "In contrast," | [LazyDP] 6, [M] 4, [PVF] 4 / [M] 6, [LazyDP] 3, [PVF] 2 | not needed at 640 words |
| "Nonetheless," | [SS] 3, [LazyDP] 2 | the loss-then-reframe move (PCIe LRU's higher hit ratio) |
| "conservative" | [TC] 4, [LazyDP] 1, [SS] 1, [CAL] 1, [PVF] 1 | "optimistic" on the rival's side instead (C2C at 219 GB/s) |
| "robust / robustness" | [SS] 4, [LazyDP] 3, [TC] 2 | not used (no sensitivity study) |
| "We first …" | [M] 4, [PVF] 2, [LazyDP] 1 | the roadmap sentence uses section numbers instead |
| "demonstrating / highlighting …" (participial closer) | [TC] 4, [LazyDP] 3, [SS] 2, [CAL] 1 | not used — the verdict is a full clause |
| "Figure N shows / summarizes" | [M] 17, [PVF] 14, [TC] 5, [LazyDP] 4 | "Figure N compares", second sentence of each subsection |
| "for brevity" / "due to space constraints" | [LazyDP] 4, [TC] 2, [SS] 1, [PVF] 2, [M] 1 | not needed — nothing is omitted |
| "As expected", "clearly", "obviously", "key takeaway" | 0 / 1 ([M], on a limitation) / 0 / 0 | never |

## D. Tone

Claim, then evidence: the sentence states the result and the number arrives late in it ("provides 85 − 155× speedup, bringing down
private DP-SGD's training time to be on par with the non-private SGD" [LazyDP]). "We" is agentive — "We first show", "We directly
measure", "We omit" — and never "we believe". Numbers are flat; hedging exists only for extrapolation ("We expect the speedup to be even
higher on more powerful mobile GPUs in the future" [M]). Conservatism is stated with a number, never as an adjective alone ("5.0 − 6.1×
… for a conservative analysis" [TC]). Bad news occupies the first clause and the reframing the second ([SS] "60% performance loss …
Nonetheless"). Omission is announced ("we only show the results using DP-SGD(F)" [LazyDP]). Present tense for setup and results, past
for one-time actions ("We evenly split the dataset" [SS]). The rival is named before it is beaten ([SS] Intel PMEM). Every paragraph
ends on what the number means, not on the number. No metaphor, no adverb of degree where the number stands.

## E. Compression habits (how 2,300 words become 640)

One paragraph per figure, one sentence per panel [PVF]; range + average instead of a per-benchmark list [TC]; the caption carries the
setup delta, so the prose does not [SS Fig. 16]; one causal clause per number [M]; small topics merged under run-in heads inside one
subsection ([TC] §VI-C "Design overheads. / Energy-efficiency. / NMP utilization."; [PVF] §6.1 four one-sentence overheads); the
configuration in the table and one number in prose [TC]; a no-effect result in one sentence [SS]; "we omit … for brevity" [TC];
forward-tags in §Method so §Eval never re-introduces a baseline [SS]; overhead / accuracy first, so the benefit paragraphs stay pure
[M, PVF].

## F. Never-list (0 occurrences in the six §Method/§Eval sections)

No re-motivation (the closest is a back-pointer, "As discussed in Section III-A"). No metric defined twice. No future work in §Eval ([M]'s
sits in §V, [PVF]'s in §7). No mechanism restated — §Eval names only the knob ("bank conflict", "coalescing granularity"). No number
without a comparison anchor (× vs., % of, normalized to). No losing panel hidden ([PVF] "only 6.7%"; [SS] "60% performance loss"). No
bulleted results (bullets appear only in §Method for baselines / variants / scenarios). No subsection ending on a raw number. No
"As expected" / "obviously" / "clearly" as evidence.

## G. Worked example (SPLEX, ASPLOS submission)

Mapping of the SPLEX §5 / §6 (`sections/05-methodology.tex`, `06-evaluation.tex`, 2026-09-05) onto the moves above. B2 applied: §6.1
Accuracy Validation came before §6.2/§6.3. §5 ran ≈ 190 words plus Table 1; §6 ≈ 640 words.

| our unit | reference move | what it holds |
|---|---|---|
| §5 **System configuration.** | A1, A2 | Table 1 named once; the one prose fact: weights + keys pinned so f_avail is equal across tiers; the key-layer spill rule |
| §5 **Simulators.** | A4 | Ramulator 2.0 + base die (one-stack rates, BW_eff, hit, swap); policy simulator on captured selections; LLMServingSim 2.0 from measured vLLM profiles with the two receipts (decode ratios within 3 %, mixer within 0.1 %); energy as ratios |
| §5 **Software and workloads.** | A1, A7 | vLLM 0.28.0 on the 8×B200 node, the indexer hook, 2,048-step decodes at 64K / 128K; SGLang 0.5.18 ran HiSparse as the host-tier check; InfiniteBench 32K–128K |
| §5 **Baselines and metrics.** | A3, A5, A6 | the five placements forward-tagged to §6.2, the node comparison to §6.3; Δ perplexity vs the two-run noise floor, TPOT at equal per-GPU batch, cluster tokens/s, SLO goodput (highest throughput at or below the SLO's TPOT), energy per token at equal throughput — each defined once |
| §6 roadmap | B1 | the three subsections in one sentence |
| §6.1 | B2, B4, B10 | claim (algorithmically equivalent) → Table 3 bounds it (32 of 33, 33 CIs, †, 0.21 %) → verdict (summation-order noise) |
| §6.2 | B4, B5, B7, B8, B9, B10 | claim + Figure 8; *Against host offload* / *Against PCIe LRU* / *Against blind interleave* / *Against the oracle*; ranges per model; one cause per number; LRU's higher hit ratio first, its traffic second; "Overall," close |
| §6.3 | B4, B7, B10 | claim + Figure 9 setup in one sentence; *Max batch* / *SLO-constrained goodput* / *Iso-throughput energy*; no metric redefinition; "Overall," close |

The SPLEX guards, as run before every commit: §5 ≤ 200 and §6 ≤ 660 prose words (`wc_prose.py`: floats and comments stripped, macros
removed, punctuation-only tokens dropped) · the must-keep list of the plan greps with the same value · no new number · every `\ref` /
`\cite` of the previous text present · `grep -c "highest throughput at or below"` = 1 (§5 only) · no "As expected" / "clearly" /
"obviously" / "key takeaway" · no `\begin{itemize}` in §6 · the first sentence of each subsection is a claim and its second names the
figure or table · each subsection's last sentence is a verdict, not a number · terminology per the paper HANDOFF ("HBM-only", "PCIe LRU
(HiSparse)", "infinite-HBM oracle", equal room in words) · the sentence test of `01_sentence_style.md` on every sentence.

## H. Guard classes (run before every commit of a methodology or evaluation section)

1. **Word budget per section, with the counter named** — floats and comments stripped, macros removed, punctuation-only tokens dropped;
   a count without its counter is not comparable.
2. **Must-keep grep** — one regex per fact of the plan; every fact greps with the same value after the pass.
3. **No new number** — the numeric-token multiset of the section is unchanged unless the plan names the change.
4. **Cross-references preserved** — every `\ref` / `\cite` of the previous text is present.
5. **Each metric defined exactly once** — grep the defining phrase; count = 1, and it sits in §Method.
6. **Banned evidence words** — "As expected", "clearly", "obviously", "key takeaway" → 0.
7. **No bulleted results** — no `\begin{itemize}` in §Eval (bullets live in §Method for baselines / variants / scenarios only).
8. **Subsection shape** — the first sentence of each subsection is a claim, its second names the figure or table; the last sentence is a
   verdict, not a number.
9. **Terminology** — baseline and variant names per the paper's vocabulary list, the same words in §Method, §Eval, captions and the abstract.
10. **The sentence test** of `01_sentence_style.md` on every sentence.
