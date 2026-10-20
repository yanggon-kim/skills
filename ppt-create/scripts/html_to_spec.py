#!/usr/bin/env python3
"""Mode 2, step 1: read an HTML prototype (references/html-prototype.md) into a deck spec for build_deck.js,
and lint it against the deck's rules first.

Run:   <work>/venv/bin/python html_to_spec.py TALK.html SPEC.json [--work DIR] [--png-fallback]
       <work>/venv/bin/python html_to_spec.py TALK.html --check          (lint only, no spec)
Needs: beautifulsoup4 (scripts/setup.sh); Pillow + Liberation Sans for the text-fit estimates (else a rough
       width per character); LibreOffice only for --png-fallback.

What it does:
  * slides in page order; storyboards keep one record per frame; the outline, a divider before every part,
    and the appendix index are added when the page does not have them;
  * the Summary part: every deck's first part is "Summary", right after the title. The outline slide
    is its divider (drawn with Summary highlighted), so the deck never shows two outlines in a row; the
    next slide is the summary slide, titled "Summary: <core message>";
  * figures: inline SVG -> native-shape records (svg_shapes.py) with content bounds for the crop. A figure
    outside the vocabulary stops the run, naming the element; --png-fallback instead embeds that single
    figure as a picture (rendered by LibreOffice; its text then escapes the type-floor check);
  * speaker notes from .notes; provenance (.source) is appended to the notes ("Figure: ..." / "Source: ...");
  * lint: ERROR stops the spec (exit 1), WARN is printed. Errors: no notes on a slide, provenance words on
    the slide, no Summary part first in the parts list, no summary slide right after the outline, a
    summary slide whose title does not start with "Summary", a divider for the Summary part (it would
    repeat the outline), a numbered or bullet point list on the title slide (the key points live only on
    the Summary slide), an appendix slide before the closing slide, a pointer to a missing appendix slide, unequal
    unkeyed elements across storyboard frames (Morph pairs them by order), a figure filling under half of
    its area (unless the slide has data-whitespace="reason"). Warnings: a title longer than one 20 pt
    line, a band over 4 lines or with more than 3 bullets, a step caption over 10 lines, loose viewBoxes,
    a figure filling under 75 % of its area, figure labels that the deck must raise to 12 pt, a table
    taller than the area or still under 75 % of it when grown, results without a methodology slide, notes
    shorter than 40 or longer than 300 words, a Summary part of more than one slide;
  * tables grow to fill the area: type up to 18 pt, then taller rows (fit_table).
"""
import argparse
import base64
import html as htmllib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from svg_shapes import Unmapped, bounds, parse_svg, unkeyed_counts  # noqa: E402

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    sys.exit("beautifulsoup4 is missing: run scripts/setup.sh and use <work>/venv/bin/python")

TAGS = re.compile(r"Paper's|After the paper|[Ss]chematic|Redrawn|Adapted from|[Ss]ource:|Courtesy of|Reproduced from")
AREA_W, AREA_H, FAREA_W, FAREA_H = 8.5, 3.2, 6.05, 4.4
FILL_ERR, FILL_WARN = 0.50, 0.75  # a figure filling less of its area stops the spec / warns (see check_fig)
TABLE_MAX_PT, TABLE_EMPTY_WARN = 18, 0.25  # a table grows to this size to fill the area; warn if still this empty
TABLE_GAP = 0.05  # in: a filled table stops this far above the area's bottom, clear of the band's hairline
BAND_W, BAND_MARL, CAP_W = 8.5, 0.1875, 2.25
SUMMARY = "Summary"  # the first part of every deck, and the first word of its summary slide's title
LIST_MARK = re.compile(r"^\s*(\d{1,2}[.)]|[•▪‣◦●■–])\s")  # a numbered or bulleted line written out as text


def is_summary(part):
    """The Summary part: id or outline label "Summary" (a label may add a sub-heading, "Summary: ...")."""
    return part["id"] == SUMMARY or (part["label"] or "").startswith(SUMMARY)

# ---------------------------------------------------------------- text measure (Liberation Sans = Arial metrics)
_FONTS = {}


