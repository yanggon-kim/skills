#!/usr/bin/env python3
"""Mechanical checks for a concept-explainer page.

Usage: python3 check_page.py page.html [--json]

Reports three groups of findings:
  contract  - artifact page-contract problems (skeleton tags, CDN, theme tokens, leftover slots)
  structure - the parts a concept-explainer page needs (figures, interaction, sections, and the
              closing "expert's version of your question")
  ladder    - the figure ladder: concept blocks in "What you already know", each with a figure that
              builds on an earlier block's figure (shared data-key elements), and mechanism figures
              that continue from the ladder
  technique - each ladder block names its chosen technique (data-technique) and its markup matches:
              contrast/sweep/extremes need 2+ g.case panels, analogy a p.breaks sentence (and
              only one, in "What you already know"), cause-chain arrows, sequence a timeline
  foreshadow- one or two p.foreshadow hints in the ladder, each recalled later by data-recalls
  voice     - sentence length, passive-voice suspects, filler and hype words
              (Korean is counted in space-separated eojeol, with a lower long-sentence limit)

ERROR findings must be fixed. WARN findings are for judgment. Exit code 1 if any ERROR.
Standard library only.
"""

import json
import re
import sys
from html.parser import HTMLParser

ALLOWED_SCRIPT_HOSTS = (
    "https://cdnjs.cloudflare.com/",
    "https://cdn.jsdelivr.net/npm/",
    "https://unpkg.com/",
    "https://cdn.tailwindcss.com",
    "https://code.jquery.com/",
)
ALLOWED_STYLE_HOSTS = ("https://fonts.googleapis.com/",)
TECHNIQUES = {"contrast", "sweep", "extremes", "sequence", "cause-chain", "analogy", "scale"}
EXPECTED_SECTIONS = ["familiar", "problem", "mechanism", "try", "result", "misconception", "recap", "deeper"]
PROSE_TAGS = {"p", "li", "dd", "dt", "summary", "figcaption", "h1", "h2", "h3", "blockquote"}
SKIP_TAGS = {"script", "style", "svg", "code", "pre", "kbd", "title"}

