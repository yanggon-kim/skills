---
name: concept-explainer
description: Explains any concept, mechanism, algorithm or idea as one self-contained HTML learning page — plain-voice prose, one diagram of the mechanism, and one interaction where the reader predicts and then checks. When the concept is a process that changes over time, the page shows it as a timeline — a storyboard of frames on one fixed layout, plus an animated player built from them. Saved locally and published as a private claude.ai artifact. Use it whenever the user wants to understand something rather than get a fact — "explain X", "how does X work", "teach me X", "walk me through X step by step", "I don't get X", "X가 뭔지 설명해줘" — in any field (computer architecture, math, statistics, ML, systems, git, physics), even when they never ask for a page or HTML. Not for one-line lookups, debugging a specific bug, line-by-line walkthroughs of the user's code, slide decks, or documents others will edit.
---

# Concept explainer

Turn one concept into one HTML page that gives a smart non-expert a **correct mental model they can
test**. The page carries three representations of the same idea, each doing a job the others cannot:

| part | the reader's action | what it gives |
|---|---|---|
| prose | reads and reasons | definitions, causes, conclusions |
| one diagram | sees the structure | parts and how they connect |
| one interaction | predicts, changes an input, compares | proof that the model works |

When the concept changes over time — a procedure, a process, an algorithm's steps — the diagram
becomes a **timeline**: a **storyboard** (every step as a frame on the same fixed layout, side by
side) and a **player** (the same frames animated in place, with play, pause, step and scrub). The
storyboard lets the reader compare states; the player lets them follow the motion.

The design comes from Andrej Karpathy's "learning ladder" (writing → diagram → web page → video) and
a learning-studio prompt built on it. The video rung is replaced by the timeline: an HTML page can
show change over time, and unlike a video the reader can pause it, step it and read every frame,
and it can be checked and corrected in minutes. A page is
judged by one question: after reading it, can the reader predict what the mechanism does in a case
the page did not show? Decoration that does not serve that question is cut.

## Defaults

- **Reader:** a smart non-expert. They are intelligent and willing to work, but they do not know
  the field's vocabulary. Never talk down; never skip a step because "everyone knows it".
- **Language:** the language of the user's request. A Korean request gets a Korean page.
- **Voice:** clear controlled language in the spirit of ASD-STE100, applied loosely — see
  `references/voice.md`. Precision wins over simplicity: never make a true fact false to make it
  short.
- **Look:** the house style in `assets/template.html` (paper, ink and pencil: warm cream, charcoal,
  coral accents, restrained teal and mustard, monospaced labels, generous space). It is the user's
  chosen style; keep it unless the user asks for another.
- **Output:** one local `.html` file, then a private claude.ai artifact.

If the user names a different reader ("explain it to my 12-year-old", "I'm a GPU architect"),
adapt the depth and the examples, not the voice rules.

## Workflow

### 1. Scope to one concept

Write down, for yourself:

- **The central question** the page answers, phrased the way the reader would ask it.
- **A one-sentence objective:** "After this page, the reader can ___."
- **Out of scope:** what the page will not cover.

A broad request ("explain GPUs", "explain transformers") gets the one mechanism at its core, and the
page names in one line what it leaves out. Two thin explanations teach less than one good one. If
the request names two things to contrast ("rebase vs merge"), the contrast itself is the one
concept.

### 2. Get the facts right before writing

A polished page makes a wrong explanation look trustworthy, so accuracy comes first.

