# The HTML prototype format

The prototype is one HTML page built on `assets/prototype-template.html` (keep its `<style>` and
`<script>`). Each slide is a `<section class="slide">` whose `.canvas` previews the deck slide at
10 × 5.625 in; the speaker notes and the provenance sit under the canvas. `html_to_spec.py` reads the
markup below; the canvas styling is only a preview, so what matters is that the classes are right.

`scripts/proto.py` writes all of this for you (Python API or JSON); write it by hand only for small edits.

## Contents
- Page skeleton and the parts list
- Slide kinds: title, outline, divider, content, story, closing, appendix
- The content area: figure, table, stats, cards, figure + stats
- Figures: the SVG vocabulary
- Notes and provenance
- proto.py API
- What the lint checks
- What the preview does

## Page skeleton and the parts list

```html
<main class="deck" data-title="Talk title" data-subject="One line" data-author="Name">
  <ol class="parts-def">                       <!-- the outline: one item per part, in order -->
    <li data-part="Summary"><b>Summary</b><span>the talk in one slide</span></li>   <!-- always first -->
    <li data-part="Background"><b>Background: the problem</b><span>what the audience needs first</span></li>
    <li data-part="Evaluation"><b>Evaluation</b><span>method, results</span></li>
  </ol>
  <section class="slide" data-kind="title">…</section>
  …
</main>
```
`data-part` is the part's id and the PowerPoint section name; `<b>` is the label shown on the outline,
`<span>` a one-line subtitle. **The first part is always `Summary`** (proto.py adds it; the lint stops
without it). The title slide is the "Opening" section; the outline and the summary slide are the
"Summary" section; appendix slides are "Appendix".

## Slide kinds

**Title** — the template's Title Opener: logo, title and subtitle between the two brand rules, the byline
(authors, venue) across the rules' width below them, presenter and date in the layout's slots. **Nothing
else: no key points, numbered or bulleted.** The talk's key points live only on the Summary slide two
slides later, so the opening is not said twice; the lint stops on a list here and QA fails on badges.
```html
<section class="slide" data-kind="title">
  <div class="canvas">
    <h1>Short title</h1><p class="subtitle">Full title or one-line framing</p>
    <div class="byline"><p>Authors</p><p>Venue, year · affiliations</p></div>
    <p class="presenter">Presenter: ______</p><p class="date">Date: ______</p>
  </div>
  <details class="notes" open><summary>Speaker notes</summary><p>Script…</p></details>
</section>
```

