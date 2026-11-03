# Page structure, figures and interaction

## Contents
1. Section order (with the parts, the route map, the concept ladder, the words this page uses, and the expert's
   version of your question)
2. Figures: the ladder
3. Interaction
4. The four-way review

## 1. Section order

The order follows how understanding is built: the reader's question, what they already have and
the concepts they will need (each taught with an easy figure), why the problem exists, how the
mechanism solves it, a chance to test it, and what to take away, with its cost. Every section is short. A typical
page carries 800–2,200 words in total, counting captions and terms (this is what `check_page.py`
counts; it warns outside 400–3,000). A page with a long concept ladder sits near the top of that
range; that is fine, because each rung is short and has a picture. The last section, the expert's
version of your question, is counted on its own (about 120–300 words), so it never crowds out the
lesson.

| # | section | job | length |
|---|---|---|---|
| 0 | **Title + one-sentence answer + route map** | The title names the concept. Under it: the reader's question as an `h1`-adjacent line, then a one-sentence answer that states the central idea. A skimmer gets the idea here in under 20 seconds. Under the answer, the route map: the parts on the way to the answer, as one-line boxes and arrows (§ The route map). | 1 question, 1–2 sentences, 1 map |
| 1 | **What you already know** | Three parts. (a) The plain background: anchor in something familiar, in prose only. (b) The concept ladder: one block per core concept the mechanism uses, in dependency order, each with a short explanation, one easy figure and one concrete example; each block builds on an earlier one, and its figure is that block's figure plus one new thing. (c) The words this page uses: a definition list (`dl.terms`), one plain line each, as a summary to glance back at. | 2–4 sentences + 2–8 blocks + 4–10 terms |
| 2 | **The problem** | What goes wrong, or what is hard, without the mechanism. Make the reader feel the cost with a concrete case and, if possible, a number. The assumption fails here, on the base scene. Show it on a ladder figure when you can. | 1 short paragraph (+ figure) |
| 3 | **The mechanism** | How it works, step by step, with as many figures as the steps need. Each step is a reason and names the blocks it follows from. Each figure climbs from the top rung of the concept ladder and adds one thing. It recalls the ladder's foreshadow where the hinted phenomenon is explained. Show each step working before you name it. A hard mechanism may be told in passes (`references/techniques.md` § Passes): one `h3.pass-label` per pass, each with its narrated figure. | 2–6 short paragraphs + figures |
| 4 | **Try it** | The interaction: predict, act, compare, explain. Its picture uses the same base scene. Where the parts include a convention, the widget or the transfer question changes it and the reader rebuilds the result. | widget + 2–3 sentences |
| 5 | **Recap** | Three to five lines, one idea each, in the order the page taught them. The last line names the trade-off: what the mechanism costs for what it buys ("The cost: ..."). | 3–5 bullets + 1 cost line |
| 6 | **The expert's version of your question** | The reader's request, upgraded: what a top professional would do that the reader did not ask for, the raw material they start from, their methods and tools, and what outside check shows the answer is right. Ends with the request rewritten as a prompt, ready to paste, and the sources you checked. | 1–2 sentences + 4 items + the prompt |

