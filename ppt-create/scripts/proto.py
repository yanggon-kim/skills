#!/usr/bin/env python3
"""Mode 1: write the HTML prototype of a talk (references/html-prototype.md) from Python or from JSON.

From Python (the usual route: figures are easier to draw with the helpers):
    import sys; sys.path.insert(0, "<skill>/scripts")
    from proto import Deck, Frame, Table, svg, R, T, L, PL, C, E, G
    d = Deck("Talk title", subject="One line on the talk", author="Name",   # part 1, "Summary", is built in
             paper="A. Author et al., Title, Venue 2026")   # a deck about a paper: its Background part is required
    d.preliminary(sub="optional: presenter's DRAM primer, not the paper")    # only on request: always part 2
    d.part("Background", "Background", "the paper's Section II, in its order")
    d.title_slide(title="Talk title", subtitle="...", byline=["Authors", "Venue, year"], notes="script ...")
                                         # title, subtitle, byline, presenter, date only: no key points
    d.outline(notes="script ...")        # the outline, with Summary highlighted: also the Summary divider
    d.summary("core message of the talk", figure=svg(...), bullets=[...], notes="script ...")  # "Summary: ..."
    d.divider("Preliminary", notes="script ...")            # its slides: part="Preliminary"
    d.divider("Background", notes="script ...")
    d.content("One-line core message", part="Background", figure=svg("0 0 640 300", R(...) + T(...)),
              bullets=["...", "..."], notes="script ...", source="Redrawn from ...", see="A1", role="method")
    d.story("One-line message", part="Background", frames=[Frame("Step title", svg(...), "caption", "script")])
    d.closing(title="Questions", recap="...", citation="...", questions=["...", "..."], notes="...")
    d.appendix("A1", "Full results table", table=Table(head, rows, colw=[...]), bullets=[...], notes="...")
    d.write("talk.html")

From JSON:  python3 proto.py CONTENT.json OUT.html
    {"title": .., "subject": .., "author": .., "paper": .., "parts": [{"id", "label", "sub", "preliminary"}],
     "slides": [{"kind": "title" | "outline" | "summary" | "divider" | "content" | "story" | "closing", ...}]}
    ("summary" takes the content fields with "message" in place of "title"; "parts" may omit Summary)
    with the same fields as the methods below ("figure" is an SVG string; a story's "frames" are
    {"step", "svg", "caption", "notes"}; a table is {"head", "rows", "colw", "font", "ours", "dense"}).

The writer only formats; the rules (one message per slide, 2-3 bullets, figure first, notes as a script,
provenance in .source, details to the appendix) are the author's. Every deck's first part is "Summary"
(added automatically; d.part("Summary", label, sub) re-labels it): the outline right after the title is
its divider, and the summary slide (d.summary) follows it, titled "Summary: <core message>". Missing
outline or divider slides are added with a warning, a missing summary slide is warned about here and
stops html_to_spec.py; appendix slides always go after the closing slide.

Background and the Preliminary Note. In a deck about a paper (Deck(paper=...)), "Background" is always the
paper's own background section, in the paper's order; html_to_spec.py stops on a paper deck without it. A
primer the presenter adds on request, for an audience that lacks the basics, is a separate optional part,
the Preliminary Note (d.preliminary()): always part 2, between Summary and Background, every slide of it
tagged as the presenter's material ("Preliminary note · presenter's primer, not the paper"), its provenance
its own sources, never the paper. A primer is never relabelled as the paper's Background, and the paper's
Background is never dropped because a primer exists.
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY = "Summary"  # the first part of every deck (html_to_spec.py stops on a deck without it)
PRELIM = "Preliminary"  # the optional presenter's primer: part 2, between Summary and Background
PRELIM_TAG = "Preliminary note · presenter's primer, not the paper"  # on every slide of it (deck_lib.js too)
TEMPLATE = os.path.join(os.path.dirname(HERE), "assets", "prototype-template.html")
E_ = html.escape


# ---------------------------------------------------------------- SVG helpers (the figure vocabulary)
def _k(key):
    return f' data-key="{E_(key)}"' if key else ""


def _n(v):
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def R(x, y, w, h, cls="f-white s-ink", key=None):
    """Rectangle. cls: one fill class (f-white f-idle f-ink f-accent f-tint f-c2 f-c3 f-pencil f-none) and
    optionally a stroke class (s-ink s-pencil s-accent s-c2 s-c3) plus 'thick' / 'dashed' / 'off' ('grid' on a gridline:
    the deck cuts it at labels)."""
    return f'<rect{_k(key)} x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" class="{cls}"></rect>'


def T(x, y, s, cls="t-label", anchor="start", key=None, size=None):
    """Text at its baseline. cls: t-label t-mono t-head t-accent t-onbar (t-onbar only on dark fills)."""
    fs = f' font-size="{_n(size)}"' if size else ""
    return f'<text{_k(key)} x="{_n(x)}" y="{_n(y)}" text-anchor="{anchor}" class="{cls}"{fs}>{E_(s)}</text>'


def _marker(cls):
    for c, m in (("s-accent", "arrow-accent"), ("s-c2", "arrow-c2"), ("s-teal", "arrow-c2"), ("s-pencil", "arrow-pencil")):
        if c in cls.split():
            return m
    return "arrow"


def L(x1, y1, x2, y2, cls="s-ink", key=None, arrow=False):
    m = f' marker-end="url(#{_marker(cls)})"' if arrow else ""
    return f'<line{_k(key)} x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" class="{cls}"{m}></line>'


def PL(points, cls="s-ink f-none", key=None, arrow=False):
    m = f' marker-end="url(#{_marker(cls)})"' if arrow else ""
    pts = " ".join(f"{_n(x)},{_n(y)}" for x, y in points)
    return f'<polyline{_k(key)} points="{pts}" class="{cls}"{m}></polyline>'


def C(cx, cy, r, cls="f-white s-ink", key=None):
    return f'<circle{_k(key)} cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}" class="{cls}"></circle>'


def E(cx, cy, rx, ry, cls="f-white s-ink", key=None):
    return f'<ellipse{_k(key)} cx="{_n(cx)}" cy="{_n(cy)}" rx="{_n(rx)}" ry="{_n(ry)}" class="{cls}"></ellipse>'


def G(body, dx=0, dy=0, cls="", key=None):
    """A group; dx/dy translate it; cls 'hot' (highlighted) or 'pend' (still to come) restyles its rect and text."""
    tr = f' transform="translate({_n(dx)} {_n(dy)})"' if (dx or dy) else ""
    c = f' class="{cls}"' if cls else ""
    return f"<g{_k(key)}{c}{tr}>{body}</g>"


def svg(vb, body, title="", desc="", text_scale=None):
    """An inline SVG figure. vb: a tight viewBox "x y w h" around the drawing (the deck crops to content anyway)."""
    ts = f' data-text-scale="{_n(text_scale)}"' if text_scale else ""
    t = f"<title>{E_(title)}</title>" if title else ""
    d = f"<desc>{E_(desc)}</desc>" if desc else ""
    return f'<svg viewBox="{vb}" role="img"{ts}>{t}{d}{body}</svg>'


# ---------------------------------------------------------------- content records
class Frame:
    def __init__(self, step, svgtext, caption, notes):
        self.step, self.svg, self.caption, self.notes = step, svgtext, caption, notes


def _attrs(see, role, whitespace):
    return ((f' data-see="{E_(see)}"' if see else "") + (f' data-role="{E_(role)}"' if role else "")
            + (f' data-whitespace="{E_(whitespace)}"' if whitespace else ""))


class Table:
    """head: [..]; rows: [[cells]]; colw: relative widths; font: 13 or 14 (12 with dense=True);
    ours: row indexes to highlight; bold_first: bold first column."""

    def __init__(self, head, rows, colw=None, font=13, ours=(), dense=False, bold_first=True):
        self.head, self.rows, self.colw, self.font, self.ours = head, rows, colw, font, set(ours)
        self.dense, self.bold_first = dense, bold_first

    def html(self):
        attrs = [f'data-font="{12 if self.dense else self.font}"']
        if self.colw:
            attrs.append(f'data-colw="{",".join(_n(c) for c in self.colw)}"')
        if not self.bold_first:
            attrs.append('data-bold-first="false"')
        cls = ' class="dense"' if self.dense else ""
        head = "".join(f"<th>{E_(h)}</th>" for h in self.head)
        ours = ' class="ours"'
        rows = "".join(f"<tr{ours if i in self.ours else ''}>" + "".join(f"<td>{E_(c)}</td>" for c in r) + "</tr>"
                       for i, r in enumerate(self.rows))
        return f'<table{cls} {" ".join(attrs)}><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>'


def _notes(text, open_=True, summary="Speaker notes"):
    if not text:
        return ""
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    o = " open" if open_ else ""
    return f'<details class="notes"{o}><summary>{E_(summary)}</summary>' + "".join(f"<p>{E_(p)}</p>" for p in paras) + "</details>"


def _source(text):
    return f'<p class="source">{E_(text)}</p>' if text else ""


def _bullets(items):
    return '<ul class="band">' + "".join(f"<li>{E_(b)}</li>" for b in items) + "</ul>"


class Deck:
    def __init__(self, title, subject="", author="", paper=""):
        """paper: the source paper's citation when the talk presents a paper; the deck must then have a
        "Background" part that is the paper's own background (html_to_spec.py stops without it)."""
        self.title, self.subject, self.author, self.paper = title, subject, author, paper
        self.parts = [(SUMMARY, SUMMARY, "the talk in one slide")]  # (id, label, sub); Summary is always first
        self.prelim = False
        self.slides = []  # (kind, part, html)
        self.appendix_slides = []
        self.warnings = []

    def part(self, pid, label=None, sub=""):
        if pid == SUMMARY:  # re-label the built-in first part; it stays first
            self.parts[0] = (SUMMARY, label or SUMMARY, sub or self.parts[0][2])
            return
        if pid == PRELIM:
            self.preliminary(label or "Preliminary Note", sub)
            return
        self.parts.append((pid, label or pid, sub))

    def preliminary(self, label="Preliminary Note", sub="optional: the presenter's primer, not the paper"):
        """The optional Preliminary Note: a primer the presenter adds on request for an audience that lacks the
        basics. It is always part 2 (right after Summary, before Background), whenever this is called; its slides
        (part="Preliminary") carry the tag PRELIM_TAG, and their .source names the primer's own sources, never
        the paper. It never replaces the paper's Background."""
        self.parts = [p for p in self.parts if p[0] != PRELIM]
        self.parts.insert(1, (PRELIM, label, sub))
        self.prelim = True

    def _add(self, kind, part, body, attrs=""):
        if part == PRELIM:
            attrs += ' data-preliminary="true"'
        sec = f'<section class="slide" data-kind="{kind}"' + (f' data-part="{E_(part)}"' if part else "") + f"{attrs}>{body}</section>"
        self.slides.append((kind, part, sec))

    def title_slide(self, title, subtitle="", byline=(), notes="", presenter="Presenter: ______", date="Date: ______", part="Opening",
                    points=None):
        """The Title Opener: title, subtitle, byline, presenter and date, nothing else. The talk's key points
        belong on the Summary slide only (d.summary), so the opening never says them twice: a point list is refused."""
        if points:
            raise ValueError("title_slide takes no point list: the key points go on the Summary slide only (d.summary)")
        by = "".join(f"<p>{E_(b)}</p>" for b in byline)
        body = (f'<div class="canvas"><h1>{E_(title)}</h1>' + (f'<p class="subtitle">{E_(subtitle)}</p>' if subtitle else "")
                + (f'<div class="byline">{by}</div>' if by else "") + f'<p class="presenter">{E_(presenter)}</p>'
                + f'<p class="date">{E_(date)}</p></div>' + _notes(notes))
        self._add("title", part, body)

    def outline(self, notes="", part=SUMMARY):
        """The outline: every part listed, Summary (part 1) highlighted. It is also the Summary part's divider,
        so its script names the parts and then introduces the summary slide."""
        self._add("outline", part, '<div class="canvas"></div>' + _notes(notes))

    def divider(self, pid, notes=""):
        if pid == SUMMARY:
            self.warnings.append("no divider for the Summary part: the outline is its divider (divider dropped)")
            return
        self._add("divider", pid, '<div class="canvas"></div>' + _notes(notes))

    def summary(self, message, **kw):
        """The summary slide, right after the outline: the whole talk on one content slide (figure or numbers
        first, 2-3 bullets). Its title is "Summary: <message>" and must stay one 20 pt line, so the message is
        short; the full message goes in the notes. Takes the content() fields."""
        title = message if message.startswith(SUMMARY) else f"{SUMMARY}: {message}"
        self.content(title, part=SUMMARY, **kw)

    def _area(self, figure=None, table=None, stats=None, cards=None):
        inner = ""
        if figure:
            inner += f'<figure class="visual">{figure}</figure>'
        if table is not None:
            inner += table.html() if isinstance(table, Table) else table
        if stats:
            inner += '<div class="stats">' + "".join(
                f'<div class="stat{" hot" if (len(s) > 2 and s[2]) else ""}"><b class="metric">{E_(s[0])}</b>'
                f'<span class="label">{E_(s[1])}</span></div>' for s in stats) + "</div>"
        if cards:
            inner += '<ol class="cards">' + "".join(f"<li><b>{E_(h)}</b><span>{E_(t)}</span></li>" for h, t in cards) + "</ol>"
        return f'<div class="area">{inner}</div>'

    def content(self, title, part=None, figure=None, table=None, stats=None, cards=None, bullets=(), notes="",
                source="", see=None, role=None, whitespace=None):
        """A figure-first slide: the area holds a figure, a table, headline numbers, cards, or a figure with
        up to four numbers beside it; 2-3 bullets go in the band. role: 'method' or 'result' (lint hints).
        whitespace: a reason, when a figure must keep proportions that leave over half its area empty (the
        lint then warns instead of stopping)."""
        attrs = _attrs(see, role, whitespace)
        body = (f'<div class="canvas"><h2>{E_(title)}</h2>{self._area(figure, table, stats, cards)}{_bullets(bullets)}</div>'
                + _notes(notes) + _source(source))
        self._add("content", part, body, attrs)

    def story(self, title, frames, part=None, notes="", source="", see=None, role=None, whitespace=None):
        """A storyboard: one deck slide per frame, joined by Morph. notes: an optional overview (goes before the
        first frame's script). whitespace: as for content()."""
        attrs = _attrs(see, role, whitespace)
        lis = "".join(f'<li class="frame" data-step="{E_(f.step)}">{f.svg}<p class="frame-caption">{E_(f.caption)}</p>'
                      f'{_notes(f.notes, open_=False, summary="notes")}</li>' for f in frames)
        body = (f'<div class="canvas"><h2>{E_(title)}</h2><div class="farea"></div><div class="stepcol"></div></div>'
                f'<ol class="storyboard">{lis}</ol>' + _notes(notes, summary="Overview (added to frame 1's notes)") + _source(source))
        self._add("story", part, body, attrs)

    def closing(self, title="Questions", recap="", citation="", questions=(), notes="", part=None):
        qs = "".join(f"<li>{E_(q)}</li>" for q in questions)
        body = (f'<div class="canvas"><h2>{E_(title)}</h2>' + (f'<p class="recap">{E_(recap)}</p>' if recap else "")
                + (f'<p class="citation">{E_(citation)}</p>' if citation else "") + (f'<ol class="questions">{qs}</ol>' if qs else "")
                + "</div>" + _notes(notes))
        self._add("closing", part or (self.parts[-1][0] if self.parts else None), body)

    def appendix(self, aid, title, frames=None, **kw):
        """An appendix slide (after the closing slide): full tables, extra numbers, derivations, per-case
        breakdowns. Point to it from a main slide with see=aid."""
        n = len(self.slides)
        if frames:
            self.story(title, frames, part="Appendix", **kw)
        else:
            self.content(title, part="Appendix", **kw)
        kind, part, sec = self.slides.pop(n)
        self.appendix_slides.append(sec.replace('<section class="slide"', f'<section class="slide" data-appendix="{E_(aid)}"', 1))

    def html_body(self):
        order = []
        kinds = [k for k, _, _ in self.slides]
        if "title" not in kinds:
            self.warnings.append("no title slide")
        have_outline = "outline" in kinds
        dividers = {p for k, p, _ in self.slides if k == "divider"}
        seen = set()
        for kind, part, sec in self.slides:
            if kind == "title":
                order.append(sec)
                if not have_outline:
                    order.append('<section class="slide" data-kind="outline" data-part="Summary"><div class="canvas"></div></section>')
                    self.warnings.append("outline added without notes: give it a script (Deck.outline(notes=...))")
                continue
            ids = [p[0] for p in self.parts]
            if part in ids and part not in seen and kind != "divider" and part != SUMMARY:
                if part not in dividers:
                    order.append(f'<section class="slide" data-kind="divider" data-part="{E_(part)}"><div class="canvas"></div></section>')
                    self.warnings.append(f"divider for part {part!r} added without notes")
            if part in ids:
                seen.add(part)
            order.append(sec)
        if "closing" not in kinds:
            self.warnings.append("no closing slide")
        if not any(k in ("content", "story") and p == SUMMARY for k, p, _ in self.slides):
            self.warnings.append("no summary slide: add Deck.summary(message, ...) after the outline (html_to_spec.py stops without it)")
        if self.paper and not any(p[0] == "Background" or p[1].startswith("Background") for p in self.parts):
            self.warnings.append("a deck about a paper needs a 'Background' part: the paper's own background, in its order "
                                 "(html_to_spec.py stops without it); a presenter's primer goes in d.preliminary(), not there")
        if self.prelim and not any(p == PRELIM and k in ("content", "story") for k, p, _ in self.slides):
            self.warnings.append("the Preliminary Note part has no slides")
        order += self.appendix_slides
        parts = "".join(f'<li data-part="{E_(i)}"' + (' data-preliminary="true"' if i == PRELIM else "")
                        + f'><b>{E_(l)}</b><span>{E_(s)}</span></li>' for i, l, s in self.parts)
        paper = f' data-paper="{E_(self.paper)}"' if self.paper else ""
        return (f'<main class="deck" data-title="{E_(self.title)}" data-subject="{E_(self.subject)}" data-author="{E_(self.author)}"{paper}>'
                f'<ol class="parts-def">{parts}</ol>\n' + "\n".join(order) + "\n</main>")

    def write(self, path):
        tpl = open(TEMPLATE, encoding="utf-8").read()
        page = tpl.replace("{{DECK_TITLE}}", E_(self.title)).replace("{{DECK_BODY}}", self.html_body())
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        for w in self.warnings:
            print("WARN", w)
        print(path, len(page), "bytes,", len(self.slides) + len(self.appendix_slides), "slides")
        return path


