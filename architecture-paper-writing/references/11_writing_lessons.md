# Writing lessons — the author's rules, in the order you write

These are the corrections the author made on rendered drafts, stated as rules. When a per-section guide (`00`–`10`, `12`,
`13`) and a rule here disagree, this file wins, because it records what the author decided after those guides were written.

**How the file is organized.** The rules are grouped in the order a writer meets them, and each has a stable id:

| part | covers | ids |
|---|---|---|
| A | Process: how an edit is planned, approved, cut and checked | A1–A6 |
| B | Structure: sections, paragraphs, headings, order, transitions | B1–B11 |
| C | Openers: how each kind of paragraph starts (one decision table) | C1–C7 |
| D | Content: what a paragraph must claim, and how truthfully | D1–D10 |
| E | Brevity: what to cut | E1–E5 |
| F | Sentences: grammar, references to things, citations | F1–F4 |
| G | Numbers and figures | G1–G7 |
| H | Section-specific: introduction and abstract | H1–H4 |

**Entry format.** Each entry has a **Rule**, a **Why** (with the author's words where they exist) and an **Example**
(before → after). Examples are labelled by the paper they come from: *SPLEX* (ASPLOS submission), *DAC* (DAC draft of CoDe) or
*CoDe* (ISCA submission). The examples illustrate the rule; their numbers belong to those papers.

**Adding a new lesson.** Put it in the part where it belongs, not at the end of the file. If it touches an existing rule,
edit that rule (or state in both which one wins) instead of adding a second rule. Then mirror it as one bullet in the same
part of SKILL.md's contract, and add a row to the index below.

## Index

| id | rule |
|---|---|
| A1 | Plan before edit: outline first, the edit plan goes to the author, nothing is pushed without approval |
| A2 | Verify a plan's premise before executing it |
| A3 | Adopt clean author edits; flag deviations, never revert them |
| A4 | Cuts drop the clause, never rewrite the fact |
| A5 | Shortening cuts qualifiers, never a number, control or promise |
| A6 | Every deletion, merge or move runs the promise check |
| B1 | One role per paragraph; the section's arc is visible |
| B2 | Define before use; background defines, it does not preview the design |
| B3 | Order items so each one leads into the next |
| B4 | Never merge measurement paragraphs of different kinds |
| B5 | Delete rather than merge a paragraph that does not serve the argument |
| B6 | One paragraph per agenda in a mechanism introduction |
| B7 | The borrowed-mechanism paragraph |
| B8 | Headings are noun phrases |
| B9 | A run-in head marks a sibling topic, and only where it helps |
| B10 | Transitions at turning points: map once, never re-map |
| B11 | One configuration table, referred to everywhere |
| C1 | The opener decision table (which opener for which paragraph) |
| C2 | Core message first, then details |
| C3 | Setting before finding |
| C4 | Plain opener for a term the paper defines |
| C5 | A figure paragraph: what the figure shows, then the setup, then the details |
| C6 | A cause paragraph states the cause directly |
| C7 | A subsection opener frames; the numbers go in the paragraphs below it |
| D1 | Each prior-work family is introduced by its defining trade-off or limit |
| D2 | Mark the terms the paper coins as its own |
| D3 | Justify a modelling choice with the prior work it follows, and attribute only what that work does |
| D4 | The informative statistic, not the trivial one |
| D5 | Constrained results are a trade, not a gap |
| D6 | No invented interfaces |
| D7 | No fabricated verification |
| D8 | No evaluative adjective without the two quantities it compares |
| D9 | State a cost at its unit, then scale it to the system |
| D10 | Say what a component does, not what it does not |
| E1 | The sentence test |
| E2 | No repetition at the sentence level |
| E3 | Scope of detail: cut what does not serve the message or confuses it |
| E4 | Shares over raw values; one worked case instead of every value |
| E5 | No audit trail in method and evaluation prose |
| F1 | Every clause has a visible subject and a finite verb |
| F2 | Name, don't point |
| F3 | No questions to the reader |
| F4 | Cite at the proper noun |
| G1 | Pace the numbers: one or two per sentence, description after each |
| G2 | A series the figure carries is printed at its endpoints |
| G3 | A figure citation says what to see |
| G4 | Minimal captions |
| G5 | One float per spot |
| G6 | The figure visual system |
| G7 | Numbers are traced, rounded once, and asserted |
| H1 | The introduction rules |
| H2 | The abstract opens on the problem and joins every move to the last |
| H3 | The abstract's move order |
| H4 | An abstract or section opening states the positive finding |

---

## A. Process

### A1. Plan before edit: outline first, the edit plan goes to the author, nothing is pushed without approval

**Rule.**
- **Structure lives in `outline.md`.** Any change of structure (add, cut, merge or move a paragraph, change its message,
  move a float) is made in the outline first, then the `.tex` follows, and both are committed together (`13`).
- **When the author is reviewing, the plan comes first.** Answer a set of comments with an edit plan: for each comment, the
  outline change and the before → after sentence. Edit only after the author approves; if the author changes the plan, edit
  the plan, not the paper.
- **Push only on approval**, and say what will be pushed.

**Why.** The author reviews structure paragraph by paragraph ("give me the outline paragraph by paragraph with core message
each"), and repeatedly adjusted a plan before approving it (CoDe, 2026-10-27/28). An edit made before that review is work the
author must undo.

### A2. Verify a plan's premise before executing it

**Rule.** When an instruction reads "do X, because Y" and Y is a measurable property of the render, measure Y first; if the
measurement kills the premise, leave the author's state untouched, deliver what the edit was for, and report the table and the
one tested alternative as the author's call.

**Why.** An order built on a false premise ships a regression in the author's own work. Do not take a forbidden option on your
own judgement even when it measures best; put the finding in the commit message and the status file, not only in the report.

**Example** *(SPLEX)*. "Set the three text boxes to a common x = 4 because the boxes are shrink-wrapped; do not touch
`align=center`" → measured: neither half held, and the letter of the plan would have replaced the author's 1.0 px alignment
with an 8.5 px stagger. The real deliverable (the alignment had never been exported into the paper) shipped; the alternative
was reported. `pdfinfo` the current figure before trusting a quoted canvas size.

### A3. Adopt clean author edits; flag deviations, never revert them

**Rule.** Adopt the author's figures or text that pass (numbers hold, render clean), hold the one that does not with a fixed
variant ready, and report deviations in palette, wording or label content instead of reverting them.

**Why.** An all-or-nothing hold stalls good work over one accidental connector, and silently editing the author's content
reverts a deviation the instructions said only to flag. "Stop if a number changed" means a measured value from the generator's
asserts, not a label.

**Example** *(SPLEX)*. An author-edited figure replaced "HBM3E stack" with "HBM stack"; every measured value was byte-identical
and the label matched the caption → adopted and flagged. A sibling figure with a broken connector → held, clean variant
exported.

### A4. Cuts drop the clause, never rewrite the fact

**Rule.** Remove a number by dropping the clause that carries it, never by restating the fact in a shorter but different form;
fix a seam by rewording a neighbour, never by adding a bridging sentence. If a fact must leave to meet a cap, say where it still
lives (table, caption, audit row).

**Why.** A restated fact is a new claim that may be false; a bridging sentence is rhetoric that the next pass deletes.

**Example** *(SPLEX)*. To lose "47 of the 48 GiB" the allocation clause was dropped, not rewritten as "48 GiB was allocated" —
which never happened.

### A5. Shortening cuts qualifiers, never a number, control or promise

**Rule.** A "N % shorter" request removes qualifiers only — every number, named mechanism, control and cross-section promise
stays — and the report gives before/after counts, the counter used, and whether any heading or float moved.

**Why.** Facts settled in an earlier pass are not reopened by a space request. A correctness pass may set the page limit aside
(ship, report the float map, say how many lines must come back); a gated pass has the author name what to cut. Never cut a
result or a float placement to close a residual; stop and report it.

**Example** *(SPLEX)*. "as for any larger device memory", "(cleared at exit)", "admitted / resident / the engine's" went; the
register name, every number, the control and the promises to the design section stayed.

Contrast with E2–E4: those rules decide *which content* the author wants gone (repetition, out-of-scope detail, raw values).
A5 governs a pure space request, where the content is already settled.

### A6. Every deletion, merge or move runs the promise check

**Rule.** Before removing a sentence, a paragraph or a number, grep the rest of the draft (sections, tables, scripts, outline
links) for what depends on it: a later "Section X shows", a number printed nowhere else, an outline link. A heading may
disappear; a claim may not. Procedure: `10`.

**Example** *(CoDe)*. Deleting III-C's "Row-switch commands in prior designs" paragraph: IV-C's "the two families of Section
III-C tie the tokens of a row sweep to one MAC slot" still had a source (the closing of the next paragraph and Table I's A
column), so the deletion went ahead with one pointer added in IV-C ("A = 2 and 4 in Table I").

---

## B. Structure

### B1. One role per paragraph; the section's arc is visible

**Rule.** Each paragraph has one role in the section's argument, and the roles follow an arc the reader can name: for an
opportunity subsection, *what is possible* → *why it is physically feasible* → *what the design does with it*. A paragraph
that serves two roles is split; a paragraph whose role another already serves is cut (B5).

**Why.** The author (CoDe, 2026-10-29): "For me, the III.D has three paragraph. First one which tells PU should be faster more
than column command restricts. The second paragraph tells this is possible physically. And, the last paragraph hints what will
be discussed in the design section."

### B2. Define before use; background defines, it does not preview the design

**Rule.**
- **Every symbol and term is defined where it first appears**, in plain words, and later paragraphs point back to that
  definition instead of re-deriving it.
- **Background defines the mechanism of the prior system and stops there.** It never states what the paper's design will do
  with it ("so a PU clocked at CK could run D beats"); that sentence belongs to the opportunity or design section.
- A definition the design needs is still given in background, neutrally ("We call D, the number of CK cycles in one column
  period, the depth").

**Why.** The author (CoDe, 2026-10-28) cut a background clause because "this is our design which will be addressed later",
and on 2026-10-29 asked "did you define or explain what D is? if not, please add one sentence".

**Example** *(CoDe)*. II-B "This column period t_col spans D = 4 cycles t_CK of the command clock CK" (D never defined) → adds
"We call D, the number of CK cycles in one column period, the depth; t_col equals D × t_CK." Nothing about PUs running D beats.

### B3. Order items so each one leads into the next

**Rule.** When a section treats several items (causes, families, mechanisms), order them so the reader's view narrows step by
step, or so each item sets up the next. Announce the order once, in the transition that lists them (B10). A later section may
keep a different order when its own logic needs it; say nothing about the switch.

**Why.** The author (CoDe, 2026-10-28) proposed covering the non-MAC commands (time *between* the MAC slots) before the idle
beats (time *inside* them): the reader zooms from the GEMM's time to the slots to the beats.

### B4. Never merge measurement paragraphs of different kinds

**Rule.** Merge only paragraphs that measure the same kind of thing; two findings of different kinds each keep their own run-in
head, even at zero page slack.

**Why.** A reader finds a finding by its head and by the claim sentence under it. Ask what each paragraph's unit is (per pair of
steps, per window, per decode); different units mean different heads. The enumeration in a section's opening of what prior work
does not capture is the breadth claim and survives a trim.

**Example** *(SPLEX)*. Retention (a pairwise measure) bundled with the 64-step working set (a set-level measure no prior system
computes) → reverted by the author.

### B5. Delete rather than merge a paragraph that does not serve the argument

**Rule.** When a paragraph's content is minor for the section's message (a small share, an artificial case) or restates what
other paragraphs and a table already carry, delete it. Move a fact out only when another section needs it, and to the place that
uses it. Do not fold it into a neighbour as one more sentence just to keep it.

**Why.** The author (CoDe, 2026-10-29) asked whether token load deserved its own paragraph (it took 0.6–2.4 % of the real
kernel), then preferred deleting the rival row-switch paragraph outright over merging its sentences into the family paragraphs:
"How about just deleting that paragraph without any merging?"

**Example** *(CoDe)*. III-B "Token load matters only where one GB fill serves few row sweeps …" → paragraph deleted; its shares
became one clause in the row-switch paragraph, and its one-kernel 28.3 % moved to the evaluation sentence that relies on it.

How B4 and B5 fit together: B4 forbids merging two *findings*; B5 removes content that is *not* a finding the section needs.

### B6. One paragraph per agenda in a mechanism introduction

**Rule.** Two or three paragraphs — definition and validity; interface; cost and deadline. Not one paragraph carrying all
three, not four that split one agenda.

**Why.** A paragraph break tells the reader the agenda changed; a single long paragraph hides the change, and extra breaks
announce changes that did not happen.

### B7. The borrowed-mechanism paragraph

**Rule.** A passage that adopts a mechanism from prior work is its own paragraph in this order: what we want to do → why it is a
problem → "we adopt X's answer" with the citation there → our instance, named so it cannot be confused with X's → the one rule
the reader needs → what stays fixed. The total word count may not grow.

**Example** *(SPLEX)*. "the region table, like RDMA's page list, …" inside a head paragraph → a separate paragraph: resolve slot
addresses without a per-page list → a page list per pool is too large → "we adopt GPUDirect RDMA's answer [cite]" → "the
migration engine's region table" → address = base + slot × stride → the bases are fixed for a pool's lifetime.

### B8. Headings are noun phrases

**Rule.** Section titles, subsection titles and run-in `\paragraph` heads all name a topic as an engineering noun phrase: never
a sentence, a where / how / why clause, or a result with a number. One labelled thesis title per section is allowed ("The
Opportunity: DRAM Timing Bounds Access, Not MACs"). The claim goes in the first sentence under the heading (C1).

**Why.** Sentence heads ("Six designs widen the MAC step with multipliers", "Where PIM and Host Cross") read as slogans; a
heading is a label the reader scans (DAC, 2026-10-17). Full rule and grep check: `01` §5.3.

**Example** *(DAC)*.

| before | after |
|---|---|
| "Where PIM and Host Cross" | "PIM–Host Crossover" |
| "Edge Server: 1.68× P3-LLM-Style's Batched Decode Speed" | "Edge-Server Platform against P3-LLM-Style" (1.68× moves to the first sentence) |
| run-in "A faster PU stops at two tokens per read" | run-in "Faster-PU family" |
| run-in "Hotness persists far beyond the next step." *(SPLEX)* | "Hotness over time", first sentence "Hot entries stay hot for hundreds of steps." |

### B9. A run-in head marks a sibling topic, and only where it helps

**Rule.** Run-in heads label topics *of the same kind* (two families, two root causes). A paragraph that looks at the same
items from another angle, or that continues one argument, gets no head: a head would make it look like one more sibling. A
subsection whose paragraphs form one argument (B1) needs no run-in heads at all.

**Why.** The author (CoDe, 2026-10-29), on a head "Row-switch commands in prior designs" placed after "Wider-PU family" and
"Faster-PU family": "I thought that we have only two sorts of previous works." The author also removed III-D's only run-in
head: "we don't need 'a)' mark as indented paragraph".

### B10. Transitions at turning points: map once, never re-map

**Rule.**
- **Where:** one transition sentence where the argument changes mode: observation → analysis; a list of causes → the first
  cause; the end of a section → the next section's components. Elsewhere paragraphs follow on without one.
- **What it carries:** it names what follows and maps it, so it carries content: "Stock AiM thus loses useful MAC beats to two
  root causes: non-MAC commands between the MAC slots, and idle beats inside them."
- **A section's last paragraph bridges causally** into the next section: what was shown, therefore what the design does —
  "A PU at CK thus fits in a DRAM die, and the wider-PU family shows how much logic area a PIM die already gives to filling
  idle beats. We therefore keep the stock multipliers, run them at CK within that area, and answer each root cause … with one
  lever."
- **Map once.** After the reader has the map, do not repeat it at the next turning point ("idle beats set the slot factor,
  non-MAC commands set the sweep factor") — the reader already knows it.
- **Never** "we explain them one by one next" with nothing named. A clause that names the items and their order ("the next
  paragraphs take the two families in turn") is part of a mapping sentence and is allowed.

**Why.** The author (CoDe, 2026-10-27): the observation → analysis sentence "is the right transition … We need transition
sentences at important moments, not every time." On 2026-10-29 the author cut a repeated mapping: "this one is also
repetitive. The readers would already know this at this moment", and asked the opportunity subsection to end on "based on this
observation … and wider PU family's excessive area usage, we tackle the two root causes, and following section will discuss".

### B11. One configuration table, referred to everywhere

**Rule.** Every hardware and configuration value lives in one methodology table: the platform block (host, DRAM standard and
rate, t_CK, column period, channels, banks, row size) above the design block (lanes, PU clock, depth, buffers, area, power).
- **First use:** the prose defines the concept and points to the table: "the command clock CK (t_CK in Table II)".
- **Later uses** refer to the table instead of reprinting the value; values are repeated only where a sentence computes with
  them.
- **Float placement:** the table sits in methodology even when earlier sections cite it — the one exception to G5.

**Why.** The author (CoDe, 2026-10-27): "have a table at the methodology section for the whole configuration and refer this
table across the paper … if you use this concept for the first time … explain it first and refer the table."

**Example** *(CoDe)*. "the cycle t_CK is 1.25 ns on the mobile platform and 1 ns on the edge server", printed in §III, §IV and
§VI → printed once, in the table; each section writes "t_CK (Table II)".

---

## C. Openers

### C1. The opener decision table

Every paragraph opens with its core message (C2), but what "core message" means depends on the paragraph's kind. Pick the row;
the rules C2–C7 give the details. This table replaces the older single rule "the finding opens the paragraph", and it decides
every disagreement with a section guide about first sentences (`02` §2, `06` §B4, `09` §B, `13`).

| paragraph kind | first sentence | then |
|---|---|---|
| section or subsection opener (C7) | the frame: the parts, families or causes, and the figure that shows them; no numbers | one mapping clause (B10) |
| figure-setup paragraph (C5) | what the figure shows | basic setup → details → pointer to the table or methodology |
| paragraph that explains a term the paper defines (C4) | one plain, symbol-free sentence saying what the thing is | setting → cause → definition and equation → value → cost |
| paragraph that explains a cause (C6) | "X arises because Y": the cause, stated directly | mechanism → evidence → consequence |
| measurement or finding, setting already established (C2) | the blunt finding, scale in words, no number | the number in the next sentence |
| measurement or test whose setting is new (C3) | the setting: what, on what, how | the finding within one or two sentences |
| prior-work family (D1) | the family's defining trade-off or limit | mechanism → representative → its numbers |
| paragraph that answers a familiar alternative | that alternative and its logic | the number showing where it falls short |
| design mechanism under a run-in head (`08`) | the definition of the mechanism the head names | validity → payoff → figure → implementation → cost |
| evaluation result (`06`) | the claim | the figure pointer, then the evidence |
| abstract, or a section's first paragraph (H4) | the positive finding, never the negation of something not yet introduced | — |

The familiar-alternative row, by example *(SPLEX)*: "The natural alternative to tracking selections is to keep the most recent
positions resident, as a sliding-window cache does." The number that follows says where it falls short; the author singled this
opener out as the way to show the contribution to readers who know the alternative.

When two rows seem to apply, the more specific row wins: a cause paragraph about a term the paper defines uses C6 if its job is
the cause, C4 if its job is the term. A paragraph has one job (B1).

### C2. Core message first, then details

**Rule.** The first sentence says the one thing the paragraph is for, directly and in plain words; the details follow in the
order the reader needs them. The first sentence is blunt and general, with a concrete subject, a plain verb and the scale in
words; it is not the measurement itself (the number opens the next sentence) and not an abstraction or an evaluation ("Recency
is not the signal", "The deadline is loose").

**Why.** The author (CoDe, 2026-10-28) on II-B: "a direct opener, 'MAC commands need non-MAC commands before and after them' …
start with the opening message and going to details."

**Example** *(CoDe)*. A paragraph that walked through WRGB, WRMAC16, TMOD, PREA and ACT16 before saying why → opens with "MAC
commands need non-MAC commands before and after them", then the commands in their fixed order. *(SPLEX)* "Hot entries stay hot
for hundreds of steps." opens the hot-set paragraph; the measured fractions follow.

### C3. Setting before finding

**Rule.** A paragraph that reports a measurement, a test or a mechanism whose setting the reader does not yet have opens with
that setting, then states the finding.
- **The setting** says what is measured, on what and how, and names the parts the finding is about: define each, or point back
  to the figure or section that defined it.
- **A test or variant is described before it is named.** Say what was replaced by what, then the result, then what it shows.
- **A term a later section introduces never appears here.**
- When the previous paragraph or the subsection opener already gave the setting, C2 applies: the finding opens.

**Why.** The author (CoDe, 2026-10-27): "A faster-PU test confirms …" "comes out of nowhere. The readers would not know what
faster-PU is at this moment"; in the breakdown paragraph "you must explain the circumstance first like there are MAC command
and non-MAC command". A brief statement of the setup and of how it was measured is wanted, not cut.

**Example** *(CoDe)*. "A faster-PU test confirms that the command count, not the PU's arithmetic, sets the time …" → "Replacing
stock AiM's PU, one beat per column period, with one four times faster, clocked at CK, leaves every stock GEMM at the same
number of cycles."

### C4. Plain opener for a term the paper defines

**Rule.** A paragraph that explains a term the paper defines (an inefficiency, a mechanism, a factor) opens with one plain
sentence saying what the thing is in everyday words — no symbol, no variable, no coined term. Then: the setting it lives in,
its cause, its formal definition and equation, its value, its cost. Never open with the equation or with a citation trail.

**Why.** The author (CoDe, 2026-10-28): the idle-beat paragraph should start "like 'idle beats mean un-useful clock of tCK
between two MAC commands' … a direct and simple sentence opening without any professional or technical variables".

**Example** *(CoDe)*. "The slot factor U_MAC = A × b × t_CK / t_slot counts …" → "An idle beat is a CK cycle in which a PU has
nothing to compute. A column period holds D = 4 such cycles, or beats (Section II-B), and a beat is useful when it computes a
token's MAC."

### C5. A figure paragraph: what the figure shows, then the setup, then the details

**Rule.** A paragraph that introduces a figure's experiment opens with what the figure shows ("Fig. 2 plots skinny-GEMM
throughput against M …"), then the basic setup a reader needs to read it (kernels, sizes, which platform is which), then the
remaining details, closing with the pointer to the configuration table or methodology. Never open with provenance ("Throughput
numbers in this section are modelled on …"). Each later paragraph about the figure explains only its own segment's background.

**Why.** The author (CoDe, 2026-10-28): "we need to open it with what figure 2 tries to show. And, leave the details at the end
if some reader who wants more detail would go to table III."

### C6. A cause paragraph states the cause directly

**Rule.** A paragraph whose purpose is to explain why an inefficiency happens opens by naming the cause as the cause: "X arises
because Y". The mechanism, the evidence and the reason the cause made sense for its original target follow.

**Why.** The author (CoDe, 2026-10-29): "this paragraph's purpose is to show the reason of idle beats … The core message should
be more direct. We want to show the reason of idle beat, then say it as it is."

**Example** *(CoDe)*. "In stock PIM, a MAC starts only when a column command delivers its weights." → "Idle beats arise because
the column command, not the PU, paces every stock MAC: a MAC starts only when a column command delivers its weights."

### C7. A subsection opener frames; the numbers go in the paragraphs below it

**Rule.** A subsection's opening paragraph names what the subsection examines (the families, the causes) and the figure that
shows them, and maps the order (B10). Counts, cycle tallies and figure walk-throughs belong to the paragraph about each item.

**Why.** The author (CoDe, 2026-10-29) on the III-C opener: "These sentences are too detailed with numbers as a part of opening
paragraph … the explanation should be on a) and c) for how many commands during how many time period."

**Example** *(CoDe)*. "Fig. 4 follows one weight column of one bank through M = 8 tokens, in column periods T of D = 4 beats
each. Its first three rows … start every MAC with a command, and stock AiM spends 8 column periods, 8 commands and 8 reads" →
"Prior PIM designs fill the idle beats in two families, with more multipliers or with more commands (Fig. 4). Fig. 4 follows
one weight column through eight tokens in stock AiM and in one design of each family, LP-Spec for more multipliers and P3-LLM
for more commands; the next paragraphs take the two families in turn." The 8 / 2 / 4 counts moved to each family's paragraph.

---

## D. Content

### D1. Each prior-work family is introduced by its defining trade-off or limit

**Rule.** The first sentence about a family of prior designs states what the family trades or what bounds it — the property the
paper's design changes — not a count of its members or a description of its mechanism. The paragraph then shows that limit in
the representative design. The limit is stated as a property of the family, without naming the paper's design (motivation
sections mention their own system at most once, last).

**Why.** The author (CoDe, 2026-10-29): for the wider-PU family "you missed the most important thing. this family trades more
compute with area. please emphasize it"; for the faster-PU family "they are bounded by coupling MAC with column command which
makes them to be restricted by column timing rules … this gives our CoDe novelty. this is very important."

**Example** *(CoDe)*.

| before | after |
|---|---|
| "Six designs widen the MAC step with multipliers." | "Wider-PU designs trade area for MAC throughput: they fill the idle beats with more multipliers per PU." |
| "A faster PU paced by per-token commands fills at most two beats per column read." | "Faster-PU designs speed up the PU but still start every MAC with a command, so DRAM command timing, not the PU clock, caps them at two beats per column read." |

### D2. Mark the terms the paper coins as its own

**Rule.** When the paper introduces its own metric or term, say so at the definition: "We define … as the sweep factor f_MAC",
"We call D … the depth". A reader must be able to tell a term of the field from one this paper made.

**Why.** The author (CoDe, 2026-10-29): "edit this one to let reader knows the fMAC term is what we made for our paper."

### D3. Justify a modelling choice with the prior work it follows, and attribute only what that work does

**Rule.** A modelling choice that could look arbitrary (precision, placement, a clock) is tied to the prior design it follows,
with the citation, in one sentence. Attribute only what the cited work actually does: when the model differs in some respect,
name the shared property, not the whole configuration.

**Why.** The author (CoDe, 2026-10-29) asked to cite LP-Spec and P3-LLM for the INT8 and W4A8 choices and "add one sentence to
emphasize it". The quoted "as LP-Spec does" was narrowed because LP-Spec shares one unit between two banks, while the model
places one per bank.

**Example** *(CoDe)*. "The mobile platform places an INT8 PU beside each LPDDR5-6400 bank, and the edge server places a W4A8 PU
beside each pair of HBM2 banks (Table III)." → adds "Each platform computes at the precision of the prior PIM design that
targets it, LP-Spec~\cite{lpspec} on the mobile platform and P3-LLM~\cite{p3llm} on the edge server."

### D4. The informative statistic, not the trivial one

**Rule.** A headline cites the statistic that justifies the mechanism, not the one prior work already stops at; every headline
verb gets a concrete object.

**Example** *(SPLEX)*. "0.79 of the selection recurs at the next step" (what prior systems already use) → "still selected 0.64 of
the time 64 steps later and 0.35 after 1024 steps".

### D5. Constrained results are a trade, not a gap

**Rule.** When the system matches an unconstrained baseline within a tolerance, name what the cap bought, with the tolerance and
the cap in the same clause, in the paper's own unit.

**Example** *(SPLEX)*. "within 0.013 under a 32-swap budget" → "within 0.013 while capping migration at 32 swaps per layer per
step" — the unbudgeted LRU pays up to 3.6× the traffic for that last 0.013.

### D6. No invented interfaces

**Rule.** Name only mechanisms, calls, registers and structures that a design document or a measurement record defines; never
coin a name to make a paragraph concrete. When a word budget and the fact list conflict, keep the facts and report the
candidates to cut.

**Example** *(SPLEX)*. `splexPinRegion` / `splexSetHotBudget` lived in the draft and nowhere else → deleted.

### D7. No fabricated verification

**Rule.** Classify every sentence about a driver, runtime or framework as *run*, *read from source* or *design*. A mechanism
read from source is described in the present tense with its source cited — never "verified / measured / run", and equally never
"not run / assumed / only one flag is missing".

**Example** *(SPLEX)*. "Range-bounded placement was documented but not run" → "The driver places a buffer by the range its
allocation flags name [source]."

### D8. No evaluative adjective without the two quantities it compares

**Rule.** "Loose", "small", "negligible", "ample" are replaced by the two numbers being compared, in one sentence.

**Example** *(SPLEX)*. "The deadline is loose." → "The swaps take microseconds against a deadline of one decode step, tens of
milliseconds."

### D9. State a cost at its unit, then scale it to the system

**Rule.** Give a cost at the smallest unit it is defined on, then carry it to the level the reader cares about, in the same
sentence.

**Why.** The unit figure is verifiable and the system figure is what matters; together they show the arithmetic. The author
singled this out as the move liked most.

**Example** *(SPLEX)*. "Swaps are capped at 32 per sequence per layer per decode step, about 50 KB in each direction per
sequence per layer per step."

### D10. Say what a component does, not what it does not

**Rule.** Roles are stated positively; "never decides", "does not choose" and similar negated roles are cut.

**Example** *(SPLEX)*. "The engine never decides what to move; that decision is the policy's, and the engine only executes it."
→ "The engine executes the policy's swap list."

---

## E. Brevity

### E1. The sentence test

**Rule.** Delete any sentence that carries no fact, no number and no necessary forward reference. Delete drum-rolls,
self-praise, meta-commentary and personification; the preferred repair is a direct sentence, a colon, and the facts (`01` §2–4).
A display equation that restates a table is a duplicate. A roadmap sentence at a `\section` opening and a minimal run-in framing
("Three goals shape the design.") survive.

**Example** *(SPLEX)*. "Note what the engine does not contain." → deleted.

### E2. No repetition at the sentence level

**Rule.** Within a paragraph and across adjacent paragraphs, say each fact once. Watch for:
- a sentence that restates the previous one in other words ("A row sweep belongs to one row … stock AiM's row sweep serves one
  token, so stock AiM sweeps each row once per token");
- a definition given twice in one paragraph (a beat is one CK cycle; the PU computes the beat in one CK cycle);
- a closing clause that repeats the opener ("…: the command spacing, not the PU clock, sets each MAC slot" after an opener
  saying the same);
- a paragraph that re-explains what background or the previous subsection defined; point back instead ("Non-MAC commands
  (Section II-B) stall every PU");
- a count stated three times ("at most two" in the opener, the mechanism and the cap).

A clarifying repeat of a *noun* (F2) is not repetition; a repeated *claim* is.

**Why.** The author (CoDe, 2026-10-29): "this sentences are repetitive and redundant … We need to reduce this repetitiveness and
redundances in the sentence level."

**Example** *(CoDe)*.

| before | after |
|---|---|
| "Even the MAC slots hold wasted time: an idle beat is a clock cycle in which a PU has nothing to compute and waits for the next MAC command. A beat is one CK cycle of PU work, so a column period holds D = 4 beats; a useful beat computes a token's MAC, and the other beats of a MAC slot are idle. Stock AiM's slot serves one token, so the PU computes the token's beat in one CK cycle and waits for the next command:" | "An idle beat is a CK cycle in which a PU has nothing to compute. A column period holds D = 4 such cycles, or beats (Section II-B), and a beat is useful when it computes a token's MAC. Stock AiM's MAC slot serves one token, so one beat of each column period is useful and three are idle (Fig. 1b)." |
| "each column command then moves one 32-byte piece of that row. An LPDDR5 row holds 2 KB, so one column access picks 32 B of the 2 KB" | "An activation opens one row of a bank, 2 KB on LPDDR5, into its sense amplifiers, and each column command moves one 32 B column of that row." |

### E3. Scope of detail: cut what does not serve the message or confuses it

**Rule.** Cut a detail that does not serve the paragraph's message, even when it is true and sourced:
- a validation tolerance on a supporting fact ("within 1.84 % on the mobile platform and 2.7 % on the edge server");
- a side effect outside the claim ("at other M, PIM throughput dips by group quantization");
- an integration note outside the paper's scope (logic-die processes, hybrid bonding);
- an extrapolation to a configuration the paper does not evaluate ("HBM3 … gets D = 2 there");
- a related-work item whose idea is close in words but different in kind, so that it blurs the paper's distinction (Paik et
  al.'s "decouple memory access from computation across banks" next to a paper about decoupling MACs from commands).

What stays: limitations of the evaluated configurations, and every number another section relies on (A6).

**Why.** The author (CoDe, 2026-10-27) marked the first four as "too detailed" or "out of scope"; on 2026-10-29: "delete this.
this makes us confused."

### E4. Shares over raw values; one worked case instead of every value

**Rule.** In motivation and analysis prose:
- **Report a share of the figure's total** (percent of the bar) rather than a list of raw times; the raw values stay in the data
  and the asserts.
- **Show a fitted or derived model with one worked case** (one platform's parameters, then the result), not every platform's
  parameter set; the other platform's result appears where it is used.
- Keep the one raw value a reader needs to judge scale; drop explanations of small fitting artefacts.

**Why.** The author (CoDe, 2026-10-29): "all those ns numbers are too detailed information. please replace them with percentage
ones … Make it simple and clear in percentage"; "I am okay to show ns for one example as a case study and show the final fMAC
is this … current one is too long."

**Example** *(CoDe)*.

| before | after |
|---|---|
| "the simulated row-switch commands take 91.2 ns per sweep. A PU that runs one beat per CK cycle needs 78.0 ns … The two TMODs take … 40.5 ns, and the ACT16 pair … 37.9 ns. PREA takes 11.5 ns, and WRMAC16 takes 1.2 ns." | "the row-switch segment takes 19.5 % of q_proj's time on the mobile platform, more than the useful beats' 18.0 %, and 13.8 % on the edge server. The two TMODs (8.1 %) and the ACT16 pair (8.5 %) take most of the mobile row switch." |
| both platforms' t_row, t_tok, ρ, plus why the fitted t_row lies below 91.2 ns | "Fitted on stock AiM at M = 1 on the mobile platform, t_row is 87.73 ns, t_tok is 4.26 ns and ρ is 0.070, so stock AiM's MAC slots fill f_MAC = 0.717 of a decoder layer's time." |

### E5. No audit trail in method and evaluation prose

**Rule.** Methodology and evaluation give only what the reader needs to interpret the results; a fact in a table is never
repeated in prose, and there are no `Metric.` / `Setup.` / `Systems.` run-ins. Every evaluation subsection opens with one or two
sentences of purpose plus what is compared, by name.

**Example** *(SPLEX)*. "The HBM rates are measured and the C2C link is modeled" while the configuration table already marked
each row → cut.

---

## F. Sentences

### F1. Every clause has a visible subject and a finite verb

**Rule.** No equation stands as a clause on its own, and a sentence fronts at most one setting; a list of settings goes after
the verb. Full rule and check: `01` §5.1.

**Example** *(DAC)*. "At 0.8 GHz on LPDDR5-6400 and 1 GHz on HBM2, D = 4, and a stock PU uses one beat." → "A PU clocked at
0.8 GHz on LPDDR5-6400 or at 1 GHz on HBM2 fits D = 4 beats into each column period; a stock PU uses one of them."

### F2. Name, don't point

**Rule.** Repeat the noun phrase instead of "the two", "both", "it", "this" or "they" whenever the antecedent is outside the
current clause or more than one noun could fit. A clarifying repeat is not restatement (E2). Full rule: `01` §5.2.

**Example** *(DAC)*. "…once the two are separated" → "…once MAC timing is separated from command timing".

### F3. No questions to the reader

**Rule.** Never write a question — neither a sentence ending in "?" nor an "asks whether / the question is / we ask" framing;
state what the section measures, shows or ranks. Before every commit, grep the section files for `?` and for
`asks (whether|how|which|what)|the question|we ask`.

**Example** *(SPLEX)*. "This section asks how much of the selection survives across steps" → "This section measures how much of
the selection survives across steps".

### F4. Cite at the proper noun

**Rule.** When a sentence names a prior system, paper, product or platform, the citation follows the name, also when the
sentence opens with that name; never park it at the end of the sentence. Your own "-style" model of a rival takes no citation.
Full rules: `12` §B; check: `scripts/check_prose.py --cite`.

**Example** *(DAC)*. "AttAcc runs batched FC layers on the xPU and attention on PIM~\cite{attacc}." →
"AttAcc~\cite{attacc} runs batched FC layers on the xPU and attention on PIM."

---

## G. Numbers and figures

### G1. Pace the numbers: one or two per sentence, description after each

**Rule.** A sentence introduces at most two new numbers and is followed by their description. Derived figures (totals, ratios
computed from the given ones) are limited to one per paragraph, and only where they complete arithmetic already on the page.
The section-level density target (`09` §C3, one sentence in three carries a number) is an average: openers (C7) and framing
paragraphs carry none, and E4 decides which numbers are worth printing.

**Example** *(SPLEX)*. "7,700 entries, 12 % of the pool, while issuing 64 × 2,048 ≈ 131K selections, so ~17 per entry" → "Over
any 64 consecutive steps a layer touches about 7,700 distinct entries, 12 % of the pool."; the 131K and the 17 go.

### G2. A series the figure carries is printed at its endpoints

**Rule.** When a figure plots the series, the prose prints the two numbers that make the claim — first point and far tail — and
cites the panel for the shape; it does not walk the curve point by point.

**Example** *(SPLEX)*. "0.79 at the next step, 0.64 after 64, 0.48 after 512, 0.35 after 1,024" → "0.79 at the next step and
still 0.35 after 1,024 steps (Figure 4b)".

### G3. A figure citation says what to see

**Rule.** Every "Figure N" in prose is followed by the specific thing to look at — a value, a knee, a gap between curves —
never "Figure N shows that X" alone.

### G4. Minimal captions

**Rule.** A caption names what is drawn: the figure's subject, each panel's letter with its metric, and only the encoding the
figure cannot show itself. Settings, workloads, explanations and findings go in the paragraph that cites the figure, printed
once. A caption fact printed nowhere else moves into that paragraph; it is never dropped. This overrides the reference papers'
setup-carrying captions. Full rule: `02` §3 F11; check: `--captions`.

**Example** *(DAC)*. A 75-word caption listing platform, precision, model, sequence length and geometric means → "Mobile
platform: (a) decode-step speed; (b) GEMM, (c) attention-layer and (d) decode-step throughput per logic mm²." Caption words
425 → 133 across the paper.

### G5. One float per spot

**Rule.** Two floats never share a column of one page. Spread them: one figure per page first, opposite columns of one page
next, each on the page that first cites it or the next. Move source blocks; never shrink a figure or add space. The one
exception is the configuration table (B11). Full rule: `02` §3 F12; mechanics: `10` §3.

**Why.** The author (2026-10-19): "we don't put two different figures in the same spot. we want to separate them in different
pages as much as possible."

### G6. The figure visual system

**Rule.** Everything that already exists is drawn in a luminance ramp (white through grays to black); the blue tint is reserved
for what the system adds and for its single chart series; red only for small pinpointing marks; green for one small positive
mark, never a fill; no hatches; square corners; four spines on every chart; canvas sizes frozen once set. A restyle touches no
number and keeps every assert passing. Full rules: `02` §3.

### G7. Numbers are traced, rounded once, and asserted

**Rule.** Every printed number traces to a frozen data view, a design document or a verified citation, and the script that
generates the paper's tables or figures asserts it. Round from the source value once: a value of 8.545 prints as 8.5, never as
8.6 by way of 8.55. When prose stops printing a number, keep its assert as a guard and mark it "not printed".

**Why.** A double-rounded value cannot be regenerated from the data and is the first thing an artifact reviewer flags (CoDe,
2026-10-29: the ACT16 share).

---

## H. Section-specific

### H1. The introduction rules

**Rule.** Open on the landscape, write subject-first sentences, state nothing by metaphor or implication, keep symbols out of §1,
give the abstract-level numbers in the penultimate paragraph, and lead each contribution with a verb. Guards: "first" at most
twice, never "First, … Second, …" in §1; numbers only from the characterization and evaluation sections; contributions ≤ 40 words
each. Full guide: `04`.

**Example** *(SPLEX)*. "LLM decode is memory-bound:" as an opener → an opening on long contexts, agentic AI and large batches;
"Used naively, …" → "The LPDDR extension expands capacity, but it does not guarantee bandwidth"; bold-noun contribution leads →
"We characterize / We propose / We evaluate".

### H2. The abstract opens on the problem and joins every move to the last

**Rule.** The first sentence names the problem the paper solves, not the technique the prior approaches are built on; each later
move connects to the one before it with a connective ("Custom HBM changes this: …"), never as a cold new noun.

### H3. The abstract's move order

**Rule.** Problem → substrate as an alternative (one sentence) → the requirement it creates → system → characterization →
mechanism → results. The technique prior approaches are built on is introduced by the characterization sentence before any later
sentence leans on it. Model: the SPLEX abstract in `03`.

### H4. An abstract or section opening states the positive finding

**Rule.** In the abstract and in the first paragraph of any section, state what sets the result; do not negate an alternative
the reader has not met. Negated alternatives belong where the alternative has been introduced (the motivation). The *problem*
move must still be explicit.

**Example** *(SPLEX)*. "placement between the tiers, not the LPDDR wire rate, sets the delivered bandwidth" → "placement between
the tiers sets the delivered bandwidth".
