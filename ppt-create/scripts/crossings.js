/* crossings.js - the label-crossing pass of the ppt-create skill (no dependencies; node).

   A crossing is a line (a gridline, rule, connector, leader or data curve) that runs through a text label's drawn
   extent. Labels must stay readable, so the build clears every crossing before QA, in the deck's own geometry:
   each label is measured at its final size, raised to the 12 pt floor, with Liberation Sans widths (the metrics
   deck_qa.py measures with), so a figure that leaves this pass gives QA `lines` nothing to report.

   fixFrames(frames, s, opts) takes the parsed figure (one frame) or a storyboard (all its frames, which share one
   crop) in SVG units, and s, the deck's scale in inches per SVG unit; it returns new shape lists and a log. The fix
   for each crossing, in order of preference:
     1. a gridline (class "grid") or a rule (an axis-parallel line without an arrowhead, not part of a polyline,
        spanning at least 30 % of the figure along its axis) is CUT around the label: a grid line wherever it meets
        a label's clear box, a rule where it runs through a label's ink;
     2. a leader or connector (a <line>, a polyline of up to three points, or any line with an arrowhead) whose end
        lies within 1 em of the label is TRIMMED to end at the label's edge (the arrowhead moves with the end);
     3. a label on a data line or curve (or on a line it cannot trim) is NUDGED to the nearest clear spot, in steps
        of 0.25 em up to 3 em: clear of every line, off every other label, inside the figure's crop, inside (or
        outside) the same boxes as before, and still nearer the line it sat on than any other line (so it keeps
        naming that line);
     4. a label with no clear spot gets a KNOCKOUT: a rectangle in the slide's background colour behind it, drawn
        above the lines (named "<label>.ko"; deck_qa.py does not count a line under a knockout as a crossing).
   Storyboards: an element is identified across frames by its data-key, or by its order among the unkeyed elements
   (Morph pairs those by order). Every fix is decided over all frames and applied identically to that element in
   every frame (one nudge, one trim, one set of cuts), so Morph names, counts and positions stay consistent.

   Used by deck_lib.js (drawFig, storySlides: every figure of every deck, from build_deck.js or a hand-written
   builder) and by html_to_spec.py's prototype lint (node crossings.js --report IN.json: prints the fix the build
   will make for each crossing, so the author can carry a moved label back into the prototype). */
"use strict";

const MIN_PT = 12; // the figure-label floor (deck_lib.js LABEL_PT)
// Liberation Sans advance widths (per 1000 em), regular and bold, for these characters; others count 0.6 / 0.65 em
const CHARS = " !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~·→←↑↓×µ–—≈≤≥²³§°…αβγδΔπσ½¼¾’‘“”≠±√∑";
const W = [
  "278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584,278,1000,1000,500,500,584,576,556,1000,549,549,549,333,333,556,400,1000,578,575,500,557,668,690,617,834,834,834,222,222,333,333,549,549,549,713",
  "278,333,474,556,556,889,722,238,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,333,333,584,584,584,611,975,722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,944,667,667,611,333,278,333,584,556,333,556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,333,611,556,778,556,556,500,389,280,389,584,278,1000,1000,500,500,584,576,556,1000,549,549,549,333,333,556,400,1000,615,610,556,606,719,766,684,834,834,834,278,278,500,500,549,549,549,713",
].map((row) => {
  const v = row.split(",").map(Number), m = new Map();
  [...CHARS].forEach((c, i) => m.set(c, v[i] / 1000));
  return m;
});

const NEAR_EM = 1.0; // a leader end this close to a label is the label's own leader: trim it there
const STEP_EM = 0.25, MAX_EM = 3.0; // nudge search
const PAD_X = 0.15, PAD_Y = 0.1; // em of clear space kept around a label's ink
const RULE_SPAN = 0.3; // a rule spans at least this share of the figure along its axis
const MIN_PIECE = 2; // SVG units: shorter cut pieces are dropped
const GAP_EM = 0.15; // a trimmed leader stops this far before the label's padded ink

