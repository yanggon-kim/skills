# Voice: controlled language, applied loosely

The page's prose follows the spirit of ASD-STE100 Simplified Technical English — the controlled
language written for aircraft maintenance manuals — without its full rulebook. There is no approved
dictionary, no hard word limit per sentence, and no ban on verb forms. What stays are the
principles that make a hard idea easy to read. They apply in every language.

## The four core principles

These are the user's own rules. Every sentence on the page is checked against them.

| principle | 원칙 | what it means on the page |
|---|---|---|
| **Short sentences** | 짧은 문장 — 한 문장에 너무 많은 정보를 넣지 않기 | Most sentences stay under about 20 words. A sentence that needs two commas and a "which" is usually two sentences. |
| **Plain words** | 쉬운 단어 — 복잡하거나 모호한 표현 피하기 | Use the common word ("use", "start", "about") over the formal one ("utilize", "commence", "approximately"). No vague words that hide the fact ("various", "certain", "significant"). |
| **Active voice** | 능동태 — 누가 무엇을 하는지 명확하게 쓰기 | Name who or what does the action. The reader must always know which part of the system acts. |
| **One idea per sentence** | 한 문장에 하나의 생각 — 독자가 헷갈리지 않도록 하기 | A sentence states one fact, one step, or one cause. "And" joining two facts is a sign to split. |

## Three supporting rules

These come from the learning-ladder document. Each prevents a specific failure.

1. **One term per concept.** Pick one name and keep it to the last line. If the field has synonyms,
   mention them once ("also called ...") and never use them again. A reader who sees two names
   assumes two things.
2. **Example first, then the term.** Show the thing working, then give it its name. Technical terms
   are allowed — the reader came to learn them — but each one appears only after the reader has
   seen what it names, and it is defined in plain words the first time.
3. **Keep facts, assumptions and examples apart.** Say which kind of statement each one is. "In this
   example, ..." for an example. "We assume ..." for a simplification. A plain sentence for a fact.

## What "loosely" means

The rules serve the reader, not a score. Break one when keeping it would make the page worse:

- A precise sentence of 26 words beats two vague sentences of 13.
- Keep the passive when the actor is unknown or does not matter ("The packet is dropped" when no
  single component is to blame).
- Precision beats simplicity. Never round a true statement into a false one to make it shorter. If
  the full truth is complicated, state the simple version and name what it leaves out.
- Simple does not mean childish. No "imagine a magical box", no talking down, no exclamation marks.

## Before and after

**Too many ideas in one sentence**
> Before: Warp divergence, which occurs when threads within the same warp take different paths at a
> branch, causes the hardware to serialize execution of each path, reducing effective throughput.
>
> After: A GPU runs threads in groups of 32, called warps. All threads in a warp run the same
> instruction at the same time. When a branch sends some threads one way and some the other, the
> warp runs both paths, one after the other. Threads on the inactive path wait.

**Passive hides the actor**
> Before: The commits are rewritten and the history is linearized.
>
> After: Rebase copies each of your commits onto the new base. Git gives each copy a new ID. Your
> branch now points to the copies.

**Vague words hide the fact**
> Before: A positive test result may significantly overstate the actual probability of disease.
>
> After: Suppose 1% of people have the disease. The test catches 90% of them, and it wrongly flags 9%
> of healthy people. Then only about 9 of every 100 people who test positive have the disease.

**Term before example**
> Before: The base rate is the prior probability of the condition in the population.
>
> After: In a city of 10,000 people, 100 have the disease. That 1% is the base rate: how common the
> condition is before anyone takes a test.

**Korean: translationese passive and noun chains**
> Before: 해당 연산의 수행이 완료되어진 후에 결과값의 메모리로의 저장이 이루어진다.
>
> After: 연산이 끝나면 GPU가 결과를 메모리에 저장한다.

In Korean, watch especially for double passives (되어지다, 이루어지다), long "의" chains, and
sentences that end in a noun phrase plus "이다" when a verb would say it directly.

## Banned on the page

These add words without adding facts, or they make the page sound like an advertisement:

- Filler: "simply", "just", "basically", "essentially", "actually", "it is worth noting", "it is
  important to note", "in other words" (say it right the first time).
- Hype: "powerful", "revolutionary", "game-changing", "cutting-edge", "seamless", "magic".
- Throat-clearing openers: "In today's world", "Have you ever wondered", "Let's dive in".
- Chains of rhetorical questions. The page opens with **one** question — the reader's question —
  and then answers it. After that, a question appears only as a prediction prompt the reader
  actually answers.
- Mannered devices: asides set off by dashes, "it's not X — it's Y" reveals, scare quotes around
  invented labels.

## Self-check for a paragraph

Read each sentence and ask:

1. Who or what does the action? (If unclear, rewrite in active voice.)
2. How many facts does it carry? (More than one: split.)
3. Is every term already defined above this point? (If not, move the definition up.)
4. Could the reader explain this sentence with a concrete example? (If not, add the example or cut
   the sentence.)
