# Style lessons from the five reference papers — structure and figures

Part of the architecture-paper-writing skill. Governs: narrative structure across every section, and every figure, caption and table. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

*Papers read in full (text and every figure):*
**[M]** Mesorasi (MICRO'20, Zhu) · **[TC]** Tensor Casting (HPCA'21, Rhu) · **[SS]** SmartSAGE
(ISCA'22, Rhu) · **[PVF]** Low-Latency Proactive Continuous Vision (PACT'20 best paper, Zhu) ·
**[CAL]** Characterization of DL for 3D Point Cloud Analytics (IEEE CAL'21, Rhu).
Each lesson names where it appears in those papers and, in the *SPLEX example* bullets, where it landed in the SPLEX paper.
Sentence-level rules (what to delete, what to keep, the merge pattern) live in
`01_sentence_style.md` — apply it in every writing pass alongside this file.

---

## 1. The narrative spine (all five share it)

The papers are built the same way: **characterize → root-cause → one insight → design that follows
from the insight → quantify the overhead where the component appears → evaluate.** The reader never
meets a design element before the measurement that justifies it.

### L1. Motivation is a *characterization*, not an argument
- [M] §III-B profiles five networks on TX2, decomposes time into 𝒩/𝒜/ℱ (Fig. 5), then closes with a
  literal **"Summary"** paragraph listing exactly two inefficiencies. [SS] §3 breaks training time
  into named stages (Fig. 6) and states "our **key observation**" in bold. [TC] §III measures the
  breakdown (Fig. 4), then isolates *one* operator (gradient expand-coalesce) and its memory
  intensity (Fig. 6). [CAL] is nothing but this: stage breakdown → operator breakdown → DRAM
  throughput/utilization (Fig. 5, 6).
- The pattern: a stacked breakdown chart, a sentence per stage, one stage singled out, a
  microarchitecture-independent explanation of *why* it is slow (fine-grained 8 B random access,
  LLC miss rate 62 %, DRAM BW 21 % of peak).
- **SPLEX example:** §3.3 must show the same three artifacts: (i) per-entry access-count CDF inside the
  top-2048, (ii) step-to-step Jaccard, (iii) the "Summary" list: *hot set is skewed; it is temporally
  stable; the indexer cache is 100 % hot.* The bandwidth observation (§3.2) is presented as a
  measured law, T(p) = max(bytes_H/BW_H, bytes_L/BW_L), with the ratio-sweep figure — the same
  role [TC] Fig. 5(a) plays for embedding-table skew.

### L2. The design opens with one insight, stated once, in italics, with an equation or rule
- [M] "The **key insight** is that feature extraction (ℱ) is *approximately distributive* over
  aggregation (𝒜)" → Eq. 2 → walk-through on PointNet++'s first module (Fig. 8).
- [TC] "**Key observations.** … coalescing gradients is functionally equivalent to conducting
  *reductions*" → Algorithm 2 → driving example Fig. 7/8.
- [SS] "**Key observations and proposed approach.**" → Fig. 10 (a) baseline vs (b) SmartSAGE on the
  same six node IDs.
- **SPLEX example:** §4.2 opens with *rename, not map*: attention is permutation-invariant over the past,
  RoPE is applied at insert, nothing outside the cache aliases a row index ⇒ hot entries can be
  physically re-indexed into [0, N) and steering is `index < N → HBM`. One rule, then a 6-entry
  (a)/(b) figure exactly like [SS] Fig. 10.

### L3. Top-down presentation: overview figure + numbered workflow, then components, then "putting it together"
- [SS] §4.1 "Architecture Overview" (**Hardware.** / **Software.** run-in paragraphs) → §4.2 with
  Fig. 11 whose circled ①–⑦ are keyed to a numbered list in the text → §4.3 software runtime.
  [TC] §IV: Algorithm → Software Runtime → Architecture → **§IV-D "Putting Everything Together."**
  [PVF] §4.1 System Overview (Fig. 6) → §4.2–4.4 mechanisms → **§4.5 "Architectural Augmentations
  and Implementation Details"** listing each new block with a bold name and its cost. [M] §V-A
  "Overall Design" with **Design** / **Work Flow** paragraphs → §V-B the one new unit.
- **SPLEX example:** §4.1 = overview figure + ①–⑦ decode-step walkthrough + placement table; §4.2 = insight,
  MML, roles (count/decide/move), engine, interface; §4.3 = software (MC-DLA shape). Circled
  numbers on the figure must match the list.

### L4. Every design choice is argued against the alternative the reviewer would raise
- [SS] §4.2 "**Why choose firmware-based (and not FPGA-based) CSDs for ISP?**" — a whole paragraph,
  later *measured* (§6.4). [M] "One might be tempted to reuse the NPU's global buffer… However…";
  "An alternative way to resolve bank-conflict would be… We leave it to future work." [PVF] "we
  choose to use a CNN-based frame prediction… a programmable NPU allows PVF to support other
  predictors." [TC] "why our casting algorithm specifically targets tensor gather-reduce is twofold."
- **SPLEX example:** three such paragraphs, each one sentence of alternative + one sentence of reason:
  hardware access counters at the MC (entry-blind, SRAM per entry) vs. counting from
  `topk_indices` the GPU already holds; a hardware page table (≈620 KB of PTEs, a walk on every
  gather line) vs. a comparator; FPGA/hard-wired policy vs. a small control core running firmware.

### L5. Deployability is claimed explicitly, with the boundary of change named
- [M] "Our design modifies only the NPU while leaving other SoC components untouched." [SS] "fully
  compatible with existing CSD architectures… maintains compatibility with current NVMe protocol."
  [TC] "can be implemented purely in software… utilizes the current software stack as-is." [PVF]
  "maximally reuse existing mobile SoC architecture… four principled augmentations."
- **SPLEX example:** §4.3's job (MC-DLA shape): the paged allocator is unchanged; the block table already
  produces the index the MML steers; the only runtime addition is applying a completed swap list
  as a permutation of slot ids at the step barrier; three optional hint calls; driver maps two
  windows. Say "the GPU's memory path is untouched" once, in §4.1 goals.

### L6. Overheads are quantified where the component is introduced
- [M] §V-B gives the PFT buffer (64 KB, 32 banks), NIT (12 KB), datapath widths; §VII-A area
  (0.059 mm², < 3.8 % of the NPU). [PVF] §4.5 lists each new block with size (PFB 1.5 MB, PRB 200 B)
  and §6.1 gives area (0.15 % of the SoC). [SS] §6.5 power (2–6 W). [TC] "copying the index array
  is negligible… several MBs."
- **SPLEX example:** every SRAM in the engine paragraph carries its KB and its derivation (ring 64 KB =
  4096 × 16 B; staging 128 KB from Little's law; region table 32 KB; 424 KB total, about two thirds of the
  ≈620 KB a page-table design would spend on PTEs alone). Swap bytes per step per layer
  (207 × 3.15 KB ≈ 0.65 MB at 64K) stated in §4.2 with the forward reference to §6.

### L7. Bold run-in headings, shallow nesting, forward references
- All five use `\paragraph{}`-style **Bold.** headings (Hardware./Software./Work Flow./Merits./
  Overhead./Direct I/O./I/O command coalescing.) inside at most two subsection levels, and every
  design claim ends with "as we quantify in Section 6.x".
- **SPLEX example:** §4.2 uses five `\paragraph{}` headings; no `\subsubsection`.

---

## 2. Sentence-level habits worth copying

| habit | examples in the references | SPLEX example |
|---|---|---|
| Signpost adverbs open the decisive sentence | "**Critically**, 𝒩, 𝒜, ℱ are serialized" [M]; "**Fundamentally**, Equ. 2 holds because…" [M]; "**Interestingly**, the off-chip memory bandwidth utilization is generally low" [SS] | one per subsection, not more |
| First sentence of a paragraph is the claim; the rest is evidence | [SS] §3.2 every paragraph; [TC] §III-A "First… Second… Third…" | rewrite any paragraph whose first sentence is context |
| Numbers carry unit + comparison | "0.05 % of a typical SoC area" [M]; "20× reduction in SSD→DRAM traffic" [SS]; "1.52× slower than a no-transfer ideal" [PVF] | never a bare number |
| Named artifacts are typeset | `T.Casted`, NS_config, SmartSAGE(HW/SW), Mesorasi-SW/-HW, Ltd-Mesorasi | `SPLEX`, `SPLEX-Free`, `index < N`, `topk_indices` in `\texttt{}` |
| Variants are system + suffix and introduced in a bullet list before evaluation | [M] §VI "Variants"; [SS] §6 "three design points" | baseline / static / ratio / SPLEX / SPLEX-Free / all-HBM, defined once |
| "Note that …" for a subtle correctness point | [M] "Note that it is the features that are being aggregated, not the original points." | "Note that the GPU only ever observes the current index." |
| Scope is fenced honestly | [PVF] §7 "Limitation and Discussion"; [M] "we leave it to future work" | §7-style paragraph for the batch ≥ 8 assumption and round-0 |

---

## 3. Figures — layout and color (the LazyDP visual system)

**Source of this section: LazyDP (ASPLOS'24, `references/papers/lazydp-asplos24.pdf`), adopted wholesale 2026-09-04** because
the owner wants the figures *understated and minimal*. The five text
references still govern §§1–2; only the *look* of the figures comes from LazyDP. Each rule below
names the LazyDP figure it was read off, so the contract stays auditable.

**The one semantic rule.** Everything that already exists — GPU, HBM, LPDDR, host, every baseline —
is drawn in white and grays and separated by *luminance*, never by hue. **Colour is reserved for what
the system adds or achieves.** Blue is a single-use accent for one distinct chart category. A reader who
sees colour on the page is looking at our contribution.

**Which colour, and how big (owner).** The "ours" colour splits by *area*:

- **A large filled area is never red.** Every block, container, span or otherwise sizeable shape that
  the system adds takes a **sky-blue tint fill `#CFE2F3` with a `#2B5FA8` stroke** (since 2026-09-04
  evening; it replaced the same day's yellow `#FFE082` / `#B8860B`). A big red block reads as an
  alarm; the blue tint still prints as a light tint in gray scale, so the understated-in-print
  property of F1 is preserved, and "ours" is one hue across block fills and the single chart series.
- **Adjacent small cells count as one large area when they abut** (owner). The size test
  is applied to what the eye sees, not to the individual shape: the SPLEX before/after figure's row (b) packs its three
  hot entries into `[0, N)` by construction, so three individually small cells fused into a ~200 pt
  continuous red band — exactly the alarm the rule forbids. When a diagram can place several marks
  side by side, colour them the blue tint. A cell stays eligible for red only when it is isolated by
  construction.
- **Red `#E03127` is reserved for small, pinpointing elements**: arrows and paths (the DMA/swap
  path), emphasis text, circled callouts, small markers, and a single operating
  point on a chart. Never as the fill of a large block. Chart bars keep the soft `#F7B0A0` fill with
  the `#E03127` edge — a bar is a thin mark, not a block, and §F5 is unaffected by this rule.
- **Why blue (owner, after one round with yellow):** LazyDP Fig. 11 colours the one
  thing the paper adds — its overhead bar — in exactly this blue, so the tint `#CFE2F3` with the
  `#2B5FA8` stroke is the reference's own "ours" colour, and it unifies the block fills with the
  single distinct chart series (the SPLEX four-GPU series in the GPU-count chart, already `#2B5FA8`). The yellow pair was
  tried first because the blue was thought to be spoken for; the owner preferred one hue for "ours".

### F1. Block diagrams: white substrate, square corners, *only the blocks the system adds are filled*
- [LazyDP Fig. 9(b)] Three light-gray containers (`#E8E8E8`), each with a **bold black title set
  above the container**, holding thin square-cornered black rectangles; the five blocks LazyDP
  contributes (Data loader, Model, ANS engine, Noise update engine, Optimizer) carry a salmon fill,
  everything else is white. No shadows, no gradients, no rounded corners, no hatches.
- [LazyDP Fig. 4] Red is also an **emphasis text** colour: the "Gradient + Noise" labels and the
  filled table rows are the paper's subject, and nothing else on the figure is coloured.
- [M] Fig. 13 / [PVF] Fig. 6 (the earlier references) agree on the principle — one fill for the new
  units, caption "Blocks added by the system are shaded" — only the hue changes.
- **SPLEX example:** vendor substrate, GPU die, UCIe, HBM/LPDDR MCs, PHYs, housekeeping = white or gray
  `#E8E8E8` with black outlines and black titles; MML steering, the migration engine, the shortlist
  kernel (dashed = software) and the per-stack LPDDR extensions of Figure 1 = **sky-blue tint fill
  `#CFE2F3` with a `#2B5FA8` outline and a black title** — the fill carries the "ours" signal, so a
  coloured title on top of it would only clash. Corners square
  (`rx = 0`; `rx = 2` only where a box must read as a chip/package). `fig_dsa` (§2) shows the
  algorithm, not our design, so it carries **no red at all**.

### F2. Two arrow classes, and circled numbers keyed to the text
- [SS] Fig. 3/9/11 (kept): data path black, the added path in the accent colour, ①–⑦ circles on the
  arrows repeated in the prose as "(step ❶ in Figure 1)". [LazyDP Fig. 9(b)] connectors are plain
  thin black lines with no labels at all — when in doubt, drop the label.
- **Rule:** requests black solid `#000000`, responses black dashed, DMA/swap path red `#E03127`,
  doorbell/completion blue dotted `#2B5FA8`; at most three non-black styles. Arrow labels take the
  colour of their arrow, which is the only way red or blue text enters a diagram. Paths are exactly
  the pinpointing marks red is for, so the swap arrow and its "swaps" label stay red even where the
  blocks around them are blue-tinted.

### F3. Before/after as stacked (a)/(b) with identical geometry
- [SS] Fig. 3(a)/(b), Fig. 10(a)/(b); [TC] Fig. 2 → Fig. 7; [M] Fig. 3 → Fig. 8; [LazyDP Fig. 4(a)
  vs (b)] — the same embedding table drawn twice, identical geometry, the difference carried by the
  fill alone.
- **SPLEX example (`fig:reindex`):** (a) six entries in position order, the hot ones scattered across the
  LPDDR region; (b) after two swaps they occupy indices 0–2. The hot cells are **blue-tinted in both
  rows** — they are the same entries before and after, and in (b) they abut into one large area
  (see the adjacency clause of the area rule); their labels stay black, the cold cells stay white.
  Same boxes, same width; the
  `N = 3` comparator is a black dashed rule; **the swap arcs and their italic label are red** — the
  action is the pinpointing mark; the tier captions above the row are black (they name existing
  hardware, so they are not coloured).

### F4. Timelines for overlap claims
- [LazyDP Fig. 8] two rows of flat rectangles on a bare time axis, the phase under discussion in
  red, the improvement marked by a plain black span arrow and one label. [SS] Fig. 4 and [TC] Fig. 9
  use the same construction.
- **SPLEX example (`fig:timeline`):** rows GPU / engine; the GPU's own work is white and gray, the engine's
  decide + swap boxes are blue-tinted (they are blocks), the swap-span bracket and its label are
  red (a mark), the decode-step window bracket black. This is the figure that carries the "design target is overlap" decision.

### F5. Charts
- **Frame:** a **full rectangle — all four spines** visible, black, `linewidth = 0.8`
  [LazyDP Figs. 10–13]. No despining. Dotted horizontal gridlines behind the data
  (`ls=":"`, `lw=0.5`, gray) — horizontal only.
- **Series colour = luminance ramp**, in fixed order white → `#E8E8E8` → `#BFBFBF` → `#808080` →
  black, with **red `#F7B0A0` (edge `#E03127`) for the system** and at most **one blue `#2B5FA8`** for a
  single distinct category [LazyDP Fig. 11's blue overhead bar]. Every bar keeps a thin black edge
  so a white bar is still a bar. **No hatches.** An *absent* measurement is marked by text alone
  (LazyDP's rotated "OOM" text, Fig. 13(a)); ours is "n/a" at the baseline of the empty slot, no
  placeholder bar *(SPLEX example)*.
- **Value labels above the bars** [LazyDP Figs. 12, 13 label every bar; its densest chart, Fig. 10,
  labels only the bars that overflow the axis]. The threshold is legibility: with at most three bars
  per group print every value, rotated 90° if the group is tight; with four or more per group print
  only the values that would otherwise be unreadable off the axis, and label nothing when nothing
  overflows. Never label some bars of a group and not others.
- **Group dividers:** thin vertical rules between groups, the group name on a **second level below
  the axis** while the per-bar names stay on the first level [LazyDP Figs. 10, 12, 13(a)–(d)].
- Log y where the range demands it, with the decades as the only y ticks [LazyDP Figs. 12, 13].
  A dashed black line at the normalization point (1.0).
- Legend inside or immediately above the frame, one row, no frame, no chart title (the caption is
  the title); axis labels carry units; captions end with "Higher is better." where needed.
- Line charts: solid lines, distinct markers, the same colour rule (existing systems black/gray,
  the system red, one blue).
- **SPLEX example, §6:** `fig_tier_speedup` (four bar series + the infinite-HBM oracle as a black dashed
  mark), `fig_gpu_curves` (HBM-only black, SPLEX 6 GPUs red, SPLEX 4 GPUs the one blue),
  `fig_gpu_energy` (6 GPUs red, 4 GPUs `#BFBFBF`), `fig_bweff` and `fig_hotness` (measured points
  black, the SPLEX operating point red).

### F6. Palette (replaces the tier-colour set; prints correctly in gray scale by construction)
| role | value | where |
|---|---|---|
| ink: outlines, text, arrows | `#000000` | everywhere |
| substrate | `#FFFFFF` | block-diagram ground, lightest bar |
| gray 1 (container / existing block) | `#E8E8E8` | nested containers, lightest gray series |
| gray 2 | `#BFBFBF` | second series |
| gray 3 | `#808080` | third series |
| black fill | `#000000` | the extreme series |
| **blue tint fill + stroke — every LARGE area the system adds** (LazyDP Fig. 11's blue) | `#CFE2F3` / `#2B5FA8` | blocks, containers, spans in block diagrams |
| **red fill — the system's chart bars only** | `#F7B0A0` | chart bars (a bar is a thin mark, not a block) |
| **red accent — strokes, emphasis text, DMA/swap path, one operating point** | `#E03127` | arrows, highlighted text, markers |
| blue — one distinct chart category, control arrows | `#2B5FA8` | the four-GPU series, doorbell/completion arrows; the same hue as the block stroke, so "ours" is one hue |
| green — small positive mark only (the overview figure's happy face and its caption); never a fill | `#1B7F3B` | one glyph + its label |
| code: comment / identifier / literal | `#1B7F3B` / `#1D4ED8` / `#E03127` | the algorithm listing |

Nothing else may be introduced. Two hues appear on a page only when one of them is red. No yellow
anywhere (a grep for `FFE082\|B8860B` across the figure generators must be empty).

### F7. Pseudo-code and code listings
- [LazyDP Fig. 9(a)] monospace inside a thin black box: **comments green** `#1B7F3B`, API/keyword
  **identifiers blue** `#1D4ED8`, **numeric literals red** `#E03127`, everything else black.
  [LazyDP Algorithm 1] a LaTeX algorithm is set the other way — rules above and below, no side
  borders, bold keywords, comments in the right margin — and stays almost monochrome.
- **SPLEX example (Algorithm 1):** `algpseudocode` already bolds the keywords, so colour only the two things
  LazyDP colours everywhere: `\Comment{}` green and the numeric literals in the statements red.
  A number inside a comment stays green — the comment is coloured as a whole.

---

## Worked example (SPLEX, ASPLOS submission)

Lesson → where it landed in the SPLEX paper:

| lesson | §3 Motivation | §4 Design | §6 Evaluation |
|---|---|---|---|
| L1 characterization with a "Summary" list | CDF + Jaccard + 100 %-hot indexer; ratio-law figure | — | — |
| L2 single insight + rule + (a)/(b) example | — | 4.2 opening paragraph + `fig:reindex` | — |
| L3 overview figure + ①–⑦ workflow | — | 4.1 + `fig:overview` | — |
| L4 alternative argued in place | — | counters-at-MC, page table, hard-wired policy | measured: SPLEX vs SPLEX-Free, ratio, static |
| L5 deployability with a named boundary | — | 4.1 goals; 4.3 (MC-DLA shape) | — |
| L6 overheads at introduction | — | SRAM table in 4.2; swap bytes/step | swap-path decomposition |
| L7 run-in headings + forward refs | — | five `\paragraph{}`s | — |
| F1–F2 block-diagram style | `fig_dsa` (red-free) | `fig:overview` (red fill only on MML + engine; ①–⑦) | — |
| F3 before/after | — | `fig:reindex` | — |
| F4 timeline | — | `fig:timeline` (overlap under o_proj+FFN) | — |
| F5 chart grammar | `fig_hotness`, `fig_bweff` | — | `fig_tier_speedup`, `fig_gpu_curves`, `fig_gpu_energy` |
| F7 pseudo-code colouring | — | Algorithm 1 (green comments, red literals) | — |

All SPLEX figures were restyled to F1–F7 in one pass; content, series and numbers were untouched
(every `NUMS` / `fig_data` assert still holds) and every canvas kept its size, because the page-8/9/10
float map depends on it. The palette lived in one place per family: a `PAPER` / `PARROW` pair in the
block-diagram generator module (the other block-diagram generators import them) and the module-level
colour constants of the chart generators.

## Guard classes

- **One palette definition per figure family.** The colour constants live in one module per family (block
  diagrams; charts) and every generator imports them. Change a colour there, never in a figure body.
- **Retired hexes are grepped out.** A grep for every retired colour (`FFE082\|B8860B` for the yellow pair)
  across the figure generators must be empty; two hues appear on a page only when one of them is red (F6).
- **A restyle changes no data.** Every data assert in the generators still holds after a restyle; content,
  series and numbers are untouched.
- **A restyle changes no canvas.** Every canvas keeps its size, because the page float map depends on it.
