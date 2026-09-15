#!/usr/bin/env python3
"""check_prose.py — a prose report for one section of an architecture paper.

Part of the architecture-paper-writing skill.  Standard library only; Python 3.8+.
It is a REPORT, not a gate: the exit status is always 0.  Read the numbers against
the guides named under each check and decide yourself.

Usage
    check_prose.py SECTION.tex [--system NAME]
    check_prose.py SECTION.md  [--system NAME]
    cat SECTION.tex | check_prose.py - [--system NAME]

What it does to the text first
    .tex   comments stripped (% not preceded by a backslash); figure / table /
           algorithm / equation floats dropped but every \\caption{...} kept as its
           own paragraph tagged [caption]; \\cite, \\ref, \\label removed; \\SYS and
           \\SYS{} replaced by the --system name (or "SYSTEM"); \\textbf{x}, \\emph{x},
           \\lead{x}, \\paragraph{x} ... reduced to x; other \\commands dropped;
           \\section / \\subsection / \\paragraph open a new heading context.
    .md    fenced code blocks dropped; '#' lines open a new heading context.
    Paragraphs are blank-line separated.  Sentences are split on . ! ? followed
    by white space, with e.g. / i.e. / Fig. / Sec. / et al. / vs. / cf. / No. protected.

The checks and the guide each comes from
    (1) Questions       interrogative sentences and the framings "asks whether",
                        "the question is", "one may ask".
                        09_motivation_and_characterization.md §E2, §H1, §I2.7;
                        07_conclusion.md §E; 01_sentence_style.md (no question to
                        the reader).
    (2) Banned list     clearly · up to N (regex "up to \\d") · compared to ·
                        interesting to note · Key takeaways · forever ·
                        sentence-initial So · merely · simply — counts with line
                        numbers.  "clearly": 06 §C/§F, 09 §H3.  "up to N": 06 §C,
                        09 §H6 (ranges print both ends).  "compared to": 06 §C,
                        09 §H7 (the house word is "against").  "interesting to
                        note": 09 §H4.  "Key takeaways": 09 §F1, §H2.  "forever":
                        08_design_section_lessons.md §3 (the aphorism cut).
                        Sentence-initial "So", "merely", "simply": 01_sentence_style.md
                        (a fact stated plainly, no rhetorical softeners).
    (3) Number density  fraction of sentences containing a digit, after citation
                        brackets and figure / table / section numbers are removed.
                        09 §C3 / §I2.2: about one sentence in three; below 0.30
                        the section reads as an essay, above 0.50 the mechanism
                        sentences are gone.  Printed per paragraph and in total.
    (4) Own-system      mentions of --system NAME (and \\SYS) per \\section /
        mentions        \\subsection / markdown heading.  09 §D1 / §I3: at most one
                        sentence per subsection, last, and at most two section-wide
                        in a characterization section.  Skipped without --system.
    (5) we / our        count of "we", "our", "ours".  09 §C1 (the workload is
                        the subject, "we" only for construction); 06 §D ("we" is
                        agentive, never "we believe").
    (6) Ranges          count of N--M / N–M / N—M ranges versus "up to N".
                        06 §C, 09 §H6: ranges print both ends.

Output
    One block per paragraph (line range, sentence count, numbered sentences,
    density, hits), then a TOTAL block with the six summary lines.
"""
import argparse
import re
import sys

BAND_LO, BAND_HI = 0.30, 0.50

