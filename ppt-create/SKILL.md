---
name: ppt-create
description: Builds a talk as an HTML prototype first — one core message per slide, figures as inline SVG, storyboard animations, short bullets, the full speaker script in the notes, details in an appendix — and then translates that prototype into a .pptx on the UCLA brand template (10 × 5.625 in, Morph-linked storyboard frames, fixed bullet band, type floors, structural QA, renders and a line-by-line fact audit). Use it whenever the user wants a slide deck, a presentation, a talk, a lab-meeting or paper-discussion deck, a pptx or PowerPoint "about X" or "from this paper / these notes / this outline", wants an HTML prototype or storyboard of a talk, or says "turn this HTML into pptx" / "make the deck from the prototype" — even if they only say "slides". Prefer it over building a deck by hand; not for editing an existing .pptx someone else made, and not for one-off charts.
---

# ppt-create: HTML prototype first, then the deck

A deck made here is never hand-built. It is **translated** from an HTML prototype the user has seen and
approved, by scripts that place every slide on one geometry, one palette and one set of type floors. The
prototype carries everything the deck needs (titles, figures, storyboards, bullets, speaker notes,
provenance, appendix), so changing a slide means changing the prototype and re-running the translation.

**Why HTML first.** A page is fast to review and fix: the author and the user read the whole argument,
the figures and the script in one scroll, before any layout work. Hand-built decks drift (fonts, positions,
colours differ slide to slide) and their content is hard to check; a translated deck inherits one layout
from code, and re-building it after a content fix costs seconds.

Two modes, usually run in sequence:

| mode | the user says | you produce |
|---|---|---|
| **1. Prototype** | "make a deck / talk / presentation about X", "HTML prototype for a talk", gives a paper, notes or an outline | `talk.html`: the prototype (a 16:9 preview canvas per slide, notes under each) |
| **2. Translate** | "turn this HTML into pptx", "make the deck", or approves the prototype | `talk.pptx` on the brand template, QA log, renders, `talk-audit.md` |

When the user asks for "a pptx about X" in one go, run Mode 1, show the prototype (path, or publish it as
an artifact if the session can), then run Mode 2 without waiting unless they asked to review first.

## Setup (once per work folder)

```bash
SK=~/.claude/skills/ppt-create
bash $SK/scripts/setup.sh WORK            # pptxgenjs 3.12.0 in WORK/node_modules, a venv in WORK/venv
PY=WORK/venv/bin/python
```
WORK is any folder outside the skill (default `./.deck_work`); raw decks, sidecars and caches land there.
Rendering needs LibreOffice and `pdftoppm`; the fit check needs Liberation Sans. The pptx skill, when
installed, is used for its `validate.py` and `soffice.py`; without it the scripts fall back (minimal
package check; plain `soffice`).

## Mode 1: build the HTML prototype

1. **Read the source** in full (paper, notes, data). List the claims you will make and where each comes
   from (section, figure, table, page). Numbers are quoted, never invented; your own inferences are kept
   apart (rule 10).
