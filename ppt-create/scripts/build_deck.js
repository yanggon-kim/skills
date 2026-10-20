#!/usr/bin/env node
/* Mode 2, step 2: a deck spec (html_to_spec.py output) -> the .pptx on the brand template.

   Run:   node build_deck.js SPEC.json OUT.pptx [--work DIR] [--brand DIR]
          DIR: the work folder made by setup.sh ($DECK_WORK, else ./.deck_work); the raw deck and the sidecar
          JSON (OUT-name.raw.pptx, OUT-name.meta.json) land there; deck_qa.py reads the sidecar.
          Label crossings are fixed during this build, before QA: deck_lib.js runs every figure (and every
          storyboard, over all its frames) through crossings.js and logs each change to OUT-name.crossings.json.
   Then:  DIR/venv/bin/python deck_qa.py OUT.pptx DIR/<name>.meta.json

   A part marked "preliminary" in the spec (the presenter's primer, part 2) becomes a preliminary section: deck_lib.js
   tags each of its slides. Every slide type comes from deck_lib.js, so a spec deck and a hand-written builder share one geometry,
   one palette and one set of type floors. Slide kinds: title, outline (which opens the Summary part), divider, content (area: figure,
   figure-stats, table, stats, cards), story (one Morph-linked slide per frame), closing, appendix-index, and
   appendix slides (content or story with an "appendix" id: titled "A1 · ...", after the closing slide). */
"use strict";
const fs = require("fs");
const path = require("path");
const lib = require(path.join(__dirname, "deck_lib.js"));

const args = process.argv.slice(2);
function opt(name) {
  const i = args.indexOf(name);
  return i >= 0 ? args.splice(i, 2)[1] : undefined;
}
const work = opt("--work");
const brand = opt("--brand");
if (args.length < 2) {
  console.error("usage: node build_deck.js SPEC.json OUT.pptx [--work DIR] [--brand DIR]");
  process.exit(2);
}
const spec = JSON.parse(fs.readFileSync(args[0], "utf8"));
const OUT = path.resolve(args[1]);

const d = lib.createDeck({ work, brand, ...spec.meta, ...(spec.options || {}) });
const { M, AREA } = lib;
const PARTS = spec.parts.map((p) => [p.label, p.sub]);
// the Preliminary Note (the presenter's primer, not the paper): its section tags every slide in it
const PRELIM = new Set(spec.parts.filter((p) => p.preliminary).map((p) => p.id));
let current = null;
function section(name) {
  if (name !== current) {
    d.section(name, { preliminary: PRELIM.has(name) });
    current = name;
  }
  return name;
}
const titleOf = (s) => (s.appendix ? `${s.appendix} · ${s.title}` : s.title);

function content(S, s) {
  const a = s.area || {};
  const o = { title: titleOf(s), body: s.bullets || [], notes: s.notes, caption: s.source || "", see: s.see, appendix: !!s.appendix };
  switch (a.type) {
    case "figure":
      return d.figSlide(S, { ...o, fig: a.fig, id: a.id });
    case "figure-stats": // figure on the left, up to four headline numbers stacked on the right
      return d.contentSlide(S, { ...o, captionLabel: "Figure" }, (sl) => {
        d.drawFig(sl, a.fig, { x: M, y: AREA.y, w: 6.85 - 0.15 - M, h: AREA.h }, { id: a.id, center: true, middle: true });
        d.statColumn(sl, a.items);
      });
    case "table":
      return d.contentSlide(S, o, (sl) => d.table(sl, a.head, a.rows, { colW: a.colW, boldFirst: a.boldFirst, name: a.name, fontSize: a.fontSize, dense: a.dense, rowH: a.rowH }));
    case "stats":
      return d.contentSlide(S, o, (sl) => d.statRow(sl, a.items));
    case "cards":
      return d.contentSlide(S, o, (sl) => d.cards(sl, a.items));
    default:
      throw new Error(`content slide "${s.title}" has no area`);
  }
}

for (const s of spec.slides) {
  const S = section(s.section);
  switch (s.kind) {
    case "title":
      d.titleSlide(S, s); // title, subtitle, byline, presenter, date: never a point list
      break;
    case "outline": // also the Summary part's divider: Summary (part 1) highlighted
      d.outlineSlide(S, PARTS, s.partIndex ?? 0, s.notes, { kind: "outline" });
      break;
    case "divider":
      d.outlineSlide(S, PARTS, s.partIndex, s.notes);
      break;
    case "appendix-index":
      d.outlineSlide(S, s.items, -1, s.notes, { title: "Appendix", kicker: "Backup details", kind: "appendix-index", appendix: true, labPt: 16, subPt: lib.LABEL_PT });
      break;
    case "content":
      content(S, s);
      break;
    case "story":
      d.storySlides(S, { story: { frames: s.frames }, id: s.id, title: titleOf(s), notes: s.notes, caption: s.source || "", appendix: !!s.appendix });
      break;
    case "closing":
      d.closingSlide(S, { ...s, recap: s.recap ? d.nb(s.recap) : "" });
      break;
    default:
      throw new Error(`unknown slide kind ${s.kind}`);
  }
}

d.write(OUT).catch((e) => {
  console.error(e);
  process.exit(1);
});
