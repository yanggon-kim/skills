# Worked example: the P3-LLM lab deck

An approved 56-slide paper-discussion deck (a lab meeting on the P3-LLM paper, arXiv 2511.06838v4), the
reference for what a finished deck from this skill looks like: `assets/reference/p3llm-intro.pptx`, and
the page it was translated from, `assets/reference/p3llm-intro.html`.

| file | what it is |
|---|---|
| `build_p3llm_intro.py` | Mode 1 for this deck: writes the lab page (21 sections, 17 figures, 4 storyboards) from SVG helpers |
| `deck_figs_p3llm.py` | reads the page's figures with `scripts/svg_shapes.py`, plus the deck-only label edits |
| `build_p3llm_deck.js` | Mode 2 for this deck: the slide text, bullets and notes, on `scripts/deck_lib.js` |
| `p3llm-deck-audit.md` | its fact audit: 123 rows, every slide and its notes against the paper |

**Older page style.** The page predates the prototype format of `references/html-prototype.md`: it is a
scrolling lab page (prose points under each figure), so its bullets, speaker notes and step captions
live in `build_p3llm_deck.js`, and the figures needed a few deck-only label edits (`DECK_TEXT`,
`DECK_ADD`, `DECK_SIZE`). A new deck puts all of that in the prototype and runs `html_to_spec.py` +
`build_deck.js` instead; the slide vocabulary, geometry, theme and QA are the same library.

**Rebuild** (output equals the reference deck slide for slide; only the section ids in
`presentation.xml` differ):
```bash
SK=~/.claude/skills/ppt-create; bash $SK/scripts/setup.sh WORK
node $SK/examples/p3llm/build_p3llm_deck.js p3llm-intro.pptx --work WORK
WORK/venv/bin/python $SK/scripts/deck_qa.py p3llm-intro.pptx WORK/p3llm-intro.meta.json   # all PASS; WARN lines 33, whitespace 1
python3 $SK/examples/p3llm/build_p3llm_intro.py p3llm-intro.html                          # needs the concept-explainer skill's template
```

**What to look at.**
- Structure: title (three key ideas) → outline → five parts, each opened by the outline with the part
  highlighted → closing with three discussion questions. Two methodology slides precede the results.
- Figure-first slides with 2–3 bullets in the band; the speaker notes are a full script (120–250 words)
  that walks the figure ("the gold bar…") and names the table or section behind every number.
- Storyboards: DRAM commands on one bank (5 frames), timing rules (6), a stock PIM run (7), the paper's
  throughput trick (6): 20 Morph-linked follow-on frames, the step column on the right.
- Provenance only in the notes ("Figure: Redrawn from the paper's Fig. 4 …"); one compact
  "simulator preset" mark kept inside the DRAM timing figures (`qa.restricted` allows it there only).
- The author's own reading carries the deck's tag on the slide and in the notes; schematic drawings say
  so in the notes. The audit marks these rows "our reading".
- Its known cosmetic leftovers are what the re-layout procedure would fix next, and what QA warns about:
  gridlines and leader lines crossing labels (`lines`, 33 on slides 11–16, 28, 35, 36, 49–51) and the
  tall perplexity dot plot of slide 35, 49.5 % empty (`whitespace`). The deck was approved with them;
  the whitespace thresholds are calibrated so that slide 35 is its only whitespace warning.
