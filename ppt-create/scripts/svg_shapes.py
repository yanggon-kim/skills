#!/usr/bin/env python3
"""Turns the prototype's inline SVG figures into native-shape records for the deck builder.

Library (imported by html_to_spec.py and by deck builders), and a small CLI for checking one figure:
    python3 svg_shapes.py FIGURE.svg            -> prints the parsed record and its content bounds

A figure is drawn in a small vocabulary (references/html-prototype.md): <rect>, <circle>, <ellipse>,
<line>, <polyline> (unfilled), <text> and <g transform="translate(x y)">, coloured only through classes:
  fills    f-paper f-sheet f-white | f-idle | f-ink | f-accent | f-tint | f-c2 (alias f-teal) |
           f-c3 (alias f-mustard) | f-pencil | f-none
  strokes  s-ink | s-pencil | s-accent | s-c2 (s-teal) | s-c3 (s-mustard); "thick", "dashed"; "grid" on a
           <line> marks a gridline (record key grid: true), which the build cuts where it meets a label
           (scripts/crossings.js; a polyline's segments carry poly: [index, segments, arrowhead] for that pass)
  text     t-label | t-mono | t-head | t-accent | t-onbar   (optional font-size="N" overrides the size)
  state    "off" hides an element in one storyboard frame; <g class="hot"> / <g class="pend"> mark a
           highlighted / still-to-come group; data-key="k" names an element across frames.
Each element becomes a record in SVG units with a palette *slot* (white, idle, ink, inksoft, accent, tint,
accentink, c2, c3, pencil, black); the deck maps slots to theme colours, so the same figure re-colours
with the theme. Anything outside the vocabulary raises Unmapped, so a builder can stop and name it.

bounds() gives the content box of one figure, or of all frames of a storyboard together (one crop for
every frame keeps Morph's placement stable), so the deck can drop empty margins and scale the figure to
fill its area. apply_edits() holds the deck-only label edits a builder may need (drop or shorten a
label, add a legend line, scale dense labels).
"""
import html
import json
import re
import sys
import xml.etree.ElementTree as ET

FILL = {"f-paper": "white", "f-sheet": "white", "f-white": "white", "f-idle": "idle", "f-ink": "ink",
        "f-accent": "accent", "f-tint": "tint", "f-c2": "c2", "f-teal": "c2", "f-c3": "c3", "f-mustard": "c3",
        "f-pencil": "pencil", "f-none": None}
STROKE = {"s-ink": "ink", "s-pencil": "pencil", "s-accent": "accent", "s-c2": "c2", "s-teal": "c2",
          "s-c3": "c3", "s-mustard": "c3"}
# text class -> (colour slot, size in px, bold, size inside a storyboard frame)
TEXT = {"t-label": ("ink", 15, False, 15), "t-mono": ("inksoft", 13, False, 15),
        "t-accent": ("accentink", 15, True, 15), "t-head": ("ink", 15, True, 15),
        "t-onbar": ("white", 13, False, 15)}
SVGNS = "{http://www.w3.org/2000/svg}"
_ENT = re.compile(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)(\w+);")


class Unmapped(Exception):
    pass


def _f(v):
    return float(v)


def _xmlsafe(svgtext):
    """HTML named entities (&nbsp; &times; ...) are not XML: turn them into characters first."""
    return _ENT.sub(lambda m: html.unescape(m.group(0)), svgtext)


