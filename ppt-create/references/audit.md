# Tightening and the fact audit

After the deck builds and passes QA, check it against the source material **claim by claim**: every
slide and every speaker note. A talk's audience repeats what was on the slides; an error there outlives
the talk, and the speaker is rarely the one who catches it.

## Contents
- The audit file
- Procedure
- Statuses
- Marking the author's own reasoning
- Tightening while you audit

## The audit file

One Markdown table next to the deck, `<deck>-audit.md`, with a header that names the deck and exactly
what it was checked against (the paper and its version, the notes, the data files, the page renders of
figures), a status legend, then one row per claim:

| slide | where | claim | source location | status |
|---|---|---|---|---|
| 9 | B | Probing touches neighbouring slots, so a short probe sequence often stays in one cache line | Knuth §6.4; general architecture knowledge | background |
| 10 | N | at three-quarters full a miss costs about eight and a half probes | ½(1 + 1/(1 − 0.75)²) = 8.5, Knuth §6.4 | ok |
| 12 | T | "Accuracy is unchanged" → "Accuracy drops 0.1 points" | Table 4, row 3 | fixed (was "unchanged") |

`where`: T title, B bullet or step caption, F figure labels, Tab table row, S headline number, C card /
question / recap, N notes. Several numbers in one sentence can share a row if one location covers them;
one fact said on several slides gets a row per slide (each place can be wrong on its own).

`scripts/audit_skeleton.py DECK.pptx AUDIT.md --source "…"` writes the table with every title, bullet,
caption, table row, number, card and every notes sentence that carries a number or a reference, all
"todo". Merge, delete and add rows from there; the skeleton is a checklist, not the audit.

## Procedure

1. Open the source itself (not a summary of it): the paper's text for every number, its figures for
   every depicted value, its tables cell by cell. For figures, look at the page render, not the
   extracted text.
2. Walk the deck in order. For each row: find the location, compare the exact value, unit, condition
   (batch size, dataset, model, version, "average over…"), and the wording of claims ("up to" vs
   "average", "about" vs exact, whose claim it is).
3. Check what the slide **implies** as well as what it says: a bar chart drawn to scale, a ratio between
   two numbers, a "best" or "first", a comparison whose baselines differ.
4. Fix every error **in the prototype** (title, bullet, notes, figure label), record "fixed (old → new)",
   rebuild, re-run QA, re-render the changed slides.
5. Recount the statuses into the file's header line ("48 rows: ok 35 · fixed 4 · author's reading 3 ·
   background 6") and report the counts with the deck.

## Statuses

- **ok** — matches the source at the location given.
- **fixed** — was wrong, unsupported, or not the source's claim; corrected (write old → new).
- **author's reading** — the author's inference, opinion, schematic depiction or arithmetic; it is
  marked as such on the slide and in the notes (below).
- **background** — general knowledge or a different source (textbook, standard, data sheet); name it.
- **todo** — not checked yet. A finished audit has none.

## Marking the author's own reasoning

Pick one tag for the deck (for example "[our reading]") and use it wherever the slide states something
the source does not: on the slide (in the title, or as the band's last bullet "[our reading] Our
interpretation, not the paper's claims") and in the notes, in words ("From here on this is my reading,
not the authors' claim"). Schematic drawings (positions or bar heights that are illustrative, not
measured) say so in the notes; arithmetic the author did (a ratio, a sum) says which numbers it used.
Why: listeners cannot tell a paraphrase from an inference unless the speaker marks it, and a talk about
someone else's work must not put words in their mouth.

## Tightening while you audit

The audit is also the last editing pass: a bullet that needs a qualifier to be true is often too long
for the band, and a number nobody will remember belongs in the appendix. While checking, cut words that
carry no claim, move detail that only answers a likely question to an appendix slide (and point to it
with `data-see`), and make every title say the claim the slide proves.
