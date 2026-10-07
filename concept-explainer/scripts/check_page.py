#!/usr/bin/env python3
"""Mechanical checks for a concept-explainer page.

Usage: python3 check_page.py page.html [--json]

Reports three groups of findings:
  contract  - artifact page-contract problems (skeleton tags, CDN, theme tokens, leftover slots)
  structure - the parts a concept-explainer page needs (diagram, interaction, sections)
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
EXPECTED_SECTIONS = ["familiar", "problem", "mechanism", "try", "result", "misconception", "recap", "terms"]
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
        self.blocks = []          # (tag, text) for prose blocks
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
        if tag == "svg":
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
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag in PROSE_TAGS and not self.skip_depth:
            if self.prose_depth == 0:
                self.current = []
                self.current_tag = tag
                self.current_class = a.get("class") or ""
            self.prose_depth += 1
        if tag in ("br",) and self.prose_depth:
            self.current.append(" ")

    def handle_endtag(self, tag):
        if tag == "svg" and self.in_svg:
            self.in_svg -= 1
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag in PROSE_TAGS and self.prose_depth and not self.skip_depth:
            self.prose_depth -= 1
            if self.prose_depth == 0:
                text = re.sub(r"\s+", " ", "".join(self.current)).strip()
                if text:
                    self.blocks.append((self.current_tag, self.current_class, text))

    def handle_data(self, data):
        if self.prose_depth and not self.skip_depth:
            self.current.append(data)


def split_sentences(text):
    parts = re.split(r"(?<=[.!?。])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 1]


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
    if "limits" not in p.classes and "limits" not in p.ids:
        missing.append("limits")
    if missing:
        add("WARN", "structure", "sections not found by id/class: " + ", ".join(missing))
    if not any(c in p.classes for c in ("answer",)):
        add("WARN", "structure", "no .answer one-sentence answer under the title")

    # ---- voice
    prose = [b for b in p.blocks]
    text = " ".join(t for _, _, t in prose)
    korean = len(HANGUL.findall(text)) > 0.3 * max(1, len(re.findall(r"\w", text)))
    limit = 15 if korean else 25
    sentences = []
    for tag, cls, t in prose:
        if tag in ("h1", "h2", "h3", "dt"):
            continue
        sentences.extend(split_sentences(t))
    counts = [len(s.split()) for s in sentences]
    words = sum(counts)
    stats = {
        "language": "ko" if korean else "en",
        "prose_words": words,
        "sentences": len(sentences),
        "mean_words_per_sentence": round(words / len(sentences), 1) if sentences else 0,
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

    qs = [t for tag, cls, t in prose if "?" in t and tag != "summary" and "question" not in cls and tag != "h1"]
    stats["questions_outside_prompts"] = len(qs)
    if len(qs) > 2:
        add("WARN", "voice", f"{len(qs)} prose blocks contain questions; keep questions to the opening and prediction prompts")
    if words < 400:
        add("WARN", "voice", f"only {words} words of prose; the page may be too thin")
    if words > 1500:
        add("WARN", "voice", f"{words} words of prose; the page may be too long for one concept")

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
        print(f"voice: {stats['language']}, {stats['prose_words']} words, {stats['sentences']} sentences, "
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