function emWidth(str, bold) {
  const m = W[bold ? 1 : 0];
  let w = 0;
  for (const c of str) w += m.has(c) ? m.get(c) : bold ? 0.65 : 0.6;
  return w;
}
const ptRound = (v) => Math.max(0.5, Math.round(v * 2) / 2);
const union = (a, b) => [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])];
const overlaps = (a, b) => Math.min(a[2], b[2]) > Math.max(a[0], b[0]) && Math.min(a[3], b[3]) > Math.max(a[1], b[1]);
const inside = (a, b) => a[0] >= b[0] && a[1] >= b[1] && a[2] <= b[2] && a[3] <= b[3];
const shift = (r, dx, dy) => [r[0] + dx, r[1] + dy, r[2] + dx, r[3] + dy];
function rectDist(px, py, r) {
  const ddx = Math.max(r[0] - px, 0, px - r[2]), ddy = Math.max(r[1] - py, 0, py - r[3]);
  return Math.hypot(ddx, ddy);
}
function pointSegDist(px, py, x1, y1, x2, y2) {
  const dx = x2 - x1, dy = y2 - y1, L = dx * dx + dy * dy;
  const t = L === 0 ? 0 : Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / L));
  return Math.hypot(px - x1 - t * dx, py - y1 - t * dy);
}
/* distance from the kept range of a line to a box (0 when it passes through) */
function lineRectDist(L, r) {
  if (hits(L, r)) return 0;
  const ax = L.x1 + (L.x2 - L.x1) * L._t0, ay = L.y1 + (L.y2 - L.y1) * L._t0;
  const bx = L.x1 + (L.x2 - L.x1) * L._t1, by = L.y1 + (L.y2 - L.y1) * L._t1;
  return Math.min(rectDist(ax, ay, r), rectDist(bx, by, r),
    ...[[r[0], r[1]], [r[2], r[1]], [r[0], r[3]], [r[2], r[3]]].map(([px, py]) => pointSegDist(px, py, ax, ay, bx, by)));
}

/* The legacy label box of the gridline knockout (ea0c0fe): 0.6 em per character plus 0.3 em each side, 0.6 em
   above and below the label's middle, at the floor-raised size. Kept as part of the clear box, so a grid line keeps
   the gaps it had. */
function labelBoxes(shapes, s) {
  return shapes.filter((t) => t.t === "text").map((t) => legacyBox(t, s));
}
function legacyBox(t, s) {
  const fsE = Math.max(MIN_PT, t.size * s * 72) / (s * 72), w = t.s.length * fsE * 0.6 + fsE * 0.6;
  const x = t.anchor === "middle" ? t.x - w / 2 : t.anchor === "end" ? t.x - w : t.x - fsE * 0.3;
  const yc = t.y - t.size * 0.33;
  return [x, yc - fsE * 0.6, x + w, yc + fsE * 0.6];
}

/* A label's geometry in SVG units, as deck_lib.js draws it and deck_qa.py measures it: the font raised to the
   floor and rounded to 0.5 pt; the ink is the measured width placed by the anchor, and the glyph band of a
   centred 1.17-em line (0.385 em above to 0.465 em below the box middle, which sits 0.33 em above the baseline).
   pad: the ink plus PAD_X / PAD_Y em (what a moved label must keep clear, where a trimmed leader stops); clear: pad
   joined with the legacy box (the gap a gridline or rule is cut to). */
