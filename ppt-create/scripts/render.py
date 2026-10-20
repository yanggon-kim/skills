#!/usr/bin/env python3
"""Render a .pptx to PDF and JPG pages for visual QA, with metric-compatible stand-in fonts.

Usage:
    python3 render.py DECK.pptx [--slides 1,3,7-9] [--out DIR] [--dpi 80]

Prints the PDF path and one JPG path per rendered slide (DIR/<deck>-<NN>.jpg).

Why the font aliasing: a server rarely has Helvetica, Arial, Calibri or Cambria, and LibreOffice then
substitutes a font with other widths, so the render wraps lines where PowerPoint would not. A scratch
fontconfig file maps each family to its metric twin (Helvetica / Arial -> Liberation Sans, Calibri ->
Carlito, Cambria -> Caladea, Times New Roman -> Liberation Serif, Courier New -> Liberation Mono), so
line breaks in the render match the real deck closely enough to judge fit.

LibreOffice: uses the pptx skill's soffice.py wrapper when it can be found (it handles sandboxes that
block sockets); otherwise calls `soffice` directly with a throw-away user profile. Needs `pdftoppm`.
LibreOffice plays Morph transitions as their fade fallback; a render shows each frame as a still.
"""
import argparse
import glob
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

ALIASES = {
    "Helvetica": "Liberation Sans", "Helvetica Regular": "Liberation Sans", "Helvetica Neue": "Liberation Sans",
    "Arial": "Liberation Sans", "Calibri": "Carlito", "Cambria": "Caladea",
    "Times New Roman": "Liberation Serif", "Courier New": "Liberation Mono",
}
EXTRA_FONT_GLOBS = [
    "~/texlive/*/texmf-dist/fonts/truetype/google/carlito",
    "~/texlive/*/texmf-dist/fonts/truetype/huerta/caladea",
    "/usr/share/texlive/texmf-dist/fonts/truetype/google/carlito",
    "/usr/share/texlive/texmf-dist/fonts/truetype/huerta/caladea",
    "/usr/share/fonts/truetype/crosextra",
]


def pptx_skill_soffice():
    """The optional pptx skill's LibreOffice wrapper (PPTX_SKILL_DIR, else a search under ~/.claude/skills)."""
    cands = []
    if os.environ.get("PPTX_SKILL_DIR"):
        cands.append(os.path.join(os.environ["PPTX_SKILL_DIR"], "scripts", "office", "soffice.py"))
    cands += glob.glob(os.path.expanduser("~/.claude/skills/**/pptx/scripts/office/soffice.py"), recursive=True)
    for c in cands:
        if os.path.isfile(c):
            spec = importlib.util.spec_from_file_location("pptx_skill_soffice", c)
            mod = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(mod)
                return mod.run_soffice
            except Exception:  # a broken optional helper must not stop the render
                continue
    return None


def font_conf(tmp, font_dirs):
    dirs = list(font_dirs)
    for g in EXTRA_FONT_GLOBS:
        dirs += glob.glob(os.path.expanduser(g))
    rules = "".join(
        f'<match target="pattern"><test name="family"><string>{a}</string></test>'
        f'<edit name="family" mode="assign" binding="strong"><string>{b}</string></edit></match>'
        for a, b in ALIASES.items())
    xml = ('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig>'
           '<include ignore_missing="yes">/etc/fonts/fonts.conf</include>'
           + "".join(f"<dir>{d}</dir>" for d in dirs) + rules + "</fontconfig>")
    path = os.path.join(tmp, "fonts.conf")
    with open(path, "w") as f:
        f.write(xml)
    return path


def parse_slides(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = []
    for part in spec.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return [s for s in out if 1 <= s <= n]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck")
    ap.add_argument("--slides", default="", help="e.g. 1,3,7-9 (default: all)")
    ap.add_argument("--out", default=None, help="output folder (default: <deck folder>/render)")
    ap.add_argument("--dpi", type=int, default=80)
    ap.add_argument("--font-dir", action="append", default=[], help="extra font folder (repeatable)")
    a = ap.parse_args()
    deck = os.path.abspath(a.deck)
    out = os.path.abspath(a.out or os.path.join(os.path.dirname(deck), "render"))
    os.makedirs(out, exist_ok=True)
    if not shutil.which("pdftoppm"):
        sys.exit("pdftoppm (poppler-utils) is needed for the JPG pages")
    base = os.path.splitext(os.path.basename(deck))[0]
    with tempfile.TemporaryDirectory(prefix="ppt_render_") as tmp:
        os.environ["FONTCONFIG_FILE"] = font_conf(tmp, a.font_dir)
        args = ["--headless", "--convert-to", "pdf", "--outdir", out, deck]
        run = pptx_skill_soffice()
        if run is not None:
            res = run(args, capture_output=True, text=True, timeout=600)
        else:
            if not shutil.which("soffice"):
                sys.exit("LibreOffice (soffice) is needed to render")
            prof = os.path.join(tmp, "profile")
            res = subprocess.run(["soffice", f"-env:UserInstallation=file://{prof}"] + args,
                                 capture_output=True, text=True, timeout=600)
        pdf = os.path.join(out, base + ".pdf")
        if not os.path.isfile(pdf):
            sys.exit(f"LibreOffice made no PDF:\n{res.stdout}\n{res.stderr}")
    info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout if shutil.which("pdfinfo") else ""
    pages = next((int(l.split()[-1]) for l in info.splitlines() if l.startswith("Pages:")), 9999)
    print(pdf)
    for s in parse_slides(a.slides, pages):
        prefix = os.path.join(out, f"{base}-{s:02d}")
        subprocess.run(["pdftoppm", "-jpeg", "-r", str(a.dpi), "-f", str(s), "-l", str(s), "-singlefile", pdf, prefix],
                       check=True)
        print(prefix + ".jpg")


if __name__ == "__main__":
    main()
