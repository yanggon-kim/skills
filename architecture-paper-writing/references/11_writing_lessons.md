# Writing lessons — what the author corrected, stated as rules

These are the corrections an author made on the rendered page, one per entry. When a per-section guide (`03`–`09`) and an
entry here disagree, this file is the later word. Each entry is a **Rule** (one sentence), a **Why**, and an **Example**
(before → after) taken from the pass that produced the rule; the examples are from one paper and are marked as such.

## The sentence test (de-rhetoric)

**Rule.** Delete any sentence that carries no fact, no number and no necessary forward reference.
**Why.** The quantitative register means every sentence must earn its place with content; bridges, flourishes and
"the next subsection presents" sentences are what an author deletes first on every pass. A display equation that restates a
table is a duplicate: keep the table and one prose sentence, drop the equation. Run-in openers such as "Three goals shape
the design." are acceptable minimal framing, and a roadmap sentence at a `\section` opening survives.
**Example** *(SPLEX example)*. "Its design follows from one property of the workload: …" / "Note what the engine does not
contain." → both deleted; the neighbours stitched so the property is stated where it is used.

## No questions to the reader

**Rule.** Never write a question — neither a sentence ending in "?" nor an "asks whether / the question is / we ask" framing;
state what the section measures, shows or ranks.
**Why.** A research paper states; it does not raise questions for the reader to hold. The rewrite keeps purpose and what is
compared and is no longer than the original. Before every commit, grep the section files for `?` and for
`asks (whether|how|which|what)|the question|we ask`; only comment lines may hit — and read the hits, because an author may
have placed the word deliberately.
**Example** *(SPLEX example)*. "This section asks how much of the selection survives across steps" → "This section measures
how much of the selection survives across steps"; "The question is how to reach the far tier at HBM bandwidth" → "The
design must reach the far tier at HBM bandwidth".

## No invented interfaces

**Rule.** Name only mechanisms, calls, registers and structures that a design document or a measurement record defines;
never coin a name to make a paragraph concrete.
**Why.** An invented interface is a fabricated claim a reviewer can grep for, and the paper's credibility rests on every
named thing tracing to a document. When a word budget and the fact list conflict, keep the facts and report the candidates
to cut; the author decides. A prior paper's section is a shape to imitate, never a model to cite as if it were ours.
**Example** *(SPLEX example)*. `splexPinRegion` / `splexSetHotBudget` / `splexReadTelemetry` lived in the draft for weeks and
nowhere else → deleted; the paragraph now names only the shortlist kernel, the doorbell, the completion word, the region
table and the block table, each defined in the design section.

## No fabricated verification

**Rule.** Classify every sentence about a driver, runtime or framework as *run*, *read from source*, or *design*; a
mechanism read from source is described in the present tense with its source cited — never "verified / measured / run",
and equally never "not run / assumed / a guess / only one flag is missing".
**Why.** The paper must not claim a run that did not happen, and it must read as design rather than as a caveat list; a
hedge reads as an admission instead of a claim. "We verified" is licensed only for the run that actually took place.
Identifiers come from the evidence table of the owner who ran it or are omitted.
**Example** *(SPLEX example)*. "Range-bounded placement was documented but not run; only the user-visible flag is missing"
→ "The driver places a buffer by the range its allocation flags name [source]" — present tense, source cited, no verdict
on what was or was not exercised.

## The borrowed-mechanism paragraph

**Rule.** A passage that adopts a mechanism from prior work is its own paragraph in this order: what we want to do → why it
is a problem → "we adopt X's answer" with the citation right there → our instance, named so it cannot be confused with X's →
the one rule the reader needs → what stays fixed; and the total word count may not grow.
**Why.** Compressed causal phrases ("contiguity collapses that list to three bases") are exactly what a first-time reader
cannot follow, and a correct sentence buried inside another paragraph is unreadable. A split that costs words is paid for
by tightening elsewhere; report both counts.
**Example** *(SPLEX example)*. One head paragraph containing "the region table, like RDMA's page list, …" → a separate
paragraph: the engine must resolve slot addresses without a per-page list → a page list per pool is too large → "we adopt
GPUDirect RDMA's answer [cite]" → "the migration engine's region table" (not "the region table" next to "RDMA's page list")
→ address = base + slot × stride → the bases are fixed for a pool's lifetime.

