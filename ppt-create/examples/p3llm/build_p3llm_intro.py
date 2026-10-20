#!/usr/bin/env python3
"""Worked example (Mode 1, older page style): builds the P3-LLM lab page, assets/reference/p3llm-intro.html.

Run: python3 build_p3llm_intro.py [OUT.html]      (default: ./p3llm-intro.html)
Inputs: the concept-explainer skill's template (CSS + timeline player), and the six timing frames that the
page reuses from the author's earlier DRAM explainer page ($DRAM_EXPLAINER_HTML); when that page is not at hand they are
read back from the bundled reference page, so the output equals assets/reference/p3llm-intro.html.

This page predates the prototype format of references/html-prototype.md: it is a scrolling lab page with
prose points under each figure, not a slide-by-slide prototype with band bullets and speaker notes, so its
deck (build_p3llm_deck.js) carries the slide text and notes itself and takes only the figures from here.
What it still shows well: figures drawn from a few SVG helpers in the shape vocabulary, storyboards with
keyed elements, a citation for every number, and schematic drawings and the author's own reading labelled.
Every P3-LLM number is quoted from arXiv 2511.06838v4; DRAM sizes and timings are simulator presets.
"""
import html
import os
import re

import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "p3llm-intro.html"
TEMPLATE = os.path.expanduser("~/.claude/skills/concept-explainer/assets/template.html")
EXPLAINER = os.environ.get("DRAM_EXPLAINER_HTML", "")  # the earlier DRAM explainer page, if at hand
REFERENCE = os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "reference", "p3llm-intro.html")

E = html.escape


# ---------------------------------------------------------------- SVG helpers
def _k(key):
    return f' data-key="{key}"' if key else ""


def R(x, y, w, h, cls, key=None, extra=""):
    return f'<rect{_k(key)} x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="0" class="{cls}"{extra}></rect>'


def T(x, y, s, cls="t-label", anchor="start", key=None, extra=""):
    return f'<text{_k(key)} x="{x:g}" y="{y:g}" text-anchor="{anchor}" class="{cls}"{extra}>{E(s)}</text>'


def L(x1, y1, x2, y2, cls="s-ink", key=None, mark=None):
    m = f' marker-end="url(#{mark})"' if mark else ""
    return f'<line{_k(key)} x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" class="{cls}"{m}></line>'


def PL(points, cls="s-ink f-none", key=None, mark=None):
    m = f' marker-end="url(#{mark})"' if mark else ""
    pts = " ".join(f"{x:g},{y:g}" for x, y in points)
    return f'<polyline{_k(key)} points="{pts}" class="{cls}"{m}></polyline>'


def C(cx, cy, r, cls, key=None):
    return f'<circle{_k(key)} cx="{cx:g}" cy="{cy:g}" r="{r:g}" class="{cls}"></circle>'


def svg(vb, sid, title, desc, body):
    return (f'<svg viewBox="{vb}" role="img" aria-labelledby="{sid}-t {sid}-d">'
            f'<title id="{sid}-t">{E(title)}</title><desc id="{sid}-d">{E(desc)}</desc>{body}</svg>')


def figure(fid, svgtext, caption, scroll=True):
    inner = f'<div class="diagram-scroll">{svgtext}</div>' if scroll else svgtext
    return (f'<figure class="sheet wide" aria-labelledby="{fid}-cap">{inner}'
            f'<figcaption id="{fid}-cap">{caption}</figcaption></figure>')


def frame(fid, title, desc, vb, body, caption):
    return (f'<li class="frame">{svg(vb, fid, title, desc, body)}'
            f'<p class="frame-caption">{caption}</p></li>')


def timeline(tid, frames, caption, hold=2000):
    return f'''<figure class="timeline sheet wide" data-step-word="Step" data-of-word="of" data-hold-ms="{hold}" aria-labelledby="{tid}-cap">
      <div class="player js-only">
        <div class="stage"></div>
        <p class="stage-caption" aria-live="polite"></p>
        <div class="controls">
          <button type="button" data-act="play" data-play-label="Play" data-pause-label="Pause">Play</button>
          <button type="button" data-act="prev" aria-label="Previous step">←</button>
          <button type="button" data-act="next" aria-label="Next step">→</button>
          <input type="range" class="scrub" min="0" max="1" step="1" value="0" aria-label="Step">
          <output class="counter"></output>
        </div>
      </div>
      <ol class="storyboard">
{chr(10).join(frames)}
      </ol>
      <figcaption id="{tid}-cap">{caption}</figcaption>
    </figure>'''


ON, OFF = "", " off"

# ================================================================ figures
# ---- Fig 1: the three parts of P3-LLM on its system
def fig_summary():
    b = []
    b.append(R(16, 50, 190, 170, "f-sheet s-ink"))
    b.append(T(28, 76, "Host NPU", "t-head"))
    b.append(T(28, 100, "FP16 / FP32 work:", "t-mono"))
    b.append(T(28, 120, "LayerNorm, RoPE,", "t-mono"))
    b.append(T(28, 140, "softmax, scales", "t-mono"))
    b.append(R(386, 28, 240, 222, "f-sheet s-ink"))
    b.append(T(398, 52, "HBM-PIM channel", "t-head"))
    b.append(R(400, 70, 96, 40, "f-idle s-pencil"))
    b.append(T(448, 95, "even bank", "t-mono", "middle"))
    b.append(R(400, 192, 96, 40, "f-idle s-pencil"))
    b.append(T(448, 217, "odd bank", "t-mono", "middle"))
    b.append(R(522, 110, 92, 72, "f-tint s-accent thick"))
    b.append(T(568, 140, "PCU", "t-label", "middle"))
    b.append(T(568, 162, "W4 × A8", "t-mono", "middle"))
    b.append(L(496, 98, 520, 124, "s-teal", mark="mkt"))
    b.append(L(496, 204, 520, 170, "s-teal", mark="mkt"))
    b.append(T(400, 150, "4-bit W, KV", "t-mono"))
    b.append(L(206, 104, 382, 104, "s-ink", mark="mk"))
    b.append(T(294, 96, "8-bit A, P", "t-mono", "middle"))
    b.append(L(384, 176, 210, 176, "s-ink", mark="mk"))
    b.append(T(294, 168, "32-bit sums", "t-mono", "middle"))
    # badges
    for (cx, cy, n) in ((236, 140, "1"), (528, 214, "2"), (40, 244, "3")):
        b.append(C(cx, cy, 11, "f-accent"))
        b.append(T(cx, cy + 5, n, "t-onbar", "middle"))
    b.append(T(252, 145, "W4A8KV4P8", "t-accent"))
    b.append(T(544, 219, "PCU + TEP", "t-accent"))
    b.append(T(56, 249, "fused dequantization", "t-accent"))
    b.append(T(300, 290, "arrow = data moves · numbers = the three design parts", "t-mono", "middle"))
    return svg("0 0 640 300", "f1", "P3-LLM: three design parts on an NPU plus HBM-PIM system",
               "A host NPU sends 8-bit inputs to a low-precision PCU between an even and an odd bank of an "
               "HBM-PIM channel; the banks feed 4-bit weights and KV-cache; the PCU returns 32-bit sums. "
               "Badges mark the formats on the operands, the PCU with TEP, and the fused dequantization on the NPU.",
               "".join(b))


# ---- Fig 2: DRAM hierarchy (adapted from the DRAM explainer, Fig. B1)
def fig_hierarchy():
    b = []
    b.append(R(10, 34, 270, 236, "f-sheet s-ink"))
    b.append(T(20, 56, "Channel", "t-head"))
    b.append(T(88, 56, "own command + data bus", "t-mono"))
    for g, (gx, gy) in enumerate(((18, 70), (150, 70), (18, 172), (150, 172))):
        b.append(R(gx, gy, 122, 92, "f-none " + ("s-accent" if g == 0 else "s-pencil")))
        b.append(T(gx + 6, gy + 18, f"bank group {g}", "t-mono"))
        for i, (dx, dy) in enumerate(((8, 28), (66, 28), (8, 58), (66, 58))):
            cls = "f-accent" if (g == 0 and i == 0) else "f-idle s-pencil"
            b.append(R(gx + dx, gy + dy, 48, 24, cls))
    b.append(R(300, 34, 330, 236, "f-sheet s-ink"))
    b.append(T(312, 56, "Bank (the coral one, zoomed)", "t-head"))
    for i in range(6):
        y = 70 + 16 * i
        b.append(R(316, y, 190, 12, "f-none s-accent thick" if i == 2 else "f-idle"))
    b.append(T(512, 82, "rows", "t-mono"))
    b.append(T(512, 112, "row: ACT opens", "t-accent"))
    b.append(L(400, 116, 400, 183, "s-ink", mark="mk"))
    b.append(T(408, 172, "ACT", "t-mono"))
    b.append(R(316, 186, 190, 26, "f-teal"))
    b.append(T(326, 204, "row buffer · 2,048 B", "t-onbar"))
    b.append(R(488, 186, 16, 26, "f-accent"))
    b.append(T(316, 232, "column: RD moves 32 B", "t-accent"))
    b.append(L(504, 199, 548, 199, "s-ink", mark="mk"))
    b.append(R(550, 182, 70, 34, "f-idle s-pencil"))
    b.append(T(585, 204, "BG I/O", "t-mono", "middle"))
    b.append(T(316, 256, "bank: one open row at a time", "t-mono"))
    b.append(T(10, 290, "bank group: 4 banks that share one I/O path · 16 banks per channel", "t-mono"))
    b.append(T(10, 310, "arrow = data moves · coral = what one read touches · teal = the open row", "t-mono"))
    return svg("0 24 640 296", "f2", "DRAM hierarchy: channel, bank group, bank, row, column",
               "Left: one channel holds four bank groups of four banks. Right: one bank zoomed in: ACT copies "
               "one row into the row buffer, and a read moves one 32 B column out through the bank-group I/O.",
               "".join(b))


# ---- Fig 3: ACT / RD / PRE on one bank (storyboard)
def fig_actrdpre():
    VB = "0 0 480 280"
    rows_y = [52 + 18 * i for i in range(6)]
    RY = rows_y[3]

    def scene(s):
        b = []
        b.append(T(8, 22, s["head"], "t-head", key="head"))
        b.append(R(8, 34, 72, 28, s.get("cmdcls", "f-sheet s-pencil"), key="cmdbox"))
        b.append(T(44, 54, s["cmd"], s.get("cmdt", "t-mono"), "middle", key="cmdtxt"))
        b.append(T(90, 112, "row", "t-mono", "end"))
        b.append(T(90, 130, "decoder", "t-mono", "end"))
        b.append(R(96, 50, 20, 106, s.get("rdec", "f-idle s-pencil"), key="rdec"))
        b.append(T(124, 44, "bank array (rows)", "t-mono"))
        for i, y in enumerate(rows_y):
            if i == 3:
                b.append(R(124, y, 220, 12, s.get("row", "f-idle"), key="rowr"))
            else:
                b.append(R(124, y, 220, 12, "f-idle"))
        b.append(T(350, RY + 11, "row r", s.get("rowlbl", "t-mono"), key="rowlbl"))
        b.append(L(116, RY + 6, 344, RY + 6, s.get("wl", "s-accent thick off"), key="wl"))
        b.append(L(234, RY + 14, 234, 176, s.get("copy", "s-accent off"), key="copy", mark="mka"))
        b.append(R(124, 180, 220, 26, s.get("sa", "f-idle s-pencil"), key="sa"))
        b.append(T(132, 198, s.get("satxt", "row buffer: empty"), s.get("sat", "t-mono"), key="satxt"))
        b.append(R(s.get("colx", 300), 180, 20, 26, s.get("col", "f-accent off"), key="col"))
        b.append(L(344, 193, 376, 193, s.get("a1", "s-accent off"), key="a1", mark="mka"))
        b.append(R(380, 178, 90, 30, s.get("bgio", "f-sheet s-ink"), key="bgio"))
        b.append(T(425, 198, "BG I/O", "t-mono", "middle"))
        b.append(L(425, 208, 425, 220, s.get("a2", "s-accent off"), key="a2", mark="mka"))
        b.append(R(380, 222, 90, 28, s.get("bus", "f-sheet s-ink"), key="bus"))
        b.append(T(425, 241, "data bus", "t-mono", "middle"))
        b.append(T(8, 272, s["note"], "t-mono", key="note"))
        return "".join(b)

    hot = dict(cmdcls="f-tint s-accent thick", cmdt="t-accent")
    openrow = dict(row="f-teal", wl="s-teal thick", sa="f-teal", satxt="row buffer: row r", sat="t-onbar")
    S = [
        dict(head="Before: every row is closed", cmd="—", note="row buffer empty; bitlines precharged"),
        dict(head="ACT opens row r", cmd="ACT", **hot, rdec="f-accent", row="f-tint s-accent thick",
             rowlbl="t-accent", wl="s-accent thick", copy="s-accent", sa="f-teal", satxt="row buffer: row r",
             sat="t-onbar", note="the whole row (2,048 B here) enters the buffer"),
        dict(head="RD moves one column out", cmd="RD", **hot, **openrow, col="f-accent", colx=300,
             a1="s-accent", a2="s-accent", bgio="f-tint s-accent", bus="f-tint s-accent",
             note="one column (32 B here) leaves, CL later"),
        dict(head="RD again: next column", cmd="RD", **hot, **openrow, col="f-accent", colx=322,
             a1="s-accent", a2="s-accent", bgio="f-tint s-accent", bus="f-tint s-accent",
             note="same open row: no new ACT needed"),
        dict(head="PRE closes the row", cmd="PRE", **hot, note="the next ACT to this bank waits tRP"),
    ]
    caps = [
        "Before any command, every row of the bank is closed and the row buffer is empty.",
        "ACT makes the row decoder raise one wordline, and the sense amplifiers copy that whole row into the row buffer.",
        "RD picks one column of the open row; it leaves through the bank-group I/O and reaches the data bus CL later.",
        "A second RD reads another column of the same open row, with no new ACT.",
        "PRE closes the row: the sense amplifiers let go and the bitlines precharge for the next ACT.",
    ]
    titles = ["Idle", "ACT", "RD", "RD again", "PRE"]
    frames = [frame(f"cf{i+1}", f"Frame {i+1}: {titles[i]}", caps[i], VB, scene(s), caps[i])
              for i, s in enumerate(S)]
    return timeline("tl3", frames,
                    "Figure 3. One bank, five steps. Coral = the path the current command uses; teal = the row "
                    "held in the row buffer; arrows = data moves. Sizes are one simulator preset (LPDDR5-6400 AiM). "
                    "The figure leaves out timing; slide 4 adds it.", hold=2200)


