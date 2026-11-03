// narrated.js: build a narrated figure (references/page-structure.md § Narrated figures) at build
// time, in Node. One sentence = one frame. The page supplies one function that draws a panel of its
// base scene; this helper lays out the two panel slots, writes every frame, the folded storyboard,
// the figure and the synced sentence list, and refuses to build frames the template's player could
// not show.
//
//   const N = require("<skill-dir>/assets/narrated.js");
//   const { html } = N.narrate({
//     id: "wcut",                      // unique per figure; frame ids become wcut1, wcut2, ...
//     lang: "en",                      // "en" or "ko": button and summary labels
//     steps: [                         // one entry per sentence
//       { tag: "1", text: "Fix a group of gates that must sit in one LUT.", a: { ...panel spec } },
//       ...,
//       { tag: "4", text: "Side by side: ...", a: { ...left }, b: { ...right } }   // a comparison
//     ],
//     drawPanel: (prefix, spec, dx, dy, visible) => svg,  // your base scene, see the contract below
//     caption: "What the colours, rings and numbers mean.",
//     width: 720, panelWidth: 360, height: 470, panelTop: 62    // optional
//   });
//
// The drawPanel contract. Draw the panel described by `spec` with its top-left corner at (dx, dy).
// Put data-key="<prefix><your key>" on EVERY element that can change between frames, one key per
// element (keys on leaves, not on groups whose children change). When `visible` is false, draw the
// same elements with " off" added to their class (the template's CSS hides .off). Elements you draw
// without a key must look the same in every frame. The helper calls drawPanel twice per frame:
// prefix "" for slot A and "B" for slot B. A frame without `b` shows A in the middle and hides B; a
// frame with `b` shows A on the left and B on the right, so the player slides A aside.
//
// Unkeyed elements are keyed for you. A panel moves between the middle (single frame) and the left
// (comparison frame), so every element in it changes position; narrate() therefore gives each
// element drawn without a data-key the key "<prefix>~<n>" (in drawing order, the same in every
// frame) and adds " off" to its class when the panel is hidden. Draw the same elements in the same
// order in every frame. Escape "<" and "&" in text you draw (esc() below).
//
// Passes (references/techniques.md § Passes): call narrate() once per pass with its own id and the
// same drawPanel; an easy pass hides layers through its panel spec instead of drawing a new picture.

"use strict";

