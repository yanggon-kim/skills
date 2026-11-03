# Timeline: showing a concept that changes over time

Many concepts are procedures: a state that changes step by step or over time. Git rebasing a
branch, a pipeline moving instructions through stages, a cache filling, a protocol exchanging
messages, an algorithm sorting an array. Prose and still figures describe the states, but the
reader has to build the motion in their head. A timeline shows it.

A timeline has two views of one sequence of frames:

| view | what the reader sees | what it is good for |
|---|---|---|
| **storyboard** | every frame side by side, numbered, each with a one-sentence caption | comparing states, seeing the whole procedure at once, reading without JavaScript or motion |
| **player** | one large frame that animates into the next, with play, pause, step and a scrubber | following motion and continuity: what moves where, what overlaps in time |

You write only the storyboard. The template's script builds the player from the same frames, so
the two views cannot disagree.

## Contents
1. When to use a timeline
2. Plan the frames
3. Draw the frames
4. Markup
5. Captions and the prediction
6. Length
7. Checks

## 1. When to use a timeline

Use one when the answer to the reader's question is a sequence: "what happens when ...", "how does X
proceed", "walk me through", or any mechanism whose state changes over steps, cycles or time.
Do not use one for a static structure (a memory hierarchy, a class diagram) or for a relationship
between quantities (Bayes' rule). Those use ordinary still figures.

For a procedure, the timeline is the mechanism's figure, placed in the mechanism section. It is part
of the page's figure ladder (`references/page-structure.md` § Figures): draw its frames on the
page's base scene, so frame 1 looks like the top rung of the concept ladder the reader just read,
and the frames then add the procedure's changes one per step.

- If the concept also has a real input to change (pipeline depth, number of commits, cache size),
  keep the normal "Try it" widget for that input.
- If the procedure is the whole concept, the player is the interaction. The "Try it" section then
  holds the prediction question before the player is used, and a transfer question afterwards. Do
  not build a second widget that teaches nothing new.

## 2. Plan the frames

Write the procedure as a list of states before drawing anything.

- **3 to 12 frames.** One frame per meaningful change. Merge steps that change nothing the reader
  must see. A long procedure (dozens of steps) shows its key frames and says in a caption what
  repeats ("Steps 3–5 repeat for every commit.").
- **One change per frame, when possible.** The reader should be able to name what changed between
  frame 3 and frame 4 in one sentence. That sentence is the caption.
- **Same layout in every frame.** Every frame contains the same elements in the same places, except
  for what the step changes. Fixed positions are what make the changes visible.
- **At most seven new primary elements per frame**, the same limit as any figure. Elements the
  reader already knows from the concept ladder do not count.
- **Drawn on the base scene.** Elements keep the positions, names and shapes they had in the ladder
  figures. If the base scene is wider than a frame allows, a frame may show the part of the scene
  the procedure touches, at the same relative positions.

### Space first, then time

Many procedures move through **stages**: the levels of a multilevel V-cycle, the stages of a
pipeline, the depths of a recursion, the layers of a memory hierarchy, the steps of a loop that
repeats. For these, a frame that shows only the current state tells the reader *what* happens but
not *where in the procedure* it happens. Lay the procedure out in space first, then let time move
across it:

1. **Give every stage a fixed place in every frame.** Draw all the stages at once (the three
   levels stacked, the five pipeline stages in a row), including the ones the procedure has not
   reached yet; draw those empty or dashed.
2. **Light the current stage only.** Coral marks the stage this frame works on; the rest keep their
   idle look. As the frames advance, the light moves through the layout. That motion is the
   procedure's time.
3. **Keep earlier results.** A stage that is done keeps its result (its order, its WL, its value)
   in later frames, so the reader can compare the current stage with the ones before it without
   stepping back.
4. **Add a small position map** beside the scene when the path through the stages is not a
   straight line: the V of a V-cycle, the circle of a loop, a pipeline strip. A dot on it marks the
   current step. The map answers "where am I?" while the scene answers "what is happening?".

Test: cover the caption of any one frame. Can the reader still say which stage the procedure is in,
and what the earlier stages produced? If not, the frame shows time without space.

Example: the multilevel-placement page's V-cycle. Each frame shows level 3 (8 cells), level 2
(4 clusters) and level 1 (2 clusters) on the same 8-slot row, stacked top to bottom. Coarsening
lights the levels from top to bottom, and placement and refinement light them from bottom to top.
Each level keeps its WL once it is placed (WL 4, then 10, then 14), and a small V on the right
carries a dot at the current step.

## 3. Draw the frames

Each frame is a complete inline SVG. All frames share the same `viewBox` and the same set of keyed
elements.

- **Key everything that changes.** Give each element that moves, appears, disappears, changes
  color or changes text a `data-key` that is unique within its frame and identical across frames:
  `<rect data-key="commit-D" ...>`. Elements without a key are background: draw them identically
  in every frame.
- **Every frame has every keyed element.** An element that is not present at a step stays in the
  frame with `class="off"` (opacity 0). Never leave it out: the player matches elements by key and
  can only animate what exists in both frames.
- **Narrated figures use the same player.** A narrated figure (`references/page-structure.md`
  § Narrated figures) is a timeline whose frames follow the sentences of a paragraph instead of the
  steps of a process. For a comparison frame, give every frame two panel slots: one panel in the
  middle with the second slot hidden, then both side by side in the comparison frame. Key every
  element of both slots, so the player can slide the first panel aside.
- **Watch out for time-cursor frames.** A natural way to generate frames is to draw the whole
  process once and cut it at a moving "now": frame k shows only what happened before time t_k. Done
  naively, this breaks both rules above — future bars are left out instead of hidden, and the keys
  sit on whole rows while the bars inside them change — so the player clones frame 1 and never
  shows anything new, while the storyboard (each frame drawn on its own) looks right. Generate
  every bar, label and arrow in every frame, each with its own key; give the ones after "now" the
  class `off`, and clip the one that "now" crosses by changing its `width`. `check_page.py` reports
  an ERROR when frames differ outside keyed elements.
- **What animates.** Between frames, the player moves these attributes smoothly: `x`, `y`, `width`,
  `height`, `cx`, `cy`, `r`, `rx`, `ry`, `x1`, `y1`, `x2`, `y2`, `opacity`, `stroke-width`, and a
  `transform` of the form `translate(a b)`. Class changes (color, `.off`) fade through the
  template's CSS transitions. Text and any other attribute (a path's `d`, for example) switch at
  the end of the move.
