#!/usr/bin/env python3
"""Draw the route map (the page's advance organizer) from the page's own markup.

Usage: python3 route_map.py page.html          # writes the map into the page, in place
       python3 route_map.py page.html --check  # only report problems, change nothing

The route map is an argument map of the page: one small box per part on the path to the answer
(ladder blocks, the problem's assumption, the mechanism's reasons, the answer), each with a one-line
summary, and arrows for "is needed for". It reads, from the page:

  data-part      the part's kind: element, fact, assumption, reason, conclusion (+ convention)
  data-summary   the box's one-line summary, in plain words
  data-from      the ids this part follows from (for a ladder block, data-builds-on is used when
                 data-from is absent)
  id             the box links to it

and writes an SVG into the <figure class="route"> slot, between <!-- route:start --> and
<!-- route:end -->. Rerun it after every change to those attributes; check_page.py warns when the
map is stale. Standard library only.
"""

import hashlib
import json
import re
import sys
from html import escape
from html.parser import HTMLParser

BANDS = ["familiar", "problem", "mechanism", "conclusion"]
MAIN_KINDS = ["conclusion", "reason", "assumption", "fact", "element"]
WORDS = {
    "en": {"familiar": "What you already know", "problem": "The problem", "mechanism": "How it works",
           "conclusion": "The answer", "element": "idea", "fact": "fact", "assumption": "assumption ✗",
           "reason": "reason", "conclusion_k": "answer", "convention": "a choice", "block": "block"},
    "ko": {"familiar": "이미 아는 것", "problem": "문제", "mechanism": "본론", "conclusion": "결론",
           "element": "개념", "fact": "사실", "assumption": "가정 ✗", "reason": "근거",
           "conclusion_k": "결론", "convention": "선택", "block": "블록"},
}
# narrow on purpose: the map fits a phone screen without scrolling sideways
VIEW_W, MARGIN, GAP, DUMMY_W = 420, 8, 12, 12
FONT, LINE, KIND_H, PAD = 16, 20, 19, 8
MAX_LINES = 3


class Collect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section, self.nodes, self.lang, self.ids = None, [], None, set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "section":
            self.section = a.get("id")
        if tag == "main" and a.get("lang") and not self.lang:
            self.lang = a["lang"]
        if "data-part" in a:
            kinds = (a.get("data-part") or "").split()
            frm = (a.get("data-from") or "").split() or (a.get("data-builds-on") or "").split()
            self.nodes.append({"id": a.get("id"), "kinds": kinds, "from": frm, "section": self.section,
                               "summary": (a.get("data-summary") or "").strip(),
                               "concept": "concept" in (a.get("class") or "").split()})


def text_w(s):
    """Rough width of s in px at FONT: Hangul and CJK count as one em, the rest as 0.53 em."""
    return sum(FONT if re.match(r"[ᄀ-ᇿ㄰-㆏가-힯一-鿿]", c) else FONT * 0.46 for c in s)


