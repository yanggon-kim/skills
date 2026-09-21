---
name: architecture-paper-writing
description: Writes, rewrites, shortens and reviews computer-architecture and systems papers (ASPLOS, ISCA, MICRO, HPCA, ACM/IEEE two-column formats) one section at a time — abstract, introduction, motivation and workload characterization, design, methodology, evaluation, related work, conclusion — plus figure style, LaTeX floats, page limits and reviewer responses, with six bundled reference papers (Mesorasi, Tensor Casting, SmartSAGE, PACT'20 proactive vision, IEEE CAL characterization, LazyDP) as concrete examples of every rule. Use it whenever the user drafts or edits any part of an architecture paper, asks for "the style of ISCA/MICRO papers", a contribution list, a characterization paragraph from measurements, how to state a measured result, a rebuttal, a de-colloquialized section, a figure in "the LazyDP style", or why a float landed on the wrong page — even when the word "paper" is never said.
---

# Architecture paper writing

## Codex execution

Resolve bundled paths relative to this skill's directory from the installed catalog. Invoke scripts by their full paths with the working directory set to the user's project (or research workspace for tracker updates). Write results there, not into the skill. Use the tools actually exposed by the current Codex client.


A skill for producing prose that an architecture reviewer reads without friction: every sentence
carries a fact, a number or a necessary forward reference; every mechanism is defined before it is
elaborated; every number can be traced to its source; and each section follows the move order the
best papers in the field actually use. The rules were distilled from six reference papers and
sharpened by a full ASPLOS submission cycle; that paper survives inside the references as the
labelled worked example of each rule.

The skill is organized **by section**. Open only the reference for the section you are writing;
each is self-contained and ends with a worked example and a set of guard checks.

## How to use it

1. **Name the section and the edit class.** Section decides which reference you open (table
   below). Edit class — *wording*, *number-bearing*, or *structural* (a float, a heading, a
   dataset) — decides how much verification the edit needs; see
   `references/10_production_and_verification.md` when the class is not plain wording.
2. **Read the contract first, then the section guide.** `references/01_sentence_style.md` is
   the sentence-level contract and applies to every sentence of every section.
   `references/11_writing_lessons.md` is the author's corrections, stated as rules; it is the
   later word when a section guide disagrees. Then the section's own file.
3. **Open the reference paper the guide points at** when you need to see a move done well —
   `references/papers/INDEX.md` says which paper is the reference *for what* and gives the page
   ranges of each section, so you can open four pages rather than fourteen. Mind the page-number
   trap described there before citing a page.
4. **Write, then run the checks.** `python3 scripts/check_prose.py --system NAME file.tex`
   reports interrogatives, banned words, number density, own-system mentions and range forms; add `--cite`
   for citation-placement suspects —
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
| Figures, captions, colour | `references/02_structure_and_figures.md` §3 | luminance ramp for what exists, one tint for what you add, red only for small marks, four-spine charts, no hatches | LazyDP Fig. 9(b) and Fig. 11 |
| The paper's spine (which section carries which claim) | `references/02_structure_and_figures.md` §1–2 and `references/00_reading_order.md` | L1–L7 | all five Set-A papers |
| Citations — where the brackets go in a sentence | `references/12_citation_placement.md` | cite an entity at its name, a claim at the smallest clause expressing it; no trailing cluster on a multi-claim sentence | SmartSAGE, LazyDP (related-work landscapes) |
| Any build, float, page-limit, number-bearing or structural edit; adding a reference | `references/10_production_and_verification.md` | the edit-class matrix; floats fixed by moving source blocks; every cited page must *print* the number | — |

There is no dedicated related-work guide; the two references named cover what the reference
papers do, which is a short landscape with each rival's own number.

## The cross-cutting contract, in brief

These are stated fully in `01_sentence_style.md`, `11_writing_lessons.md` and `10`; this is the
list to hold in mind while drafting.

- **The sentence test.** A sentence earns its place with a fact, a number, or a forward reference
  the reader needs. Delete drum-rolls, self-praise, meta-commentary, restatement, and
  personification ("the data tells us", "placement needs more"). The preferred repair is a direct
  sentence, a colon, and the facts.
- **No questions to the reader** — neither a sentence ending in "?" nor an "asks whether / the
  question is" framing. State what the section measures or shows.
- **Claim only what exists.** Never print an API, register, call or mechanism name that no design
  document or measurement defines. A mechanism read from source but never exercised is described
  in present tense with its source cited — never "verified" or "measured", and never hedged as
  "assumed" or "not run".
- **Numbers are traced, not typed.** Each traces to a frozen data view, a design document or a
  verified citation; print both ends of a range, never "up to N"; judge a number against a cited
  external budget, not an adverb ("clearly", "merely"); a number is printed with its setting in
  reader order.
- **Define before elaborating.** Name → definition → validity → payoff → implementation → cost. A
  component is its role. Our mechanism first, the familiar precedent last, as a citation.
- **A characterization is not an advertisement.** In a motivation section the reference papers
  mention their own system zero to two times; cap it at one per subsection, placed last, and let
  the design implication follow the number rather than precede it.
- **Constrained results are trades, not gaps.** A result achieved under a budget is written as
  "the same outcome at a fraction of the cost", with the tolerance in the same clause as the cap —
  never as "N % behind the unconstrained baseline".
- **Run-in heads are blunt, general findings.** Concrete subject, plain verb, the scale in words: "Hot
  entries stay hot for hundreds of steps." Not the measurement itself — the number opens the sentence
  below — and never an abstraction or an evaluation. Pace the numbers: one or two per sentence, then their
  description; derived figures at most one per paragraph.
- **An evaluative adjective is replaced by the two quantities it compares.** "The deadline is loose" →
  "microseconds of work against a deadline of tens of milliseconds". A cost is stated at its unit and scaled to
  the system in the same sentence.
- **Numbers the figure carries are printed at their endpoints;** every figure citation names the thing to
  look at. Roles are stated positively — what a part does, never what it does not.
- **Citation scope is placement.** Cite an entity immediately after its name and a claim immediately after the
  smallest clause expressing it; split the references when one sentence carries two claims, and give each category
  or example in a landscape sentence its own group. A cluster at the end of a long sentence claims support for
  everything in it. Full rules in `12_citation_placement.md`.
- **Terminology discipline.** One canonical name per concept, defined once, with the synonyms you
  are *not* using listed somewhere you will see them. Readers notice a system called three things.
- **The banned list**, verified as absent from all six reference papers in the relevant
  sections: rhetorical questions; italic "Key takeaways:" labels; "clearly"; "it is interesting to
  note"; "up to N"; "compared to" (use "against"); sentence-initial "So"; "forever".

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
the rule above them. They show what a compliant paragraph looks like in a real draft; they are not
rules, and their numbers belong to that paper alone.

## When the guides disagree

`11_writing_lessons.md` is the later word over any section guide, because it records what the
author corrected *after* the guides were written. `09` §H lists where the reference papers'
practice conflicts with these rules and which side wins; the same reasoning applies to any new
conflict: a reference paper shows what has passed review, the house rule shows what this author
has decided, and the house rule wins unless the guide says otherwise.

## Scope

This skill covers prose, structure, figures, and the production mechanics of a LaTeX paper. It
does not run experiments, produce the numbers, or decide what a paper claims — it makes what is
claimed read correctly and verifiably. For a grant proposal, a blog post, a thesis chapter or a
theory paper the section guides still apply loosely, but the move orders and the reference papers
are specific to architecture and systems venues.
