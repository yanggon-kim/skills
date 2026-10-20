#!/usr/bin/env node
/* Worked example: the approved P3-LLM lab deck (56 slides), rebuilt with the skill's library.

   Run:   node build_p3llm_deck.js [OUT.pptx] [--work DIR]
          (default OUT: ./p3llm-intro.pptx; DIR: $DECK_WORK or ./.deck_work, made by scripts/setup.sh)
   Then:  DIR/venv/bin/python ../../scripts/deck_qa.py OUT.pptx DIR/p3llm-intro.meta.json

   Its page (assets/reference/p3llm-intro.html) predates the prototype format, so the slide content that the
   format now keeps in the HTML (titles, band bullets, speaker notes, step captions) lives here; the figures
   still come from the page (deck_figs_p3llm.py), never redrawn. The structure is the skill's: title, then the
   outline with part 1 (Summary) highlighted, which is also the Summary part's divider, then the summary
   slide ("Summary: ..."), a divider before every later part with that part highlighted, figure-first content slides with 2-3 bullets
   in the fixed band, storyboards as one Morph-linked slide per frame, two methodology slides before the
   results, a closing slide; provenance in the notes ("Figure: ..."), the author's own reading tagged on the
   slide with the deck's own tag.

   Content rules of this deck: every P3-LLM number comes from arXiv 2511.06838v4 with its section, figure or
   table; DRAM sizes and timings are simulator presets (LPDDR5-6400 AiM in Ramulator 2.0), never JEDEC values.
   The page drew in coral / teal / mustard; colorWords re-words the notes and legends for the theme. */
"use strict";
const path = require("path");
const fs = require("fs");
const { execFileSync } = require("child_process");
const SKILL = path.resolve(__dirname, "..", "..");
const lib = require(path.join(SKILL, "scripts", "deck_lib.js"));
const { M, R, CW, F, AREA, LABEL_PT } = lib;

const args = process.argv.slice(2);
const wi = args.indexOf("--work");
const WORK = path.resolve(wi >= 0 ? args.splice(wi, 2)[1] : process.env.DECK_WORK || ".deck_work");
const OUT = path.resolve(args[0] || "p3llm-intro.pptx");
fs.mkdirSync(WORK, { recursive: true });

// ------------------------------------------------------------------ figures from the page
const FIGJSON = path.join(WORK, "p3llm_figs.json");
execFileSync("python3", [path.join(__dirname, "deck_figs_p3llm.py"), FIGJSON], { stdio: "inherit" });
const FIGDATA = JSON.parse(fs.readFileSync(FIGJSON, "utf8"));
const FIG = FIGDATA.figs;
if (Object.keys(FIGDATA.fallback).length) {
  throw new Error("figures the converter cannot map: " + Object.keys(FIGDATA.fallback).join(", "));
}

const d = lib.createDeck({
  work: WORK,
  title: "P3-LLM for the Lab", subject: "Lab paper discussion: P3-LLM (arXiv 2511.06838v4)", author: "yanggon-kim",
  colorWords: { coral: "gold", Coral: "Gold", teal: "blue", Teal: "Blue", mustard: "light blue", Mustard: "Light blue", black: "dark gray" },
  nbRules: [[/\b(t|tCCD_[LS]|CL|RL|tRCD|tRRD|tRAS|tRP) = /g, "$1\u00a0=\u00a0"]],
  qa: {
    restricted: [{ text: "simulator preset", allowIn: ["fig_timing", "!!", "fig_tccd"] }],
    extraTags: ["DRAM explainer", "Fig\\. B\\d"],
    footerWords: ["Lab paper discussion", "P3-LLM for the Lab"],
  },
});
const { pres, C, NAVY, GOLD, nb, band, drawFig, notes, newSlide, stat, cards, table } = d;

// ------------------------------------------------------------------ the library's slide types, by figure name
const PARTS = [
  ["Summary", "the paper in one slide"],
  ["Background: DRAM and AiM", "hierarchy, ACT/RD/PRE, timing, stock AiM, HBM-PIM"],
  ["Motivation", "the compute roof of FP16 PIM, W4A8KV4P8"],
  ["Design", "four formats, the PCU and TEP, the dataflow"],
  ["Evaluation", "methodology, quality, speed and energy, area"],
  ["Discussion", "where the gain comes from, open questions"],
];
// slide 2 (overview = true) is the outline and the Summary part's divider at once: Summary highlighted
const outlineSlide = (section, hi, text, overview = false) => d.outlineSlide(section, PARTS, hi, text, overview ? { kind: "outline" } : {});
const figSlide = (section, o) => d.figSlide(section, { ...o, id: o.fig, fig: FIG[o.fig] });
const storySlides = (section, o) => d.storySlides(section, { ...o, id: o.story, story: FIG[o.story] });

// ================================================================== the deck
const S_OPEN = "Opening", S_SUM = "Summary", S_BG = "Background", S_MOT = "Motivation", S_DES = "Design", S_EVAL = "Evaluation", S_DISC = "Discussion";

// ---- 1 title
d.section(S_OPEN);
d.titleSlide(S_OPEN, {
  title: "P3-LLM",
  subtitle: "An Integrated NPU-PIM Accelerator for Edge LLM Inference Using Hybrid Numerical Formats",
  byline: ["Y. Chen, C. Fang, X. Dai, Y. Wu, T. Tambe, M. Verhelst, M. S. Abdelfattah", "arXiv 2511.06838v4, 2026 · Cornell, KU Leuven, Stanford"],
  notes: "Today's paper is P3-LLM, by Yuzong Chen, Chao Fang, Xilai Dai, Yuheng Wu, Thierry Tambe, Marian Verhelst and Mohamed Abdelfattah, from Cornell, KU Leuven and Stanford. I am using version 4 on arXiv, number 2511.06838, from May 2026. " +
    "The paper asks one question: how can DRAM processing-in-memory stay fast for LLM decoding on an edge device once the batch is larger than one? " +
    "I will start with the whole paper on one slide, then give the DRAM and PIM background we need, the motivation, the three design parts, the evaluation, and finally some points for discussion. Every number I quote comes from the paper, and I will say which section, figure or table it comes from. DRAM sizes and timings in the background are simulator presets that I use for illustration, not JEDEC values.",
});

// ---- 2 outline, which also opens part 1 (Summary)
d.section(S_SUM);
outlineSlide(S_SUM, 0,
  "Here is the plan for the talk, in six parts. Part one, highlighted, is a summary: the whole paper on one slide, which comes next. Part two is background: how a DRAM is organised, which commands read it, which timing rules space those commands, and how a stock PIM design, SK hynix's AiM, computes inside the DRAM. It ends with Samsung's HBM-PIM, which P3-LLM builds on. " +
  "Part three is the motivation: why FP16 PIM units run out of compute as soon as the batch grows, and which operands can be shrunk without losing accuracy. " +
  "Part four is the design: four number formats, the low-precision compute unit with its throughput trick called TEP, and the dataflow that folds the scales away. " +
  "Part five is the evaluation, starting with how the authors model the hardware, then accuracy, speed, energy and area. " +
  "Part six is discussion: where the speedup really comes from, and a few open questions I would like us to talk about. " +
  "Each later part starts with this outline again, with that part highlighted, so you always know where we are. If you already know DRAM timing well, part two will go quickly; I keep it because TEP only makes sense once tCCD_S and tCCD_L are clear.", true);

