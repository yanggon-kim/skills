#!/usr/bin/env python3
"""Worked example: the figures of the approved P3-LLM lab page as native-shape specs for build_p3llm_deck.js.

Run by build_p3llm_deck.js (or by hand): python3 deck_figs_p3llm.py OUT.json [PAGE.html]
PAGE.html defaults to the skill's assets/reference/p3llm-intro.html. Figures are read from the page and
parsed with scripts/svg_shapes.py, never redrawn. Storyboards become one record per frame; elements keep
their data-key so the deck can name them "!!<key>" for Morph. Each figure (each storyboard, over all its
frames) gets "bb", its content bounds plus a small pad, so the deck can crop the SVG's empty margins.

DECK_TEXT, DECK_ADD and DECK_SIZE are the few edits that are the deck's own: source references on figure
labels move to the speaker notes, one "simulator preset" mark stays on the DRAM timing figures, row labels
that collide once raised to the 12 pt floor become one legend line, and dense figures get a label scale.
(This page predates the prototype format of references/html-prototype.md, where the prototype already
shows the deck's labels and these edits are not needed.)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(SKILL, "scripts"))
from svg_shapes import Unmapped, apply_edits, bounds, parse_svg, parse_timeline, unkeyed_counts  # noqa: E402

PAGE = os.path.join(SKILL, "assets", "reference", "p3llm-intro.html")

# figure -> the id prefix of its <svg> (aria-labelledby="fN-t fN-d") on the page; storyboard -> its <figure> id
FIGS = {"fig_summary": "f1", "fig_hierarchy": "f2", "fig_tccd": "f5", "fig_llm": "fb1", "fig_gqa": "fb2", "fig_pim": "fb3",
        "fig_quant": "fb4", "fig_roofline": "f8",
        "fig_quadrant": "f9", "fig_kv": "f10", "fig_bits": "f11", "fig_bitmod": "f12", "fig_act": "f13",
        "fig_pcu": "f14", "fig_dataflow": "f16", "fig_setup": "f17", "fig_quality": "f18", "fig_speed": "f19",
        "fig_area": "f20", "fig_ablation": "f21"}
STORIES = {"fig_actrdpre": "tl3", "fig_timing": "tl4", "fig_aim": "tl6", "fig_tep": "tl15"}

# Deck-only label edits (the page keeps its own); None drops the label. Matched on the whole label text.
DECK_TEXT = {
    "fig_quadrant": {"memory footprint (Fig. 3a) →": "memory footprint →", "(Fig. 3b)": None},
    "fig_bits": {"activations (§IV-D)": "activations", "attention scores (§IV-B)": "attention scores"},
    # labels that run past their box once raised to the 12 pt floor
    "fig_summary": {"PCU + TEP": "TEP"},
    "fig_hierarchy": {"row: ACT opens": "ACT opens"},
    "fig_ablation": {"Fig. 15: average over 5 models at batch 2 and 4, each step over the one before":
                     "average over 5 models at batch 2 and 4; each step over the one before"},
    # the 12 per-row labels collide once raised to 12 pt: one legend line replaces them (DECK_ADD)
    "fig_act": {"FP16": None, "W4 + FP8-E4M3": None, "W4 + INT8-SQ": None},
    "fig_speed": {"coral = speedup (Fig. 9) · teal = energy efficiency (Fig. 10)": "coral = speedup · teal = energy efficiency"},
}
# the one compact "simulator preset" mark the deck keeps, in figures that show DRAM timing values; a legend line
DECK_ADD = {
    "fig_tccd": [dict(t="text", x=630.0, y=28.0, s="simulator preset", anchor="end", color="inksoft", size=13, bold=False, name=None)],
    "fig_act": [dict(t="text", x=14.0, y=14.0, s="hollow = FP16 · teal = W4 + FP8-E4M3 · coral = W4 + INT8-SQ", anchor="start",
                     color="ink", size=13, bold=False, name=None)],
    "fig_timing": [dict(t="text", x=472.0, y=24.0, s="timings: simulator preset", anchor="end", color="inksoft", size=13, bold=False, name=None)],
}
# text scale for figures whose labels fill their boxes (stays above the deck's 12 pt floor after scaling)
DECK_SIZE = {"fig_aim": 0.88, "fig_ablation": 1.2}


def edit(name, fig):
    apply_edits(fig, DECK_TEXT.get(name), DECK_ADD.get(name), DECK_SIZE.get(name, 1.0))


def main():
    out = sys.argv[1]
    page = open(sys.argv[2] if len(sys.argv) > 2 else PAGE, encoding="utf-8").read()
    res, fallback = {}, {}
    for name, sid in FIGS.items():
        svgtext = re.search(rf'<svg viewBox="[^"]*" role="img" aria-labelledby="{sid}-t {sid}-d">.*?</svg>', page, re.S).group(0)
        try:
            res[name] = parse_svg(svgtext)
        except Unmapped as e:
            fallback[name] = {"reason": str(e)}
            continue
        edit(name, res[name])
        res[name]["bb"] = bounds([res[name]])
    for name, tid in STORIES.items():
        markup = re.search(rf'<figure class="timeline[^"]*"[^>]*aria-labelledby="{tid}-cap">.*?</figure>', page, re.S).group(0)
        try:
            res[name] = parse_timeline(markup)
        except Unmapped as e:
            fallback[name] = {"reason": str(e)}
            continue
        for f in res[name]["frames"]:
            edit(name, f)
        bb = bounds(res[name]["frames"])  # one crop for every frame, so Morph sees the same placement
        for f in res[name]["frames"]:
            f["bb"] = bb
        counts = unkeyed_counts(res[name]["frames"])
        assert len(set(counts)) == 1, (name, counts)  # Morph pairs unkeyed elements by order
    json.dump({"figs": res, "fallback": fallback}, open(out, "w", encoding="utf-8"), ensure_ascii=False)
    print(out, len(res), "figures,", len(fallback), "fallbacks", sorted(fallback))


if __name__ == "__main__":
    main()