function labelGeom(t, s, text) {
  const fsE = ptRound(Math.max(MIN_PT, t.size * s * 72)) / (s * 72);
  const w = emWidth(text, !!t.bold) * fsE;
  const x0 = t.anchor === "middle" ? t.x - w / 2 : t.anchor === "end" ? t.x - w : t.x;
  const yc = t.y - t.size * 0.33;
  const ink = [x0, yc - 0.385 * fsE, x0 + w, yc + 0.465 * fsE];
  const pad = [ink[0] - PAD_X * fsE, ink[1] - PAD_Y * fsE, ink[2] + PAD_X * fsE, ink[3] + PAD_Y * fsE];
  return { fsE, ink, pad, clear: union(pad, legacyBox(t, s)) };
}

function segInRect(x1, y1, x2, y2, r) { // Liang-Barsky: the [t0, t1] part of the segment inside r, or null
  const dx = x2 - x1, dy = y2 - y1;
  let t0 = 0, t1 = 1;
  for (const [p, q] of [[-dx, x1 - r[0]], [dx, r[2] - x1], [-dy, y1 - r[1]], [dy, r[3] - y1]]) {
    if (p === 0) { if (q < 0) return null; continue; }
    const t = q / p;
    if (p < 0) t0 = Math.max(t0, t); else t1 = Math.min(t1, t);
    if (t0 > t1) return null;
  }
  return [t0, t1];
}
/* The kept parts of a line after removing the [t0, t1] stretches inside each box; parts under MIN_PIECE are dropped. */
function gridPieces(sh, boxes, keep = [[0, 1]]) {
  let iv = keep;
  for (const r of boxes) {
    const hit = segInRect(sh.x1, sh.y1, sh.x2, sh.y2, r);
    if (hit) iv = iv.flatMap(([a, b]) => [[a, Math.min(b, hit[0])], [Math.max(a, hit[1]), b]]);
  }
  const len = Math.hypot(sh.x2 - sh.x1, sh.y2 - sh.y1);
  return iv.filter(([a, b]) => (b - a) * len >= MIN_PIECE);
}
/* Does the kept range [t0, t1] of a line pass through r? */
function hits(L, r, t0 = L._t0, t1 = L._t1) {
  const h = segInRect(L.x1, L.y1, L.x2, L.y2, r);
  return !!h && Math.min(h[1], t1) > Math.max(h[0], t0);
}

/* gridline / rule (cut), leader (trim), data (move the label) */
function lineKind(L, bb) {
  if (L.grid) return "grid";
  const dx = Math.abs(L.x2 - L.x1), dy = Math.abs(L.y2 - L.y1);
  const poly = L.poly; // [segment index, segments, arrowhead on the polyline]
  if (!L.arrow && !poly && ((dy <= 0.5 && dx >= RULE_SPAN * bb[2]) || (dx <= 0.5 && dy >= RULE_SPAN * bb[3]))) return "rule";
  if (poly && poly[1] >= 3 && !poly[2]) return "data"; // a polyline of four or more points without an arrowhead: a curve
  return "leader";
}

/* frames: [{shapes, bb}] (one figure, or every frame of one storyboard: same bb); s: inches per SVG unit.
   opts.text(str): the text as the deck draws it (colour words replaced). Returns {frames: [shapes], log}. */