FILLER_EN = [
    "simply", "just", "basically", "essentially", "actually", "it is worth noting", "it's worth noting",
    "it is important to note", "in other words", "powerful", "revolutionary", "game-changing",
    "game changer", "cutting-edge", "seamless", "seamlessly", "magic", "magical", "in today's",
    "have you ever wondered", "let's dive", "dive into", "delve", "leverage", "utilize", "commence",
]
FILLER_KO = ["기본적으로", "사실상", "그냥", "단순히 말해", "혁신적", "강력한"]
PASSIVE_EN = re.compile(
    r"\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?"
    r"(?:\w+ed|built|made|done|sent|kept|held|run|set|put|written|known|shown|given|taken|seen|"
    r"found|left|lost|paid|split|hidden|chosen|thrown|drawn|stored|broken)\b",
    re.I,
)
PASSIVE_KO = re.compile(r"(되어지|되어진|이루어지|이루어진|시켜지|되어져)")
HANGUL = re.compile(r"[가-힣]")


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.skip_depth = 0
        self.prose_depth = 0
        self.blocks = []          # (tag, class, text, in_deeper) for prose blocks
        self.sections = []        # ids of the open <section> elements
        self.current = []
        self.tags = []            # (tag, attrs)
        self.svg_count = 0
        self.svg_info = []        # dict per svg
        self.in_svg = 0
        self.ids = set()
        self.classes = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append((tag, a))
        if a.get("id"):
            self.ids.add(a["id"])
        for c in (a.get("class") or "").split():
            self.classes.add(c)
        if tag == "svg" and a.get("aria-hidden") == "true":
            pass                          # a hidden defs-only svg (shared markers) is not a diagram
        elif tag == "svg":
            self.svg_count += 1
            self.in_svg += 1
            self.svg_info.append({"role": a.get("role"), "title": False, "desc": False,
                                  "literal_colors": 0, "viewBox": "viewBox" in a or "viewbox" in a})
        elif self.in_svg and self.svg_info:
            if tag == "title":
                self.svg_info[-1]["title"] = True
            if tag == "desc":
                self.svg_info[-1]["desc"] = True
            for k in ("fill", "stroke"):
                v = (a.get(k) or "").strip().lower()
                if v.startswith("#") or v.startswith("rgb") or v in ("black", "white", "red", "blue", "green", "gray", "grey"):
                    self.svg_info[-1]["literal_colors"] += 1
            if re.search(r"(fill|stroke)\s*:\s*(#|rgb)", a.get("style") or "", re.I):
                self.svg_info[-1]["literal_colors"] += 1
        if tag == "section":
            self.sections.append(a.get("id") or "")
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag in PROSE_TAGS and not self.skip_depth:
            if self.prose_depth == 0:
                self.current = []
                self.current_tag = tag
                self.current_class = a.get("class") or ""
                self.current_deeper = "deeper" in self.sections
            self.prose_depth += 1
        if tag in ("br",) and self.prose_depth:
            self.current.append(" ")

    def handle_endtag(self, tag):
        if tag == "section" and self.sections:
            self.sections.pop()
        if tag == "svg" and self.in_svg:
            self.in_svg -= 1
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag in PROSE_TAGS and self.prose_depth and not self.skip_depth:
            self.prose_depth -= 1
            if self.prose_depth == 0:
                text = re.sub(r"\s+", " ", "".join(self.current)).strip()
                if text:
                    self.blocks.append((self.current_tag, self.current_class, text, self.current_deeper))

    def handle_data(self, data):
        if self.prose_depth and not self.skip_depth:
            self.current.append(data)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?。])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


def check_timeline(nc, add_outer, tag=""):
    def add(level, group, msg):
        add_outer(level, group, tag + msg)
    frames = re.findall(r'<li[^>]*class="[^"]*\bframe\b[^"]*"[^>]*>(.*?)</li>', nc, re.S)
    if len(frames) < 2:
        add("ERROR", "timeline", f"{len(frames)} storyboard frame(s); a timeline needs at least 2")
        return
    if len(frames) > 12:
        add("WARN", "timeline", f"{len(frames)} frames; keep 3-12 and show only key frames")
    viewboxes, keysets = [], []
    for i, f in enumerate(frames, 1):
        if "<svg" not in f:
            add("ERROR", "timeline", f"frame {i} has no <svg>")
            continue
        if "frame-caption" not in f:
            add("WARN", "timeline", f"frame {i} has no .frame-caption sentence")
        vb = re.search(r'viewBox="([^"]+)"', f)
        viewboxes.append(vb.group(1) if vb else None)
        keys = re.findall(r'data-key="([^"]+)"', f)
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            add("ERROR", "timeline", f"frame {i} repeats data-key {', '.join(dup)}; keys must be unique per frame")
        keysets.append(set(keys))
        if vb:
            try:
                w = float(vb.group(1).split()[2])
                if w > 480:
                    add("WARN", "timeline", f"frame {i} viewBox is {w:.0f} wide; keep <= 480 so labels stay readable in the storyboard")
            except (IndexError, ValueError):
                pass
    if len(set(viewboxes)) > 1:
        add("ERROR", "timeline", "frames use different viewBox values; every frame needs the same one")
    if keysets and any(k != keysets[0] for k in keysets):
        allk = set().union(*keysets)
        for i, k in enumerate(keysets, 1):
            missing = sorted(allk - k)
            if missing:
                add("ERROR", "timeline", f"frame {i} lacks data-key {', '.join(missing)}; keep every keyed element in every frame (use class=\"off\" to hide it)")
    if keysets and not keysets[0]:
        add("WARN", "timeline", "no data-key elements; the player can only cross-cut, not animate")
    for need, what in (('class="stage"', "a .stage element"), ('data-act="play"', "a play button"),
                       ('data-act="next"', "a next button"), ('class="scrub"', "a .scrub range")):
        if need not in nc:
            add("WARN", "timeline", f"player is missing {what}")


