# 13 · Outline first: the paragraph outline as the paper's structure

A paper of 11 pages holds 80–100 paragraphs. In LaTeX nobody can see whether the motivation's findings are the
problems the design solves and the evaluation measures; in a list of one-sentence messages anyone can, in two
minutes. This guide makes that list (`outline.md`) the place where the paper's structure is decided. The `.tex`
follows it.

## A. The procedure

1. **Capture.** Write the outline of the paper as it stands: every source paragraph, from the abstract to the
   conclusion, with its one-sentence message and its links (§B). Tie each entry to the source with an anchor
   comment (§C). The capture changes no prose.
2. **Edit the outline.** Every structural change is made here first: add, cut, merge, split or move a
   paragraph, rewrite its message, move a float, add or drop a promise. The author reviews the outline diff,
   not a LaTeX diff.
3. **Edit the paper to match.** Rewrite the `.tex` so that each paragraph delivers exactly its entry's message,
   in the entry's order, with the entry's floats, numbers and citations. Commit the outline and the `.tex`
   together.
4. **Re-sync.** Any edit made outside this loop (a co-author's Overleaf change, a wording pass that shifted a
   claim) is reconciled into the outline before the next outline-driven change. Update the `Synced with` line on
   each sync.

Wording-only edits that leave every message intact need no outline change. A change of a message, an order, a
float or a number does.

## B. The outline format

```markdown
# <title>: outline
Synced with: <hash>; body ends p. <N> col <L/R>; refs end p. <M>.

## III. Motivation  (sections/03_motivation.tex)
### B. Idle Beats
- **[mot-idle-beats]** "Idle beats"
  - Message: A stock PU spends three of every four MAC beats waiting for the next column read.
  - Floats: Fig. 4 (first cite)
  - Numbers: idle share 42.2–57.4 % ← evaluation/dac_2x2 fig4_idle_*
  - Cites: aim-isscc22
  - Links: ← bg-mac-sequence; → des-beat-filling
```

- **Levels.** `##` section, `###` subsection (omitted where a section has none), `-` one paragraph. A paragraph
  is a source paragraph: text between blank lines, or one `\paragraph{}` block. A list belongs to the paragraph
  that introduces it. Abstract paragraphs count; captions do not.
- **Id.** Short, kebab-case and stable, prefixed by the section (`abs-`, `intro-`, `bg-`, `mot-`, `des-`,
  `meth-`, `eval-`, `rel-`, `conc-`). An id names the content (`mot-idle-beats`), never a position (`mot-p3`),
  so moving a paragraph keeps its id.
- **Message.** One sentence, under the sentence rules of `01` §5: a concrete subject, a finite verb, the claim as
  a reader should take it away. It is the paragraph's opening finding (`11`: the finding opens the paragraph),
  stated without the numbers. "This paragraph discusses X" is not a message.
- **Floats / Numbers / Cites.** The figures, tables and equations the paragraph cites, with "(first cite)" where
  it is the first; the printed numbers that matter, each with its source (data view id or the script that prints
  it); the bib keys. Write "—" for an empty field.
- **Links.** Only the links that carry the argument: `→ id` for a promise this paragraph makes that `id`
  fulfils, `← id` for what it relies on. An intro contribution links to the evaluation paragraph that proves it.
- **Closing tables.** A *float map* (float, label, source file, first-citing id, page/column where it lands) and
  an *observations* table (§D), both regenerated on each sync.

## C. Anchors and the sync check

Put `% P:<id>` on its own line immediately before each paragraph in the `.tex`, one per outline entry and in the
same order. The comments change nothing in the PDF; prove it once with identical `pdftotext` output. A check
script then compares the two lists and fails on a missing id, an extra id, a duplicate, or a different order
(walk the sections in `\input` order):

```bash
python3 <skill-dir>/scripts/check_outline.py outline.md main.tex
```

Run it before every commit that touches either file.

## D. What the outline exposes

Read the outline top to bottom, messages only, and list these as observations before editing anything:

| defect | how it shows in the outline |
|---|---|
| two messages in one paragraph | the Message needs "and" between two claims, or two sentences |
| no message | the Message can only be written as "describes" / "discusses" |
| restatement | two entries carry the same Message |
| broken promise | an intro or motivation `→` link has no entry that fulfils it; an evaluation result no earlier entry asked for |
| late or orphan float | a float's first cite sits pages after the float, or no entry cites it |
| untraced number | a Numbers item has no source |
| wrong order | an entry relies (`←`) on an entry that comes later |

The section guides still decide each section's move order (`03`–`09`); the outline is where a move order is
checked against the actual paragraphs.

## E. Guard checks

- [ ] Every paragraph of the `.tex` has an entry and an anchor; `check_outline.py` passes.
- [ ] Every Message is one sentence with one claim.
- [ ] Every float has a first-citing entry, and the float map shows it on that page or the next (`02` §3 F12).
- [ ] Every contribution in the introduction has a `→` link to the entry that proves it.
- [ ] The `Synced with` line names the commit that contains the matching `.tex`.

## Worked example (CoDe, ISCA submission)

The outline was captured from the full paper in one pass (anchors + `outline.md` + `check_outline.py` in the
paper repo), before any restructuring. Its observations table, not a reread of the LaTeX, became the list of
structural edits the author chose from.
