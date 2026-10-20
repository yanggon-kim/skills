# Storyboards and Morph

A process that changes over time (a protocol, a pipeline, an algorithm step by step, a timing diagram)
is shown as a **storyboard**: a few frames drawn on one fixed layout, where each frame changes one thing.
In the prototype a player tweens the frames; in the deck each frame is a slide and PowerPoint's Morph
transition tweens between them.

## Contents
- When to use a storyboard
- Drawing frames
- Keys: how elements are paired
- What the deck does
- Checking it

## When to use a storyboard

Use one when the order of events is the point (what happens first, what waits for what, what a step
changes). Keep it to 3–7 frames; each frame's step title names the change ("ACT opens a row", "Probe
slot 4"), and its caption (1–3 sentences, 16 pt in a 2.25 in column) says what to look at. A static
comparison is a figure, not a storyboard.

Why one slide per frame (not PowerPoint animations): every step stays visible in a PDF, a printout or
a viewer without Morph; slide numbers and notes are per step, so the speaker script follows the frames;
and the frames are the same drawings the prototype shows.

## Drawing frames

- **One fixed layout.** Every frame draws the same scene at the same coordinates and changes only what
  the step changes (a colour, a label, a moved marker). The deck crops all frames with one shared box
  (the union of their content), so a frame that adds far-away content shrinks every frame.
- **Proportions.** The frame area is 6.05 × 4.4 in (about 1.4 : 1); draw frames close to that.
- **Highlight the change.** The element that changed in this step is gold (`f-accent`, `f-tint`,
  `s-accent`, or a `<g class="hot">` group); finished steps can go gray (`pend` for "still to come").
- **Hide, don't delete.** An element that appears later is present in every frame with class `off` in
  the frames where it is hidden; then Morph fades it in.
- **Step text in the column, not in the figure.** A short note inside the figure is fine; the sentence
  goes in `.frame-caption`, the script in the frame's notes.

## Keys: how elements are paired

- An element with `data-key="k"` is named `!!k` on every frame slide (`!!k.r0`, `!!k.t1` for the
  children of a keyed group; `!!k.0`, `!!k.1` for the segments of a keyed polyline). Morph pairs objects
  whose names start with `!!` and match, and tweens their position, size and colour.
- Elements **without** a key are named `!!u0`, `!!u1`, … in drawing order. Morph pairs them by that
  order, so every frame must have the **same number of unkeyed elements** in the same order; the lint
  and QA fail otherwise. Give a key to everything that moves, changes, appears or disappears, and leave
  only the static scene (axes, lane labels, fixed boxes) unkeyed.
- Keys must be unique within a frame.
- The step dots (`!!dot0…`) and the step label (`!!steplabel`) are keyed by the deck itself, so they
  morph too.

## What the deck does

- Frame 1 is a slide with the storyboard's title; frames 2…n are slides with the same title and a Morph
  transition. The transition is written as `mc:AlternateContent`: Morph (`p159:morph option="byObject"`,
  speed slow) for PowerPoint 2019 / 365, a fade fallback for everything else. It sits right after
  `p:clrMapOvr` in the slide XML, where the schema expects it.
- The right-hand column: step dots (gold = this step, gray = done, light = to come), "Step i of n"
  (12 pt gray) with the step title (16 pt bold navy), and the caption placeholder (16 pt), at one
  position on every frame so nothing jumps between slides.
- Each frame slide carries that frame's notes; the storyboard's `.source` is appended to each.

## Checking it

- `deck_qa.py` morph: the Morph count equals the number of follow-on frames, and consecutive frames of
  one storyboard have the same set of `!!u<n>` names and no duplicate names.
- The render (LibreOffice) shows each frame as a still with a fade; look that each frame reads on its
  own and that the highlight sits on the change.
- Morph itself is seen only in PowerPoint (2019 / 365) or Keynote's import: open the deck there and step
  through a storyboard once if the motion matters for the talk.