- **Moving a group.** To move a box with its label, wrap them in `<g data-key="..."
  transform="translate(a b)">` and change only the `translate`. The player compares a keyed
  element's own attributes, not its children, so the children of a keyed group must be identical
  in every frame.
- **Readable at storyboard size.** Frames show at about 20rem wide in the storyboard, and narrower
  on a phone. Use a `viewBox` about 400 units wide (at most 480) and text at least 15 units high, so
  labels stay readable in the small view. Put fewer, larger labels in a frame rather than many
  small ones; the caption carries the detail. The player shows the same SVG larger.
- **Wide frames, when a frame must hold many rows.** If each frame has to show many rows at once
  (a time chart with five or six lanes and state readouts), shrinking it to 480 units makes the
  labels unreadable. Then add the class `wide-frames` to the timeline figure: the storyboard shows
  one frame per row at full width, the player drops its width cap, and the frame `viewBox` may be
  up to about 720 units wide. Prefer the narrow frame whenever the content allows it; wide frames
  make a long storyboard.
- **Shared definitions go once, outside the frames.** Arrowheads and other `<defs>` would repeat
  their ids if every frame carried them. The template already defines `#arrow` and `#arrow-accent`
  in a hidden SVG at the top of the page; add any other shared definition there, or in a hidden SVG
  just before the timeline, and let every frame refer to it with `url(#id)`:
  `<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs><marker id="tl-arrow" ...>...</marker></defs></svg>`.
- **Color.** Coral (`.f-accent`, `.s-accent`) marks what changed in this frame. Everything else
  keeps its normal ink and idle colors, so the eye goes to the change.
- **Generate, do not hand-copy.** Produce each frame from the page's base scene by changing
  attributes, with the same short Python or Node script that draws the ladder figures. Copying SVG by hand across ten frames
  invites a mismatched key or a shifted element.