def _font(bold, size):
    try:
        from PIL import ImageFont
    except ImportError:
        return None
    key = (bold, round(size * 4))
    if key not in _FONTS:
        name = "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"
        path = None
        for d in ("/usr/share/fonts/truetype/liberation2", "/usr/share/fonts/truetype/liberation", "/usr/share/fonts/liberation-sans"):
            if os.path.isfile(os.path.join(d, name)):
                path = os.path.join(d, name)
        _FONTS[key] = ImageFont.truetype(path, key[1]) if path else None
    return _FONTS[key]


def width_in(text, size, bold=False):
    f = _font(bold, size)
    if f is None:
        return len(text) * size * (0.55 if bold else 0.5) / 72
    return f.getlength(text) / 4 / 72


def lines(text, size, width, bold=False):
    n, cur = 1, 0.0
    for w in re.split(r"(\s+)", text):
        if not w:
            continue
        wl = width_in(w, size, bold)
        if w.isspace():
            cur += wl
        elif cur > 0 and cur + wl > width * 0.97:
            n, cur = n + 1, wl
        else:
            cur += wl
    return n


# ---------------------------------------------------------------- parsing
def clean(el):
    """Text of an element, whitespace collapsed (inline tags add no spaces)."""
    if el is None:
        return ""
    return " ".join(el.get_text("").split())


def notes_of(el):
    """Speaker notes: every .notes child that belongs to this element (not to a storyboard frame inside it)."""
    out = []
    for n in el.select(".notes"):
        if el.name == "section" and n.find_parent("li", class_="frame"):
            continue
        for s in n.find_all("summary"):
            s.extract()
        ps = n.find_all("p")
        out += [clean(p) for p in ps] if ps else [clean(n)]
    return " ".join(t for t in out if t)


def svg_css():
    """The figure vocabulary's colours, for a standalone SVG (the PNG fallback)."""
    return ("text{font-family:Arial,'Liberation Sans',sans-serif}.f-paper,.f-sheet,.f-white{fill:#fff}.f-idle{fill:#DAE6F4}"
            ".f-ink{fill:#57585B}.f-accent{fill:#FFC72B;stroke:#00375B}.f-tint{fill:#FFC72B;fill-opacity:.4;stroke:#00375B}"
            ".f-c2,.f-teal{fill:#2774AE}.f-c3,.f-mustard{fill:#8AB8E8}.f-pencil{fill:#898989}.f-none{fill:none}"
            ".s-ink{stroke:#57585B}.s-pencil{stroke:#898989}.s-c2,.s-teal{stroke:#2774AE}.s-c3,.s-mustard{stroke:#8AB8E8}"
            "rect.s-accent,circle.s-accent,ellipse.s-accent,path.s-accent,polygon.s-accent{stroke:#00375B}line.s-accent,polyline.s-accent{stroke:#FFC72B}[class*='s-']{stroke-width:1.5}.thick{stroke-width:2.5}.dashed{stroke-dasharray:5 4}"
            ".t-label{fill:#57585B;font-size:15px}.t-mono{fill:#57585B;font-size:13px}.t-head,.t-accent{fill:#00375B;font-size:15px;"
            "font-weight:700}.t-onbar{fill:#fff;font-size:13px}.off{opacity:0}")


def svg_to_png(svgtext, work):
    """Render one SVG to a PNG data URI with LibreOffice (the optional pptx skill's wrapper when present)."""
    sys.path.insert(0, HERE)
    import render  # noqa: E402
    vb = [float(v) for v in re.split(r"[ ,]+", re.search(r'viewBox="([^"]+)"', svgtext).group(1).strip())]
    scale = 2400 / vb[2]
    s = re.sub(r"<svg\b[^>]*>", f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(f"{v:g}" for v in vb)}" '
               f'width="{vb[2] * scale:.0f}" height="{vb[3] * scale:.0f}"><style>{svg_css()}</style>', svgtext, count=1)
    s = re.sub(r'marker-end="[^"]*"', "", s)
    s = s.replace("</style>", "</style>" + f'<rect x="{vb[0]:g}" y="{vb[1]:g}" width="{vb[2]:g}" height="{vb[3]:g}" fill="#fff"/>', 1)
    tmp = tempfile.mkdtemp(prefix="svgpng_", dir=work)
    src = os.path.join(tmp, "fig.svg")
    open(src, "w", encoding="utf-8").write(s)
    run = render.pptx_skill_soffice()
    args = ["--headless", "--convert-to", "png", "--outdir", tmp, src]
    if run:
        run(args, capture_output=True, timeout=300)
    else:
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/profile"] + args, capture_output=True, timeout=300)
    png = os.path.join(tmp, "fig.png")
    if not os.path.isfile(png):
        raise RuntimeError("LibreOffice could not render the figure to PNG")
    return "image/png;base64," + base64.b64encode(open(png, "rb").read()).decode()


