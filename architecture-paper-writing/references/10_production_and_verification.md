# Production and verification — the mechanics of an edit that must survive a build

Open this before any build, float move, page-limit pass, number-bearing or structural edit, or reference addition. It says
how much checking an edit needs, where every number must come from, how floats actually move, how to prove a page is what
you say it is, and what a citation must carry before it prints. The per-section guides (`03`–`09`) say what to write; this
file says how to ship it without breaking the page or the audit.

## 1. Edit classes — ceremony is scoped by what the edit can break

Pick the class first and name it in the first line of the plan; do only that column and skip the rest. When classes mix,
take the highest. The point is cost: an audit once found a three-line wording edit that cost four commits, three agents and
thirty-six lines of bookkeeping because every gate was applied uniformly.

| | **wording** (no number, no float) | **number-bearing** | **structural** (new or moved float, new section or dataset) |
|---|---|---|---|
| read first | the sentence contract + the one section guide | same | same, plus `08_design_section_lessons.md` for design text |
| verify | build: 0 undefined refs, 0 `[?]`, bibtex 0 errors | + re-derive every touched number from its frozen data view; numeric multiset of the file unchanged except the intended values | + full float/heading map diffed against the previous commit |
| audit row | no | only if a citation is involved | same |
| independent re-check | no | no | yes, by an agent that did not make the edit |

- The page map costs a build and a script. Ask for it when a float or a page boundary is in play, not for a sentence that
  cannot move one; when a task asks for a page map on such a sentence, say it is a wording edit and skip it.
- The design-pass checklist in `08_design_section_lessons.md` is a design-pass rule; do not drag it onto wording edits.
- A wording pass *can* be structural in effect: a few added lines before a `figure*` source can push that source across a
  page break and move the figure a page. After any text change ahead of a `figure*` source, diff the per-page caption map
  against a scratch build of the previous commit.

## 2. Numbers — every printed value traces to something a reader could open

- Never invent a number. Each one traces to a frozen data view, a design document, or a verified citation; a value that has
  none of these is a `\TBD{}` until it does. Fill placeholders only from simulator or profiling output or a verified source,
  because a reviewer can grep a paper for a number and ask where it came from.
- Generators keep every printed number in one dictionary with asserts against the frozen data, so a restyle cannot move a
  value silently and a regenerated figure proves its own numbers *(example: 273 asserts across the evaluation figures)*.
- Print both ends of a range. A single value in the abstract that the body prints as a range, or the reverse, reads as an
  overclaim the moment the reader follows it.
- A measured number is printed with its setting, in reader order: the baseline → the one thing changed, named → what read it →
  what a program then did → the control. A bare list of values leaves the reader without the frame that makes them evidence,
  and clarity here beats the word budget when every clause is a fact.
- Every word count ships with its counter named (comments and floats stripped, which macros are removed with their argument,
  what counts as a token). Two counters on the same text differ by a few percent, and a cap set against one counter is
  missed or met by accident under another; when a plan's headline count does not reproduce, say so rather than adopt it.
- Abstract/body parity: every number in the abstract is also printed in the body, and the abstract uses the body's defined
  term for it. When a claim's scope has to widen to more models or configurations, widen the scope *words* and attribute the
  number with a short clause; do not replace a value with a range the body cannot back. Data existing in a frozen file is
  necessary but not sufficient — the body must print it before the abstract may.
- The promise check before any deletion or merge: collect what promises the thing being cut — the contribution list, the
  "we analyze …" sentence, every cross-reference into the section, every `\S\ref` of its label — and confirm after the edit
  that each promise still lands in the *built PDF*. A heading may disappear; a claim may not. For every number removed, grep
  the value across the section files first: if this is its last occurrence and another section prints or relies on it, it
  stays *(example: a summary's "8–36 %" was the only printed form of a fraction that §1 copied; it stayed while values that
  §3.2 still printed went)*.

## 3. Floats and pages — the rules LaTeX actually follows

- A `[t]` float renders on the page where LaTeX meets its source **or later**; a `figure*` renders at the top of the **next**
  page. This is a statement about pages, not columns: TeX's page builder is asynchronous, so a source met near the end of a
  column that has not yet been output can back-fill that column's top. To force the next column, push the source past a
  paragraph long enough to overflow the open column.