There is no "assumptions and limits" box, and no separate result or misconception section. State
each simplification in one plain sentence where the reader meets it: in the paragraph, the figure
caption or the widget note that relies on it ("This page counts every gate as one unit of delay;
real gates differ."). The same holds for wrong beliefs:

- **The reader's assumption** — what they bring before the lesson — fails in "The problem", on the
  base scene (§ The parts).
- **A misunderstanding of the mechanism itself** — one a reader can only form after learning it —
  is corrected in one sentence at the mechanism step where it would arise ("This does not make the
  answer approximate: the search keeps only whole plans as answers.").
- **The trade-off** — what the mechanism costs for what it buys — is the recap's last line, so the
  reader leaves knowing it is not free.

### The parts: what the ladder is made of

The ladder climbs from small parts to the conclusion. Find the parts before you plan blocks
(`SKILL.md` step 2), two ways, and merge them into one list:

- **Take the conclusion apart from first principles.** Ask "why is this true?" of the conclusion
  and of every answer, until you reach facts the reader can check. This finds the parts that carry
  the argument.
- **Peel the mechanism's figure.** Remove one thing at a time down to the simplest picture (§ Plan
  it backwards). This finds the parts the reader needs before they can even read the argument: the
  objects, the picture, the terms. First principles alone would skip them.

Each part is one of five kinds:

| kind | what it is | ILP example | where it goes | first technique to try |
|---|---|---|---|---|
| **element** | an object, picture or term the reader needs in order to read a fact or a reason | the grid of plans; the area line | a ladder block (plain ones stay in prose) | picture, show then name; contrast when it has a boundary |
| **fact** | true and checkable without trusting the page: a law, a definition, a line of the code, a published or measured number | "x and y must be whole numbers" (the problem says so) | a ladder block, often with its element; one `p.source` line says how to check it | contrast or extreme cases that show the fact holding |
| **reason** | a step that follows from earlier parts | "the LP score is a ceiling for every whole plan" | the mechanism; it names the parts it follows from | cause chain |
| **assumption** | what the reader, or the field by habit, takes for granted and the conclusion overturns | "round the LP answer and you have the best whole plan" | the problem (it fails there) | problem first; contrast (believed vs. real) |
| **convention** | a fact people chose and could choose otherwise; mark it as a convention where the page states it | "one memory port" in a loop page; "a 0.5 rounding threshold" | the ladder states it; "Try it" or the transfer question changes it | manipulate one input |

Rules for the parts:

- **Stop at facts the reader can check.** "Experts say so" is not a fact; keep asking why. But not
  everything reaches physics: a definition or a convention is a fine place to stop, as long as the
  page says which it is. Do not force a derivation onto an idea that is a choice.
- **Three to six facts per conclusion.** More means the scope is too wide or the facts are too
  small; merge or cut. An element and the fact about it may share one block, so the parts list does
  not have to make the page longer. The word budget stays the same.
- **Every reason names its parts.** In its text ("Blocks 2 and 3 give ...") and in its markup
  (`data-from`). A mechanism step that rests on a fact the ladder never showed is a hole; add the
  fact to the ladder or cut the step.
- **The assumption fails on the page.** The problem section shows it failing on a concrete case on
  the base scene, before the mechanism explains why.
- **A convention is a lever.** Where the parts hold a convention, the reader changes it in "Try it"
  or in the transfer question and sees the result rebuilt from the same facts. This is the step
  where the reader goes past the page: from "why it is so" to "what would change it".
- **The parts become the route map.** The graph of parts is printed once, as the route map under
  the answer. Elsewhere the reader sees blocks, steps and a widget; the kinds show through the
  `p.source` lines and the "follows from" phrases.

### The route map

An **advance organizer** (Ausubel's term) is a short overview, given before the lesson, that shows
how the new ideas will fit together; an **argument map** draws claims as boxes and their support as
arrows. The route map is both: before the reader starts, it shows which parts they will understand,
in which order, and how those parts join into the answer. It is the page's plan made visible: the
skill takes the conclusion apart into this graph first (`SKILL.md` step 2), and the page then
explains the graph top down.

- **Where.** In the masthead, right under the one-sentence answer, in a `<figure class="route">`.
- **What is on it.** One box per part on the way to the answer: each ladder block, the problem's
  assumption, each reason in the mechanism, and the answer itself. A pure convention (a choice the
  widget changes) is a lever, not a step, so it is not a box; a block that states a convention
  shows a small "a choice" tag. The widget, the recap and the expert section are not on it.
- **Each box: one line in plain words.** `data-summary`, about 40 characters (about 20 in Korean).
  The reader has not learned the terms yet, so use the page's plain words, not jargon ("The LP
  score is a ceiling" is fine once the box's block says what LP is; "LP relaxation bound" is not).
  Above the summary the script prints the kind and number ("block 3 · fact", "reason 2").
- **Arrows mean "is needed for".** They come from `data-from` (a ladder block without one uses its
  `data-builds-on`). The arrow from the assumption is dashed: the answer overturns it. An arrow that
  another path already implies is left out, so the map shows the route, not every citation.
- **Bands, top to bottom.** "What you already know", "The problem", "How it works", "The answer",
  in that order, so the map reads in the page's order.
- **Every box links to its part,** and every part leads to the answer. A part that leads nowhere is
  either missing a `data-from` or not needed; `check_page.py` warns about it.
- **Small.** About 6–12 boxes. More means the scope is too wide or the parts are too small.
- **Never drawn by hand.** `scripts/route_map.py` reads the markup and writes the SVG between
  `<!-- route:start -->` and `<!-- route:end -->`, so the map and the page cannot disagree. Rerun
  it after any change; `check_page.py` warns when the map is stale.
- **The caption** says how to read it, in the page language: top to bottom, what an arrow and a
  dashed arrow mean, and that each box links to its part.

**The route rail** keeps the map with the reader. On screens at least 88rem wide, the template's
"Route rail" script puts the route in the empty left margin as a subway line: each section heading,
the one-line summary of every part under it (the same `data-summary` as the map's boxes, the answer
left out), and one line for each section without parts ("Try it", the recap, the expert's
version). While the reader scrolls, the part they are reading lights up in coral, the parts above
it are filled in as read, and the rest stay hollow; each line links to its part. It is deliberately
simpler than the map — no branches, no arrows — because its job is "you are here", not the
argument. It needs no slot and no authoring; it appears whenever three or more lines exist, hides
on narrower screens (where the map at the top does the job), and leaves the page unchanged without
JavaScript.

### The concept ladder

The ladder is where the page teaches what the reader is missing before the mechanism needs it. It
is the most important part of "What you already know", and usually the longest.

- **Which concepts get a block.** Every element and fact from the parts list that the mechanism's
  reasons rely on and that a smart non-expert does not already have. A concept the reader surely has (an AND gate, a list)
  stays in the plain background as a sentence. The concept's own name usually gets the last block
  ("FlowMap in plain words") or none, if the mechanism section introduces it.
- **Dependency order.** A block uses only concepts from the background or from earlier blocks. Write
  the dependencies down before you order the blocks.
- **Each block builds on one earlier block.** The first block starts from nothing. Every later block
  names the block it builds on, in its text ("Take the cut picture from above. Now cover the whole
  network ...") and in its markup (`data-builds-on`). It is usually the block just before it, but
  it can be any earlier one.
- **One block = one idea.** A heading that names the concept, two to five short paragraphs, one
  figure, and a concrete example worked on that figure. The idea is one element, one fact, or an
  element together with the fact about it.
- **A fact shows its ground.** A block that states a fact ends with one `<p class="source">` line:
  where the fact comes from or how the reader can check it ("Check: count the loads in the loop
  body." "Source: Lecture 3, slide 12."). Mark a fact that is a convention as one in the same line
  ("A convention: HLS gives an array one port unless you partition it.").
- **One chosen technique per block.** Pick it from `references/techniques.md` by the shape of the
  question the block answers, and name it in `data-technique`. Contrasting cases (§ Figures, Show
  each idea in contrasting cases) are the strongest candidate and fit most "what is it?" blocks; a
  "why?" block takes a cause chain; rarely, one abstract first contact may take an analogy (at most
  one per page, ladder blocks only). A small table is
  welcome when it lists the cases the figure shows (each way to cut a node, with its inputs and
  whether it fits).
- **Its figure is a rung.** The figure is the figure of the block it builds on, plus one new thing.
  § Figures says how to draw it.
- **Close a family with a comparison table.** When three or more blocks (or two blocks and the
  mechanism) teach versions of the same thing — a history (`__syncthreads()` → `bar.arrive` →
  `mbarrier`), or rival answers to one need (LP, ILP, a heuristic) — the reader has met each one
  separately but has not seen them side by side. End that run of blocks with one table (§ The
  comparison table).
- **Foreshadow the main question once.** The block whose figure first shows the phenomenon the
  page is about ends with one `<p class="foreshadow">`: an observation the reader can check in
  the figure, a `<b class="handle">` that names it, and a cue to keep it in mind. It adds no cause
  and no significance. It may lean toward the answer as an open question, but it never states it.
  The mechanism recalls it with `data-recalls` and the handle's own words. Use one per page, two at
  most (`references/techniques.md` § Foreshadow).

Markup (the template has it):

```html
<div class="concept" id="c-cut" data-builds-on="c-network" data-technique="contrast" data-part="element fact">
  <h3>4. Cut: the list of inputs a LUT takes</h3>
  <p>...</p>
  <figure class="sheet">...one SVG drawn on the base scene...</figure>
  <p class="source">Check: a 3-input LUT has 2^3 = 8 table rows; count the inputs of each cut.</p>
  <p class="foreshadow">Both cuts give y depth 2, yet the left one needs 3 LUTs and the right one 2. Keep <b class="handle">this LUT gap</b> in mind.</p>
</div>
...
<p class="answer" id="answer" data-part="conclusion" data-from="m-proof p-guess"
   data-summary="FlowMap gets the least depth">...</p>                    <!-- in the masthead -->
<p id="p-guess" data-part="assumption" data-from="c-cut" data-summary="...">The usual guess: ...</p>  <!-- in #problem -->
<p id="m-label" data-part="reason" data-from="c-cut c-depth" data-summary="...">Blocks 4 and 5 give ...</p>  <!-- in #mechanism -->
<p data-recalls="c-cut">This is the difference you saw in <a href="#c-cut">block 4</a>: ...</p>
<details class="transfer" data-changes="c-port">...</details>          <!-- in #try -->
```

`data-part` takes one or two of `element`, `fact`, `reason`, `assumption`, `convention`,
`conclusion`. A block that states a convention carries both `fact convention`. Every part on the
route (blocks, the problem's assumption, reasons, the answer) also carries an `id` and a one-line
`data-summary` for the route map. `data-from` lists the ids of the blocks or
reasons a reason follows from. `data-changes` on the widget or a transfer question names the
convention block it changes.

Number the blocks only when the order is the real dependency order the reader should follow (it
usually is, in a ladder).

### The comparison table

A family of mechanisms is easiest to remember as one table: what changed from each version to the
next, and what stayed the same. The blocks teach each version with a picture; the table is the
summary the reader keeps.

- **When.** Three or more versions of the same thing appear on the page (a history, or rival
  answers to one need). For two, the contrast figures usually suffice; add a table only if they
  differ in more than three ways.
- **Where.** Right after the last block of the family, before the term list (or right after the
  mechanism step, if the last version is the mechanism itself). Introduce it with one sentence.
- **Columns: the versions,** in the order the page taught them, named as the page names them.
- **Rows: the dimensions,** one per question the blocks answered ("Does arriving wait?", "Who can
  take part?", "What completes it?"). Use only dimensions the blocks showed; the table summarizes
  and never introduces a fact.
- **Cells: a few words each,** six or fewer. The cell where a version brings its new step is marked
  `class="new"` (coral), so the reader sees what each step of the history added.
- **What they share:** a last row `tr.same`, or one sentence under the table, saying what every
  version has in common ("each counts arrivals toward a target and resets itself for the next
  round"). The similarity is half the lesson: it is what the reader can carry to the next version.

Markup:

```html
<figure class="compare-table" data-compares="c-sync c-split c-mbar" aria-labelledby="cmp-caption">
  <div class="table-scroll"><table class="family">
    <thead><tr><th></th><th>__syncthreads()</th><th>named barrier</th><th>mbarrier</th></tr></thead>
    <tbody>
      <tr><th>Does arriving wait?</th><td>yes, one step</td><td class="new">bar.arrive: no</td><td>never</td></tr>
      ...
      <tr class="same"><th>Same in all</th><td colspan="3">count arrivals, release waiters, reset</td></tr>
    </tbody>
  </table></div>
  <figcaption id="cmp-caption">...</figcaption>
</figure>
```

The table's class is `family`, not `compare`: `.compare` is the widget's before/after grid, and a
table that takes it is laid out as a grid with its header out of line.

`check_page.py` checks that `data-compares` names two or more real ids, that the header has one
column per version, and that the table says what the versions share.

### The words this page uses

The term list closes "What you already know", after the ladder. The reader has met every core term
in a block by then; the list is the one place to glance back at all of them. Rules for the list:

- **Complete for this page.** Any term that a smart non-expert might not know, and that appears
  later on the page, is in the list. Check this after the page is written: scan the prose, the
  figure labels and the widget for words that are missing.
- **One plain line each.** A definition says what the thing is or does, in plain words, with a
  number where it helps ("A warp is 32 threads that run the same instruction together.").
- **Background first.** Background words come first, then the words the ladder and the page
  introduce, in the order they appear.
- **Introduced before used.** A word a ladder block needs before its own block teaches it is
  defined in the plain background, so no block relies on a word the reader has not met.
- **One name per concept.** The list fixes the name. The prose, the figures and the widget use that
  name and no synonym. If the field has a common synonym, give it once in the definition ("also
  called ...").

### The expert's version of your question

A beginner's request is often not the sharpest version of itself. The reader asks what they know to
ask; an expert would ask something deeper, start from rawer material, use tools the reader has not
heard of, and trust a check that does not depend on anyone's say-so. This last section shows that
upgrade, so the reader leaves with a better next question, not only an answer.

It upgrades the **question**, never the **page**. Everything above it answers the request as the
reader asked it, at the reader's level. Do not let the expert view raise the level of the lesson,
add scope to it, or change what it explains: a newcomer who stops before this section must still get
the whole lesson. The section itself stays in the page's plain voice, because the reader of this
section is still the newcomer.

Answer four questions, each about this concept and this request (generic advice such as "read
papers" or "run benchmarks" teaches nothing):

1. **What would a top professional do here that the reader did not ask for?** The sharper question
   and the work it leads to. Often it turns "does X happen?" into "how much, when, and what does it
   cost?" — for a query-engine page: not "is prefetching done?" but "where does the query's time go,
   and how many cache misses does each hash-table lookup cost?"
2. **What raw material would they start from?** Primary sources instead of digested ones: the
   original paper, the specification, the source code of a real system, a real dataset, the
   measured trace. Link each one.
3. **What methods and tools would they use?** Named commands, instruments, techniques or
   experiments, and in a few words what each one shows (`EXPLAIN ANALYZE` prints the plan with the
   time each step took).
4. **What, other than the AI or the reader, would show the result is right?** A measurement, a
   reproduction, a test, a proof, a primary source. State the result to expect if the page's model
   is right ("probe time per row jumps when the hash table outgrows the L3 cache"), so the reader
   can test the page against reality.

Then **rewrite the request** to ask for exactly that, in the reader's own voice and language, as a
prompt they can paste into a new conversation. It names the concept, the raw material, the methods
and the outside check, and it still asks for a plain explanation, because the reader has not
changed — only the question has.

Rules for the section:

- **Real and checked.** Every paper, repository, command and dataset named here passes step 2's
  fact check. A made-up tool or paper is worse here than anywhere else, because this section exists
  to send the reader to real sources. If you cannot verify a source, leave it out.
- **Plain words.** Each source, tool or term the page has not already defined gets a plain
  half-sentence saying what it is. The term list at the top stays the lesson's list; do not add this
  section's words to it.
- **Last on the page.** It follows the recap. The page states its simplifications where they
  happen; this section says how an expert would go further.
- **Sources go here.** If you checked facts on the web, list those sources as links in a short
  "Sources" line after the prompt, so the lesson above stays uncluttered.
- **The prompt is text.** It sits in `<pre class="prompt">`, selectable without JavaScript; the copy
  button is an extra.

Headings are plain statements or the plain section names above; avoid clever headings. Number the
sections only when the order is a real sequence the reader follows (it usually is not — the page is
read top to bottom anyway).

## 2. Figures: the ladder

Explain with pictures wherever a picture helps — in the concept ladder as much as in the mechanism.
The page has no limit on the number of figures. What makes many figures easy instead of tiring is
that they are **one picture growing**: a reader who learned the easy picture can read the hard one,
because the hard one is the same picture with a little more on it.

### The base scene

The page has one visual vocabulary, the **base scene**:

- **One layout.** The same thing sits at the same place in every figure. Node `n` that sat
  top-centre in the cut figure sits top-centre in the mechanism figure.
- **One name per element.** The label in every figure matches the term list.
- **One look per kind of thing.** The same shape and color mean the same kind of thing in every
  figure (a gate is a circle, an input is a square, a LUT is a soft hull).

Define it once in code: the positions, the element list and a drawing function. Generate every
figure — ladder rungs, mechanism figures, timeline frames and the widget's picture — from that
code with a short Node or Python script, so nothing drifts. Give each recurring element a
`data-key` that stays the same in every figure (the same convention the timeline uses).

### Plan it backwards

1. **Top rung first.** Sketch the mechanism's richest figure, the one that shows the answer. Its
   layout becomes the base scene.
2. **Dependencies.** List which concept needs which.
3. **Peel off one thing at a time.** From the top rung, remove one element or one idea per step,
   down to the simplest picture. Every step down is one rung.
4. **Reverse.** That list, reversed, is the reading order: ladder blocks, then the problem, then
   the mechanism's figures, then the widget.

Not every rung needs the whole scene. An early rung can show a crop of it (one LUT and its truth
table, or one node and its inputs) as long as what it shows sits and looks as it will later.

### Rules for each rung

- **One new thing per figure.** The rung adds exactly one idea to the figure it builds on: a new
  element, a new label (a number on every node), or a new grouping (a hull around some nodes). It
  then shows that one idea in several cases; the cases are not extra ideas.
- **New in coral, known in its old look.** The new thing is drawn in coral (`.f-accent`,
  `.s-accent`, `.t-accent`). What the reader already knows keeps the ink, pencil and idle colors it
  had, so the eye goes to the change.
- **Say what it builds on.** The text before the figure, or its caption, names the earlier figure
  ("the same network as in block 2, now with ...").
- **At most seven new primary elements.** Boxes, lanes or nodes the reader has not seen before.
  Elements carried over from earlier rungs do not count, so a figure can hold a whole network the
  reader already knows, and a new element repeated in every case counts once. If one figure must
  introduce more than seven, split it into two rungs.
- **The mechanism continues the ladder.** Mechanism figures start from the top rung of the concept
  ladder, not from a new drawing. A mechanism that changes over time is a timeline whose frames are
  drawn on the base scene (`references/timeline.md`).

### Show each idea in contrasting cases

Contrast is the strongest of the chosen techniques (`references/techniques.md`), so it gets its
full rules here. One example shows that a concept exists; contrasting cases show what it is. People
pick out a property when they see it change while everything else stays the same. When a block or
step uses contrast, its figure shows **2–4 cases side by side**, all drawn on the base scene:

- **Vary one thing; hold the rest.** The same network, the same layout, the same scale in every
  case. Only the property the figure teaches changes. If two things change at once, the reader
  cannot tell which one caused the difference.
- **Label each case with its result.** Under each case, the measured value or the verdict, in the
  terms of the page: "3 inputs ✓", "4 inputs ✗", "depth 2 · area 3". The labels make the contrast
  readable without the prose.
- **Show the boundary when there is one.** Include a case that fails (a non-example) next to the
  ones that work. Only examples that work never show where the concept stops.
- **Say what varies and what is fixed.** The caption names both: "Both mappings have depth 2; only
  the number of LUTs differs."
- **Repeat the cases in a table when it helps.** A small table under the figure, one row per case,
  lets the reader compare the numbers.

Pick the kind of contrast that fits the concept:

| kind | use it for | example |
|---|---|---|
| example / non-example | a concept with a condition or a limit | cuts of node n with 2, 3 and 4 inputs: the first two fit a 3-input LUT, the third does not |
| two choices for the same problem | a concept that is a score or a criterion | two mappings of one network: same depth 2, area 3 against 2 |
| a sweep of one value | a concept whose result grows or shrinks with one input | cuts of height 1, 2 and 3 for the same node |
| before / after | what a mechanism changes | the same network mapped by FlowMap (5 LUTs) and with slack (4 LUTs) |

Lay the cases out as small multiples: equal panels in one row, each a `<g class="case"
data-case="...">` in the SVG, with the result label under each panel. On a phone the row may scroll
inside `.diagram-scroll`; keep at most four panels so each stays readable. Sweeps and extreme cases
use the same small-multiples layout.

### Other techniques on the base scene

A block whose question is not "what is it?" uses another technique, still drawn on the base scene:
a cause chain as numbered callouts and "causes" arrows on one picture of the scene; an analogy as
the familiar picture beside a base-scene picture, matched part to part, followed by a
`<p class="breaks">` sentence that says where the analogy breaks; a sequence as a timeline. Each
technique's entry in `references/techniques.md` says how to draw it and when not to use it.

### Narrated figures: one sentence, one frame

A paragraph that explains a figure asks the reader to do two things at once: read a sentence, and
find in the picture what the sentence is talking about. When the paragraph introduces several
things that are parts of the same picture ("the group", "a path", "the cut", "paths that share no
node"), that second job fails silently: the reader no longer knows what each word points at, and
every later sentence floats. A **narrated figure** removes the second job. The paragraph becomes a
numbered list of short sentences, and each sentence has its own frame of the figure, in which the
thing the sentence names is the thing that changes. The reader steps through it, and the sentence
of the current frame lights up under the player. This applies three findings from multimedia
learning research: show words and the picture they describe at the same time, highlight what the
words refer to, and let the reader set the pace.

- **When.** Use it where a paragraph has three or more sentences that each point at a different
  part of one figure. That is most concept blocks, the problem section (the assumption failing is a
  short story: the guess, applying it, where it breaks, why) and the mechanism's steps. Keep a
  static figure for a block of one or two sentences, and keep plain prose for text with nothing to
  point at (the plain background, the recap, the trade-off, the expert's section). The plain
  background still uses static figures generously: a picture of the example the page will use is
  almost always worth it.
- **One sentence, one frame.** Write each sentence so that its subject is something visible, and
  make that thing, and only that, change in its frame (in coral or in a path colour). A sentence
  whose frame changes nothing is not pulling its weight; two sentences that need the same frame
  are one sentence.
- **3 to 8 frames.** More than eight means the block holds two ideas: split it.
- **Contrast ends side by side.** When the paragraph compares cases, the frame of the comparing
  sentence shows the cases next to each other, with what the sentence names highlighted in each.
  Never let a comparison end on a lone picture that sends the reader back through the frames to
  see the other case. The way to build this: give every frame two panel slots; a frame with one
  panel shows it in the middle and hides the second slot with `.off`; the comparison frame moves
  the first panel to the left and shows the second beside it. The player slides one into the
  other.
- **The last frame holds the whole picture.** Whatever the steps added, the final frame shows it
  all at once (the side-by-side frame, for a contrast), so the reader leaves with one complete
  image.
- **Reader-paced.** No autoplay; a hold of about 4 seconds when the reader presses play. Clicking a
  sentence jumps to its frame.
- **Readable without JavaScript.** The sentences are an ordinary list, and all frames sit in a
  folded `<details>` ("all frames at once") under the player.
- **A timeline is a narrated figure** whose frames are the steps of a process. Give the mechanism's
  timeline a synced sentence list too: its frame captions are the sentences.

Markup (the template has the script and the CSS):

```html
<figure class="timeline wide-frames narrated sheet wide" aria-labelledby="w1-caption">
  <div class="player js-only">...the template's player...</div>
  <details class="all-frames"><summary>All frames at once</summary>
    <ol class="storyboard"><li class="frame"><svg>...</svg><p class="frame-caption">sentence 1</p></li>...</ol>
  </details>
  <figcaption id="w1-caption">what the colours, rings and numbers mean</figcaption>
</figure>
<ol class="sync-steps">
  <li><span class="sync-tag">①</span> sentence 1</li> ...
</ol>
```

The frames follow the timeline rules (`references/timeline.md`): the same keyed elements in every
frame, hidden with `.off` when unused. A narrated block names `sequence` in `data-technique`, with
`contrast` beside it when it ends side by side. Build the frames with `assets/narrated.js` from a function that draws one panel of your base scene;
it handles the panel slots and the keys and refuses frames the player cannot show. Write the
sentences by `references/voice.md` § Sentences for a narrated figure. `check_page.py` checks that
each sentence list has exactly as many sentences as its figure has frames, and points out blocks
with a long paragraph and only a static figure; `scripts/check_players.mjs` steps through every
player in a headless browser and confirms the shown frames and the lit sentences.


#### Passes: the same unit, two or three narrated figures

A unit told in passes (`references/techniques.md` § Passes) holds two or three narrated figures in
a row, built from the same `drawPanel`, so every pass shows the same base scene. The figures follow
the pass order, and each one comes after a pass label:

```html
<p class="label pass-label">Pass 1 · picture only</p>
...narrated figure + ol.sync-steps...
<p class="label pass-label">Pass 2 · with numbers</p>
...
```

Give each figure its own `id` in `narrate()` (`b1e`, `b1m`, `b1f`). Easy passes hide layers through
the panel spec instead of drawing a new picture, so the player can show what pass 2 adds to pass 1.
Name the passes once near the top of the page (`p.howto`): the explanations come in passes, and pass
1 alone gives the big picture.

### Choose the base scene's type

| the idea is about | base scene type |
|---|---|
| steps in order | flow (left to right, or top to bottom) |
| a thing that changes mode | state diagram |
| parts and how they connect | system map, graph or network |
| events over time, overlap, waiting | timeline (time runs left to right) |
| two designs or two cases | side-by-side comparison, same scale on both sides |
| a stack of abstractions | layers |
| why A leads to B | cause-and-effect chain |

### Rules for every figure

- **One reading direction.** Left to right or top to bottom. The eye never has to backtrack.
- **Every arrow has one meaning.** "Data moves", "time passes", "causes" — pick one per arrow style.
  If two styles appear, a small legend says what each means. Keep the same meaning in every figure.
- **Labels work without the prose.** A reader who looks only at the figure and its caption gets
  the main relationship.
- **It reads in grayscale.** Color supports a distinction that shape, line style, position or a
  label already makes. Coral marks the one new thing, not everything.
- **Draw to scale where scale is the point.** If one bar means 4 cycles and another 32, their
  lengths are 4:32.
- **Accessible.** `role="img"` on the `<svg>`, with `<title>` and `<desc>` inside it, referenced by
  `aria-labelledby`. The `<desc>` is the alt text: the main relationship in one or two sentences.
- **Caption.** The `<figcaption>` says what the figure shows, what is new in it, and, where it
  matters, what it simplifies or leaves out.

### SVG mechanics

- Set a `viewBox` and `width="100%"`; never a fixed pixel width. Wrap wide figures in the
  template's `.diagram-scroll` box so the page body never scrolls sideways.
- Color every shape and text through the template's CSS classes, which read the theme tokens. A
  literal hex color in the SVG breaks dark mode.
  - fills: `.f-paper`, `.f-sheet`, `.f-idle`, `.f-ink`, `.f-accent`, `.f-teal`, `.f-mustard`,
    `.f-none`
  - strokes: `.s-ink`, `.s-pencil`, `.s-accent`, `.s-teal`, `.s-mustard`; add `.thick` or
    `.dashed` to change weight or style
  - text: `.t-label` (body face), `.t-mono` (small monospaced annotation), `.t-accent`
  - arrowheads: the template defines `#arrow` (ink) and `#arrow-accent` (coral) once, in a hidden
    SVG at the top of the page; every figure refers to them with `url(#arrow)`. Do not repeat
    `<defs>` with the same ids inside each figure.
- Give every drawn shape an explicit fill (`fill="none"` counts). Leave room in the `viewBox` for
  the outermost labels.
- Keep text at 13px or larger in SVG units at the default width, so it stays legible on a phone.
- Give each figure's `<title>` and `<desc>` ids unique to that figure.

## 3. Interaction

### What makes it meaningful

An interaction earns its place only if using it teaches something reading cannot. It must:

1. **Ask for a prediction first.** Before the reader touches the control, a short prompt asks what
   they expect. The answer sits in a `<details>` element, so it works without JavaScript.
2. **Change one real input.** One slider, one toggle, or one step button that maps to a real
   variable of the mechanism (threads that take the branch, prior probability, number of commits).
   Not a color picker. Not five sliders.
3. **Show the mechanism respond.** A figure drawn on the page's base scene redraws next to the
   control, so the reader recognises the picture from the ladder. Show the internal state, not only
   a final number.
4. **Compare two states.** Keep the starting state visible, or show "before" and "after" side by
   side, so the reader sees the difference instead of remembering it.
5. **Explain why the result changed.** One or two sentences, updated with the state, in the page's
   voice. "4 of 32 threads took the branch, so the warp spent 2 of 3 passes with most lanes idle."
6. **Reset.** A visible reset button returns the starting state. Pressing it twice changes nothing.

### One widget, plus questions

The page has one widget. Prediction questions in `<details>` are not widgets: one comes before the
widget (required), and one transfer question after it is encouraged. More than three questions
turns the page into a quiz.

### When there is no natural dial

Some concepts have no variable to slide (a definition, a historical idea, a proof). Use one of these
instead, in this order of preference:

- **Step-through.** Walk the mechanism one state at a time. Good for algorithms and protocols (git
  rebase, a cache lookup, TCP handshake). Build it as a timeline (`references/timeline.md`): its
  player already has previous, next, play and a scrubber, and its storyboard keeps every state
  readable without JavaScript.
- **Predict-then-reveal questions.** Two or three questions in `<details>` that test transfer to a
  case the page did not show. Each answer explains why. This needs no JavaScript at all.
- **Sort or match.** The reader assigns a few cases to categories, then checks.

Never ship an interaction that teaches nothing. If none fits, use predict-then-reveal questions.

### Correctness and robustness

- Compute every displayed number from the real rule (Bayes' formula, the real cycle count of the
  model). If the model simplifies reality, one sentence next to the widget says how.
- Test the minimum, typical and maximum inputs. Watch for division by zero, empty states and
  negative values at the extremes.
- Use real `<button>` and `<input>` elements with `<label>`s and stable `id`s, so they work with the
  keyboard and screen readers. Visible focus comes from the template.
- Announce changes politely: the "why" text sits in an `aria-live="polite"` region.
- No `alert()`, `confirm()` or `prompt()` — the artifact viewer suppresses them.
- No `localStorage` needed. If you use it for convenience, wrap it in try/catch.
- Animation is optional and short. Under `prefers-reduced-motion: reduce`, state changes are
  instant; the template handles transitions, so add none outside it.

### Without JavaScript

The page must still teach with scripts off:

- Prediction answers live in `<details>`.
- Put the static "before" and "after" states in the HTML (a two-column comparison, or a figure of
  each state). The script enhances them; it does not create them from nothing.
- The control itself may do nothing without JavaScript. Nothing the reader needs to read may
  exist only after a script runs.

## 4. The four-way review

After the page is built, look at the route map alone: follow it from the top box to the answer.
Does each box match its part, is each arrow a real "is needed for", and is the order the order the
page teaches? If the page has a comparison table, check every cell against its block. Then review the page four ways. Each one alone must teach the same correct model:

1. **Text only.** Read the prose and skip the figures and the widget. Is the mechanism complete?
   Start at the conclusion and walk down: does every reason name the blocks it follows from, and
   does every chain end at a fact the page showed, with a way to check it? Does the problem show
   the assumption failing? Does every analogy say where it breaks?
2. **Figures only, in order.** For every narrated figure, step through it and read each sentence
   with its frame: does the frame change exactly what the sentence names, and does a comparing
   sentence show the cases side by side? Flip through every figure and caption from the first ladder block to
   the widget. Does it read as one picture growing, one thing per rung? Does any figure start over
   with a new layout, rename an element, or add two ideas at once? For each unit, does the chosen
   technique fit the question's shape? Where a figure shows cases, can you name in one word what
   varies between them, and does a failing case show the boundary? Does the foreshadow point at
   something visible in its figure, stop before the answer, and get recalled?
3. **Interaction only.** Use the widget at minimum, typical and maximum values, then reset twice.
   Does each state's explanation match the prose?
4. **Without JavaScript.** Do the predictions have answers? Is the comparison visible?

Write down every disagreement between parts and fix it. Common ones: a figure labels a part with a
different term than the prose; a mechanism figure moves a node the ladder placed elsewhere; the
widget's numbers do not match the worked example; the recap mentions something the page never
explained.
