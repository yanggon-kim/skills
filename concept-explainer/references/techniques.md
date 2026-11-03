# Explanation techniques: the toolkit

Different concepts are easy in different ways. "What is a cut?" is answered best by showing cuts
that fit and one that does not. "Why is the best LP point a corner?" is answered by a chain of
causes. "How does branch and bound proceed?" is answered by a sequence of frames. This file is the
encyclopedia of techniques the page can use. Step 3 of `SKILL.md` picks from it, unit by unit,
according to the shape of the question each unit answers.

## Contents
1. The three tiers
2. How to choose: question shapes
3. How to combine: rules that keep the page calm
4. The technique plan
5. Tier 1 — defaults (every unit)
6. Tier 2 — the page skeleton (fixed places)
7. Tier 3 — chosen per unit (full entries)
8. Markup and checks

## 1. The three tiers

| tier | techniques | when |
|---|---|---|
| **1. Defaults** | picture, concrete example, ladder, show then name | in every unit, always. They are the house method: the reader's favourite way to learn. |
| **2. Page skeleton** | route map, anchor in the familiar, foreshadow, problem first, predict first, manipulate one input, transfer question | each in its fixed place on the page (`references/page-structure.md` § Section order). Not chosen; the structure provides them. |
| **3. Chosen per unit** | contrast, sweep, extreme cases, sequence, cause chain, analogy, numbers and scale, passes | one per unit (two at most), picked by the shape of the question the unit answers. |

A **unit** is one ladder block, the problem section, one mechanism step, or the widget.

## 2. How to choose: question shapes

Before drawing, name the question each unit answers, in the reader's words, and find its shape
below. The shape points to the first candidates. Pick the one that makes the unit's idea most
visible on the base scene; when two fit equally, prefer the one higher in the list, because
contrast is the strongest general tool.

| the unit answers ... | its shape | first candidates |
|---|---|---|
| "What is it? When does it count?" | a concept with a condition or a boundary | contrast (example / non-example), extreme cases |
| "Which one is better?" | a criterion or a score | contrast (two choices for the same problem) |
| "How much? What does it depend on?" | a result that grows or shrinks with one input | sweep, extreme cases |
| "What happens, step by step?" | a procedure or a process | sequence |
| "What does it change?" | a mechanism or a rule applied to a fixed case | contrast (before / after) |
| "Why does that happen?" | a cause that leads to an effect | cause chain |
| "What is this even like?" | an abstract idea with nothing physical to draw, or a first contact with an unfamiliar field | analogy, only in "What you already know" and rarely (see its entry) |
| "How big is it? Does it matter?" | a size, a cost, a growth rate | numbers and scale |
| "This is too much at once." (the reader says it is hard, or the unit is dense) | an idea with heavy notation, or with many parts that act on each other | passes: the same unit told three times, easy to hard, on one axis (see its entry) |
| "How do these versions differ, and what do they share?" | three or more versions of the same thing: a history, or rival answers | the units themselves use contrast; the run of units closes with a comparison table (`references/page-structure.md` § The comparison table) |

Contrast is the strongest candidate, not a rule. Use it whenever the unit's idea is a property
that a reader can see change; skip it when another shape fits better (a pure procedure, a cause).

The unit's **part** (`references/page-structure.md` § The parts) is a second hint. The question's
shape decides; the part suggests where to look first:

| part | usual question | first candidates |
|---|---|---|
| element | "What is it?" | contrast (example / non-example), or the plain picture alone |
| fact | "Is that really so? When does it hold?" | contrast or extreme cases that show the fact holding, and failing where it stops |
| reason | "Why does that follow?" | cause chain, whose links point at the blocks it follows from |
| assumption | "Isn't it obvious that ...?" | contrast: what the reader expects beside what really happens |
| convention | "What if we chose differently?" | sweep or before / after in the widget or the transfer question |

## 3. How to combine: rules that keep the page calm