class Lint:
    def __init__(self):
        self.errors, self.warns = [], []

    def err(self, where, msg):
        self.errors.append(f"ERROR {where}: {msg}")

    def warn(self, where, msg):
        self.warns.append(f"WARN  {where}: {msg}")


def figure_record(svgtext, where, lint, timeline=False, area=(AREA_W, AREA_H), png=False, work="."):
    try:
        fig = parse_svg(svgtext, timeline=timeline)
    except Unmapped as e:
        if png and not timeline:
            lint.warn(where, f"figure outside the shape vocabulary ({e}); embedded as a picture, its labels are not checked")
            vb = [float(v) for v in re.split(r"[ ,]+", re.search(r'viewBox="([^"]+)"', svgtext).group(1).strip())]
            return {"vb": vb, "bb": vb, "shapes": [], "image": svg_to_png(svgtext, work)}
        lint.err(where, f"figure outside the shape vocabulary: {e}" + ("" if timeline else " (or rerun with --png-fallback)"))
        return None
    return fig


def table_lines(cells_rows, colw, font, bold_first):
    """Lines of each cell at one font size: greedy word wrap with Liberation Sans at 97 % of the column width
    less its margins (0.075 in a side); the header row and a bold first column measured bold."""
    tw = sum(colw)
    return [[lines(c, font, AREA_W * w / tw - 0.15, i == 0 or (j == 0 and bold_first)) for j, (c, w) in enumerate(zip(cells, colw))]
            for i, cells in enumerate(cells_rows)]


def table_rows(cells_rows, colw, font, bold_first):
    """Estimated height of each row (in): its tallest cell at 1.17 em per line, plus 0.05 in above and below.
    deck_qa.py estimates the same way, so a table sized here passes its fit check."""
    return [max(r) * font * 1.17 / 72 + 0.1 for r in table_lines(cells_rows, colw, font, bold_first)]


def fit_table(head, rows, colw, font, bold_first):
    """Grow a table to fill the content area: the largest size from the author's size up to TABLE_MAX_PT
    at which the table still fits and no header cell or row label (first column) wraps onto more lines
    than at the author's size (a bigger font that breaks "where keys live" in two reads worse than the
    smaller one; body cells may wrap), then taller rows (each by at most one line of that size, text
    centred in the row). Returns the size, the row heights, the natural
    height at the author's size and the empty share."""
    cells = [head] + rows
    natural = sum(table_rows(cells, colw, font, bold_first))
    base = table_lines(cells, colw, font, bold_first)
    best = font
    for f in range(int(font) + 1, TABLE_MAX_PT + 1):
        wraps = table_lines(cells, colw, f, bold_first)
        labels = [(wraps[0], base[0])] + [([rw[0]], [rb[0]]) for rw, rb in zip(wraps[1:], base[1:])]
        if any(n > b for rw, rb in labels for n, b in zip(rw, rb)) or sum(table_rows(cells, colw, f, bold_first)) > AREA_H - TABLE_GAP:
            break
        best = f
    hs = table_rows(cells, colw, best, bold_first)
    if sum(hs) > AREA_H - TABLE_GAP:  # too tall even at the author's size: leave it to the warning, no stretch
        return {"font": font, "rowH": None, "natural": natural, "empty": 0.0}
    pad = min((AREA_H - TABLE_GAP - sum(hs)) / len(hs), best * 1.17 / 72)
    hs = [round(h + pad, 3) for h in hs]
    return {"font": best, "rowH": hs, "natural": natural, "empty": 1 - sum(hs) / AREA_H}