## Constrained results are a trade, not a gap

**Rule.** When the system matches an unconstrained baseline within a tolerance, name what the cap bought, with the tolerance
and the cap in the same clause, and state the budget in the paper's own unit.
**Why.** "Within t under a C budget" reads as falling t behind; "within t while capping C" reads as the price of the saving
the cap delivers. Cost numbers stay in the evaluation section; the summary gets the contrast word. A compressed coinage
("32-swap budget") hides the unit the rest of the paper uses.
**Example** *(SPLEX example)*. "matches an unbudgeted LRU's hit ratio within 0.013 under a 32-swap budget" → "matches an
unbudgeted LRU's hit ratio within 0.013 while capping migration at 32 swaps per layer per step" — the unbudgeted LRU pays
up to 3.6× the traffic for that last 0.013, so the 0.013 is what a 3.6× saving costs.

## Never merge measurement paragraphs of different kinds

**Rule.** Merge only paragraphs that measure the same kind of thing; two findings of different kinds each keep their own
run-in head, even at zero page slack, because the run-in head is where the claim is made.
**Why.** Every number and promise can survive a merge as sentences while the section's point dies, because a reader takes
the claims from the heads. Ask what each paragraph's unit is (per pair of steps, per window, per decode); different units
mean different heads, and a finding whose value is that nobody else computes it always gets its own. The enumeration in a
section's opening paragraph of what prior work does not capture is the breadth claim, not a qualifier, and survives a trim.
**Example** *(SPLEX example)*. Four run-ins merged into two: retention (a pairwise measure, lag-1 generalized to long lags)
bundled with the 64-step working set (a set-level measure, the one prior systems never compute) → reverted by the author;
dropping one point of the retention curve in the same pass had also turned a curve into three scattered values.

## Cuts drop the clause, never rewrite the fact

**Rule.** Remove a number by dropping the clause that carries it, never by restating the fact in a shorter but different
form; fix a seam by rewording a neighbour, never by adding a bridging sentence.
**Why.** A restated fact is a new claim that may be false; a bridging sentence is rhetoric that the next pass deletes. Keep
the closing sentence a handoff or a payoff, never a parameter, and if a fact must leave to meet a cap, say where it still
lives (table, caption, audit row).
**Example** *(SPLEX example)*. To lose "47 of the 48 GiB" the allocation clause was dropped, not rewritten as "48 GiB was
allocated" — which never happened.

## Shortening cuts qualifiers, never a number, control or promise

**Rule.** A "N % shorter" request removes qualifiers only — every number, named mechanism, control and cross-section promise
stays — and the report gives before/after counts with the counter named and whether any heading or float moved.
**Why.** The facts were settled in an earlier pass and are not reopened by a space request; the author often supplies the
target text verbatim, and it is applied verbatim. Ask which mode a pass is in: a correctness pass may deprioritise the page
limit outright (ship, report the map, say how many lines must come back later), and a gated pass has the author name what
to cut — trim from the working tree, never restart, and stop and report the residual rather than cut a result or a float
placement to close it. When the approved float map sits below the text being cut, the map cannot survive; build both,
report the delta, and do not spend words buying old positions back.
**Example** *(SPLEX example)*. "as for any larger device memory", the four-layer list → "every layer", "(cleared at exit)",
"admitted / resident / the engine's" went; the register name, every number, the control and the promises to the design
section stayed.

## The introduction rules