2. **Plan the talk** as parts (sections of the outline), then slides. **Part 1 is always "Summary"**:
   one slide right after the outline, titled "Summary: <core message of the talk>", with the talk's key
   picture or numbers (rule 2). Each slide states **one core
   message**, and its title *is* that message in a few words ("The cache halves median latency only
   above 64 users", not "Results"). Decide for every slide what the audience must see (the figure or table) and what it
   must hear (the notes). Push every detail that is not needed to follow the argument to the appendix.
3. **Write the prototype** with `scripts/proto.py` (Python API, recommended: its SVG helpers keep figures
   inside the vocabulary) or by hand from `assets/prototype-template.html`. The format, every slide kind and
   the figure vocabulary are in **references/html-prototype.md** — read it before writing.
   ```python
   import sys; sys.path.insert(0, f"{SK}/scripts")
   from proto import Deck, Frame, Table, svg, R, T, L, PL, C, E, G
   d = Deck("Title", subject="...", author="...")        # part 1, "Summary", is built in
   d.part("Background", "Background: the problem", "what the audience needs first")
   d.title_slide(title=..., subtitle=..., byline=[...], notes=...)   # no key points: those go on the summary
   d.outline(notes=...)                                     # the outline, Summary highlighted
   d.summary("the talk's core message", figure=svg(...), bullets=[...], notes=...)  # -> "Summary: ..."
   d.divider("Background", notes=...)
   d.content("One-line message", part="Background", figure=svg("0 0 600 260", ...), bullets=[...], notes=..., source=...)
   d.story("One-line message", part="Background", frames=[Frame("step", svg(...), "caption", "script"), ...])
   d.closing(...); d.appendix("A1", "Full table", table=Table(...), bullets=[...], notes=...)
   d.write("talk.html")
   ```
4. **Lint it**: `$PY $SK/scripts/html_to_spec.py talk.html --check`. Fix every ERROR; read every WARN
   (no Summary part first, no summary slide right after the outline, a summary title that does not
   start with "Summary", or a point list on the title slide are ERRORs; title over one line, band over 4 lines, loose viewBox, figure that
   leaves white space, labels the deck must raise to 12 pt, results without methodology, notes length). A figure that would fill less
   than half its area is an ERROR naming the proportions to redraw at.
5. **Look at it** in a browser (or a headless screenshot). The canvas flags a title wider than its line or
   a band taller than its box in red; storyboards play with ←/→ and Play. Then hand it to the user.

## Mode 2: translate the prototype into the deck

```bash
$PY $SK/scripts/html_to_spec.py talk.html talk.spec.json --work WORK     # lint + spec (exit 1 on ERROR)
node $SK/scripts/build_deck.js talk.spec.json talk.pptx --work WORK       # raw deck -> transplant onto the template
$PY $SK/scripts/deck_qa.py talk.pptx WORK/talk.meta.json                  # footer … fit, overlap; WARN lines, edges, whitespace
$PY $SK/scripts/validate_deck.py talk.pptx                                # package / schema validation
python3 $SK/scripts/render.py talk.pptx --out render                      # PDF + one JPG per slide
$PY $SK/scripts/audit_skeleton.py talk.pptx talk-audit.md --source "..."  # start the fact audit
```
1. Every QA check must PASS. A FAIL names the slide; fix it **in the prototype** (shorten, split, re-draw),
   never in the .pptx, and re-run. The fixes for each failure are in references/translation-layout.md.
   Clear every WARN too (a line through a label, a label over its box's edge, an area more than 25 %
   (table) or 42 % (figure, frame) empty), or accept it knowingly after looking at the render.
2. **Look at every rendered slide** (contact sheets of 4–6 slides are quick). Check what QA cannot: labels
   that collide after being raised to 12 pt, gridlines through labels, arrows over text, white space a
   figure leaves, a highlight on the wrong element. LibreOffice shows Morph as a fade; that is expected.
3. **Tighten and fact-check** (rule 11, references/audit.md): every slide and its notes against the
   source, item by item, in the audit file; fix every error in the prototype and rebuild.
4. Report: the .pptx path, slide count, QA result, the renders, the audit counts, and anything left
   open (for example a presenter name or date left blank on the title slide).

## The rules, and why

Each rule exists because a reviewer of an earlier deck asked for it; the reason decides edge cases.

1. **HTML first, deck translated.** (Above.) Never edit the .pptx by hand: the next build overwrites it,
   and a hand edit is invisible to QA and to the audit.
2. **Structure: title → outline (Summary highlighted) → summary slide → [divider → part]… → closing →
   appendix.** The outline after the title tells the audience the route; repeating it before each part
   with that part highlighted tells them where they are, which is what people lose first in a talk.
   **Every deck's first part is "Summary"**: the whole talk on one slide, titled "Summary: <core
   message>" (one 20 pt line: shorten the message, the full sentence goes to the notes), so a listener
   who keeps only one slide keeps the right one. **The title slide carries only the title, subtitle,
   authors / venue, presenter / date and the logo — never the summary points**: the key points live only
   on the Summary slide, so the opening is not duplicated two slides apart (the lint stops on a point list
   on the title slide; QA fails on list or badge shapes there). The outline slide doubles as the Summary divider (it
   lists every part with Summary highlighted, "Next: part 1 of N"), so the deck never shows two outline
   slides in a row; the later dividers read "part k of N". One or two **methodology / setup** slides come
   before any results (how numbers were produced decides whether they can be trusted); mark them
   `data-role="method"` and results `data-role="result"`. The closing slide recaps in one sentence and
   opens the discussion. The translator adds a missing outline or divider, with a warning; a missing summary slide stops it.
3. **Figure or table first.** On a normal slide the figure, table, numbers or cards fill the content area
   (8.5 × 3.2 in) — a table grows its type and rows to fill it, a figure is drawn in the area's
   proportions; the audience looks at the picture while the speaker talks. **Two or three supporting
   bullets** sit in one fixed band at the bottom (16 pt, at most 4 lines), identical in position on every
   slide, so the eye always knows where the words are. Everything else is said, not shown: **the full
   explanation goes in the speaker notes, written as a script** (what to say, in order, referring to what
   is on screen: "the gold box", "the blue curve"), typically 100–250 words per slide.
4. **Appendix for detail.** Main slides carry only the simple, clean facts needed for the argument.
   Detailed facts (full tables, extra numbers, derivations, per-case breakdowns, ablations) go on appendix
   slides **after the closing slide**, behind an "Appendix" index slide. A main slide points to its
   appendix slide (`data-see="A1"` adds "→ appendix A1" to its last bullet), so a question can be answered
   by jumping there. Why: a dense main slide loses the room; an absent detail loses the Q&A.
5. **Storyboards become Morph sequences.** A process that changes over time is drawn as frames on one
   fixed layout (references/animations.md). Each frame becomes its own slide; elements keep their names
   (`!!key`) across frames and every follow-on frame has a Morph transition (fade fallback), so PowerPoint
   tweens the change the way the prototype's player does, and a PDF or a viewer without Morph still shows
   every step. The step dots, step title and caption sit in a fixed right-hand column (2.25 in, 16 pt).
6. **Re-layout and size: minimise white space, never shrink type below the floors.** Draw each figure
   with a tight viewBox in the proportions of its area; the deck crops to content and scales the figure to
   fill the area. Floors: bullets and captions 16 pt, figure labels ≥ 12 pt, tables 13–14 pt, a dense
   setup table ≥ 12 pt, titles 20 pt. When something does not fit, **shorten the words** (the full text
   goes to the notes) **or split the slide** — never shrink the type: small type is what audiences
   complain about first, and it hides that a slide carries too much.
7. **Title at the very top, footer at the very bottom.** One title line at 20 pt (box y 0.22–0.58 in,
   anchored at its bottom), the header rule at y 0.64 in; the footer is only the logo and the page number
   (y ≈ 5.30 in), with no footer text. This gives the content area every inch the template allows.
8. **No stray source sentences on slides.** "Redrawn from…", "Adapted from…", "Source: …", "schematic"
   go in the speaker notes (the prototype's `.source` line is appended to the notes as "Figure: …").
   A short citation in a bullet, "(Fig. 9)", "(§III-B)", is fine; a sentence about provenance is not.
9. **UCLA theme by default.** 10 × 5.625 in; Brand-01 colours (Brand-03 on the dark master); Helvetica
   headings, Arial body; the one highlight is a **gold fill with a 00375B (navy) outline**, its text navy,
   never gold text on white. The deck is built by **transplanting** the raw slides onto the template
   package (its masters, layouts, logo and notes master), because pptxgenjs cannot open a template.
   Details and the template parts relied on: references/theme.md.
10. **Mark your own reasoning.** Facts taken from the source and the author's own inferences, opinions or
    depictions are kept visibly apart: a tag on the slide (one tag per deck, e.g. "[our reading]") and a
    sentence in the notes ("this is my reading, not the paper's claim"). Schematic drawings say so in the
    notes. Why: a talk about someone else's work must not put words in their mouth.
11. **Tighten and fact-check after the build.** Check every slide and its notes against the source
    material, claim by claim, in an audit file with one row per claim: slide, claim, source location,
    status (ok · fixed · author's reading · background). Fix every error found in the prototype, rebuild,
    and keep the audit next to the deck. Why: a deck is quoted from memory by its audience; an error on a
    slide outlives the talk. Procedure: references/audit.md.

## When QA or the render shows a problem

| symptom | fix in the prototype |
|---|---|
| title wraps (fit) | shorten the title to the core message; detail goes to the band or notes |
| band over 4 lines (fit) | shorten bullets, keep 2–3; the full sentences go to the notes |
| table ends below the area (fit) | shorter cells, fewer columns, or move rows to an appendix table |
| floors | a table at < 13 pt (12 if dense): split it; never lower the size |
| labels collide after the 12 pt raise (overlap) | shorten labels, replace repeated row labels with one legend line, draw the figure larger (fewer, bigger elements) |
| lines / edges (WARN) | move the label beside the curve, between gridlines or past their end; end arrows short of the text; shorten a label wider than its box |
| figure leaves white space (lint fill, QA whitespace) | change the figure's proportions to the area's (8.5 × 3.2 in; frames 6.05 × 4.4 in): wrap a long row, stack panels, enlarge |
| table leaves white space | the deck already grows it (type to 18 pt, taller rows); widen the row-label column, add the rows the talk needs, or use a figure or stats |
| tags | move the provenance sentence to `.source` |
| morph / unkeyed counts | give a `data-key` to every element that appears, disappears or changes; hide with class `off` |
| structure | title first (no point list or badges on it), outline second, the "Summary: …" slide third, a divider per later part, one closing slide, appendix only after it |
| summary lint (ERROR) | add `d.summary("core message", …)` right after the outline; title "Summary: …"; never a divider for the Summary part |
| title-slide list (lint ERROR, QA structure) | delete the points from the title slide; they belong on the summary slide, and the script that walked them goes to its notes |

## Files

```
SKILL.md                      this file
references/html-prototype.md  the prototype format: slide kinds, markup, figure vocabulary, proto.py API, lints
references/translation-layout.md  pipeline, geometry, type floors, figure scaling, tables, fixes, pptxgenjs gotchas
references/theme.md           UCLA template, colours by role, fonts, the transplant, porting to another template
references/animations.md      storyboards, data-key, Morph names and transitions, the step column
references/audit.md           the fact-check procedure, statuses, marking the author's reasoning
scripts/setup.sh              installs pptxgenjs 3.12.0 + a venv (python-pptx, lxml, Pillow, bs4) into WORK
scripts/proto.py              Mode 1: Deck API + SVG helpers -> the prototype HTML (also JSON -> HTML)
scripts/html_to_spec.py       Mode 2: prototype -> lint + deck spec JSON (--check: lint only)
scripts/svg_shapes.py         SVG figure -> native-shape records, content bounds, deck-only edits
scripts/deck_lib.js           the slide vocabulary (title, outline, figure, storyboard, table, stats, cards, closing)
scripts/build_deck.js         spec JSON -> raw deck + sidecar -> transplant.py -> .pptx
scripts/transplant.py         raw deck -> the brand template (layouts, theme, footer, Morph, sections)
scripts/deck_qa.py            structural and fit checks (PASS / FAIL per check)
scripts/validate_deck.py      package validation (pptx skill's validate.py, else a minimal check)
scripts/render.py             .pptx -> PDF -> JPG with metric-compatible fonts
scripts/audit_skeleton.py     one audit row per claim on every slide and in its notes
assets/prototype-template.html  CSS + JS of the prototype (preview canvas, player, fit flags, index)
assets/ucla/                  the brand template and theme files
assets/reference/             an approved deck (p3llm-intro.pptx) and its page (p3llm-intro.html)
examples/p3llm/               how that deck is built with deck_lib.js; its audit file
```

**Worked example.** `examples/p3llm/` rebuilds the approved reference deck in `assets/reference/` with the
same library; see its README. Read it for the tone of titles, bullets and notes, the storyboards, and the
shape of a finished audit.

## Gotchas worth knowing before the first build

- pptxgenjs is not assumed to be installed anywhere: `setup.sh` pins it in WORK. Run node scripts with
  `--work WORK` (or `DECK_WORK=WORK`) so they find it.
- Figures must stay inside the vocabulary (rect, circle, ellipse, line, polyline, text, g translate,
  colour classes). `--png-fallback` embeds a figure outside it as a picture, as a last resort: its text
  is not checked against the floors and does not re-colour with the theme.
- Raising small figure labels to 12 pt grows their boxes; dense figures then collide. Draw figures at a
  size where labels already land near 12–14 pt after scaling (html_to_spec warns with the number).
- The fit check measures with Liberation Sans (Arial's metrics) at 97 % of the box width; trust the
  render when a table fails by about 0.1 in (the table-height estimate runs high).
- A storyboard's frames share one crop (the union of their content), so Morph sees the same placement;
  a frame that adds far-away content shrinks every frame.
