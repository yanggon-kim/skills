/* deck_lib.js - the slide vocabulary of the ppt-create skill, on pptxgenjs 3.12.0.

   const { createDeck } = require("<skill>/scripts/deck_lib.js");
   const d = createDeck({ work, title, subject, author });
   d.titleSlide({...}); d.outlineSlide(parts, -1, notes); d.figSlide(section, {...}); ... await d.write(out);

   build_deck.js drives this library from a deck spec (html_to_spec.py output); a hand-written builder may
   call it directly (examples/p3llm/build_p3llm_deck.js). Either way the deck is written in two steps,
   because pptxgenjs cannot open a template: write() saves a raw deck (10 x 5.625 in, scheme colours and
   theme fonts only) plus a sidecar JSON (layout, kind, section, Morph flag per slide; the shared geometry;
   QA settings) in the work folder, then runs transplant.py, which re-creates every slide on the brand
   template's layouts. Geometry and type sizes live here and in the sidecar only; see
   references/translation-layout.md for the reasons behind each number.

   Colours are theme roles, never hex (except table borders, which pptxgenjs takes as hex only):
   text dk1; headings and emphasis accent6 (navy); the one highlight is a gold accent5 fill with an accent6
   outline (light highlight boxes: gold at 60 % transparency); highlight text is accent6, never gold text
   on white; category 2 accent1; category 3 accent4; idle fills and "ours" table rows accent3; secondary
   strokes accent2. */
"use strict";
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const SKILL = path.resolve(__dirname, "..");

// ------------------------------------------------------------------ geometry (inches on 10 x 5.625)
const K = 0.75; // sizes first drawn on a 13.33 x 7.5 in canvas, scaled (outline, title and closing slides)
const F = (v) => Math.round(v * K * 2) / 2;
const M = 0.70, R = 9.20, CW = R - M; // the template's margins: its title and header rule run x 0.70-9.20
const TITLE_PT = 20; // every title is one line at 20 pt
const TEXT_PT = 16; // bullets, step captions and card text
const LABEL_PT = 12; // the floor for figure labels, stat labels and other small slide text
const TBOX = { x: M, y: 0.22, w: CW, h: 0.36 }; // title box (anchored at its bottom: one line ends at y 0.58)
const HRULE = { x: M, y: 0.64, w: CW, h: 0.04 }; // the template's header rule, moved up
const AREA = { x: M, y: 0.80, w: CW, h: 3.20 }; // content slides: figure / table area (to 4.00)
const RULE = { x: M, y: 4.07, w: CW, h: 0.01 }; // hairline above the band
const BAND = { x: M, y: 4.14, w: CW, h: 1.06 }; // content slides: the bullet band, 4 lines at 16 pt (to 5.20)
const FAREA = { x: M, y: 0.80, w: 6.05, h: 4.40 }; // frame slides: figure area (to 5.20)
const FCOL = { x: 6.95, w: R - 6.95 }; // frame slides: right-hand column (2.25 in)
const FDOTS_Y = 0.84, FDOT = 0.2, FDOT_STEP = 0.28, FSTEP = { y: 1.14, h: 0.72 };
const FCAP = { x: FCOL.x, y: 1.92, w: FCOL.w, h: 3.28 }; // frame slides: step caption (to 5.20)
const FOOT = { logo: [0.375, 5.30, 0.463, 0.149], sldNum: [9.50, 5.31, 0.50, 0.14] }; // the template's footer, lowered
const MIN_PT = LABEL_PT; // smallest figure text after scaling
const GEOM = {
  titlePt: TITLE_PT, textPt: TEXT_PT, labelPt: LABEL_PT, title: [TBOX.x, TBOX.y, TBOX.w, TBOX.h],
  hrule: [HRULE.x, HRULE.y, HRULE.w, HRULE.h], area: [AREA.x, AREA.y, AREA.w, AREA.h],
  rule: [RULE.x, RULE.y, RULE.w, RULE.h], band: [BAND.x, BAND.y, BAND.w, BAND.h],
  farea: [FAREA.x, FAREA.y, FAREA.w, FAREA.h], stepcaption: [FCAP.x, FCAP.y, FCAP.w, FCAP.h], stepLabelY: FSTEP.y,
  footLogo: FOOT.logo, sldNum: FOOT.sldNum,
  dividerColW: 2.85, bandSpcBef: 3, closingBody: [M, 2.85, 4.9, 1.45], logo: [0.71, 0.52, 1.26, 0.41],
};
const NUMBERED = ["DIVIDER", "CONTENT", "FRAME"]; // raw layouts whose slides show a slide number