- Fix pages by moving the float's *source block*, marked with a placement comment (`% float placed early: renders on p. N`),
  never `[h]` or `\vspace`. Escalation if a float still slips: `[!t]`, then the class's `\topfraction`/`\dbltopfraction`
  and `\floatpagefraction` in the preamble. Source order sets the numbering, so a table can never be pushed past the next
  table's source or pulled before the previous one's, or every `\ref` renumbers.
- A departing `figure*` opens a hole on its old page that no other float refills (a later `figure*` cannot render on the page
  where it is met), so text slides up and every heading between the old and new page moves while the body end stays put.
  Recheck heading positions after every move.
- Page cost is a step function, not a line count. A text cut above a `[t]` float pulls it a column earlier; the cheaper lever
  is then to move its source later, which restores the old page at zero printed lines. The mirror holds: a text add pushes
  a float later, and pulling its source earlier restores the map and gives lines back. After any text change, check the
  float map first and pay with a source move before considering a text cut. Floats cascade — once one takes a column top,
  the next is deferred — so later blocks need less pushing than they look like they do.
- A `[t]` float is deaf to a source push *within its own column*; only a source met past the column break moves it. When a
  float will not move, the question is never "how much later" but "which side of the break". The reverse is not symmetric: a
  tall float cannot be pulled into a column with less room left than its height, so a column exchange is one-directional.
- Flush-bottom classes must put a short column's shortfall somewhere, and it pools at whatever stretchable glue is left in
  the column — typically a heading's `beforeskip` or `\textfloatsep`. Diagnose by measuring the baseline advance across the
  band against that construct's natural advance; confirm with an underfull-vbox warning between the shipout markers in the
  log. Fix by destretching that glue (redefine the heading skips without their `plus`, set `\textfloatsep` with `minus` only)
  so the slack falls to the column foot; never re-add stretch. Once nothing stretchable remains, a mid-column band means new
  stretch was added, and a white foot is a column-break necessity — a heading plus its non-widow lines that will not fit. A
  float move cannot change how much text a column holds except by its own height, so it over-corrects — unless the float
  leaves for the *other column of the same page*, which buys whole lines without touching prose. Report where the residual
  went and how big it is; "the white is gone" is only true of where the reader was looking.
- A float may legitimately precede its first reference when the author placed it so; report the separation, do not fix it.
- The formatting rule: no `\vspace`, no space squeezing, figure text at 8 pt or larger. These are the things a venue's
  format check rejects, and squeezed space is the first thing a reviewer's eye catches.
- A run-in head that ends in a capital letter followed by a period prints a double period under acmart's `\@addpunct`; write
  `LRU\@.` or drop the source period, and check every new head on the render.
- Never guess a `p{}` column width: probe natural widths with `\settowidth` in a scratch build and do the arithmetic against
  `\columnwidth`; measure a table's height with an `lrbox`, not from the page.

## 4. Build — a page placement claim is only as good as the build it was measured on

- Build font-faithfully: with the class's fonts installed and the packages the submission build uses, and confirm with
  `pdffonts` that the class's body font is present. A font-less fallback paginates about a page behind the real build, so
  every page placement judged on it is wrong. If the log says "You do not have …", the class fell back silently.
- Run the passes as `pdflatex; bibtex; pdflatex; pdflatex` — with `;`, not `&&`. Some classes exit non-zero on deliberate
  warnings, so an `&&` chain stops after the first pass and the log then shows dozens of undefined-citation lines that are
  not real. Gate on `Citation … undefined` = 0 in the log, `[?]` = 0 in the text layer, and the bibtex error count = 0.
  Record the clean baseline of `^!` lines the class prints deliberately and gate on additions, not on zero.
- BibTeX has no `%` comment syntax inside an entry: a comment line between fields breaks the entry silently (citations still
  resolve, only the `.blg` shows it). Keep such lines between entries and read the `.blg` error count.
- Verify per page with `pdftotext -f N -l N` and grep the caption's first words; `-layout` misses indented captions.
- The verification workflow for any figure or layout change: build the previous commit in a scratch directory
  (`git archive HEAD`, never the live tree) → per-page text diff and a float map diff (every figure, table, heading and the
  references heading with page and y) → rasterize the affected page with `pdftoppm` and *look at it* → report the body end
  (page, column, y), the page count, and that every heading and float is in place. The page budget is usually exactly full,
  so verification is by measurement, not by expectation.