BANNED = [
    ("clearly", re.compile(r"\bclearly\b", re.I)),
    ("up to N", re.compile(r"\bup to \d", re.I)),
    ("compared to", re.compile(r"\bcompared to\b", re.I)),
    ("interesting to note", re.compile(r"\binteresting to note\b", re.I)),
    ("Key takeaways", re.compile(r"\bKey takeaways?\b")),
    ("forever", re.compile(r"\bforever\b", re.I)),
    ("sentence-initial So", re.compile(r"(?:^|[.!?]\s+|^\s*)So\b(?!-)")),
    ("merely", re.compile(r"\bmerely\b", re.I)),
    ("simply", re.compile(r"\bsimply\b", re.I)),
]
QUESTION_FRAMINGS = re.compile(r"\b(asks? whether|the question is|one may ask)\b", re.I)
RANGE_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:--|–|—)\s*\d")
UPTO_RE = re.compile(r"\bup to \d", re.I)
WE_RE = re.compile(r"\b(we|our|ours)\b", re.I)
CITE_BRACKET_RE = re.compile(r"\[[\d,\s–-]+\]")
FIGNUM_RE = re.compile(
    r"(?:Figures?|Fig\.|Tables?|Sections?|Sec\.|§|Algorithms?|Alg\.|Eq\.|Equations?|Lines?)\s*~?\s*\d+(?:[.\-–]\d+)*[a-z]?",
    re.I)
ABBREV = ["e.g.", "i.e.", "Fig.", "Figs.", "Sec.", "Secs.", "et al.", "vs.", "cf.", "No.", "Eq.", "Eqs.", "Tab.", "approx."]

FLOAT_ENVS = ("figure", "figure*", "table", "table*", "algorithm", "algorithmic", "equation", "equation*", "align", "align*")


# --------------------------------------------------------------------------- LaTeX stripping
def balanced_arg(s, i):
    """s[i] == '{'; return (content, index after the closing brace)."""
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def strip_comment(line):
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


DROP_CMDS = ("cite", "citep", "citet", "ref", "autoref", "cref", "Cref", "label", "vspace", "hspace", "includegraphics",
             "input", "include", "bibliography", "bibliographystyle", "usepackage", "documentclass", "footnotemark")
KEEP_CMDS = ("textbf", "textit", "emph", "lead", "paragraph", "subparagraph", "text", "textsc", "mbox", "footnote",
             "section", "subsection", "subsubsection", "caption", "textrm", "textsf", "texttt", "underline", "url")


def reduce_commands(line, system):
    """Replace \\SYS, drop cite/ref/label with their args, keep the argument of formatting commands, drop the rest."""
    line = re.sub(r"\\SYS(\{\})?", system, line)
    line = line.replace("~", " ").replace("\\,", " ").replace("\\ ", " ").replace("\\%", "%").replace("\\&", "&")
    out, i = [], 0
    while i < len(line):
        if line[i] == "\\" and i + 1 < len(line) and line[i + 1].isalpha():
            m = re.match(r"\\([A-Za-z]+)\*?", line[i:])
            name = m.group(1)
            j = i + m.end()
            # optional [..]
            if j < len(line) and line[j] == "[":
                k = line.find("]", j)
                j = k + 1 if k != -1 else len(line)
            if j < len(line) and line[j] == "{":
                arg, j2 = balanced_arg(line, j)
                if name in DROP_CMDS:
                    pass
                elif name in KEEP_CMDS or name not in DROP_CMDS:
                    out.append(reduce_commands(arg, system))
                i = j2
            else:
                i = j
            continue
        out.append(line[i])
        i += 1
    return "".join(out)


