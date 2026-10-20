# P3-LLM lab deck: fact audit against the paper

*Deck: `assets/reference/p3llm-intro.pptx` (60 slides, built by `examples/p3llm/build_p3llm_deck.js`). Paper: Y. Chen
et al., "P3-LLM", arXiv 2511.06838v4 (3 May 2026), read from the PDF (text extracted with `pdftotext -layout`; Figs. 1,
2, 4, 6, 7, 9, 10, 11, 12, 15 checked on page renders; §II, the Background part, read in full) and the author's reading
notes. The Preliminary Note (slides 4–25, the presenter's DRAM primer, not the paper) is checked against the author's
earlier DRAM explainer page (Fig. B1–B3, Tables B1–B2) and the simulator's LPDDR5 AiM timing preset (read at its
0.625 ns cycle [A0]), not against the paper or JEDEC. [A0], [A1] are that project's tagged assumptions; [BRAINSTORM]
is this deck's tag for the author's own reading.*

Status: **ok** = matches the paper · **fixed** = was wrong or not the paper's claim, corrected in the builder (old
→ new) · **our reading [BRAINSTORM]** = our inference or depiction, flagged as such on the slide or in the notes ·
**preliminary** = the Preliminary Note (the presenter's DRAM primer), checked against DRAM explainer and our presets, not
the paper. "N" = speaker notes,
"F" = figure, "B" = band bullet, "T" = title.

| slide | claim | paper location | status |
|---|---|---|---|
| 1 | Title, seven authors, Cornell / KU Leuven / Stanford, arXiv 2511.06838v4, 2026 (N: May 2026) | p. 1 header, arXiv stamp "3 May 2026" | ok |
| 1 | N: the question is fast PIM decoding at batch > 1 on the edge | §I ¶2–3 (low-batch edge, GQA, arithmetic intensity > 1) | ok |
| 1 | N: a short preliminary note on DRAM follows the summary; it is the presenter's addition, not part of the paper; its DRAM sizes and timings are simulator presets | (deck structure) | ok |
| 2 | Outline: seven parts, Summary (highlighted: slide 2 also opens part 1), Preliminary Note (optional, the presenter's DRAM primer, not the paper), Background (the paper's §II) … Discussion; dividers say "part k of 7" | (deck structure) | ok |
| 3 | B: decoding waits on DRAM; FP16 PIM loses its gain as batch or GQA group nears 4 | §III-B ("benefits … gradually disappear as BS and G approach 4") | fixed (was "hit their compute roof already at batch 2–4", not the paper's statement) |
| 3 | F: host NPU does FP16/FP32 work (LayerNorm, RoPE, softmax, scales); even/odd bank share a PCU; 4-bit W, KV from banks; 8-bit A, P from the NPU; 32-bit sums back | Fig. 6(a, b); §V-A ("16 32-bit outputs") | ok |
| 3 | 4.9× speed vs HBM-PIM; 7.8× NPU; 2.0× Ecco | §VI-C Speedup, Fig. 9 | ok |
| 3 | 3.5× energy efficiency vs HBM-PIM; 6.3× NPU; 2.1× Ecco | §VI-C Energy, Fig. 10 | ok |
| 3 | 17.5 % HBM area overhead vs 16.4 % for HBM-PIM | Table VII | ok |
| 3 | 0.25 mean Wikitext ppl loss; QuaRot and QoQ 0.30 | Table IV, Mean Δppl column | ok |
| 3 | N: three badges = three parts: W4A8KV4P8 formats, every operand in 4 or 8 bits, a format per operand (§IV); low-precision PCU + TEP, run twice per weight read (§V-A, §V-D); fused dequantization, the work hidden on the NPU (§V-C) (moved from slide 1, whose key points were removed: the title slide carries none) | §I contributions; §IV; §V-A, §V-C, §V-D | ok |
| 3 | N: "the four numbers on the right" | (layout) | fixed (notes said "at the bottom"; the numbers sit on the right) |
| 4 | Divider of part 2, the Preliminary Note: the presenter's addition, not the paper's; sources our DRAM explainer and one simulator preset (LPDDR5-6400 AiM, Ramulator 2.0), not JEDEC | DRAM explainer §dram intro | preliminary |
| 4–25 | Every Preliminary Note slide (divider included) carries the tag "Preliminary note · presenter's primer, not the paper" above its title; slide 25 N closes the note | (deck structure) | ok |
| 5 | Channel = own command + data bus; 4 bank groups × 4 banks = 16 banks | DRAM explainer Table B1 (mobile: 4 × 4 = 16 per channel) | preliminary |
| 5 | A bank holds one open row; ACT copies a row of 2,048 B; RD moves one 32 B column | DRAM explainer Table B1 (row 2,048 B, column access 32 B); preset org 1<<10 columns × 16 bit | preliminary |
| 5 | Banks of a bank group share one I/O path | DRAM explainer §dram ("banks of one bank group share column circuitry") | preliminary |
| 6–10 | ACT raises one wordline, sense amps copy the row; RD moves one column CL later; second RD needs no new ACT; PRE closes, next ACT waits tRP | DRAM explainer Fig. B1 / "Reading one column" | preliminary |
| 11 | tRCD = 9.375 ns | preset nRCD 15 × 0.625 ns | preliminary |
| 12 | tRRD = 2.5 ns | preset nRRD 4 × 0.625 ns | preliminary |
| 13 | CL = 12.5 ns, burst 2.5 ns, RL = 15 ns | preset nCL 20, nBL 4 (× 0.625 ns) | preliminary |
| 14 | Same-group second read waits tCCD_L = 5 ns | DRAM explainer Table B1: tCCD_L 5 ns "set as the MAC column [A1]" (the simulator spaces ordinary reads at tCCD_S) | preliminary (N of slide 17 now says 5 ns is the simulator's MAC-command spacing, not a JEDEC value) |
| 15 | Other-group read waits tCCD_S = 2.5 ns; bursts back to back | preset nCCD 4 × 0.625 ns | preliminary |
| 16 | tRAS = 21.25 ns; tRP = 9.375 ns | preset nRAS 34, nRPpb 15 (× 0.625 ns) | preliminary |
| 11–16 | F: one "timings: simulator preset" mark in the figure legend | (brief: one compact mark allowed where DRAM timings show) | preliminary |
| 17 | (a) same group tCCD_L 5 ns, bus gap; (b) other group tCCD_S 2.5 ns, bursts touch; "simulator preset" mark | DRAM explainer Fig. B2, Table B1 | preliminary |
| 17 | B: in HBM, tCCD_S is about half of tCCD_L (§V-D) | §V-D ("typically a half of tCCD_L across all HBM generations") | ok |
| 17 | N: "these two values are our simulator preset" | DRAM explainer Table B1 | fixed (2.5 ns is the preset's tCCD_S; 5 ns is the MAC-command spacing [A1]) |
| 18–24 | Stock AiM run: WRGB (one 32 B burst into the GB), WRMAC16 (bias or zero), TMOD, PREA + ACT16 (same row in all 16 banks), c × MAC16 tCCD_L apart, TMOD, RDMAC16 | DRAM explainer Fig. B3, Table B2 (128 WRGB per input vector, 2.5 ns apart; TMOD 2.02 per run; 64 MAC16 per row, 5 ns) | preliminary |
| 25 | Table: only WRGB, WRMAC16, RDMAC16 use the data bus; TMOD twice per run | DRAM explainer Table B2 ("register commands"; TMOD 2.02 per run) | preliminary |
| 25 | B: every MAC16 touches all four bank groups, so MAC16s go tCCD_L apart | DRAM explainer "The stock AiM MAC pass" | preliminary |
| 25 | N: HBM-PIM likewise issues one PIM command per tCCD_L | §V-D ("a PIM command is initiated every tCCD_L on HBM-PIM") | ok |
| 26 | Divider of part 3, Background = the paper's §II in its order: §II-A LLM architecture and GQA, §II-B PIM for LLM acceleration (HBM-PIM, AiM), §II-C LLM quantization | §II headings A–C | ok |
| 27 | F/N: prefill: the N_T-token prompt → embedding table (N_VOC × H) → L decoder layers → LM head → first output token | §II-A ¶1; Fig. 1(a) | ok |
| 27 | T/B/N: decoding takes the output token as the next input and repeats the same operations, one token per step (auto-regressive) | §II-A ¶1 | ok |
| 27 | F/N: decoder layer = self-attention + MLP; W_Q, W_K, W_V; RoPE after W_Q and W_K in recent LLMs; per head Q·Kᵀ, softmax → P, P·V; W_O; MLP W_gate, W_up, W_down | §II-A ¶2–3; Fig. 1(a) | ok |
| 27 | B/F/N: the new key (after RoPE) and value are cached in off-chip memory: the KV-cache, read by Q·Kᵀ and P·V | §II-A ¶2; Fig. 1(a) (KV$ fed by K after RoPE and by V) | fixed (first draft drew both K and V straight from the projections; K now leaves RoPE) |
| 27 | F: layer norms, residual adds and the MLP's activation left out; "black outline = holds weights" | Fig. 1(a) | our reading [BRAINSTORM] (simplified depiction; N caption says what is left out) |
| 28 | B/N: the KV-cache is stored for every token, so it becomes significant at long context | §II-A ¶4 | ok |
| 28 | N: queries split into N_A heads, keys and values into N_KV heads; MHA has N_A = N_KV | §II-A ¶2, ¶4; Fig. 1(b) | ok |
| 28 | T/B/F: GQA with G = N_A / N_KV shrinks the KV-cache G×; example 8 query and 4 KV heads, G = 2 | §II-A ¶4; Fig. 1(b) | ok (the paper words it as G groups of query heads sharing KV vectors; the slide says G query heads per KV head, as Fig. 1(b) draws it; both give N_KV = N_A / G; N gives both) |
| 28 | N: GQA models have arithmetic intensity above one during decoding | §I ¶1 | fixed (draft added a reason clause, "because each key read serves several heads", not in the paper; removed) |
| 29 | B/N: PIM accelerates decoding with the DRAM's higher internal bandwidth for memory-bound operations; two commercial devices, Samsung HBM-PIM and SK hynix AiM | §II-B ¶1 (and §I: decoding is memory-intensive GEMV) | ok |
| 29 | F/N: one PIM channel = 16 banks in 4 bank groups, a PCU near each bank, peripheral and global buffer between; two banks may share a PCU | §II-B ¶1; Fig. 2 | ok |
| 29 | B/F/N: banks send weights / KV-cache to the PCU 256 bits (16 × 16-bit) per access; input to the PCU register file (HBM-PIM) or the global buffer (AiM) | §II-B ¶1 | ok |
| 29 | F/N: HBM-PIM PCU = 16-way SIMD MAC, FP16 multipliers, FP32 accumulators, input reuse (one input × 16 weights); AiM PCU = BF16 multipliers and an adder tree, output reuse | §II-B ¶2; Fig. 2 | ok (AiM's FP32 accumulator, drawn in Fig. 2, is left out of our figure) |
| 29 | T/B/N: high-precision PCUs take 20–27 % of the DRAM die (~10× lower transistor density, fewer metal layers); PIM gains mainly at batch 1 and MHA, which have no data reuse | §II-B ¶2 | ok (moved here from the motivation slide, where it duplicated §II-B) |
| 29 | N: P3-LLM's base pairs an even and an odd bank on one PCU, 8 PCUs per channel | §V-A ("One PIM channel contains 8 PCUs, each … shared by 2 banks") | ok (carried over from the removed bridge slide) |
| 29 | (layout) the bridge slide "P3-LLM builds on HBM-PIM: one PCU per bank pair" (redrawn from Fig. 2 + Fig. 6(a)) is replaced by this redraw of Fig. 2 alone, in Background | §II-B | fixed (the paper's Fig. 2 belongs to its §II-B, not to the presenter's primer) |
| 30 | F/B/N: Eq. 1: Δ = \|X\|max / Q_max; X_Q = Round(X / Δ, Q), Round = closest value of the set Q; X̃ = X_Q · Δ; rounding leaves an error | §II-C, Eq. 1 | ok |
| 30 | F: the largest \|X\| maps to ±Q_max | follows from Eq. 1 | ok |
| 30 | F/N: example Q = integers −7 … 7, eight illustrative values | — | our reading [BRAINSTORM] (caption and N: "my own example, not the paper's") |
| 30 | B/N: weight-only and KV-cache-only methods near-lossless at 4 bits; weight-activation quantization explored for further savings | §II-C ¶2 | ok |
| 30 | B/N: custom formats adapt better to LLM tensor distributions; NVIDIA and AMD support FP8-E4M3 and FP8-E5M2 | §II-C ¶2 | ok |
| 32 | B/N: the NPU stays memory-bound even at batch ≥ 16 | §III-B | ok (replaces the §II-B area bullet, now on slide 29) |
| 32 | T/B: FP16 PIM's gain fades as batch or GQA group nears 4 | §III-B | fixed (title was "hits its compute roof at batch 2–4 or with GQA") |
| 32 | HBM-PIM roof 1.23 TOPS, bandwidth 1.23 TB/s; NPU 307 GB/s; P3-LLM roof 9.84 TOPS | Fig. 4 labels | ok |
| 32 | 4× the multipliers (iso compute area) at 2× the clock = 8× roof | §III-B ("4× PCUs under iso-compute-area … 2× higher operating frequency … 8× higher throughput") | ok |
| 32 | F: operator guides MHA BS1, GQA G4 BS4, GQA G8 BS8 at x = 1, 4, 8, dots on the HBM-PIM roof | Fig. 4 (paper marks MHA/BS1 and G4/BS4 on HBM-PIM, G8/BS8 on the NPU line, and P3-LLM's MHA/BS1 at x = 4) | our reading [BRAINSTORM] (x positions from Fig. 4; caption and N say "approximate") |
| 32 | F: axes 0–35 OP/byte, 0–10 TOPS (paper 0–11) | Fig. 4 | ok (range trimmed, shape kept) |
| 33 | Weights dominate memory at batch 1; KV-cache grows with batch (4K, batch 1–8, four models) | §III-A, Fig. 3(a) | ok |
| 33 | Activations and scores are the most quantization-sensitive; W and KV acceptable down to 4 bits (C4 ppl, one operand at a time) | §III-A, Fig. 3(b) | ok |
| 33 | Scores quantized so P·V runs on the low-precision PCU | §III-A ("allowing the P·V operation … to run on low-precision compute units") | ok |
| 33 | F: quadrant positions of the four operands | after Fig. 3 | our reading [BRAINSTORM] (schematic; N says so) |
| 34 | Table I rows: BitMoD W4A16KV16 M/H/M; Oaken W16A16KV4 M/H/L; MANT W4A8KV4 H/M/M; Ecco W4A8KV4 H/H/L; Pimba W16A16KV8 L/H/M; P3-LLM W4A8KV4P8 H/H/H | Table I | ok |
| 34 | Notes in cells: Ecco decompresses to FP16; Pimba leaves linear layers unquantized | §III-C | ok |
| 34 | B: plain-integer W4A8KV4P8 loses too much perplexity → one format per operand | §III-A, Fig. 3(b) | ok (citation narrowed §III → §III-A) |
| 36 | Key cache has fixed outlier channels, value cache none | §IV-A, Fig. 5 | ok |
| 36 | Each key channel divided by its prefill absolute maximum (Eq. 2); factors reused in decoding | §IV-A, Eq. 2 | ok |
| 36 | No calibration set; factors < 1 % of memory; < 5 ms for Llama-3.1-8B at 32K on an A6000 (N) | §IV-A | ok |
| 36 | 128 values share a 16-bit scale and 4-bit zero point → 4.16 bits; Oaken ~4.8 bits | §VI-B Perplexity Results | ok |
| 36 | N: pre-RoPE for Llama-1/2, post-RoPE for Llama-3 and Mistral, "because their outlier channels survive RoPE" | §IV-A (reason shown for Llama-3: 128K max length, small angles at 4K), §VI-A | fixed (the reason is the paper's for Llama-3 only; Mistral's choice is stated, not explained) |
| 36 | F: "2 outlier channels", bar heights | after Fig. 5 | our reading [BRAINSTORM] (schematic; N says so) |
| 37 | Scores in [0, 1]: no sign bit needed | §IV-B | ok |
| 37 | FP16 exponents below 1 span [−14, −1], 14 values; 4-bit exponent, bias −15 | §IV-B | ok |
| 37 | No scale: round the FP16 score, keep its top 4 mantissa bits | §V-C Quantization Granularity | ok |
| 37 | Llama-3.1-8B Wikitext: FP16 5.95, S0E4M4 5.95, E4M3 5.99 (N), INT8 6.06 | Table II | ok |
| 37 | F: FP16 = s + 5e + 10m; FP8-E4M3 = s + 4e + 3m; FP8-S0E4M4 = 4e + 4m | §II-C, §IV-B | ok |
| 37 | N: scores share the activations' PCU input, and INT8 is poor for activations | §IV-B ("attention-scores behave the same as activations during the MAC operation") | ok |
| 38 | FP4 values {±0, ±0.5, ±1, ±1.5, ±2, ±3, ±4, ±6}: 16 codes, 15 values | §IV-C | ok |
| 38 | BitMoD maps −0 to one of {±5, ±8}, chosen per weight group | §IV-C | ok |
| 38 | Group of 128 weights | §V-C ("per-group with a group size of 128 following BitMoD") | fixed (citation: §IV-C → §IV-C, §V-C) |
| 38 | One decoder for BitMoD and INT4-Asym (shared operand) | §IV-C, §V-A | ok |
| 38 | N: BitMoD by the same first author; recovers 0.01 / 0.07 ppl; smoothing 0.10 / 0.17 | ref. [6]; Table VI | ok |
| 39 | Hadamard rotation (QuaRot, SpinQuant) costs run time; SmoothQuant migrates difficulty into weights | §IV-D | ok |
| 39 | Per-token FP8-E4M3; beats INT8-SQ with 4-bit weights on all four models | §IV-D, §V-C, Table III | ok |
| 39 | F: Wikitext ppl 2-7B 5.12 / 5.24 / 5.37; 2-13B 4.57 / 4.66 / 4.76; 3.1-8B 5.84 / 6.16 / 6.36; 3.2-3B 7.28 / 7.64 / 7.87 (FP16 / W4+FP8 / W4+INT8-SQ), 4K | Table III | ok |
| 40 | 256-bit column = 64 four-bit values → 64 multipliers, 4× HBM-PIM's 16 | §V-A | ok |
| 40 | 16 outputs kept, input widened to 4: a 1×4×16 tile (HBM-PIM 1×1×16) | §V-A, footnote 2 | ok |
| 40 | F: input register 4 × FP8; decoder BitMoD / INT4-Asym → 6 bit; 6b×6b multipliers; shift by input exponent; 4:2 compressor; 32-bit accumulator | §V-A; Fig. 6(a) (widths 6, 12, 26, 28, 32) | ok |
| 40 | 4 MACs/cycle at 1.08× the area of the FP16 PE | Table VIII (normalized to 4-bit weights) | ok |
| 41–46 | tCCD_L = 4, tCCD_S = 2 DRAM clocks | §V-D ("4 memory bus cycles"), §VI-A (tCCD_S of HBM2 = 2 clocks) | ok |
| 41–46 | Inputs written first; HBM-PIM command at t = 1, W1×A1 fills tCCD_L; P3-LLM W1×A1 in one tCCD_S, second command at t = 3 for W1×B1; weight 2 from t = 5 | Fig. 7 (page render) | ok |
| 41–46 | One PIM command per input vector (N, slide 40) | Fig. 7: C/A bus commands at t = 1, 3, 5, 7 | ok |
| 46 | Batch 1: second slot idle, TEP gains nothing | (not in the paper) | our reading [BRAINSTORM] (frame marked "our addition" in N) |
| 46 | N: hence the speedup peaks at batch 2 | §VI-C ("highest speedup at a batch size of 2, owing to its TEP") | ok |
| 47 | +28 % PIM power at tCCD_S; 1.56× energy efficiency | §V-D | ok |
| 47 | 1.6× from TEP over W4A8KV4, batch 2 and 4 | §VI-C Architecture Ablation, Fig. 15 | ok |
| 47 | Power dominated by cell access and column decoding; weights reused across two tCCD_S windows | §V-D | ok |
| 47 | n×4×16 needs n× multipliers; n×4×(16/n) under-uses the 256-bit column | §V-D | ok |
| 48 | NPU: LayerNorm, RoPE, softmax; PIM: linear layers, P·V; Q·Kᵀ on PIM only for post-RoPE keys | §V-B, Fig. 6(b) | ok |
| 48 | Linear: scale after the matmul; S_SF folded into Q before FP8; S_V into P, divided by S_Vmax, multiplied back after P·V | §V-C, Fig. 6(c) | ok |
| 50 | RTL in SystemVerilog, Synopsys DC, TSMC 28 nm, DeepScaleTool to 20 nm (HBM-PIM's node) | §VI-A Hardware Implementation | ok |
| 50 | Area (only) × 10 for the DRAM process: 10× lower transistor density at the same feature size | §VI-A | ok |
| 50 | HBM-PIM's area counts only MAC hardware; instruction decoder left out | §VI-C Area and Power | ok |
| 50 | N: TEP's +28 % power comes from the authors' simulation | §V-D ("Our simulation shows …") | ok |
| 50 | N (old slide): "the chain at the top", "the diagram below" | (layout) | fixed (positions were wrong for the side-by-side layout; the slide is now split in two and the notes follow each) |
| 51 | Cycle-level simulator: 4 NPU cores (after NeuPIMs), 16 HBM2 pseudo-channels, PIM after Newton | §VI-A | ok |
| 51 | Per core 128×128 systolic array, 128-way vector unit, 16 MB scratchpad (CACTI) | §VI-A | ok |
| 51 | NPU 1 GHz, PCU 500 MHz = HBM2 tCCD_S of 2 DRAM clocks | §VI-A | ok |
| 51 | Baselines NPU (FP16), NPU + HBM-PIM (FP16), Ecco (W4A8KV4); same NPU and DRAM, comparable total area | §VI-A Accelerator Baselines | ok |
| 51 | F: "16 pseudo-channels (8 drawn)" | (drawing) | ok |
| 52 | NPU row incl. 307 GB/s | §VI-A; Fig. 4 | ok |
| 52 | Memory row: HBM2, 16 pseudo-channels, 8 PCUs/channel, 500 MHz, 1.23 TB/s internal | §VI-A, §V-A, Fig. 4 | ok |
| 52 | Ecco with k-means codebooks and Huffman coding | §VI-A | ok |
| 52 | Speed/energy: decode only, 4K, batch 1–8, five models (Llama-2 7B/13B, 3.1-8B, 3.2-3B, Mistral-7B v0.3) | §VI-A | ok |
| 52 | Accuracy: eight models; Wikitext-2 and C4 at 2K; MMLU, ARC-C, GSM8K via LM-Eval | §VI-A, footnote 3 | ok |
| 52 | B/N: "accuracy uses eight models at 2K context" | footnote 3 (2K only for the comparison with baselines); Tables II, III say 4K | fixed (now "perplexity against the baselines … at 2K"; N adds that Tables II–III use 4K) |
| 52 | Oaken (KV4); QuaRot, QoQ (W4A8KV4, FP16 query and scores), official repositories | §VI-A Algorithm Baselines; Table IV footnote | ok |
| 52 | Source column (§ / Fig. per row) | — | fixed (removed from the slide as a source tag; the sources are in N) |
| 53 | Mean Δppl Wikitext / C4: Oaken 0.08 / 0.09; P3-LLM KV4 0.06 / 0.07; QuaRot 0.30 / 0.48; QoQ 0.30 / 0.38; P3-LLM W4A8KV4P8 0.25 / 0.31 | Table IV | ok |
| 53 | 39 % and 22 % lower perplexity loss than QuaRot and QoQ | §VI-B | ok |
| 53 | QuaRot, QoQ keep query and scores in FP16; P3-LLM quantizes scores always, query for Llama-3 and Mistral | Table IV footnote | ok |
| 53 | Reasoning averages 73.69 / 71.12 / 70.64, FP16 76.30; largest gap on Llama-3.2-3B | Table V; §VI-B Accuracy Results | ok |
| 54 | 7.8× / 4.9× / 2.0× speed; 6.3× / 3.5× / 2.1× energy over NPU / HBM-PIM / Ecco; five models, batch 1–8, 4K | §VI-C, Figs. 9, 10 | ok |
| 54 | Speedup peaks at batch 2 (TEP fills both slots) | §VI-C Speedup | ok |
| 54 | Energy: 4-bit operands cut traffic; TEP reuses each read twice | §VI-C Energy | ok |
| 54 | N: "HBM-PIM beats the NPU only at batch 1 and 2" | §VI-C (beats it at 1 and 2 on all models; at 4 its advantage diminishes for Llama-2 and disappears for Llama-3, Mistral) | fixed (the "only" overstated it) |
| 54 | N: 3.4× over an enhanced W8A8KV8 Pimba (Fig. 12); linear layers back to the NPU from batch 8 (Fig. 16) | §VI-C, Figs. 12, 16 | ok |
| 55 | PCU compute 7.7 → 8.4 mm², buffer 6.2; overhead 16.4 % → 17.5 %; 25 % limit | Table VII; §VI-C | ok |
| 55 | Energy per MAC at 1 GHz: HBM-PIM 0.69 (1 MAC/cycle), MANT 0.40 (2), BitMoD 0.61 (2), P3-LLM 0.18 (4); 3.8× better | Table VIII; §VI-C | ok |
| 55 | N: BitMoD pays an FP32 accumulator, MANT a wide partial-sum adder | §VI-C | ok |
| 57 | Ablation, batch 2 and 4, five models: W4A8KV4 3.3×, + TEP 1.6×, + 8-bit scores 1.2× | §VI-C Architecture Ablation; Fig. 15 (five models) | ok |
| 57 | A 4-bit-weight baseline would shrink the headline; ablation batches ≠ the 4.9× average's | — | our reading [BRAINSTORM] (tagged on the slide) |
| 58 | TEP needs PCU timing at tCCD_S (500 MHz on HBM2) in a DRAM process | §V-D, §VI-A ("can reliably achieve 2× higher frequency") | our reading [BRAINSTORM] (the question is ours; the facts are the paper's) |
| 58 | Fig. 7 draws one command per input vector → deeper reuse needs more command slots | Fig. 7 | our reading [BRAINSTORM] |
| 58 | TEP carries over to LPDDR (tCCD_S half of tCCD_L), not evaluated | §VII | ok (fact) / our reading (the open question) |
| 59 | Frozen smoothing factors: the paper does not say what happens when a decode key exceeds the prefill maximum | §IV-A (silent) | our reading [BRAINSTORM] |
| 59 | Pre/post-RoPE per family from 4K profiling; pre-RoPE keeps Q·Kᵀ on the NPU, slower at long context | §IV-A, §V-B, Fig. 11 (Llama-2-7B gains less from 2K to 16K) | ok (fact) / our reading (the open question) |
| 59 | "Accuracy uses 2K context, speed 4K" | footnote 3; Tables II, III at 4K | fixed (now "the baseline perplexities use 2K context, speed 4K"; N adds Tables II–III at 4K) |
| 59 | Simulator in-house, flat 10× DRAM area factor | §VI-A | ok |
| 60 | Recap: 4.9× speed at 17.5 % area overhead; 4× multipliers at tCCD_S | Fig. 9, Table VII, §V | ok |
| 60 | Citation and code URL github.com/yc2367/P3-LLM | abstract | ok |

## Totals

143 rows, counted by the first status in each row: **ok 103 · fixed 14 · our reading [BRAINSTORM] 10 · preliminary 16**
(the two rows that pair a paper fact with our open question count as ok). The fourteen fixes, all made in
`build_p3llm_deck.js` (12–14 also in `build_p3llm_intro.py`, whose figures the deck draws):

1. Slide 3 B and slide 32 T/B: "hit their compute roof already at batch 2–4" → the paper's "gain fades as the batch or
   GQA group nears 4" (§III-B).
2. Slide 3 N: the headline numbers sit "on the right", not "at the bottom".
3. Slide 17 N: 5 ns is the simulator's MAC-command spacing [A1], not a preset tCCD_L entry.
4. Slide 34 B: citation §III → §III-A.
5. Slide 36 N: the RoPE reason is the paper's for Llama-3 only; Mistral's post-RoPE choice is stated, not explained.
6. Slide 38 B: the group size of 128 now cites §V-C as well.
7. Slides 50–51 N: wrong positions ("the chain at the top", "the diagram below"); the methodology slide is split in two
   and each half has its own notes.
8. Slide 52 B/N: 2K context applies to the baseline perplexity comparison only (footnote 3); Tables II–III use 4K.
9. Slide 52: the per-row source column left the table (a source tag; the sources are in the notes).
10. Slide 54 N: "HBM-PIM beats the NPU only at batch 1 and 2" → at batch 1 and 2 on every model; at batch 4 its advantage
    shrinks for Llama-2 and disappears for Llama-3 and Mistral.
11. Slide 59 card 3 and N: the same 2K / 4K correction as fix 8.
12. Slide 29 (was 26, "P3-LLM builds on HBM-PIM"): the paper's Fig. 2 is §II-B, so the comparison left the presenter's
    primer and is now the Background slide redrawn from Fig. 2 alone; the §II-B die-area claim moved there from the
    motivation slide (32), which now cites §III-B only.
13. Slide 27 F/N: the new key enters the KV-cache after RoPE, as Fig. 1(a) draws it (the draft drew K and V straight
    from the projections).
14. Slide 28 N: the reason clause for GQA's arithmetic intensity was ours, not §I's; removed.