- List **five facts** the page depends on, **the terms the page will use** (every word a smart
  non-expert might not know, typically four to eight, including the concept's own name), **one
  common misconception**, and **one real-world example** (a real system, product, dataset or event
  — not a toy story). The real example usually belongs in "the problem" or "the result".
- For each fact, ask: do I know this firmly? For recent topics, niche details, exact numbers, or
  anything about the user's own code or paper, check it — search the web or read the file — before
  you print it.
- Anything still uncertain goes into the page's "Assumptions and limits" box, stated plainly. Never
  hide a simplification; name it ("This page ignores caches. Real hardware adds ...").

### 3. Write the prose

Read `references/voice.md` first. Follow the section order in `references/page-structure.md`:
question → what you already know (background and the words the page uses) → the problem → the
mechanism → try it → the result → a common misconception → recap → assumptions and limits.

The terms are not a glossary at the end. "What you already know" explains the background and then
defines, one plain line each, every word the rest of the page uses, so the reader meets each word
before it appears. Use exactly those words afterwards, one name per concept.

Show before you name: the list near the top gives each word a short definition, and the mechanism
section still shows each new term working, with its concrete example, before it relies on it.
The central idea must be findable in under 20 seconds — it sits in the one-sentence answer under
the title. If a stranger skimming the top of the page cannot find it, rewrite the top.

### 4. Draw the diagram

One primary diagram, inline SVG, placed beside the mechanism it explains. Rules and diagram types are
in `references/page-structure.md` § Diagram. The short version: one reading direction, at most seven
primary elements, every arrow has one defined meaning, labels make sense without the prose, and it
still reads in grayscale. Use inline SVG, not Mermaid or images, so the page works offline and the
diagram follows the light and dark themes.

**If the concept changes over time, draw a timeline instead.** Ask: is the answer to the reader's
question a sequence of states ("what happens when ...", "walk me through ...", a pipeline, a
protocol, an algorithm's steps, a git operation)? If yes, read `references/timeline.md` and build
the storyboard: 3–12 frames, one change per frame, the same layout and the same keyed elements in
every frame, one caption sentence each. You write only the storyboard; the template's script builds
the player from those frames, so the two views cannot disagree, and the storyboard alone still
teaches without JavaScript or motion. A static structure or a relationship between quantities keeps
the single diagram.

### 5. Build the interaction

One interactive widget that changes one real input and shows the mechanism respond. Prediction
questions are not extra widgets: one before the widget is required, and one transfer question after
it ("now try a case the page did not show") is encouraged. The reader **predicts
first**, then acts, then compares two states, then reads why the result changed. Details and the
fallback for concepts with no natural dial are in `references/page-structure.md` § Interaction. If
the interaction computes anything, compute it from the real rule, not from invented numbers, and say
on the page what the model simplifies.

For a pure procedure with no real input to change, the timeline's player is the interaction: ask
the reader to predict a later frame before pressing play, and ask a transfer question afterwards.
Build a separate widget only when the concept also has a real input to change.

### 6. Assemble the page

If the Artifact tool is available, load its `artifact-design` guidance now, before writing the
file — the tool asks for it before any page is written. Its page contract applies in full. Its
visual advice lists "warm cream, serif display, terracotta accent" among looks to avoid by default;
that advice is for pages where nobody chose a look. Here the user chose this house style, and that
guidance itself says the user's words win, so keep the house style.

Copy `assets/template.html` and fill its slots. Write every visible label in the page language,
including the "Explainer" eyebrow and the button text. The template already satisfies the artifact
page contract:

- no `<!doctype>`, `<html>`, `<head>` or `<body>` tags (the publisher adds them);
- a `<title>` first — a name of two to five words, never "X: an explainer";
- every color a token, with light and dark values;
- a 16px side gutter, nothing wider than the phone screen except inside its own scroll box;
- `prefers-reduced-motion` respected; keyboard focus visible;
- the page still teaches with JavaScript off (prediction answers live in `<details>`, and the
  interaction's two states also exist as static text).

No external scripts are needed. Google Fonts is the only external stylesheet allowed, and every
font has a fallback stack, so the local file still reads well offline.

### 7. Check

Run the mechanical check and fix every error it reports:

```bash
python3 <skill-dir>/scripts/check_page.py <page.html>
```

It checks the page contract, the structure (diagram, interaction, sections), and the voice (sentence
length, passive-voice suspects in English, filler words). It is a report, not a judge. Read its
warnings and decide.

If the interaction computes anything, run its model function once outside the page (for example
with `node`) at the minimum, typical and maximum inputs, and confirm the first render prints exactly
the static "other case" text written in the HTML.

To look at the page at phone width locally, load it in a 400px-wide `<iframe>`: headless Chrome
clamps `--window-size` to about 500px, so a 400px screenshot crops the page and looks like an
overflow that is not there.

Then review the page four ways. Each one alone must teach the same correct mental model:

1. **Text only** — read the prose and skip the figure and the widget.
2. **Diagram only** — read the figure and its caption.
3. **Interaction only** — use the widget at its minimum, typical and maximum values; press reset
   twice.
4. **Without JavaScript** — the predictions still have answers and the comparison still shows.

Fix every place where two parts disagree. A diagram that says one thing and a paragraph that says
another teaches confusion.

### 8. Save and publish

1. Save the page as `<concept-slug>.html` in the current working directory, unless the user named a
   place.
2. Publish it with the Artifact tool as a private artifact: `file_path` = the local file,
   `icon` = `"lesson"` (or another one-word generic noun that fits), and a one-sentence
   `description` saying what the reader will understand.
3. If no Artifact tool is available in this session, stop after saving and say that the page was
   not published.

### 9. Report

Reply with the artifact link, the local path, and one or two sentences on what the page covers and
what it leaves out. Do not paste the explanation into the chat — the page is the answer.

## Files in this skill

| file | read it when |
|---|---|
| `references/voice.md` | before writing any prose (step 3) |
| `references/page-structure.md` | when planning the sections, diagram and interaction (steps 3–5) |
| `references/timeline.md` | when the concept changes over time (step 4) |
| `assets/template.html` | when assembling the page (step 6) — copy it, do not edit it in place |
| `scripts/check_page.py` | after the page is written (step 7) |