# ---- Fig 4: timing rules = the DRAM explainer's Figure B2 frames, reused
def _markers_to_axis(fr):
    """The rule markers (g0-g2) of one timing frame start at the lane of the command they mark and stop at the time
    axis (y 184): from y 40 to 208 they ran through the other lane's command labels and the tick numbers. The
    bracket under the tick numbers still spans the same two times. Same keys on every frame (Morph); idempotent."""
    cmds = [(float(x), float(y)) for x, y in
            re.findall(r'<g data-key="\w+" class="cmd(?: hot| pend)?" transform="translate\(([\d.]+) ([\d.]+)\)">', fr)]

    def fix(m):
        x = float(m.group(2))
        lanes = {y for cx, y in cmds if abs(cx - x) < 0.2}
        y1 = 90.0 if lanes == {94.0} else 40.0  # a BG 1 command: start below the BG 0 lane
        return f'{m.group(1)}y1="{y1:.1f}" x2="{m.group(3)}" y2="184.0"'
    return re.sub(r'(<line data-key="g\d" x1="([\d.]+)" )y1="[\d.]+" x2="([\d.]+)" y2="[\d.]+"', fix, fr)


def fig_timing():
    if EXPLAINER and os.path.isfile(EXPLAINER):
        src = open(EXPLAINER, encoding="utf-8").read()
        frames = re.findall(r'<li class="frame"><svg viewBox="0 0 480 250" role="img" aria-labelledby="rd\d-title.*?</li>',
                            src, re.S)
    else:  # the same six frames, already renamed, from the bundled reference page
        src = open(REFERENCE, encoding="utf-8").read()
        frames = re.findall(r'<li class="frame"><svg viewBox="0 0 480 250" role="img" aria-labelledby="b2f\d-title.*?</li>',
                            src, re.S)
    assert len(frames) == 6, len(frames)
    frames = [_markers_to_axis(re.sub(r'\brd(\d)-(title|desc)\b', r'b2f\1-\2', f)) for f in frames]
    return timeline("tl4", frames,
                    "Figure 4. Commands to one bank in bank group 0 and one in bank group 1, to scale in ns. "
                    "Timings are simulator presets (LPDDR5-6400 AiM in Ramulator 2.0), not JEDEC values. Lanes: "
                    "BG 0 and BG 1 (boxes = commands, teal = row open) and the data bus (bursts). Coral marks each "
                    "step's change and the rule that places it. Frames 4 and 5 are two alternatives for the second "
                    "read. Adapted from our earlier DRAM explainer (Fig. B2).", hold=2400)


# ---- Fig 5: tCCD_S vs tCCD_L
def fig_tccd():
    b = []
    b.append(T(10, 24, "why: shared I/O path", "t-head"))
    for g, gx in ((0, 16), (1, 156)):
        b.append(R(gx, 36, 124, 96, "f-none s-pencil"))
        b.append(T(gx + 6, 54, f"bank group {g}", "t-mono"))
        for dx, dy in ((8, 64), (66, 64), (8, 98), (66, 98)):
            b.append(R(gx + dx, dy, 50, 24, "f-idle s-pencil"))
        b.append(R(gx, 146, 124, 24, "f-tint s-accent"))
        b.append(T(gx + 62, 163, f"BG {g} I/O", "t-mono", "middle"))
        b.append(L(gx + 62, 132, gx + 62, 144, "s-ink", mark="mk"))
        b.append(L(gx + 62, 170, gx + 62, 196, "s-ink", mark="mk"))
    b.append(R(16, 200, 264, 26, "f-sheet s-ink"))
    b.append(T(148, 218, "channel I/O → data bus", "t-mono", "middle"))
    b.append(T(16, 250, "4 banks of a group share one path", "t-mono"))
    # right: two timelines, 13 px per ns from x0 = 352
    x0, k = 352, 13

    def X(t):
        return x0 + k * t
    for (y, lab, t2, rule) in ((40, "(a) same bank group", 5.0, "tCCD_L 5 ns"),
                               (160, "(b) different bank groups", 2.5, "tCCD_S 2.5 ns")):
        b.append(T(318, y - 12, lab, "t-head"))
        b.append(T(318, y + 15, "cmd", "t-mono"))
        b.append(T(318, y + 55, "bus", "t-mono"))
        b.append(L(x0 - 4, y + 24, 620, y + 24, "s-pencil"))
        b.append(L(x0 - 4, y + 64, 620, y + 64, "s-pencil"))
        for t, cls in ((0, "f-sheet s-ink"), (t2, "f-tint s-accent")):
            b.append(R(X(t), y, 28, 20, cls))
            b.append(T(X(t) + 14, y + 15, "RD", "t-mono", "middle"))
        b.append(R(X(12.5), y + 40, k * 2.5, 22, "f-ink"))
        b.append(R(X(12.5 + t2), y + 40, k * 2.5, 22, "f-accent"))
        b.append(L(X(0), y + 84, X(t2), y + 84, "s-accent thick"))
        b.append(T(X(t2) + 6, y + 89, rule, "t-accent"))
    for t in (0, 5, 10, 15, 20):
        b.append(T(X(t), 290, f"{t}" + (" ns" if t == 20 else ""), "t-mono", "middle"))
    return svg("0 0 640 300", "f5", "tCCD_L versus tCCD_S",
               "Left: each bank group has one shared I/O path into the channel I/O. Right: two reads to the same "
               "bank group must be tCCD_L = 5 ns apart and leave a gap on the bus; two reads to different bank "
               "groups need only tCCD_S = 2.5 ns and their bursts touch.", "".join(b))


# ---- Fig 6: stock AiM MAC run (storyboard), adapted from the DRAM explainer, Fig. B3
def fig_aim():
    VB = "0 0 480 290"
    cmds = [("WRGB", ""), ("WRMAC16", ""), ("TMOD", ""), ("PREA", "ACT16"), ("MAC16", "×c"), ("TMOD", ""),
            ("RDMAC16", "")]
    widths = [48, 74, 48, 58, 58, 48, 74]

    def scene(i, s):
        b = []
        x = 12
        for j, ((a, c), w) in enumerate(zip(cmds, widths)):
            st = "cmd hot" if j == i else ("cmd" if j < i else "cmd pend")
            b.append(f'<g data-key="k{j}" class="{st}">' + R(x, 18, w, 44, "f-sheet s-ink")
                     + T(x + w / 2, 36, a, "t-mono", "middle") + T(x + w / 2, 55, c, "t-mono", "middle") + "</g>")
            x += w + 8
        b.append(T(8, 86, s["mode"], "t-mono", key="mode"))
        b.append(R(8, 100, 70, 160, "f-sheet s-ink"))
        b.append(T(43, 122, "host", "t-label", "middle"))
        b.append(R(120, 96, 130, 50, s.get("gb", "f-idle s-pencil"), key="gb"))
        b.append(T(128, 116, "global buffer", "t-mono"))
        b.append(T(128, 138, s.get("gbs", "empty"), "t-mono", key="gbs"))
        b.append(R(120, 166, 130, 72, "f-none s-pencil"))
        b.append(T(128, 186, "16 banks", "t-mono"))
        b.append(T(128, 206, s.get("bks", "rows closed"), "t-mono", key="bks"))
        b.append(R(128, 216, 114, 14, s.get("row", "f-idle"), key="row"))
        b.append(R(200, 216, 10, 14, s.get("col", "f-accent off"), key="col"))
        b.append(R(280, 136, 70, 60, s.get("pu", "f-sheet s-ink"), key="pu"))
        b.append(T(315, 160, "16 PUs", "t-mono", "middle"))
        b.append(T(315, 182, "× and Σ", "t-mono", "middle"))
        b.append(R(376, 136, 96, 60, s.get("mr", "f-idle s-pencil"), key="mr"))
        b.append(T(424, 158, "MAC regs", "t-mono", "middle"))
        b.append(T(424, 182, s.get("mrs", "—"), "t-mono", "middle", key="mrs"))
        b.append(L(78, 120, 116, 120, s.get("awg", "s-accent off"), key="awg", mark="mka"))
        b.append(PL([(78, 250), (424, 250), (424, 200)], s.get("awm", "s-accent f-none off"), key="awm", mark="mka"))
        b.append(PL([(424, 198), (424, 250), (82, 250)], s.get("ard", "s-accent f-none off"), key="ard", mark="mka"))
        b.append(L(250, 130, 278, 152, s.get("m1", "s-accent off"), key="m1", mark="mka"))
        b.append(L(250, 216, 278, 184, s.get("m2", "s-accent off"), key="m2", mark="mka"))
        b.append(L(350, 166, 374, 166, s.get("m3", "s-accent off"), key="m3", mark="mka"))
        b.append(T(8, 282, s["note"], "t-mono", key="note"))
        return "".join(b)

    reg, arr = "mode: register access", "mode: array (MAC)"
    full = dict(gb="f-none s-teal thick", gbs="input slice")
    S = [
        dict(mode=reg, gb="f-tint s-accent", gbs="input slice", awg="s-accent",
             note="host → GB: one 32 B burst on the data bus"),
        dict(mode=reg, **full, mr="f-none s-mustard thick", mrs="bias or 0", awm="s-accent f-none",
             note="host → 16 MAC registers: bias or zero"),
        dict(mode=arr, **full, mr="f-none s-mustard thick", mrs="bias or 0", note="register access → array mode"),
        dict(mode=arr, **full, mr="f-none s-mustard thick", mrs="bias or 0", row="f-teal", bks="one row open",
             note="PREA closes rows; ACT16 opens one in all 16"),
        dict(mode=arr, **full, row="f-teal", bks="one row open", col="f-accent", pu="f-tint s-accent thick",
             mr="f-tint s-accent", mrs="summing", m1="s-accent", m2="s-accent", m3="s-accent",
             note="per bank: 32 B column + 32 B GB → PU → MAC reg"),
        dict(mode=reg, **full, row="f-teal", bks="one row open", mr="f-none s-mustard thick", mrs="sums ready",
             note="array → register access mode"),
        dict(mode=reg, **full, row="f-teal", bks="one row open", mr="f-idle s-pencil", mrs="sent",
             ard="s-accent f-none", note="16 MAC registers → host on the data bus"),
    ]
    caps = [
        "WRGB writes one 32 B burst of the input vector from the host into the global buffer (GB).",
        "WRMAC16 writes the bias, or zero, from the host into all 16 MAC registers.",
        "TMOD switches the channel from register-access mode to array mode.",
        "PREA closes any open rows, and ACT16 opens the same row in all 16 banks.",
        "Each MAC16 reads one 32 B column from every bank; the GB broadcasts one 32 B input slice; every PU "
        "multiplies, sums in its adder tree and adds into its MAC register. Nothing crosses the data bus. The host "
        "sends c MAC16s, one per column, tCCD_L apart.",
        "TMOD switches the channel back to register-access mode.",
        "RDMAC16 sends the 16 MAC registers to the host over the data bus.",
    ]
    titles = ["WRGB", "WRMAC16", "TMOD", "PREA and ACT16", "MAC16 ×c", "TMOD", "RDMAC16"]
    frames = [frame(f"af{i+1}", f"Frame {i+1}: {titles[i]}", caps[i], VB, scene(i, s), caps[i])
              for i, s in enumerate(S)]
    return timeline("tl6", frames,
                    "Figure 6. One accumulation run of stock AiM on one channel. Top: the command strip (gray = still "
                    "to come; coral outline = this step). Bottom: the parts each command changes; arrows = data moves. "
                    "Schematic, not to scale: the c MAC16 commands take most of the time. The figure leaves out "
                    "refresh and the exact interleaving. Adapted from our earlier DRAM explainer (Fig. B3, Table B2).",
                    hold=2400)


# ---- Background (the paper's §II), figure 1 of 4: LLM decoding, after the paper's Fig. 1(a)
def fig_llm():
    b = []
    b.append(T(8, 18, "prefill: the N_T-token prompt at once", "t-mono"))
    b.append(R(8, 28, 88, 36, "f-sheet s-ink"))
    b.append(T(52, 51, "prompt", "t-mono", "middle"))
    b.append(L(96, 46, 110, 46, "s-ink", mark="mk"))
    b.append(R(112, 28, 104, 36, "f-idle s-pencil"))
    b.append(T(164, 51, "embedding", "t-mono", "middle"))
    b.append(L(216, 46, 230, 46, "s-ink", mark="mk"))
    b.append(R(240, 22, 132, 36, "f-idle s-pencil"))
    b.append(R(234, 28, 132, 36, "f-tint s-accent thick"))
    b.append(T(300, 51, "decoder layer", "t-label", "middle"))
    b.append(T(380, 51, "× L", "t-accent"))
    b.append(L(410, 46, 424, 46, "s-ink", mark="mk"))
    b.append(R(426, 28, 92, 36, "f-idle s-pencil"))
    b.append(T(472, 51, "LM head", "t-mono", "middle"))
    b.append(L(518, 46, 532, 46, "s-ink", mark="mk"))
    b.append(R(534, 28, 98, 36, "f-sheet s-accent thick"))
    b.append(T(583, 51, "new token", "t-mono", "middle"))
    b.append(PL([(583, 64), (583, 86), (164, 86), (164, 68)], "s-accent thick f-none", mark="mka"))
    b.append(T(632, 108, "decode: each new token goes back in, one per step", "t-accent", "end"))
    # one decoder layer, zoomed
    b.append(R(8, 122, 624, 122, "f-none s-pencil dashed"))
    b.append(T(18, 142, "inside one decoder layer", "t-head"))
    ops = [(18, 112, "W_Q, W_K, W_V"), (144, 64, "RoPE"), (222, 56, "Q·Kᵀ"), (292, 74, "softmax"),
           (380, 50, "P·V"), (444, 48, "W_O"), (506, 126, "MLP")]
    for i, (x, w, lab) in enumerate(ops):
        lin = lab.startswith("W_") or lab == "MLP"
        b.append(R(x, 152, w, 26, "f-sheet s-ink" if lin else "f-idle s-pencil"))
        b.append(T(x + w / 2, 170, lab, "t-mono", "middle"))
        if i < len(ops) - 1:
            b.append(L(x + w, 165, ops[i + 1][0] - 2, 165, "s-ink", mark="mk"))
    b.append(T(624, 198, "W_gate, W_up, W_down", "t-mono", "end"))
    b.append(PL([(74, 178), (74, 222), (220, 222)], "s-teal f-none", mark="mkt"))
    b.append(T(84, 216, "new V", "t-mono"))
    b.append(PL([(176, 178), (176, 210), (220, 210)], "s-teal f-none", mark="mkt"))
    b.append(T(184, 204, "K", "t-mono"))
    b.append(R(222, 204, 208, 26, "f-teal"))
    b.append(T(326, 222, "KV-cache: all past K, V", "t-onbar", "middle"))
    b.append(L(250, 204, 250, 180, "s-teal", mark="mkt"))
    b.append(L(405, 204, 405, 180, "s-teal", mark="mkt"))
    return svg("0 0 640 248", "fb1", "LLM inference: prefill, decoding and one decoder layer",
               "Top: the prompt passes through the embedding table, L decoder layers and the LM head to give a new "
               "token; in decoding each new token goes back in. Bottom: one decoder layer: the Q, K and V "
               "projections, RoPE, Q times K transpose, softmax, P times V, the output projection and the MLP; the new "
               "key after RoPE and the new value enter the KV-cache, which feeds Q times K transpose and P times V.", "".join(b))