// ---- 3 summary
{
  const sl = newSlide("CONTENT", S_SUM, "content");
  sl.addText("Summary: shrink every operand; use each weight read twice", { placeholder: "title" });
  band(sl, [
    "Decoding reads every weight once per token, so it waits on DRAM; FP16 PIM loses its gain as the batch or the GQA group nears 4 (§III-B).",
    "P3-LLM adds W4A8KV4P8 formats (§IV), a low-precision PCU with TEP (§V-A, §V-D) and fused dequantization (§V-C).",
  ]);
  // figure on the left, the four headline numbers stacked on the right
  const sx = 6.85, sw = R - sx;
  drawFig(sl, FIG.fig_summary, { x: M, y: AREA.y, w: sx - 0.15 - M, h: AREA.h }, { id: "fig_summary", center: true, middle: true });
  [["4.9×", "speed vs HBM-PIM (7.8× NPU, 2.0× Ecco; Fig. 9)", true],
    ["3.5×", "energy efficiency vs HBM-PIM (6.3× NPU, 2.1× Ecco)"],
    ["17.5 %", "HBM area overhead; HBM-PIM 16.4 % (Table VII)"],
    ["0.25", "mean Wikitext ppl loss; QuaRot, QoQ 0.30 (Table IV)"]].forEach(([m, l, hot], i) =>
    stat(sl, sx, AREA.y + i * (AREA.h / 4), sw, m, l, hot));
  notes(sl, "In one sentence: P3-LLM shrinks every operand and uses each weight read twice. This slide is the whole paper in one picture. On the left is the host, a neural processing unit or NPU, which runs everything that needs FP16 or FP32: LayerNorm, rotary embeddings, softmax and the scales. On the right is one HBM-PIM channel. Between an even bank and an odd bank sits a PIM compute unit, the PCU. The banks stream 4-bit weights and 4-bit KV-cache into the PCU, the NPU sends 8-bit activations or attention scores, and the PCU sends 32-bit sums back. " +
    "The three numbered badges are the three design parts. Badge one is the W4A8KV4P8 formats, Section IV, which put every operand into 4 or 8 bits in a format chosen per operand. Badge two is the low-precision PCU and the throughput-enhanced PCU, TEP, which runs it twice per weight read, Sections V-A and V-D. Badge three is fused dequantization, a dataflow that hides the dequantization work on the NPU, Section V-C. " +
    "The four numbers on the right are the headline results. Speed is 4.9 times that of HBM-PIM, Figure 9. Energy efficiency is 3.5 times, Figure 10. The HBM area overhead is 17.5 percent against 16.4 percent, Table VII. And the mean Wikitext perplexity loss is 0.25, where QuaRot and QoQ lose 0.30, Table IV. Keep the 4.9 times in mind; in the discussion we will ask how much of it comes from the hardware idea and how much from quantization.", "Redrawn from the paper's Fig. 6(a) and §I.");
}

// ---- Background
d.section(S_BG);
outlineSlide(S_BG, 1, "Part two, background. P3-LLM's main hardware trick depends on DRAM timing details, so we need some vocabulary first: how a DRAM is organised, the three commands that read it, the timing rules between them, and how a stock PIM design, SK hynix's AiM, computes inside the DRAM. We end with Samsung's HBM-PIM, the design P3-LLM extends. All DRAM sizes and timings in this part are one simulator preset, LPDDR5-6400 AiM in Ramulator 2.0, not JEDEC values.");

figSlide(S_BG, {
  fig: "fig_hierarchy",
  title: "DRAM is a tree: channel, bank group, bank, row, column",
  body: [
    "A channel has its own command and data bus; a bank group is four banks that share one I/O path.",
    "A bank keeps one row open at a time: ACT opens a row (2,048 B here) and RD moves one 32 B column out.",
  ],
  caption: "Adapted from our DRAM explainer (Fig. B1); not to scale. Sizes are one simulator preset (LPDDR5-6400 AiM in Ramulator 2.0), not JEDEC values; HBM has the same levels with other sizes.",
  notes: "Before P3-LLM we need some DRAM vocabulary, because the paper's main hardware idea depends on it. A DRAM is organised as a tree. At the top is a channel: it has its own command bus and data bus, and the host drives each channel independently. Inside a channel are bank groups; in this picture there are four bank groups of four banks, so sixteen banks per channel. " +
    "A bank is one memory array, and the key fact is that a bank can hold only one row open at a time, in its row buffer. On the right I zoom into the coral bank. An activate command, ACT, copies one whole row into the row buffer; in the simulator preset we use here, a row is 2,048 bytes. A read command, RD, then moves one column out, 32 bytes in this preset, through the bank group's I/O path. " +
    "Remember that the four banks of a bank group share that one I/O path. Two slides from now this sets a timing rule, and P3-LLM builds its throughput trick on that rule. These sizes are a simulator preset for LPDDR5-6400 AiM in Ramulator 2.0, not JEDEC values; HBM has the same levels of hierarchy with different sizes.",
});

storySlides(S_BG, {
  story: "fig_actrdpre",
  title: "ACT opens a row, RD moves a column, PRE closes it",
  caption: "One bank. Coral = the path the current command uses; teal = the row in the row buffer. Sizes: simulator preset (LPDDR5-6400 AiM). Timing is left out here; the next storyboard adds it.",
  notes: [
    "This storyboard shows one bank and three commands. In the first frame nothing has happened yet: every row is closed, the row buffer is empty, and the bitlines are precharged. Watch the colours: coral marks the path the current command uses, and teal will mark the row held in the row buffer.",
    "ACT arrives. The row decoder raises one wordline, and the sense amplifiers copy the whole of row r into the row buffer, 2,048 bytes in this preset. This is the expensive step, because it moves an entire row out of the cells. From now on the row stays open, shown in teal.",
    "Now RD picks one column of the open row, 32 bytes here. The column leaves through the bank-group I/O and reaches the data bus a CAS latency later. Only a small slice of the open row moves.",
    "A second RD reads the next column of the same open row, and no new ACT is needed. This is the fact PIM depends on: open a row once, then compute on every column of it cheaply.",
    "Finally PRE closes the row. The sense amplifiers let go, the bitlines precharge, and the next ACT to this bank must wait tRP. So a row is opened, read column by column, and closed. The next storyboard adds the timing rules between these commands.",
  ],
});

storySlides(S_BG, {
  story: "fig_timing",
  title: "Timing rules set when each command may issue",
  titles: ["ACT in BG 0", "ACT in BG 1", "RD", "RD, same group", "RD, other group", "PRE"],
  caption: "Two banks (BG 0, BG 1) and the data bus, to scale in ns. Timings are simulator presets (LPDDR5-6400 AiM in Ramulator 2.0), not JEDEC values. Frames 4 and 5 are two alternatives for the second read. Adapted from our DRAM explainer (Fig. B2).",
  notes: [
    "This storyboard puts the same commands on a time axis, to scale in nanoseconds, with two banks: one in bank group 0 and one in bank group 1. The lanes are BG 0, BG 1 and the data bus, and coral marks each step's change and the rule that places it. First, ACT opens a row in bank group 0, and a read must wait tRCD, 9.375 nanoseconds in this simulator preset.",
    "A second ACT opens a row in bank group 1. ACTs to different banks must be at least tRRD apart, 2.5 nanoseconds here. Both rows are now open, shown in teal.",
    "The first RD goes to bank group 0. Its data reach the bus CL later, 12.5 nanoseconds, and take one 2.5-nanosecond burst, so the read latency RL is 15 nanoseconds in this preset.",
    "Frames four and five are two alternatives for the second read. Here it goes to the same bank group 0. It must wait tCCD_L, 5 nanoseconds, so its burst leaves a gap on the data bus.",
    "The alternative: the second read goes to bank group 1 instead. Now it waits only tCCD_S, 2.5 nanoseconds, and the two bursts touch. tCCD_S is half of tCCD_L in this preset. Keep this factor of two in mind; it is the basis of P3-LLM's TEP.",
    "Last, PRE closes bank group 0's row. It may not come earlier than tRAS, 21.25 nanoseconds after its ACT, and the next ACT to that bank waits tRP, 9.375 nanoseconds. All values here are simulator presets, not JEDEC table values.",
  ],
});

figSlide(S_BG, {
  fig: "fig_tccd",
  title: "Same bank group: tCCD_L apart; other groups: tCCD_S",
  body: [
    "A group's banks share one I/O path, so a second read to that group waits tCCD_L (5 ns here).",
    "Reads to other groups wait only tCCD_S (2.5 ns): the bursts touch.",
    "In HBM, tCCD_S is about half of tCCD_L (§V-D); TEP builds on this.",
  ],
  caption: "Right: two reads, to scale in ns. (a) same bank group, (b) different bank groups. Simulator presets, not JEDEC values.",
  notes: "This slide isolates the one timing rule P3-LLM builds on. On the left are two bank groups. The four banks of a group share one I/O path into the channel I/O. After that path carries one read, it needs time before it can carry the next; that time is tCCD_L, L for long. Banks in different bank groups use separate paths, so their reads can overlap, and the next read needs to wait only tCCD_S, S for short, which is one burst on the bus. " +
    "On the right the same two reads are drawn to scale. In case (a) both go to the same bank group: the second RD waits 5 nanoseconds and the bus idles between bursts. In case (b) they go to different bank groups: the second waits 2.5 nanoseconds and the bursts touch. These two values come from our simulator setup: 2.5 nanoseconds is the preset's tCCD_S, and 5 nanoseconds is the spacing the simulator uses between MAC commands, not a JEDEC table value. " +
    "The general point comes from the paper. In Section V-D the authors note that tCCD_S is typically about half of tCCD_L across all HBM generations. Stock PIM designs issue one compute command per tCCD_L, as we will see on the next slides. P3-LLM's TEP asks what happens if the compute unit instead runs at tCCD_S.",
});

