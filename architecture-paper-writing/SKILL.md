---
name: architecture-paper-writing
description: Writes, rewrites, shortens and reviews computer-architecture and systems papers (ASPLOS, ISCA, MICRO, HPCA, ACM/IEEE two-column formats) one section at a time — abstract, introduction, motivation and workload characterization, design, methodology, evaluation, related work, conclusion — plus figure style, LaTeX floats, page limits and reviewer responses, with six bundled reference papers (Mesorasi, Tensor Casting, SmartSAGE, PACT'20 proactive vision, IEEE CAL characterization, LazyDP) as concrete examples of every rule. Use it whenever the user drafts or edits any part of an architecture paper, asks for "the style of ISCA/MICRO papers", a contribution list, a characterization paragraph from measurements, how to state a measured result, a rebuttal, a paragraph outline of a paper (outline.md: one message per paragraph, edited before the LaTeX), a de-colloquialized section, a figure in "the LazyDP style", or why a float landed on the wrong page — even when the word "paper" is never said.
---

# Architecture paper writing

A skill for producing prose that an architecture reviewer reads without friction: every sentence
carries a fact, a number or a necessary forward reference; every mechanism is defined before it is
elaborated; every number can be traced to its source; and each section follows the move order the
best papers in the field actually use. The rules were distilled from six reference papers and
sharpened by a full ASPLOS submission cycle; that paper survives inside the references as the
labelled worked example of each rule.

The skill is organized **by section**. Open only the reference for the section you are writing;
each is self-contained and ends with a worked example and a set of guard checks.

## How to use it

0. **Outline first, and plan before you edit.** The paper's structure lives in `outline.md`: one entry per source paragraph, each with a
   one-sentence message and its floats, numbers, citations and promise links, tied to the `.tex` by `% P:<id>`
   anchors. Capture the outline once from the current draft. After that, make every structural change (add, cut,
   merge, move a paragraph, change its message, move a float) in the outline first, then edit the `.tex` to
   match, and commit both together; `scripts/check_outline.py` keeps the two in sync. Wording-only edits need no
   outline change. Full procedure and format: `references/13_outline_first.md`. When the author is reviewing the
   draft, turn their comments into an edit plan first (the outline change and the before → after sentence for each
   comment), edit only after approval, and push only when told to (`11` A1).
1. **Name the section and the edit class.** Section decides which reference you open (table
   below). Edit class — *wording*, *number-bearing*, or *structural* (a float, a heading, a
   dataset) — decides how much verification the edit needs; see
   `references/10_production_and_verification.md` when the class is not plain wording.
2. **Read the contract first, then the section guide.** `references/01_sentence_style.md` is
   the sentence-level contract and applies to every sentence of every section.
   `references/11_writing_lessons.md` is the author's corrections, stated as rules and grouped in writing order
   (A process, B structure, C openers, D content, E brevity, F sentences, G numbers and figures, H section-specific);
   it is the later word when a section guide disagrees, and its opener table (C1) decides how every paragraph starts.
   Then the section's own file.
3. **Open the reference paper the guide points at** when you need to see a move done well —
   `references/papers/INDEX.md` says which paper is the reference *for what* and gives the page
   ranges of each section, so you can open four pages rather than fourteen. Mind the page-number
   trap described there before citing a page.
4. **Write, then run the checks.** `python3 scripts/check_prose.py --system NAME file.tex`
   reports interrogatives, banned words, number density, own-system mentions and range forms; add `--cite`
   for citation-placement suspects and `--captions` for caption length and caption text repeated in the prose —
   the mechanical half of the guides' guards. It is a report, not a gate; read it, then apply the
   section's reader test by hand.
5. **Apply the reader test.** Each section guide ends with one. They exist because prose that
   reads fine to its author is routinely under-specified to a stranger: the test asks whether each
   sentence can be explained with a concrete example, and a sentence that cannot is rewritten or
   cut.
6. **For any deletion, merge or shortening, run the promise check** (in `10`): grep the rest of
   the draft for what depends on the text you are removing. A heading may disappear; a claim may
   not; some numbers are another section's only source.

## Section → reference map

| section you are writing | open | its reader test, in one line | paper to open for a model |
|---|---|---|---|
| Abstract | `references/03_abstract.md` | seven moves in order, ≤ 200 words, every number also printed in the body | Tensor Casting, LazyDP |
| Introduction | `references/04_introduction.md` | eight-move arc; landscape opener; claim-first paragraphs; verb-led contribution list | SmartSAGE, PACT'20 vision |
| Background / motivation / workload characterization | `references/09_motivation_and_characterization.md` | five-role reader test; ~one sentence in three carries a number; at most one mention of your own system, placed last | IEEE CAL (the archetype), LazyDP, Mesorasi |
| Design — any named mechanism | `references/05_design.md`, **then** `references/08_design_section_lessons.md` | name → definition → validity → payoff → figure → implementation → cost; every sentence explainable with a concrete example | Mesorasi, Tensor Casting, SmartSAGE |
| Methodology and evaluation | `references/06_methodology_evaluation.md` | claim first, figure pointer second; a fact in a table is never repeated in prose; one headline number per subsection; both ends of every range | PACT'20 vision, SmartSAGE, Mesorasi |
| Related work | `references/04_introduction.md` §A (the landscape moves) and `references/09_…` §D (how to print a rival's best case) | each rival's mechanism named, its own best number given, then the measured gap | SmartSAGE, LazyDP |
| Conclusion | `references/07_conclusion.md` | five moves; claim → key idea → what was done → one number → outlook; no result clause; ~115 words | PACT'20 vision, Tensor Casting |
| Figures, captions, colour | `references/02_structure_and_figures.md` §3; diagrams prototyped in HTML, then PDF (`10` §7) | luminance ramp for what exists, one tint for what you add, red only for small marks, four-spine charts, no hatches; a background concept gets a block diagram + command timeline (F8); a micro-architecture figure is a block diagram, never a flowchart (F9); fill the figure's rectangle — full-height side blocks, packed blocks, "…" arrays, text ≥ caption size (F10); a minimal caption names what is drawn, and the setting and finding go in the paragraph (F11); one float per column of a page, floats spread across pages (F12) | LazyDP Fig. 9(b) and Fig. 11; LoCaLUT Fig. 1, P3-LLM Fig. 7, GROW Fig. 8, TensorDIMM Fig. 6(a) (cited, not bundled) |
| The paragraph outline: capturing it, editing it, then editing the paper to match | `references/13_outline_first.md` | every paragraph has one entry with one message; every intro promise links to the entry that proves it; `check_outline.py` passes | — |
| The paper's spine (which section carries which claim) | `references/02_structure_and_figures.md` §1–2 and `references/00_reading_order.md` | L1–L7 | all five Set-A papers |
| Citations — where the brackets go in a sentence | `references/12_citation_placement.md` | cite an entity at its name, a claim at the smallest clause expressing it; no trailing cluster on a multi-claim sentence | SmartSAGE, LazyDP (related-work landscapes) |
| Any build, float, page-limit, number-bearing or structural edit; adding a reference | `references/10_production_and_verification.md` | the edit-class matrix; floats fixed by moving source blocks; every cited page must *print* the number | — |

There is no dedicated related-work guide; the two references named cover what the reference
papers do, which is a short landscape with each rival's own number.

## The cross-cutting contract, in brief

The full rules, with the author's reasons and before → after examples, are in `11_writing_lessons.md`, grouped in the
order below and cited by id (`11` C4). Sentence mechanics are in `01`, production mechanics in `10`. When this summary and
a section guide disagree, `11` wins. Hold this list in mind while drafting, in this order.

**A. Process**
- **Plan, then edit, then push on approval** (A1). Structure changes go into `outline.md` first (`13`). When the author is
  reviewing, answer comments with an edit plan (outline change plus before → after sentence for each comment) and edit
  only after approval. Push only when told to.
- **Verify a plan's premise** before executing it (A2); **adopt clean author edits** and flag deviations rather than
  reverting them (A3).
- **Cuts drop the clause, never rewrite the fact** (A4); a space request cuts qualifiers, never a number, control or promise
  (A5); every deletion, merge or move runs the promise check (A6, `10`).

**B. Structure**
- **One role per paragraph, and a visible arc** (B1), e.g. *what is possible → why it is feasible → what the design does*.
- **Define before use** (B2): every symbol and term at its first appearance. Background defines the prior mechanism and
  stops; it never previews the design.
- **Order items so each leads into the next** (B3), and announce the order once.
- **Never merge findings of different kinds** (B4); **delete rather than merge** a paragraph that does not serve the argument
  (B5). One paragraph per agenda in a mechanism introduction (B6); the borrowed-mechanism paragraph has its own order (B7).
- **Every heading is a noun phrase** (B8): section, subsection and run-in heads. **A run-in head marks a sibling topic, and
  only where it helps** (B9): a paragraph that views the same items from another angle gets no head.
- **Transitions at turning points; map once, never re-map** (B10). One content-carrying sentence where the argument changes
  mode, naming and mapping what follows; a section's last paragraph bridges causally into the next ("…; we therefore …").
  Never "we explain them next", and never repeat a map the reader already has.
- **One configuration table** (B11): the first use defines a concept and points to the table; later uses cite the table.

**C. Openers** — every paragraph opens with its core message; the opener decision table (C1) says what that is for each kind:
- a finding whose setting is established → the blunt finding in words, the number next (C2);
- a measurement or test with a new setting → the setting first, the finding within one or two sentences; describe a test
  before naming it (C3);
- a term the paper defines → one plain, symbol-free sentence saying what it is, then setting, cause, equation, value, cost (C4);
- a figure's experiment → what the figure shows, then the setup, then the details and the table pointer (C5);
- a cause → "X arises because Y", stated directly (C6);
- a subsection opener → the frame only (the families or causes and the figure), no numbers (C7);
- a prior-work family → its defining trade-off or limit (D1); an evaluation result → the claim, then the figure pointer (`06`);
- a design mechanism → its definition, then validity → payoff → figure → implementation → cost; a component is its role;
  our mechanism first, the familiar precedent last, as a citation (`05`, `08`).

**D. Content**
- **Introduce each prior-work family by its defining trade-off or limit** (D1) — the property the paper's design changes.
- **Mark the paper's own terms as its own** ("We define … as the sweep factor") (D2). **Justify a modelling choice with the
  prior work it follows**, attributing only what that work does (D3).
- **Cite the informative statistic** (D4); state a constrained result as a trade, the tolerance in the cap's clause (D5).
- **Claim only what exists**: no invented interfaces (D6); a mechanism read from source is described in the present tense
  with its source, never "verified" and never hedged (D7).
- **Replace an evaluative adjective with the two quantities it compares** (D8); state a cost at its unit and scale it to the
  system in the same sentence (D9); say what a component does, not what it does not (D10).
- **Terminology discipline**: one canonical name per concept, defined once; keep a list of the synonyms you are *not*
  using. Readers notice a system called three things.
- **A characterization is not an advertisement**: in motivation, mention your own system at most once per subsection, last,
  and let the implication follow the number (`09`).

**E. Brevity**
- **The sentence test** (E1): a sentence earns its place with a fact, a number or a needed forward reference. Delete
  drum-rolls, self-praise, meta-commentary and personification; repair with a direct sentence, a colon and the facts.
- **No repetition at the sentence level** (E2): say each fact once; point back to a definition instead of re-explaining it.
  A repeated noun is fine (F2); a repeated claim is not.
- **Scope of detail** (E3): cut true details that do not serve the message — tolerances, side effects, out-of-scope notes,
  unevaluated extrapolations — and related work that blurs the paper's distinction.
- **Shares over raw values; one worked case** (E4). **No audit trail** in method and evaluation prose (E5).

**F. Sentences**
- **Every clause has a subject and a finite verb**; no equation stands as a clause; at most one fronted setting (F1, `01` §5.1).
- **Name, don't point** (F2): repeat the noun instead of "the two", "both", "it", "this".
- **No questions to the reader** (F3). **Cite at the proper noun** (F4, `12`): "AttAcc~\cite{attacc} runs …".
- **The banned list**, absent from all six reference papers in the relevant sections: rhetorical questions; italic "Key
  takeaways:" labels; "clearly"; "it is interesting to note"; "up to N"; "compared to" (use "against"); sentence-initial
  "So"; "forever".

**G. Numbers and figures**
- **Pace the numbers**: one or two per sentence, each described; at most one derived figure per paragraph (G1). Print both
  ends of a range, with the setting attached to the noun it qualifies.
- **A plotted series is printed at its endpoints** (G2); **every figure citation names what to see** (G3).
- **Minimal captions** (G4): the caption names what is drawn; setting and finding go in the citing paragraph (`02` F11).
- **One float per spot** (G5, `02` F12); **the figure visual system** (G6): luminance ramp for what exists, one tint for what
  you add, red only for small marks, no hatches, four spines.
- **Numbers are traced, rounded once from the source, and asserted** by the script that prints them (G7).

**H. Section-specific**
- **Introduction** (H1, `04`): landscape opener, subject-first claims, symbols out of §1, verb-led contributions.
- **Abstract** (H2–H4, `03`): open on the problem, join every move to the last, follow the move order, and state the positive
  finding rather than negating an alternative the reader has not met.

## The reference papers

Six papers, bundled in `references/papers/` so the guides can point at a page rather than
describe one. `INDEX.md` there carries titles, venues, page counts, what each is the reference
*for*, which guides cite it, and per-section page ranges.

| tag | file | open it for |
|---|---|---|
| [M] | `mesorasi-micro20.pdf` | the top-down walk-through of a mechanism; closing `Summary.` paragraphs instead of italic takeaways; how densely "Figure N shows" is used in evaluation |
| [TC] | `tensor-casting-hpca21.pdf` | the driving-example framing of a design; abstract diction; a conclusion that names "the unique contribution of our study"; saying "first" once |
| [SS] | `smartsage-isca22.pdf` | the key-intuition figure; a design-points bullet list; "Figure N summarizes" evaluation openers |
| [PVF] | `low-latency-proactive-vision-pact20.pdf` | claim-first, figure-second evaluation paragraphs; judging a number against a cited budget; "This paper argues that" |
| [CAL] | `characterization-3d-point-cloud-cal21.pdf` | the archetype of a characterization section — four pages that are nothing else; the reason a characterization carries no table |
| [LazyDP] | `lazydp-asplos24.pdf` | the entire figure and colour system (Fig. 9(b) for arrow classes and circled numbers, Fig. 11 for the tint); breakdown-paragraph skeletons — and two practices deliberately *not* copied, questions to the reader and "Key takeaways" |

**Before citing a page:** the five proceedings PDFs print the page number in the footer, so in
`pdftotext` output the number marker *ends* its page; IEEE CAL prints it in the header, so its
marker *starts* the page. Reading one convention as the other puts every page citation off by
one. Cite a section's page range from `INDEX.md` rather than a single page you counted yourself.

## Worked examples

Every reference ends with a block headed **Worked example (SPLEX, ASPLOS submission)** — the
sentences, figures and numbers of the paper these rules were forged on, kept as illustrations of
the rule above them. `11_writing_lessons.md` adds examples from two later papers, labelled *DAC*
and *CoDe* (the DAC draft and the ISCA submission of a command-decoupled PIM). They show what a
compliant paragraph looks like in a real draft; they are not rules, and their numbers belong to
those papers alone.

## When the guides disagree

`11_writing_lessons.md` is the later word over any section guide, because it records what the
author corrected *after* the guides were written. `09` §H lists where the reference papers'
practice conflicts with these rules and which side wins; the same reasoning applies to any new
conflict: a reference paper shows what has passed review, the house rule shows what this author
has decided, and the house rule wins unless the guide says otherwise. Inside `11`, rules never
contradict each other: where two seem to (a finding-first opener against a setting-first one), the
opener table `11` C1 says which applies to which kind of paragraph. A new lesson is added to the
part of `11` where it belongs and mirrored in the same part of the contract above, never appended
as a separate list.

## Scope

This skill covers prose, structure, figures, and the production mechanics of a LaTeX paper. It
does not run experiments, produce the numbers, or decide what a paper claims — it makes what is
claimed read correctly and verifiably. For a grant proposal, a blog post, a thesis chapter or a
theory paper the section guides still apply loosely, but the move orders and the reference papers
are specific to architecture and systems venues.
