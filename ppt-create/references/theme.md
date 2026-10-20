# The theme: UCLA brand template and the transplant

## Contents
- What the deck looks like
- Colours by role
- Fonts
- The transplant, step by step
- Template parts the scripts rely on
- Template traps
- Using another template
- Fonts for QA renders

## What the deck looks like

10 × 5.625 in (16 : 9), white background, the UCLA wordmark top left on the title slide and as a small
logo bottom left elsewhere, a blue header rule under every title, the slide number bottom right, no
footer text. Titles in gray Helvetica bold; body text in gray Arial; navy for emphasis; one gold
highlight per slide. Files: `assets/ucla/Presentation-01-master.pptx` (the template package),
`brand-01-colors.xml` (light colour scheme), `brand-03-colors.xml` (the dark master's scheme),
`brand-fonts.xml` (Helvetica headings, Arial body).

## Colours by role (Brand-01)

| role | scheme slot | hex | used for |
|---|---|---|---|
| text | dk1 | 57585B | body text, figure ink, table text |
| headings, emphasis | accent6 | 00375B | navy: bold figure headings, highlight outlines and text, step titles, card heads |
| the highlight | accent5 | FFC72B | gold fill **with a navy outline**; light highlight = gold at 60 % transparency; highlight lines |
| category 2 | accent1 | 2774AE | blue: second series, header rule, table header |
| category 3 | accent4 | 8AB8E8 | light blue: third series, hairline, table borders |
| idle | accent3 | DAE6F4 | idle fills, highlighted ("ours") table rows, outline highlight card |
| secondary | accent2 | 898989 | gray: secondary strokes, "Step i of n", past step dots |
| background | lt1 | FFFFFF | |

Rules, and why: **one gold element per slide** (the eye goes to it first, so it must be the thing the
title is about); **never gold text on white** (contrast too low; highlight text is navy); categories in
blue tones so the gold stays unique; everything is a scheme colour, never hex (except table borders,
which pptxgenjs accepts only as hex), so a theme change re-colours the whole deck. Brand-03 is applied to
the template's dark master only (its "Statement w/dark background" layouts); the deck itself uses the
light master.

## Fonts

Headings Helvetica (major font), body Arial (minor font), both from `brand-fonts.xml`. The raw deck sets
the same pair, but the transplanted deck's text inherits the template theme, so no run names a font
except a few headline numbers (`+mj-lt`, the heading font). The template's notes master used
Office / Calibri; the transplant gives it the brand theme too, so no Calibri remains anywhere.

## The transplant, step by step (`scripts/transplant.py`)

1. **Brand the template package.** theme1 ← Brand-01 colours + brand fonts; theme2 (dark master) ←
   Brand-03 + fonts; theme3 (notes master) ← Brand-01 + fonts. `docProps/app.xml` is reset (the
   template lists its own fonts and sample-slide titles there). Both masters lose their footer text boxes
   ("Text Placeholder-left", "Text Placeholder-middle"); master 1's title placeholder, header rule, logo
   and slide number move to the shared geometry (title higher, footer lower).
2. **Derive four layouts inside master 1** (zip-level: layout part + rels + content-type override +
   `sldLayoutIdLst` entry): *Header w/figure and bullets* (from Header w/copy: title, band placeholder
   idx 13, hairline), *Header w/storyboard* (from Header w/copy: title, step-caption placeholder idx 13),
   *Section Divider w/outline* (from Section Divider: a real title placeholder replaces the fixed
   "Section Divider" text; rule and kicker narrowed to the left column), *Thank You w/title* (from Thank
   You: a title placeholder replaces the fixed "Thank You" text, plus a body placeholder idx 20).
3. **Drop the template's sample slides** (remove the relationship and the `sldId`; unreachable parts
   vanish on save).
4. **Re-create every raw slide** on its layout (TITLE → Title Opener, DIVIDER → Section Divider
   w/outline, CONTENT → Header w/figure and bullets, FRAME → Header w/storyboard, CLOSING → Thank You
   w/title): deep-copy the raw shapes, re-point each placeholder at the layout's (type and idx), empty its
   `spPr` so the geometry is inherited, strip per-run size / bold / colour where the layout should rule,
   copy picture parts, add the slide number, the speaker notes, and the Morph transition on storyboard
   follow-on frames; text boxes named `ph:body:23` / `ph:body:22` become the title slide's presenter and
   date placeholders; the UCLA wordmark fills the title slide's picture placeholder.
5. **Sections** from the sidecar (one per part, "Opening", "Appendix"); core properties from the deck
   meta.

## Template parts the scripts rely on

| part | used as |
|---|---|
| `slideLayout1.xml` Title Opener | title slide; placeholders idx 31 (title text), 24 (logo picture), 23 (presenter), 22 (date) |
| `slideLayout2.xml` Section Divider | base of *Section Divider w/outline* (idx 20 = kicker) |
| `slideLayout3.xml` Header w/copy | base of the content and storyboard layouts (idx 13 = band / caption) |
| `slideLayout16.xml` Thank You | base of *Thank You w/title* |
| master 1 shapes | "Title Placeholder", "Header rule", "Brand logo", "Slide Number Placeholder" (idx 19), footer boxes "Text Placeholder-left" / "-middle" |
| `ppt/media/image1.png` | the UCLA wordmark for the title slide |

## Template traps

- The Section Divider and Thank You layouts carry **fixed text boxes** ("Section Divider", "Thank You"):
  a real title needs a derived layout with a title placeholder, or the fixed text shows through.
- Several layouts hold **hidden designer tables and shapes**; derived layouts drop hidden elements.
- The **notes master theme** is Office / Calibri and `docProps/app.xml` lists Calibri and sample
  titles: re-brand and reset both, or a "no Calibri" check fails and the file lists phantom slides.
- The master **footer text** says "(edit in Slide Master)"; it is removed, and QA fails if it returns.

## Using another template

The transplant is written for this package's file numbers, placeholder idx values and shape names (the
table above). For another template: open it with `markitdown` or a layout thumbnail grid, find its
title / section / content / closing layouts and their placeholder idx values and master shape names,
change `layouts_xml()`, `restyle_master()`, `LAYOUT`, `PHMAP` and `FOOTER_TEXT` in `transplant.py`, put
its theme files next to it, and pass `--brand DIR` (build_deck.js `--brand`). Keep the geometry in
`deck_lib.js` inside the new template's margins, then let `deck_qa.py` confirm footer and geometry.

## Fonts for QA renders

The server rarely has Helvetica or Arial. `render.py` writes a scratch fontconfig file that maps
Helvetica / Arial → Liberation Sans (same metrics), Calibri → Carlito, Cambria → Caladea, so line breaks
in the render match PowerPoint's closely; `deck_qa.py` measures text with Liberation Sans for the same
reason. The rendered glyphs look slightly different from Helvetica; the widths are what matter.