A toolkit invites two failures. These rules prevent them.

**Failure 1: a technique showroom.** Each block uses a different trick, and the page feels busy
and disconnected.

- **One chosen technique per unit**, on top of the defaults. Two only when the question really has
  two shapes (a sweep whose two ends are worth showing as extreme cases).
- **Change the technique only when the question's shape changes.** If three blocks in a row ask
  "what is it?", all three use contrast. Variety is never a reason.
- **Keep the same visual grammar.** A contrast is always side-by-side panels with a result label
  under each; a cause chain always reads in one direction with one arrow meaning "causes". The
  reader learns each format once.

**Failure 2: a broken ladder.** A technique that needs its own picture (an analogy above all)
starts a new drawing, and the reader loses the base scene.

- **Every chosen technique is drawn on the base scene.** Each entry in § 7 says how.
- **An analogy is drawn beside the base scene, never instead of it.** The familiar picture stands
  next to the base-scene picture, with each part matched to its partner, so the reader carries the
  intuition across and then keeps the base scene.
- **The defaults still hold.** Whatever is chosen, the unit still has a picture, a concrete example,
  builds on an earlier rung, and shows before it names.

## 4. The technique plan

Before drawing, write one line per unit, for yourself. Then add one line for the foreshadow: which
block first shows the main question's phenomenon, the sentence, and where the mechanism recalls it.


| unit | part | question in the reader's words | shape | technique | why it fits | how it sits on the base scene |
|---|---|---|---|---|---|---|
| c-area | element + fact | "What does the area limit allow?" | boundary | contrast: example / non-example | the line is the boundary; one plan outside shows it | three plans on the grid, same line |
| c-ceiling | element | "What is this ceiling?" | abstract | analogy | nothing physical to point at yet | room-and-ceiling picture beside the grid, parts matched |
| m-corner | reason (from c-area, c-score) | "Why is the best point a corner?" | why | cause chain | the answer is a chain of three facts | the score line on the grid, three arrows |
| widget | convention (the budget) | "When does rounding work?" | depends on input | sweep + extreme cases | budget is a real input; the small budgets show LP = ILP | the grid with the budget line moving |
| m-uzawa | reason (from c-bins, c-smooth) | "How does GFD spread the pile?" | procedure in heavy notation | passes (axis: representation) + sequence | the steps are simple; the symbols are what is hard | three narrated figures of the same run on the bin row |

If a cell is hard to fill, the unit is not ready: usually its question is unclear, or it holds two
ideas and should be two units.

## 5. Tier 1 — defaults (every unit)

These are described in full in `references/page-structure.md`. In short:

- **Picture.** Every unit that teaches a concept has a figure drawn on the base scene. When the
  unit's paragraph has three or more sentences that point at parts of the figure, the figure is
  narrated: one frame per sentence, synced with the sentence list (`references/page-structure.md`
  § Narrated figures).
- **Concrete example.** Real numbers, real names, one worked case on the figure.
- **Ladder.** The unit builds on an earlier unit and adds one new thing, in coral.
- **Show then name.** The reader sees the thing work before the page gives it its name.

## 6. Tier 2 — the page skeleton (fixed places)

| technique | place | what it does for the reader |
|---|---|---|
| route map (advance organizer) | under the one-sentence answer | shows, before the lesson, which parts the reader will understand, in which order, and how they join into the answer (`references/page-structure.md` § The route map) |
| anchor in the familiar | "What you already know", first paragraph | connects the new idea to something the reader has done |
| foreshadow | the end of the ladder block whose figure first shows the main question's phenomenon; recalled in the mechanism | plants the main question early, on a picture the reader has just understood, so the mechanism lands on prepared ground |
| problem first | "The problem" | makes the reader feel the cost before the mechanism removes it |
| predict first | `<details class="predict">` before the widget or timeline | commits the reader to a guess, so the answer sticks or corrects |
| manipulate one input | "Try it" widget | lets the reader test the model on cases the page did not show |
| transfer question | `<details>` after the widget | checks that the model works on a new case |

