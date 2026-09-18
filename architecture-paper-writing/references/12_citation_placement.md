# Citation placement — making citation scope obvious

Part of the architecture-paper-writing skill. Governs: where a citation goes inside a sentence, in every section.
Read with: `references/01_sentence_style.md` (always), `references/10_production_and_verification.md` §references (what a
citation must be verified against), and `references/09_motivation_and_characterization.md` §D (how to print a rival's own
best number).

**The principle, in one sentence:**

> Cite an entity immediately after its name; cite a claim immediately after the smallest textual unit that expresses it.

Placement is not decoration and not a house habit — it is how a reader learns *what each reference is being held
responsible for*. A citation parked at the end of a sentence claims support for everything in that sentence. If the
reference does not support all of it, the placement is a factual error, not a style preference.

The common failure is mechanical: every citation pushed to the end of every sentence. That is the one habit this file
exists to break.

## A. The placement hierarchy

Decide in this order. The first row that matches the text you are writing decides where the brackets go.

| what the citation supports | where it goes | section it shows up in most |
|---|---|---|
| A named work, system, model, method, benchmark, dataset or artifact | immediately after the name | everywhere |
| A technical claim, empirical observation, known property or borrowed finding | immediately after the smallest clause expressing it | background, motivation, evaluation |
| A research *category* in a landscape sentence | immediately after that category | background, related work |
| Items in a list of examples drawn from different sources | after each example | background, introduction |
| Several independent claims inside one sentence | separately, one group per claim | everywhere |
| One claim that several works jointly establish | one group, after that claim | everywhere |

## B. A named entity is cited at its name

**Rule.** When the sentence names a specific prior system, model, method or artifact, the citation follows the name, not
the sentence.

**Why.** The citation is identifying the thing, and the reader is looking for the identification at the moment the name
appears. Deferring it to the end makes the reader hold an unresolved name for the length of the sentence, and — worse —
silently extends the citation's apparent scope to whatever else the sentence claims.

**Example.**
- *Yes:* "vLLM [42] manages the KV cache with PagedAttention." · "We compare against Orca [12] and vLLM [42]."
- *No:* "vLLM manages the KV cache with PagedAttention [42]." — now the citation reads as support for the claim about
  PagedAttention rather than as the identification of vLLM, which matters if the two have different sources.

## C. A claim is cited at the claim

**Rule.** When the citation is evidence for a proposition rather than the identity of a noun, it goes at the end of the
proposition.

**Why.** The unit being supported is the assertion. Placing the brackets at the assertion's boundary tells the reader
exactly how much of the sentence the literature is carrying.

**Example.** "Prefill is compute-intensive, whereas decode is bounded by memory bandwidth [1, 2, 35, 56, 84]." — the
brackets sit at the end because the whole contrast is the borrowed claim. Compare with §D, where it is not.

## D. Think in claim boundaries, not sentence boundaries

**Rule.** If one sentence carries two independently supported claims, cite each one separately.

**Why.** A single trailing cluster destroys the mapping. The reader cannot tell which half of your sentence each reference
was written about, and neither can a reviewer checking whether you read them.

**Example.**
- *Yes:* "Decode is typically memory-bandwidth-bound [1, 2], while prefill benefits substantially from batching [3, 4]."
- *No:* "Decode is typically memory-bandwidth-bound, while prefill benefits substantially from batching [1, 2, 3, 4]."

This is the rule that most often forces a sentence split. If the two claims need four references between them and the
sentence is already long, the repair is two sentences, not a cluster.

## E. In background and related work, cite the category

**Rule.** When a sentence organizes prior work into categories, each category takes its own group of references
immediately after it.

**Why.** The sentence's content *is* the mapping from categories to bodies of work. Collapsing the references into one
trailing list deletes exactly the information the sentence was written to convey.

**Example.**
- *Yes:* "Prior systems have explored request scheduling [3, 7, 14], KV-cache management [21, 25, 32], and model
  parallelism [40, 43]."
- *No:* "Prior systems have explored request scheduling, KV-cache management, and model parallelism [3, 7, 14, 21, 25,
  32, 40, 43]."

The same applies when the categories are of different kinds: "Hardware accelerators [34, 55, 60, 70, 79, 80] and
deployment schemes [3, 18, 64, 72] for on-device LLMs have also been proposed."

## F. In a list of examples, cite each example

**Rule.** When the examples come from different sources, each citation attaches to its own example.

**Why.** Same reason as §E: the mapping is the content.

**Example.** "AI functionality is increasingly available on edge devices, including voice transcription [11],
Circle-to-Search [25], and personal assistants [9, 24, 59]."

## G. Group references that jointly support one claim

**Rule.** When several works collectively establish the same observation, they form one group after that observation.
Do not scatter them across the clause to look thorough.

**Why.** Splitting a jointly-supported claim invents distinctions the literature does not make, and invites a reader to
look for a difference between the references that is not there.

**Example.** "Decode is commonly limited by memory bandwidth [1, 2, 35, 56, 84]." · "Compact LLMs for
resource-constrained devices have recently emerged [13, 29]."

## H. Repetition, and the author's own synthesis

**Rule 1.** If a named work is cited at its name and the rest of a short sentence plainly describes that same work, do not
repeat the citation at the end.

- *Yes:* "Prefix caching [37] precomputes KV caches for shared prefixes, reducing repeated prefill computation."
- *Usually no:* the same sentence with "[37]" again at the end.