def parse_svg(svgtext, timeline=False):
    """One <svg> element as text -> {"vb": [x, y, w, h], "shapes": [...], "textScale": k}."""
    root = ET.fromstring(_xmlsafe(svgtext))
    vb = [float(v) for v in re.split(r"[ ,]+", root.get("viewBox").strip())]
    shapes = []

    def walk(el, ctx):
        tag = el.tag.replace(SVGNS, "")
        cls = (el.get("class") or "").split()
        key = el.get("data-key") or ctx.get("key")
        if tag in ("title", "desc", "defs", "style", "marker"):
            return
        if "off" in cls:
            return  # hidden in this frame: the deck leaves it out, Morph fades it
        if tag == "g":
            tr = el.get("transform") or ""
            dx = dy = 0.0
            if tr:
                m = re.fullmatch(r"translate\(\s*([-\d.]+)(?:[ ,]+([-\d.]+))?\s*\)", tr.strip())
                if not m:
                    raise Unmapped(f"g transform {tr!r} (only translate(x y) is supported)")
                dx, dy = float(m.group(1)), float(m.group(2) or 0)
            sub = dict(ctx, dx=ctx["dx"] + dx, dy=ctx["dy"] + dy, key=key, sub=0,
                       hot="hot" in cls or ctx.get("hot"), pend="pend" in cls or ctx.get("pend"))
            for ch in el:
                walk(ch, sub)
                sub["sub"] += 1
            return
        dx, dy = ctx["dx"], ctx["dy"]
        name = None
        if key:
            name = key if el.get("data-key") else f"{key}.{tag[0]}{ctx.get('sub', 0)}"
        thick = "thick" in cls
        dashed = "dashed" in cls
        stroke = next((STROKE[c] for c in cls if c in STROKE), None)
        sw = (2.5 if thick else 1.5) if stroke else 0
        fills = [c for c in cls if c in FILL]
        fill = None
        if tag in ("rect", "circle", "ellipse", "polyline"):
            fill = FILL[fills[0]] if fills else "black"
            if ctx.get("hot") and tag == "rect":
                fill, stroke, sw = "tint", "accent", 2.5
            if ctx.get("pend") and tag == "rect":
                fill, stroke = "idle", "pencil"
        if tag == "rect":
            shapes.append(dict(t="rect", x=_f(el.get("x", 0)) + dx, y=_f(el.get("y", 0)) + dy, w=_f(el.get("width")),
                               h=_f(el.get("height")), fill=fill, stroke=stroke, sw=sw, dash=dashed, name=name))
        elif tag == "circle":
            shapes.append(dict(t="circle", cx=_f(el.get("cx")) + dx, cy=_f(el.get("cy")) + dy, r=_f(el.get("r")),
                               fill=fill, stroke=stroke, sw=sw, dash=dashed, name=name))
        elif tag == "ellipse":
            shapes.append(dict(t="ellipse", cx=_f(el.get("cx")) + dx, cy=_f(el.get("cy")) + dy, rx=_f(el.get("rx")),
                               ry=_f(el.get("ry")), fill=fill, stroke=stroke, sw=sw, dash=dashed, name=name))
        elif tag == "text":
            s = "".join(el.itertext())
            if not s.strip():
                return
            tcls = next((c for c in cls if c in TEXT), None)
            if tcls is None:
                raise Unmapped(f"text class {cls} (use t-label, t-mono, t-head, t-accent or t-onbar)")
            col, size, bold, tsize = TEXT[tcls]
            size = tsize if timeline else size
            if el.get("font-size"):
                size = float(re.sub(r"px$", "", el.get("font-size")))
            if el.get("font-weight") in ("bold", "600", "700"):
                bold = True
            if ctx.get("hot"):
                col = "accentink"
            if ctx.get("pend"):
                col = "pencil"
            shapes.append(dict(t="text", x=_f(el.get("x", 0)) + dx, y=_f(el.get("y", 0)) + dy, s=s,
                               anchor=el.get("text-anchor") or "start", color=col, size=size, bold=bold, name=name))
        elif tag in ("line", "polyline"):
            if tag == "line":
                pts = [(_f(el.get("x1")), _f(el.get("y1"))), (_f(el.get("x2")), _f(el.get("y2")))]
            else:
                if fills and FILL[fills[0]] is not None:
                    raise Unmapped("filled polyline (draw the area as rects, or leave it unfilled)")
                pts = [tuple(float(v) for v in p.split(",")) for p in el.get("points").split()]
            arrow = bool(el.get("marker-end"))
            n = len(pts) - 1
            for i in range(n):
                (x1, y1), (x2, y2) = pts[i], pts[i + 1]
                nm = name if n == 1 or name is None else f"{name}.{i}"
                shapes.append(dict(t="line", x1=x1 + dx, y1=y1 + dy, x2=x2 + dx, y2=y2 + dy, stroke=stroke or "black",
                                   sw=sw or 1.5, dash=dashed, arrow=arrow and i == n - 1, name=nm,
                                   **({"grid": True} if "grid" in cls else {}),  # a gridline: cut at labels (crossings.js)
                                   # a polyline segment: [index, segments, arrowhead], so crossings.js tells a curve from a leader
                                   **({"poly": [i, n, int(arrow)]} if tag == "polyline" else {})))
        else:
            raise Unmapped(f"element <{tag}> (supported: rect, circle, ellipse, line, polyline, text, g)")

    for ch in root:
        walk(ch, {"dx": 0.0, "dy": 0.0, "key": None})
    out = {"vb": vb, "shapes": shapes}
    if root.get("data-text-scale"):
        apply_edits(out, size=float(root.get("data-text-scale")))
    return out