- For a pure float-reordering pass, prove "no number moved" with a line-multiset diff over the union of touched files
  (`sort` both sides and `diff`): every line survived verbatim and only its position changed, which also catches an
  accidental re-wrap. Take the union, because a block crossing a file boundary breaks per-file multisets.
- Prove a highlight or colour is gone by rasterizing and counting pixels in the target hue. Named xcolor colours emit the
  CMYK operator `k`, not `rg`, so a content-stream scan for `rg` is a false negative even on a page that visibly carries
  the colour. Grep the sources for call sites separately from the macro definition; a definition with no call site prints
  nothing and is the author's to remove.
- `pdftotext -bbox` XML is not well-formed for ElementTree (stray control characters); regex-parse the `<word …>` elements
  and split pages on `<page `. Drop words with `x < 45` when a line ruler is on, match a heading's number and title by equal
  `yMin`, and tell a heading from a body line by glyph height. Read the *current* figure's MediaBox with `pdfinfo` before
  trusting a quoted canvas size.
- Shell hygiene: `env -C "$dir" pdflatex …` works from any cwd; never end a command chain with a `grep -c` that may return
  0 matches, or the whole call reports failure for nothing. Clean the `.aux/.bbl/.blg/.log/.out` after a scratch build.

## 5. References — verified before they print, and the bib stays publication-clean

- Every entry is verified against a primary source before it is cited — an arXiv abstract page, a DOI resolver, the
  publisher's page, a patent office, a vendor page — and gets one audit row: claim · source · location · verbatim quote ·
  status. Never accept your own memory of a paper as evidence; a fabricated or misattributed citation is the one defect a
  reviewer can confirm in a minute.
- The cited page must *print* the number the sentence asserts, not imply it. A ridge point on a roofline is not a batch
  size; a figure's axis is not a stated value. Before quoting a number about someone else's work, check the claim-level
  fact-check table, and log the check there before the number prints.
- Bib `note` fields hold only bibliographic information: an accessed date for a web-only source, a section pointer for a
  specification, an acceptance venue, a patent continuation, a version date, the authoring organizations when the author
  field lacks them. Verbatim quotes, "no venue listed", and claim verdicts are audit residue that would print in the
  reference list; they live only in the audit table. Never put a system name into a title the primary source does not carry.
- The word `TODO` must not appear anywhere in the bib file (grep gate). A bib-only change leaves the body pages
  byte-identical in `pdftotext`; verify with the map diff and report only the reference span.
- The page-number trap when quoting PDFs: proceedings PDFs (ACM, IEEE conferences) carry the page number in the *footer*, so
  a `pdftotext` page marker *terminates* its page; letter-format PDFs (IEEE CAL) carry it in the *header*, so the marker
  *starts* the page. Getting this backwards puts every page citation off by one. Cite section page ranges instead of a
  single page wherever the quote's section is known.
- arXiv PDFs fetched over the web may come back as binary; use the local PDF with `pdftotext -layout` and grep, or the
  abstract page. Anonymous submissions stay `{Anonymous}` with the URL and an accessed date.

## 6. Terminology and the change record

- One canonical name per concept, defined once, with its banned synonyms listed where the writers can see them. A second
  name for the same thing reads as a second thing *(example: "infinite-HBM oracle" defined once in §1 and once in its
  figure caption; "HBM-only" for the baseline node, never "stock"; a prior system's mechanism is an "LRU buffer")*.
- Terminology parity runs from the body outward: the abstract, the conclusion and every caption use the term the body
  defines, never a paraphrase of it.
- The commit message is the change record: what changed, why, and the gate results. Keep one home for it — no change map
  appended to a README, no log in a status file. A status file holds *current state*: section status, one block of key
  numbers, the newest handful of decisions, open issues. Its chronology moves to a history file under dated headings, never
  deleted. Never append a pass entry to an existing line; one thought, one line, and a new entry starts a new paragraph,
  because a single 99,000-character line makes every read of the file expensive for everyone.