function fixFrames(frames, s, opts = {}) {
  const txt = opts.text || ((x) => x);
  const bb = frames[0].bb || frames[0].vb;
  const crop = [bb[0], bb[1], bb[0] + bb[2], bb[1] + bb[3]];
  const log = [];
  // identities, as drawFig names them: data-key, else u<n> by order among the unnamed shapes
  const F = frames.map((f) => {
    let un = 0;
    const shapes = f.shapes.map((sh) => ({ ...sh, _id: sh._id || sh.name || `u${un++}` }));
    const labels = shapes.filter((t) => t.t === "text");
    for (const t of labels) t._g = labelGeom(t, s, txt(t.s));
    const lines = shapes.filter((l) => l.t === "line");
    let grp = null; // the segments of one polyline form one line for the anchor rule below
    for (const l of lines) {
      l._t0 = 0; l._t1 = 1; l._kind = lineKind(l, bb);
      if (!l.poly || l.poly[0] === 0) grp = l._id;
      l._grp = grp;
    }
    const boxes = shapes.filter((r) => r.t === "rect" || r.t === "circle" || r.t === "ellipse").map((r) =>
      r.t === "rect" ? [r.x, r.y, r.x + r.w, r.y + r.h] : r.t === "circle" ? [r.cx - r.r, r.cy - r.r, r.cx + r.r, r.cy + r.r]
        : [r.cx - r.rx, r.cy - r.ry, r.cx + r.rx, r.cy + r.ry]);
    return { shapes, labels, lines, boxes };
  });
  const each = (fn) => F.forEach((f, i) => fn(f, i));
  const labelIds = [], seenL = new Set();
  each((f) => f.labels.forEach((t) => { if (!seenL.has(t._id)) { seenL.add(t._id); labelIds.push(t._id); } }));
  const textOf = (id) => { for (const f of F) { const t = f.labels.find((x) => x._id === id); if (t) return t.s; } return ""; };
  const entry = (o) => log.push(o);

  // 1. leaders: trim the end that sits at a label (decided over all frames, applied in all)
  const trims = new Map(); // line id -> {t0, t1, labels}
  const nudge = new Set();
  const anchor = new Map(); // label id -> the lines (polyline groups) it sat on: it stays nearest to them
  const onLine = (id, g) => { if (!anchor.has(id)) anchor.set(id, new Set()); anchor.get(id).add(g); };
  each((f) => {
    for (const L of f.lines) {
      if (L._kind !== "leader" && L._kind !== "data") continue;
      for (const T of f.labels) {
        if (!hits(L, T._g.ink)) continue;
        if (L._kind === "data") { nudge.add(T._id); onLine(T._id, L._grp); continue; }
        const len = Math.hypot(L.x2 - L.x1, L.y2 - L.y1), near = NEAR_EM * T._g.fsE;
        const startEnd = !L.poly || L.poly[0] === 0, endEnd = !L.poly || L.poly[0] === L.poly[1] - 1;
        // the end at the label (the nearer one when a short leader has both close): trim it if 0.5 em stays
        const dS = startEnd ? rectDist(L.x1, L.y1, T._g.pad) : Infinity, dE = endEnd ? rectDist(L.x2, L.y2, T._g.pad) : Infinity;
        const h = segInRect(L.x1, L.y1, L.x2, L.y2, T._g.pad);
        const gap = GAP_EM * T._g.fsE / len, keep = 0.5 * T._g.fsE;
        const tr = trims.get(L._id) || { t0: 0, t1: 1, labels: new Set() };
        if (h && dE <= near && dE <= dS && (h[0] - gap) * len >= keep) {
          tr.t1 = Math.min(tr.t1, h[0] - gap);
        } else if (h && dS <= near && dS < dE && (1 - h[1] - gap) * len >= keep) {
          tr.t0 = Math.max(tr.t0, h[1] + gap);
        } else { nudge.add(T._id); onLine(T._id, L._grp); continue; }
        tr.labels.add(T._id);
        trims.set(L._id, tr);
      }
    }
  });
  for (const [id, tr] of trims) {
    each((f) => f.lines.filter((L) => L._id === id).forEach((L) => { L._t0 = tr.t0; L._t1 = tr.t1; }));
    const lbl = [...tr.labels].map((x) => `'${textOf(x)}'`).join(", ");
    if (tr.t1 < 1) entry({ element: id, action: "trim end", label: lbl, detail: `leader ends at the label's edge (kept 0-${tr.t1.toFixed(3)} of its length)` });
    if (tr.t0 > 0) entry({ element: id, action: "trim start", label: lbl, detail: `leader starts at the label's edge (kept ${tr.t0.toFixed(3)}-1 of its length)` });
  }
  // any label still crossed by a line that is not cut (a trimmed leader can cross another label) moves
  each((f) => f.lines.forEach((L) => {
    if (L._kind === "grid" || L._kind === "rule") return;
    f.labels.forEach((T) => { if (hits(L, T._g.ink)) { nudge.add(T._id); onLine(T._id, L._grp); } });
  }));

  // 2. labels on lines: the nearest clear spot, the same move in every frame; no spot: a knockout
  const cand = [];
  const dirs = [[0, -1], [0, 1], [1, 0], [-1, 0], [1, -1], [-1, -1], [1, 1], [-1, 1]];
  for (let k = 1; k <= MAX_EM / STEP_EM; k++) dirs.forEach(([a, b], j) => cand.push([a * k, b * k, Math.hypot(a, b) * k, j]));
  cand.sort((p, q) => p[2] - q[2] || p[3] - q[3]);
  const knock = new Set();
  for (const id of labelIds) {
    if (!nudge.has(id)) continue;
    const inst = [];
    each((f, i) => f.labels.filter((t) => t._id === id).forEach((t) => inst.push([f, t])));
    const fsE = inst[0][1]._g.fsE;
    const ok = (dx, dy) => inst.every(([f, T]) => {
      const g = T._g, ink = shift(g.ink, dx, dy), pad = shift(g.pad, dx, dy);
      if (!inside(pad, crop)) return false;
      if (f.lines.some((L) => L._kind !== "grid" && L._kind !== "rule" && hits(L, pad))) return false;
      if (f.labels.some((o) => o !== T && overlaps(pad, o._g.ink))) return false;
      // its anchor: the label stays nearer the line it sat on than any other line (its own trimmed leaders aside)
      const own = anchor.get(id) || new Set();
      let dOwn = Infinity, dOther = Infinity;
      for (const L of f.lines) {
        if (L._kind === "grid" || L._kind === "rule" || (trims.get(L._id) && trims.get(L._id).labels.has(id))) continue;
        const d = lineRectDist(L, pad);
        if (own.has(L._grp)) dOwn = Math.min(dOwn, d); else dOther = Math.min(dOther, d);
      }
      if (dOwn < Infinity && dOwn > dOther) return false; // (a frame without that line has no anchor to keep)
      return f.boxes.every((b) => {
        const was = inside(g.ink, b) ? "in" : overlaps(g.ink, b) ? "part" : "out";
        return was === "part" || (was === "in" ? inside(ink, b) : !overlaps(ink, b));
      });
    });
    const hit = cand.find(([a, b]) => ok(a * STEP_EM * fsE, b * STEP_EM * fsE));
    if (hit) {
      const dx = hit[0] * STEP_EM * fsE, dy = hit[1] * STEP_EM * fsE;
      for (const [, T] of inst) {
        T.x += dx; T.y += dy;
        for (const k of ["ink", "pad", "clear"]) T._g[k] = shift(T._g[k], dx, dy);
      }
      entry({ element: id, action: "nudge", label: `'${textOf(id)}'`, dx: +(dx * s).toFixed(3), dy: +(dy * s).toFixed(3),
        dxU: +dx.toFixed(1), dyU: +dy.toFixed(1),
        detail: `moved ${(Math.hypot(dx, dy) * s).toFixed(2)} in ${dirWord(dx, dy)}, clear of the line` });
    } else {
      knock.add(id);
      entry({ element: id, action: "knockout", label: `'${textOf(id)}'`, detail: "no clear spot within 3 em: a background-colour box behind the label" });
    }
  }

  // 3. gridlines and rules: cut at the labels in their final places (one set of cuts over all frames)
  const cuts = new Map(); // line id -> {iv: [[a, b]] cut away, labels}
  each((f) => f.lines.forEach((L) => {
    if (L._kind !== "grid" && L._kind !== "rule") return;
    for (const T of f.labels) {
      const meets = L._kind === "grid" ? hits(L, T._g.clear) : hits(L, T._g.ink);
      if (!meets) continue;
      const h = segInRect(L.x1, L.y1, L.x2, L.y2, T._g.clear);
      if (!h) continue;
      const c = cuts.get(L._id) || { iv: [], labels: new Set(), kind: L._kind };
      c.iv.push(h);
      c.labels.add(T._id);
      cuts.set(L._id, c);
    }
  }));
  for (const [id, c] of cuts) {
    entry({ element: id, action: "cut", label: [...c.labels].map((x) => `'${textOf(x)}'`).join(", "),
      detail: `${c.kind === "grid" ? "gridline" : "rule (axis-parallel line across the plot)"} cut around the label${c.labels.size > 1 ? "s" : ""}` });
  }

  // 4. the new shape lists: kept line parts, knockouts with their labels on top
  const out = F.map((f) => {
    const res = [], top = [];
    for (const sh of f.shapes) {
      if (sh.t === "line") {
        const c = cuts.get(sh._id);
        let parts = [[sh._t0, sh._t1]];
        if (c) {
          for (const h of c.iv) parts = parts.flatMap(([a, b]) => [[a, Math.min(b, h[0])], [Math.max(a, h[1]), b]]);
          const len = Math.hypot(sh.x2 - sh.x1, sh.y2 - sh.y1);
          parts = parts.filter(([a, b]) => (b - a) * len >= MIN_PIECE);
        }
        const o = clean(sh);
        if (c || sh._t0 > 0 || sh._t1 < 1) { o.parts = parts; o.tEnd = sh._t1; }
        res.push(o);
      } else if (sh.t === "text" && knock.has(sh._id)) {
        const r = sh._g.pad;
        top.push({ t: "rect", x: r[0], y: r[1], w: r[2] - r[0], h: r[3] - r[1], fill: "white", stroke: null, sw: 0, dash: false,
          name: null, _id: `${sh._id}.ko`, ko: true }, clean(sh));
      } else res.push(clean(sh));
    }
    return res.concat(top);
  });
  // 5. what is left (should be nothing): a line through a label that is neither cut nor under a knockout
  each((f) => f.lines.forEach((L) => {
    if (cuts.has(L._id)) return;
    f.labels.forEach((T) => {
      if (!knock.has(T._id) && hits(L, T._g.ink)) entry({ element: T._id, action: "unresolved", label: `'${T.s}'`, detail: `line ${L._id} still crosses it` });
    });
  }));
  return { frames: out, log };
}
function clean(sh) {
  const o = { ...sh };
  for (const k of ["_g", "_t0", "_t1", "_kind", "_grp"]) delete o[k];
  return o;
}
function dirWord(dx, dy) {
  const v = Math.abs(dy) < 1e-9 ? "" : dy < 0 ? "up" : "down", h = Math.abs(dx) < 1e-9 ? "" : dx < 0 ? "left" : "right";
  return [v, h].filter(Boolean).join(" and ");
}

module.exports = { fixFrames, labelGeom, labelBoxes, gridPieces, segInRect, emWidth, lineKind, MIN_PT };

/* CLI for the prototype lint: node crossings.js --report IN.json  (IN: [{where, frames: [{shapes, bb}], box: [w, h]}])
   prints [{where, log}] for the figures the pass would change. */
if (require.main === module) {
  const fs = require("fs");
  const args = process.argv.slice(2);
  if (args[0] !== "--report" || !args[1]) {
    console.error("usage: node crossings.js --report IN.json");
    process.exit(2);
  }
  const items = JSON.parse(fs.readFileSync(args[1], "utf8"));
  const out = [];
  for (const it of items) {
    const bb = it.frames[0].bb || it.frames[0].vb;
    const s = Math.min(it.box[0] / bb[2], it.box[1] / bb[3]);
    const { log } = fixFrames(it.frames, s);
    if (log.length) out.push({ where: it.where, log });
  }
  process.stdout.write(JSON.stringify(out));
}