## 4. Markup

The template already contains the CSS and the player script. Put this block in the mechanism
section, in the page language, with one `<li class="frame">` per frame:

```html
<figure class="timeline sheet wide" data-step-word="Step" data-of-word="of"
        aria-labelledby="tl-caption">
  <div class="player js-only">
    <div class="stage"></div>
    <p class="stage-caption" aria-live="polite"></p>
    <div class="controls">
      <button type="button" data-act="play" data-play-label="Play" data-pause-label="Pause">Play</button>
      <button type="button" data-act="prev" aria-label="Previous step">←</button>
      <button type="button" data-act="next" aria-label="Next step">→</button>
      <input type="range" class="scrub" min="0" max="1" step="1" value="0" aria-label="Step">
      <output class="counter"></output>
    </div>
  </div>
  <ol class="storyboard">
    <li class="frame">
      <svg viewBox="0 0 400 220" role="img" aria-labelledby="f1-title f1-desc">
        <title id="f1-title">Step 1: ...</title>
        <desc id="f1-desc">...</desc>
        <!-- keyed and background elements -->
      </svg>
      <p class="frame-caption">One sentence: what this step changes.</p>
    </li>
    <!-- more frames -->
  </ol>
  <figcaption id="tl-caption">What the frames show, what each color and arrow means, and what
  the timeline leaves out.</figcaption>
</figure>
```

- Give each frame's `<title>` and `<desc>` ids unique to that frame (`f1-title`, `f2-title`, ...).
- Translate every visible label and the `data-*-word` and `data-*-label` attributes into the page
  language.
- Optional pacing: `data-tween-ms` (move time, default 600) and `data-hold-ms` (pause on each frame
  during play, default 1600) on the `<figure>`. Slow the hold for frames with long captions.

How the player behaves, so you can describe it correctly on the page:

- It starts paused on frame 1. It never plays by itself.
- Play steps through the frames and stops on the last one. Pressing play there starts again from
  frame 1.
- Previous, next, the scrubber, and clicking a storyboard frame all jump to that frame and pause.
- The current frame is outlined in the storyboard, and its caption shows under the stage.
- For readers who ask for reduced motion, frames change instantly, without moving.
- Without JavaScript, the player is hidden and the storyboard alone teaches the procedure.

## 5. Captions and the prediction

- **One caption per frame**, one sentence in the page's voice, naming what changed and, where it
  matters, why: "Git copies commit D onto C. The copy gets a new ID, D′." Captions are the text
  version of the timeline. Read them alone: they must tell the whole procedure.
- **Predict before playing.** Put a `<details class="predict">` question right before the timeline:
  "Before you press play: after step 3, where does the branch name point?" The answer names the
  frame that shows it.
- **Transfer after.** A second question asks about a variant the timeline did not show ("What
  changes if commit E conflicts with C?").
- **At most three questions on the page.** With both a timeline and a widget, ask one before the
  timeline, one before the widget, and one transfer question at the end.

## 6. Length

Frame captions are the timeline's text version, so they are not counted against the page's prose
budget. `check_page.py` reports them separately. Keep each caption to one sentence; nine frames add
about 150–250 words of captions on top of the usual 800–2,200 words of prose.

## 7. Checks

`check_page.py` verifies the mechanical part: at least two frames, a caption in each, the same
`viewBox` and the same set of `data-key` values in every frame, nothing changing between frames
outside keyed elements (what the player can never show), the player controls, and no autoplay.
Then check by eye:

1. **Storyboard only.** Read the frames and captions top to bottom with the player ignored. Is the
   procedure complete?
2. **Where am I?** For a procedure with stages, take any one frame alone: can you tell which stage
   it is in and what the earlier stages produced (§ Space first, then time)?
3. **Player only.** Play it through, step back and forth, drag the scrubber to the end and back. Does
   anything jump, overlap or move the wrong way? Press "next" a few times and compare the stage
   with the matching storyboard frame: they must show the same picture. A storyboard that looks
   right says nothing about the player, because each frame is drawn on its own.
4. **Same story.** The prose, the captions and the frames name the same steps in the same order.
