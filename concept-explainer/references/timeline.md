# Timeline: showing a concept that changes over time

Many concepts are procedures: a state that changes step by step or over time. Git rebasing a
branch, a pipeline moving instructions through stages, a cache filling, a protocol exchanging
messages, an algorithm sorting an array. Prose and one still diagram describe the states, but the
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
between quantities (Bayes' rule). Those keep the normal single diagram.

For a procedure, the timeline **is** the page's one diagram, placed in the mechanism section.

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
- **At most seven primary elements per frame**, the same limit as any diagram.

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
- **Shared definitions go once, outside the frames.** Arrowheads and other `<defs>` would repeat
  their ids if every frame carried them. Put them once in a hidden SVG just before the timeline,
  and let every frame refer to them with `url(#id)`:
  `<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs><marker id="tl-arrow" ...>...</marker></defs></svg>`.
- **Color.** Coral (`.f-accent`, `.s-accent`) marks what changed in this frame. Everything else
  keeps its normal ink and idle colors, so the eye goes to the change.
- **Generate, do not hand-copy.** Write the base scene once, then produce each frame by changing
  attributes, for example with a short Python or Node script. Copying SVG by hand across ten frames
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
about 150–250 words of captions on top of the usual 600–1,300 words of prose.

## 7. Checks

`check_page.py` verifies the mechanical part: at least two frames, a caption in each, the same
`viewBox` and the same set of `data-key` values in every frame, the player controls, and no
autoplay. Then check by eye:

1. **Storyboard only.** Read the frames and captions top to bottom with the player ignored. Is the
   procedure complete?
2. **Player only.** Play it through, step back and forth, drag the scrubber to the end and back. Does
   anything jump, overlap or move the wrong way?
3. **Same story.** The prose, the captions and the frames name the same steps in the same order.
