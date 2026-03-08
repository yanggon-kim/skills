# Hypothesis Sources by System Layer

When generating 10 hypotheses, think systematically across these layers. Not every layer applies to every bug, but scanning this list prevents blind spots.

## Software Layers

- **Input validation**: Is the input well-formed? Are edge cases (empty, max-size, boundary) handled?
- **Algorithm logic**: Is the algorithm correct for all input ranges? Off-by-one errors? Wrong loop bounds?
- **Data structures**: Are indices computed correctly? Buffer overflows? Wrong stride or offset?
- **Concurrency**: Race conditions? Lock ordering? Shared mutable state without synchronization?
- **Memory management**: Use-after-free? Double-free? Buffer overrun? Stack overflow at large inputs?
- **Compiler/toolchain**: Does the compiler optimize away something important? Different optimization levels?
- **Configuration**: Do compile-time and runtime parameters match? Environment variables? Feature flags?
- **Serialization**: Data format differences between platforms? Endianness? Alignment? Padding?

## Hardware / RTL Layers

- **Data path**: Is the right data reaching the right place? Signal bit-width mismatches? Truncation?
- **Control path**: State machine transitions correct? Enable signals timed right? Reset logic complete?
- **Memory subsystem**: Read/write addresses correct? Aliasing? Cache coherence? Write-enable logic?
- **Timing**: Setup/hold violations? Clock domain crossings? Pipeline hazard forwarding?
- **Initialization**: All registers and memories initialized? Stale values from previous operations?
- **Resource sharing**: When buffers/ports are reused, is cleanup complete? Leftover state?
- **Synthesis artifacts**: Does the synthesized netlist match behavioral RTL? BRAM vs LUTRAM inference?
- **Physical**: Temperature-dependent? Power supply noise? PCB signal integrity?

## Cross-Platform Layers

- **Simulation vs hardware**: Behavioral semantics vs physical implementation (e.g., memory read-during-write modes)
- **OS differences**: System call behavior? File system semantics? Thread scheduling?
- **Library versions**: Different implementations of the same API? Floating-point behavior?
- **Precision**: FP rounding mode differences? Integer overflow behavior? Signed vs unsigned?

## Generating Good Hypotheses

1. Start with the **differentiator** — the single parameter that separates passing from failing configs
2. List everything that parameter touches in the system
3. For each touchpoint, ask: "could this behave differently between the two platforms?"
4. Rank by likelihood and testability
5. Fill remaining slots with less likely but still possible explanations