HEADING_TEX = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\s*(?:\[[^\]]*\])?\s*\{")
BEGIN_RE = re.compile(r"\\begin\{([a-zA-Z*]+)\}")
END_RE = re.compile(r"\\end\{([a-zA-Z*]+)\}")


def preprocess_tex(lines, system):
    """Return list of (lineno, text, heading_or_None, is_caption)."""
    res, in_float, depth = [], None, 0
    for n, raw in enumerate(lines, 1):
        line = strip_comment(raw.rstrip("\n"))
        heading = None
        hm = HEADING_TEX.search(line)
        if hm and hm.group(1) in ("section", "subsection", "subsubsection"):
            arg, _ = balanced_arg(line, hm.end() - 1)
            heading = "%s: %s" % (hm.group(1), reduce_commands(arg, system).strip())
        if in_float:
            for cm in re.finditer(r"\\caption\s*(?:\[[^\]]*\])?\s*\{", line):
                arg, _ = balanced_arg(line, cm.end() - 1)
                res.append((n, "", None, False))
                res.append((n, reduce_commands(arg, system), None, True))
                res.append((n, "", None, False))
            for bm in BEGIN_RE.finditer(line):
                if bm.group(1) == in_float:
                    depth += 1
            for em in END_RE.finditer(line):
                if em.group(1) == in_float:
                    depth -= 1
                    if depth == 0:
                        in_float = None
            continue
        bm = BEGIN_RE.search(line)
        if bm and bm.group(1) in FLOAT_ENVS:
            in_float, depth = bm.group(1), 1
            line = line[:bm.start()]
            # a one-line float
            em = END_RE.search(raw, bm.end())
            if em and em.group(1) == in_float:
                in_float, depth = None, 0
        line = reduce_commands(line, system)
        line = re.sub(r"\\[A-Za-z]+\*?", " ", line)  # any bare command left
        line = line.replace("{", "").replace("}", "")
        if heading:
            res.append((n, "", heading, False))
            continue
        res.append((n, line, None, False))
    return res


def preprocess_md(lines, system):
    res, in_code = [], False
    for n, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        hm = re.match(r"^(#{1,6})\s+(.*)$", line)
        if hm:
            res.append((n, "", "heading: " + hm.group(2).strip(), False))
            continue
        line = re.sub(r"\\SYS(\{\})?", system, line)
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)   # links
        line = re.sub(r"[*_`]+", "", line)
        res.append((n, line, None, False))
    return res


# --------------------------------------------------------------------------- sentences
def split_sentences(text):
    t = text
    for a in ABBREV:
        t = t.replace(a, a.replace(".", "\x00"))
    parts = re.split(r"(?<=[.!?])[\"'”’)]*\s+(?=[\"'“‘(]*[A-Z0-9])", t)
    out = []
    for p in parts:
        p = p.replace("\x00", ".").strip()
        if p and re.search(r"[A-Za-z]", p):
            out.append(p)
    return out


def has_number(sentence):
    s = CITE_BRACKET_RE.sub(" ", sentence)
    s = FIGNUM_RE.sub(" ", s)
    return bool(re.search(r"\d", s))