### Foreshadow

The skeleton technique that needs the most care, so it gets a full entry.

- **What it does.** While the ladder teaches a background concept, one sentence points at what the
  same picture already shows about the page's main question, and stops there. The reader meets
  the main tension on ground they have just understood; when the mechanism arrives, they
  recognise it ("that is the difference from block 5"). Educational research calls this an advance
  organiser: it prepares a place for the new idea before the idea comes.
- **Where.** At the end of the ladder block whose figure **first** shows the phenomenon the main
  question is about. Usually that is a contrast block, because the difference between its cases is
  the phenomenon.
- **Shape: an observation, a handle, a cue.** Two short sentences, three at most.
  1. **One observation** the reader can check in this block's figure, with its values ("b goes
     from slot 2 to slot 8"; "bin 3 is over by 3.45, bins 2 and 4 by 0.15").
  2. **A handle**: a name of two to four words for that observation ("this long trip", "이 먼
     이동"). Mark it with `<b class="handle">`. The recall uses the same words, so the reader hears
     the callback.
  3. **A cue** to keep it: "Keep this in mind." / "기억해 두자." One open question may follow the
     cue ("Can one push strength suit both?").

  Model: "A에서 B로 가면서 b는 2번 칸에서 8번 칸까지 멀리 간다. 이 <b class="handle">먼 이동</b>을
  기억해 두자." It does not explain anything. It tells the reader where to look and what to carry
  forward.
- **The figure shows; the sentence does not explain.** By default, leave out the cause, the fix and
  why the observation matters. The mechanism says those things, and the reader feels the click when
  they connect them. Cut clauses such as "it decides what a one-cell engine can reach": they hand
  over a conclusion before the reader can see it.
- **A hint toward the answer is allowed; stating it is not.** Sometimes the best foreshadow leans
  toward the answer. Write the lean as an open question, or as a side-by-side view that the reader
  completes ("The pins' x values are 1, 3, 4, and the tree joins at x = 3."; "Is the best dot next
  to it?"). Never write it as a settled fact ("the join point takes the middle value of each list").
  The test: could someone who has seen only this figure, and not the mechanism, write the sentence?
  If not, it states the answer. Turn it back into an observation or a question.
- **Grounded in the figure.** The observation is something the reader can see in that block's
  figure (the two LUT counts under the two panels). A preview of something not on the page is a
  promise the reader cannot check.
- **Once or twice per page.** More than that and every block sounds like a trailer; the effect
  fades.
- **Always recalled, by its handle.** The mechanism section calls it back with the handle's own
  words and links to the block ("Recall the long trip from block 1"), with `data-recalls` on that
  element. A foreshadow that is never recalled leaves a loose end. A recall that renames the
  observation ("the difference" for "the long trip") makes the reader search for the link.
- **Examples, good and weak.**

  | foreshadow | verdict |
  |---|---|
  | "A에서 B로 가면서 b는 2번 칸에서 8번 칸까지 멀리 간다. 이 **먼 이동**을 기억해 두자." | model: an observation, a handle, a cue |
  | "The LP corner (3.5, 1.5) is not a dot. Is the best dot next to it?" | good: the lean is an open question |
  | "…Keep this distance in mind: it decides what an engine that moves one cell at a time can reach." | weak: the last clause gives the reason away; end at "in mind" |
  | "…The join point takes the middle value of each list." | weak: states the answer (the median); put the numbers side by side and let the reader see it |
  | "Nothing yet says where the cells go when nothing holds the ends." | weak: nothing concrete to carry; name what is visible (the two pads) |
  | "This picture already shows the heart of the question: …" | filler opener; start with the observation |

## 7. Tier 3 — chosen per unit (full entries)

Every entry has the same parts: what it does for the reader, use it when, avoid it when, how to
draw it on the base scene, and an example.

### Contrast

- **What it does.** People notice a property when they see it change while everything else stays
  still. Two to four cases side by side make the property visible; a failing case shows where the
  concept stops.
- **Kinds.** Example / non-example (a condition or limit). Two choices for the same problem (a
  score or criterion). Before / after (what a mechanism or rule changes).
- **Use it when** the idea is a property that can differ between cases.
- **Avoid it when** the cases would differ in two things at once, or the idea is a procedure (use
  sequence) or a cause (use cause chain).
- **On the base scene.** Small multiples: equal panels in one row, each `<g class="case">`, the same
  scene and scale in every panel, one thing varied, a result label under each panel. The caption
  says what varies and what is fixed. Full rules: `references/page-structure.md` § Show each idea
  in contrasting cases.
- **Example.** Cuts of node n with 2, 3 and 4 inputs: 2 and 3 fit a 3-input LUT, 4 does not. Two
  mappings of one network: both depth 2, area 3 against 2.

### Sweep

- **What it does.** Shows how a result moves as one input moves, so the reader sees the trend, not
  one point.
- **Use it when** the question is "how much?" or "what does it depend on?" and there is one input
  that matters.
- **Avoid it when** the result jumps between unrelated states (use contrast) or the input is not
  something a reader can picture changing.
- **On the base scene.** Three or four panels at increasing values of the input, the rest fixed, the
  value in each panel's title and the result under it. In the widget, the same sweep becomes a
  slider.
- **Example.** The score line 2x + 5y at 6, 14.5 and 16: it crosses the region, touches it only at a
  corner, then misses it.

### Extreme cases

- **What it does.** Pushes an input to its smallest or largest sensible value, or to the edge where
  the behaviour changes. The ends are often the easiest cases to reason about, and they show the
  limits of the rule.
- **Use it when** the concept has a limit worth knowing ("with fractions allowed, the gap is
  zero"; "with one LUT input left, every cut fails"), or to check a reader's intuition against a
  case they can work out in their head.
- **Avoid it when** the extremes are degenerate in a way that teaches nothing (an empty problem) or
  break the model's assumptions without saying so.
- **On the base scene.** Two panels at the two ends (or one end beside the typical case), each
  labelled with its value and result. In the widget, give the slider's range real ends and say
  what happens there.
- **Example.** Area budgets 2 to 5: the LP corner lies on the x axis at a whole number, so the LP
  and the ILP agree and rounding is harmless.

### Sequence

- **What it does.** Shows a procedure as states in order, so the reader follows the motion and can
  compare any two steps.
- **Use it when** the answer to the question is a series of states: an algorithm, a protocol, a
  pipeline.
- **Avoid it when** the idea is static, or the steps add nothing the reader must see.
- **On the base scene.** A timeline whose frames are drawn on the base scene, one change per frame.
  Rules: `references/timeline.md`. When the procedure moves through stages (levels, pipeline
  stages, recursion depths, the steps of a loop), lay the stages out in space and let time move
  across them: every stage has a fixed place in every frame, the current stage is lit, earlier
  results stay visible, and a small position map shows where the procedure is
  (`references/timeline.md` § Space first, then time).
- **Example.** Branch and bound in eight frames: solve, split on x, solve A, split A on y, best so
  far 11, best so far 14, skip B, done.

### Passes

- **What it does.** Tells the same unit two or three times, easy to hard, and changes only one
  thing between the passes. The reader meets the hard version after two easier versions of the
  same thing, so each new word or step names something they have already seen. Education research
  calls the two forms below *concreteness fading* and *simple-to-complex sequencing*.
- **Pick the axis by asking why the idea is hard.**

  | axis | what changes between passes | what stays fixed | use it when the hard part is |
  |---|---|---|---|
  | `representation` | the way of saying it: (1) the picture only, in plain words the ladder already used; (2) the numbers, said in words ("0.2 times the part above 0.75"); (3) the field's notation, each formula pinned to a frame ("λ<sub>k+1</sub> = λ<sub>k</sub> − α(φ − κ)") | the example, the run, the frames | the notation: the steps are simple once the symbols are known |
  | `complexity` | the size of the example: (1) the smallest example that shows the core effect, small enough to work out in your head; (2) the page's standard example, where a second effect first appears; (3) the target form, such as the exam-sized case, the slide's case or a variant | the way of saying it: the same words, picture grammar and level of notation | many parts that act on each other: each part is easy, but together they are hard to follow |

- **Rules.**
  - Change one axis between two passes. A pass that makes the example bigger *and* switches to
    formulas leaves the reader unable to tell what is new. To use both axes, go in order: first
    the representation passes on the small example, then hold the notation and grow the example.
    Never go diagonally.
  - Every pass is drawn on the base scene with the same drawing function. An easy pass hides
    layers (a chart, the numbers); it does not draw a different picture.
  - On the complexity axis, each bigger example must show one effect the smaller one could not.
    If it shows nothing new, it is the same pass twice: cut it.
  - The last pass is the target form: the slide's notation, or the exam-sized case.
  - Each pass is a narrated figure (3–8 sentences, one per frame). It opens with a pass label
    (`<p class="label pass-label">Pass 1 · picture only</p>`) and may end with one line naming
    what it left out for the next pass.
  - Pass 1 adds no new terms: it uses only words the ladder or the plain background already gave.
    `references/voice.md` § Vocabulary per pass.
  - Say once, near the top of the page, that the explanations come in passes and that pass 1 alone
    gives the big picture. A reader who stops after pass 1 should still leave with a true model.
- **Use it when** the reader asks for an easier version, says the page is hard, or the unit holds
  three or more new terms, a formula, or a procedure with many parts that act on each other.
- **Avoid it when** one figure already makes the unit clear, or the passes would repeat without
  adding. Passes cost length: a unit roughly triples in sentences and frames, so use them on the
  units that are hard, not on every unit by default (unless the reader asks for that).
- **On the base scene.** Two or three narrated figures in a row, built with `assets/narrated.js`
  from one `drawPanel`. The panel takes a flag for the easy pass (plain labels, fewer layers).
- **Examples.** Axis `representation`, mPL5's GFD placement: pass 1 "a crowded bin pushes its
  cells out; if it stays crowded, it pushes harder"; pass 2 "each bin adds 0.2 × (its smoothed
  density − 0.75) to its λ: bin 3 gets 0.29"; pass 3 "λ<sub>k+1</sub> = λ<sub>k</sub> − α(φ − κ),
  0 − 0.2 × (−2.19 + 0.75) = 0.29". Axis `complexity`, multilevel placement: 4 cells and one
  coarsening level (just merge and place); then 8 cells and two levels (interpolation appears);
  then the full V-cycle with refinement at every level.

### Cause chain

- **What it does.** Answers "why" with a short chain of facts, each one causing the next, so the
  reader can retrace the argument on their own.
- **Use it when** the question is "why does that happen?" and the answer has two to four links.
- **Avoid it when** the links are not causes (a list of features is not a chain), or the chain
  needs more than four links (split it, or the idea is too large for one unit).
- **On the base scene.** The figure shows the situation once, with numbered callouts placed on the
  parts each link refers to, joined by arrows that all mean "causes". Or two to four panels, one
  per link, each adding the consequence of the previous one. One reading direction.
- **Example.** Why the best LP point is a corner: the score is a straight line → raising the score
  slides the line without turning it → the last point the line touches as it leaves the region is
  a corner.

### Analogy

**Restricted: only in "What you already know", and rarely.** At most one analogy per page, in one
ladder block, and only when the defaults cannot do the job: no literal picture on the base scene
shows the idea yet. Most pages need none. Never use one in the problem, the mechanism or the
widget: by then the reader has the base scene, and a second picture from another world only
competes with it.

- **What it does.** Gives a newcomer an intuition from a world they already know, so an abstract
  idea gets a shape before it gets its precise form.
- **Use it when** the idea is abstract and has nothing physical to draw yet, or the reader is new to
  the whole field, and only in a "What you already know" block.
- **Avoid it when** a literal picture on the base scene already shows the idea (then the analogy
  adds a second picture for no gain), or when the analogy breaks in a place the page relies on.
- **On the base scene.** Two panels side by side: the familiar picture and the base-scene picture,
  with matched parts labelled with the same letters or colors ("room height" ↔ "LP score"). The
  analogy never replaces the base scene; the next unit continues from the base-scene panel.
- **Where it breaks.** Every analogy breaks somewhere. Say where in one sentence, in a
  `<p class="breaks">`, right after the figure. An analogy without this sentence plants a wrong
  belief that the page never removes.
- **Example.** The LP relaxation's score is a ceiling: like a room's ceiling, nothing standing in
  the room (no whole plan) can be taller. Where it breaks: a room's ceiling is known before you
  move in; the LP ceiling is found by solving the relaxation, and it changes when the problem is
  split.

### Numbers and scale

- **What it does.** Turns "big", "slow" or "expensive" into a number the reader can compare, and
  draws sizes in their true ratio.
- **Use it when** the point is a size, a cost or a growth rate ("why not check every plan?").
- **Avoid it when** the numbers are invented or the precision is false; give the source or the
  arithmetic.
- **On the base scene.** Bars or areas drawn to scale next to the scene, or the count written onto
  the scene ("14 dots") and then the real-size count beside it.
- **Example.** The toy has 14 whole plans; a scheduling ILP with 300 binary variables has 2^300,
  about 2 × 10^90.

## 8. Markup and checks

Each ladder block, and each mechanism figure that uses a Tier 3 technique, names it:

```html
<div class="concept" id="c-ceiling" data-builds-on="c-whole" data-technique="analogy"> ... </div>
<figure class="sheet wide" data-builds-on="c-whole" data-technique="contrast"> ... </figure>
```

Each unit also names its part with `data-part` (`element`, `fact`, `reason`, `assumption`,
`convention`; one or two), a reason lists what it follows from in `data-from`, and the widget or
transfer question that changes a convention names it in `data-changes`. The rules and checks are in
`references/page-structure.md` § The parts.

A foreshadow is `<p class="foreshadow">` inside its ladder block, with its handle in
`<b class="handle">`. The element in the mechanism (or the problem) that recalls it carries
`data-recalls="<block id>"`, links to the block and repeats the handle's words. The checker warns
when the ladder has no foreshadow or more than two, when a foreshadow runs past three sentences or
has no handle, and when a foreshadow's block is never recalled or its recall does not repeat the
handle.

Passes name their axis next to the technique, on the unit that holds them: a ladder block, or the
`<section id="problem">` or `<section id="mechanism">` tag when the whole section is told in passes.

```html
<div class="concept" id="c-bins" data-technique="passes contrast" data-axis="representation"> ... </div>
<section id="mechanism" data-technique="passes" data-axis="complexity"> ... </section>
```

Allowed values: `contrast`, `sweep`, `extremes`, `sequence`, `cause-chain`, `analogy`, `scale`,
`passes`. Two values are separated by a space. `scripts/check_page.py` warns when a ladder block has
no `data-technique`, when a value is unknown or more than two are given, and when the markup does
not match the technique:

| technique | the checker expects |
|---|---|
| contrast, sweep, extremes | at least two `<g class="case">` panels |
| analogy | a `<p class="breaks">` sentence in the block |
| cause-chain | arrows in the figure (`marker-end`) |
| sequence | a timeline (`figure.timeline`) |
| scale | nothing mechanical; check the numbers by hand |
| passes | `data-axis` set to `representation` or `complexity`, and two or three narrated figures, each after a pass label (`p.pass-label`, or `h3.pass-label` when a section is split into passes) |
