#!/usr/bin/env node
// check_players.mjs: step through every player on a page in headless Chrome and check what
// check_page.py cannot, because it never runs the page:
//   - after each "next", the stage shows exactly the matching storyboard frame (classes and text of
//     every keyed element), so the animation and the storyboard tell the same story;
//   - for a narrated figure, exactly the current frame's sentence is lit in its ol.sync-steps;
//   - no visible SVG text runs past its figure's viewBox (a clipped label or readout), in any
//     figure on the page: static figures, storyboard frames (folded <details> are opened for this)
//     and the widget's first render. A long one-line label is the usual cause: split it in two or
//     make the figure taller.
//
// Usage: node check_players.mjs page.html   (slow: about a second of browser time per frame)
// Needs a Chrome or Chromium binary (set CHROME=/path/to/chrome to choose one). Without one it says
// so and exits 0: this check is optional. Exit code 1 if any player fails or any text is clipped.
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const page = process.argv[2];
if (!page) { console.error("usage: node check_players.mjs page.html"); process.exit(2); }

function findChrome() {
  if (process.env.CHROME) return process.env.CHROME;
  for (const name of ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"]) {
    const r = spawnSync("which", [name], { encoding: "utf8" });
    if (r.status === 0 && r.stdout.trim()) return r.stdout.trim();
  }
  for (const p of ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]) { try { readFileSync(p); return p; } catch (e) { /* not there */ } }
  return null;
}
const chrome = findChrome();
if (!chrome) { console.log("SKIP  no Chrome or Chromium found (set CHROME=...); players not checked"); process.exit(0); }

const html = readFileSync(resolve(page), "utf8");
const frames = (html.match(/<li[^>]*class="[^"]*\bframe\b/g) || []).length;
const hasPlayers = /class="[^"]*\btimeline\b/.test(html);

const probe = `<script>
(function () {
  function wait(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function attrs(el) {
    var o = {};
    Array.prototype.forEach.call(el.attributes, function (a) { if (a.name !== "id" && a.name.indexOf("aria-") !== 0) o[a.name] = a.value; });
    return JSON.stringify(Object.keys(o).sort().map(function (k) { return [k, o[k]]; }));
  }
  function diff(a, b) {
    var n = 0, ka = Array.prototype.filter.call(a.children, function (c) { return c.tagName !== "title" && c.tagName !== "desc"; }),
        kb = Array.prototype.filter.call(b.children, function (c) { return c.tagName !== "title" && c.tagName !== "desc"; });
    if (ka.length !== kb.length) return 1 + Math.abs(ka.length - kb.length);
    for (var i = 0; i < ka.length; i++) {
      var x = ka[i], y = kb[i];
      if (x.tagName !== y.tagName || attrs(x) !== attrs(y)) { n++; continue; }
      if (!x.children.length && !y.children.length) { if (x.textContent !== y.textContent) n++; continue; }
      n += diff(x, y);
    }
    return n;
  }
  async function run() {
    var tls = Array.prototype.slice.call(document.querySelectorAll(".timeline")), out = [];
    for (var k = 0; k < tls.length; k++) {
      var tl = tls[k], fr = tl.querySelectorAll(".storyboard .frame"), n = fr.length, next = tl.querySelector('[data-act="next"]');
      var list = tl.nextElementSibling;
      while (list && !(list.classList && list.classList.contains("sync-steps"))) {
        if (list.classList && list.classList.contains("timeline")) { list = null; break; }
        list = list.nextElementSibling;
      }
      var res = { index: k + 1, frames: n, bad: [], sync: list ? "ok" : "no list", narrated: tl.classList.contains("narrated") };
      if (!next || !tl.querySelector(".stage svg")) { res.bad.push("no player built"); out.push(res); continue; }
      for (var i = 0; i < n; i++) {
        if (i > 0) { next.click(); await wait(950); }
        // compare the whole drawing, keyed or not: tags, attributes (ids aside) and text, node by node
        var stage = tl.querySelector(".stage svg"), want = fr[i].querySelector("svg"), mism = diff(stage, want);
        if (mism) res.bad.push("frame " + (i + 1) + ": " + mism + " element" + (mism === 1 ? "" : "s") + " differ from the storyboard");
        if (list) {
          var on = Array.prototype.map.call(list.querySelectorAll("li"), function (li, j) { return li.classList.contains("on") ? j : -1; }).filter(function (j) { return j >= 0; });
          if ((on.length !== 1 || on[0] !== i) && res.sync === "ok") res.sync = "frame " + (i + 1) + " lit sentence " + (on.map(function (j) { return j + 1; }).join(",") || "none");
        }
      }
      out.push(res);
    }
    document.body.setAttribute("data-player-report", encodeURIComponent(JSON.stringify(out)));
    // clipped text: open folded storyboards, then measure every visible <text> against its viewBox
    Array.prototype.forEach.call(document.querySelectorAll("details"), function (d) { d.open = true; });
    await wait(200);
    var clip = [];
    Array.prototype.forEach.call(document.querySelectorAll("svg[viewBox]"), function (svg) {
      if (svg.closest(".stage")) return;            // the stage is a copy of a storyboard frame
      var vb = svg.viewBox.baseVal;
      if (!vb || !vb.width) return;
      Array.prototype.forEach.call(svg.querySelectorAll("text"), function (t) {
        if (t.closest(".off") || !t.textContent.trim()) return;
        var b; try { b = t.getBBox(); } catch (e) { return; }
        if (!b.width) return;
        var tol = 1.5;
        if (b.x < vb.x - tol || b.y < vb.y - tol || b.x + b.width > vb.x + vb.width + tol || b.y + b.height > vb.y + vb.height + tol) {
          var fig = svg.closest("figure"), cap = fig && fig.querySelector("figcaption");
          var where = (fig && fig.id) || (cap && cap.id) || (svg.closest("[id]") || {}).id || "?";
          clip.push(where + ': "' + t.textContent.trim().slice(0, 50) + '" spans x ' + Math.round(b.x) + "–" + Math.round(b.x + b.width) + ", y " + Math.round(b.y) + "–" + Math.round(b.y + b.height) + " in a " + vb.width + " × " + vb.height + " viewBox");
        }
      });
    });
    var seen = {}; clip = clip.filter(function (c) { if (seen[c]) return false; seen[c] = 1; return true; });
    document.body.setAttribute("data-clip-report", encodeURIComponent(JSON.stringify(clip)));
  }
  setTimeout(run, 300);
})();
</script>`;

