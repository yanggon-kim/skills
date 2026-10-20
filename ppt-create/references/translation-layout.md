# Translation and layout geometry

## Contents
- The pipeline
- Geometry (inches on 10 × 5.625)
- Type floors and sizes
- How a figure is placed
- Tables, numbers, cards
- Re-layout procedure
- QA checks and their fixes
- Writing a builder by hand
- pptxgenjs and python-pptx gotchas

## The pipeline

```
talk.html ──html_to_spec.py──> talk.spec.json ──build_deck.js (deck_lib.js)──> WORK/talk.raw.pptx + WORK/talk.meta.json
          (lint, SVG -> shapes,                   (one geometry, palette,                │
           outline/dividers/appendix index)        type floors; Morph flags)             └─transplant.py──> talk.pptx
talk.pptx ──deck_qa.py (+ meta)──> PASS/FAIL     ──validate_deck.py──> schema check     ──render.py──> PDF + JPGs
```
- **Why two decks.** pptxgenjs writes clean slides but cannot open a template; python-pptx opens the
  template but is clumsy for drawing. So pptxgenjs writes a raw deck at the template's size using only
  theme colours and theme fonts, and `transplant.py` re-creates every slide on the template's layouts,
  copying the shapes and re-pointing placeholders so their geometry and text style come from the layout.
- **The sidecar** (`WORK/<name>.meta.json`) carries per slide: raw layout, kind, section, Morph flag,
  appendix flag, slide-number flag, notes word count; the shared geometry; QA settings (table floors,
  restricted phrases, extra tag patterns, footer words). `deck_qa.py` needs it for the geometry, Morph,
  structure and table-floor checks.

## Geometry (inches on 10 × 5.625)

| element | x | y | w | h | why |
|---|---|---|---|---|---|
| margins | 0.70 | | 8.50 (to 9.20) | | the template's own title and header-rule extent |
| title box | 0.70 | 0.22 | 8.50 | 0.36 | one 20 pt line, anchored at its bottom: ends at y 0.58, as high as the template allows |
| header rule | 0.70 | 0.64 | 8.50 | 0.04 | the template's rule, moved up with the title |
| content area | 0.70 | 0.80 | 8.50 | 3.20 | figure / table / numbers / cards (to y 4.00) |
| hairline | 0.70 | 4.07 | 8.50 | 0.01 | separates picture from words |
| band | 0.70 | 4.14 | 8.50 | 1.06 | 2–3 bullets, 16 pt, at most 4 lines (to y 5.20); the same on every content slide |
| frame figure | 0.70 | 0.80 | 6.05 | 4.40 | storyboard frames: figure to y 5.20 |
| step column | 6.95 | | 2.25 | | dots y 0.84 (0.20 in, every 0.28 in), step label y 1.14 h 0.72 ("Step i of n" 12 pt + step title 16 pt bold navy), caption y 1.92 h 3.28 at 16 pt |
| footer | logo (0.375, 5.30, 0.463 × 0.149); slide number (9.50, 5.31, 0.50 × 0.14) | | | | only these two; no footer text |
| outline / divider | title (0.70, 2.05, 2.85 × 0.61) 36 pt; rule and kicker in that 2.85 in column; parts listed from x 3.80, rows 0.87 in | | | | the template's Section Divider, with a title placeholder instead of its fixed text |
| closing | title on the brand rule; recap (0.70, 2.85, 4.9 × 1.45) 16 pt; citation y 4.40 12 pt; questions from x 5.85 | | | | the template's Thank You layout, with a title placeholder |

The numbers live in `deck_lib.js` (constants and `GEOM`) and reach `transplant.py` and `deck_qa.py`
through the sidecar; change them there only, and re-run QA, which checks every layout against them.

## Type floors and sizes

| text | size | floor | note |
|---|---|---|---|
| titles | 20 pt bold Helvetica | one line | shorten, never shrink |
| band bullets, step captions, card text | 16 pt | 16 | the template's bullet and spacing (3 pt before) |
| figure labels | scaled with the figure | 12 | raised to 12 when the scale puts them lower; the text box grows with the font |
| stat labels, byline, citation, "Step i of n" | 12 pt | 12 | |
| tables | 13–14 pt | 13 | a dense setup table 12 |
| cards head | 17 pt bold navy | | |
| big numbers | 54 pt (row) / 20 pt (column beside a figure) | | |