def section_span(nc, sid):
    """Start and end offsets of <section id=sid>, up to the next <section (sections are not nested)."""
    m = re.search(r'<section[^>]*\bid="' + re.escape(sid) + r'"', nc)
    if not m:
        return None
    nxt = nc.find("<section", m.end())
    return m.start(), (nxt if nxt != -1 else len(nc))


def keys_in(html):
    return set(re.findall(r'data-key="([^"]+)"', html))


def check_technique(techs, html, where, add):
    """The chosen technique's markup is present: references/techniques.md § Markup and checks."""
    unknown = [t for t in techs if t not in TECHNIQUES]
    if unknown:
        add("WARN", "technique", f"{where}: unknown technique {', '.join(unknown)}; use {', '.join(sorted(TECHNIQUES))}")
    if len(techs) > 2:
        add("WARN", "technique", f"{where}: {len(techs)} techniques; choose one per unit, two at most")
    if not techs:
        add("WARN", "technique", f"{where}: data-technique is empty")
    cases = len(re.findall(r'\bclass="(?:[^"]*\s)?case(?:\s[^"]*)?"', html))
    if any(t in ("contrast", "sweep", "extremes") for t in techs) and cases < 2:
        add("WARN", "technique", f"{where}: {'/'.join(t for t in techs if t in ('contrast', 'sweep', 'extremes'))} needs 2-4 side-by-side cases (<g class=\"case\">); found {cases}")
    if "analogy" in techs and not re.search(r'<p\b[^>]*\bclass="(?:[^"]*\s)?breaks(?:\s[^"]*)?"', html):
        add("WARN", "technique", f"{where}: an analogy needs a <p class=\"breaks\"> sentence saying where it breaks")
    if "cause-chain" in techs and "marker-end" not in html:
        add("WARN", "technique", f"{where}: a cause chain needs arrows (marker-end) that mean \"causes\"")
    if "sequence" in techs and not re.search(r'class="[^"]*\btimeline\b', html):
        add("WARN", "technique", f"{where}: a sequence is drawn as a timeline (figure.timeline)")