const dir = mkdtempSync(join(tmpdir(), "players-"));
const file = join(dir, "probe.html");
writeFileSync(file, '<!doctype html><html><head><meta charset="utf-8"></head><body>' + html + probe + "</body></html>");
const budget = 3000 + frames * 1000;
let dom = "";
try {
  dom = execFileSync(chrome, ["--headless=new", "--disable-gpu", "--no-sandbox", "--window-size=1200,1000", "--virtual-time-budget=" + budget, "--dump-dom", "file://" + file], { encoding: "utf8", maxBuffer: 64 * 1024 * 1024, stdio: ["ignore", "pipe", "ignore"], timeout: 240000 });
} catch (e) { console.log("SKIP  Chrome did not run (" + e.message.split("\n")[0] + ")"); process.exit(0); }
const m = dom.match(/data-player-report="([^"]*)"/);
if (!m) { console.log("ERROR the probe did not finish; a player script may have failed"); process.exit(1); }
const report = JSON.parse(decodeURIComponent(m[1]));
let failed = false;
if (!hasPlayers) console.log("OK    no players on this page");
for (const r of report) {
  const kind = r.narrated ? "narrated figure" : "timeline";
  const syncBad = r.sync !== "ok" && !(r.sync === "no list" && !r.narrated);
  if (r.bad.length || syncBad) {
    failed = true;
    console.log(`ERROR player ${r.index} (${kind}, ${r.frames} frames): ${r.bad.concat(syncBad ? ["sentences: " + r.sync] : []).join("; ")}`);
  } else {
    console.log(`OK    player ${r.index} (${kind}, ${r.frames} frames)${r.sync === "ok" ? ", sentences in sync" : ""}`);
  }
}
const mc = dom.match(/data-clip-report="([^"]*)"/);
const clipped = mc ? JSON.parse(decodeURIComponent(mc[1])) : [];
if (clipped.length) {
  failed = true;
  console.log(`ERROR ${clipped.length} SVG text label${clipped.length === 1 ? "" : "s"} run past the figure's edge (split the line or make the figure larger):`);
  clipped.slice(0, 20).forEach((c) => console.log("        " + c));
  if (clipped.length > 20) console.log(`        ... and ${clipped.length - 20} more`);
} else if (mc) {
  console.log("OK    no SVG text runs past its figure's edge");
}
process.exit(failed ? 1 : 0);