def parse_timeline(markup):
    """A storyboard written as <li class="frame"><svg>...</svg><p class="frame-caption">...</p></li> items
    (the concept-explainer markup) -> {"frames": [...], "caption": figcaption text}."""
    frames = []
    for m in re.finditer(r'<li class="frame">(<svg.*?</svg>)<p class="frame-caption">(.*?)</p></li>', markup, re.S):
        svgtext, cap = m.group(1), html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
        title = html.unescape(re.search(r"<title[^>]*>(.*?)</title>", svgtext, re.S).group(1))
        f = parse_svg(svgtext, timeline=True)
        f.update(title=re.sub(r"^Frame \d+: ", "", title), caption=cap)
        frames.append(f)
    figcap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", markup, re.S)
    return {"frames": frames, "caption": html.unescape(re.sub(r"<[^>]+>", "", figcap.group(1))) if figcap else ""}


def apply_edits(fig, text=None, add=None, size=1.0):
    """Deck-only edits of one parsed figure, in place.
    text: {label: new label or None to drop}, matched on the whole label, so a changed label fails loudly;
    add:  extra shape records (a legend line, a one-word mark); size: a scale for every label."""
    edits = text or {}
    seen = set()
    out = []
    for s in fig["shapes"]:
        if s["t"] == "text" and s["s"] in edits:
            seen.add(s["s"])
            if edits[s["s"]] is None:
                continue
            s = dict(s, s=edits[s["s"]])
        out.append(s)
    missing = set(edits) - seen
    assert not missing, ("labels not found", missing)
    out = [dict(s, size=s["size"] * size) if s["t"] == "text" else s for s in out]
    fig["shapes"] = out + [dict(a) for a in (add or [])]
    return fig


def text_box(s):
    """Estimated extent of a text record: 0.56 em per character, 0.95 em above and 0.3 em below the baseline."""
    w = len(s["s"]) * s["size"] * 0.56
    x = s["x"] - (w / 2 if s["anchor"] == "middle" else w if s["anchor"] == "end" else 0)
    return x, s["y"] - s["size"] * 0.95, x + w, s["y"] + s["size"] * 0.3


def bounds(frames, pad=6.0):
    """Content bounding box [x, y, w, h] in SVG units over one figure or all frames of a storyboard, plus a pad,
    clipped to the viewBox."""
    xs, ys = [], []
    for f in frames:
        for s in f["shapes"]:
            if s["t"] == "rect":
                xs += [s["x"], s["x"] + s["w"]]
                ys += [s["y"], s["y"] + s["h"]]
            elif s["t"] == "circle":
                xs += [s["cx"] - s["r"], s["cx"] + s["r"]]
                ys += [s["cy"] - s["r"], s["cy"] + s["r"]]
            elif s["t"] == "ellipse":
                xs += [s["cx"] - s["rx"], s["cx"] + s["rx"]]
                ys += [s["cy"] - s["ry"], s["cy"] + s["ry"]]
            elif s["t"] == "line":
                xs += [s["x1"], s["x2"]]
                ys += [s["y1"], s["y2"]]
            else:
                x0, y0, x1, y1 = text_box(s)
                xs += [x0, x1]
                ys += [y0, y1]
    vx, vy, vw, vh = frames[0]["vb"]
    if not xs:
        return [vx, vy, vw, vh]
    x0, y0 = max(vx, min(xs) - pad), max(vy, min(ys) - pad)
    x1, y1 = min(vx + vw, max(xs) + pad), min(vy + vh, max(ys) + pad)
    return [round(x0, 1), round(y0, 1), round(x1 - x0, 1), round(y1 - y0, 1)]


def unkeyed_counts(frames):
    """Morph pairs unkeyed elements by their order, so every frame of a storyboard needs the same count."""
    return [sum(1 for s in f["shapes"] if not s["name"]) for f in frames]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    fig = parse_svg(open(sys.argv[1], encoding="utf-8").read())
    print(json.dumps({"vb": fig["vb"], "bb": bounds([fig]), "shapes": len(fig["shapes"])}, indent=1))