function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
// a sentence may carry inline HTML (<strong>, <sub>); the SVG title and desc take its plain text
function plain(s) { return String(s).replace(/<[^>]+>/g, "").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&"); }
function off(visible) { return visible ? "" : " off"; }

const LABELS = {
  en: { play: "Play", pause: "Pause", prev: "Previous frame", next: "Next frame", step: "Frame", of: "of", all: "All frames at once" },
  ko: { play: "재생", pause: "일시정지", prev: "이전 장면", next: "다음 장면", step: "장면", of: "/", all: "모든 장면 한 번에 보기" }
};

// what the player never updates: the SVG with keyed leaves removed and keyed groups reduced to a tag
// (the same rule as check_page.py's frame_background)
function background(svg) {
  let s = svg.replace(/<title\b[\s\S]*?<\/title>|<desc\b[\s\S]*?<\/desc>/g, "");
  s = s.replace(/\s(?:id|aria-labelledby)="[^"]*"/g, "");
  s = s.replace(/<(\w+)\b[^>]*\bdata-key="[^"]*"[^>]*\/>/g, "");
  s = s.replace(/<(\w+)\b[^>]*\bdata-key="[^"]*"[^>]*>[^<]*<\/\1>/g, "");
  s = s.replace(/<(\w+)\b[^>]*\bdata-key="([^"]*)"[^>]*>/g, "<$1 key=$2>");
  return s.replace(/\s+/g, " ");
}
// key every unkeyed shape or text element (see the header) and hide it with a hidden panel
function autoKey(svg, prefix, visible) {
  let n = 0;
  return svg.replace(/<(rect|text|line|path|circle|ellipse|polygon|polyline)\b(?![^>]*\bdata-key=)([^>]*)>/g, (m, tag, rest) => {
    let r = rest, selfClose = /\/\s*$/.test(r);
    if (selfClose) r = r.replace(/\/\s*$/, "");
    if (!visible) r = /\bclass="/.test(r) ? r.replace(/\bclass="([^"]*)"/, (q, c) => `class="${c} off"`) : r + ' class="off"';
    return `<${tag} data-key="${prefix}~${n++}"${r}${selfClose ? "/" : ""}>`;
  });
}
function keys(svg) { return [...svg.matchAll(/data-key="([^"]+)"/g)].map((m) => m[1]); }

function validate(id, frames) {
  const k0 = keys(frames[0]), bg0 = background(frames[0]);
  const dup = k0.filter((k, i) => k0.indexOf(k) !== i);
  if (dup.length) throw new Error(`narrated ${id}: frame 1 repeats data-key ${[...new Set(dup)].join(", ")}`);
  frames.forEach((f, i) => {
    const k = keys(f);
    if (k.join(",") !== k0.join(",")) {
      const miss = k0.filter((x) => !k.includes(x)).concat(k.filter((x) => !k0.includes(x)));
      throw new Error(`narrated ${id}: frame ${i + 1} has different keyed elements (${miss.slice(0, 6).join(", ")}); draw every element in every frame and hide unused ones with .off`);
    }
    if (background(f) !== bg0) throw new Error(`narrated ${id}: frame ${i + 1} changes something that has no data-key; the player would never show that change`);
  });
}

function narrate(o) {
  const W = o.width || 720, PW = o.panelWidth || W / 2, H = o.height || 470, top = o.panelTop || 62;
  const L = LABELS[o.lang] || LABELS.en;
  if (!o.steps || o.steps.length < 3 || o.steps.length > 8) throw new Error(`narrated ${o.id}: use 3 to 8 sentences (got ${o.steps ? o.steps.length : 0}); split the block if it needs more`);
  const last = o.steps[o.steps.length - 1];
  if (o.steps.some((s) => s.b) && !last.b) console.warn(`narrated ${o.id}: a comparison frame exists but the last frame is single; end a comparison side by side`);
  const frames = o.steps.map((F, i) => {
    const two = !!F.b;
    const head = `<text data-key="tag" x="10" y="22" class="t-case">${esc(F.tag)}</text>`;
    const split = `<line data-key="split" x1="${PW}" y1="40" x2="${PW}" y2="${H - 10}" class="s-grid dashed${off(two)}"></line>`;
    const draw = (prefix, spec, dx, vis) => (o.autoKey === false ? o.drawPanel(prefix, spec, dx, top, vis) : autoKey(o.drawPanel(prefix, spec, dx, top, vis), prefix, vis));
    const A = `<g class="case" data-case="A">${draw("", F.a || {}, two ? 0 : (W - PW) / 2, true)}</g>`;
    const B = `<g class="case" data-case="B">${draw("B", F.b || F.a || {}, PW, two)}</g>`;
    return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-labelledby="${o.id}${i + 1}-title ${o.id}${i + 1}-desc"><title id="${o.id}${i + 1}-title">${esc(plain(F.tag))}</title><desc id="${o.id}${i + 1}-desc">${esc(plain(F.text))}</desc>${head}${split}${A}${B}</svg>`;
  });
  validate(o.id, frames);
  const storyboard = frames.map((svg, i) => `            <li class="frame">\n              ${svg}\n              <p class="frame-caption">${o.steps[i].text}</p>\n            </li>`).join("\n");
  const sentences = o.steps.map((F) => `        <li><span class="sync-tag">${esc(F.mark || F.tag.split(/\s/)[0])}</span> ${F.text}</li>`).join("\n");
  const figure = `      <figure class="timeline wide-frames narrated sheet wide" data-step-word="${L.step}" data-of-word="${L.of}" data-hold-ms="${o.holdMs || 4200}" aria-labelledby="${o.id}-caption">
        <div class="player js-only">
          <div class="stage"></div>
          <p class="stage-caption" aria-live="polite"></p>
          <div class="controls">
            <button type="button" data-act="play" data-play-label="${L.play}" data-pause-label="${L.pause}">${L.play}</button>
            <button type="button" data-act="prev" aria-label="${L.prev}">←</button>
            <button type="button" data-act="next" aria-label="${L.next}">→</button>
            <input type="range" class="scrub" min="0" max="1" step="1" value="0" aria-label="${L.step}">
            <output class="counter"></output>
          </div>
        </div>
        <details class="all-frames">
          <summary>${L.all}</summary>
          <ol class="storyboard">
${storyboard}
          </ol>
        </details>
        <figcaption id="${o.id}-caption">${o.caption || ""}</figcaption>
      </figure>`;
  const list = `      <ol class="sync-steps">\n${sentences}\n      </ol>`;
  return { html: figure + "\n" + list, figure, list, frames };
}

module.exports = { narrate, validate, background, keys, autoKey, esc, off, plain };
