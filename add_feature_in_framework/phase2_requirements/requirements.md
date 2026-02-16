# Phase 2: Understand the Requirements

## Goal

Fully understand what the user wants to build, why they want it, and which layers of the framework are affected. Never start implementing without answering "what" and "why."

## Why This Phase Exists

The most expensive bug is building the wrong thing. A new feature might look like "add instruction X" but the real goal might be "improve performance of workload Y by 2x." Understanding the motivation determines the design decisions. If you only know the "what" without the "why," you will make wrong trade-offs.

## Step-by-Step Process

### 1. Ask the User for the Specification

The user may provide the feature spec in different forms. Ask explicitly:

> "Will you provide the specification for this feature via prompt, documentation, or a reference paper? And what is the primary motivation — new functionality, performance improvement, or both?"

Possible spec sources:
- **Direct prompt:** User describes the feature in conversation
- **Documentation:** PDF, paper, internal spec document
- **Reference implementation:** Code in another project or language
- **Research paper:** Academic paper describing the technique

### 2. Read and Understand the Specification

For each spec source, extract these core elements:

| Element | Question to Answer |
|---------|-------------------|
| **What** | What is the new feature? What does it do? |
| **Why** | Why is this needed? Functionality? Performance? Both? |
| **Where** | Which layers need changes? (hardware, software, test, build) |
| **Interface** | What is the user-visible API or interface? |
| **Data flow** | How does data move through the new feature? |
| **Constraints** | Are there correctness constraints, timing requirements, compatibility needs? |
| **Scope** | What is in scope? What is explicitly out of scope? |

### 3. Understand the Motivation

This is the most important part. The motivation determines everything else:

**Functionality-only features:**
- New capability that didn't exist before
- Focus on correctness — does it produce the right answer?
- Performance is secondary; it just needs to work
- Example: Adding a new data type support

**Performance-improvement features:**
- Existing capability works, but needs to be faster/smaller/more efficient
- Must define the baseline to compare against
- Must define the target metric (cycles, throughput, bandwidth, area)
- Must define the target workload (what program benefits?)
- Example: Adding hardware sparsity support to skip zero computations

**Both functionality and performance:**
- New capability that is also expected to improve performance
- Requires both correctness verification AND performance measurement
- Example: Adding a new instruction that compresses data AND reduces memory bandwidth

### 4. Identify Affected Layers

Map the feature to the framework's layers (identified in Phase 1):

```
Feature: [name]
├── Hardware/RTL: [what changes? new module? modified datapath?]
├── Simulator: [what changes? new execution path? new timing model?]
├── Compiler/Toolchain: [new instruction encoding? new intrinsic?]
├── Kernel API: [new function? modified function signature?]
├── Host Driver: [new memory allocation? new kernel argument?]
├── Build System: [new compile flags? new config options?]
├── Tests: [new test? modified existing test?]
└── Configuration: [new parameters? new modes?]
```

### 5. Identify What You Can and Cannot Test

Be explicit about testability:

- **Can build and test immediately:** Which layers have a working build and test flow?
- **Need new tests:** Which layers lack tests for the new feature?
- **Cannot test in isolation:** Which layers can only be tested end-to-end?
- **External dependencies:** Are there tools, libraries, or hardware you don't have access to?

### 6. Write the Requirements Document

Create a persistent document:

```markdown
# Feature Requirements: [Feature Name]

## What
[1-2 sentence description]

## Why
[Motivation: functionality / performance / both]
[If performance: baseline metric, target metric, target workload]

## Specification Source
[Prompt / document / paper — with reference]

## Affected Layers
[List each affected layer and what changes]

## Interface
[User-visible API, instruction encoding, command-line flags, etc.]

## Data Flow
[How data moves through the new feature, input → processing → output]

## Constraints
[Correctness requirements, compatibility, backward compatibility]

## Out of Scope
[What this feature does NOT include]

## Open Questions
[Anything unclear — to be resolved with the user]
```

### 7. Resolve Open Questions with the User

If anything is unclear, ask the user before proceeding. Do not guess. Present your understanding and let the user correct it:

> "Here's my understanding of the feature. Please confirm or correct:
> - [bullet point summary]
> - Open question: [specific question]"

## Checklist Before Moving to Phase 3

- [ ] Do you know what the feature does?
- [ ] Do you know why the feature is needed (functionality / performance / both)?
- [ ] Have you identified all affected layers?
- [ ] Have you written and saved the requirements document?
- [ ] Are all open questions resolved with the user?
