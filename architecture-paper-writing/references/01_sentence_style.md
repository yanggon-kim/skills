# Sentence-style tips — the sentence-level contract

Part of the architecture-paper-writing skill. Governs: every sentence in every section. Read with: references/01_sentence_style.md (always) and references/11_writing_lessons.md.

Distilled from the user's feedback on the v4 §2/§3 rhetoric pass (2026-08-31). This is the
sentence-level companion to `02_structure_and_figures.md` (which governs structure, figures, and argument
shape). Every example below is a real before/after from the SPLEX draft, marked *(SPLEX example)*.

## 1. The test

A sentence earns its place with **a fact, a number, or a necessary forward reference**. If it has
none of the three, delete it and stitch the neighbors. Apply the test to clauses too: a factual
sentence can still carry a freeloading clause.

## 2. Delete these species

- **Drum-roll / puzzle setup** — a sentence whose only job is to announce that the next sentence
  matters. Name the thing immediately.
  - Before: "That optimum has a weakness. It presumes room in HBM for 77% of the latent
    entries, and …" → After: "That optimum presumes room in HBM for 77% of the latent entries;
    in the memory-bound MoE decode that room is taken by …" *(SPLEX example)*
- **Self-characterization / advance praise** — the text grading its own subject before showing it.
  - Before: "Two capabilities follow, and their combination produces a new memory organization."
    → After: deleted; the two run-in headings that follow carry the structure. *(SPLEX example)*
  - Same species: "SPLEX assigns each to the agent that already holds the needed information"
    (removed in the §4 pass). *(SPLEX example)*
- **Meta-commentary on the writing itself.**
  - Before: "three bandwidths, stated plainly:" → After: "three bandwidths:". *(SPLEX example)*
  - Before: "The substrate, in short, is arriving." → After: deleted; the paragraph opens directly
    with "Each HBM site can become the head of a small memory network: …". *(SPLEX example)*
- **Restatement-with-drums** — a second clause that repeats the first with emphasis.
  - Before: "… must be measured against it; no static property of the memories supplies it."
    → After: "… must be measured against it." *(SPLEX example)*
- **Evaluative metaphors on our own design.**
  - Before: "exactly 2048 entries per query, selected by the model itself -- a stable contract an
    architecture can provision against." → After: ends at "selected by the model itself." *(SPLEX example)*
  - Same species: "the budget is the far tier's price for tracking, and it is small." *(SPLEX example)*
- **Rhetorical anticipation and personification.**
  - Before: "A link equal to one stack's wire is not the bottleneck it may seem, because …"
    → After: "A link at one stack's wire peak does not bottleneck the gather: …" *(SPLEX example)*
  - Before: "the selection statistics just measured say that it can be done:"
    → After: "the measured statistics support it:". *(SPLEX example)*
  - Before: "implements exactly this" → After: "implements this" (intensifiers are drums too). *(SPLEX example)*

## 3. Keep these (user-calibrated)

**Preparation is allowed; praise and suspense are not.**

- **Short introductory sentences that prepare the reader for upcoming facts.** They pass the test
  as necessary forward references: the reader needs to know what list is coming.
  - Kept: "Two implications frame this paper." (introduces the (i)/(ii) pair that follows.) *(SPLEX example)*
  - Kept: "Serving systems have begun to measure and exploit the statistics of these selections."
    (introduces the ESS/HiSparse survey.) *(SPLEX example)*
- **Thesis/antithesis sentences that ARE the argument**, not decoration around it.
  - Kept: "bandwidth of the wrong shape"; "not how many, but which". *(SPLEX example)*
- **Compact factual aphorisms** — short sentences whose content is a fact.
  - Kept: "an undecayed count never forgets"; "The batch axis multiplies this." *(SPLEX example)*
- Sentence adverbs that mark a real logical turn ("Critically,") were reviewed and kept.

The distinction from species 2: a keeper tells the reader *what is coming or what is true*; a
delete-candidate tells the reader *how to feel about it* (praise), *that something is about to be
revealed* (suspense), or *how it is being said* (meta).

## 4. The preferred fix pattern: direct sentence, colon, facts

When an announcement sentence precedes a factual one, do not just delete it — **merge the
announcement into the first factual sentence**: a direct claim, a colon, then the facts. The user
explicitly endorsed this pattern (fixes 8, 12, 13 of the 2026-08-31 pass).

- "DeepSeek-V3.2 builds the sparsity that H2O and InfiniGen approximated into the model itself:
  DeepSeek Sparse Attention (DSA), layered on multi-head latent attention (MLA), …"
  (replaced "What H2O and InfiniGen approximated with system-side heuristics is now built into the
  model. DeepSeek-V3.2 introduces …") *(SPLEX example)*
- "A link at one stack's wire peak does not bottleneck the gather: the kernel -- identical across
  DeepSeek-V3.2, GLM-5, and GLM-5.2 -- reaches 2,197 GB/s …" *(SPLEX example)*
- "… and the measured statistics support it: the hot entries are few, layer-dependent, …" *(SPLEX example)*

Merging by trailing clause also works when the announcement closes a paragraph:
"… and what the base-die logic must contain -- the subject of this paper." (replaced a standalone
"That is the subject of this paper.") *(SPLEX example)*