# --------------------------------------------------------------------------- report
def main():
    ap = argparse.ArgumentParser(
        prog="check_prose.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?", default="-", help=".tex or .md file, or '-' for stdin (default)")
    ap.add_argument("--system", default=None, metavar="NAME",
                    help="the paper's own system name; \\SYS is mapped to it and check (4) counts it (default: none)")
    ap.add_argument("--quiet", action="store_true", help="print only the TOTAL block")
    args = ap.parse_args()

    if args.file == "-":
        raw = sys.stdin.read()
        kind = "tex" if "\\" in raw[:4000] and "\\section" in raw or "\\begin" in raw else "md"
    else:
        with open(args.file, encoding="utf-8", errors="replace") as fh:
            raw = fh.read()
        kind = "md" if args.file.lower().endswith((".md", ".markdown", ".txt")) else "tex"
    lines = raw.splitlines(True)
    system = args.system or "SYSTEM"
    rows = preprocess_tex(lines, system) if kind == "tex" else preprocess_md(lines, system)

    # group into paragraphs
    paras, cur, heading = [], None, "(before first heading)"
    for n, text, head, is_cap in rows:
        if head:
            if cur:
                paras.append(cur)
                cur = None
            heading = head
            continue
        if not text.strip():
            if cur:
                paras.append(cur)
                cur = None
            continue
        if cur is None:
            cur = {"start": n, "end": n, "lines": [], "heading": heading, "caption": is_cap}
        cur["end"] = n
        cur["lines"].append((n, text))
    if cur:
        paras.append(cur)

    sys_re = re.compile(r"\b%s\b" % re.escape(args.system)) if args.system else None

    tot = {"sent": 0, "num": 0, "q": 0, "we": 0, "ranges": 0, "upto": 0, "banned": {k: 0 for k, _ in BANNED},
           "sys": {}, "paras": 0}
    out = []
    for i, p in enumerate(paras, 1):
        text = " ".join(t.strip() for _, t in p["lines"])
        sents = split_sentences(text)
        n_num = sum(1 for s in sents if has_number(s))
        qs = [s for s in sents if s.rstrip().endswith("?")]
        framings = [(n, m.group(0)) for n, t in p["lines"] for m in QUESTION_FRAMINGS.finditer(t)]
        hits = []
        for name, rx in BANNED:
            for n, t in p["lines"]:
                for _ in rx.finditer(t):
                    hits.append((name, n))
                    tot["banned"][name] += 1
        we = len(WE_RE.findall(text))
        ranges = len(RANGE_RE.findall(text))
        upto = len(UPTO_RE.findall(text))
        sys_hits = len(sys_re.findall(text)) if sys_re else 0
        if sys_re:
            tot["sys"][p["heading"]] = tot["sys"].get(p["heading"], 0) + sys_hits
        tot["sent"] += len(sents)
        tot["num"] += n_num
        tot["q"] += len(qs) + len(framings)
        tot["we"] += we
        tot["ranges"] += ranges
        tot["upto"] += upto
        tot["paras"] += 1
        if args.quiet:
            continue
        dens = (n_num / len(sents)) if sents else 0.0
        tag = " [caption]" if p["caption"] else ""
        out.append("¶%d  lines %d-%d%s  under %s" % (i, p["start"], p["end"], tag, p["heading"]))
        out.append("    sentences %d, with a number %d, density %.2f%s" % (
            len(sents), n_num, dens, band_note(dens) if len(sents) >= 3 else ""))
        if qs or framings:
            out.append("    QUESTIONS: %d interrogative%s%s" % (
                len(qs), "; " + "; ".join('"%s"' % q[:70] for q in qs) if qs else "",
                "; framings: " + ", ".join("%s (line %d)" % (f, n) for n, f in framings) if framings else ""))
        if hits:
            out.append("    BANNED: " + ", ".join("%s (line %d)" % (name, n) for name, n in hits))
        extras = []
        if sys_re and sys_hits:
            extras.append("%s x%d" % (args.system, sys_hits))
        if we:
            extras.append("we/our x%d" % we)
        if ranges or upto:
            extras.append("ranges %d, 'up to N' %d" % (ranges, upto))
        if extras:
            out.append("    " + "; ".join(extras))
    print("\n".join(out))
    if out:
        print()
    dens = (tot["num"] / tot["sent"]) if tot["sent"] else 0.0
    print("TOTAL  (%s, %d paragraphs, %d sentences)" % (args.file, tot["paras"], tot["sent"]))
    print("  (1) questions            : %d  (interrogative sentences + framings)" % tot["q"])
    banned_txt = ", ".join("%s %d" % (k, v) for k, v in tot["banned"].items() if v) or "none"
    print("  (2) banned               : %d  [%s]" % (sum(tot["banned"].values()), banned_txt))
    print("  (3) number density       : %.2f  (%d of %d sentences carry a digit; guide band about 1 in 3 — below %.2f reads as an essay, above %.2f the mechanism sentences are gone)%s" % (
        dens, tot["num"], tot["sent"], BAND_LO, BAND_HI, band_note(dens)))
    if sys_re:
        per = "; ".join("%s: %d" % (h, c) for h, c in tot["sys"].items()) or "none"
        print("  (4) own-system mentions  : %d  [%s]" % (sum(tot["sys"].values()), per))
    else:
        print("  (4) own-system mentions  : skipped (pass --system NAME)")
    print("  (5) we/our               : %d" % tot["we"])
    print("  (6) ranges N--M          : %d  versus 'up to N': %d" % (tot["ranges"], tot["upto"]))
    return 0


def band_note(d):
    if d < BAND_LO:
        return "  <- below band (essay)"
    if d > BAND_HI:
        return "  <- above band (mechanism sentences squeezed out)"
    return "  (in band)"


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
    sys.exit(0)