def wrap(s, width):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and text_w(trial) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def graph(html):
    """Nodes on the route, their edges, and the problems found. Pure; used by check_page.py too."""
    p = Collect()
    p.feed(re.sub(r"<!--.*?-->", "", html, flags=re.S))
    lang = "ko" if (p.lang or "").startswith("ko") else "en"
    problems, nodes = [], []
    for n in p.nodes:
        main = next((k for k in MAIN_KINDS if k in n["kinds"]), None)
        if main is None:          # a pure convention is a lever for "Try it", not a step on the route
            continue
        band = "conclusion" if main == "conclusion" else n["section"]
        if band not in BANDS:     # e.g. a part in "Try it": not on the route
            continue
        if not n["summary"]:
            problems.append(f"{n['id'] or main}: a part on the route has no data-summary (one plain line for the route map)")
            continue
        if not n["id"]:
            problems.append(f"{n['summary'][:40]!r}: a part on the route has no id, so its box cannot link to it")
            continue
        nodes.append(dict(n, kind=main, band=band, conv="convention" in n["kinds"]))
    ids = {n["id"] for n in nodes}
    for n in nodes:
        for f in n["from"]:
            if f not in ids:
                problems.append(f"{n['id']} follows from {f!r}, which is not a part on the route")
        n["from"] = [f for f in n["from"] if f in ids]
    concl = [n for n in nodes if n["kind"] == "conclusion"]
    if not concl:
        problems.append('no conclusion part: mark the one-sentence answer with data-part="conclusion", data-summary and data-from')
    elif len(concl) > 1:
        problems.append(f"{len(concl)} conclusion parts; the route ends in one answer")
    # every part on the route leads to the answer
    if concl:
        succ = {n["id"]: [] for n in nodes}
        for n in nodes:
            for f in n["from"]:
                succ[f].append(n["id"])
        target = concl[0]["id"]
        for n in nodes:
            seen, stack, ok = set(), [n["id"]], False
            while stack:
                v = stack.pop()
                if v == target:
                    ok = True
                    break
                if v not in seen:
                    seen.add(v)
                    stack.extend(succ[v])
            if not ok:
                problems.append(f"{n['id']} does not lead to the answer; connect it (data-from on a later part) or cut it from the page")
    # no cycles
    state = {}

    def visit(v, byid):
        state[v] = 1
        for f in byid[v]["from"]:
            if state.get(f) == 1:
                problems.append(f"a cycle runs through {v} and {f}")
            elif f not in state:
                visit(f, byid)
        state[v] = 2
    byid = {n["id"]: n for n in nodes}
    for n in nodes:
        if n["id"] not in state:
            visit(n["id"], byid)
    for n in nodes:
        if text_w(n["summary"]) > 340:
            problems.append(f"{n['id']}: the summary is long; keep it to one line of about 40 characters (about 20 in Korean)")
    return lang, nodes, problems


def fingerprint(nodes):
    spec = [[n["id"], n["kind"], n["conv"], n["summary"], n["from"]] for n in nodes]
    return hashlib.sha1(json.dumps(spec, ensure_ascii=False).encode()).hexdigest()[:12]


def reduce_edges(nodes):
    """Transitive reduction: leave out an arrow u -> v when another path from u already reaches v.
    The map shows the route, not every citation; the page's text still names every source."""
    byid = {n["id"]: n for n in nodes}

    def reaches(a, b, skip):
        stack, seen = [a], set()
        while stack:
            x = stack.pop()
            if x == b:
                return True
            if x in seen:
                continue
            seen.add(x)
            for n in nodes:
                if x in n["from"] and (x, n["id"]) != skip:
                    stack.append(n["id"])
        return False
    for n in nodes:
        n["draw_from"] = [u for u in n["from"] if not reaches(u, n["id"], (u, n["id"]))]
    return byid


def layout(nodes):
    """Layers top to bottom: bands in order, and within a band the longest path from its sources."""
    byid = reduce_edges(nodes)
    order = {n["id"]: i for i, n in enumerate(nodes)}
    layer, start = {}, 0
    for band in BANDS:
        members = [n for n in nodes if n["band"] == band]

        def lay(n, depth=0):
            if n["id"] in layer:
                return layer[n["id"]]
            if depth > len(nodes):
                return start
            preds = [byid[f] for f in n["from"] if byid[f]["band"] == band or BANDS.index(byid[f]["band"]) < BANDS.index(band)]
            L = start
            for q in preds:
                L = max(L, (layer[q["id"]] if q["id"] in layer else lay(q, depth + 1)) + 1)
            layer[n["id"]] = L
            return L
        for n in members:
            lay(n)
        if members:
            start = max(layer[n["id"]] for n in members) + 1
    nl = max(layer.values()) + 1 if layer else 0
    rows = [[] for _ in range(nl)]
    for n in nodes:
        rows[layer[n["id"]]].append({"id": n["id"], "node": n})
    # long edges pass through dummy slots, so they never cross a box
    edges = []
    for n in nodes:
        for f in n["draw_from"]:
            a, b = layer[f], layer[n["id"]]
            if b <= a:
                continue
            chain = [f]
            for L in range(a + 1, b):
                d = f"~{f}>{n['id']}@{L}"
                rows[L].append({"id": d, "node": None, "src": order[f]})
                chain.append(d)
            chain.append(n["id"])
            edges.append({"chain": chain, "dashed": byid[f]["kind"] == "assumption"})
    # order each row: barycentre of neighbours, a few sweeps down and up
    pos = {}

    def index_rows():
        # positions as fractions of the row, so rows of different lengths compare
        for r in rows:
            for i, it in enumerate(r):
                pos[it["id"]] = (i + 0.5) / len(r)
    for r in rows:
        r.sort(key=lambda it: order[it["id"]] if it["node"] else it["src"] + 0.5)
    index_rows()
    up, down = {}, {}
    for e in edges:
        for u, v in zip(e["chain"], e["chain"][1:]):
            down.setdefault(u, []).append(v)
            up.setdefault(v, []).append(u)
    for sweep in range(8):
        rng = range(1, nl) if sweep % 2 == 0 else range(nl - 2, -1, -1)
        for L in rng:
            def key(it):
                # the last sweeps look both ways, so a lane sits on the side of where it goes
                ns = (up if sweep % 2 == 0 else down).get(it["id"], []) if sweep < 6 else up.get(it["id"], []) + down.get(it["id"], [])
                return (sum(pos[x] for x in ns) / len(ns)) if ns else pos[it["id"]]
            rows[L].sort(key=key)
            index_rows()
    return rows, edges