storySlides(S_BG, {
  story: "fig_aim",
  title: "Stock AiM: one MAC16, one column in all 16 banks",
  titles: ["WRGB", "WRMAC16", "TMOD", "PREA and ACT16", "MAC16 × c", "TMOD", "RDMAC16"],
  captions: [null, null, null, null,
    "Each MAC16 reads one 32 B column from every bank; each PU multiplies it by the GB's 32 B input slice and adds into its MAC register. Nothing crosses the data bus; c MAC16s go tCCD_L apart."],
  caption: "One accumulation run on one channel. Top: the command strip (gray = to come; coral outline = this step). Schematic, not to scale: the c MAC16s take most of the time; refresh and exact interleaving are left out. Adapted from our DRAM explainer (Fig. B3).",
  notes: [
    "Now a stock PIM design, SK hynix's AiM, running one accumulation on one channel. The top strip shows the seven commands of a run: gray means still to come, and the coral outline is the current step. First, WRGB writes one 32-byte burst of the input vector from the host into the global buffer, the GB. This command uses the data bus.",
    "WRMAC16 writes a bias, or zero, from the host into all 16 MAC registers, one per bank. This also uses the data bus. The mustard outline marks registers that hold a value.",
    "TMOD switches the channel from register-access mode to array mode. Nothing moves; it changes how the following commands are interpreted.",
    "PREA closes any open rows, and ACT16 opens the same row in all 16 banks at once. Every bank now has a row of weights in its row buffer, shown in teal.",
    "This is the compute step. Each MAC16 reads one 32-byte column from every bank, and the global buffer broadcasts one 32-byte input slice. Each PU multiplies, sums in its adder tree and adds into its MAC register. Nothing crosses the data bus. The host sends c MAC16s, one per column, tCCD_L apart, and this phase takes most of the time.",
    "TMOD switches back to register-access mode, so that the MAC registers can be read.",
    "Finally RDMAC16 sends the 16 MAC registers to the host over the data bus. One run is complete: three commands used the data bus, and the compute itself did not.",
  ],
});

{
  const sl = newSlide("CONTENT", S_BG, "content");
  sl.addText("Only WRGB, WRMAC16 and RDMAC16 use the data bus", { placeholder: "title" });
  table(sl, ["command", "what moves", "data bus"], [
    { cells: ["WRGB", "host → global buffer: one 32 B burst", "yes"] },
    { cells: ["WRMAC16", "host → all 16 MAC registers: bias or zero", "yes"] },
    { cells: ["TMOD", "nothing; switches register-access ↔ array mode (twice per run)", "no"] },
    { cells: ["PREA / ACT16", "closes old rows; opens the same row in all 16 banks", "no"] },
    { cells: ["MAC16 × c", "each bank's 32 B column + the GB's 32 B broadcast → PU multiply and adder tree → MAC register", "no"], ours: true },
    { cells: ["RDMAC16", "16 MAC registers → host", "yes"] },
  ], { colW: [2.2, 8.65, 1.45], boldFirst: true, name: "table-aim", fontSize: 14, margin: [0.055, 0.09, 0.055, 0.09] });
  band(sl, [
    "MAC16 moves nothing on the data bus: each bank feeds its own PU, and the input comes from the on-chip global buffer.",
    "Every MAC16 touches all four bank groups, so MAC16s go tCCD_L apart: one MAC command per tCCD_L.",
  ]);
  notes(sl, "This table summarises the run we just watched. Only three commands use the data bus between the host and the DRAM: WRGB, which writes the input into the global buffer; WRMAC16, which initialises the MAC registers; and RDMAC16, which returns the results. TMOD only switches mode, twice per run, and PREA and ACT16 close and open rows. " +
    "The command that matters is MAC16, the highlighted row. It moves nothing over the data bus: each bank sends its column to its own PU, and the input comes from the global buffer inside the chip. That is how PIM uses the internal bandwidth of all banks at once. " +
    "Now the timing consequence. Every MAC16 touches all four bank groups, because all sixteen banks work together. So two consecutive MAC16s always fall under the same-bank-group rule, and they must be tCCD_L apart. Stock AiM therefore issues one MAC command per tCCD_L. P3-LLM's base design, HBM-PIM, has the same property: Section V-D says a PIM command is issued every tCCD_L. Keep this in mind for TEP, which asks how to do more work inside that tCCD_L window.", "One stock AiM run, from our DRAM explainer (Table B2). Sizes: simulator preset (LPDDR5-6400 AiM).");
}

figSlide(S_BG, {
  fig: "fig_bridge",
  title: "P3-LLM builds on HBM-PIM: one PCU per bank pair",
  body: [
    "HBM-PIM puts one PCU between an even and an odd bank, 8 per channel: a 16-way SIMD FP16 MAC fed 256 bits per column access (§II-B, §V-A).",
    "AiM differs: one PU per bank, BF16, an adder tree, a global buffer. From here on we say PCU, as the paper does.",
  ],
  caption: "Redrawn from the paper's Fig. 2 and Fig. 6(a); 4 of 16 banks drawn. Teal = weights, 256 bits per column access; dashed = input.",
  notes: "P3-LLM is not built on AiM but on Samsung's HBM-PIM, so let me bridge the two. On the left is stock AiM again: one PU under every bank, and a shared global buffer that holds the input. On the right is HBM-PIM, redrawn from the paper's Figure 2 and Figure 6(a). " +
    "HBM-PIM puts one PIM compute unit, a PCU, between an even bank and an odd bank, so a channel of 16 banks has 8 PCUs, as Section V-A describes. Each PCU has its own input register instead of a global buffer. Each PCU is a 16-way SIMD FP16 multiply-accumulate unit. One column access delivers 256 bits, which is 16 FP16 weights, and the PCU reuses one input element across all 16 weights, according to Section II-B. " +
    "So the MAC idea is the same as AiM's: multiply the open row's columns by an input held next to the banks. AiM differs in the details: one PU per bank, BF16 numbers, an adder tree and a global buffer. And like AiM, HBM-PIM issues one PIM command per tCCD_L. From here on I use the paper's word, PCU, for the compute unit.",
});

// ---- Motivation
d.section(S_MOT);
outlineSlide(S_MOT, 2, "Part three, motivation, which is Section III of the paper. Two questions. First, why does an FP16 PIM unit lose its advantage as soon as the batch grows or the model uses grouped-query attention? Second, which of the four operands, weights, activations, KV-cache and attention scores, can be shrunk without hurting accuracy?");

figSlide(S_MOT, {
  fig: "fig_roofline",
  title: "FP16 PIM's gain fades as batch or GQA group nears 4",
  body: [
    "HBM-PIM's roof is 1.23 TOPS on 1.23 TB/s: batching or GQA soon makes it compute-bound (Fig. 4, §III-B).",
    "FP16/BF16 PCUs already take 20–27 % of the DRAM die (§II-B).",
    "P3-LLM: 4× the multipliers at 2× the clock, an 8× roof of 9.84 TOPS (§III-B).",
  ],
  caption: "Redrawn from the paper's Fig. 4. The NPU line is its 307 GB/s DRAM bandwidth (compute roof not drawn). Mustard guides: operator positions, approximate.",
  notes: "Now the motivation, Section III, built on this roofline from the paper's Figure 4. The x-axis is arithmetic intensity, operations per byte of memory traffic; the y-axis is peak throughput in TOPS. HBM-PIM, in teal, has an internal bandwidth of about 1.23 terabytes per second and a compute roof of 1.23 TOPS, so its corner sits near one operation per byte. " +
    "Multi-head attention at batch 1 sits right at that corner, the case PIM was designed for. But as soon as a batch, or grouped-query attention, reuses each weight or key for more inputs, the operator moves right, past the corner, where HBM-PIM is capped by compute. The paper puts it this way: HBM-PIM's advantage gradually disappears as the batch size and the GQA group size approach 4. The mustard guides show GQA with group 4 at batch 4 and group 8 at batch 8; their positions are approximate, read from the figure. " +
    "Why is the roof so low? Section II-B: FP16 or BF16 PCUs already take 20 to 27 percent of the DRAM die, and a DRAM process has about ten times lower transistor density than logic, so few units fit. " +
    "P3-LLM's answer, in coral, is a roof eight times higher, 9.84 TOPS: four times the multipliers in the same compute area, because the operands are 4 bits, and clocked twice as fast. The gray line is the NPU with its 307 gigabytes per second of DRAM bandwidth.",
});