def check_fig(fig, bb, where, lint, area, accept=None):
    """Lint one figure against its area. The deck scales the content box uniformly until one side meets the
    area (never stretched: text and circles would distort), so a figure whose proportions differ from the
    area's leaves bands on two sides. The translation does not re-flow a drawing by itself (where a row
    wraps or a legend goes changes what the figure says), so the lint names the proportions to redraw at:
    below FILL_WARN of the area it warns, below FILL_ERR it stops, unless the slide gives a reason
    (data-whitespace="..."), which turns the stop into a warning."""
    vx, vy, vw, vh = fig["vb"]
    if bb[2] < vw * 0.9 or bb[3] < vh * 0.9:
        lint.warn(where, f"loose viewBox {vx:g} {vy:g} {vw:g} {vh:g}; the content is {bb[0]:g} {bb[1]:g} {bb[2]:g} {bb[3]:g} "
                         "(the deck crops it; tighten it so the prototype shows what the deck shows)")
    s = min(area[0] / bb[2], area[1] / bb[3])  # inches per SVG unit
    fill = bb[2] * s * bb[3] * s / (area[0] * area[1])
    if fill < FILL_WARN:
        ar, AR = bb[2] / bb[3], area[0] / area[1]
        if ar > AR:
            shape = f"{ar:.1f} : 1 is wider than the area's {AR:.2f} : 1, so it fills the width and leaves bands above and below"
            redo = f"redraw it near {bb[2]:.0f} x {bb[2] / AR:.0f} units: wrap a long row into two, stack panels, put side labels above or below, enlarge the elements"
        else:
            shape = f"{ar:.2f} : 1 is taller than the area's {AR:.2f} : 1, so it fills the height and leaves bands left and right"
            redo = f"redraw it near {bb[3] * AR:.0f} x {bb[3]:.0f} units: set panels side by side, move a legend or labels beside it"
        msg = f"the figure fills {fill:.0%} of its area ({area[0]} x {area[1]} in): its content {shape}; {redo}"
        if fill < FILL_ERR and not accept:
            lint.err(where, msg + " (or give the slide data-whitespace=\"reason\" to keep it)")
        else:
            lint.warn(where, msg + (f" [kept: {accept}]" if accept else ""))
    sizes = [t["size"] for t in fig["shapes"] if t["t"] == "text"]
    if sizes:
        small = min(sizes) * s * 72
        if small < 9:
            lint.warn(where, f"smallest label scales to {small:.1f} pt; the deck raises it to 12 pt and labels may collide: "
                             "enlarge labels, shorten them, or simplify the figure")
        elif small < 12:
            lint.warn(where, f"smallest label scales to {small:.1f} pt and is raised to 12 pt; check the render for collisions")