Why floors and not "fit to box": shrinking type to make content fit is the most common way a deck
becomes unreadable from the back of a room; a floor turns "too much on the slide" into a visible
failure, which is then fixed by cutting words or splitting the slide.

## How a figure is placed

1. `svg_shapes.py` parses the SVG into records in SVG units and computes **bb**, the content bounds plus
   a 6-unit pad, clipped to the viewBox (text extents estimated at 0.56 em per character). A storyboard
   gets one bb over all its frames.
2. `drawFig()` scales bb to fit the box (`s = min(box.w / bb.w, box.h / bb.h)` inches per unit) and
   centres it. Rects, ovals and lines become native shapes (stroke width scales, 0.5 pt minimum). Text
   becomes a text box at `size × s × 72` pt, raised to 12 pt if lower; the box is sized for the raised
   font (0.58 em per character + 0.6 em), so raised labels widen and may collide.
3. Colours map by slot: white → lt1, idle → accent3, ink/black → dk1, accent → gold accent5 with a navy
   outline, tint → gold at 60 % transparency with a navy outline, c2 → accent1, c3 → accent4, pencil →
   accent2; navy text for highlights and bold headings; white text on a light fill turns navy.
4. **A figure whose proportions differ from its area is not stretched or re-flowed: the lint stops it.**
   The scale is uniform, so a figure wider than the area's 2.66 : 1 (frames 1.375 : 1) meets the width
   and leaves bands above and below, and a taller one leaves bands left and right. Stretching would
   distort text, circles and arrowheads; re-flowing automatically (wrapping a row, moving a legend)
   changes what the figure says and where Morph finds its elements. So `html_to_spec.py` measures the
   share of the area the scaled figure covers and names the proportions to redraw at: below 75 % it
   warns, below 50 % it stops with an ERROR, unless the slide gives a reason (`data-whitespace="..."`,
   `whitespace=` in proto.py), which turns the stop into a warning. The fix is in the drawing: wrap a long
   row into two, stack panels, put side labels above or below, enlarge the elements.

## Tables, numbers, cards

- Tables are full width at the top of the area, header row accent1 with white bold text, borders accent4,
  rows highlighted with accent3 (`ours`), first column bold. Column widths are relative (`data-colw`).
  The QA estimate of a table's height (greedy wrap per cell) runs ~0.1 in high: a table "ending below
  the area" by less than that is usually fine in the render.
- **A table grows to fill the area** (`html_to_spec.py`, `fit_table()`): first its type, from the author's
  size up to 18 pt, as long as it fits 3.15 in and no header cell or row label (first column) wraps onto
  more lines than at the author's size; then its rows, each by at most one line of that size, with the
  text centred in the row (`rowH` in the spec; `d.table(..., {rowH})` in a hand-written builder). A table
  that still leaves more than 25 % of the area empty gets a lint warning and a QA warning: it is too
  short for a slide of its own, and a figure or headline numbers may say it better. Give the row-label
  column room for its longest label (`data-colw`), or the labels stop the type from growing.
- Stats: a row of 2–4 (54 pt numbers, 16 pt labels) or a column of up to 4 beside a figure (20 / 12 pt).
- Cards: up to three, each a number badge, a 17 pt head and 16 pt text; use them for open questions or
  three parallel points, not for prose.

## Re-layout procedure (after the first render)

Look at every slide and fix in the prototype, in this order:
1. **Overflow** (QA fit failures, red flags in the preview): shorten words first; split the slide if the
   message needs the words; move detail to the appendix.
2. **Collisions** (labels raised to 12 pt running into each other or into shapes): shorten the label;
   replace a column of repeated row labels with one legend line; give the element more room; scale a
   dense figure's text with `data-text-scale` only as far as it stays ≥ 12 pt after scaling.
3. **White space** (a figure that fills little of its area; QA `whitespace`): change the figure's
   proportions (stack panels vertically or side by side to match ~2.65 : 1), enlarge elements, bring
   legends inside.
4. **Labels clear of lines** (QA `lines`, `edges`): a label sits beside a curve, between gridlines or past
   their end, never on them; an arrow ends short of the text it points at; a label fits inside its box.
5. **Highlight**: exactly one gold element per slide or frame, on the thing the title talks about.
6. Rebuild, re-run QA and re-render; repeat until both are clean.