def from_json(spec):
    d = Deck(spec["title"], spec.get("subject", ""), spec.get("author", ""), spec.get("paper", ""))
    for p in spec.get("parts", []):
        if p.get("preliminary"):
            d.preliminary(p.get("label") or "Preliminary Note", p.get("sub", ""))
        else:
            d.part(p["id"], p.get("label"), p.get("sub", ""))
    for s in spec["slides"]:
        s = dict(s)
        kind = s.pop("kind")
        if isinstance(s.get("table"), dict):
            t = s["table"]
            s["table"] = Table(t["head"], t["rows"], t.get("colw"), t.get("font", 13), t.get("ours", ()), t.get("dense", False),
                               t.get("bold_first", True))
        if "frames" in s:
            s["frames"] = [Frame(f["step"], f["svg"], f["caption"], f.get("notes", "")) for f in s["frames"]]
        if kind == "title":
            d.title_slide(**s)
        elif kind == "outline":
            d.outline(**s)
        elif kind == "divider":
            d.divider(s.pop("part"), **s)
        elif kind == "summary":
            d.summary(s.pop("message"), **s)
        elif kind == "content":
            d.content(**s)
        elif kind == "story":
            d.story(**s)
        elif kind == "closing":
            d.closing(**s)
        elif kind == "appendix":
            d.appendix(s.pop("id"), s.pop("title"), **s)
        else:
            raise ValueError(f"unknown slide kind {kind!r}")
    return d


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    from_json(json.load(open(sys.argv[1], encoding="utf-8"))).write(sys.argv[2])