**Outline and dividers** — no canvas markup needed: the preview and the deck draw them from the parts
list. The outline comes right after the title and lists every part with part 1, Summary, highlighted
("Next: part 1 of 4"): it is also the Summary part's divider, so there is no separate Summary divider
(the lint stops on one: two outline slides in a row). A divider opens each later part, with that part
highlighted ("Next: part 2 of 4"). Each carries its own short script (what this part is for; the
outline's names the parts and leads into the summary).
```html
<section class="slide" data-kind="outline" data-part="Summary"><details class="notes" open>…</details></section>
<section class="slide" data-kind="divider" data-part="Background"><details class="notes" open>…</details></section>
```

**Summary** — a content slide (any area form; a figure with its headline numbers beside it works well)
in part `Summary`, right after the outline, titled `Summary: <core message>`. The title must stay one
20 pt line: shorten the message and say the full sentence in the notes. `d.summary(message, …)` writes it.
```html
<section class="slide" data-kind="content" data-part="Summary">
  <div class="canvas"><h2>Summary: shrink every operand; use each weight read twice</h2> … </div> …
</section>
```

**Content** — one core message: title, the area, the band.
```html
<section class="slide" data-kind="content" data-part="Background" data-see="A1" data-role="method">
  <div class="canvas">
    <h2>One-line core message</h2>
    <div class="area"> … one of the area forms below … </div>
    <ul class="band"><li>Supporting sentence one.</li><li>Supporting sentence two.</li></ul>
  </div>
  <details class="notes" open><summary>Speaker notes</summary><p>Script…</p></details>
  <p class="source">Redrawn from the paper's Fig. 4.</p>
</section>
```
`data-see` points to an appendix slide; `data-role` is `method` or `result` (the lint checks that
results have a methodology slide before them).

**Story** — a storyboard: one deck slide per frame (references/animations.md).
```html
<section class="slide" data-kind="story" data-part="Background">
  <div class="canvas"><h2>One-line message</h2><div class="farea"></div><div class="stepcol"></div></div>
  <ol class="storyboard">
    <li class="frame" data-step="Short step title"><svg viewBox="…">…</svg>
      <p class="frame-caption">One to three sentences for the step column.</p>
      <details class="notes"><summary>notes</summary><p>Script for this frame…</p></details></li>
    …
  </ol>
  <p class="source">…</p>
</section>
```
A `.notes` block directly in the section (outside the frames) is an overview; it is prepended to the
first frame's notes.

**Closing** — title (usually "Questions"), a one-sentence recap, the citation, up to three questions that
open the discussion.
```html
<section class="slide" data-kind="closing" data-part="Discussion">
  <div class="canvas"><h2>Questions</h2><p class="recap">…</p><p class="citation">…</p>
    <ol class="questions"><li>…</li><li>…</li></ol></div>
  <details class="notes" open>…</details>
</section>
```

**Appendix** — any content or story slide with `data-appendix="A1"`, placed after the closing slide. The
deck titles it "A1 · Title" and adds an "Appendix" index slide before the first one (rows: id, title,
"from slide N"); the notes get "(Back to slide N: …)". Put full tables, extra numbers, derivations and
per-case breakdowns here, and point to them from the main slide with `data-see="A1"`.

## The content area

| form | markup inside `.area` | deck layout |
|---|---|---|
| figure | `<figure class="visual"><svg …></svg></figure>` | cropped to content, scaled to fill 8.5 × 3.2 in, centred |
| table | `<table data-colw="2,5,5" data-font="14">` with `<thead>`, `<tbody>`; `<tr class="ours">` highlights a row; `class="dense"` = 12 pt | full width at the top of the area, grown to fill it (type up to 18 pt, then taller rows); header row accent1, borders accent4, first column bold (`data-bold-first="false"` to drop) |
| stats | `<div class="stats"><div class="stat hot"><b class="metric">4.9×</b><span class="label">what it measures (Fig. 9)</span></div>…</div>` | 2–4 big numbers in a row; `hot` = gold rule, navy number |
| cards | `<ol class="cards"><li><b>Head</b><span>Two sentences.</span></li>…</ol>` | up to three numbered cards filling the area |
| figure + stats | a `figure.visual` followed by a `div.stats` | figure on the left (6 in), up to four numbers stacked on the right |

Tables: 13 or 14 pt; 12 pt only for a dense setup table. A table that does not fit is split or moved to
the appendix, never shrunk. `data-colw` gives relative column widths (else they follow the longest cell);
give the first column room for its longest row label, because the deck grows the type only while no row
label wraps more (translation-layout.md, "Tables"). The preview shows the author's size; the deck's is
larger when the table is short.

## Figures: the SVG vocabulary

Figures are inline SVG converted to native, editable PowerPoint shapes, so they stay sharp, re-colour with
the theme and can be keyed for Morph. Only this vocabulary converts:

| element | notes |
|---|---|
| `<rect x y width height class>` | rounded corners are ignored |
| `<circle cx cy r>`, `<ellipse cx cy rx ry>` | drawn as ovals |
| `<line x1 y1 x2 y2>`, `<polyline points>` | unfilled; `marker-end="url(#arrow)"` = arrowhead (markers: `arrow`, `arrow-accent`, `arrow-c2`, `arrow-pencil`) |
| `<text x y text-anchor class>` | one line; `font-size="18"` overrides the class size |
| `<g transform="translate(x y)">` | groups; `class="hot"` (highlighted) / `class="pend"` (to come) restyle its rects and text |

Colour only through classes (no inline colours): fills `f-white` (`f-paper`, `f-sheet`) · `f-idle`
(light blue-gray) · `f-ink` · `f-accent` (gold, navy outline: **the one thing to look at**) · `f-tint`
(light gold) · `f-c2` (blue, second category) · `f-c3` (light blue, third) · `f-pencil` (gray) ·
`f-none`; strokes `s-ink` · `s-pencil` · `s-accent` (navy on shapes, gold on lines) · `s-c2` · `s-c3`;
modifiers `thick`, `dashed`, `off` (hidden in this frame). Text: `t-label` (15 px), `t-mono` (13 px; 15 px
in storyboards), `t-head` and `t-accent` (bold navy), `t-onbar` (white, **only on dark fills** `f-c2`,
`f-ink`, `f-pencil`; the deck turns it navy elsewhere). The aliases `f-teal`/`s-teal` = c2 and
`f-mustard`/`s-mustard` = c3 are accepted. `<svg data-text-scale="0.9">` scales every label of a dense
figure.

Drawing rules (each saves a re-layout later):
- **Tight viewBox, area proportions.** Give the viewBox just a small margin around the drawing, and draw
  in the area's proportions: about 2.65 : 1 for a content figure (8.5 × 3.2 in), 1.4 : 1 for a storyboard
  frame (6.05 × 4.4 in). A 5 : 1 strip leaves half the area empty, and the lint stops it (below 50 % of
  the area; `data-whitespace="reason"` on the slide keeps it, with a warning).
- **Labels clear of lines.** Put a curve's label beside the curve's end or between gridlines, never on
  the curve or a gridline; end arrows short of the text they point at; keep a label inside its box. The
  deck's QA warns on every line through a text and FAILs on text over text.
- **Labels near 12–14 pt after scaling.** A 640-unit-wide figure in the 8.5 in area scales by ~0.0133 in
  per unit, so a 13 px label lands at ~12.4 pt. Labels below 12 pt are raised and may collide.
- **One highlight.** Gold marks the single thing the slide is about; categories use c2 / c3.
- **Legends inside the figure** ("gold = …, blue = …") rather than a caption under it.
- **No provenance in the figure** ("after Fig. 3", "schematic"): that goes to `.source`.
- Outside the vocabulary (paths, polygons, gradients, images) the translator stops; `--png-fallback`
  embeds such a figure as a picture as a last resort (no type-floor check, no theme colours, no Morph).

## Notes and provenance

- `.notes` (a `<details>` or any element with that class): the **speaker script**, in paragraphs. Write
  what the speaker says, in order, pointing at the screen ("on the left…", "the gold box…"), with every
  number's source said aloud where it matters ("Table IV"). 100–250 words for a content slide, 30–80 for
  a storyboard frame, 40–80 for a divider.
- `.source`: one line of provenance ("Redrawn from Fig. 6(a)", "Values from Table VII", "Schematic").
  It never appears on the slide; the deck appends it to the notes as "Figure: …" (or "Source: …").
- The author's own reasoning on a slide carries the deck's tag (for example "[our reading]") in the title
  or the bullet, and the notes say so in words (references/audit.md).

## proto.py API

```python
from proto import Deck, Frame, Table, svg, R, T, L, PL, C, E, G
R(x, y, w, h, cls="f-white s-ink", key=None)            # rect
T(x, y, text, cls="t-label", anchor="start", key=None, size=None)
L(x1, y1, x2, y2, cls="s-ink", key=None, arrow=False)   # arrow picks the marker colour from cls
PL(points, cls="s-ink f-none", key=None, arrow=False)
C(cx, cy, r, cls, key=None); E(cx, cy, rx, ry, cls, key=None)
G(body, dx=0, dy=0, cls="", key=None)                   # cls "hot" / "pend"
svg(viewBox, body, title="", desc="", text_scale=None)

d = Deck(title, subject="", author="")       # part 1 "Summary" is built in
d.part(id, label=None, sub="")                # d.part("Summary", label, sub) re-labels part 1
d.title_slide(title, subtitle="", byline=(), notes="", presenter=…, date=…)   # no points: they go in d.summary
d.outline(notes="")                           # Summary highlighted: also the Summary divider
d.summary(message, **content_kwargs)          # right after the outline; title "Summary: <message>"
d.divider(part_id, notes="")                  # every later part (a "Summary" divider is dropped)
d.content(title, part=None, figure=None | table=Table(...) | stats=[(metric, label, hot)] | cards=[(head, text)],
          bullets=(), notes="", source="", see=None, role=None, whitespace=None)   # figure + stats = figure-stats
d.story(title, frames=[Frame(step, svg, caption, notes)], part=None, notes="", source="", see=None, role=None,
        whitespace=None)       # whitespace: the reason a figure keeps proportions that leave half its area empty
d.closing(title="Questions", recap="", citation="", questions=(), notes="")
d.appendix(aid, title, frames=None, **content_or_story_kwargs)
Table(head, rows, colw=None, font=13, ours=(), dense=False, bold_first=True)
d.write(path)        # warns about a missing outline / divider / summary / closing; appendix slides go last
```
`python3 proto.py content.json out.html` takes the same fields as JSON (see the script's docstring).

## What the lint checks (`html_to_spec.py --check`)

ERROR (no spec is written): no `Summary` part first in the parts list; no summary slide right after the
outline; a summary slide whose title does not start with "Summary"; a divider for the Summary part; a numbered or
bullet point list on the title slide (`ol`, `ul`, `li` or a line written "1." / "•"); a slide without notes; provenance words on a slide (`Source:`, `Redrawn`,
`Adapted from`, `schematic`, …); an appendix slide before the closing slide or a main slide after it; a
`data-see` to a missing appendix id; a figure outside the vocabulary (without `--png-fallback`); storyboard
frames with different numbers of unkeyed elements; a table below 12 pt; no title or no closing slide; a
figure filling < 50 % of its area (with the proportions to redraw at) unless the slide has `data-whitespace`.
WARN: a title over one 20 pt line; a band over 4 lines or with more than 3 bullets; a step caption over
10 lines or a step title over 2; a loose viewBox (with the tight one to use); a figure filling < 75 % of
its area; labels that scale below 12 pt; a table taller than the area, or one that fills < 75 % of it
even at its grown size; results without a methodology
slide; notes outside 40–300 words; an appendix slide nobody points to; a part without slides; a Summary
part of more than one slide.

## What the preview does

The template's script numbers slides as the deck will (a storyboard of n frames spans n slides), draws
the outline (Summary highlighted), dividers and appendix index from the parts list, flags a deck without
a Summary part first, a summary slide not right after the outline or not titled "Summary…", plays storyboards (←, Play, →; click a
frame), flags in red a title wider than its line, a band or caption taller than its box, and an area that
overflows, lists the slides in a side index, and moves between slides with the arrow keys. Fonts in the
preview are the browser's Arial / Helvetica, so a line that barely fits may wrap differently in
PowerPoint; the deck's own fit check (`deck_qa.py`) is the authority.
