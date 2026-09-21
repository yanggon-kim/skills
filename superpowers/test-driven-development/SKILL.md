---
name: test-driven-development
description: Develop a behavior change or bug fix using a failing regression test, a minimal implementation, and verification; apply where an automated behavior test is meaningful.
---

# Test-driven development

Use a test that demonstrates the intended behavior before implementing a new behavior or fix
when practical. Preserve user code and existing work; test order is not a reason to delete it.

## Red, green, refactor

1. Write a focused test for the requirement or reproducible bug. Prefer real behavior over
   mocks; mock only dependencies that cannot reasonably run in the test.
2. Run it and confirm failure for the intended reason, not a syntax/setup error. If it already
   passes, determine whether the behavior already exists or the test misses the problem.
3. Make the smallest implementation that satisfies the requirement.
4. Run the test and appropriate regression checks. Investigate failures; do not weaken the
   expected behavior to make the test green.
5. Refactor only where it improves the changed code, keeping tests passing.

Example: retry logic should fail twice, succeed on the third call, and return the result.

```python
def test_retry_recovers_after_two_failures():
    attempts = []
    def operation():
        attempts.append(None)
        if len(attempts) < 3:
            raise RuntimeError("transient")
        return "ok"
    assert retry(operation, attempts=3) == "ok"
    assert len(attempts) == 3
```

A useful test checks the actual requirement and would catch its regression. Tests that only
repeat implementation details, assert newly written wording, or cover trivial reversible
formatting/config changes often add little value. Use direct inspection or an appropriate
configuration/artifact validator for those cases. No extra permission is needed merely to
choose a proportionate verification method within an authorized task.

If code already exists, add a regression test and demonstrate that it detects the bug using
an isolated reproduction or safe temporary change. Do not discard user edits or reset a
working tree to enforce this workflow. Report any limits to reproducing the failure.

Read `testing-anti-patterns.md` when designing mocks or test utilities. It covers testing mock
behavior, test-only production methods, and mocking without understanding dependencies.