Repeat it only when the trailing statement is a **distinct empirical claim** whose support would otherwise be ambiguous —
for instance a measured speedup taken from that paper rather than a description of its mechanism.

**Rule 2.** Do not force a citation onto a phrase that is your own synthesis. A sentence may legitimately carry a
literature-backed half and an interpretive half:

> "Hardware accelerators [34, 55, 60, 70, 79, 80] and deployment schemes [3, 18, 64, 72] for on-device LLMs have been
> proposed, accelerating the integration of on-device LLMs into everyday applications."

The brackets establish that the prior work exists. The closing clause is the paper's reading of what that body of work
adds up to, and citing it would misattribute your synthesis to those authors. This is the citation-level form of the
skill's standing rule that you never claim support that does not exist — see `10` §references.

## I. The failure mode, and the repair

**The failure mode** is a long sentence containing several unrelated claims with one cluster at the end:

> *No:* "LLM inference consists of prefill and decode, prefill processes input tokens in parallel, decode is
> autoregressive, and decode often dominates latency [1-8]."

Nothing here is checkable. Eight references stand behind four claims in unknown combination.

**The repair** is to split by claim and place each group at its own boundary:

> *Yes:* "LLM inference consists of a prefill phase that processes input tokens in parallel and a decode phase that
> generates tokens autoregressively [1, 2]. Decode is typically memory-bandwidth-bound [3-5] and can dominate end-to-end
> latency in conversational workloads [6, 7]."

Note that the repair also shortened the sentences, which is the usual side effect: ambiguous citation scope and
overlong sentences are the same defect seen from two directions.

## J. The LaTeX mechanics that placement creates

Moving a citation inside a sentence changes the line-breaking problem, so placement is a *number-bearing or structural*
edit in the sense of `10`, not plain wording. Three consequences recur:

1. **A tie before a citation is unbreakable.** `Name~\cite{key}` forbids a line break between the name and the brackets.
   Mid-sentence citations therefore create long unbreakable units, and in a two-column format a line holding one can
   protrude into the margin. If a line overflows after you move a citation, the fix is the tie, not the wording: use a
   normal space, or allow a break, rather than rewording a correct sentence.
2. **Punctuation follows the brackets**, not the other way round: "…bounded by memory bandwidth [1, 2], while…".
3. **A group prints as a range only if the class asks it to.** With natbib options including `sort&compress` (as ACM and
   IEEE classes commonly set), `\cite{a,b,c}` on consecutive numbers prints `[1–3]`; without it you get `[1, 2, 3]`. Do
   not hand-type either form — write the keys and let the class render them, or the numbers will drift the next time the
   bibliography changes.

Each citation you add still owes what `10` requires of every reference: a verified entry, and a cited page that actually
*prints* the claim. Placement makes the scope clear; it does not make the support real.

## K. Worked example (SPLEX, ASPLOS submission)

Four instances from the submission cycle. Where the exact printed sentence is not reproduced here, the edit is described
rather than quoted.

1. **A methodology paragraph regrouped by component (§E).** §6.1's area-model paragraph had its nine references scattered
   through the prose, each sitting wherever its sentence happened to end. The author's instruction was to "collect the
   references and arrange in a row for each part". The paragraph was rewritten so each component carried its own group —
   the SRAM estimate's five references, the core's two, the DMA-and-steering's two — with no reference left at a sentence
   boundary it did not belong to. Same nine references, same length; the mapping from component to source became
   readable.

2. **Named systems cited at the name (§B).** The introduction names exactly two prior systems, and each carries its
   citation at the name, so that the sentences that follow — which make claims about *this* paper's measurements — cannot
   be read as claims attributed to those papers.

3. **Related work: mechanism, then the rival's own number (§C).** §7's three run-in paragraphs each name a rival's
   mechanism, give that rival's own best published number, and only then state the measured gap. Each number is cited at
   the clause that states it, because the number belongs to that paper and the gap does not.

4. **The tie problem is real (§J).** After a pass that moved citations next to the names they identify, two lines on
   page 1 protruded three to five points into the right margin, caused by unbreakable `Name~\cite{key}` ties. The
   placement was correct and was kept; the protrusion is a line-breaking defect to be fixed at the tie.

The paper also carries a standing rule from `10`: all 41 references were verified against primary sources, and every new
reference gets a row in the audit table. Placement discipline and verification discipline are independent — a
perfectly-placed citation to a misattributed claim is still wrong.

## L. Guard classes (run before the commit)

1. **No trailing cluster on a multi-claim sentence.** For each sentence with two or more independently supported claims,
   confirm the references are split by claim. Mechanical first pass:
   `python3 scripts/check_prose.py --cite file.tex` flags sentences whose only citation group sits at the end while the
   sentence contains a clause break.
2. **Every named prior system carries its citation at the name** — grep the section for the names of the systems you
   discuss and check the brackets follow the name on first mention.
3. **Category sentences map one group per category** — in background and related work, every "A [refs], B [refs], and
   C [refs]" list has as many groups as categories.
4. **No unnecessary repetition** — a citation appearing twice in one sentence is justified only by a distinct empirical
   claim in the second position.
5. **No citation on your own synthesis** — the interpretive clause of a sentence carries no brackets.
6. **Every non-obvious borrowed claim has one** — the converse check; a technical assertion the paper does not measure
   itself and does not cite is either common knowledge or an unsupported claim.
7. **The reader test.** For each citation, ask: can a reader say in one phrase what this reference is being held
   responsible for? If the honest answer is "something in this sentence", move it.
