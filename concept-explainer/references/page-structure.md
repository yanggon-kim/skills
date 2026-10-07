# Page structure, diagram and interaction

## Contents
1. Section order
2. Diagram
3. Interaction
4. The four-way review

## 1. Section order

The order follows how understanding is built: the reader's question, what they already have, why
the problem exists, how the mechanism solves it, a chance to test it, and what to take away. Every
section is short. A typical page carries 600–1,300 words in total, counting captions, terms and the
limits box (this is what `check_page.py` counts; it warns outside 400–1,500). The core explanation
(problem + mechanism + result) is about 250–450 of them.

| # | section | job | length |
|---|---|---|---|
| 0 | **Title + one-sentence answer** | The title names the concept. Under it: the reader's question as an `h1`-adjacent line, then a one-sentence answer that states the central idea. A skimmer gets the idea here in under 20 seconds. | 1 question, 1–2 sentences |
| 1 | **What you already know** | Anchor in something familiar: a daily experience or a concept the reader surely has. This is the bridge, not an analogy that later breaks. | 2–4 sentences |
| 2 | **The problem** | What goes wrong, or what is hard, without the mechanism. Make the reader feel the cost with a concrete case and, if possible, a number. | 1 short paragraph |
| 3 | **The mechanism** | How it works, step by step, with the diagram beside it. Show each step working before you name it. | 2–4 short paragraphs + diagram |
| 4 | **Try it** | The interaction: predict, act, compare, explain. | widget + 2–3 sentences |
| 5 | **The result** | What the mechanism buys, and what it costs. Every mechanism has a trade-off; name it. | 1 paragraph |
| 6 | **A common misconception** | One wrong belief people hold, why it is tempting, and what is true instead. | 3–5 sentences |
| 7 | **Recap** | Three to five lines, one idea each, in the order the page taught them. | 3–5 bullets |
| 8 | **Terms** | The three terms the page taught, each with a one-line plain definition. | 3 entries |
| 9 | **Assumptions and limits** | What the page simplified, what it left out, and anything not verified. | 2–5 bullets |

Headings are plain statements or the plain section names above; avoid clever headings. Number the
sections only when the order is a real sequence the reader follows (it usually is not — the page is
read top to bottom anyway).

## 2. Diagram

### Choose the type that matches the idea

| the idea is about | diagram type |
|---|---|
| steps in order | flow (left to right, or top to bottom) |
| a thing that changes mode | state diagram |
| parts and how they connect | system map |
| events over time, overlap, waiting | timeline (time runs left to right) |
| two designs or two cases | side-by-side comparison, same scale on both sides |
| a stack of abstractions | layers |
| why A leads to B | cause-and-effect chain |

### Rules

- **One reading direction.** Left to right or top to bottom. The eye never has to backtrack.
- **At most seven primary elements.** Boxes, lanes or nodes that carry meaning. Labels and arrows
  do not count. If you need more, the diagram is two ideas; keep the one that shows the mechanism.
  A two-case concept (merge vs rebase) may use two side-by-side panels of at most seven elements
  each, or put the second case in the widget. Small graphs inside the widget follow the same rules
  but do not count as a second diagram.
- **Every arrow has one meaning.** "Data moves", "time passes", "causes" — pick one per arrow style.
  If two styles appear, a small legend says what each means.
- **Labels work without the prose.** A reader who looks only at the figure and its caption gets
  the main relationship.
- **It reads in grayscale.** Color supports a distinction that shape, line style, position or a
  label already makes. Coral marks the one thing the reader should look at, not everything.
- **Draw to scale where scale is the point.** If one bar means 4 cycles and another 32, their
  lengths are 4:32.
- **Accessible.** `role="img"` on the `<svg>`, with `<title>` and `<desc>` inside it, referenced by
  `aria-labelledby`. The `<desc>` is the alt text: the main relationship in one or two sentences.
- **Caption.** The `<figcaption>` says what the figure shows and, where it matters, what it does
  not show. List the relationships the figure encodes ("left to right = time; gray = idle lane").

### SVG mechanics

- Set a `viewBox` and `width="100%"`; never a fixed pixel width. Wrap wide diagrams in the
  template's `.diagram-scroll` box so the page body never scrolls sideways.