figSlide(S_MOT, {
  fig: "fig_quadrant",
  title: "4 bits for robust operands, 8 bits for fragile ones",
  body: [
    "Weights fill memory at batch 1 and the KV-cache grows with the batch; both still work at 4 bits (Fig. 3).",
    "Activations and scores are the most fragile and keep 8 bits; scores are quantized so P·V runs on the PCU (§III-A).",
  ],
  caption: "The four operands placed by memory footprint and by sensitivity to quantization, after the paper's Fig. 3. Schematic positions, not measured values.",
  notes: "Which operands can shrink? Figure 3 of the paper measures two things. First, memory footprint, Figure 3(a), for four models at 4K context and batch 1 to 8. At batch 1 the weights fill most of the memory, and as the batch grows the KV-cache grows with it. Activations and attention scores stay small, because they are freed right after use. " +
    "Second, sensitivity, Figure 3(b): the authors quantize one operand at a time to an n-bit integer and measure C4 perplexity. Activations and attention scores are the most fragile; weights and the KV-cache still work at four bits. " +
    "This slide places the four operands on those two axes. The large, robust operands, weights and KV-cache, drop to 4 bits to save memory traffic. The small, fragile ones, activations and scores, keep 8 bits to protect accuracy. That is where the name W4A8KV4P8 comes from: weights 4, activations 8, KV 4, P for the probabilities, or scores, 8. " +
    "One choice stands out: the scores are quantized too, so that the P times V product can also run on the low-precision PCU instead of the NPU. The positions on this slide are schematic, not measured values.",
});

{
  const sl = newSlide("CONTENT", S_MOT, "content");
  sl.addText("Earlier co-designs miss memory, accuracy or efficiency", { placeholder: "title" });
  table(sl, ["design", "precision", "memory saving", "accuracy", "HW efficiency"], [
    { cells: ["BitMoD", "W4A16KV16", "medium", "high", "medium"] },
    { cells: ["Oaken", "W16A16KV4", "medium", "high", "low"] },
    { cells: ["MANT", "W4A8KV4", "high", "medium", "medium"] },
    { cells: ["Ecco", "W4A8KV4", "high", "high", "low (decompresses to FP16)"] },
    { cells: ["Pimba", "W16A16KV8", "low", "high", "medium (linear layers unquantized)"] },
    { cells: ["P3-LLM", "W4A8KV4P8", "high", "high", "high"], ours: true },
  ], { colW: [1.7, 2.3, 2.4, 1.7, 4.1], boldFirst: true, name: "table-i", fontSize: 14, margin: [0.075, 0.09, 0.075, 0.09] });
  band(sl, [
    "MANT and Ecco already reach W4A8KV4, but MANT loses accuracy and Ecco decompresses to FP16 online (Table I).",
    "Plain integers at W4A8KV4P8 lose too much perplexity, so P3-LLM gives each operand its own format (§III-A).",
  ]);
  notes(sl, "Table I of the paper compares earlier quantization and hardware co-designs on three criteria: memory saving, model accuracy and hardware efficiency. " +
    "BitMoD quantizes only the weights, and Oaken only the KV-cache, so each saves a medium amount of memory. MANT and Ecco already reach W4A8KV4. MANT loses accuracy, and Ecco, while accurate, decompresses its data to FP16 online, so the paper rates its hardware efficiency low. Pimba keeps weights and activations at 16 bits and the KV-cache at 8, so it saves little memory, and its linear layers stay unquantized. " +
    "P3-LLM, the highlighted row, claims high on all three columns at a more aggressive point, W4A8KV4P8, with the scores also at 8 bits. " +
    "Why not simply use integers everywhere? The paper notes that naive W4A8KV4P8 with plain integers loses a lot of perplexity. Its answer is to give each operand its own number format, chosen for that operand's value distribution. The next four slides go through those formats one at a time: KV-cache, attention scores, weights and activations. Keep in mind that these ratings are qualitative, and they are the authors' own.", "After the paper's Table I; the ratings are the paper's.");
}

// ---- Design
d.section(S_DES);
outlineSlide(S_DES, 3, "Part four, the design, Sections IV and V of the paper. First the four number formats, one per operand: INT4 asymmetric for the KV-cache, a new unsigned FP8 for attention scores, BitMoD for weights and FP8-E4M3 for activations. Then the low-precision PCU and TEP, its throughput trick. Then the dataflow that folds the dequantization into neighbouring operators.");

figSlide(S_DES, {
  fig: "fig_kv",
  title: "KV-cache: smooth keys by their prefill maxima, then INT4",
  body: [
    "Key outliers sit in fixed channels: each is divided by its prefill maximum, and decoding reuses the factors (Fig. 5, Eq. 2).",
    "No calibration set; factors < 1 % of memory. 128 values share a 16-bit scale and 4-bit zero point: 4.16 bits each (§VI-B).",
  ],
  caption: "Left and right: key magnitudes per channel before and after smoothing (schematic, after the paper's Fig. 5). Bottom: one INT4-Asym group (§IV-A, §VI-B).",
  notes: "The first format is for the KV-cache, Section IV-A. The authors profile the cache on Wikitext-2 in Figure 5. The value cache shows no outlier pattern. The key cache does: a few fixed channels are much larger than the rest, like the two coral bars on the left, which are schematic. " +
    "Their fix is dynamic key smoothing, Equation 2. During prefill, record each key channel's largest magnitude and divide the channel by it, so that every channel fits between minus one and one, as on the right. During decoding, reuse the same factors. No calibration dataset is needed, unlike Oaken, SmoothQuant or QoQ, so the method cannot overfit to one dataset. The factors take less than one percent of memory, and computing them takes less than 5 milliseconds for Llama-3.1-8B at 32K context on an A6000 GPU. " +
    "One subtlety is the rotary embedding, RoPE, which rotates keys by position. Llama-1 and 2 keys are quantized before RoPE, Llama-3 and Mistral keys after it. The paper's reason is shown for Llama-3: its maximum length is 128K, so at a 4K context the rotation angles are small and the outlier channels survive RoPE; Llama-2's do not. " +
    "The stored format, at the bottom, is INT4 asymmetric per head: 128 four-bit values share a 16-bit scale and a 4-bit zero point, which is 4.16 bits per value in effect, against about 4.8 bits for Oaken, Section VI-B.",
});

figSlide(S_DES, {
  fig: "fig_bits",
  title: "Scores: trade the sign bit for a mantissa bit",
  body: [
    "Scores lie in [0, 1]: no sign is needed, and their 14 FP16 exponents fit 4 bits with bias −15 (§IV-B).",
    "No scale: keep the top 4 mantissa bits of the FP16 score. Llama-3.1-8B Wikitext: 5.95, as FP16; INT8 6.06 (Table II).",
  ],
  caption: "Bit layouts, one box per bit. Mustard = sign; teal = exponent; gray = mantissa; coral = the bit FP8-S0E4M4 gains from the dropped sign (§IV-B).",
  notes: "The second format is new: FP8-S0E4M4, for attention scores, Section IV-B. Look at the bit layouts. FP16 has a sign bit, five exponent bits and ten mantissa bits. Standard FP8-E4M3 has a sign, four exponent bits and three mantissa bits. " +
    "The argument for the new format has two steps. First, scores come out of softmax, so they lie between zero and one and are never negative; a sign bit carries nothing. Second, FP16 values below one use only fourteen exponent values, minus fourteen to minus one, and four exponent bits with a bias of minus fifteen cover exactly those. So the freed sign bit becomes a fourth mantissa bit, the coral box: no sign, four exponent bits, four mantissa bits, hence S0 E4 M4. " +
    "Quantizing needs no scale factor at all: round the FP16 score and keep its top four mantissa bits. " +
    "Table II shows it works. On Llama-3.1-8B with Wikitext, FP8-S0E4M4 gives perplexity 5.95, the same as FP16, while INT8 gives 6.06 and FP8-E4M3 gives 5.99. INT8 is also a poor fit for hardware reasons: in the PCU the scores take the same input port as the activations, and INT8 is bad for activations too, as we will see two slides from now.",
});