# ---- Background, figure 2 of 4: multi-head vs grouped-query attention, after the paper's Fig. 1(b)
def fig_gqa():
    b = []
    for px, title, gqa in ((8, "multi-head attention (MHA)", False), (328, "grouped-query attention (GQA)", True)):
        b.append(R(px, 8, 304, 220, "f-none s-pencil"))
        b.append(T(px + 12, 30, title, "t-head"))
        for lab, y in (("Q", 46), ("K", 110), ("V", 146)):
            b.append(T(px + 12, y + 18, lab, "t-head"))
        qx = [px + 36 + 33 * i for i in range(8)]
        for i, x in enumerate(qx):
            b.append(R(x, 46, 29, 26, "f-idle s-pencil"))
            b.append(T(x + 14.5, 64, f"q{i}", "t-mono", "middle"))
        if gqa:
            kx = [(px + 36 + 66 * j, 62) for j in range(4)]
        else:
            kx = [(x, 29) for x in qx]
        for j, (x, w) in enumerate(kx):
            b.append(R(x, 110, w, 26, "f-teal"))
            b.append(T(x + w / 2, 128, f"k{j}", "t-onbar", "middle"))
            b.append(R(x, 146, w, 26, "f-mustard"))
            b.append(T(x + w / 2, 164, f"v{j}", "t-onbar", "middle"))
        for i, x in enumerate(qx):
            kxj, kw = kx[i // 2] if gqa else kx[i]
            b.append(L(x + 14.5, 72, kxj + kw / 2, 108, "s-pencil"))
        if gqa:
            b.append(T(px + 12, 198, "N_A = 8, N_KV = 4: G = N_A / N_KV = 2", "t-mono"))
            b.append(T(px + 12, 218, "KV-cache: G× smaller", "t-accent"))
        else:
            b.append(T(px + 12, 198, "N_A = N_KV = 8 heads", "t-mono"))
            b.append(T(px + 12, 218, "KV-cache: 8 K, V heads per token", "t-mono"))
    return svg("0 0 640 236", "fb2", "Multi-head attention and grouped-query attention",
               "Left: eight query heads, each with its own key and value head. Right: eight query heads share four "
               "key and value heads, two query heads per key-value head, so the KV-cache is two times smaller.",
               "".join(b))


# ---- Background, figure 3 of 4: PIM for LLM decoding, after the paper's Fig. 2
def fig_pim():
    b = []
    b.append(T(8, 18, "one PIM channel (coral = PCU)", "t-head"))
    for g, (gx, gy) in enumerate(((8, 28), (152, 28), (8, 150), (152, 150))):
        b.append(R(gx, gy, 136, 88, "f-none s-pencil"))
        b.append(T(gx + 6, gy + 15, f"bank group {g}", "t-mono"))
        for dx, dy in ((6, 22), (70, 22), (6, 55), (70, 55)):
            b.append(R(gx + dx, gy + dy, 60, 18, "f-idle s-pencil"))
            b.append(T(gx + dx + 30, gy + dy + 14, "bank", "t-mono", "middle"))
            b.append(R(gx + dx, gy + dy + 18, 60, 12, "f-tint s-accent"))
    b.append(R(8, 122, 280, 22, "f-teal"))
    b.append(T(148, 138, "peripheral + global buffer (GB)", "t-onbar", "middle"))
    # the two PCU designs
    b.append(R(304, 8, 328, 112, "f-sheet s-ink"))
    b.append(T(316, 30, "Samsung HBM-PIM: SIMD", "t-head"))
    b.append(R(316, 44, 84, 26, "f-mustard"))
    b.append(T(358, 62, "input reg", "t-onbar", "middle"))
    b.append(L(400, 57, 414, 57, "s-ink", mark="mk"))
    b.append(R(416, 44, 112, 26, "f-tint s-accent"))
    b.append(T(472, 62, "16 × FP16 mul", "t-mono", "middle"))
    b.append(L(528, 57, 540, 57, "s-ink", mark="mk"))
    b.append(R(542, 44, 82, 26, "f-idle s-pencil"))
    b.append(T(583, 62, "FP32 acc", "t-mono", "middle"))
    b.append(T(316, 92, "weights: 16 × 16 bit from the bank", "t-mono"))
    b.append(T(316, 112, "input reuse: one input × 16 weights", "t-accent"))
    b.append(R(304, 132, 328, 112, "f-sheet s-ink"))
    b.append(T(316, 154, "SK hynix AiM: adder tree", "t-head"))
    b.append(R(316, 168, 60, 26, "f-teal"))
    b.append(T(346, 186, "GB", "t-onbar", "middle"))
    b.append(L(376, 181, 388, 181, "s-ink", mark="mk"))
    b.append(R(390, 168, 112, 26, "f-tint s-accent"))
    b.append(T(446, 186, "16 × BF16 mul", "t-mono", "middle"))
    b.append(L(502, 181, 514, 181, "s-ink", mark="mk"))
    b.append(R(516, 168, 108, 26, "f-idle s-pencil"))
    b.append(T(570, 186, "adder tree", "t-mono", "middle"))
    b.append(T(316, 216, "weights: 16 × 16 bit; input from the GB", "t-mono"))
    b.append(T(316, 236, "output reuse: 16 products → one sum", "t-accent"))
    return svg("0 0 640 250", "fb3", "PIM for LLM decoding: HBM-PIM and AiM",
               "Left: one PIM channel with four bank groups of four banks, a PIM compute unit at each bank, and the "
               "peripheral logic with the global buffer in the middle. Right: HBM-PIM's PCU, an input register and "
               "16 FP16 multipliers with FP32 accumulators, reuses one input across 16 weights; AiM's PCU, fed from "
               "the global buffer, has 16 BF16 multipliers and an adder tree that sums 16 products into one output.",
               "".join(b))


# ---- Background, figure 4 of 4: quantization, Eq. 1 of the paper, with an example of our own
def fig_quant():
    b = []
    boxes = [(8, 110, "X: a group"), (134, 156, "Δ = |X|max / Q_max"), (306, 188, "X_Q = Round(X / Δ, Q)"),
             (510, 122, "X̃ = X_Q · Δ")]
    for i, (x, w, lab) in enumerate(boxes):
        b.append(R(x, 14, w, 34, "f-tint s-accent" if i == 2 else "f-sheet s-ink"))
        b.append(T(x + w / 2, 36, lab, "t-mono", "middle"))
        if i < 3:
            b.append(L(x + w, 31, boxes[i + 1][0] - 2, 31, "s-ink", mark="mk"))
    for x, lab in ((63, "operands"), (212, "scale"), (400, "quantize"), (571, "dequantize")):
        b.append(T(x, 68, lab, "t-mono", "middle"))
    # the number line: X / Δ above, the nearest value of Q below (example: Q = integers -7 ... 7)
    def X(v):
        return 340 + 38 * v
    b.append(T(8, 104, "example: Q = the integers −7 … 7, so Q_max = 7", "t-mono"))
    b.append(T(8, 145, "X / Δ", "t-mono"))
    b.append(T(8, 201, "X_Q", "t-mono"))
    b.append(L(60, 140, 620, 140, "s-pencil"))
    b.append(L(60, 196, 620, 196, "s-ink"))
    for k in range(-7, 8):
        b.append(L(X(k), 190, X(k), 202, "s-ink"))
    for k, lab in ((-7, "−7"), (0, "0")):
        b.append(T(X(k), 220, lab, "t-mono", "middle"))
    b.append(T(632, 220, "Q_max = 7", "t-mono", "end"))
    for v in (-7.0, -4.6, -2.3, -0.4, 1.3, 2.8, 3.6, 5.2):
        q = round(v)
        b.append(L(X(v), 145, X(q), 190, "s-accent dashed"))
        b.append(C(X(v), 140, 5, "f-idle s-pencil"))
        b.append(C(X(q), 196, 5, "f-accent"))
    b.append(T(X(-7), 128, "largest |X| → −Q_max", "t-mono"))
    b.append(T(632, 238, "dashed: each value rounds to its nearest Q value", "t-mono", "end"))
    return svg("0 0 640 246", "fb4", "Quantization and dequantization, Eq. 1",
               "Top: a group of operands X gets a scale Delta equal to its largest magnitude over Q_max; each value of "
               "X over Delta is rounded to the closest value of the set Q, and multiplying back by Delta gives the "
               "dequantized operand. Bottom: an example with Q the integers from minus 7 to 7; dashed lines join each "
               "scaled value to the integer it rounds to.", "".join(b))


# ---- Fig 8: roofline after the paper's Fig. 4
def fig_roofline():
    x0, x1, y0, y1 = 70, 610, 300, 76
    IMAX, PMAX = 36.0, 11.0

    def X(i):
        return x0 + (x1 - x0) * i / IMAX

    def Y(p):
        return y0 - (y0 - y1) * p / PMAX
    b = []
    for p in (0, 2, 4, 6, 8, 10):
        b.append(L(x0, Y(p), x1, Y(p), "s-pencil dashed grid" if p else "s-ink"))
        b.append(T(x0 - 8, Y(p) + 5, str(p), "t-mono", "end"))
    for i in (0, 5, 10, 15, 20, 25, 30, 35):
        b.append(T(X(i), y0 + 20, str(i), "t-mono", "middle"))
    b.append(L(x0, y0, x0, y1, "s-ink"))
    b.append(T((x0 + x1) / 2, y0 + 42, "arithmetic intensity (operations per byte)", "t-mono", "middle"))
    b.append(T(14, 70, "TOPS", "t-mono"))
    # NPU line, 0.307 TOPS per op/byte, clipped at the top
    b.append(L(X(0), Y(0), X(PMAX / 0.307), Y(PMAX), "s-pencil thick"))
    b.append(T(X(24), Y(24 * 0.307) + 22, "NPU 307 GB/s", "t-mono"))
    # P3-LLM roof
    b.append(PL([(X(0), Y(0)), (X(9.84 / 1.23), Y(9.84)), (X(IMAX), Y(9.84))], "s-accent thick f-none"))
    b.append(T(X(12), Y(9.84) - 10, "P3-LLM roof 9.84 TOPS", "t-accent"))
    # HBM-PIM roof
    b.append(PL([(X(0), Y(0)), (X(1), Y(1.23)), (X(IMAX), Y(1.23))], "s-teal thick f-none"))
    b.append(T(X(20), Y(1.23) + 20, "HBM-PIM roof 1.23 TOPS", "t-label"))
    # beside the knee, under the roof: on the slope it ran across the GQA G8 guide and the 6 TOPS gridline
    b.append(T(X(8) + 8, Y(8.9) + 9, "slope 1.23 TB/s", "t-mono"))
    # approximate operator positions (read from Fig. 4)
    for (i, lab, ly) in ((1, "MHA BS1", 22), (4, "GQA G4 BS4", 40), (8, "GQA G8 BS8", 58)):
        b.append(L(X(i), y0, X(i), ly + 4, "s-mustard dashed"))
        b.append(C(X(i), Y(1.23), 5, "f-mustard"))
        b.append(T(X(i) + 4, ly, lab, "t-mono"))
    return svg("0 0 640 355", "f8", "Roofline of HBM-PIM, P3-LLM and the NPU",
               "HBM-PIM's compute roof is 1.23 TOPS with 1.23 TB/s inside, so its corner sits near 1 operation "
               "per byte. Multi-head attention at batch 1 sits there; GQA with batch 4 or 8 sits far to the right, "
               "where HBM-PIM is capped. P3-LLM's roof is 8 times higher, 9.84 TOPS.", "".join(b))


# ---- Fig 9: operand quadrant
def fig_quadrant():
    b = []
    b.append(L(100, 260, 620, 260, "s-ink", mark="mk"))
    b.append(L(100, 260, 100, 20, "s-ink", mark="mk"))
    b.append(T(620, 282, "memory footprint (Fig. 3a) →", "t-mono", "end"))
    b.append(T(92, 30, "fragile", "t-mono", "end"))
    b.append(T(92, 250, "robust", "t-mono", "end"))
    b.append(T(14, 140, "sensitivity", "t-mono"))
    b.append(T(14, 158, "(Fig. 3b)", "t-mono"))
    b.append(L(384, 30, 384, 250, "s-pencil dashed"))
    b.append(L(110, 140, 610, 140, "s-pencil dashed"))
    b.append(R(116, 40, 256, 88, "f-tint s-accent"))
    b.append(T(132, 64, "8 bits", "t-accent"))
    b.append(T(132, 88, "A  activations · FP8-E4M3", "t-mono"))
    b.append(T(132, 110, "P  attention scores · FP8-S0E4M4", "t-mono"))
    b.append(R(396, 152, 222, 88, "f-none s-teal thick"))
    b.append(T(408, 176, "4 bits", "t-head"))
    b.append(T(408, 200, "W  weights · BitMoD FP4", "t-mono"))
    b.append(T(408, 222, "KV KV-cache · INT4-Asym", "t-mono"))
    b.append(T(396, 64, "large and fragile: none", "t-mono"))
    b.append(T(120, 200, "small and robust: none", "t-mono"))
    return svg("0 0 640 295", "f9", "Where each operand sits: footprint against sensitivity",
               "Activations and attention scores are small but fragile, so they keep 8 bits. Weights and the "
               "KV-cache are large but robust, so they drop to 4 bits.", "".join(b))


# ---- Fig 10: key smoothing (schematic) and INT4-Asym group
def fig_kv():
    b = []
    before = [0.5, 0.4, 0.6, 3.6, 0.5, 0.45, 0.55, 0.4, 0.5, 0.6, 3.1, 0.5, 0.4, 0.55, 0.5, 0.45]
    maxes = [0.8, 0.7, 0.9, 4.0, 0.8, 0.7, 0.9, 0.7, 0.8, 0.9, 3.6, 0.8, 0.7, 0.9, 0.8, 0.7]
    for panel, (px, title) in enumerate(((20, "before: |K| per channel"), (340, "after: K / prefill max"))):
        b.append(T(px, 26, title, "t-head"))
        b.append(L(px, 190, px + 280, 190, "s-ink"))
        for c in range(16):
            v = before[c] if panel == 0 else before[c] / maxes[c]
            h = v * 34 if panel == 0 else v * 120
            outlier = c in (3, 10)
            cls = ("f-accent" if outlier else "f-pencil-ish") if panel == 0 else "f-teal"
            cls = cls.replace("f-pencil-ish", "f-idle s-pencil")
            b.append(R(px + 6 + 17 * c, 190 - h, 12, h, cls))
        b.append(T(px, 208, "channels →", "t-mono"))
    b.append(L(340, 70, 620, 70, "s-accent dashed"))
    b.append(T(620, 64, "1", "t-accent", "end"))
    b.append(T(20, 64, "2 outlier channels", "t-accent"))
    # INT4-Asym group strip
    b.append(R(20, 232, 330, 26, "f-idle s-pencil"))
    b.append(T(30, 250, "128 values × 4 bit (one head)", "t-mono"))
    b.append(R(354, 232, 120, 26, "f-mustard"))
    b.append(T(414, 250, "16-bit scale", "t-onbar", "middle"))
    b.append(R(478, 232, 144, 26, "f-teal"))
    b.append(T(550, 250, "4-bit zero point", "t-onbar", "middle"))
    b.append(T(20, 282, "INT4-Asym group: 4.16 bits per value in effect (Oaken: about 4.8)", "t-mono"))
    return svg("0 0 640 292", "f10", "Dynamic key smoothing and the INT4-Asym group",
               "Left: two key channels are far larger than the rest. Right: after each channel is divided by its "
               "prefill maximum, every channel fits under 1. Bottom: 128 four-bit values share a 16-bit scale and a "
               "4-bit zero point. Bar heights are schematic.", "".join(b))


# ---- Fig 11: bit layouts
def fig_bits():
    b = []
    rows = [("FP16", "s" + "e" * 5 + "m" * 10, 40),
            ("FP8-E4M3", "s" + "e" * 4 + "m" * 3, 110),
            ("FP8-S0E4M4", "e" * 4 + "m" * 4, 180)]
    cls = {"s": "f-mustard", "e": "f-teal", "m": "f-idle s-pencil"}
    tcls = {"s": "t-onbar", "e": "t-onbar", "m": "t-mono"}
    for name, bits, y in rows:
        b.append(T(14, y + 20, name, "t-head"))
        for i, ch in enumerate(bits):
            x = 150 + 26 * i
            c = cls[ch]
            if name == "FP8-S0E4M4" and i == 7:
                c = "f-accent"
            b.append(R(x, y, 24, 28, c))
            b.append(T(x + 12, y + 19, ch, tcls[ch] if c != "f-accent" else "t-onbar", "middle"))
    b.append(T(150, 98, "activations (§IV-D)", "t-mono"))
    b.append(T(150, 168, "attention scores (§IV-B)", "t-mono"))
    b.append(T(372, 190, "no sign: scores are ≥ 0", "t-mono"))
    b.append(T(372, 208, "bias −15 → 2⁻¹⁴ … 2⁻¹", "t-mono"))
    b.append(T(372, 226, "coral: 4th mantissa bit", "t-accent"))
    b.append(T(14, 252, "s = sign · e = exponent · m = mantissa", "t-mono"))
    return svg("0 0 640 262", "f11", "Bit layouts of FP16, FP8-E4M3 and FP8-S0E4M4",
               "FP16 has 1 sign, 5 exponent and 10 mantissa bits. FP8-E4M3 has 1 sign, 4 exponent and 3 mantissa "
               "bits. FP8-S0E4M4 has no sign bit, 4 exponent bits with bias minus 15, and 4 mantissa bits.",
               "".join(b))


# ---- Fig 12: BitMoD number line
def fig_bitmod():
    b = []
    cx, k = 320, 36

    def X(v):
        return cx + k * v
    b.append(L(X(-8.4), 100, X(8.4), 100, "s-ink"))
    vals = [0.5, 1, 1.5, 2, 3, 4, 6]
    for v in vals:
        for s in (1, -1):
            b.append(C(X(s * v), 100, 5, "f-ink"))
    b.append(C(X(0), 100, 6, "f-ink"))
    for v in (1, 2, 3, 4, 6):
        for s in (1, -1):
            b.append(T(X(s * v), 130, f"{'−' if s < 0 else ''}{v}", "t-mono", "middle"))
    b.append(T(X(0), 130, "0", "t-mono", "middle"))
    for v in (5, 8):
        for s in (1, -1):
            b.append(C(X(s * v), 100, 8, "f-none s-accent thick"))
            b.append(T(X(s * v), 76, f"{'−' if s < 0 else '+'}{v}", "t-accent", "middle"))
    b.append(L(X(0), 92, X(0), 48, "s-pencil dashed"))
    b.append(T(X(0), 40, "+0 and −0: one value, two codes", "t-mono", "middle"))
    b.append(T(X(-8.4), 170, "dots: the 15 values of FP4 (16 codes)", "t-mono"))
    b.append(T(X(-8.4), 192, "coral rings: BitMoD's candidates for the spare −0 code", "t-accent"))
    b.append(T(X(-8.4), 214, "one group of 128 weights uses exactly one of them", "t-mono"))
    return svg("0 0 640 225", "f12", "FP4 values and BitMoD's special values",
               "FP4 values plus and minus 0.5, 1, 1.5, 2, 3, 4 and 6 sit on a number line; plus zero and minus zero "
               "are one value. BitMoD turns the spare minus-zero code into one of plus or minus 5 or 8, chosen per "
               "group of 128 weights.", "".join(b))


# ---- Fig 13: Table III dot plot
def fig_act():
    data = [("Llama-2-7B", 5.12, 5.24, 5.37), ("Llama-2-13B", 4.57, 4.66, 4.76),
            ("Llama-3.1-8B", 5.84, 6.16, 6.36), ("Llama-3.2-3B", 7.28, 7.64, 7.87)]
    # wide and low, near the deck's content area (8.5 x 3.2 in): one legend line instead of a format label per row,
    # three sub-rows of 14 px per model; value labels sit right of their dots (the deck cuts the gridlines there)
    x0, x1, lo, hi = 150, 586, 4.4, 8.0
    top, pitch, gap = 28, 14, 10
    ybot = top + 4 * 3 * pitch + 3 * gap

    def X(v):
        return x0 + (x1 - x0) * (v - lo) / (hi - lo)
    b = [T(14, 16, "hollow = FP16 · teal = W4 + FP8-E4M3 · coral = W4 + INT8-SQ", "t-mono")]
    for v in (4.5, 5.5, 6.5, 7.5):
        b.append(L(X(v), top, X(v), ybot, "s-pencil dashed grid"))
        b.append(T(X(v), ybot + 16, f"{v}", "t-mono", "middle"))
    y = top
    for name, f16, fp8, i8 in data:
        b.append(T(14, y + 1.5 * pitch + 5, name, "t-head"))
        for k, (v, cls) in enumerate(((f16, "f-sheet s-ink"), (fp8, "f-teal"), (i8, "f-accent"))):
            yy = y + pitch / 2 + pitch * k
            b.append(C(X(v), yy, 5, cls))
            b.append(T(X(v) + 10, yy + 4.5, f"{v:.2f}", "t-mono"))
        y += 3 * pitch + gap
    b.append(T(x0, ybot + 34, "Wikitext-2 perplexity (lower is better)", "t-mono"))
    return svg(f"0 0 640 {ybot + 40:g}", "f13", "Activation formats compared, Table III",
               "For four models, Wikitext-2 perplexity with FP16, with 4-bit weights and FP8-E4M3 activations, and "
               "with 4-bit weights and INT8 SmoothQuant activations. FP8-E4M3 is closer to FP16 on every model.",
               "".join(b))


# ---- Fig 14: the 1x4x16 PCU
def fig_pcu():
    b = []
    b.append(R(20, 30, 200, 40, "f-tint s-accent"))
    for i in range(4):
        b.append(L(20 + 50 * i, 30, 20 + 50 * i, 70, "s-accent")) if i else None
        b.append(T(45 + 50 * i, 56, "A8", "t-mono", "middle"))
    b.append(T(20, 22, "input register: 4 × FP8", "t-mono"))
    b.append(R(250, 30, 370, 40, "f-teal"))
    b.append(T(435, 56, "64 × 4-bit W or KV = 256 bits", "t-onbar", "middle"))
    b.append(T(250, 22, "one column access from the bank", "t-mono"))
    b.append(R(250, 86, 370, 28, "f-sheet s-ink"))
    b.append(T(435, 105, "decoder: BitMoD / INT4-Asym → 6 bit", "t-mono", "middle"))
    b.append(L(435, 70, 435, 84, "s-ink", mark="mk"))
    b.append(L(120, 70, 120, 136, "s-ink", mark="mk"))
    b.append(L(435, 114, 435, 136, "s-ink", mark="mk"))
    for i in range(16):
        x = 20 + 37.5 * i
        b.append(R(x, 140, 32, 28, "f-tint s-accent thick" if i == 0 else "f-idle s-pencil"))
        b.append(T(x + 16, 159, "PE", "t-mono", "middle"))
    b.append(T(48, 186, "16 PEs = 16 outputs, as in HBM-PIM", "t-mono"))  # right of the PE-zoom leader (x 36)
    b.append(L(36, 168, 36, 204, "s-accent dashed"))
    b.append(R(20, 206, 600, 112, "f-none s-accent"))
    b.append(T(30, 226, "one PE: a 4-way dot product", "t-accent"))
    for i in range(4):
        x = 34 + 66 * i
        b.append(R(x, 238, 56, 28, "f-sheet s-ink"))
        b.append(T(x + 28, 257, "6b×6b", "t-mono", "middle"))
        b.append(L(x + 28, 266, x + 28, 276, "s-ink", mark="mk"))
    b.append(R(34, 278, 254, 26, "f-idle s-pencil"))
    b.append(T(161, 296, "shift by input exponent", "t-mono", "middle"))
    b.append(L(288, 291, 318, 291, "s-ink", mark="mk"))
    b.append(R(320, 278, 140, 26, "f-sheet s-ink"))
    b.append(T(390, 296, "4:2 compressor", "t-mono", "middle"))
    b.append(L(460, 291, 478, 291, "s-ink", mark="mk"))
    b.append(R(480, 278, 130, 26, "f-mustard"))
    b.append(T(545, 296, "32-bit accum.", "t-onbar", "middle"))
    return svg("0 0 640 326", "f14", "The 1×4×16 low-precision PCU",
               "Four 8-bit inputs from the input register and 64 four-bit weights from one column access feed 16 "
               "PEs. Each PE multiplies four pairs in 6-bit fixed point, shifts each product by the input exponent, "
               "adds them in a 4:2 compressor tree and accumulates in 32 bits.", "".join(b))


# ---- Fig 15: TEP timing (storyboard), after the paper's Fig. 7
def fig_tep():
    VB = "0 0 480 266"

    def X(t):
        return 84 + 42 * t
    lanes = (("C/A bus", 28), ("bank", 102), ("HBM-PIM", 140), ("P3-LLM", 178))

    def scene(s):
        b = []
        for name, y in lanes:
            b.append(T(8, y + 16, name, "t-mono"))
            b.append(L(X(0), y + 24, X(9), y + 24, "s-pencil"))
        for t in range(10):
            b.append(L(X(t), 212, X(t), 218, "s-pencil"))
            b.append(T(X(t), 234, str(t), "t-mono", "middle"))
        b.append(R(X(0) + 4, 28, 34, 22, s.get("iw", "f-mustard"), key="iw"))
        b.append(T(X(0) + 21, 45, "in", "t-onbar", "middle", key="iwt"))
        for j, (t, lab, base) in enumerate(((1, "A", "f-teal"), (3, "B", "f-accent"), (5, "A", "f-teal"),
                                            (7, "B", "f-accent"))):
            b.append(R(X(t) + 4, 28, 30, 22, s.get(f"c{j}", base + " off"), key=f"c{j}"))
            b.append(T(X(t) + 19, 45, lab, "t-onbar" + s.get(f"c{j}t", " off"), "middle", key=f"c{j}t"))
        b.append(R(X(1), 102, X(5) - X(1) - 2, 22, s.get("w1", "f-idle off"), key="w1"))
        b.append(T(X(3), 118, "weight 1", "t-mono" + s.get("w1t", " off"), "middle", key="w1t"))
        b.append(R(X(5), 102, X(9) - X(5), 22, s.get("w2", "f-idle off"), key="w2"))
        b.append(T(X(7), 118, "weight 2", "t-mono" + s.get("w2t", " off"), "middle", key="w2t"))
        for j, (t0, t1, lab) in enumerate(((1, 5, "W1×A1"), (5, 9, "W2×A2"))):
            b.append(R(X(t0), 140, X(t1) - X(t0) - 2, 22, s.get(f"h{j}", "f-none s-teal thick off"), key=f"h{j}"))
            b.append(T((X(t0) + X(t1)) / 2, 156, lab, "t-mono" + s.get(f"h{j}t", " off"), "middle", key=f"h{j}t"))
        for j, (t0, t1, lab, base) in enumerate(((1, 3, "W1×A1", "f-none s-teal thick"),
                                                 (3, 5, "W1×B1", "f-tint s-accent thick"),
                                                 (5, 7, "W2×A2", "f-none s-teal thick"),
                                                 (7, 9, "W2×B2", "f-tint s-accent thick"))):
            b.append(R(X(t0), 178, X(t1) - X(t0) - 2, 22, s.get(f"p{j}", base + " off"), key=f"p{j}"))
            b.append(T((X(t0) + X(t1)) / 2, 194, s.get(f"p{j}l", lab), "t-mono" + s.get(f"p{j}t", " off"),
                       "middle", key=f"p{j}t"))
        a0, a1 = s.get("annL", (1, 5, " off"))[:2], s.get("annL", (1, 5, " off"))[2]
        b.append(L(X(a0[0]), 72, X(a0[1]), 72, "s-ink" + a1, key="annL"))
        b.append(T(X(a0[0]) + 2, 67, "tCCD_L", "t-mono" + a1, key="annLt"))
        sa = s.get("annS", (1, 3, " off"))
        b.append(L(X(sa[0]), 80, X(sa[1]), 80, "s-accent thick" + sa[2], key="annS"))
        b.append(T(X(sa[1]) - 2, 96, "tCCD_S", "t-accent" + sa[2], "end", key="annSt"))
        b.append(T(8, 258, s["note"], "t-mono", key="note"))
        return "".join(b)

    show = ""
    f2 = dict(c0="f-teal", c0t=show, w1="f-idle", w1t=show, h0="f-none s-teal thick", h0t=show,
              annL=(1, 5, show))
    f3 = dict(f2, p0="f-none s-teal thick", p0t=show, annS=(1, 3, show))
    f4 = dict(f3, c1="f-accent", c1t=show, p1="f-tint s-accent thick", p1t=show, annS=(3, 5, show))
    f5 = dict(f4, c2="f-teal", c2t=show, c3="f-accent", c3t=show, w2="f-idle", w2t=show, h1="f-none s-teal thick",
              h1t=show, p2="f-none s-teal thick", p2t=show, p3="f-tint s-accent thick", p3t=show,
              annL=(5, 9, show), annS=(5, 7, show))
    f6 = dict(f5, c1="f-accent off", c1t=" off", c3="f-accent off", c3t=" off",
              p1="f-none s-pencil dashed", p1l="idle", p3="f-none s-pencil dashed", p3l="idle",
              annL=(1, 5, show), annS=(3, 5, show))
    S = [dict(note="NPU writes inputs A and B to the input register"),
         dict(f2, note="HBM-PIM: one command, W1×A1 fills tCCD_L"),
         dict(f3, note="P3-LLM: W1×A1 done in one tCCD_S"),
         dict(f4, note="second command: same W1, input B"),
         dict(f5, note="per tCCD_L: HBM-PIM 1 product, P3-LLM 2"),
         dict(f6, note="batch 1: no input B, second slot idle")]
    caps = [
        "The NPU writes the inputs, A and B, into the PCU's input register.",
        "HBM-PIM: one PIM command at t = 1 reads weight column 1; its FP16 PCU needs the whole tCCD_L window for W1×A1.",
        "P3-LLM: the low-precision PCU runs at tCCD_S, so it finishes W1×A1 in half the window.",
        "A second PIM command at t = 3 multiplies the same weight column, W1, by input B.",
        "The pattern repeats for weight column 2: per tCCD_L window HBM-PIM makes one product and P3-LLM makes two.",
        "At batch 1 there is no input B, so the second tCCD_S slot stays idle and TEP gains nothing.",
    ]
    titles = ["Inputs", "HBM-PIM", "P3-LLM slot 1", "P3-LLM slot 2", "Next column", "Batch 1"]
    frames = [frame(f"tf{i+1}", f"Frame {i+1}: {titles[i]}", caps[i], VB, scene(s), caps[i])
              for i, s in enumerate(S)]
    return timeline("tl15", frames,
                    "Figure 15. Command timing of HBM-PIM and P3-LLM, redrawn from the paper's Fig. 7 (frame 6 is our "
                    "addition). Time runs left to right in DRAM clocks: tCCD_L = 4, tCCD_S = 2. Lanes: the "
                    "command/address bus, the weight column read from the bank, and each design's PCU. Mustard = "
                    "input-register write; teal = work on input A; coral = work on input B.", hold=2400)


# ---- Fig 16: operator split and fused scales
def fig_dataflow():
    b = []
    b.append(T(22, 20, "operator order in one decoder layer →", "t-mono"))
    b.append(R(10, 30, 620, 72, "f-none s-pencil"))
    b.append(T(18, 50, "NPU · FP16 / FP32", "t-head"))
    b.append(R(10, 176, 620, 78, "f-tint s-accent"))
    b.append(T(18, 194, "PIM PCU · low precision", "t-accent"))
    ops = [("norm", "n"), ("QKV", "p"), ("RoPE", "n"), ("Q·Kᵀ", "q"), ("softmax", "n"), ("P·V", "p"),
           ("O proj", "p"), ("MLP", "p")]
    for i, (lab, where) in enumerate(ops):
        x = 22 + 76 * i
        if where == "n":
            y, cls = 60, "f-sheet s-ink"
        elif where == "p":
            y, cls = 206, "f-sheet s-accent thick"
        else:
            y, cls = 124, "f-sheet s-ink dashed"
        b.append(R(x, y, 64, 32, cls))
        b.append(T(x + 32, y + 21, lab, "t-mono", "middle"))
    b.append(T(322, 136, "pre-RoPE keys: NPU", "t-mono"))
    b.append(T(322, 154, "post-RoPE keys: PIM", "t-mono"))
    b.append(T(130, 298, "× scale after", "t-accent", "middle"))
    b.append(T(282, 298, "S_SF into Q", "t-accent", "middle"))
    b.append(T(434, 298, "S_V / S_Vmax into P", "t-accent", "middle"))
    for x in (130, 282, 434):
        b.append(L(x, 282, x, 258, "s-accent dashed", mark="mka"))
    return svg("0 0 640 305", "f16", "Operator mapping and fused dequantization",
               "One decoder layer from left to right. LayerNorm, RoPE and softmax run on the NPU; QKV, P times V, the "
               "output projection and the MLP run on the PIM PCU; Q times K transpose runs on PIM for post-RoPE keys "
               "and on the NPU for pre-RoPE keys. Coral tags show where each scale is folded.", "".join(b))


# ---- Fig 17: evaluation setup
def fig_setup():
    b = []
    b.append(R(14, 24, 290, 150, "f-sheet s-ink"))
    b.append(T(26, 48, "host NPU · 1 GHz", "t-head"))
    for i in range(4):
        b.append(R(26 + 56 * i, 62, 48, 32, "f-idle s-pencil"))
        b.append(T(50 + 56 * i, 83, "core", "t-mono", "middle"))
    b.append(T(26, 116, "per core: 128×128 systolic array,", "t-mono"))
    b.append(T(26, 134, "128-way vector unit,", "t-mono"))
    b.append(T(26, 152, "16 MB scratchpad (after NeuPIMs)", "t-mono"))
    b.append(L(306, 98, 334, 98, "s-ink", mark="mk"))
    b.append(L(336, 112, 308, 112, "s-ink", mark="mk"))
    b.append(R(338, 24, 288, 150, "f-tint s-accent"))
    b.append(T(350, 48, "HBM2 + PIM", "t-head"))
    for i in range(8):
        b.append(R(350 + 33 * i, 62, 26, 32, "f-sheet s-pencil"))
    b.append(T(350, 116, "16 pseudo-channels (8 drawn)", "t-mono"))
    b.append(T(350, 134, "PCUs at 500 MHz = tCCD_S", "t-mono"))
    b.append(T(350, 152, "PIM modelled after Newton", "t-mono"))
    b.append(T(14, 204, "baselines, same NPU and DRAM:", "t-head"))
    for i, lab in enumerate(("1  NPU alone, FP16", "2  NPU + HBM-PIM, FP16", "3  Ecco, W4A8KV4")):
        b.append(T(26 + 206 * i, 228, lab, "t-mono"))
    b.append(T(14, 256, "decode only · 4K context · batch 1–8 · 5 models", "t-mono"))
    return svg("0 0 640 266", "f17", "The simulated system and its baselines",
               "Four NPU cores at 1 GHz connect to HBM2 with 16 pseudo-channels whose PCUs run at 500 MHz. The "
               "baselines use the same NPU and DRAM: the NPU alone, the NPU with HBM-PIM, and Ecco.", "".join(b))


# ---- Fig 18: Table IV mean delta perplexity
def fig_quality():
    rows = [("Oaken · KV4", 0.08, 0.09, False), ("P3-LLM · KV4", 0.06, 0.07, True),
            ("QuaRot · W4A8KV4", 0.30, 0.48, False), ("QoQ · W4A8KV4", 0.30, 0.38, False),
            ("P3-LLM · W4A8KV4P8", 0.25, 0.31, True)]
    b = []
    k = 340  # px per unit of perplexity
    panels = ((200, "Wikitext-2"), (420, "C4"))
    for px, name in panels:
        b.append(T(px, 24, name, "t-head"))
        b.append(L(px, 34, px, 250, "s-ink"))
        for v in (0.2, 0.4):
            b.append(L(px + k * v, 34, px + k * v, 250, "s-pencil dashed grid"))
        for v in (0, 0.2, 0.4):
            b.append(T(px + k * v, 268, f"{v:.1f}", "t-mono", "middle"))
    y = 44
    for i, (lab, w, c4, ours) in enumerate(rows):
        if i == 2:
            b.append(L(10, y - 6, 630, y - 6, "s-pencil"))
            y += 6
        b.append(T(10, y + 22, lab, "t-accent" if ours else "t-mono"))
        for (px, _), v in zip(panels, (w, c4)):
            b.append(R(px, y + 6, k * v, 22, "f-accent" if ours else "f-idle s-pencil"))
            b.append(T(px + k * v + 6, y + 22, f"{v:.2f}", "t-mono"))
        y += 40
    b.append(T(200, 288, "mean perplexity increase over FP16 (lower is better)", "t-mono"))
    return svg("0 0 640 296", "f18", "Mean perplexity loss, Table IV",
               "Mean perplexity increase over FP16 on Wikitext-2 and C4. KV-cache only: Oaken 0.08 and 0.09, "
               "P3-LLM 0.06 and 0.07. Weights and activations: QuaRot 0.30 and 0.48, QoQ 0.30 and 0.38, P3-LLM "
               "0.25 and 0.31.", "".join(b))


# ---- Fig 19: average speedup and energy-efficiency gain
def fig_speed():
    rows = [("vs NPU", 7.8, 6.3), ("vs HBM-PIM", 4.9, 3.5), ("vs Ecco", 2.0, 2.1)]
    x0, k = 130, 50
    b = []
    for v in range(0, 9):
        b.append(L(x0 + k * v, 30, x0 + k * v, 236, "s-pencil dashed grid" if v != 1 else "s-ink dashed grid"))
        b.append(T(x0 + k * v, 254, f"{v}×", "t-mono", "middle"))
    y = 40
    for lab, sp, en in rows:
        b.append(T(10, y + 34, lab, "t-head"))
        b.append(R(x0, y, k * sp, 24, "f-accent"))
        b.append(T(x0 + k * sp + 6, y + 17, f"{sp}× speed", "t-mono"))
        b.append(R(x0, y + 28, k * en, 24, "f-teal"))
        b.append(T(x0 + k * en + 6, y + 45, f"{en}× energy eff.", "t-mono"))
        y += 66
    b.append(T(10, 278, "coral = speedup (Fig. 9) · teal = energy efficiency (Fig. 10)", "t-mono"))
    return svg("0 0 640 290", "f19", "Average speedup and energy-efficiency gain of P3-LLM",
               "Over the NPU: 7.8 times speed and 6.3 times energy efficiency. Over HBM-PIM: 4.9 and 3.5. Over "
               "Ecco: 2.0 and 2.1.", "".join(b))


# ---- Fig 20: area and PE energy
def fig_area():
    b = []
    b.append(T(10, 24, "(a) HBM area overhead", "t-head"))
    x0, k = 96, 7.0  # px per percent
    for v in (0, 10, 20, 30):
        b.append(L(x0 + k * v, 36, x0 + k * v, 150, "s-pencil dashed grid"))
        b.append(T(x0 + k * v, 168, f"{v} %", "t-mono", "middle"))
    for i, (lab, v, cls) in enumerate((("HBM-PIM", 16.4, "f-idle s-pencil"), ("P3-LLM", 17.5, "f-accent"))):
        y = 50 + 46 * i
        b.append(T(10, y + 18, lab, "t-mono"))
        b.append(R(x0, y, k * v, 26, cls))
        b.append(T(x0 + k * v + 6, y + 18, f"{v} %", "t-mono"))
    b.append(L(x0 + k * 25, 36, x0 + k * 25, 150, "s-ink thick dashed"))
    b.append(T(x0 + k * 25 - 4, 194, "25 % limit", "t-mono", "middle"))
    b.append(T(330, 24, "(b) energy per MAC, pJ", "t-head"))
    x0, k = 470, 200
    pes = [("HBM-PIM (1)", 0.69, "f-idle s-pencil"), ("MANT (2)", 0.40, "f-idle s-pencil"),
           ("BitMoD (2)", 0.61, "f-idle s-pencil"), ("P3-LLM (4)", 0.18, "f-accent")]
    for i, (lab, v, cls) in enumerate(pes):
        y = 40 + 38 * i
        b.append(T(330, y + 18, lab, "t-mono"))
        b.append(R(x0, y, k * v, 24, cls))
        b.append(T(x0 + k * v + 6, y + 18, f"{v:.2f}", "t-mono"))
    b.append(T(330, 210, "(n) = MACs per cycle", "t-mono"))
    return svg("0 0 640 220", "f20", "Area overhead and PE energy",
               "Left: HBM area overhead 16.4 percent for HBM-PIM and 17.5 percent for P3-LLM, both under the 25 "
               "percent limit. Right: energy per MAC 0.69 pJ for the HBM-PIM PE, 0.40 for MANT, 0.61 for BitMoD and "
               "0.18 for P3-LLM.", "".join(b))


# ---- Fig 21: the ablation chain, Fig. 15
def fig_ablation():
    b = []
    boxes = [("HBM-PIM, FP16", "1× (baseline)", "f-idle s-pencil", "t-mono"),
             ("+ W4A8KV4", "×3.3", "f-sheet s-ink", "t-head"),
             ("+ TEP", "×1.6", "f-tint s-accent thick", "t-accent"),
             ("+ 8-bit scores", "×1.2", "f-sheet s-ink", "t-head")]
    x = 10
    for i, (lab, mul, cls, tc) in enumerate(boxes):
        b.append(R(x, 40, 136, 70, cls))
        b.append(T(x + 68, 66, lab, "t-mono", "middle"))
        b.append(T(x + 68, 94, mul, tc, "middle"))
        if i < 3:
            b.append(L(x + 136, 75, x + 156, 75, "s-ink", mark="mk"))
        x += 158
    b.append(T(10, 140, "quantization", "t-mono"))
    b.append(T(326, 140, "the PIM-side idea", "t-accent"))
    b.append(T(10, 168, "Fig. 15: average over 5 models at batch 2 and 4, each step over the one before", "t-mono"))
    return svg("0 0 640 180", "f21", "Where the speedup comes from, Fig. 15",
               "Starting from FP16 HBM-PIM, W4A8KV4 quantization gives 3.3 times, TEP another 1.6 times, and 8-bit "
               "attention scores another 1.2 times.", "".join(b))


# ================================================================ slides
SLIDES = []


# The talk's seven parts, the same as the deck's outline (build_p3llm_deck.js PARTS): Summary first, then the
# Preliminary Note, then the paper's own parts from its Background (§II) on.
# The Preliminary Note is the presenter's DRAM primer, added at the user's request for lab members who lack the
# basics: it is not the paper's content (its sources are our DRAM explainer and a simulator preset), it is optional,
# and it is marked as such on every one of its slides. Background is the paper's §II, in the paper's order.
PARTS = [
    ("Summary", "the paper in one slide"),
    ("Preliminary Note", "optional: presenter's DRAM primer, not the paper"),
    ("Background", "Section II: LLM decoding, GQA, PIM, quantization"),
    ("Motivation", "the compute roof of FP16 PIM, W4A8KV4P8"),
    ("Design", "four formats, the PCU and TEP, the dataflow"),
    ("Evaluation", "methodology, quality, speed and energy, area"),
    ("Discussion", "where the gain comes from, open questions"),
]
PRELIM = 2  # the Preliminary Note's part number
PRELIM_MARK = "optional · presenter's primer, not the paper"


def slide(sid, part, short, headline, body):
    """part: the part number (1-7), or (number, sub-topic) for the design slides and the discussion."""
    k, sub = part if isinstance(part, tuple) else (part, "")
    tag = f"Part {k} of {len(PARTS)} · {PARTS[k - 1][0]}" + (f" · {sub}" if sub else "")
    SLIDES.append((sid, (f"{k} · {PARTS[k - 1][0]}", tag, k == PRELIM), short, headline, body))


TERMS = [
    ("decode", "The model makes one new token per step. Each step reads every weight from DRAM once."),
    ("GEMV", "A matrix times one vector. A batch of B requests turns it into a thin matrix product."),
    ("NPU", "The host accelerator (neural processing unit) that runs everything PIM does not."),
    ("bank", "One DRAM memory array. It can hold one row open at a time."),
    ("PIM", "Processing-in-memory: compute logic placed inside the DRAM die, next to the banks."),
    ("PCU / PU", "The PIM compute unit beside a bank. P3-LLM says PCU; AiM says PU."),
    ("AiM", "SK hynix's PIM design: one PU per bank and a shared global buffer for the input."),
    ("HBM-PIM", "Samsung's PIM in HBM: one PCU per pair of banks. P3-LLM builds on it."),
    ("tCCD_S, tCCD_L", "The shortest spacing between two column commands: to different bank groups (S) or "
                       "to the same bank group (L). tCCD_S is about half of tCCD_L."),
    ("TEP", "P3-LLM's throughput-enhanced PCU: it runs at tCCD_S and uses one weight read for two inputs."),
    ("W4A8KV4P8", "4-bit weights, 8-bit activations, 4-bit KV-cache and 8-bit attention scores."),
    ("KV-cache", "The stored keys and values of all earlier tokens."),
    ("GQA", "Grouped-query attention: G query heads share one key/value head."),
    ("perplexity", "A language-model loss score; lower is better."),
]


def build_slides():
    terms = "".join(f"<dt>{E(t)}</dt><dd>{E(d)}</dd>" for t, d in TERMS)
    slide("s01", 1, "P3-LLM in one slide",
          "Summary: P3-LLM keeps DRAM processing-in-memory fast at small batches by shrinking every operand and running a "
          "small compute unit twice per weight read.",
          figure("fig1", fig_summary(),
                 "Figure 1. The three design parts on P3-LLM's system: a host NPU and an HBM-PIM channel. Arrows = "
                 "data moves. Redrawn from the paper's Fig. 6(a) and §I.") + f'''
    <div class="points">
      <p><strong>The problem.</strong> An LLM writes text one token at a time, and every token reads every weight from DRAM. So decoding waits on memory bandwidth. PIM puts multipliers next to the DRAM banks to use their internal bandwidth. Today's PIM units compute in FP16 or BF16, and in a DRAM process they are large and slow. PIM therefore loses its edge already at batch 2–4 or with grouped-query attention (§II–III).</p>
      <ol class="parts">
        <li><strong>W4A8KV4P8 formats.</strong> 4-bit weights and KV-cache, 8-bit activations and attention scores, each operand in its own number format (§IV).</li>
        <li><strong>Low-precision PCU with TEP.</strong> 4× the multipliers in about the same area, clocked at tCCD_S instead of tCCD_L, so one weight read serves two inputs (§V-A, §V-D).</li>
        <li><strong>Fused dequantization.</strong> The NPU folds each scale into a neighbouring operator, so PIM runs only low-precision math (§V-C).</li>
      </ol>
    </div>
    <div class="stats">
      <div class="stat hot"><p class="metric">4.9×</p><p>speed over HBM-PIM; 7.8× over the NPU, 2.0× over Ecco (Fig. 9)</p></div>
      <div class="stat"><p class="metric">3.5×</p><p>energy efficiency over HBM-PIM; 6.3× NPU, 2.1× Ecco (Fig. 10)</p></div>
      <div class="stat"><p class="metric">17.5 %</p><p>HBM area overhead, against 16.4 % for HBM-PIM (Table VII)</p></div>
      <div class="stat"><p class="metric">0.25</p><p>mean Wikitext perplexity loss; QuaRot and QoQ lose 0.30 (Table IV)</p></div>
    </div>
    <p class="note">Paper: Y. Chen, C. Fang, X. Dai, Y. Wu, T. Tambe, M. Verhelst, M. S. Abdelfattah, “P3-LLM: An Integrated NPU-PIM Accelerator for Edge LLM Inference Using Hybrid Numerical Formats”, <a href="https://arxiv.org/abs/2511.06838">arXiv 2511.06838v4</a>, 2026. Section, figure and table numbers on every slide refer to it.</p>
    <details class="glossary">
      <summary>Words this talk uses</summary>
      <dl class="terms">{terms}</dl>
    </details>''')

    slide("s02", 2, "DRAM hierarchy",
          "DRAM is a tree: a channel holds bank groups, a bank group holds banks, and a bank holds rows of columns.",
          figure("fig2", fig_hierarchy(),
                 "Figure 2. Left: one channel with 4 bank groups of 4 banks. Right: the coral bank zoomed in. ACT "
                 "copies one row into the row buffer; RD moves one column out. Sizes are one simulator preset "
                 "(LPDDR5-6400 AiM in Ramulator 2.0); HBM has the same levels with other sizes. Adapted from our "
                 "earlier DRAM explainer (Fig. B1); not to scale.") + '''
    <div class="points">
      <p>A channel has its own command bus and data bus. The host drives each channel on its own.</p>
      <p>A bank is one memory array. It can keep one row open at a time, in its row buffer.</p>
      <p>A bank group is a set of banks that share one path to the channel's I/O. That shared path sets a timing rule on slide 5.</p>
      <p>A row is what one ACT opens: 2,048 B in this preset. A column is what one read moves: 32 B here.</p>
    </div>''')

    slide("s03", 2, "ACT, RD, PRE",
          "Reading one column takes three commands: ACT opens a row, RD moves one column out, and PRE closes the row.",
          fig_actrdpre() + '''
    <div class="points">
      <p>ACT is the expensive step. It moves a whole row from the cells into the sense amplifiers.</p>
      <p>Once the row is open, each RD is cheap. The host can read many columns of the same row with no new ACT (frame 4).</p>
      <p>PIM depends on this fact. It opens a row once and then computes on every column of it.</p>
    </div>''')

    slide("s04", 2, "Timing rules",
          "Timing rules set the earliest moment for each command: tRCD after ACT, CL before the data, tRAS before "
          "PRE and tRP before the next ACT.",
          '''<details class="predict">
      <summary>Before you press play: the host has a row open in bank group 0 and one in bank group 1. It wants a second read 2.5 ns after the first. Which bank group can that read go to?</summary>
      <p>Only bank group 1 (frame 5). A second read to bank group 0 needs tCCD_L = 5 ns, so it must wait (frame 4).</p>
    </details>''' + fig_timing() + '''
    <div class="points">
      <p><strong>tRCD:</strong> from ACT to the first RD of that row. <strong>CL:</strong> from RD to the first data on the bus.</p>
      <p><strong>tRAS:</strong> the shortest time a row stays open. <strong>tRP:</strong> from PRE to the next ACT in the same bank.</p>
      <p><strong>tCCD:</strong> the shortest spacing between two column commands. Frames 4 and 5 show that it depends on the bank group.</p>
      <p>All values here are simulator presets, not JEDEC table values.</p>
    </div>''')

    slide("s05", 2, "tCCD_S vs tCCD_L",
          "Two column reads in the same bank group must be tCCD_L apart; reads to different bank groups need only "
          "tCCD_S.",
          figure("fig5", fig_tccd(),
                 "Figure 5. Left: two bank groups, each with one shared I/O path into the channel I/O. Right: two "
                 "reads, to scale in ns. (a) Same bank group: the second RD waits tCCD_L and the bus idles between "
                 "bursts. (b) Different bank groups: the second RD waits tCCD_S and the bursts touch. Simulator "
                 "presets, not JEDEC values.") + '''
    <div class="points">
      <p>The four banks of a bank group share one I/O path. After one read, that path needs time before it carries the next. That time is tCCD_L.</p>
      <p>Banks in different bank groups use separate paths. Their reads overlap, so the next read waits only tCCD_S, one burst on the bus.</p>
      <p>In this preset tCCD_S is 2.5 ns and tCCD_L is 5 ns. P3-LLM notes that tCCD_S is about half of tCCD_L in every HBM generation (§V-D).</p>
      <p>Keep this factor of two in mind: P3-LLM's TEP is built on it.</p>
    </div>''')

    slide("s06", 2, "Stock AiM MAC",
          "Stock AiM computes inside the DRAM: one MAC16 command makes all 16 banks multiply one column of weights "
          "by the same input slice.",
          '''<details class="predict">
      <summary>Before you press play: which of these commands use the data bus between the host and the DRAM?</summary>
      <p>WRGB (frame 1), WRMAC16 (frame 2) and RDMAC16 (frame 7). MAC16 (frame 5) moves nothing on the data bus: each bank sends its column to its own PU, and the input comes from the global buffer inside the chip.</p>
    </details>''' + fig_aim() + '''
    <div class="table-scroll">
      <table>
        <caption>What moves at each command of one run.</caption>
        <thead><tr><th>command</th><th>what moves</th><th>data bus</th></tr></thead>
        <tbody>
          <tr><td>WRGB</td><td>host → global buffer: one 32 B burst</td><td>yes</td></tr>
          <tr><td>WRMAC16</td><td>host → all 16 MAC registers: bias or zero</td><td>yes</td></tr>
          <tr><td>TMOD</td><td>nothing; switches register-access mode ↔ array mode (twice per run)</td><td>no</td></tr>
          <tr><td>PREA / ACT16</td><td>closes old rows; opens the same row in all 16 banks</td><td>no</td></tr>
          <tr><td>MAC16 ×c</td><td>each bank's 32 B column + the GB's 32 B broadcast → PU multiply and adder tree → MAC register</td><td>no</td></tr>
          <tr><td>RDMAC16</td><td>16 MAC registers → host</td><td>yes</td></tr>
        </tbody>
      </table>
    </div>
    <div class="points">
      <p>Each bank has its own processing unit (PU). All PUs read the same input from one shared global buffer (GB). Each PU keeps its running sum in a MAC register.</p>
      <p>Every MAC16 touches all four bank groups. So two MAC16s always fall under the same-group rule and go tCCD_L apart: stock AiM does one MAC command per tCCD_L.</p>
    </div>''')

    slide("b01", 3, "LLM decoding",
          "An LLM runs all its decoder layers once per new token: prefill reads the prompt, and decoding feeds each "
          "new token back in.",
          figure("fig_llm", fig_llm(),
                 "Figure 7. Top: from the prompt to a new token; the coral loop is decoding. Bottom: one decoder "
                 "layer; boxes with a black outline hold weights. Redrawn from the paper's Fig. 1(a); layer norms and "
                 "the residual adds are left out.") + '''
    <div class="points">
      <p>Prefilling turns the prompt of N_T tokens into a matrix through an embedding table of size N_VOC × H, runs it through L decoder layers and the LM head, and produces the first output token (§II-A).</p>
      <p>Decoding takes that token as the next input and repeats the same operations: one new token per step, auto-regressively.</p>
      <p>A decoder layer has a self-attention module and an MLP. W_Q, W_K and W_V make the queries, keys and values; RoPE rotates Q and K by position; Q·Kᵀ and a softmax give the attention scores P; P·V and W_O give the output. The MLP has three linear layers: W_gate, W_up and W_down.</p>
      <p>The keys (after RoPE) and values are stored in off-chip memory for the later steps: the KV-cache.</p>
    </div>''')

    slide("b02", 3, "GQA",
          "Grouped-query attention lets several query heads share one key-value head, so the KV-cache shrinks by G×.",
          figure("fig_gqa", fig_gqa(),
                 "Figure 8. Left: multi-head attention, one key and value head per query head. Right: grouped-query "
                 "attention with G = 2. Redrawn from the paper's Fig. 1(b).") + '''
    <div class="points">
      <p>The KV-cache stores keys and values for every token, so it becomes large for long contexts (§II-A).</p>
      <p>Each query is split into N_A heads and each key and value into N_KV heads. Multi-head attention has N_A = N_KV.</p>
      <p>GQA splits the N_A query heads into G = N_A / N_KV groups that share key-value heads; in Fig. 1(b) each key-value head serves two query heads. The KV-cache shrinks by G×.</p>
    </div>''')

    slide("b03", 3, "PIM for LLMs",
          "Commercial PIM puts a compute unit next to every DRAM bank, but FP16 and BF16 units cost 20–27 % of the "
          "DRAM die.",
          figure("fig_pim", fig_pim(),
                 "Figure 9. Left: one PIM channel, 16 banks in 4 bank groups, a PIM compute unit (PCU, coral) at each "
                 "bank. Right: the PCUs of Samsung's HBM-PIM and SK hynix's AiM. Redrawn from the paper's Fig. 2.") + '''
    <div class="points">
      <p>DRAM PIM speeds up decoding because it uses the DRAM's higher internal bandwidth for memory-bound operations. Fig. 2 shows two commercial designs: Samsung's HBM-PIM and SK hynix's AiM (§II-B).</p>
      <p>A channel has 16 banks in 4 bank groups, with one PCU near each bank; two banks may share a PCU to save area. Each access sends 256 bits, 16 values of 16 bits, from the bank to the PCU. The input vector goes to the PCU's register file in HBM-PIM and to the global buffer in AiM.</p>
      <p>HBM-PIM's PCU is a 16-way SIMD MAC unit in FP16 that multiplies one input element with 16 weights (input reuse). AiM's PCU uses BF16 and an adder tree (output reuse).</p>
      <p>These high-precision PCUs take 20–27 % of the DRAM die, because a DRAM process has about 10× lower transistor density and fewer metal layers than logic. So PIM pays off mainly at batch 1 and for multi-head attention, which have no data reuse.</p>
      <p>P3-LLM's base pairs an even and an odd bank on one PCU, 8 PCUs per channel (§V-A). From here on the slides use the paper's word, PCU.</p>
    </div>''')

    slide("b04", 3, "Quantization",
          "Quantization scales a group of operands, rounds each one to a fixed set of values and scales back, at "
          "the cost of a rounding error.",
          figure("fig_quant", fig_quant(),
                 "Figure 10. Top: Eq. 1 of the paper as three steps. Bottom: our own example with Q the integers −7 … 7; "
                 "the values are illustrative.") + '''
    <div class="points">
      <p>Eq. 1: a group X gets the scale Δ = |X|max / Q_max; each X / Δ is rounded to the closest value in the set Q, giving X_Q; X_Q · Δ is the dequantized operand. The rounding leaves an error (§II-C).</p>
      <p>Mixed precision: weight-only and KV-cache-only methods are near-lossless at 4 bits; weight-activation methods go further to cut compute and memory.</p>
      <p>Custom number formats adapt better to the value distribution of LLM tensors. NVIDIA and AMD support FP8 in two variants, E4M3 and E5M2.</p>
    </div>''')

    slide("s08", 4, "Compute roof",
          "An FP16 PIM unit loses its advantage as the batch size or the GQA group size approaches 4.",
          figure("fig8", fig_roofline(),
                 "Figure 11. Roofline: peak TOPS against arithmetic intensity, redrawn from the paper's Fig. 4. "
                 "HBM-PIM and P3-LLM share the 1.23 TB/s internal bandwidth; the NPU line is its 307 GB/s DRAM "
                 "bandwidth (its compute roof is not drawn). Mustard guides mark operators at approximate positions "
                 "read from Fig. 4.") + '''
    <div class="points">
      <p>HBM-PIM has 4× the bandwidth of normal HBM during PIM operations, but its FP16 roof is 1.23 TOPS (§III-B, Fig. 4).</p>
      <p>A batch or GQA reuses each weight or key for more inputs and pushes the operator past the roof's corner: HBM-PIM's gain fades as the batch size and the GQA group size approach 4 (§III-B).</p>
      <p>The NPU stays memory-bound even at batch 16 or more, so the system needs more PIM compute (§III-B).</p>
      <p>P3-LLM fits 4× the multipliers in the same compute area and clocks them 2× faster. Its roof is 8× higher, 9.84 TOPS (§III-B).</p>
    </div>''')

    slide("s09", 4, "W4A8KV4P8",
          "P3-LLM gives 4 bits to the large, robust operands and 8 bits to the small, fragile ones: W4A8KV4P8.",
          figure("fig9", fig_quadrant(),
                 "Figure 9. The four operands placed by memory size and by sensitivity to quantization, after the "
                 "paper's Fig. 3. Schematic positions, not measured values.") + '''
    <div class="points">
      <p>At batch 1 the weights fill most of the memory. As the batch grows, the KV-cache grows with it. Activations and scores stay small (Fig. 3a).</p>
      <p>Activations and scores lose the most accuracy when quantized. Weights and KV-cache still work at 4 bits (Fig. 3b).</p>
      <p>P3-LLM quantizes the scores too, so that P·V also runs on the low-precision PCU. Plain integers at W4A8KV4P8 lose too much, so each operand gets its own format (next four slides).</p>
    </div>
    <div class="table-scroll">
      <table class="compact">
        <caption>Earlier co-designs, after the paper's Table I.</caption>
        <thead><tr><th>design</th><th>precision</th><th>memory saving</th><th>accuracy</th><th>HW efficiency</th></tr></thead>
        <tbody>
          <tr><td>BitMoD</td><td>W4A16KV16</td><td>medium</td><td>high</td><td>medium</td></tr>
          <tr><td>Oaken</td><td>W16A16KV4</td><td>medium</td><td>high</td><td>low</td></tr>
          <tr><td>MANT</td><td>W4A8KV4</td><td>high</td><td>medium</td><td>medium</td></tr>
          <tr><td>Ecco</td><td>W4A8KV4</td><td>high</td><td>high</td><td>low (decompresses to FP16)</td></tr>
          <tr><td>Pimba</td><td>W16A16KV8</td><td>low</td><td>high</td><td>medium (linear layers unquantized)</td></tr>
          <tr class="ours"><td>P3-LLM</td><td>W4A8KV4P8</td><td>high</td><td>high</td><td>high</td></tr>
        </tbody>
      </table>
    </div>''')

    slide("s10", (5, "1: formats"), "KV-cache: INT4-Asym",
          "Key-cache outliers sit in a few fixed channels, so P3-LLM divides each channel by its prefill maximum "
          "and then stores 4-bit integers.",
          figure("fig10", fig_kv(),
                 "Figure 10. Left: typical key magnitudes per channel, with two outlier channels (schematic, after "
                 "the paper's Fig. 5). Right: the same channels after division by their prefill maxima. Bottom: one "
                 "INT4-Asym group (§IV-A, §VI-B).") + '''
    <div class="points">
      <p>The value cache shows no outlier pattern. The key cache has a few outlier channels (Fig. 5).</p>
      <p>During prefill, P3-LLM records each key channel's largest magnitude and divides the channel by it, so the channel fits in [−1, 1]. Decoding reuses the same factors (Eq. 2).</p>
      <p>No calibration dataset is needed, so the method cannot overfit one. The factors take &lt; 1 % of memory and &lt; 5 ms for Llama-3.1-8B at 32K context on an A6000 GPU (§IV-A).</p>
      <p>RoPE rotates keys by position. Llama-1/2 keys are quantized before RoPE; Llama-3 and Mistral keys after it, because their outlier channels survive RoPE.</p>
    </div>''')

    slide("s11", (5, "1: formats"), "Scores: FP8-S0E4M4",
          "Attention scores lie between 0 and 1, so P3-LLM drops the sign bit and gives it to the mantissa: "
          "FP8-S0E4M4.",
          figure("fig11", fig_bits(),
                 "Figure 11. Bit layouts, one box per bit. Mustard = sign; teal = exponent; gray = mantissa; coral = "
                 "the mantissa bit that FP8-S0E4M4 gains from the dropped sign (§IV-B).") + '''
    <div class="points">
      <p>Softmax outputs are never negative, so a sign bit carries nothing.</p>
      <p>FP16 values below 1 use only 14 exponent values, −14 to −1. Four exponent bits with a bias of −15 cover them, which leaves 4 mantissa bits.</p>
      <p>Quantizing needs no scale: P3-LLM rounds the FP16 score and keeps its top 4 mantissa bits.</p>
      <p>Table II, Llama-3.1-8B on Wikitext: FP8-S0E4M4 gives perplexity 5.95, the same as FP16. INT8 gives 6.06 and FP8-E4M3 gives 5.99.</p>
    </div>''')

    slide("s12", (5, "1: formats"), "Weights: BitMoD",
          "Weights use BitMoD: FP4 whose spare −0 code becomes one extra value, ±5 or ±8, chosen per group of 128 "
          "weights.",
          figure("fig12", fig_bitmod(),
                 "Figure 12. FP4 values on a number line, the spare −0 code, and BitMoD's four candidate special "
                 "values (§IV-C).") + '''
    <div class="points">
      <p>FP4 has 16 codes but only 15 values, because +0 and −0 are equal.</p>
      <p>BitMoD maps −0 to one special value from {±5, ±8}. For each group of 128 weights it picks the value with the smallest error (§IV-C).</p>
      <p>Weights and the KV-cache enter the PCU through the same input. So each PE has one decoder for both BitMoD and INT4-Asym (§V-A).</p>
      <p>In the ablation, BitMoD instead of INT4 weights recovers 0.01 and 0.07 perplexity on Llama-2-7B and Llama-3.1-8B (Table VI).</p>
    </div>''')

    slide("s13", (5, "1: formats"), "Activations: FP8-E4M3",
          "Activations are cast straight to FP8-E4M3, whose wide range absorbs outliers without rotations or "
          "smoothing.",
          figure("fig13", fig_act(),
                 "Figure 13. Wikitext-2 perplexity from the paper's Table III (4K context). Hollow = FP16 weights and "
                 "activations; teal = 4-bit BitMoD weights with FP8-E4M3 activations; coral = 4-bit weights with "
                 "INT8 SmoothQuant activations.") + '''
    <div class="points">
      <p>Activations also have outlier channels (§IV-D).</p>
      <p>Rotations (QuaRot, SpinQuant) add work at run time. Smoothing (SmoothQuant) moves the difficulty into the weights, which hurts 4-bit weights.</p>
      <p>A per-token cast to FP8-E4M3 has neither cost. With 4-bit weights it beats INT8 SmoothQuant on all four models: on Llama-3.1-8B, 6.16 against 6.36 (Table III).</p>
    </div>''')

    slide("s14", (5, "2: PCU and TEP"), "1×4×16 PCU",
          "The low-precision PCU keeps HBM-PIM's 16 outputs but takes 4 inputs and 64 weights per column: a "
          "1×4×16 dot-product tile.",
          figure("fig14", fig_pcu(),
                 "Figure 14. Top: the operands of one column access. Middle: the 16 PEs. Bottom: one PE zoomed in. "
                 "Arrows = data moves. Redrawn from the paper's Fig. 6(a).") + '''
    <div class="points">
      <p>A 256-bit column holds 64 four-bit values, so the PCU has 64 multipliers: 4× HBM-PIM's 16 FP16 multipliers (§V-A).</p>
      <p>A 64-wide SIMD unit would need 64 accumulators of 32 bits. P3-LLM keeps 16 outputs and widens the input instead. HBM-PIM's tile is 1×1×16.</p>
      <p>Each PE multiplies in 6-bit fixed point, shifts each product by the input's exponent, adds the four in a 4:2 compressor tree and accumulates in 32 bits.</p>
      <p>The PE has no floating-point multipliers and no exponent alignment. It does 4 MACs per cycle at 1.08× the area of an FP16 PE (Table VIII).</p>
    </div>''')

    slide("s15", (5, "2: PCU and TEP"), "TEP at tCCD_S",
          "TEP clocks the PCU at tCCD_S, so each weight column, read once per tCCD_L, serves two input vectors.",
          '''<details class="predict">
      <summary>Before you press play: at batch 1 there is only one input vector. What does P3-LLM's PCU do in the second tCCD_S slot of each window?</summary>
      <p>Nothing (frame 6). TEP needs a second input that uses the same weights. This is why P3-LLM's speedup peaks at batch 2 (Fig. 9).</p>
    </details>''' + fig_tep() + '''
    <div class="points">
      <p>HBM-PIM's PCU runs once per tCCD_L: each PIM command reads 256 bits of weights and does one GEMV step (§V-D).</p>
      <p>The small PCU closes timing at tCCD_S, about half of tCCD_L. So within one window it multiplies weight W1 by input A, then by input B. Fig. 7 draws one PIM command per input.</p>
      <p>The paper rejects two spatial options: an n×4×16 tile needs n× the multipliers, and an n×4×(16/n) tile wastes the 256-bit column.</p>
      <p>PIM power rises only 28 %, because cell access and column decoding dominate it and do not change (§V-D).</p>
    </div>
    <div class="stats">
      <div class="stat"><p class="metric">+28 %</p><p>PIM power at tCCD_S (§V-D)</p></div>
      <div class="stat hot"><p class="metric">1.56×</p><p>energy efficiency (§V-D)</p></div>
      <div class="stat"><p class="metric">1.6×</p><p>speed from TEP, batch 2 and 4 (Fig. 15)</p></div>
    </div>''')

    slide("s16", (5, "3: dataflow"), "Operator split and fused scales",
          "The NPU keeps the FP16 operators and the dequantization, and P3-LLM folds each scale into a neighbouring "
          "operator, so PIM computes only in low precision.",
          figure("fig16", fig_dataflow(),
                 "Figure 16. One decoder layer during decoding; left to right = operator order. Top lane = NPU; "
                 "bottom lane = PIM; dashed box = depends on the model; coral tags = where each scale is folded. "
                 "Redrawn from the paper's Fig. 6(b, c).") + '''
    <div class="points">
      <p>The NPU runs LayerNorm, RoPE, softmax and the element-wise work in FP16/FP32. PIM runs every linear layer and P·V (Fig. 6b).</p>
      <p>Q·Kᵀ runs on PIM only for keys quantized after RoPE (Llama-3, Mistral). Pre-RoPE keys (Llama-1/2) need RoPE on every stored key in every step, so the NPU does Q·Kᵀ.</p>
      <p>Linear layers: the NPU multiplies the output by the scale after the matmul. Q·Kᵀ: the key smoothing factor S_SF is folded into the query before its FP8 cast.</p>
      <p>P·V: the value scale S_V is folded into the scores, after division by its maximum S_Vmax so the scores stay in [0, 1]. The NPU multiplies S_Vmax back after P·V (§V-C).</p>
    </div>''')

    slide("s17", 6, "Setup",
          "The evaluation simulates 4 NPU cores with 16 HBM2 pseudo-channels and compares P3-LLM against three "
          "systems with the same NPU and DRAM.",
          figure("fig17", fig_setup(),
                 "Figure 17. The simulated system and the three hardware baselines, from §VI-A. All baselines use "
                 "the same NPU and DRAM at comparable total area.") + '''
    <div class="points">
      <p>The PCU is RTL synthesized in TSMC 28 nm, scaled to HBM-PIM's 20 nm with DeepScaleTool, then given a 10× penalty for the DRAM process. An in-house cycle-level simulator runs the system (§VI-A).</p>
      <p>The NPU runs at 1 GHz. The PCU runs at 500 MHz, which is HBM2's tCCD_S of 2 DRAM clocks.</p>
      <p>Speed and energy: decoding only, 4K context, batch 1–8, five models (Llama-2 7B and 13B, Llama-3.1-8B, Llama-3.2-3B, Mistral-7B v0.3).</p>
      <p>Accuracy: eight models, perplexity on Wikitext-2 and C4 at 2K context, plus MMLU, ARC-Challenge and GSM8K.</p>
    </div>''')

    slide("s18", 6, "Model quality",
          "Even with more operands quantized, P3-LLM loses less perplexity than QuaRot and QoQ.",
          figure("fig18", fig_quality(),
                 "Figure 18. Mean perplexity increase over FP16 across eight models, from the paper's Table IV (2K "
                 "context). Coral = P3-LLM.") + '''
    <div class="points">
      <p>KV-cache only: P3-LLM loses 0.06 on Wikitext against Oaken's 0.08 (Table IV).</p>
      <p>With weights and activations quantized, P3-LLM loses 39 % and 22 % less perplexity than QuaRot and QoQ. Those two keep the query and the scores in FP16.</p>
      <p>Reasoning tasks, averaged over MMLU, ARC-C and GSM8K on two instruct models: P3-LLM 73.69, QuaRot 71.12, QoQ 70.64, FP16 76.30 (Table V).</p>
      <p>The gap is largest on Llama-3.2-3B, where calibrated integer methods overfit (§VI-B).</p>
    </div>''')

    slide("s19", 6, "Speed and energy",
          "Across batch 1–8 at 4K context, P3-LLM averages 4.9× the speed and 3.5× the energy efficiency of HBM-PIM.",
          figure("fig19", fig_speed(),
                 "Figure 19. Average speedup (Fig. 9) and energy-efficiency gain (Fig. 10) of P3-LLM over each "
                 "baseline: five models, batch 1–8, 4K context. The black dashed line marks 1×.") + '''
    <div class="points">
      <p>HBM-PIM beats the NPU only at batch 1–2. Its edge fades at batch 4 and disappears for GQA models (Fig. 9).</p>
      <p>P3-LLM's speedup peaks at batch 2, where TEP fills both tCCD_S slots.</p>
      <p>Energy falls because 4-bit operands cut DRAM traffic and the PCU is cheaper. HBM-PIM re-reads the weights for each request; TEP halves that repeat (Fig. 10).</p>
      <p>P3-LLM is also 3.4× faster than Pimba enhanced to W8A8KV8 (Fig. 12). From batch 8, P3-LLM moves the linear layers back to the NPU (Fig. 16).</p>
    </div>''')

    slide("s20", 6, "Area",
          "The wider PCU costs 1.1 points of HBM die area: 17.5 % against HBM-PIM's 16.4 %.",
          figure("fig20", fig_area(),
                 "Figure 20. (a) HBM area overhead from Table VII; the dashed line is the 25 % limit the paper cites "
                 "from prior work. (b) Energy per MAC of four PE designs at 1 GHz, from Table VIII.") + '''
    <div class="points">
      <p>PCU compute area grows from 7.7 to 8.4 mm². The buffer stays at 6.2 mm² (Table VII).</p>
      <p>Per PE, P3-LLM does 4 MACs per cycle at 0.18 pJ per MAC: 3.8× better energy per MAC than the FP16 PE (Table VIII).</p>
      <p>The count includes only HBM-PIM's MAC hardware. Its instruction decoder and other operators are left out (§VI-C).</p>
    </div>''')

    slide("s21", (7, "[BRAINSTORM]"), "Discussion points",
          "Points to discuss: quantization gives most of the gain, and TEP, the PIM-side idea, stops at two inputs "
          "per weight read.",
          figure("fig21", fig_ablation(),
                 "Figure 21. The architecture ablation, from the paper's Fig. 15. Each multiplier is over the step "
                 "before it.") + '''
    <p class="label">[BRAINSTORM] Our reading, not the paper's claims</p>
    <ol class="points-list">
      <li><strong>Where the speedup comes from.</strong> W4A8KV4 alone gives 3.3× over FP16 HBM-PIM; TEP adds 1.6×. A baseline already at 4-bit weights would shrink the headline.</li>
      <li><strong>Would a DRAM vendor accept TEP?</strong> It needs the PCU to close timing at tCCD_S (500 MHz on HBM2) and a weight slice to stay valid for a whole tCCD_L.</li>
      <li><strong>One command per input.</strong> Fig. 7 draws a separate PIM command per input vector, so deeper reuse would need more command slots. TEP reaches depth 2, and from batch 8 the linear layers leave PIM. Our group's CoDe work studies this command-bound limit.</li>
      <li><strong>"Edge" means HBM2 here.</strong> The paper says TEP carries over to LPDDR, where tCCD_S is half of tCCD_L, but does not evaluate it.</li>
      <li><strong>Frozen smoothing factors.</strong> The paper does not say what happens when a decode-time key exceeds the prefill maximum. Pre- or post-RoPE is chosen per model family; pre-RoPE models keep Q·Kᵀ on the NPU (Fig. 11).</li>
      <li><strong>Model outputs, not silicon.</strong> An in-house simulator and a flat 10× DRAM penalty give the absolute numbers. Accuracy uses 2K context; speed uses 4K.</li>
    </ol>''')


# ================================================================ page
PAGE_CSS = r"""
/* Page additions for the slide form: index rail, slides, tables, stats */
:root { --tint: #f5d9cf; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --tint: #4a2c23; } }
:root[data-theme="dark"] { --tint: #4a2c23; }
.deck { padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 0; display: grid; }
.page { padding-inline: 0; }
.slide-index { font-family: var(--font-mono); font-size: var(--step--1); padding-top: 1.5rem; min-width: 0; }
.slide-index .label { margin-bottom: 0.5rem; }
.slide-index ol { list-style: none; padding: 0; margin: 0; display: flex; gap: 0.4rem; overflow-x: auto; padding-bottom: 0.4rem; }
.slide-index li { flex: 0 0 auto; }
.slide-index a { display: block; text-decoration: none; color: var(--ink-soft); border: 1px solid var(--idle); border-radius: 2px; padding: 0.15rem 0.45rem; white-space: nowrap; }
.slide-index a .n { color: var(--pencil); margin-right: 0.35rem; }
.slide-index a[aria-current="true"] { border-color: var(--accent); color: var(--accent-ink); }
.slide-index .part { display: none; }
@media (min-width: 76rem) {
  .deck { grid-template-columns: 15rem minmax(0, 52rem); justify-content: center; column-gap: 3rem; }
  .page { max-width: 52rem; }
  .page .wide { margin-inline: 0; }
  .slide-index { position: sticky; top: env(safe-area-inset-top, 0px); align-self: start; max-height: 100vh; overflow-y: auto; padding-block: 3rem 2rem; }
  .slide-index ol { flex-direction: column; overflow-x: visible; gap: 0.15rem; }
  .slide-index a { border: 0; border-left: 2px solid transparent; padding: 0.15rem 0.6rem; white-space: normal; }
  .slide-index a[aria-current="true"] { border-left-color: var(--accent); background: var(--sheet); }
  .slide-index .part { display: block; color: var(--pencil); font-size: 0.75rem; letter-spacing: 0.06em; text-transform: uppercase; margin: 0.7rem 0 0.15rem 0.6rem; }
}
.slide { display: grid; gap: 1rem; border-top: 1px solid var(--pencil); padding-top: 1.25rem; scroll-margin-top: 1rem; }
section.slide > h2 { border-top: 0; padding-top: 0; font-size: 1.5rem; line-height: 1.3; }
@media (min-width: 60rem) and (min-height: 40rem) { .slide { min-height: calc(100vh - 3rem); align-content: center; } }
.slide-tag { font-family: var(--font-mono); font-size: var(--step--1); letter-spacing: 0.06em; text-transform: uppercase; color: var(--pencil); }
.slide-tag .no { color: var(--accent-ink); margin-right: 0.6rem; }
.slide-tag .prelim { margin-left: 0.6rem; padding: 0.05rem 0.4rem; border: 1px solid var(--accent); color: var(--accent-ink); text-transform: none; letter-spacing: 0; }
.points { display: grid; gap: 0.5rem; }
.points p + p { margin-top: 0; }
.parts { display: grid; gap: 0.4rem; }
.points-list { display: grid; gap: 0.5rem; }
.outline-parts { display: grid; gap: 0.15rem; padding-left: 1.4rem; font-family: var(--font-mono); font-size: var(--step--1); color: var(--ink-soft); }
.outline-parts b { color: var(--ink); font-weight: 600; }
.keys-hint { font-family: var(--font-mono); font-size: var(--step--1); color: var(--pencil); }
.f-tint { fill: var(--tint); }
.t-onbar { fill: var(--paper); font-family: var(--font-mono); font-size: 13px; }
.t-head { fill: var(--ink); font-family: var(--font-body); font-size: 15px; font-weight: 600; }
.timeline .t-mono, .timeline .t-onbar { font-size: 15px; }
svg .hot > rect { fill: var(--tint); stroke: var(--accent); stroke-width: 2.5; }
svg .hot > text { fill: var(--accent-ink); }
svg .pend > rect { fill: var(--idle); stroke: var(--pencil); }
svg .pend > text { fill: var(--pencil); }
/* gridlines (class "grid") stop at labels: a halo in the sheet colour knocks them out; the deck cuts them instead */
svg:has(line.grid) text:not(.t-onbar) { paint-order: stroke; stroke: var(--sheet); stroke-width: 4px; stroke-linejoin: round; }
.table-scroll { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; font-size: var(--step--1); line-height: 1.45; }
caption { caption-side: top; text-align: left; font-family: var(--font-mono); font-size: var(--step--1); color: var(--ink-soft); padding-bottom: 0.5rem; }
th, td { text-align: left; vertical-align: top; padding: 0.4rem 0.6rem; border-bottom: 1px solid var(--idle); }
th { font-family: var(--font-mono); font-weight: 500; color: var(--ink-soft); }
tr.ours td { background: var(--tint); }
table.compact th, table.compact td { padding: 0.35rem 0.4rem; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr)); gap: 1rem; }
.stat { border-top: 2px solid var(--pencil); padding-top: 0.5rem; display: grid; gap: 0.2rem; align-content: start; }
.stat.hot { border-top-color: var(--accent); }
.stat .metric { font-size: var(--step-2); line-height: 1.1; }
.stat p:last-child { font-size: var(--step--1); color: var(--ink-soft); }
.note { font-family: var(--font-mono); font-size: var(--step--1); line-height: 1.5; color: var(--ink-soft); }
.glossary summary { cursor: pointer; font-family: var(--font-mono); font-size: var(--step--1); color: var(--accent-ink); }
.glossary[open] summary { margin-bottom: 0.75rem; }
"""

NAV_JS = r"""
<script>
/* Slide navigation: highlights the current slide in the index and moves with the left and right arrow
   keys. Without JavaScript the page is a plain scroll and the index is a list of links. */
(function () {
  var slides = Array.prototype.slice.call(document.querySelectorAll("section.slide"));
  if (!slides.length) return;
  var links = {};
  Array.prototype.forEach.call(document.querySelectorAll(".slide-index a"), function (a) {
    links[a.getAttribute("href").slice(1)] = a;
  });
  var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  var hint = document.querySelector(".keys-hint");
  if (hint) hint.hidden = false;

  function current() {
    var idx = 0;
    for (var i = 0; i < slides.length; i++) {
      if (slides[i].getBoundingClientRect().top <= 80) idx = i; else break;
    }
    return idx;
  }
  function mark() {
    var c = slides[current()].id;
    Object.keys(links).forEach(function (k) {
      if (k === c) links[k].setAttribute("aria-current", "true"); else links[k].removeAttribute("aria-current");
    });
  }
  function go(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    slides[i].scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    setTimeout(mark, reduce ? 0 : 800);
  }
  var pending = 0;
  window.addEventListener("scroll", function () {
    if (pending) return;
    pending = setTimeout(function () { pending = 0; mark(); }, 60);
  }, { passive: true });
  document.addEventListener("keydown", function (e) {
    if (e.defaultPrevented || e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return;
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    var t = e.target;
    if (t && t.closest && t.closest("input, select, textarea, [contenteditable], .timeline")) return;
    var c = current();
    var top = slides[c].getBoundingClientRect().top;
    e.preventDefault();
    if (e.key === "ArrowRight") go(c + 1);
    else go(top < -40 ? c : c - 1);
  });
  mark();
})();
</script>
"""

LIMITS = """
  <aside class="limits" aria-labelledby="limits-label">
    <p class="label" id="limits-label">Sources, assumptions and limits</p>
    <ul>
      <li>Every P3-LLM number comes from arXiv 2511.06838v4 and names its section, figure or table. All figures are redrawn. Chart values come from the paper's text and tables; the operator positions on the roofline, the bars of the key-smoothing and operand figures, and the values in the quantization example are schematic.</li>
      <li>The Preliminary Note (part 2) is the presenter's DRAM primer, added for listeners new to DRAM; it is not the paper's content. Its sizes and timings are one simulator preset (LPDDR5-6400 AiM in Ramulator 2.0), not JEDEC values; HBM2 uses other values. The Background (part 3) is the paper's own Section II.</li>
      <li>The stock AiM run leaves out refresh and the exact command interleaving. TMOD is drawn as one mode switch at each end of the MAC phase.</li>
      <li>Averages such as 4.9× are the paper's averages over five models and batch 1–8 at 4K context. The ablation (Fig. 15) uses batch 2 and 4, so its factors are not parts of the 4.9×.</li>
      <li>The discussion slide is our reading, tagged [BRAINSTORM]; it is not a claim of the paper.</li>
    </ul>
  </aside>
"""


def main():
    tpl = open(TEMPLATE, encoding="utf-8").read()
    style = re.search(r"<style>(.*?)</style>", tpl, re.S).group(1)
    head_links = re.search(r'(<meta name="viewport".*?)<style>', tpl, re.S).group(1)
    player = re.findall(r"<script>.*?</script>", tpl, re.S)
    player = [p for p in player if "Timeline player:" in p][0]

    build_slides()
    nav, parts_seen = [], None
    for i, (sid, (part, _, pre), short, _, _) in enumerate(SLIDES, 1):
        if part != parts_seen:
            nav.append(f'<li class="part" aria-hidden="true">{E(part)}{" (optional)" if pre else ""}</li>')
            parts_seen = part
        nav.append(f'<li><a href="#{sid}"><span class="n">{i:02d}</span>{E(short)}</a></li>')
    sections = []
    for i, (sid, (_, tag, pre), short, headline, body) in enumerate(SLIDES, 1):
        # the Preliminary Note's slides carry a mark: the presenter's primer, not the paper's content
        mark = f'<span class="prelim">{E(PRELIM_MARK)}</span>' if pre else ""
        sections.append(f'''
  <section class="slide{" prelim" if pre else ""}" id="{sid}" aria-labelledby="{sid}-h">
    <p class="slide-tag"><span class="no">{i:02d} / {len(SLIDES)}</span>{E(tag)}{mark}</p>
    <h2 id="{sid}-h">{E(headline)}</h2>
    {body}
  </section>''')
    # figures are numbered in page order
    fig_no = iter(range(1, 100))
    sections = [re.sub(r'(<figcaption id="[^"]+">)Figure \d+\.', lambda m: f"{m.group(1)}Figure {next(fig_no)}.", sec)
                for sec in sections]

    defs = ('<svg width="0" height="0" aria-hidden="true" style="position:absolute"><defs>'
            + "".join(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                      f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="{cls}"></path></marker>'
                      for mid, cls in (("mk", "f-ink"), ("mka", "f-accent"), ("mkt", "f-teal"), ("mkp", "f-pencil")))
            + "</defs></svg>")

    page = f'''<title>P3-LLM for the Lab</title>
<meta name="claude:viewport-fit-sides" content="cover">
{head_links}<style>{style}
.f-pencil {{ fill: var(--pencil); }}
{PAGE_CSS}</style>
{defs}
<div class="deck">
<nav class="slide-index" aria-label="Slide index">
  <p class="label">Slides</p>
  <ol>
    {chr(10).join("    " + n for n in nav).strip()}
  </ol>
</nav>
<main class="page" lang="en">

  <header class="masthead">
    <p class="label">Lab paper discussion · PIM for LLM decoding</p>
    <h1>P3-LLM</h1>
    <p class="question">How does P3-LLM make DRAM processing-in-memory fast for small-batch LLM decoding?</p>
    <p class="answer">It shrinks every operand to 4 or 8 bits in a format chosen per operand, so a small PCU with 4× the multipliers fits in the DRAM. That PCU runs twice per column read and uses each weight for two requests.</p>
    <ol class="outline-parts" aria-label="The talk in seven parts">{"".join(f"<li><b>{E(lab)}</b> · {E(sub)}</li>" for lab, sub in PARTS)}</ol>
    <p class="keys-hint" hidden>Keys: → next slide · ← previous slide</p>
  </header>
{"".join(sections)}
{LIMITS}
</main>
</div>
{player}
{NAV_JS}'''
    open(OUT, "w", encoding="utf-8").write(page)
    print(OUT, len(page), "bytes,", len(SLIDES), "slides")


if __name__ == "__main__":
    main()