**Rule.** Open on the landscape, write subject-first sentences, state nothing by metaphor or implication, keep symbols out of
§1, give the abstract-level numbers in the penultimate paragraph, and lead each contribution with a verb.
**Why.** Reviewers read §1 first and expect a wide opening, direct claims, evidence after the claim, and nothing they must
infer; a named prior system per clause beats four in one sentence. Guards: "first" at most twice, never "First, … Second, …"
in §1; numbers only from the characterization and evaluation sections; contributions ≤ 40 words each.
**Example** *(SPLEX example)*. "LLM decode is memory-bound:" as an opener → an opening on long contexts, agentic AI and large
batches with named models and frameworks; "The established relief is host memory" → "Prior systems offload the KV cache to
host memory"; "Used naively, …" → "The LPDDR extension expands capacity, but it does not guarantee bandwidth"; "the optimal
split h* keeps 77 %" → "the optimal split, which balances the utilization of both tiers, keeps 77 %"; bold-noun contribution
leads → "We characterize / We propose / We evaluate".

## The informative statistic, not the trivial one

**Rule.** A headline cites the statistic that justifies the mechanism, not the one prior work already stops at; and every
headline verb gets a concrete object.
**Why.** If the introduction says prior systems act on the lag-1 overlap, a lag-1 number in the abstract reads as the same
knowledge; the long-horizon persistence is what a decayed count under a fixed budget rests on. A clause the author cuts is
usually a secondary number; keep the one number per claim that the mechanism rests on.
**Example** *(SPLEX example)*. "0.79 of the selection recurs at the next step" → "still selected 0.64 of the time 64 steps
later and 0.35 after 1024 steps"; "the serving framework commits them" → "applies the completed swaps to its KV-cache block
table (e.g., vLLM)".

## No audit trail in method and evaluation prose

**Rule.** Methodology and evaluation give only what the reader needs to interpret the results; a fact in a table is never
repeated in prose, and there are no `Metric.` / `Setup.` / `Systems.` run-ins.
**Why.** The reviewer needs to trust and interpret the numbers, not re-run the campaign; sub-channel counts, normalization
constants, hook internals and protocol minutiae stay in the evaluation documents. Every evaluation subsection opens with one
or two sentences of purpose plus what is compared, by name; keep the calibration claims that establish trust, not their
derivations; measure the page extent honestly rather than cutting a load-bearing fact to hit a budget.
**Example** *(SPLEX example)*. "The HBM rates are measured and the C2C link is modeled" while the configuration table already
marked each row measured or modeled → cut.

## Verify a plan's premise before executing it

**Rule.** When an instruction reads "do X, because Y" and Y is a measurable property of the render, measure Y first; if the
measurement kills the premise, leave the author's state untouched, deliver what the edit was for, and report the table and
the one tested alternative as the author's call.
**Why.** An order built on a false premise ships a regression in the author's own work, and the verification step is usually
already in the task. Do not take a forbidden option on your own judgement even when it measures best; put the finding in
the commit message and the status file's for-the-author list, not only in the report.
**Example** *(SPLEX example)*. "Set the three text boxes to a common x = 4 because the boxes are shrink-wrapped, so the origin
is the left edge; do not touch `align=center`" → measured: neither half held, and the letter of the plan would have replaced
the author's 1.0 px alignment with an 8.5 px stagger; the real deliverable — the author's alignment had never been exported
into the paper — was shipped, the alternative reported. The plan's quoted canvas size was also wrong; `pdfinfo` the current
figure before trusting one.

## Adopt clean author edits; flag deviations, never revert them

**Rule.** Adopt the author's figures or text that pass (numbers hold, render clean), hold the one that does not with a fixed
variant ready, and report deviations in palette, wording or label content instead of reverting them.
**Why.** An all-or-nothing hold stalls good work over one accidental connector, and silently editing the author's content
reverts a deviation the instructions said only to flag. The "stop if a number changed" gate means a measured value from the
generator's asserts, not a label: a generation name replaced by a generic one is adopted and flagged when it still agrees
with the caption and the asserts.
**Example** *(SPLEX example)*. An author-edited figure replaced "HBM3E stack" with "HBM stack" and "LPDDR6 16DP" with
"LPDDR"; every measured value in the figure was byte-identical and both labels matched the caption → adopted and flagged.
A sibling figure with a broken connector → held, clean variant exported, one line in the next-steps list.