figSlide(S_DES, {
  fig: "fig_bitmod",
  title: "Weights: BitMoD turns FP4's spare −0 into ±5 or ±8",
  body: [
    "FP4 has 16 codes but 15 values; BitMoD maps −0 to one of {±5, ±8}, chosen per group of 128 weights (§IV-C, §V-C).",
    "Weights and KV-cache share one PCU input, so each PE has one decoder for BitMoD and INT4-Asym (§V-A).",
  ],
  caption: "FP4 values on a number line, the spare −0 code, and BitMoD's four candidate special values (§IV-C).",
  notes: "The third format, for weights, is not new: it is BitMoD, earlier work by the same first author, used here in Section IV-C. Plain FP4 has sixteen codes but only fifteen distinct values, because plus zero and minus zero are equal. The dots on this number line are those fifteen values: zero, and plus or minus 0.5, 1, 1.5, 2, 3, 4 and 6. " +
    "BitMoD reuses the spare minus-zero code as one special value. The candidates are the coral rings: plus or minus 5, or plus or minus 8. For each group of 128 weights, BitMoD picks the one that gives the smallest quantization error, so the extra value lands where that group needs it most. " +
    "There is a hardware consequence. Weights and the KV-cache enter the PCU through the same input, so each processing element has one decoder that handles both BitMoD and INT4 asymmetric, as Section V-A describes. " +
    "How much does BitMoD buy over plain INT4 weights? In the algorithm ablation, Table VI, it recovers 0.01 perplexity on Llama-2-7B and 0.07 on Llama-3.1-8B. That is a small step compared with the key smoothing, which recovers 0.10 and 0.17 in the same table.",
});

figSlide(S_DES, {
  fig: "fig_act",
  title: "Activations: a plain per-token cast to FP8-E4M3",
  body: [
    "Rotations (QuaRot, SpinQuant) add run-time work; smoothing (SmoothQuant) pushes the difficulty into 4-bit weights (§IV-D).",
    "FP8-E4M3's wide range absorbs outliers: with 4-bit weights it beats INT8 SmoothQuant on all four models (Table III).",
  ],
  caption: "Wikitext-2 perplexity from the paper's Table III (4K context). Hollow = FP16; teal = 4-bit BitMoD weights + FP8-E4M3 activations; coral = 4-bit weights + INT8 SmoothQuant activations.",
  notes: "The fourth format is for activations, Section IV-D. Activations also have outlier channels, and the usual fixes have costs. Rotation methods, such as QuaRot and SpinQuant, apply a Hadamard rotation at run time, which adds work. Smoothing, as in SmoothQuant, moves the difficulty from the activations into the weights, which hurts when the weights are only four bits. " +
    "The paper's finding is that a plain per-token cast to FP8-E4M3 is enough, because the floating-point format's wide range absorbs outliers by itself. " +
    "This chart is Table III: Wikitext-2 perplexity at 4K context for four models. The hollow dot is FP16. The teal dot is 4-bit BitMoD weights with FP8-E4M3 activations. The coral dot is 4-bit weights with INT8 SmoothQuant activations. On every model teal sits closer to FP16 than coral does. For example, Llama-3.1-8B gives 6.16 with FP8 against 6.36 with INT8 SmoothQuant, and FP16 is 5.84. " +
    "That completes the four formats: INT4 asymmetric with key smoothing for the KV-cache, FP8-S0E4M4 for scores, BitMoD for weights and FP8-E4M3 for activations. Next, the hardware that computes on them.",
});

figSlide(S_DES, {
  fig: "fig_pcu",
  title: "The PCU: a 1×4×16 tile with 64 multipliers",
  body: [
    "A 256-bit column holds 64 four-bit values: 64 multipliers, 4× HBM-PIM's 16, with 16 outputs and a 4-wide input (§V-A).",
    "Each PE does 4 MACs per cycle in 6-bit fixed point, at 1.08× the area of an FP16 PE (Table VIII).",
  ],
  caption: "Top: the operands of one column access. Middle: the 16 PEs. Bottom: one PE zoomed in. Arrows = data moves. Redrawn from the paper's Fig. 6(a).",
  notes: "Now the hardware, Section V-A, redrawn from Figure 6(a). A column access delivers 256 bits, as in HBM-PIM. At four bits that is 64 weights or KV values, shown in teal at the top right, so the PCU has 64 multipliers, four times HBM-PIM's 16 FP16 multipliers. " +
    "The authors could have built a 64-wide SIMD unit, but that would need 64 accumulators of 32 bits each, too many registers. Instead they keep HBM-PIM's 16 outputs and widen the input: the input register holds four 8-bit values. The result is a 1 by 4 by 16 tile: one row of 4 inputs, times a 4 by 16 block of weights, gives 16 outputs. HBM-PIM's tile is 1 by 1 by 16. " +
    "The bottom box zooms into one PE, which is a 4-way dot product. Each multiplier works in 6-bit fixed point; each product is shifted by the input's exponent; a 4:2 compressor tree adds the four; and a 32-bit accumulator holds the sum. There are no floating-point multipliers and no exponent-alignment units, which is where the area goes away. " +
    "Table VIII reports that this PE does 4 MACs per cycle at 1.08 times the area of an FP16 PE.",
});

storySlides(S_DES, {
  story: "fig_tep",
  title: "TEP: run the PCU at tCCD_S, use each column twice",
  caption: "Redrawn from the paper's Fig. 7; frame 6 is our addition. Time in DRAM clocks: tCCD_L = 4, tCCD_S = 2 (§V-D, §VI-A). Mustard = input-register write; teal = work on input A; coral = work on input B.",
  notes: [
    "This storyboard is the paper's Figure 7 and the key hardware idea, TEP, the throughput-enhanced PCU. Time runs left to right in DRAM clocks. The lanes are the command bus, the weight column read from the bank, and each design's PCU. First, the NPU writes the inputs, A and B, into the PCU's input register; that is the mustard box.",
    "HBM-PIM first. One PIM command at time 1 reads weight column 1. Its FP16 PCU needs the whole tCCD_L window, four clocks, to compute W1 times A1. The next weight column cannot come earlier anyway, because of the same-bank-group rule.",
    "Now P3-LLM. Its low-precision PCU closes timing at tCCD_S, two clocks, so it finishes W1 times A1 in half the window. The second half of the window is free, while weight column 1 is still at the PCU.",
    "A second PIM command at time 3 multiplies the same weight column, W1, by input B. Note that the paper draws one PIM command per input vector. The weight was read from the row buffer once and used twice.",
    "The pattern repeats for weight column 2. Per tCCD_L window HBM-PIM makes one product and P3-LLM makes two: double the throughput whenever two inputs share the same weights, for example two requests in a batch.",
    "This last frame is our addition, not the paper's. At batch 1 there is no input B, so the second tCCD_S slot stays idle and TEP gains nothing. This is why P3-LLM's speedup peaks at batch 2 in Figure 9.",
  ],
});