function loadPptxgen(work) {
  const nm = path.join(work, "node_modules");
  process.env.NODE_PATH = [nm, process.env.NODE_PATH].filter(Boolean).join(path.delimiter);
  require("module").Module._initPaths();
  try {
    return require("pptxgenjs");
  } catch (e) {
    throw new Error(`pptxgenjs is not installed in ${nm}: run  bash ${path.join(SKILL, "scripts", "setup.sh")} ${work}`);
  }
}

/* opts: work (folder made by setup.sh: node_modules, venv), title, subject, author, brand (template folder,
   default assets/ucla), colorWords ({word: replacement}, applied to notes and figure text, e.g. when the
   prototype's colour words differ from the theme's), nbRules ([[RegExp, replacement]] added to nb()),
   qa ({restricted: [{text, allowIn: [name prefixes]}], extraTags: [regex source], footerWords: [..]}). */
function createDeck(opts = {}) {
  const work = path.resolve(opts.work || process.env.DECK_WORK || ".deck_work");
  const brand = path.resolve(opts.brand || path.join(SKILL, "assets", "ucla"));
  const pptxgen = loadPptxgen(work);
  const pres = new pptxgen();
  pres.defineLayout({ name: "UCLA_16x9", width: 10, height: 5.625 }); // the template's slide size
  pres.layout = "UCLA_16x9";
  pres.theme = { headFontFace: "Helvetica", bodyFontFace: "Arial" }; // the raw deck only; the template's theme wins
  const META_DOC = { title: opts.title || "Presentation", subject: opts.subject || "", author: opts.author || "" };
  Object.assign(pres, META_DOC);
  const C = pres.SchemeColor;
  // palette slots of svg_shapes.py -> scheme colours (see the header comment)
  const COL = {
    ink: C.text1, inksoft: C.text1, black: C.text1, white: C.background1, c2: C.accent1, c3: C.accent4,
    pencil: C.accent2, idle: C.accent3, accent: C.accent5, accentink: C.accent6, tint: C.accent5,
  };
  const NAVY = C.accent6, GOLD = C.accent5;
  const HEX = { line: "8AB8E8" }; // table borders (a hex-only option): accent4 of Brand-01
  const LIGHT = ["accent", "tint", "c3", "idle", "white"]; // fills that take navy text instead of white
  const gold = (w = 0.75) => ({ fill: { color: GOLD }, line: { color: NAVY, width: w } });
  const QA = { tableFloors: {}, restricted: [], extraTags: [], footerWords: [META_DOC.title], ...(opts.qa || {}) };

  // ---------------------------------------------------------------- raw layouts
  // Only their placeholders matter: transplant.py re-points them at the template-derived layouts, which set the
  // geometry and text style. pptxgenjs converts option objects to EMU in place, so every layout gets fresh ones.
  const ph = (name, type, box, extra = {}) => ({ placeholder: { options: { name, type, ...box, margin: 0, valign: "top", ...extra }, text: "" } });
  pres.defineSlideMaster({ title: "TITLE", objects: [ph("title", "title", { x: M, y: 2.07, w: CW, h: 1.21 }, { valign: "middle" })] });
  pres.defineSlideMaster({ title: "DIVIDER", objects: [ph("title", "title", TBOX), ph("kicker", "body", { x: M, y: 2.9, w: 2.85, h: 0.3 }, { fontSize: 16 })] });
  pres.defineSlideMaster({ title: "CONTENT", objects: [ph("title", "title", TBOX), ph("band", "body", BAND)] });
  pres.defineSlideMaster({ title: "FRAME", objects: [ph("title", "title", TBOX), ph("stepcaption", "body", FCAP)] });
  pres.defineSlideMaster({ title: "CLOSING", objects: [ph("title", "title", TBOX), ph("recap", "body", { x: M, y: 2.85, w: 4.9, h: 1.1 })] });

  // ---------------------------------------------------------------- helpers
  const r2 = (v) => Math.round(v * 1000) / 1000;
  const pt = (v) => Math.max(0.5, Math.round(v * 2) / 2);
  const words = Object.entries(opts.colorWords || {}).map(([a, b]) => [new RegExp(`\\b${a}\\b`, "g"), b]);
  /* Colour words follow the theme when the prototype named other colours. */
  const rc = (t) => words.reduce((s, [re, b]) => s.replace(re, b), t);
  /* Keep references and quantities on one line: "§V-D", "28 nm", "Fig. 9" never break. */
  const NB = [
    [/§([IVX]+)-([A-D])/g, "§$1‑$2"],
    [/(\d) (nm|ns|µs|ms|MB|GB|KB|GB\/s|TB\/s|GHz|MHz|kHz|B|%|pJ|nJ|mW|mm²|TOPS|GOPS)(?![\w])/g, "$1 $2"],
    ...(opts.nbRules || []),
    [/\b(Fig\.|Figs\.|Table|Eq\.|Sec\.) (\d|[IVX])/g, "$1 $2"],
    [/§([IVX]+)–([IVX]+)/g, "§$1–⁠$2"],
  ];
  const nb = (t) => NB.reduce((s, [re, b]) => s.replace(re, b), t);
  const wordCount = (s) => s.trim().split(/\s+/).filter(Boolean).length;

  const NOTES = []; // [slide no, kind, words of the spoken notes] for the build report
  const FIGPT = []; // [slide no, figure, scaled pt, set pt] for every figure text
  let SLIDE_NO = 0;

  function section(title) { pres.addSection({ title }); }
  function newSlide(master, sectionTitle, kind, extra = {}) {
    const sl = pres.addSlide({ masterName: master, sectionTitle });
    SLIDE_NO += 1;
    Object.assign(sl, { _kind: kind, _no: SLIDE_NO, _master: master, _section: sectionTitle, _appendix: !!extra.appendix });
    return sl;
  }
  /* Speaker notes; a figure caption or source moved off the slide is appended ("Figure: ..."). */
  function notes(sl, text, figCaption, label = "Figure") {
    const t = text || "";
    sl.addNotes(rc(figCaption ? `${t} ${label}: ${figCaption}` : t));
    NOTES.push([sl._no, sl._kind, wordCount(t)]);
  }
  function paras(sentences, extra = {}) {
    return sentences.map((t, i) => ({ text: nb(t), options: { breakLine: i < sentences.length - 1, ...extra } }));
  }
  /* The supporting sentences of a content slide: bullets in the layout's band (size, bullet and spacing come
     from the template's body style; transplant.py strips the per-run size and colour pptxgenjs writes).
     see: an appendix id; the last bullet then ends with a pointer to it. */
  function band(sl, sentences, see) {
    const runs = sentences.map((t, i) => ({ text: nb(t), options: { breakLine: i < sentences.length - 1 } }));
    if (see) {
      runs[runs.length - 1].options.breakLine = false;
      runs.push({ text: ` → appendix ${see}`, options: { bold: true, color: NAVY } });
    }
    sl.addText(runs, { placeholder: "band" });
  }

  /* Draw one parsed SVG figure into `box` (inches). morph: name keyed elements "!!key" and the static ones
     "!!u<n>", so Morph can pair every element across the frame slides of a storyboard. */
  function drawFig(slide, fig, box, opt = {}) {
    const [vx, vy, vw, vh] = fig.bb || fig.vb; // the content bounds, so the figure fills the box
    const s = Math.min(box.w / vw, box.h / vh);
    const ox = box.x + (opt.center ? (box.w - vw * s) / 2 : 0);
    const oy = box.y + (opt.middle ? (box.h - vh * s) / 2 : 0);
    const X = (u) => ox + (u - vx) * s, Y = (u) => oy + (u - vy) * s;
    let un = 0;
    const id = opt.id || "fig";
    const filled = []; // filled shapes drawn so far, to pick the text colour on top of them
    if (fig.image) { // an embedded picture (a figure outside the shape vocabulary)
      slide.addImage({ data: fig.image, x: r2(ox), y: r2(oy), w: r2(vw * s), h: r2(vh * s), objectName: `${id}:image` });
      return { x: ox, y: oy, w: vw * s, h: vh * s, scale: s };
    }
    for (const sh of fig.shapes) {
      const base = sh.name ? sh.name : `u${un++}`;
      const objectName = opt.morph ? `!!${base}` : `${id}:${base}`;
      if (sh.t === "rect" || sh.t === "circle" || sh.t === "ellipse") {
        const o = { objectName };
        let b;
        if (sh.t === "rect") b = { x0: sh.x, y0: sh.y, x1: sh.x + sh.w, y1: sh.y + sh.h };
        else if (sh.t === "circle") b = { x0: sh.cx - sh.r, y0: sh.cy - sh.r, x1: sh.cx + sh.r, y1: sh.cy + sh.r };
        else b = { x0: sh.cx - sh.rx, y0: sh.cy - sh.ry, x1: sh.cx + sh.rx, y1: sh.cy + sh.ry };
        if (sh.t === "rect") Object.assign(o, { x: r2(X(sh.x)), y: r2(Y(sh.y)), w: r2(sh.w * s), h: r2(sh.h * s) });
        else if (sh.t === "circle") Object.assign(o, { x: r2(X(sh.cx - sh.r)), y: r2(Y(sh.cy - sh.r)), w: r2(2 * sh.r * s), h: r2(2 * sh.r * s) });
        else Object.assign(o, { x: r2(X(sh.cx - sh.rx)), y: r2(Y(sh.cy - sh.ry)), w: r2(2 * sh.rx * s), h: r2(2 * sh.ry * s) });
        const sw = sh.stroke ? pt(sh.sw * s * 72) : 0.75;
        // highlight: gold fill (light boxes at 60 % transparency) with a navy outline
        if (sh.fill) o.fill = sh.fill === "tint" ? { color: GOLD, transparency: 60 } : { color: COL[sh.fill] };
        if (sh.stroke) o.line = { color: sh.stroke === "accent" ? NAVY : COL[sh.stroke], width: sw, ...(sh.dash ? { dashType: "dash" } : {}) };
        else if (sh.fill === "accent" || sh.fill === "tint") o.line = { color: NAVY, width: sw };
        slide.addShape(sh.t === "rect" ? pres.shapes.RECTANGLE : pres.shapes.OVAL, o);
        if (sh.fill) filled.push({ ...b, fill: sh.fill });
      } else if (sh.t === "line") {
        const x1 = X(sh.x1), y1 = Y(sh.y1), x2 = X(sh.x2), y2 = Y(sh.y2);
        slide.addShape(pres.shapes.LINE, {
          objectName, x: r2(Math.min(x1, x2)), y: r2(Math.min(y1, y2)), w: r2(Math.abs(x2 - x1)), h: r2(Math.abs(y2 - y1)),
          flipH: x2 < x1, flipV: y2 < y1,
          line: { color: COL[sh.stroke], width: pt(sh.sw * s * 72), ...(sh.dash ? { dashType: "dash" } : {}),
            ...(sh.arrow ? { endArrowType: "triangle" } : {}) },
        });
      } else if (sh.t === "text") {
        const fs_ = sh.size; // px in SVG units
        // the scaled size, raised to MIN_PT where the figure is too small; the box grows with the font
        const ptScaled = fs_ * s * 72, ptSet = Math.max(MIN_PT, ptScaled), fsE = ptSet / (s * 72);
        FIGPT.push([SLIDE_NO, id, ptScaled, ptSet]);
        const wU = sh.s.length * fsE * 0.58 + fsE * 0.6;
        const hU = fsE * 1.5;
        let xU = sh.x;
        if (sh.anchor === "middle") xU = sh.x - wU / 2;
        else if (sh.anchor === "end") xU = sh.x - wU;
        // text colour: highlight text and bold headings navy; white text on a light fill becomes navy
        let color = COL[sh.color];
        if (sh.color === "accentink" || (sh.bold && sh.color === "ink")) color = NAVY;
        if (sh.color === "white") {
          const ty = sh.y - fs_ * 0.33;
          const under = filled.filter((b) => sh.x >= b.x0 && sh.x <= b.x1 && ty >= b.y0 && ty <= b.y1).pop();
          if (!under || LIGHT.includes(under.fill)) color = NAVY;
        }
        slide.addText(rc(sh.s), {
          objectName, x: r2(X(xU)), y: r2(Y(sh.y - fs_ * 0.33 - hU / 2)), w: r2(wU * s), h: r2(hU * s),
          fontSize: pt(ptSet), bold: !!sh.bold, color,
          align: sh.anchor === "middle" ? "center" : sh.anchor === "end" ? "right" : "left",
          valign: "middle", margin: 0, wrap: false, fit: "none", isTextBox: true,
        });
      }
    }
    return { x: ox, y: oy, w: vw * s, h: vh * s, scale: s };
  }

  // ---------------------------------------------------------------- title, outline, dividers, closing
  /* Title Opener: logo top left (transplant.py), title between the template's two brand rules, byline,
     presenter and date below the second rule on the left, up to three key points on the right.
     o: title, subtitle, byline [lines], presenter, date, points [[head, sub]], notes. */
  function titleSlide(sectionTitle, o) {
    const sl = newSlide("TITLE", sectionTitle, "title");
    const t = [{ text: o.title, options: { fontSize: 36, bold: true, color: C.text1, breakLine: !!o.subtitle } }];
    if (o.subtitle) t.push({ text: o.subtitle, options: { fontSize: 16, bold: false, color: C.text1 } });
    sl.addText(t, { placeholder: "title" });
    const by = o.byline || [];
    if (by.length) {
      sl.addText(by.map((l, i) => ({ text: l, options: i < by.length - 1 ? { breakLine: true } : {} })),
        { x: M, y: 3.45, w: 3.95, h: 0.85, fontSize: F(16), color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "authors" });
    }
    // the template's presenter and department slots (Title Opener placeholders 23 and 22)
    sl.addText(o.presenter || "Presenter: ______", { x: M, y: 4.90, w: 4.0, h: 0.18, fontSize: 12, bold: true, color: NAVY, margin: 0, valign: "bottom", isTextBox: true, objectName: "ph:body:23" });
    sl.addText(o.date || "Date: ______", { x: M, y: 5.10, w: 4.0, h: 0.18, fontSize: 12, color: C.text1, margin: 0, valign: "bottom", isTextBox: true, objectName: "ph:body:22" });
    (o.points || []).slice(0, 3).forEach(([h, s], i) => {
      const y = 3.45 + i * 0.5, d = 0.36, x = 4.95;
      sl.addShape(pres.shapes.OVAL, { x, y: y + 0.04, w: d, h: d, ...gold(), objectName: `part${i}-dot` });
      sl.addText(String(i + 1), { x, y: y + 0.04, w: d, h: d, fontSize: F(18), bold: true, color: NAVY, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `part${i}-n` });
      sl.addText([{ text: h, options: { fontSize: F(20), bold: true, color: NAVY, breakLine: true } }, { text: s, options: { fontSize: F(16), color: C.text1 } }],
        { x: x + 0.5, y, w: R - x - 0.5, h: 0.45, valign: "middle", margin: 0, isTextBox: true, objectName: `part${i}-text` });
    });
    notes(sl, o.notes);
    return sl;
  }

  const NUMWORD = ["No", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"];
  /* The outline (hi < 0) or a section divider (hi = the part about to start, highlighted).
     parts: [[label, sub]]; o: { title, kicker } overrides (the appendix index uses them). */
  function outlineSlide(sectionTitle, parts, hi, noteText, o = {}) {
    const sl = newSlide("DIVIDER", sectionTitle, o.kind || (hi < 0 ? "outline" : "divider"), { appendix: o.appendix });
    const n = parts.length;
    sl.addText(o.title || "Outline", { placeholder: "title" });
    sl.addText(o.kicker || (hi < 0 ? `${NUMWORD[n] || n} parts` : `Next: part ${hi + 1} of ${n}`), { placeholder: "kicker", color: hi < 0 ? C.text1 : NAVY });
    const x0 = 3.80, y0 = 0.56, rowH = n <= 5 ? 0.87 : 4.35 / n, d = Math.min(0.525, rowH - 0.2);
    const labPt = o.labPt || (n <= 5 ? F(26) : 16), subPt = o.subPt || (n <= 5 ? F(18) : LABEL_PT);
    parts.forEach(([lab, sub, mark], i) => {
      const y = y0 + i * rowH, on = i === hi;
      if (on) sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x0 - 0.15, y: y - 0.09, w: R - (x0 - 0.15), h: rowH - 0.075, rectRadius: 0.06, fill: { color: C.accent3 }, objectName: `row${i}-card` });
      sl.addShape(pres.shapes.OVAL, { x: x0, y: y + 0.09, w: d, h: d, objectName: `row${i}-dot`,
        ...(on ? gold() : { fill: { color: hi < 0 ? NAVY : C.accent3 } }) });
      sl.addText(mark || String(i + 1), { x: x0, y: y + 0.09, w: d, h: d, align: "center", valign: "middle", fontSize: mark && mark.length > 1 ? LABEL_PT : F(22), bold: true,
        color: on ? NAVY : hi < 0 ? C.background1 : C.accent2, margin: 0, isTextBox: true, objectName: `row${i}-n` });
      const rows = [{ text: lab, options: { fontSize: labPt, bold: on || hi < 0, color: on ? NAVY : hi < 0 ? C.text1 : C.accent2, breakLine: !!sub } }];
      if (sub) rows.push({ text: sub, options: { fontSize: subPt, color: on || hi < 0 ? C.text1 : C.accent2 } });
      sl.addText(rows, { x: x0 + 0.71, y: y, w: R - (x0 + 0.71) - 0.05, h: rowH - 0.15, valign: "middle", margin: 0, isTextBox: true, objectName: `row${i}-text` });
    });
    notes(sl, noteText);
    return sl;
  }

  /* Thank You w/title: title on the brand rule, recap and citation below it on the left, up to three
     questions on the right. o: title, recap, citation, questions [..], notes. */
  function closingSlide(sectionTitle, o) {
    const sl = newSlide("CLOSING", sectionTitle, "closing");
    sl.addText(o.title || "Questions", { placeholder: "title" });
    if (o.recap) sl.addText(o.recap, { placeholder: "recap" });
    if (o.citation) {
      sl.addText(o.citation, { x: M, y: 4.40, w: 4.9, h: 0.75, fontSize: LABEL_PT, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "citation" });
    }
    (o.questions || []).slice(0, 3).forEach((q, i) => {
      const y = 2.85 + i * 0.72, d = 0.42, x = 5.85;
      sl.addShape(pres.shapes.OVAL, { x, y: y + 0.08, w: d, h: d, ...gold(), objectName: `q${i}-dot` });
      sl.addText("?", { x, y: y + 0.08, w: d, h: d, fontSize: F(20), bold: true, color: NAVY, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `q${i}-mark` });
      sl.addText(q, { x: x + 0.57, y, w: R - x - 0.57, h: 0.62, fontSize: TEXT_PT, bold: true, color: NAVY, valign: "middle", margin: 0, isTextBox: true, objectName: `q${i}-text` });
    });
    notes(sl, o.notes);
    return sl;
  }

  // ---------------------------------------------------------------- content slides
  /* A content slide whose area holds one figure, cropped to its content and scaled to fill the area.
     o: fig (parsed), id, title, body [bullets], notes, caption (to the notes), see (appendix id). */
  function figSlide(sectionTitle, o) {
    const sl = newSlide("CONTENT", sectionTitle, o.kind || "content", { appendix: o.appendix });
    sl.addText(o.title, { placeholder: "title" });
    band(sl, o.body, o.see);
    drawFig(sl, o.fig, AREA, { id: o.id, center: true, middle: true });
    notes(sl, o.notes, o.caption);
    return sl;
  }

  /* One slide per storyboard frame on the FRAME layout; every frame after the first gets Morph.
     o: story ({frames: [{shapes, bb, title, caption}]}), id, title, titles [step titles], captions, notes [per frame]. */
  function storySlides(sectionTitle, o) {
    const st = o.story;
    const n = st.frames.length;
    st.frames.forEach((f, i) => {
      const sl = newSlide("FRAME", sectionTitle, i === 0 ? "frame-first" : "frame", { appendix: o.appendix });
      sl._morph = i > 0;
      sl.addText(o.title, { placeholder: "title" });
      // step indicator: dots + label, same names on every frame
      for (let j = 0; j < n; j++) {
        sl.addShape(pres.shapes.OVAL, { x: r2(FCOL.x + j * FDOT_STEP), y: FDOTS_Y, w: FDOT, h: FDOT, objectName: `!!dot${j}`,
          ...(j === i ? gold() : { fill: { color: j < i ? C.accent2 : C.accent3 } }) });
      }
      sl.addText([
        { text: `Step ${i + 1} of ${n}`, options: { color: C.accent2, fontSize: LABEL_PT, breakLine: true } },
        { text: rc((o.titles && o.titles[i]) || f.title), options: { color: NAVY, fontSize: TEXT_PT, bold: true } },
      ], { x: FCOL.x, y: FSTEP.y, w: FCOL.w, h: FSTEP.h, margin: 0, valign: "top", isTextBox: true, objectName: "!!steplabel" });
      const cap = (o.captions && o.captions[i]) || f.caption;
      sl.addText(paras([rc(cap)]), { placeholder: "stepcaption" });
      drawFig(sl, f, FAREA, { id: o.id, morph: true, center: true, middle: true });
      notes(sl, o.notes[i], o.caption);
    });
  }

  /* A headline number: rule, metric, label. */
  function stat(sl, x, y, w, metric, label, hot, sz = { metric: 20, label: LABEL_PT, mh: 0.33, lh: 0.40 }) {
    sl.addShape(pres.shapes.RECTANGLE, { x, y, w, h: 0.03, ...(hot ? gold(0.5) : { fill: { color: C.accent2 } }), objectName: `stat-rule-${metric}` });
    sl.addText(metric, { x, y: y + 0.05, w, h: sz.mh, fontSize: sz.metric, bold: true, fontFace: "+mj-lt", color: hot ? NAVY : C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: `stat-${metric}` });
    sl.addText(nb(label), { x, y: y + 0.06 + sz.mh, w, h: sz.lh, fontSize: sz.label, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: `stat-label-${metric}` });
  }
  /* Up to four headline numbers stacked in a right-hand column of the area (beside a figure). */
  function statColumn(sl, items, x = 6.85) {
    const w = R - x;
    items.forEach(([m, l, hot], i) => stat(sl, x, AREA.y + i * (AREA.h / Math.max(4, items.length)), w, m, l, hot));
  }
  /* Two to four big headline numbers in a row across the area. */
  function statRow(sl, items) {
    const gap = 0.45, n = items.length, sw = (AREA.w - (n - 1) * gap) / n;
    const big = n <= 3 ? { metric: F(72), label: F(22), mh: 0.9, lh: 0.85 } : { metric: 36, label: TEXT_PT, mh: 0.7, lh: 0.85 };
    items.forEach(([m, l, hot], i) => stat(sl, M + i * (sw + gap), AREA.y + 0.70, sw, m, nb(l), hot, big));
  }

  /* Up to three cards (number, head, text) filling the content area. */
  function cards(sl, items) {
    const n = items.length, gap = 0.15, w = (AREA.w - (n - 1) * gap) / n, y = AREA.y, h = AREA.h, d = 0.4;
    items.forEach(([head, text], i) => {
      const x = M + i * (w + gap);
      sl.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.accent3, transparency: 50 }, objectName: `card${i}` });
      sl.addShape(pres.shapes.OVAL, { x: x + 0.15, y: y + 0.12, w: d, h: d, ...gold(), objectName: `card${i}-dot` });
      sl.addText(String(i + 1), { x: x + 0.15, y: y + 0.12, w: d, h: d, fontSize: F(20), bold: true, color: NAVY, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: `card${i}-n` });
      sl.addText(head, { x: x + 0.15, y: y + 0.62, w: w - 0.3, h: 0.58, fontSize: 17, bold: true, color: NAVY, valign: "top", margin: 0, isTextBox: true, objectName: `card${i}-head` });
      sl.addText(nb(text), { x: x + 0.15, y: y + 1.24, w: w - 0.3, h: h - 1.30, fontSize: TEXT_PT, color: C.text1, valign: "top", margin: 0, isTextBox: true, objectName: `card${i}-text` });
    });
  }

  /* A full-width table at the top of the content area, in the template's table style (blue header row);
     13-14 pt, header and body alike; a dense setup table may go to 12 pt (the QA floor follows fontSize).
     rows: [{cells: [..], ours}]; o: colW (relative widths), boldFirst, name, fontSize, margin, rowH (inches per
     row, header first: html_to_spec.py's fit_table() grows the size and the rows so the table fills the area;
     the text is then centred in its row). Without rowH the rows take their natural height. */
  function table(sl, head, rows, o) {
    const border = { type: "solid", pt: 0.75, color: HEX.line };
    const fs = o.fontSize || 13, hfs = fs;
    const name = o.name || "table";
    QA.tableFloors[name] = o.dense || fs < 13 ? 12 : 13; // the QA floor: 13 pt, a dense setup table 12 pt
    const hdr = head.map((t) => ({ text: t, options: { bold: true, fontSize: hfs, color: C.background1, fill: { color: C.accent1 }, border } }));
    const body = rows.map((r) => r.cells.map((t, j) => ({ text: nb(t), options: { fontSize: fs, color: C.text1, bold: j === 0 && !!o.boldFirst, fill: { color: r.ours ? C.accent3 : C.background1 }, border } })));
    const tw = AREA.w, sum = o.colW.reduce((a, b) => a + b, 0);
    const fill = Array.isArray(o.rowH) && o.rowH.length === rows.length + 1 ? { rowH: o.rowH.map(r2), valign: "middle" } : { valign: "top" };
    sl.addTable([hdr, ...body], { x: AREA.x, y: AREA.y, w: tw, colW: o.colW.map((c) => r2(c * tw / sum)), fontSize: fs, margin: o.margin || [0.05, 0.075, 0.05, 0.075], objectName: name, ...fill });
  }

  /* A content slide with only a title, an area filler (fn) and the band. */
  function contentSlide(sectionTitle, o, fill) {
    const sl = newSlide("CONTENT", sectionTitle, o.kind || "content", { appendix: o.appendix });
    sl.addText(o.title, { placeholder: "title" });
    fill(sl);
    band(sl, o.body, o.see);
    notes(sl, o.notes, o.caption, o.captionLabel || "Source");
    return sl;
  }

  // ---------------------------------------------------------------- write
  async function write(out) {
    out = path.resolve(out);
    fs.mkdirSync(work, { recursive: true });
    const base = path.basename(out, ".pptx");
    const RAW = path.join(work, `${base}.raw.pptx`), META = path.join(work, `${base}.meta.json`);
    await pres.writeFile({ fileName: RAW });
    const notesWords = Object.fromEntries(NOTES.map(([n, , w]) => [n, w]));
    fs.writeFileSync(META, JSON.stringify({ ...META_DOC, geometry: GEOM, qa: QA,
      slides: pres._slides.map((s) => ({ layout: s._master, kind: s._kind, section: s._section, morph: !!s._morph,
        appendix: !!s._appendix, slideNumber: NUMBERED.includes(s._master), notesWords: notesWords[s._no] || 0 })) }, null, 1));
    const py = path.join(work, "venv", "bin", "python");
    execFileSync(fs.existsSync(py) ? py : "python3", [path.join(__dirname, "transplant.py"), RAW, META, out, "--brand", brand], { stdio: "inherit" });
    const morphSlides = pres._slides.filter((s) => s._morph).map((s) => s._no);
    console.log(`${out}: ${SLIDE_NO} slides, Morph on ${morphSlides.length} frame slides`);
    console.log("notes words by slide:", NOTES.map(([n, k, w]) => `${n}:${k[0]}${w}`).join(" "));
    const short = NOTES.filter(([, k, w]) => ["content", "title", "outline", "closing"].includes(k) && (w < 60 || w > 300));
    if (short.length) console.log("WARN notes outside 60-300 words (slide, kind, words):", JSON.stringify(short));
    // figures whose smallest text, scaled with the figure, falls below MIN_PT and is raised to it
    const lift = {};
    for (const [n, id, scaled] of FIGPT) {
      const k = `${n}:${id}`;
      lift[k] = Math.min(lift[k] ?? 99, scaled);
    }
    const raised = Object.entries(lift).filter(([, v]) => v < MIN_PT).map(([k, v]) => `${k} ${v.toFixed(1)}`);
    console.log(`figure text raised to ${MIN_PT} pt (slide:figure smallest scaled pt):`, raised.join(", ") || "none");
    return { raw: RAW, meta: META, out, slides: SLIDE_NO };
  }

  return {
    pres, C, NAVY, GOLD, gold, nb, rc, paras, band, drawFig, notes, newSlide, section,
    titleSlide, outlineSlide, closingSlide, figSlide, storySlides, stat, statColumn, statRow, cards, table,
    contentSlide, write, get slideCount() { return SLIDE_NO; },
  };
}

module.exports = { createDeck, GEOM, M, R, CW, F, K, AREA, BAND, FAREA, FCOL, TITLE_PT, TEXT_PT, LABEL_PT };