def check_ladder(nc, add):
    """The figure ladder: concept blocks that build on each other, drawn on one base scene."""
    fam = section_span(nc, "familiar")
    if not fam:
        return
    body = nc[fam[0]:fam[1]]
    starts = list(re.finditer(r'<div\b[^>]*\bclass="(?:[^"]*\s)?concept(?:\s[^"]*)?"[^>]*>', body))
    if not starts:
        add("WARN", "ladder", 'no .concept blocks in "What you already know"; teach each core concept with a short block and an easy figure')
        return
    blocks = []
    for i, m in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(body)
        tag = m.group(0)
        bid = re.search(r'\bid="([^"]+)"', tag)
        on = re.search(r'\bdata-builds-on="([^"]+)"', tag)
        span = body[m.end():end]
        tech = re.search(r'\bdata-technique="([^"]*)"', tag)
        blocks.append({"id": bid.group(1) if bid else f"#{i + 1}", "on": on.group(1) if on else None,
                       "svg": "<svg" in span, "keys": keys_in(span), "span": span,
                       "tech": tech.group(1).split() if tech else None})
    seen = {}
    for i, b in enumerate(blocks):
        name = b["id"]
        if not b["svg"]:
            add("WARN", "ladder", f"block {name} has no figure; a core concept gets an easy picture (plain background stays in prose, outside the blocks)")
        elif not b["keys"]:
            add("WARN", "ladder", f"block {name}: its figure has no data-key elements, so later figures cannot be checked against it")
        if b["tech"] is None:
            add("WARN", "technique", f"block {name} names no technique (data-technique); choose one from references/techniques.md")
        else:
            check_technique(b["tech"], b["span"], f"block {name}", add)
        if i > 0 and not b["on"]:
            add("WARN", "ladder", f"block {name} does not say which earlier block it builds on (data-builds-on)")
        if b["on"]:
            parent = seen.get(b["on"])
            if parent is None:
                add("WARN", "ladder", f"block {name} builds on {b['on']!r}, which is not an earlier block")
            elif b["keys"] and parent["keys"] and not (b["keys"] & parent["keys"]):
                add("WARN", "ladder", f"block {name} shares no data-key with {b['on']}; its figure should be that figure plus one new thing")
        seen[b["id"]] = b
    # analogies are rare: at most one, and only in "What you already know"
    n_analogy = sum(1 for b in blocks if b["tech"] and "analogy" in b["tech"])
    if n_analogy > 1:
        add("WARN", "technique", f"{n_analogy} analogy blocks; use an analogy rarely, at most once per page")
    outside = nc[:fam[0]] + nc[fam[1]:]
    if re.search(r'\bdata-technique="[^"]*\banalogy\b', outside):
        add("WARN", "technique", 'an analogy outside "What you already know"; use analogies only in the ladder, and rarely')
    # the foreshadow: one or two hints in the ladder, each recalled after "What you already know"
    shadows = [b for b in blocks if re.search(r'<p\b[^>]*\bclass="(?:[^"]*\s)?foreshadow(?:\s[^"]*)?"', b["span"])]
    loose = len(re.findall(r'class="(?:[^"]*\s)?foreshadow(?:\s[^"]*)?"', body)) - len(shadows)
    if not shadows:
        add("WARN", "foreshadow", "no p.foreshadow in the ladder; end the block that first shows the main question's phenomenon with a one-sentence hint")
    if len(shadows) > 2:
        add("WARN", "foreshadow", f"{len(shadows)} foreshadows; keep one, two at most")
    if loose > 0:
        add("WARN", "foreshadow", "a p.foreshadow sits outside a .concept block; put it at the end of the block whose figure shows the phenomenon")
    later = nc[fam[1]:]
    for b in shadows:
        if not re.search(r'\bdata-recalls="' + re.escape(b["id"]) + r'"', later):
            add("WARN", "foreshadow", f"the foreshadow in {b['id']} is never recalled; add data-recalls=\"{b['id']}\" where the mechanism explains it")
    mech = section_span(nc, "mechanism")
    ladder_keys = set().union(*(b["keys"] for b in blocks))
    if mech and ladder_keys:
        mbody = nc[mech[0]:mech[1]]
        if "<svg" in mbody and not (keys_in(mbody) & ladder_keys):
            add("WARN", "ladder", "the mechanism's figures share no data-key with the ladder figures; draw them on the same base scene")
        for t in re.finditer(r'<figure\b[^>]*\bdata-technique="([^"]*)"[^>]*>', mbody):
            end = mbody.find("</figure>", t.end())
            fig = mbody[t.start():end if end != -1 else len(mbody)]
            check_technique(t.group(1).split(), fig, "a mechanism figure", add)
        for on in re.findall(r'\bdata-builds-on="([^"]+)"', mbody):
            if on not in seen:
                add("WARN", "ladder", f"a mechanism figure builds on {on!r}, which is not a concept block")