{
  const sl = newSlide("CONTENT", S_DES, "content");
  sl.addText("TEP: 28 % more PIM power, each weight read used twice", { placeholder: "title" });
  const sw = (AREA.w - 2 * 0.45) / 3;
  [["+28 %", "PIM power with the PCU at tCCD_S instead of tCCD_L (§V-D)"],
    ["1.56×", "energy efficiency from TEP (§V-D)", true],
    ["1.6×", "speed from TEP over W4A8KV4 alone, batch 2 and 4 (Fig. 15)"]].forEach(([m, l, hot], i) => {
    const x = M + i * (sw + 0.45);
    stat(sl, x, AREA.y + 0.70, sw, m, nb(l), hot, { metric: F(72), label: F(22), mh: 0.9, lh: 0.85 });
  });
  band(sl, [
    "Power rises only 28 %: DRAM cell access and column decoding dominate it, and the weights are reused across two tCCD_S windows (§V-D).",
    "Spatial reuse loses: an n×4×16 tile needs n× the multipliers; n×4×(16/n) wastes the 256-bit column (§V-D).",
  ]);
  notes(sl, "What does TEP cost, and what does it buy? Three numbers from the paper. " +
    "First, PIM power rises 28 percent when the PCU runs at tCCD_S instead of tCCD_L, Section V-D. It is only 28 percent because most PIM power goes to DRAM cell access and column-decoder switching, and those do not change: the same weights are reused from the row buffer across two consecutive tCCD_S windows. Throughput doubles for shared weights while power rises 28 percent, so the paper reports 1.56 times better energy efficiency. " +
    "Second, in the architecture ablation, Figure 15, TEP adds 1.6 times speed at batch 2 and 4, on top of W4A8KV4 quantization. " +
    "Third, the paper explains why it chose temporal reuse rather than spatial reuse. An n by 4 by 16 tile, with n inputs at once, needs n times the multipliers, which costs too much area in a DRAM process. An n by 4 by 16-over-n tile keeps the multiplier count but wastes the 256-bit column bandwidth. Temporal reuse costs neither: it uses the same multipliers twice within the window that the DRAM timing already imposes. " +
    "The power figure comes from the authors' simulation, which we will look at in the methodology slides.");
}

figSlide(S_DES, {
  fig: "fig_dataflow",
  title: "The NPU keeps FP16 work; scales fold into neighbours",
  body: [
    "The NPU runs LayerNorm, RoPE and softmax; PIM runs the linear layers and P·V, and Q·Kᵀ only for post-RoPE keys (Fig. 6b).",
    "Each scale folds into a neighbouring operator, so PIM computes only in low precision (§V-C).",
  ],
  caption: "One decoder layer; left to right = operator order. Top lane = NPU, bottom lane = PIM; dashed box = depends on the model; coral tags = where each scale is folded. Redrawn from the paper's Fig. 6(b, c).",
  notes: "The third design part is the dataflow, Section V-C, redrawn from Figure 6(b) and (c). Operator order in one decoder layer runs left to right. The top lane is the NPU, in FP16 and FP32: LayerNorm, rotary embedding and softmax. The bottom lane is the PIM PCU, in low precision: the QKV projection, P times V, the output projection and the MLP. " +
    "Q times K-transpose, the dashed box, depends on the model. For Llama-3 and Mistral the keys were quantized after RoPE, so the stored keys can be multiplied directly on PIM. For Llama-1 and 2 the keys were quantized before RoPE, so RoPE would have to be applied to every stored key in every step, and the NPU does Q times K-transpose instead. " +
    "Dequantization runs on the NPU, but it is folded into neighbouring operators, the coral tags. For linear layers, the output is multiplied by the scale after the matmul. For Q times K-transpose, the key smoothing factor S_SF is folded into the query before its FP8 cast. For P times V, the value scale S_V is folded into the scores; it is first divided by its maximum, S_Vmax, so that the scores stay between zero and one, and S_Vmax is multiplied back after P times V.",
});

// ---- Evaluation
d.section(S_EVAL);
outlineSlide(S_EVAL, 4, "Part five, the evaluation, Section VI of the paper. I start with three slides on methodology and setup, because every hardware result in this paper is modelled, not measured on silicon, so we should know how. Then model quality, speed and energy, and area.");

{
  // methodology (1/2): the hardware-cost chain left to right, then two facts that qualify the area numbers
  const sl = newSlide("CONTENT", S_EVAL, "content");
  sl.addText("Methodology: area and power from RTL synthesis", { placeholder: "title" });
  band(sl, [
    "The PCU is RTL in SystemVerilog, synthesized with Synopsys DC in TSMC 28 nm and scaled to HBM-PIM's 20 nm with DeepScaleTool (§VI-A).",
    "Area and power both come from this flow; only the area then gets the 10× DRAM-process factor (§VI-A).",
  ]);
  const gap = 0.36, bw = (CW - 3 * gap) / 4, bh = 0.95, y0 = AREA.y + 0.42;
  sl.addText("Hardware cost of one PCU: area and power", { x: M, y: AREA.y, w: CW, h: 0.32, fontSize: 16, bold: true, color: NAVY, margin: 0, valign: "top", isTextBox: true, objectName: "chain-head" });
  const steps = ["RTL in SystemVerilog", "Synopsys DC, TSMC 28 nm", "DeepScaleTool to 20 nm (HBM-PIM's node)", "area × 10 for the DRAM process"];
  steps.forEach((t, i) => {
    const x = M + i * (bw + gap);
    sl.addShape(pres.shapes.RECTANGLE, { x, y: y0, w: bw, h: bh,
      ...(i === 3 ? { fill: { color: GOLD, transparency: 60 }, line: { color: NAVY, width: 1.5 } } : { fill: { color: C.background1 }, line: { color: C.text1, width: 0.75 } }), objectName: `chain${i}` });
    sl.addText(nb(t), { x: x + 0.08, y: y0, w: bw - 0.16, h: bh, fontSize: 15, color: C.text1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `chain${i}-text` });
    if (i < 3) sl.addShape(pres.shapes.LINE, { x: x + bw + 0.04, y: y0 + bh / 2, w: gap - 0.08, h: 0, line: { color: C.text1, width: 1.25, endArrowType: "triangle" }, objectName: `chain${i}-arrow` });
  });
  const tw = (CW - 0.45) / 2, ty = y0 + bh + 0.38, big = { metric: 28, label: 15, mh: 0.46, lh: 0.80 };
  stat(sl, M, ty, tw, "10×", "area factor for the DRAM process: 10× lower transistor density than logic at the same node (§VI-A)", true, big);
  stat(sl, M + tw + 0.45, ty, tw, "MAC only", "HBM-PIM's area counts only its MAC hardware; its instruction decoder is left out (§VI-C)", false, big);
  notes(sl, "Before the results: how were they produced? Every hardware number in this paper is modelled, not measured on silicon, so the method matters. This slide is the hardware cost, from Section VI-A. " +
    "The chain runs left to right. The PCU is written as RTL in SystemVerilog and synthesized with Synopsys Design Compiler in TSMC 28 nanometre. The area and power results are scaled to HBM-PIM's 20 nanometre node with DeepScaleTool. Then the area, and only the area, is scaled once more for the DRAM process, which the paper says has ten times lower transistor density than a logic process at the same feature size; that is the gold box. " +
    "Two facts qualify the area numbers we will see. First, the ten-times factor is flat: one number for the whole PCU. Second, Section VI-C says the HBM-PIM baseline is modelled with its MAC hardware only; its instruction decoder and its other operators, such as element-wise multiplication and addition, are left out. Both choices apply to HBM-PIM and P3-LLM alike, so the comparison stays like for like, but the absolute percentages depend on them. " +
    "The power figure for TEP, plus 28 percent, also comes from this simulation of the RTL.", "From the paper's §VI-A and §VI-C. The 10× factor is the DRAM process's lower transistor density at the same feature size.");
}

figSlide(S_EVAL, {
  // methodology (2/2): the simulated system
  fig: "fig_setup",
  title: "Methodology: a cycle-level simulator for performance",
  body: [
    "An in-house cycle-level simulator models 4 NPU cores after NeuPIMs and 16 HBM2 pseudo-channels whose PIM follows Newton (§VI-A).",
    "NPU at 1 GHz, PCU at 500 MHz = HBM2's tCCD_S of 2 DRAM clocks; all baselines share the NPU and DRAM (§VI-A).",
  ],
  caption: "The simulated system and its three hardware baselines, from the paper's §VI-A. All baselines share the NPU and DRAM at comparable total area.",
  notes: "Performance comes from an in-house cycle-level simulator; this diagram is the system it models, from Section VI-A. On the left, the host NPU: four cores. The NPU design follows NeuPIMs: each core has a 128 by 128 systolic array, a 128-way vector unit and a 16-megabyte scratchpad, modelled with CACTI. On the right, sixteen pseudo-channels of HBM2 with PIM. The PIM side follows the methodology of Newton, extended to the new PCU's computation flow. " +
    "The NPU runs at 1 gigahertz and the PCU at 500 megahertz, which matches HBM2's tCCD_S of two DRAM clocks. " +
    "The three hardware baselines are listed at the bottom: the NPU alone, the NPU with HBM-PIM, and Ecco. All of them share the same NPU and DRAM configuration at comparable total area. The runs cover decoding only, at 4K context, batch 1 to 8, on five models.",
});