def parse(path, png=False, work="."):
    src = open(path, encoding="utf-8").read()
    svgs = []

    def keep(m):
        svgs.append(m.group(0))
        return f'<svgref data-i="{len(svgs) - 1}"></svgref>'
    body = re.sub(r"<svg\b(?![^>]*aria-hidden)[^>]*>.*?</svg>", keep, src, flags=re.S)
    soup = BeautifulSoup(body, "html.parser")
    deck = soup.select_one("main.deck")
    if deck is None:
        sys.exit("no <main class=\"deck\"> in the page: is this a ppt-create prototype?")
    lint = Lint()
    title_tag = soup.find("title")
    meta = {"title": deck.get("data-title") or (clean(title_tag) if title_tag else "Presentation"),
            "subject": deck.get("data-subject", ""), "author": deck.get("data-author", "")}
    parts = [{"id": li.get("data-part"), "label": clean(li.find("b")) or clean(li), "sub": clean(li.find("span"))}
             for li in deck.select("ol.parts-def > li")]
    pid = [p["id"] for p in parts]
    sections = deck.select("section.slide")
    if not parts:
        lint.warn("deck", "no parts list (ol.parts-def): the outline will be empty")
    if not parts or not is_summary(parts[0]):
        lint.err("deck", f"the first part must be {SUMMARY!r} (ol.parts-def): every deck opens, right after the title, "
                         "with a Summary part of one slide titled \"Summary: <core message>\" (proto.py adds the part; "
                         "write the slide with Deck.summary(...))")
    sum_id = parts[0]["id"] if parts and is_summary(parts[0]) else None

    def svgtext(el):
        r = el.find("svgref") if el is not None else None
        return svgs[int(r["data-i"])] if r is not None else None

    slides, n_fig = [], 0
    for sec in sections:
        kind = sec.get("data-kind")
        if kind == "appendix-index" and sec.has_attr("data-auto"):
            continue
        part = sec.get("data-part")
        aid = sec.get("data-appendix")
        canvas = sec.select_one(".canvas")
        where = f"[{len(slides) + 1}] {kind} {clean(canvas.find(['h1', 'h2'])) if canvas else ''}"[:80]
        rec = {"kind": kind, "part": part, "appendix": aid, "notes": notes_of(sec), "src_id": sec.get("id")}
        src_text = clean(sec.select_one(".source"))
        if kind == "title":
            rec.update(title=clean(canvas.find("h1")), subtitle=clean(canvas.select_one(".subtitle")),
                       byline=[clean(p) for p in canvas.select(".byline p")],
                       presenter=clean(canvas.select_one(".presenter")) or "Presenter: ______",
                       date=clean(canvas.select_one(".date")) or "Date: ______")
            # the title slide carries no point list: the key points live only on the Summary slide
            listed = canvas.select("ol, ul, li, .key-points") or [
                p for p in canvas.find_all(["p", "div", "span"]) if LIST_MARK.match(clean(p) or "")]
            if listed:
                lint.err(where, "the title slide has a numbered or bullet point list: it carries only the title, subtitle, "
                                "byline, presenter and date; the key points go on the Summary slide (once, not twice)")
        elif kind in ("outline", "divider"):
            if kind == "divider" and part not in pid:
                lint.err(where, f"divider for unknown part {part!r} (parts: {pid})")
            elif kind == "divider" and part == sum_id:
                lint.err(where, "divider for the Summary part: the outline slide is its divider (drawn with Summary "
                                "highlighted), so this slide would repeat it; remove it")
        elif kind == "closing":
            rec.update(title=clean(canvas.find("h2")) or "Questions", recap=clean(canvas.select_one(".recap")),
                       citation=clean(canvas.select_one(".citation")), questions=[clean(li) for li in canvas.select(".questions > li")])
        elif kind == "content":
            area = canvas.select_one(".area")
            rec.update(title=clean(canvas.find("h2")), bullets=[clean(li) for li in canvas.select(".band > li")],
                       see=sec.get("data-see"), role=sec.get("data-role"), source=src_text)
            fig_el, tab, stats, cards = area.select_one("figure"), area.find("table"), area.select_one(".stats"), area.select_one(".cards")
            st_items = [[clean(s.select_one(".metric")), clean(s.select_one(".label")), "hot" in (s.get("class") or [])]
                        for s in stats.select(".stat")] if stats else []
            if fig_el is not None:
                n_fig += 1
                fid = sec.get("id") or f"fig{n_fig}"
                box = (6.0, AREA_H) if stats else (AREA_W, AREA_H)
                fig = figure_record(svgtext(fig_el), where, lint, area=box, png=png, work=work)
                if fig:
                    fig["bb"] = fig.get("bb") or bounds([fig])
                    if fig["shapes"]:
                        check_fig(fig, fig["bb"], where, lint, box, sec.get("data-whitespace"))
                rec["area"] = {"type": "figure-stats" if stats else "figure", "id": fid, "fig": fig, "items": st_items}
            elif tab is not None:
                head = [clean(th) for th in tab.select("thead th")] or [clean(c) for c in tab.find("tr").find_all(["th", "td"])]
                body_rows = tab.select("tbody tr") or tab.find_all("tr")[1:]
                rows = [{"cells": [clean(td) for td in tr.find_all("td")], "ours": "ours" in (tr.get("class") or [])} for tr in body_rows]
                font = int(tab.get("data-font") or (12 if "dense" in (tab.get("class") or []) else 13))
                colw = [float(v) for v in tab.get("data-colw").split(",")] if tab.get("data-colw") else None
                if not colw:  # relative widths from the longest cell of each column
                    colw = [max([len(head[j])] + [len(r["cells"][j]) for r in rows if j < len(r["cells"])]) + 4 for j in range(len(head))]
                if font < 12:
                    lint.err(where, f"table at {font} pt: the floor is 13 pt (12 for a dense setup table); split the table or move rows to the appendix")
                bold_first = tab.get("data-bold-first") != "false"
                fit = fit_table(head, [r["cells"] for r in rows], colw, font, bold_first)
                rec["area"] = {"type": "table", "head": head, "rows": rows, "colW": colw, "fontSize": fit["font"],
                               "rowH": fit["rowH"], "boldFirst": bold_first, "dense": font < 13,
                               "name": sec.get("id") or f"table{len(slides) + 1}"}
                if fit["natural"] > AREA_H:
                    lint.warn(where, f"table about {fit['natural']:.1f} in tall at {font} pt, the area is {AREA_H} in: shorten cells, split it, or move rows to the appendix")
                elif fit["empty"] > TABLE_EMPTY_WARN:
                    lint.warn(where, f"the table fills only {1 - fit['empty']:.0%} of the area even at {fit['font']} pt with taller rows: "
                                     "add the rows or columns the talk needs, or say it with a figure or headline numbers")
            elif stats is not None:
                rec["area"] = {"type": "stats", "items": st_items}
            elif cards is not None:
                rec["area"] = {"type": "cards", "items": [[clean(li.find("b")), clean(li.find("span"))] for li in cards.select("li")]}
            else:
                lint.err(where, "content slide without a figure, table, stats or cards in .area")
            nb_ = len(rec["bullets"])
            if nb_ == 0:
                lint.warn(where, "no band bullets (2-3 supporting sentences)")
            elif nb_ > 3:
                lint.warn(where, f"{nb_} bullets: keep 2-3, the rest goes to the notes")
            nl = sum(lines(b, 16, BAND_W - BAND_MARL) for b in rec["bullets"]) if rec["bullets"] else 0
            if nl > 4:
                lint.warn(where, f"band needs {nl} lines at 16 pt (4 fit): shorten the bullets, the full text goes to the notes")
        elif kind == "story":
            frames, fnotes = [], []
            items = sec.select("ol.storyboard > li.frame")
            if len(items) < 2:
                lint.warn(where, f"storyboard with {len(items)} frame(s)")
            for i, li in enumerate(items):
                f = figure_record(svgtext(li), f"{where} frame {i + 1}", lint, timeline=True, area=(FAREA_W, FAREA_H))
                if f is None:
                    continue
                f.update(title=li.get("data-step") or f"Step {i + 1}", caption=clean(li.select_one(".frame-caption")))
                frames.append(f)
                fn = notes_of(li)
                fnotes.append(fn)
                if not fn:
                    lint.err(f"{where} frame {i + 1}", "no speaker notes")
                if lines(f["caption"], 16, CAP_W) > 10:
                    lint.warn(f"{where} frame {i + 1}", "step caption over 10 lines at 16 pt in the 2.25 in column: shorten it")
                if lines(f["title"], 16, CAP_W, True) > 2:
                    lint.warn(f"{where} frame {i + 1}", "step title over 2 lines: shorten data-step")
            if frames:
                bb = bounds(frames)
                for f in frames:
                    f["bb"] = bb
                check_fig(frames[0], bb, where, lint, (FAREA_W, FAREA_H), sec.get("data-whitespace"))
                counts = unkeyed_counts(frames)
                if len(set(counts)) > 1:
                    lint.err(where, f"unkeyed elements per frame {counts}: Morph pairs them by order, so give data-key to "
                                    "every element that appears, disappears or changes, or hide it with class 'off'")
            if rec["notes"] and fnotes:
                fnotes[0] = (rec["notes"] + " " + fnotes[0]).strip()
            n_fig += 1
            rec.update(title=clean(canvas.find("h2")), frames=frames, notes=fnotes, see=sec.get("data-see"),
                       role=sec.get("data-role"), source=src_text, id=sec.get("id") or f"story{n_fig}")
        else:
            lint.err(where, f"unknown data-kind {kind!r}")
            continue
        # every slide: title length, notes, provenance words
        t = rec.get("title") or ""
        if kind in ("content", "story") and width_in((aid + " · " if aid else "") + t, 20, True) > 8.5 * 0.97:
            lint.warn(where, "title longer than one 20 pt line: shorten it (one core message, few words)")
        if kind != "story" and not rec["notes"] and kind not in ("outline", "divider"):
            lint.err(where, "no speaker notes (write the script under the slide)")
        if kind in ("outline", "divider") and not rec["notes"]:
            lint.warn(where, "no speaker notes")
        words = len(rec["notes"].split()) if isinstance(rec["notes"], str) else 0
        if kind in ("content", "title", "closing") and rec["notes"] and not 40 <= words <= 300:
            lint.warn(where, f"notes are {words} words (40-300 reads well as a script)")
        on_slide = " ".join([t] + rec.get("bullets", []) + [rec.get("recap", ""), rec.get("subtitle", "")])
        if rec.get("area", {}).get("type") in ("figure", "figure-stats") and rec["area"].get("fig"):
            on_slide += " " + " ".join(s["s"] for s in rec["area"]["fig"]["shapes"] if s["t"] == "text")
        for f in rec.get("frames", []):
            on_slide += " " + f["caption"] + " " + " ".join(s["s"] for s in f["shapes"] if s["t"] == "text")
        m = TAGS.search(on_slide)
        if m:
            lint.err(where, f"provenance on the slide ({m.group(0)!r}): move it to .source (it goes to the notes)")
        slides.append(rec)

    # ---------------------------------------------------------------- structure: outline, dividers, closing, appendix
    out = []
    kinds = [s["kind"] for s in slides]
    if not slides or kinds[0] != "title":
        lint.err("deck", "the first slide must be the title slide (data-kind=\"title\")")
    if "closing" not in kinds:
        lint.err("deck", "no closing slide (data-kind=\"closing\")")
    has_outline = "outline" in kinds
    divided = {s["part"] for s in slides if s["kind"] == "divider"}
    seen = set()
    for s in slides:
        if s["appendix"]:
            continue
        if s["kind"] == "title":
            out.append(s)
            if not has_outline:
                lint.warn("deck", "no outline slide: added after the title, without notes")
                out.append({"kind": "outline", "part": "Opening", "notes": "", "appendix": None})
            continue
        p = s["part"]
        if p in pid and p not in seen and s["kind"] != "divider" and p not in divided and p != sum_id:
            lint.warn("deck", f"part {p!r} has no divider slide: added, without notes")
            out.append({"kind": "divider", "part": p, "notes": "", "appendix": None})
        if p in pid:
            seen.add(p)
        out.append(s)
    closing_at = next((i for i, s in enumerate(slides) if s["kind"] == "closing"), len(slides))
    for i, s in enumerate(slides):
        if s["appendix"] and i < closing_at:
            lint.err(f"appendix {s['appendix']}", "appendix slides go after the closing slide")
        if not s["appendix"] and i > closing_at:
            lint.err(f"[{i + 1}] {s['kind']}", "a main slide after the closing slide: move it before, or make it an appendix slide")
    for p in pid:
        if p not in seen and p != sum_id:
            lint.warn("deck", f"part {p!r} has no slides")
    # the Summary part: right after the outline, one slide, titled "Summary: <core message>"
    if sum_id:
        main_ = [s for s in out if not s["appendix"] and s["kind"] not in ("title", "outline")]
        summ = [s for s in main_ if s["part"] == sum_id and s["kind"] in ("content", "story")]
        if not summ:
            lint.err("deck", f"no summary slide: give the part {sum_id!r} one content slide titled \"Summary: <core message>\", "
                             "right after the outline (Deck.summary(...))")
        elif main_[0] is not summ[0]:
            lint.err(f"{main_[0]['kind']} {(main_[0].get('title') or '')[:40]}",
                     "the summary slide must come right after the outline (title, outline, summary, then the parts)")
        for s in summ:
            if not (s.get("title") or "").startswith(SUMMARY):
                lint.err(f"{s['kind']} {(s.get('title') or '')[:40]}", f"the summary slide's title must start with {SUMMARY!r}: "
                                                                     "\"Summary: <core message>\", one 20 pt line (shorten the message; the full one goes to the notes)")
        if len(summ) > 1:
            lint.warn("deck", f"the Summary part has {len(summ)} slides: keep the talk's summary on one slide")
    appx = [s for s in slides if s["appendix"]]
    ids = [s["appendix"] for s in appx]
    for s in out:
        if s.get("see") and s["see"] not in ids:
            lint.err(f"{s['kind']} {s.get('title', '')[:40]}", f"points to appendix {s['see']!r}, which does not exist")
    for a in ids:
        if not any(s.get("see") == a for s in out):
            lint.warn(f"appendix {a}", "no main slide points to it (data-see)")
    # results without methodology
    has_result = any(s.get("role") == "result" or re.search(r"evaluat|result", (s.get("part") or ""), re.I) for s in out)
    has_method = any(s.get("role") == "method" or re.search(r"method|setup", s.get("title") or "", re.I) for s in out)
    if has_result and not has_method:
        lint.warn("deck", "results without a methodology / setup slide: add one or two before the results (data-role=\"method\")")

    # deck slide numbers (a storyboard spans one slide per frame), for "from slide N"
    def span(s):
        return max(1, len(s.get("frames", []))) if s["kind"] == "story" else 1
    no, first = 0, {}
    for s in out:
        first[id(s)] = no + 1
        no += span(s)
    if appx:
        items = []
        for a in appx:
            src = next((s for s in out if s.get("see") == a["appendix"]), None)
            items.append([a.get("title", ""), f"from slide {first[id(src)]}" if src else "", a["appendix"]])
        script = "The appendix holds the details behind the main slides: " + "; ".join(
            f"{m} {t}" + (f", {f}" if f else "") for t, f, m in items) + "."
        out.append({"kind": "appendix-index", "part": "Appendix", "notes": script, "appendix": "index", "items": items})
        for a in appx:
            src = next((s for s in out if s.get("see") == a["appendix"]), None)
            back = f" (Back to slide {first[id(src)]}: {src.get('title', '')}.)" if src else ""
            if a["kind"] == "story":
                a["notes"][-1] = a["notes"][-1] + back
            else:
                a["notes"] = a["notes"] + back
            out.append(a)
    # sections: the opening (the title and slides outside every part), one per part (the outline opens the
    # Summary part: it is that part's divider, with Summary highlighted), the appendix
    for s in out:
        if s["appendix"]:
            s["section"] = "Appendix"
        elif s["kind"] == "closing":
            s["section"] = s["part"] if s["part"] in pid else (pid[-1] if pid else "Closing")
        elif s["kind"] == "outline":
            s["section"] = sum_id or "Opening"
            s["partIndex"] = 0 if sum_id else -1
        elif s["kind"] == "title" or s["part"] not in pid:
            s["section"] = "Opening"
        else:
            s["section"] = s["part"]
        if s["kind"] == "divider":
            s["partIndex"] = pid.index(s["part"]) if s["part"] in pid else -1
    return {"meta": meta, "parts": parts, "slides": out, "deckSlides": no + sum(span(a) for a in appx) + (1 if appx else 0)}, lint


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html")
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--check", action="store_true", help="lint only")
    ap.add_argument("--work", default=os.environ.get("DECK_WORK", ".deck_work"))
    ap.add_argument("--png-fallback", action="store_true", help="embed figures outside the vocabulary as pictures")
    a = ap.parse_args()
    os.makedirs(a.work, exist_ok=True)
    spec, lint = parse(a.html, png=a.png_fallback, work=a.work)
    for m in lint.errors + lint.warns:
        print(m)
    print(f"{len(spec['slides'])} spec slides -> {spec['deckSlides']} deck slides; {len(lint.errors)} errors, {len(lint.warns)} warnings")
    if lint.errors:
        sys.exit(1)
    if a.check:
        return
    if not a.spec:
        sys.exit("give SPEC.json (or --check)")
    with open(a.spec, "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    print(a.spec)


if __name__ == "__main__":
    main()
