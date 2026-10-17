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
  (Repeating a *noun phrase* so the reader knows what a clause is about is not restatement — see §5.2.)
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

## 5. Grammar the reader can parse on the first pass (owner, 2026-10-16)

The cuts above make sentences shorter; these rules keep the shorter sentence parseable. They were written after
the owner flagged DAC-paper sentences in which a reader could not find the subject, the verb or the referent.

### 5.1 Every clause has a visible subject and a finite verb
- An equation is never a clause on its own. "…, D = 4, and …" between commas leaves the reader to supply the
  verb; write "fits D = 4 beats", "gives D = 4", "D equals 4".
- At most **one** fronted setting per sentence. A list of settings goes after the verb, attached to the noun
  it qualifies.
- Before: "At 0.8 GHz on LPDDR5-6400 and 1 GHz on HBM2, D = 4, and a stock PU uses one beat." (three
  constructions joined by commas; only the last has a subject and verb) → After: "A PU clocked at 0.8 GHz on
  LPDDR5-6400 or at 1 GHz on HBM2 fits D = 4 beats into each column period; a stock PU uses one of them."
  *(DAC example)*
- Check: read each comma-separated piece alone; every piece that carries a claim must have its own verb.

### 5.2 Name, don't point
- Write the noun phrase again instead of "the two", "both", "the former / latter", "it", "this", "they"
  whenever the antecedent sits outside the current clause or more than one noun could fit. A clarifying repeat
  is not restatement, and it costs two or three words that the reader would otherwise pay for by re-reading.
- A pronoun is fine when its only possible antecedent is in the same clause ("a PU and its accumulator").
  Possessive "its" on the subject of the same sentence is normal; do not over-correct it.
- A sentence never opens with a bare "This" or "It" that points at the previous sentence: name the thing
  ("This cap", "The crossover").
- Before: "…and derive the depth a column allows once the two are separated" → After: "…once MAC timing is
  separated from command timing". Before: "Two deployments create it." → After: "Two deployments create skinny
  GEMMs." *(DAC examples)*
- Check: grep the section for `the two|both|\bit\b|\bthis\b|they|them|former|latter` and resolve each hit
  by looking only at its own sentence.

### 5.3 Section and subsection titles are noun phrases
- A `\section` / `\subsection` title names the topic in engineering terms: "Command Interface", "PU
  Microarchitecture", "PIM–Host Crossover", "Sources of the Gain". It is never a sentence ("Every Prior
  Design Paces MACs by Commands"), a where / how / why clause ("Where PIM and Host Cross", "Where the Gain
  Comes From"), or a result with a number ("1.68× P3-LLM-Style's Speed").
- A labelled claim is allowed once per section when it is the section's thesis, written as label + noun
  phrase or label + compact statement: "The Opportunity: DRAM Timing Bounds Access, Not MACs".
- The blunt-finding rule (`11_writing_lessons.md` "Run-in heads are blunt findings") governs **run-in
  `\paragraph` heads only**, never numbered titles.
- A number dropped from a title must still be printed in that subsection's text (promise check, `10`).