{
  const sl = newSlide("CONTENT", S_EVAL, "content");
  sl.addText("Hardware and software setup", { placeholder: "title" });
  band(sl, ["Speed and energy: five models, decode only, 4K. Perplexity against the baselines: eight models at 2K, as they report (§VI-A)."]);
  table(sl, ["item", "setting"], [
    { cells: ["NPU", "4 cores at 1 GHz after NeuPIMs; per core a 128×128 systolic array, a 128-way vector unit, a 16 MB scratchpad (CACTI); 307 GB/s DRAM"] },
    { cells: ["Memory + PIM", "HBM2, 16 pseudo-channels; 8 PCUs per channel, one per bank pair; PCU at 500 MHz = tCCD_S (2 DRAM clocks); 1.23 TB/s internal"], ours: true },
    { cells: ["HW baselines", "NPU (FP16); NPU + HBM-PIM (FP16); Ecco (W4A8KV4, k-means codebooks, Huffman coding); same NPU and DRAM, comparable area"] },
    { cells: ["Speed, energy", "decode only, 4K context, batch 1–8; Llama-2 7B and 13B, Llama-3.1-8B, Llama-3.2-3B, Mistral-7B v0.3"] },
    { cells: ["Accuracy", "8 models (Llama-1/2 7B and 13B, Llama-3.1-8B, Llama-3.2-3B, Mistral-7B v0.1, v0.3); Wikitext-2 and C4 perplexity at 2K; MMLU, ARC-C, GSM8K"] },
    { cells: ["Algorithm baselines", "Oaken (KV4); QuaRot and QoQ (W4A8KV4, FP16 query and scores), from their official repositories"] },
  ], { colW: [2.1, 10.03], boldFirst: true, name: "table-setup", fontSize: 12, margin: [0.035, 0.08, 0.035, 0.08] });
  notes(sl, "This table collects the rest of the setup, from Section VI-A; the NPU's DRAM bandwidth and the internal PIM bandwidth come from the roofline in Figure 4, and the PCU count from Section V-A. " +
    "The NPU row repeats the simulated host, and adds its DRAM bandwidth of 307 gigabytes per second. The memory row is HBM2 with 16 pseudo-channels, 8 PCUs per channel, one per bank pair, the PCU at 500 megahertz, and 1.23 terabytes per second of internal bandwidth. " +
    "The hardware baselines are three: the NPU alone running FP16 models; the NPU with Samsung's HBM-PIM, also FP16; and Ecco, an LLM accelerator at W4A8KV4 with k-means codebooks and Huffman coding. " +
    "Speed and energy use five models, because the other three share size or architecture with these. They cover the decoding stage only, which the authors argue dominates edge latency, at 4K context and batch sizes 1 to 8. " +
    "Accuracy uses eight models from HuggingFace, with the quantization implemented in PyTorch. The perplexity comparison with the baselines, Table IV, uses Wikitext-2 and C4 at 2K context, to match the baselines' reported results and because Llama-1 supports only 2K; the format studies in Tables II and III use 4K. Reasoning accuracy uses MMLU, ARC-Challenge and GSM8K through LM-Eval, on the instruct versions of Llama-3.1-8B and Llama-3.2-3B. " +
    "The algorithm baselines are Oaken for KV-cache-only quantization, and QuaRot and QoQ at W4A8KV4, reproduced from their official repositories.", "All values from the paper's §VI-A, except the 307 GB/s and 1.23 TB/s (Fig. 4) and the PCU count (§V-A).");
}

figSlide(S_EVAL, {
  fig: "fig_quality",
  title: "P3-LLM loses less perplexity than QuaRot and QoQ",
  body: [
    "Mean perplexity loss is 39 % and 22 % lower than QuaRot's and QoQ's, which keep query and scores in FP16 (Table IV).",
    "Reasoning average: 73.69 vs 71.12 (QuaRot) and 70.64 (QoQ), FP16 76.30; largest gap on Llama-3.2-3B (Table V).",
  ],
  caption: "Mean perplexity increase over FP16 across eight models at 2K context, from the paper's Table IV. Coral = P3-LLM.",
  notes: "First, model quality, from Table IV, shown as the mean perplexity increase over FP16 across eight models at 2K context. Lower is better, and coral is P3-LLM. " +
    "The top two rows are KV-cache-only quantization. Oaken loses 0.08 on Wikitext and 0.09 on C4; P3-LLM's dynamic smoothing loses 0.06 and 0.07, and it does so at 4.16 effective bits against Oaken's 4.8. " +
    "The bottom three rows quantize weights and activations too. QuaRot loses 0.30 and 0.48, QoQ 0.30 and 0.38, and P3-LLM 0.25 and 0.31. The paper summarizes this as 39 and 22 percent lower perplexity loss than QuaRot and QoQ. Remember that those two keep the query and the scores in FP16, while P3-LLM quantizes the scores to 8 bits on every model, and the query too on Llama-3 and Mistral. " +
    "Table V repeats the comparison on reasoning tasks, MMLU, ARC-Challenge and GSM8K, on two instruct models. The average accuracy is 73.69 for P3-LLM, 71.12 for QuaRot and 70.64 for QoQ, with FP16 at 76.30. The gap is largest on Llama-3.2-3B, where the paper argues that calibrated integer methods overfit their calibration data.",
});

figSlide(S_EVAL, {
  fig: "fig_speed",
  title: "4.9× faster and 3.5× more efficient than HBM-PIM",
  body: [
    "7.8×, 4.9×, 2.0× faster than the NPU, HBM-PIM, Ecco: five models, batch 1–8, 4K (Fig. 9).",
    "The speedup peaks at batch 2, where TEP fills both tCCD_S slots.",
    "Energy: 4-bit operands cut DRAM traffic; TEP uses each read twice (Fig. 10).",
  ],
  caption: "Average speedup (Fig. 9) and energy-efficiency gain (Fig. 10) over each baseline: five models, batch 1–8, 4K context. Dashed black line = 1×.",
  notes: "Now speed and energy, Figures 9 and 10, averaged over five models, batch 1 to 8, at 4K context. Coral bars are speedup and teal bars are energy-efficiency gain. P3-LLM is 7.8 times faster than the NPU alone, 4.9 times faster than HBM-PIM and 2.0 times faster than Ecco. Its energy efficiency is 6.3, 3.5 and 2.1 times better than the same three. " +
    "Two patterns in Figure 9 are worth pointing out. First, HBM-PIM beats the NPU at batch 1 and 2 on every model; at batch 4 its advantage shrinks for Llama-2 and disappears for the GQA models, Llama-3 and Mistral, because the NPU exploits the reuse that HBM-PIM cannot. Second, P3-LLM's speedup peaks at batch 2, where TEP fills both tCCD_S slots. " +
    "The energy saving has two sources: 4-bit operands cut DRAM traffic, and the PCU is cheaper. HBM-PIM's linear-layer energy grows with batch size, because it re-reads the weights for every request; TEP reuses each read twice, which cuts that repetition. " +
    "Two more results that are not drawn here: P3-LLM is 3.4 times faster than an enhanced W8A8KV8 version of Pimba, Figure 12, and from batch 8 it moves the linear layers back to the NPU, Figure 16, because PIM becomes compute-bound.",
});