- Color every shape and text through the template's CSS classes, which read the theme tokens. A
  literal hex color in the SVG breaks dark mode.
  - fills: `.f-paper`, `.f-sheet`, `.f-idle`, `.f-ink`, `.f-accent`, `.f-teal`, `.f-mustard`,
    `.f-none`
  - strokes: `.s-ink`, `.s-pencil`, `.s-accent`, `.s-teal`, `.s-mustard`; add `.thick` or
    `.dashed` to change weight or style
  - text: `.t-label` (body face), `.t-mono` (small monospaced annotation), `.t-accent`
  - arrowheads: reuse the template's `<marker id="arrow">`; copy it with a new id and an
    `.f-accent` path for a coral arrow.
- Give every drawn shape an explicit fill (`fill="none"` counts). Leave room in the `viewBox` for
  the outermost labels.
- Keep text at 13px or larger in SVG units at the default width, so it stays legible on a phone.

## 3. Interaction

### What makes it meaningful

An interaction earns its place only if using it teaches something reading cannot. It must:

1. **Ask for a prediction first.** Before the reader touches the control, a short prompt asks what
   they expect. The answer sits in a `<details>` element, so it works without JavaScript.
2. **Change one real input.** One slider, one toggle, or one step button that maps to a real
   variable of the mechanism (threads that take the branch, prior probability, number of commits).
   Not a color picker. Not five sliders.
3. **Show the mechanism respond.** The diagram or a small visual next to the control redraws. Show
   the internal state, not only a final number.
4. **Compare two states.** Keep the starting state visible, or show "before" and "after" side by
   side, so the reader sees the difference instead of remembering it.
5. **Explain why the result changed.** One or two sentences, updated with the state, in the page's
   voice. "4 of 32 threads took the branch, so the warp spent 2 of 3 passes with most lanes idle."
6. **Reset.** A visible reset button returns the starting state. Pressing it twice changes nothing.

### One widget, plus questions

The page has one widget. Prediction questions in `<details>` are not widgets: one comes before the
widget (required), and one transfer question after it is encouraged. More than three questions
turns the page into a quiz.

### When there is no natural dial

Some concepts have no variable to slide (a definition, a historical idea, a proof). Use one of these
instead, in this order of preference:

- **Step-through.** "Next step" / "Previous step" buttons walk the mechanism one state at a time,
  highlighting the active part of the diagram. Good for algorithms and protocols (git rebase, a
  cache lookup, TCP handshake).
- **Predict-then-reveal questions.** Two or three questions in `<details>` that test transfer to a
  case the page did not show. Each answer explains why. This needs no JavaScript at all.
- **Sort or match.** The reader assigns a few cases to categories, then checks.

Never ship an interaction that teaches nothing. If none fits, use predict-then-reveal questions.

### Correctness and robustness

- Compute every displayed number from the real rule (Bayes' formula, the real cycle count of the
  model). If the model simplifies reality, the "Assumptions and limits" box says how.
- Test the minimum, typical and maximum inputs. Watch for division by zero, empty states and
  negative values at the extremes.
- Use real `<button>` and `<input>` elements with `<label>`s and stable `id`s, so they work with the
  keyboard and screen readers. Visible focus comes from the template.
- Announce changes politely: the "why" text sits in an `aria-live="polite"` region.
- No `alert()`, `confirm()` or `prompt()` — the artifact viewer suppresses them.
- No `localStorage` needed. If you use it for convenience, wrap it in try/catch.
- Animation is optional and short. Under `prefers-reduced-motion: reduce`, state changes are
  instant; the template handles transitions, so add none outside it.

### Without JavaScript

The page must still teach with scripts off:

- Prediction answers live in `<details>`.
- Put the static "before" and "after" states in the HTML (a two-column comparison, or a figure of
  each state). The script enhances them; it does not create them from nothing.
- The control itself may do nothing without JavaScript. Nothing the reader needs to read may
  exist only after a script runs.

## 4. The four-way review

After the page is built, review it four ways. Each one alone must teach the same correct model:

1. **Text only.** Read the prose and skip the figure and the widget. Is the mechanism complete?
2. **Diagram only.** Look at the figure and its caption. Is the main relationship clear?
3. **Interaction only.** Use the widget at minimum, typical and maximum values, then reset twice.
   Does each state's explanation match the prose?
4. **Without JavaScript.** Do the predictions have answers? Is the comparison visible?

Write down every disagreement between parts and fix it. Common ones: the diagram labels a part with
a different term than the prose; the widget's numbers do not match the worked example; the recap
mentions something the page never explained.