## The figure visual system

**Rule.** Figures are understated and minimal: everything that already exists is drawn in a luminance ramp (white through
grays to black), the blue tint is reserved for what the system adds and for its single chart series, red is for small
pinpointing marks only, green for one small positive mark only and never a fill, no hatches, square corners, four spines on
every chart, and canvas sizes are frozen once set.
**Why.** Colour spent on anything other than the contribution defeats the point of colour, a large red area reads as
threatening (abutting small cells count as one area), and a canvas change moves every float below it. A restyle is
presentation only: no series added or reordered, no number touched, every assert still passing; a mark that explains a
surprising bar is added with a frozen-value assert and a caption clause. Never colour a baseline red because it is the
interesting one; "n/a" text alone marks an absent measurement.
**Example** *(SPLEX example)*. The old tier palette (HBM blue, LPDDR teal, an amber for ours, hatches, hidden spines) → gray
ramp for GPU, HBM, LPDDR, host and every baseline; sky-blue fill for the blocks the base die adds and for the one system
curve; red kept for swap arrows and one operating point; the hatched "n/a" placeholder bar dropped.

## Run-in heads are blunt findings

**Rule.** A run-in head states the finding as a plain declarative with a concrete subject, a plain verb and the
scale *in words*: "Hot entries stay hot for hundreds of steps." It is general and direct — not the measurement
itself ("Sixty-four consecutive steps touch 12 % of the pool" is too specific for a head; the number belongs in
the first sentence below it) and not an abstraction or an evaluation ("Recency is not the signal", "The deadline
is loose").
**Why.** The head is the claim a skimming reviewer reads; an abstraction makes them read the paragraph to learn
what was found, a blunt fact lets them decide whether to. The author's standard is direct, straightforward,
outspoken.
**Example.** *(eval)* "Recency is not the signal." → "The most recent 2,048 positions cover 0.47 of a selection."
"Hotness persists far beyond the next step." (acceptable) → "Hot entries stay hot for hundreds of steps." (better:
the scale is in the head).

## No evaluative adjective without the two quantities it compares

**Rule.** "Loose", "small", "negligible", "ample" are replaced by the two numbers being compared, in one sentence.
**Why.** An adjective asks the reader to trust a judgement; the two quantities let them make it. The author reads
"The deadline is loose" as too broad and abstract.
**Example.** *(eval)* "The deadline is loose." → "The swaps take microseconds against a deadline of one decode
step, tens of milliseconds."

## State a cost at its unit, then scale it to the system in the same sentence

**Rule.** Give a cost or a limit at the smallest unit it is defined on, then carry it to the level the reader cares
about, in the same sentence: per swap → per sequence per layer per step → per stack, per GPU.
**Why.** The unit figure is verifiable; the system figure is what matters; putting both in one sentence shows the
arithmetic and lets a reviewer check it. The author singled this out as the move he liked most.
**Example.** *(eval)* "Swaps are capped at 32 per sequence per layer per decode step, about 50 KB in each direction
per sequence per layer per step."

## The abstract states the positive finding; it does not negate an alternative the reader has not met

**Rule.** In the abstract (and the first paragraph of any section), state what sets the result; do not write
"placement — not the wire rate — sets the bandwidth" when the reader has not yet met the wire rate. Negated
alternatives belong where the alternative has been introduced (the motivation), not in the abstract.
**Why.** A negation of an unintroduced quantity costs words and adds nothing the reader can use; the author cut
"not the LPDDR wire rate" from the abstract as unnecessary. Conversely, the *problem* move must be explicit — the
version that skipped it was judged not to emphasize what the paper solves.
**Example.** *(eval)* "placement between the tiers, not the LPDDR wire rate, sets the delivered bandwidth" →
"placement between the tiers sets the delivered bandwidth".

## Pace the numbers: one or two per sentence, description after each

**Rule.** A sentence introduces at most two new numbers and is followed by their description; a sentence that
carries a number opens with it. Derived figures (totals, ratios computed from the given ones) are limited to
one per paragraph, and only where they complete arithmetic already on the page.
**Why.** A reader takes numbers at a pace; a long sentence that chains a measurement with two derived figures
("7,700 entries, 12 % of the pool, while issuing 64 × 2,048 ≈ 131K selections, so ~17 per entry") is too much
information at once, and the derived figures add nothing the measurement did not already say.
**Example.** *(eval)* Split into: "Over any 64 consecutive steps a layer touches about 7,700 distinct entries,
12 % of the pool." then the description; the 131K and the 17 go.

## A paragraph may open on the familiar alternative

**Rule.** When readers know the prior approach, a measurement paragraph may open by stating that approach and
its logic — "The natural alternative to tracking selections is to keep the most recent positions resident, as a
sliding-window cache does." — and let the number that follows say where it falls short.
**Why.** It names what the reader would have done first, so the measurement lands as an answer rather than a
fact in isolation; the author singled this opener out as the way to emphasize the contribution to readers who
know the alternative.

## The abstract opens on the problem the paper solves, and joins every move to the last

**Rule.** The first sentence names the problem the paper solves (the KV-cache capacity wall), not the technique
the prior approaches are built on (sparse attention); and each later move connects to the one before it — the
substrate or insight move follows the problem move with a connective ("Custom HBM changes this: …"), never as a
cold new noun.
**Why.** Opening on the rivals' technique tells the reader the paper is about that technique; an unconnected
substrate sentence reads as abrupt. The author kept "Unfortunately, …" and flagged the sentence after it.

## One paragraph per agenda in a mechanism introduction

**Rule.** Two or three paragraphs — definition and validity; interface; cost and deadline. Not one paragraph
carrying all three, not four that split one agenda.
**Why.** A paragraph break tells the reader the agenda changed; a single long paragraph hides the change, and
extra breaks announce changes that did not happen. *(author feedback on both eval variants)*

## A series the figure carries is printed at its endpoints

**Rule.** When a figure plots the series, the prose prints the two numbers that make the claim — first point
and far tail — and cites the panel for the shape; it does not walk the curve point by point.
**Why.** Four numbers in two sentences is number-centred description the reader cannot hold, and the figure
already carries the curve. *(author feedback)*
**Example.** *(eval)* "0.79 at the next step, 0.64 after 64, 0.48 after 512, 0.35 after 1,024" → "0.79 at the
next step and still 0.35 after 1,024 steps (Figure 4b); the curve between them is the slow erosion the figure
shows."

## A figure citation says what to see

**Rule.** Every "Figure N" in prose is followed by the specific thing to look at — a value, a knee, a gap between
curves — never "Figure N shows that X" alone.
**Why.** The reader is led to the point, not assumed to extract it; "don't just throw the figure at the reader."

## Say what a component does, not what it does not

**Rule.** Roles are stated positively; "never decides", "does not choose" and similar negated roles are cut, and
the positive statement of each part's job carries the division of labour.
**Why.** A negation is written-language padding — the author's phrase — and states nothing the positive role
did not.
**Example.** *(eval)* "The engine never decides what to move; that decision is the policy's, and the engine
only executes it." → "The engine executes the policy's swap list."

## The abstract's move order: problem → substrate as an alternative → requirement → system → characterization → mechanism → results

**Rule.** Open on the problem in its setting; the substrate may follow at once but only as "an alternative"
(one sentence, what it offers) and must be followed by the requirement it creates, which leads to the system;
sparse attention (or whatever the prior approaches are built on) is introduced by the characterization
sentence — mechanism, models, numbers — before any later sentence leans on it.
**Why.** A substrate sentence followed by a finding, with the setting's mechanism appearing as an unintroduced
modifier, was judged abrupt in two rounds. The submitted SPLEX abstract in `03_abstract.md` is the model,
sentence by sentence.
