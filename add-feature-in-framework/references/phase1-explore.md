# Phase 1: Explore the Framework

## Goal

Build a working mental model of the entire framework before making any changes. You must be able to build it, run it, and trace an existing feature through all layers.

## Why This Phase Exists

Frameworks are multi-layer systems. A feature that looks like "just add a hardware module" actually requires changes in the instruction decoder, the micro-op sequencer, the execution unit, the kernel API, the host driver, the test harness, and the build system. If you skip exploration, you will miss layers and produce a broken implementation.

## Step-by-Step Process

### 1. Identify the Framework's Layers

Every framework has some subset of these layers. Identify which ones exist:

| Layer | Examples |
|-------|----------|
| **Hardware RTL** | Verilog/SystemVerilog modules, VHDL entities |
| **Cycle-level Simulator** | C++ simulator modeling pipeline stages (gpgpu-sim, gem5) |
| **Functional Simulator** | Software model for correctness (not cycle-accurate) |
| **Compiler / Toolchain** | Instruction encoding, intrinsics, code generation |
| **Kernel / Runtime API** | Device-side library functions (e.g., CUDA, OpenCL, custom) |
| **Host Driver** | Host-side code that launches kernels and manages memory |
| **Build System** | Makefiles, CMake, configure scripts, dependency management |
| **Test Suite** | Regression tests, unit tests, integration tests |
| **Configuration System** | Compile-time macros, config files, TOML/YAML parameters |

### 2. Learn How to Build

Find the build instructions. Try building from scratch:

- Read README, INSTALL, CLAUDE.md, Makefile, configure scripts
- Execute the build commands — does it succeed?
- Note any environment setup required (toolchains, env vars, paths)
- Note the clean-build process (what must be cleaned when switching configs)
- Document any gotchas (submodule drift, stale caches, order-dependent builds)

**Build system traps to watch for:**

- **Automated scripts that override manual builds.** Many frameworks have convenience scripts (test runners, CI scripts) that rebuild layers with their own configuration flags. If you manually built the hardware with flag X=8, but the test runner rebuilds it with its default X=4, your manual build is silently overwritten. Document which scripts trigger rebuilds and what flags they use.
- **Hidden config dependencies.** A config flag may have a default value that happens to work for the most common configuration. You won't discover the dependency until you test a different config and get wrong results. During exploration, search for `ifdef`, `ifndef`, `define`, and default parameter values in the code you'll be modifying.
- **Submodule and dependency drift.** Git submodules can drift from their expected commit if other work touches them. When builds produce unexpected errors, check if submodules are at the expected commit before debugging your own code.
- **Clean build scope.** `make clean` may not clean everything. Different layers may have separate clean targets (e.g., `make -C runtime clean` vs `make -C simulator clean`). Know which clean command affects which layer, and always clean ALL affected layers when switching configs.

### 3. Find and Run Existing Tests

Do NOT skip this. You must confirm the framework is functional before changing it.

- Look in `tests/`, `regression/`, `examples/`, `benchmarks/` directories
- Find the simplest test that exercises the area you'll be modifying
- Run it. Does it pass? If not, fix the environment before proceeding
- Note the test command format and any required arguments

### 4. Trace an Existing Feature End-to-End

Pick one feature similar to what you'll be adding. Trace it through every layer:

- **Top-down:** Start from the test program → host driver → kernel API → hardware/simulator
- **Bottom-up:** Start from the hardware module → how is it connected? → what instruction triggers it? → how does the kernel call it?

For each layer, note:
- Which files implement this feature?
- What is the interface between this layer and the next?
- What compile-time flags or configs control this feature?

### 5. Map Config Flag Propagation

For the area you'll be modifying, map how compile-time config flags propagate across layers. This is critical for multi-config features (e.g., features that must work across data types, thread counts, or modes):

```
Flag: [FLAG_NAME]
├── Where defined:  [config file, Makefile, command line]
├── RTL layer:      [flag name used] or [not needed]
├── Simulator:      [flag name used] or [not needed]
├── Runtime:        [flag name used] or [not needed]
├── Test program:   [flag name used] or [not needed]
└── Test runner:    [flag name used] or [not needed, but beware overrides]
```

**Watch for name changes across layers.** The same concept may have different flag names in different layers (e.g., `-DITYPE_BITS=8` in hardware vs `-DITYPE=int8` in software). The mapping between them can be implicit and easy to get wrong.

**Watch for defaults.** If a layer doesn't receive a flag, it may use a default value. That default may work for the config you're testing, masking the fact that it's missing. Test with at least two different configs to catch missing flag propagation.

### 6. Write the Framework Understanding Document

Create a persistent document (e.g., `docs/framework_understanding.md` or in your memory files) containing:

```markdown
# Framework Understanding: [Framework Name]

## Layers
- [List each layer and its directory]

## Build Process
- [Step-by-step build commands]
- [Environment setup required]
- [Clean-build procedure]

## Key Files for [Feature Area]
- [File path]: [What it does]
- [File path]: [What it does]

## Existing Feature Trace: [Feature Name]
- Test: [test path and command]
- Host: [host file and key functions]
- Kernel: [kernel file and key functions]
- Hardware/Simulator: [module files and interfaces]
- Config: [relevant compile-time flags]

## Build Gotchas
- [List any discovered gotchas]

## Config Flag Propagation Map
- [Flag name]: [which layers receive it, which use defaults, any name changes]
```

For a concrete example of Phase 1 discoveries (build traps, hidden config dependencies, clean build scope), see `../examples/vortex_sparse_tcu.md` — Phase 1 section.

## Checklist Before Moving to Phase 2

- [ ] Can you build the framework from scratch?
- [ ] Have you run at least one existing test successfully?
- [ ] Can you trace an existing feature through all layers?
- [ ] Have you mapped config flag propagation across all layers?
- [ ] Have you identified which scripts trigger automatic rebuilds?
- [ ] Is the framework understanding document written and saved?