## QA checks and their fixes

| check | what fails | fix (in the prototype) |
|---|---|---|
| footer | footer text on a master or layout; logo or number off the geometry | template or transplant problem: see theme.md |
| geometry | a layout placeholder off the shared geometry | edit `deck_lib.js` constants only, never the template by hand |
| floors | a run below its floor | shorten / split; never lower the size |
| tags | provenance words on a slide; a restricted phrase outside its figures | move to `.source`; keep restricted phrases in the named figures |
| morph | Morph count ≠ follow-on frames; `!!u<n>` sets differ between frames | key every changing element; equal unkeyed elements per frame |
| notes | a slide without notes | write the script |
| structure | title not first, outline not second, a part without a divider, closing count ≠ 1, appendix misplaced | reorder the prototype |
| fit | a title over one line, a text box too small for its text, a table below the area | shorten, split, or move to the appendix |
| overlap | two texts overlap (each text's ink: measured width placed by its alignment, lines placed by the anchor, trimmed to the glyphs, so empty box padding never counts) | move or shorten one label; a label raised to 12 pt needs more room |
| lines (WARN) | a line or connector passes through a text's ink: gridlines, arrows, curves over labels | put the label beside the curve, between gridlines or past their end; end the arrow short of the text |
| edges (WARN) | a text mostly inside a drawn shape runs out over its edge | shorten the label or widen the box |
| whitespace (WARN) | the share of the area farther than 0.25 in from every element (shape, text ink, line) is above 25 % on a table slide or 42 % on a figure slide or storyboard frame | the figure's proportions, the table's rows (re-layout step 3) |

WARN does not change the exit status; look at each in the render and fix it or accept it. The
whitespace thresholds are calibrated on the approved reference deck (`assets/reference/`): its frames
reach 40 %, its figure slides 39.5 % except slide 35 (49.5 %, a tall dot plot), its tables 3 %; that
slide and 33 gridline crossings (timing grids s11–16, charts s28, s35, s36, s49–51) are its warnings.

## Writing a builder by hand

A deck whose content does not come from the prototype format (an older page, a generated report) can call
the library directly, as `examples/p3llm/build_p3llm_deck.js` does:
```js
const lib = require(`${SKILL}/scripts/deck_lib.js`);
const d = lib.createDeck({ work, title, subject, author, colorWords, nbRules, qa });
d.section("Opening"); d.titleSlide("Opening", {...}); d.outlineSlide("Opening", PARTS, -1, notes);
d.figSlide(S, { fig, id, title, body, notes, caption, see });
d.storySlides(S, { story: { frames }, id, title, titles, captions, notes: [...], caption });
d.contentSlide(S, { title, body, notes }, (sl) => d.table(sl, head, rows, { colW, fontSize }));
d.closingSlide(S, {...}); await d.write("out.pptx");
```
Primitives for custom slides: `newSlide(layout, section, kind)`, `drawFig`, `band`, `notes`, `stat`,
`statRow`, `statColumn`, `cards`, `table`, `nb` (keeps "§V-D", "28 nm", "Fig. 9" unbroken), `gold()`,
and the scheme colours `C`, `NAVY`, `GOLD`. `colorWords` re-words colour names in notes and figure text
when the source drew in other colours; `qa.restricted` allows a phrase only inside named figures.

## pptxgenjs and python-pptx gotchas

- pptxgenjs `bold: false` writes no `b="0"`, so a run in a bold placeholder stays bold; the transplant
  sets `b="0"` on the title slide's subtitle explicitly.
- Placeholder `name` options are ignored (shapes come out as "Text N"); the transplant renames the band
  and the step caption so QA can find them.
- pptxgenjs converts option objects to EMU **in place**: build fresh option objects per layout and slide.
- Morph is not a pptxgenjs option: the transplant inserts an `mc:AlternateContent` transition after
  `p:clrMapOvr` (don't redeclare namespaces when parsing that fragment).
- pptxgenjs writes per-run size and colour on placeholder text; the transplant strips them where the
  layout should rule (titles, band, captions, recap).
- Pictures: the transplant carries each `a:blip` image part to the new slide (a copied picture without
  its relationship renders empty).
- An `&` in a slide-master title or `pres.company` is written unescaped by pptxgenjs; avoid it there.