figSlide(S_EVAL, {
  fig: "fig_area",
  title: "The wider PCU costs 1.1 points of HBM die area",
  body: [
    "PCU compute area grows from 7.7 to 8.4 mm²: the overhead rises from 16.4 % to 17.5 %, under the cited 25 % limit (Table VII).",
    "Per PE: 4 MACs per cycle at 0.18 pJ per MAC, 3.8× better than the FP16 PE (Table VIII).",
  ],
  caption: "(a) HBM area overhead, Table VII; dashed line = the 25 % limit cited from prior work. (b) Energy per MAC of four PE designs at 1 GHz, Table VIII.",
  notes: "The last result is cost, from Table VII and Table VIII. On the left is the HBM area overhead, the fraction of the HBM die taken by PIM logic. HBM-PIM's is 16.4 percent and P3-LLM's 17.5 percent, both under the 25 percent maximum logic ratio that the paper cites from prior work. The difference, 1.1 points, comes from the PCU compute area growing from 7.7 to 8.4 square millimetres, while the buffer stays at 6.2. " +
    "On the right is energy per MAC for four processing-element designs at 1 gigahertz, from Table VIII. The FP16 HBM-PIM PE does one MAC per cycle at 0.69 picojoules. MANT and BitMoD do two MACs per cycle at 0.40 and 0.61. P3-LLM's PE does four MACs per cycle at 0.18 picojoules per MAC, which is 3.8 times better than the FP16 PE, at 1.08 times its area. The paper notes that BitMoD pays for an FP32 accumulator and MANT for a wide partial-sum adder. " +
    "One caveat from Section VI-C: the area count includes only HBM-PIM's MAC hardware; its instruction decoder and other operators are left out. And recall from the methodology that these areas come from 28-nanometre synthesis with a flat ten-times DRAM penalty.",
});

// ---- Discussion
d.section(S_DISC);
outlineSlide(S_DISC, 5, "Part six, discussion. I first show where the speedup comes from, using the paper's own ablation, and then six open questions in two groups, hardware and method. From here on, points tagged BRAINSTORM are our reading, not the paper's claims.");

figSlide(S_DISC, {
  fig: "fig_ablation",
  title: "Quantization gives most of the gain; TEP adds 1.6×",
  body: [
    "Over FP16 HBM-PIM at batch 2 and 4: W4A8KV4 alone gives 3.3×, TEP another 1.6×, 8-bit scores another 1.2× (Fig. 15).",
    "[BRAINSTORM] A 4-bit-weight baseline would shrink the headline; these batches differ from those of the 4.9× average.",
  ],
  caption: "From the paper's Fig. 15: five models, batch 2 and 4; each factor is over the step before.",
  notes: "To start the discussion, here is the paper's own architecture ablation, Figure 15, averaged over five models at batch 2 and 4 and normalized to FP16 HBM-PIM. Each box multiplies the step before it. Quantizing to W4A8KV4 alone gives 3.3 times. Adding TEP gives another 1.6 times. Adding 8-bit attention scores, which lets attention run on the PCU, gives another 1.2 times. " +
    "From here on, what I say is my own reading, tagged BRAINSTORM, not the paper's claims. Most of the gain is quantization: four-bit weights cut DRAM traffic against an FP16 baseline. The PIM micro-architecture idea, TEP, is the 1.6 times. So a baseline that already used 4-bit weights would make the headline look smaller. " +
    "Also note that the ablation uses batch 2 and 4, while the 4.9 times average covers batch 1 to 8. So the ablation factors are not parts of the 4.9 times, and multiplying them together does not give it. " +
    "A question for the group: what is the right baseline for a PIM paper like this one, FP16 PIM, which is what the hardware vendors ship, or PIM at the same precision, which isolates the hardware idea?",
});

{
  const sl = newSlide("CONTENT", S_DISC, "content");
  sl.addText("Open questions on the hardware [BRAINSTORM]", { placeholder: "title" });
  cards(sl, [
    ["Would a DRAM vendor accept TEP?", "The PCU must close timing at tCCD_S (500 MHz on HBM2) in a DRAM process, with a weight slice held for a whole tCCD_L."],
    ["One PIM command per input", "Fig. 7 draws one command per input vector, so reuse deeper than 2 needs more command slots; our CoDe work studies this limit."],
    ["“Edge” means HBM2 here", "The paper says TEP carries over to LPDDR, whose tCCD_S is also half of tCCD_L, but does not evaluate it (§VII)."],
  ]);
  band(sl, ["[BRAINSTORM] Our reading, not the paper's claims."]);
  notes(sl, "These three questions are about the hardware, and they are our reading, tagged BRAINSTORM, not the paper's claims. " +
    "First, would a DRAM vendor accept TEP? It needs the PCU to close timing at tCCD_S, 500 megahertz on HBM2, inside a DRAM process, and it needs a weight slice to stay valid at the PCU for a whole tCCD_L window. The paper argues that the low-precision PCU can reliably reach twice HBM-PIM's frequency, and it gives a simulated power figure, plus 28 percent; the question is whether that holds in a real DRAM process. " +
    "Second, command bandwidth. Figure 7 draws a separate PIM command per input vector: W1 times A1 and W1 times B1 each have their own command. So reuse deeper than two would need more command slots on the command bus. TEP stops at depth two, the gain peaks at batch 2, and from batch 8 the linear layers leave PIM anyway. Our group's CoDe work studies this command-bound limit; I will not go into it here. " +
    "Third, edge means HBM2 in this paper, while phones use LPDDR. Section VII says TEP carries over to LPDDR, where tCCD_S is also half of tCCD_L, but the paper does not evaluate it.");
}

{
  const sl = newSlide("CONTENT", S_DISC, "content");
  sl.addText("Open questions on the method [BRAINSTORM]", { placeholder: "title" });
  cards(sl, [
    ["Frozen smoothing factors", "A decode-time key can exceed its channel's prefill maximum; the paper does not say what happens then."],
    ["Pre- or post-RoPE, per family", "Chosen from profiling at 4K; pre-RoPE models keep Q·Kᵀ on the NPU, which costs speed at long context (Fig. 11)."],
    ["Model outputs, not silicon", "An in-house simulator and a flat 10× DRAM area factor give the numbers; the baseline perplexities use 2K context, speed 4K."],
  ]);
  band(sl, ["[BRAINSTORM] Our reading, not the paper's claims."]);
  notes(sl, "Three more questions, about the algorithm and the method, again our reading and not the paper's claims. " +
    "First, the key smoothing factors are frozen after prefill. A key generated during decoding can exceed its channel's prefill maximum and fall outside minus one to one. The paper does not discuss what happens then, for example whether such values are clipped, or how often it occurs in long generations. " +
    "Second, pre-RoPE versus post-RoPE key quantization is chosen per model family, from profiling at 4K context. Pre-RoPE models, Llama-1 and 2, keep Q times K-transpose on the NPU, which costs speed at long context; Figure 11 shows Llama-2-7B gaining less as the context grows. A new model family would need new profiling. " +
    "Third, these are model outputs, not silicon. The simulator is in-house, the NPU model follows NeuPIMs, the PIM model follows Newton, and area is scaled from 28-nanometre logic with a flat ten-times DRAM penalty. Also, the perplexity comparison with the baselines, Table IV, uses 2K context while speed uses 4K; the format studies in Tables II and III use 4K. " +
    "Which of these six questions should we spend the most time on?");
}

d.closingSlide(S_DISC, {
  title: "Questions",
  recap: nb("P3-LLM shrinks every operand to 4 or 8 bits and runs a PCU with 4× the multipliers at tCCD_S, so each weight read serves two inputs: 4.9× the speed of HBM-PIM at 17.5 % area overhead (Fig. 9, Table VII)."),
  citation: "Y. Chen et al., “P3-LLM: An Integrated NPU-PIM Accelerator for Edge LLM Inference Using Hybrid Numerical Formats”, arXiv 2511.06838v4, 2026. Code: github.com/yc2367/P3-LLM.",
  questions: ["Is TEP's timing realistic in a DRAM process?", "The right baseline: FP16 or same-precision PIM?", "Does it transfer to LPDDR on a phone?"],
  notes: "That is the paper. To recap: P3-LLM shrinks every operand to four or eight bits, with a format chosen per operand. That lets a PCU with four times the multipliers fit into about the same area, and the PCU is clocked at tCCD_S so that each weight read serves two inputs. The paper reports 4.9 times the speed and 3.5 times the energy efficiency of HBM-PIM, at an HBM area overhead of 17.5 percent. " +
    "I am happy to take questions. To open the discussion, I suggest the three questions on the right. First, whether TEP's timing is realistic in a DRAM process. Second, what the right baseline is: FP16 PIM, or PIM at the same precision, which would isolate the hardware idea from the quantization. Third, whether the design transfers to LPDDR on a phone, where the paper says TEP applies but does not evaluate it. The code is public on GitHub if anyone wants to look at the quantization details.",
});

// ================================================================== write: raw deck + sidecar, then the transplant
d.write(OUT).catch((e) => { console.error(e); process.exit(1); });
