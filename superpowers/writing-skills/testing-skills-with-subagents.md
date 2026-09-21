# Testing skills with Codex subagents

Use behavioral evaluations for workflows whose routing, context handling, or completion
criteria cannot be checked by static validation alone. Label evaluations as tests and run
in disposable projects. Do not use production services or expensive hardware implicitly.

1. Define a realistic task and observable acceptance criteria before running it.
2. Include relevant files, constraints, available tools, and prior user authorization.
3. When delegation is available and authorized, use a fresh subagent with a bounded task.
   Record its ID and collect its final result. Otherwise perform a clearly labeled local
   walkthrough; do not claim that an independent agent evaluation occurred.
4. Inspect the resulting artifacts and command evidence, not just the agent's confidence.
5. Fix demonstrated ambiguity and repeat affected cases. A baseline without the skill can
   help measure its value, but is not a prerequisite for correcting an existing skill.

Include a normal case and meaningful boundary cases: missing tools, a path with spaces,
existing user work, an explicitly requested review checkpoint, and prior authorization to
finish the task. Expected behavior must honor user instructions and host permission rules.
A skill should not force redundant approval, erase work to satisfy test ordering, or invent
unavailable tools. Avoid dramatic roleplay that rewards rigid compliance over useful results.

Report the prompt, fixtures, observed artifacts, actual checks, and remaining limitations.
Passing selected scenarios is evidence for those scenarios, not a guarantee for every task.
See `examples/AGENTS_MD_TESTING.md` for workspace evaluation cases.
