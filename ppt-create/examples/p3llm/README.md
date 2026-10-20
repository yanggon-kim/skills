# Worked example: the P3-LLM lab deck

An approved 60-slide paper-discussion deck (a lab meeting on the P3-LLM paper, arXiv 2511.06838v4), the
reference for what a finished deck from this skill looks like: `assets/reference/p3llm-intro.pptx`, and
the page it was translated from, `assets/reference/p3llm-intro.html`.

| file | what it is |
|---|---|
| `build_p3llm_intro.py` | Mode 1 for this deck: writes the lab page (24 sections, 20 figures, 4 storyboards) from SVG helpers |
| `deck_figs_p3llm.py` | reads the page's figures with `scripts/svg_shapes.py`, plus the deck-only label edits |
| `build_p3llm_deck.js` | Mode 2 for this deck: the slide text, bullets and notes, on `scripts/deck_lib.js` |
| `p3llm-deck-audit.md` | its fact audit: 143 rows, every slide and its notes against the paper |

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
WORK/venv/bin/python $SK/scripts/deck_qa.py p3llm-intro.pptx WORK/p3llm-intro.meta.json   # all PASS; WARN lines 33, whitespace 1 (s39)
python3 $SK/examples/p3llm/build_p3llm_intro.py p3llm-intro.html                          # needs the concept-explainer skill's template
```

**What to look at.**
- Structure: title (title, subtitle, byline, presenter, date: no key points) → outline with part 1, Summary, highlighted (it is also the Summary
  divider) → "Summary: shrink every operand; use each weight read twice" → six more parts, each opened
  by the outline with that part highlighted ("Next: part k of 7") → closing with three discussion questions. Two methodology slides precede the results.
- Background vs Preliminary Note: part 3, **Background**, is the paper's own §II in the paper's order (LLM
  decoding, GQA, PIM for LLMs redrawn from its Fig. 2, quantization and Eq. 1). Part 2, the **Preliminary
  Note** (slides 4–25: DRAM hierarchy, commands, timing, stock AiM), is the presenter's DRAM primer, added on
  request for listeners new to DRAM: optional, sourced from the author's own explainer and a simulator
  preset, and tagged "Preliminary note · presenter's primer, not the paper" on its divider and every slide
  (`d.section(S_PRE, { preliminary: true })`). The deck passes `paper` to `createDeck`, so QA checks that
  the Background section exists and that the Preliminary Note sits whole between Summary and Background.
- Figure-first slides with 2–3 bullets in the band; the speaker notes are a full script (120–250 words)
  that walks the figure ("the gold bar…") and names the table or section behind every number.
- Storyboards: DRAM commands on one bank (5 frames), timing rules (6), a stock PIM run (7), the paper's
  throughput trick (6): 20 Morph-linked follow-on frames, the step column on the right.
- Provenance only in the notes ("Figure: Redrawn from the paper's Fig. 4 …"); one compact
  "simulator preset" mark kept inside the DRAM timing figures (`qa.restricted` allows it there only).
- The author's own reading carries the deck's tag on the slide and in the notes; schematic drawings say
  so in the notes. The audit marks these rows "our reading".
- Its known cosmetic leftovers are what the re-layout procedure would fix next, and what QA warns about:
  gridlines and leader lines crossing labels (`lines`, 33 on slides 11–16, 32, 39, 40, 53–55) and the
  tall perplexity dot plot of slide 39, 49.5 % empty (`whitespace`). The deck was approved with them;
  the whitespace thresholds are calibrated so that slide 39 is its only whitespace warning.