def render(html):
    lang, nodes, problems = graph(html)
    W = WORDS[lang]
    if not nodes:
        return None, problems
    rows, edges = layout(nodes)
    block_no = {n["id"]: i + 1 for i, n in enumerate(x for x in nodes if x["band"] == "familiar")}
    reason_no = {n["id"]: i + 1 for i, n in enumerate(x for x in nodes if x["kind"] == "reason")}
    geo, out, labels, y = {}, [], [], 8
    band_of_row = [next((it["node"]["band"] for it in r if it["node"]), None) for r in rows]
    for i, r in enumerate(rows):
        band = next((it["node"]["band"] for it in r if it["node"]), None)
        if band and (i == 0 or band != next((b for b in reversed(band_of_row[:i]) if b), None)):
            if i:
                out.append(f'<line x1="{MARGIN}" y1="{y + 4}" x2="{VIEW_W - MARGIN}" y2="{y + 4}" class="s-pencil dashed" stroke-width="1"></line>')
                y += 10
            labels.append(f'<text x="{MARGIN}" y="{y + 15}" class="t-band">{escape(W[band])}</text>')
            y += 24
        n_real = sum(1 for it in r if it["node"])
        n_dummy = len(r) - n_real
        avail = VIEW_W - 2 * MARGIN - n_dummy * DUMMY_W - (len(r) - 1) * GAP
        bw = min(320, avail / max(n_real, 1))
        lines = {it["id"]: wrap(it["node"]["summary"], bw - 2 * PAD) for it in r if it["node"]}
        bh = KIND_H + LINE * max([len(v) for v in lines.values()] or [1]) + PAD + 4
        total = sum(bw if it["node"] else DUMMY_W for it in r) + (len(r) - 1) * GAP
        x = (VIEW_W - total) / 2
        for it in r:
            w = bw if it["node"] else DUMMY_W
            geo[it["id"]] = {"x": x, "y": y, "w": w, "h": bh, "cx": x + w / 2, "lines": lines.get(it["id"])}
            x += w + GAP
        y += bh + 26
    height = y - 10
    # edges first, so boxes sit on top
    ins, outs = {}, {}
    for e in edges:
        outs.setdefault(e["chain"][0], []).append(e)
        ins.setdefault(e["chain"][-1], []).append(e)

    def spread(vid, lst, end):
        lst.sort(key=lambda e: geo[e["chain"][-2 if end == "in" else 1]]["cx"])
        g = geo[vid]
        k = len(lst)
        for j, e in enumerate(lst):
            e[end + "_x"] = g["cx"] + (j - (k - 1) / 2) * min(22, (g["w"] - 20) / max(k, 1))
    for v, lst in ins.items():
        spread(v, lst, "in")
    for v, lst in outs.items():
        spread(v, lst, "out")
    edge_svg = []
    for e in edges:
        a, b = geo[e["chain"][0]], geo[e["chain"][-1]]
        pts = [(e["out_x"], a["y"] + a["h"])]
        for d in e["chain"][1:-1]:
            g = geo[d]
            pts += [(g["cx"], g["y"]), (g["cx"], g["y"] + g["h"])]
        pts.append((e["in_x"], b["y"] - 3))
        dpath = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            if abs(x1 - x2) < 0.5:
                dpath += f" L{x2:.1f},{y2:.1f}"
            else:
                m = (y1 + y2) / 2
                dpath += f" C{x1:.1f},{m:.1f} {x2:.1f},{m:.1f} {x2:.1f},{y2:.1f}"
        cls = "s-pencil dashed" if e["dashed"] else "s-ink"
        edge_svg.append(f'<path d="{dpath}" class="f-none {cls}" stroke-width="1.4" marker-end="url(#arrow)"></path>')
    box_svg = []
    for n in nodes:
        g = geo[n["id"]]
        k = n["kind"]
        if n["band"] == "familiar":
            kind = f"{W['block']} {block_no[n['id']]} · {W[k]}"
        elif k == "reason":
            kind = f"{W['reason']} {reason_no[n['id']]}"
        elif k == "conclusion":
            kind = W["conclusion_k"]
        else:
            kind = W[k]
        cls = {"element": "f-paper s-pencil", "fact": "f-sheet s-ink", "assumption": "f-paper s-ink dashed",
               "reason": "f-sheet s-accent", "conclusion": "f-route-answer s-accent"}[k]
        t = [f'<a href="#{escape(n["id"])}" data-key="route-{escape(n["id"])}">',
             f'<rect x="{g["x"]:.1f}" y="{g["y"]:.1f}" width="{g["w"]:.1f}" height="{g["h"]:.1f}" rx="3" class="{cls}" stroke-width="{2 if k in ("reason", "conclusion") else 1.2}"></rect>',
             f'<text x="{g["x"] + PAD:.1f}" y="{g["y"] + 15:.1f}" class="t-kind">{escape(kind)}']
        if n["conv"]:
            t.append(f'<tspan class="t-choice"> · {escape(W["convention"])}</tspan>')
        t.append("</text>")
        for j, line in enumerate(g["lines"]):
            t.append(f'<text x="{g["x"] + PAD:.1f}" y="{g["y"] + KIND_H + 14 + j * LINE:.1f}" class="t-node">{escape(line)}</text>')
        t.append("</a>")
        box_svg.append("".join(t))
    title = {"en": "The route to the answer", "ko": "결론까지 가는 길"}[lang]
    desc = " ".join(f"{n['summary']}" + (f" (from {', '.join(n['from'])})" if n["from"] else "") + "." for n in nodes)
    svg = (f'<svg viewBox="0 0 {VIEW_W} {height:.0f}" role="img" aria-labelledby="route-title route-desc" data-route="{fingerprint(nodes)}">'
           f'<title id="route-title">{escape(title)}</title><desc id="route-desc">{escape(desc)}</desc>'
           + "".join(out) + "".join(edge_svg) + "".join(labels) + "".join(box_svg) + "</svg>")
    return svg, problems


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    path = sys.argv[1]
    html = open(path, encoding="utf-8").read()
    svg, problems = render(html)
    for p in problems:
        print("WARN  [route]", p)
    if "--check" in sys.argv:
        sys.exit(0)
    if svg is None:
        print("no parts with data-summary; nothing to draw")
        sys.exit(1)
    m = re.search(r"<!-- route:start -->.*?<!-- route:end -->", html, flags=re.S)
    if not m:
        print('no <!-- route:start --> ... <!-- route:end --> slot in a <figure class="route">; add it under the one-sentence answer')
        sys.exit(1)
    html = html[:m.start()] + "<!-- route:start -->" + svg + "<!-- route:end -->" + html[m.end():]
    open(path, "w", encoding="utf-8").write(html)
    print(f"route map written: {len(svg)} bytes")


if __name__ == "__main__":
    main()