def check(path):
    raw = open(path, encoding="utf-8").read()
    findings = []

    def add(level, group, msg):
        findings.append({"level": level, "group": group, "message": msg})

    low = raw.lower()
    nocomment = re.sub(r"<!--.*?-->", "", low, flags=re.S)

    # ---- contract
    for tag in ("<!doctype", "<html", "<head>", "<head ", "<body>", "<body "):
        if tag in nocomment:
            add("ERROR", "contract", f"skeleton tag {tag.strip('<> ')!r} present; the publisher adds the skeleton")
    m = re.search(r"<title>(.*?)</title>", raw[:8192], re.S | re.I)
    if not m:
        add("ERROR", "contract", "no <title> in the first 8KB")
    else:
        title = m.group(1).strip()
        words = len(title.split()) if not HANGUL.search(title) else len(title.split()) + 1
        if re.search(r"[:—–|]| - ", title) or re.search(r"explainer|설명", title, re.I):
            add("WARN", "contract", f"title {title!r} looks like a caption; use a plain name")
        if words > 6:
            add("WARN", "contract", f"title {title!r} is long; aim for 2-5 words")
    if "{{" in raw or "SLOT NOTE" in raw:
        n = raw.count("{{") + raw.count("SLOT NOTE")
        add("ERROR", "contract", f"{n} unfilled template slot(s) or SLOT NOTE comment(s) left")
    for src in re.findall(r"<script[^>]+src=[\"']([^\"']+)", raw, re.I):
        if not src.startswith(ALLOWED_SCRIPT_HOSTS):
            add("ERROR", "contract", f"script from a blocked host: {src}")
        elif not re.search(r"\d+\.\d+", src):
            add("ERROR", "contract", f"script URL not pinned to an exact version: {src}")
    for href in re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)", raw, re.I) + \
            re.findall(r"<link[^>]+href=[\"']([^\"']+)[\"'][^>]*rel=[\"']stylesheet", raw, re.I):
        if href.startswith("http") and not href.startswith(ALLOWED_STYLE_HOSTS):
            add("ERROR", "contract", f"stylesheet from a blocked host: {href}")
    if not re.search(r":root\s*\{", raw):
        add("ERROR", "contract", "no :root token block")
    if "prefers-color-scheme: dark" not in low and "prefers-color-scheme:dark" not in low:
        add("ERROR", "contract", "no dark-mode tokens under prefers-color-scheme: dark")
    if '[data-theme="dark"]' not in raw and "[data-theme=dark]" not in raw:
        add("ERROR", "contract", 'no :root[data-theme="dark"] block')
    if not re.search(r"body\s*\{[^}]*background", raw):
        add("WARN", "contract", "body has no explicit background")
    if "prefers-reduced-motion" not in low:
        add("WARN", "contract", "no prefers-reduced-motion rule")
    for fn in ("alert(", "confirm(", "prompt("):
        if re.search(r"(?<![\w.])" + re.escape(fn), raw):
            add("ERROR", "contract", f"{fn[:-1]}() is suppressed in the artifact viewer")
    if "localstorage" in low and "try" not in low:
        add("WARN", "contract", "localStorage used without try/catch")

    p = PageParser()
    p.feed(raw)

    # ---- structure
    if p.svg_count == 0:
        add("ERROR", "structure", "no inline <svg> diagram")
    for i, s in enumerate(p.svg_info, 1):
        if s["role"] != "img":
            add("WARN", "structure", f"svg #{i}: no role=\"img\"")
        if not (s["title"] and s["desc"]):
            add("WARN", "structure", f"svg #{i}: missing <title> or <desc> (alt text)")
        if not s["viewBox"]:
            add("WARN", "structure", f"svg #{i}: no viewBox, will not scale")
        if s["literal_colors"]:
            add("WARN", "structure", f"svg #{i}: {s['literal_colors']} literal color(s); use token classes so dark mode works")
    tagnames = [t for t, _ in p.tags]
    if not any(t in tagnames for t in ("button", "input", "select")):
        add("WARN", "structure", "no button/input control; fine only if predict-then-reveal questions are the interaction")
    if "details" not in tagnames:
        add("WARN", "structure", "no <details> prediction; the reader should predict before the reveal")
    if not any(t in ("button", "input", "select", "details") for t in tagnames):
        add("ERROR", "structure", "no interaction at all")
    if not any(a.get("aria-live") for _, a in p.tags) and any(t in tagnames for t in ("button", "input")):
        add("WARN", "structure", "no aria-live region for the interaction's explanation")
    missing = [s for s in EXPECTED_SECTIONS if s not in p.ids]
    if "limits" in p.classes or "limits" in p.ids:
        add("WARN", "structure", "an assumptions-and-limits box found; state each simplification where the reader meets it instead")
    if missing:
        add("WARN", "structure", "sections not found by id/class: " + ", ".join(missing))
    # the term list belongs inside "What you already know", not in a glossary at the end
    nc = re.sub(r"<!--.*?-->", "", raw, flags=re.S)
    fam = re.search(r'<section[^>]*\bid="familiar"', nc)
    terms_at = [m.start() for m in re.finditer(r'<dl[^>]*class="[^"]*\bterms\b', nc)]
    if 'id="terms"' in nc:
        add("WARN", "structure", 'separate Terms section found; move the term list into "What you already know"')
    if not terms_at:
        add("WARN", "structure", 'no dl.terms list of the words this page uses')
    elif fam:
        nxt = nc.find("<section", fam.end())
        end = nxt if nxt != -1 else len(nc)
        if not any(fam.start() < t < end for t in terms_at):
            add("WARN", "structure", 'dl.terms is not inside the "What you already know" section')
    check_ladder(nc, add)
    # timeline: a storyboard of frames that the template's script turns into a player
    starts = [m.start() for m in re.finditer(r'<figure[^>]*class="[^"]*\btimeline\b', nc)]
    for n_tl, a in enumerate(starts, 1):
        end = starts[n_tl] if n_tl < len(starts) else len(nc)
        check_timeline(nc[a:end], add, f"timeline {n_tl}: " if len(starts) > 1 else "")
    if starts and "Timeline player:" not in nc:
        add("ERROR", "timeline", "the template's timeline player script is missing")
    if starts and re.search(r"\bautoplay\b", nc):
        add("ERROR", "timeline", "autoplay found; the timeline must start paused on frame 1")
    if not any(c in p.classes for c in ("answer",)):
        add("WARN", "structure", "no .answer one-sentence answer under the title")
    # the expert's version of your question: last section, four items, a pasteable prompt, real sources
    dp = re.search(r'<section[^>]*\bid="deeper"', nc)
    if dp:
        body = nc[dp.start():]
        end = re.search(r"</section>", body)
        body = body[:end.end()] if end else body
        n_items = len(re.findall(r"<dt\b", body))
        if n_items != 4:
            add("WARN", "deeper", f"{n_items} items in the expert's version; give the four: what an expert would do, raw material, methods and tools, the outside check")
        if not re.search(r'<pre[^>]*class="[^"]*\bprompt\b', body):
            add("WARN", "deeper", 'no <pre class="prompt"> with the rewritten request')
        if not re.search(r'<a[^>]+href="https?://', body):
            add("WARN", "deeper", "no links to raw material; link the primary sources you name")
        if re.search(r'<section[^>]*\bid="(?!deeper")', nc[dp.end():]):
            add("WARN", "deeper", "a section follows the expert's version; it belongs last on the page")

    # ---- voice
    prose = [b for b in p.blocks]
    text = " ".join(t for _, _, t, _ in prose)
    korean = len(HANGUL.findall(text)) > 0.3 * max(1, len(re.findall(r"\w", text)))
    limit = 15 if korean else 25
    sentences = []
    caption_words = 0
    deeper_words = 0
    for tag, cls, t, in_deeper in prose:
        if tag in ("h1", "h2", "h3", "dt"):
            continue
        if "frame-caption" in cls or "frame" in cls.split():
            caption_words += len(t.split())
        if in_deeper:
            deeper_words += len(t.split())
        sentences.extend(split_sentences(t))
    counts = [len(s.split()) for s in sentences]
    # captions are the timeline's text and the last section is the upgraded question;
    # neither is in the lesson's prose budget
    words = sum(counts) - caption_words - deeper_words
    stats = {
        "timeline_caption_words": caption_words,
        "deeper_words": deeper_words,
        "language": "ko" if korean else "en",
        "prose_words": words,
        "sentences": len(sentences),
        "mean_words_per_sentence": round(sum(counts) / len(sentences), 1) if sentences else 0,
        "long_sentence_limit": limit,
        "long_sentences": sum(1 for c in counts if c > limit),
    }
    if sentences:
        share = stats["long_sentences"] / len(sentences)
        stats["long_sentence_share"] = round(share, 3)
        if share > 0.15:
            add("WARN", "voice", f"{share:.0%} of sentences exceed {limit} words; split the longest")
        if stats["mean_words_per_sentence"] > (12 if korean else 18):
            add("WARN", "voice", f"mean sentence length {stats['mean_words_per_sentence']} words is high")
    longest = sorted(sentences, key=lambda s: -len(s.split()))[:5]
    stats["longest"] = [s for s in longest if len(s.split()) > limit]

    passive = []
    for s in sentences:
        if korean:
            passive += [s for _ in PASSIVE_KO.findall(s)]
        else:
            passive += [s for _ in PASSIVE_EN.findall(s)]
    stats["passive_suspects"] = len(passive)
    if sentences and len(passive) / len(sentences) > 0.12:
        add("WARN", "voice", f"{len(passive)} passive-voice suspects in {len(sentences)} sentences")
    stats["passive_examples"] = passive[:5]

    filler_hits = []
    lowtext = text.lower()
    for w in (FILLER_KO if korean else FILLER_EN):
        n = len(re.findall(r"(?<![\w-])" + re.escape(w) + r"(?![\w-])", lowtext)) if not korean else lowtext.count(w)
        if n:
            filler_hits.append(f"{w} x{n}")
    stats["filler"] = filler_hits
    if filler_hits:
        add("WARN", "voice", "filler/hype words: " + ", ".join(filler_hits))

    qs = [t for tag, cls, t, in_deeper in prose
          if "?" in t and tag != "summary" and "question" not in cls and tag != "h1" and not in_deeper]
    stats["questions_outside_prompts"] = len(qs)
    if len(qs) > 2:
        add("WARN", "voice", f"{len(qs)} prose blocks contain questions; keep questions to the opening and prediction prompts")
    if words < 400:
        add("WARN", "voice", f"only {words} words of prose; the page may be too thin")
    if words > 3000:
        add("WARN", "voice", f"{words} words of prose; the page may be too long for one concept")
    if deeper_words and not 80 <= deeper_words <= 350:
        add("WARN", "deeper", f"{deeper_words} words in the expert's version; aim for about 120-300")

    return findings, stats


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    findings, stats = check(args[0])
    if "--json" in sys.argv:
        print(json.dumps({"findings": findings, "stats": stats}, ensure_ascii=False, indent=2))
    else:
        for level in ("ERROR", "WARN"):
            for f in findings:
                if f["level"] == level:
                    print(f"{level:5} [{f['group']}] {f['message']}")
        if not findings:
            print("OK    no findings")
        print()
        cap = f" (+{stats['timeline_caption_words']} in frame captions)" if stats['timeline_caption_words'] else ""
        cap += f" (+{stats['deeper_words']} in the expert's version)" if stats['deeper_words'] else ""
        print(f"voice: {stats['language']}, {stats['prose_words']} words{cap}, {stats['sentences']} sentences, "
              f"mean {stats['mean_words_per_sentence']} words/sentence, "
              f"{stats['long_sentences']} over {stats['long_sentence_limit']}, "
              f"{stats['passive_suspects']} passive suspects")
        for s in stats["longest"]:
            print(f"  long: {s}")
        for s in stats["passive_examples"]:
            print(f"  passive?: {s}")
    sys.exit(1 if any(f["level"] == "ERROR" for f in findings) else 0)


if __name__ == "__main__":
    main()
