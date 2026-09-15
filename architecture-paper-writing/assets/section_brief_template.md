# §N <Section title> — writing brief for one pass

Part of the architecture-paper-writing skill. Copy this file, fill it, and hand it to the agent that writes
`<section source file>`. The brief records what is **DECIDED**, what is **OPEN** (the writer's to develop), and where
the **FIXED-RHETORICAL-SHAPE** is prescribed. Every content item below carries exactly one of those three marks.
The writer reads the brief in full before writing, and the section guides it names before that.

Guides to read first: `references/01_sentence_style.md` (always) · the per-section guide for §N
(`references/03`–`09`) · `references/08_design_section_lessons.md` if the section explains a mechanism ·
`references/11_writing_lessons.md`.

---

## 0. Ground rules (hard — do not violate)

- **Never invent measurements.** A number enters the text only from a simulator or profiling output, a frozen
  data view, a design document, or a verified citation. Anything else is the placeholder macro `\TBD{}` (or the
  paper's equivalent) until a source exists; a `\TBD{}` is never "filled" from memory or estimation.
- **Scope exclusions are hard rules, not preferences.** List each thing the section must NOT contain, with the
  reason and where it lives instead:
  - OUT: `<topic>` — `<reason; where it is covered, if anywhere>`
  - OUT: `<topic>` — `<reason>`
  - OUT (undecided): `<topic>` — do not re-add; if it must be mentioned, one sentence max, marked `\TBD{}`.
- **Formatting (venue rules):** no `\vspace`, no space squeezing of any kind (no negative skips, no
  `\small` in body text, no shrunken captions), figure text ≥ 8 pt.
- **The system name** is the macro `\SYS` everywhere in the source; never the literal name.
- **Naming.** Subsection titles below are *working titles*: improve them, but never use bare "Hardware" /
  "Software" (or any single generic noun) as a title — a title names what the subsection settles.

## 1. Section shape

§N has `<k>` parts. Mark each:

```latex
\subsection{<working title>}     % N.1 — DECIDED content, write it out (see §2)
\subsection{<working title>}     % N.2 — OPEN, yours to develop (see §3)
\subsection{<working title>}     % N.3 — FIXED-RHETORICAL-SHAPE (see §4)
```

Sub-subsections / run-in `\paragraph{}` heads may be added inside OPEN parts freely; FIXED parts keep the
prescribed shape.

## 2. §N.1 — DECIDED: write it out

State the content the writer must render, in the order it must appear, with the figure(s) it walks and the
facts it must carry. Each fact names its source (file and line, or citation key).

- Figure `fig:<label>` (in `figures/`): `<what it shows, its panels, what the walkthrough paragraph must name>`
- Walkthrough of one `<unit of work>`: `<step 1>` → `<step 2>` → `<step 3>`.
- Design goals to state, numbered: (1) `<goal>` (2) `<goal>` (3) `<goal>`.
- A table that is FIXED, presented as *derived from* §M's findings, never as an arbitrary choice:

| column | column | why (tie back to §M) |
|---|---|---|
| `<row>` | `<row>` | `<the finding it follows from>` |

## 3. §N.2 — OPEN: the writer's to develop

Constraints and required coverage; everything else is the writer's call.

**Must cover** (already committed elsewhere in the paper — list where):
- `<item>` — committed in `<§ / figure / contribution bullet>`; open variables the writer resolves or marks
  `\TBD{}` with options: `<var 1>`, `<var 2>`.
- `<item>`.

**Must END with:** `<the closing topic>` — `<the class of mechanism, one sentence; the writer develops it>`.

**Decision notes** (dated, with who decided) supersede anything above they contradict; keep superseded text
only if marked "kept for history".

> **Decision note (`<date>`, `<who>`).** `<what changed and the source it rests on>`.

## 4. §N.3 — FIXED-RHETORICAL-SHAPE

Model this subsection on `<named section of a named reference paper>` — read it before writing (pages in
`references/papers/INDEX.md` if it is one of the six). Its rhetorical job, which the writer must reproduce, is to
deliver the message: *"`<the one-sentence message>`"*. The reference did this by showing (i) `<move>`, (ii)
`<move>`, (iii) `<move>`. The version here argues, in the same spirit:
- `<point 1>`
- `<point 2>`
- `<point 3>`

Tone: `<e.g. confident, brief, concrete>`. This subsection exists to close the "`<reviewer question>`" question, not
to open new ones.

## 5. Terminology-correspondence policy

When exposition and evaluation use different vendor vocabularies (one vendor's names are the familiar terms,
another vendor's stack is what the evaluation actually exercises), every familiar term is framed as *the
mechanism class*, the evaluated stack's equivalent is named once, and **one explicit correspondence sentence**
appears exactly once (in §N.k or in §Methodology) so the paper never reads as "vendor-A design, vendor-B
evaluation" without saying so.

- Exposition vocabulary: `<vendor A terms>` · Evaluated stack: `<vendor B stack>` · The correspondence sentence
  lives in: `<§>`.

## 6. Bib keys available (add new ones as needed; venue bib rules: full author names, DOI/URL)

`<key1>`, `<key2>`, `<key3>` (required in §N.k), … . New keys the writer will likely need: `<topics>`. Every
new key gets a row in the paper's reference-verification table with the verbatim quote that prints the claim.

## 7. Checklist before the text is committed

- [ ] §N.1 contains the figure reference, the walkthrough, the numbered goals, and the fixed table tied to §M.
- [ ] §N.2 covers every must-cover item, ends with the prescribed closing topic, and every unresolved variable
      is `\TBD{}`.
- [ ] §N.3 reads like its model: `<the three moves>`; the required `\cite{<key>}` is present.
- [ ] The terminology-correspondence sentence appears exactly once.
- [ ] No excluded topic re-entered (§0); nothing claimed as a contribution that §0 says is not one.
- [ ] No number without a source; `\TBD{}` count reported; no `\vspace`, no squeezing, figure text ≥ 8 pt.
- [ ] No bare "Hardware" / "Software" titles.
- [ ] The document compiles (`latexmk -pdf main.tex`) with zero errors, zero undefined references.
- [ ] `scripts/check_prose.py <section>.tex --system <NAME>` run and its TOTAL block pasted into the change map.

---

### Filled example row (from the SPLEX ASPLOS brief for its design section)

| mark | item |
|---|---|
| DECIDED | §4.1 data placement table — HBM (near): weights, the entire indexer key cache, hot latent KV entries; LPDDR (far): cold latent entries — presented as derived from §3.3's placement rules, each row's "why" tied to a §3.3 finding |
