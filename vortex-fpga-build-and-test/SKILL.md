---
name: vortex-fpga-build-and-test
description: >
  Build modified Vortex GPGPU RTL into an FPGA bitstream on the Alveo U55C and run test applications to verify correctness and measure working frequency.
  Use this skill whenever the user wants to synthesize Vortex for FPGA, build a bitstream, check timing or utilization, run apps on the FPGA,
  or verify that their RTL changes work on real hardware. Also use it when the user mentions FPGA build, xclbin, bitstream, working frequency,
  timing violations, WNS, DUT synthesis, or anything related to putting Vortex on the U55C board.
  This skill covers the full flow: configure, environment setup, optional quick DUT synthesis, full bitstream build, timing/utilization analysis, and running test apps.
---

# Vortex FPGA Build & Test Workflow

This skill guides you through building modified Vortex RTL into an FPGA bitstream on the Alveo U55C and running test applications to verify the design works and measure how the working frequency changes.

## Server Environment (Fixed)

These paths are fixed on this server and do not change:

| Resource | Path |
|----------|------|
| XRT 2.18.179 | `/opt/xilinx/xrt/` |
| Vivado 2024.1 | `/tools/Xilinx/Vivado/2024.1/` |
| Vitis 2024.1 | `/tools/Xilinx/Vitis/2024.1/` |
| Platform | `xilinx_u55c_gen3x16_xdma_3_202210_1` |
| Vortex toolchain | `/opt/` (verilator, sv2v, yosys, riscv64-gnu-toolchain, llvm-vortex) |
| FPGA board | Alveo U55C at PCIe `0000:3d:00.1` |
| Target clock | 300 MHz (3.333 ns period) |

## Workflow Overview

```
1. Gather info from user
2. Check prerequisites (config.mk, tools)
3. Source environment
4. Quick DUT synthesis (sanity check, ~10-15 min)
5. Full FPGA bitstream build (~2 hours for 1-core)
6. Analyze timing & utilization
7. Build kernel library (if not already built)
8. Run test application on FPGA
9. Report results
```

---

## Step 1: Gather Information from User

Before doing anything, ask the user for these three things. Use defaults if they don't specify:

1. **Vortex repo path** (required, no default) — the root directory of the Vortex repository to build.
   Ask: "What is the path to your Vortex repository?"

2. **CONFIGS** (optional, default: none) — extra RTL defines to pass to the build.
   Ask: "Do you have any CONFIGS to pass? (e.g., `CONFIGS=\"-DVM_ENABLE\"`) If not, I'll build with the default configuration."
   If user says no or doesn't specify, use no CONFIGS (basic build).

3. **Test application** (optional, default: `demo`) — which app to run after the bitstream is ready.
   Ask: "Which test application should I run on the FPGA? (e.g., demo, vecadd, sgemm) If you don't have a preference, I'll use `demo`."
   If user says no or doesn't specify, use `demo`.

Also ask the user what PREFIX name they want for the build directory. Suggest a descriptive name based on their CONFIGS (e.g., `build_vm_1c` for VM_ENABLE, `build_clean_1c` for no configs). Default to `build_1c`.

Store these as variables for the rest of the workflow:
- `VORTEX_DIR` — absolute path to Vortex repo root
- `USER_CONFIGS` — the CONFIGS string, or empty
- `TEST_APP` — the test application name
- `BUILD_PREFIX` — the PREFIX for the build directory

---

## Step 2: Check Prerequisites

Before building, verify these prerequisites. If any fail, fix them before proceeding.

### 2a. Check config.mk exists

```bash
ls $VORTEX_DIR/config.mk
```

If it does NOT exist, run configure:
```bash
cd $VORTEX_DIR && ./configure --xlen=64 --tooldir=/opt
```

Then verify:
```bash
grep TOOLDIR $VORTEX_DIR/config.mk
# Should show: TOOLDIR ?= /opt
```

### 2b. Verify XLEN in config.mk

```bash
grep "^XLEN" $VORTEX_DIR/config.mk
```

Confirm it matches expectations (64 for SV39 VM work, 32 for SV32).

### 2c. Check FPGA device is accessible

```bash
source /opt/xilinx/xrt/setup.sh 2>/dev/null && xbutil examine 2>&1 | head -20
```

The U55C should appear in the device list. If not, the FPGA may need a reset (`xbutil reset`).

---

## Step 3: Source Environment

Every shell session needs these environment variables set. Source them all and verify:

```bash
source /opt/xilinx/xrt/setup.sh
source /tools/Xilinx/Vivado/2024.1/settings64.sh
source /tools/Xilinx/Vitis/2024.1/settings64.sh
source $VORTEX_DIR/ci/toolchain_env.sh
export PATH=/opt/riscv64-gnu-toolchain/bin:$PATH
export PATH=/opt/llvm-vortex/bin:$PATH
```

Verify critical tools:
```bash
which verilator   # /opt/verilator/bin/verilator
which vivado      # /tools/Xilinx/Vivado/2024.1/bin/vivado
which v++         # /tools/Xilinx/Vitis/2024.1/bin/v++
```

If any tool is missing, stop and report the issue.

---

## Step 4: Quick DUT Synthesis (Sanity Check)

Before committing to the 2-hour full build, run a quick standalone synthesis of VX_afu_wrap (the full top-level design including AFU wrapper) to catch RTL errors across the entire design and get early timing/utilization estimates. This takes about 45-90 minutes but catches bugs that a core-only synthesis would miss (e.g., AFU wrapper issues, memory interface mismatches).

```bash
cd $VORTEX_DIR/hw/syn/xilinx/dut
```

If there are CONFIGS, include them:
```bash
CONFIGS="$USER_CONFIGS" make top 2>&1 | tee dut_top.log
```

If no CONFIGS:
```bash
make top 2>&1 | tee dut_top.log
```

Note: The build runs in the background (the DUT Makefile appends `&`). Monitor progress with:
```bash
tail -f top/build/build.log
```

### Alternative DUT targets (for faster iteration)

If the user wants a quicker sanity check, these narrower targets are available:
- `make core` — VX_core_top only (~20 min) — catches core RTL errors but misses AFU/memory interface issues
- `make vortex` — Vortex without AFU wrapper (~30-45 min) — catches core + memory/cache issues
- `make top` — VX_afu_wrap full design (~45-90 min) — **recommended**, catches all RTL issues before full FPGA build

### Interpret DUT results

After DUT synthesis completes, check:

1. **Did it succeed?** Look for errors in the log. Synthesis errors here mean the RTL has issues — fix them before proceeding to the full build.

2. **Timing estimate:** Check the DUT timing report for VX_afu_wrap. This gives an early signal of whether the design will meet timing at 300 MHz.

3. **Utilization estimate:** Note the LUT/FF/BRAM usage. The baseline clean Vortex 1-core uses about 12% of U55C LUTs (159K / 1.3M).

Tell the user the DUT results and ask if they want to proceed with the full build. If there are synthesis errors, help fix them first.

---

## Step 5: Full FPGA Bitstream Build

This is the main build. It takes approximately 2 hours for a 1-core design on this server.

Navigate to the XRT build directory:
```bash
cd $VORTEX_DIR/hw/syn/xilinx/xrt
```

Build command (with or without CONFIGS):

If CONFIGS are specified:
```bash
PREFIX=$BUILD_PREFIX NUM_CORES=1 TARGET=hw \
  PLATFORM=xilinx_u55c_gen3x16_xdma_3_202210_1 \
  CONFIGS="$USER_CONFIGS" \
  make > ${BUILD_PREFIX}.log 2>&1 &
```

If no CONFIGS:
```bash
PREFIX=$BUILD_PREFIX NUM_CORES=1 TARGET=hw \
  PLATFORM=xilinx_u55c_gen3x16_xdma_3_202210_1 \
  make > ${BUILD_PREFIX}.log 2>&1 &
```

Run this in the background. The build directory will be:
```
${BUILD_PREFIX}_xilinx_u55c_gen3x16_xdma_3_202210_1_hw/
```

Tell the user:
- The build is running in the background
- They can monitor with: `tail -f ${BUILD_PREFIX}.log`
- Expected time: ~2 hours for 1-core
- The build proceeds through three phases: gen-sources (RTL preprocessing, ~1 min), gen-xo (Vivado kernel packaging, ~2 min), gen-bin (v++ linking/synthesis/implementation, ~2 hours)

### Build progress indicators

Monitor these milestones in the log:
- `gen_sources.sh` — RTL preprocessing with verilator
- `gen_xo.tcl` — Vivado creating IP cores (FPU etc.)
- `system_link` — v++ linking kernel with platform
- `Block-level synthesis in progress, X of 135 jobs` — synthesis phase
- `Route design` — routing phase (near the end)
- `Successfully wrote ... vortex_afu.xclbin` — build complete!

### If the build fails

Common failures:
- **RTL syntax errors**: Fix the RTL and rebuild (may need to delete the build directory first)
- **Out of memory**: Reduce `MAX_JOBS` (add `MAX_JOBS=4` to the make command)
- **Build directory exists**: Use a different PREFIX or delete the old build directory

---

## Step 6: Analyze Timing & Utilization

After the build completes successfully, analyze the results. This is the key step for understanding how the RTL modifications affect working frequency.

Set the build directory path:
```bash
BUILD_DIR=$VORTEX_DIR/hw/syn/xilinx/xrt/${BUILD_PREFIX}_xilinx_u55c_gen3x16_xdma_3_202210_1_hw
```

### 6a. Timing Check (Working Frequency)

```bash
grep "VIOLATED" $BUILD_DIR/bin/impl_1_hw_bb_locked_timing_summary_routed.rpt
```

- **No output** = timing met (all paths have positive slack)
- **VIOLATED lines** = timing failed on some paths

Extract WNS (Worst Negative Slack):
```bash
grep -A3 "WNS(ns)" $BUILD_DIR/bin/impl_1_hw_bb_locked_timing_summary_routed.rpt | head -8
```

Interpret for the user:
- **WNS >= 0**: Timing met. The design runs at 300 MHz. Report the actual WNS value.
  - Example: WNS = +0.003 ns means timing passes with 0.003 ns margin
- **WNS < 0**: Timing violated. The design may not work reliably.
  - Estimated max frequency: Fmax = 1000 / (3.333 - WNS) MHz
  - Example: WNS = -0.5 ns means Fmax = 1000 / 3.833 = ~261 MHz

### 6b. Utilization Check

```bash
grep -A15 "CLB Logic" $BUILD_DIR/bin/impl_1_hw_bb_locked_utilization_placed.rpt | head -20
```

Report the key metrics:
- **CLB LUTs**: Used / Available (% utilization)
- **CLB Registers (FFs)**: Used / Available
- **Block RAM**: Used / Available
- **DSPs**: Used / Available

Reference baseline (clean Vortex 1-core on U55C): ~159K LUTs (12.25%), which leaves substantial headroom for additions.

### 6c. Hierarchical Utilization (optional, but useful)

```bash
head -50 $BUILD_DIR/bin/hier_utilization.rpt
```

This shows which modules consume the most resources — useful for understanding where added RTL is costing resources.

### 6d. Report to User

Summarize the results clearly:
```
Timing:  WNS = +X.XXX ns (PASSED / VIOLATED)
         Target: 300 MHz (3.333 ns period)
         Estimated Fmax: XXX MHz

Utilization:
         LUTs: XXX,XXX / 1,303,680 (XX.X%)
         FFs:  XXX,XXX / 2,607,360 (XX.X%)
         BRAM: XXX / 2,016 (XX.X%)
         DSPs: XXX / 9,024 (XX.X%)

Build time: Xh Ym
```

---

## Step 7: Build Kernel Library

Before running test apps, the kernel library (`libvortex.a`) must be built. Check if it exists:

```bash
ls $VORTEX_DIR/kernel/libvortex.a 2>/dev/null
```

If it does NOT exist, build it:
```bash
cd $VORTEX_DIR && make -C kernel -s 2>&1
```

Verify it was created:
```bash
ls -la $VORTEX_DIR/kernel/libvortex.a
```

---

## Step 8: Run Test Application on FPGA

Set up the environment and run the test:

```bash
cd $VORTEX_DIR
export FPGA_BIN_DIR=$VORTEX_DIR/hw/syn/xilinx/xrt/${BUILD_PREFIX}_xilinx_u55c_gen3x16_xdma_3_202210_1_hw/bin
TARGET=hw ./ci/blackbox.sh --driver=xrt --app=$TEST_APP 2>&1
```

### Interpret results

- **PASSED!** — The application ran correctly on the FPGA. Report the performance stats (instructions, cycles, IPC) shown in the output.
- **Failed / Error** — Something went wrong. Common issues:
  - `No devices found`: FPGA not programmed or needs reset
  - `kernel/libvortex.a` missing: Go back to Step 7
  - Timeout: The design may be too slow or hung (timing violations can cause this)
  - Wrong results: The RTL modification may have a functional bug

---

## Step 9: Final Report

After everything completes, present a clear summary to the user:

```
=== FPGA Build & Test Results ===

Vortex Repo:  $VORTEX_DIR
CONFIGS:      $USER_CONFIGS (or "none / default")
Build Prefix: $BUILD_PREFIX
Build Time:   Xh Ym

Timing:       WNS = +X.XXX ns (PASSED)
              Working frequency: 300 MHz

Utilization:  LUTs: XX.X%  |  FFs: XX.X%  |  BRAM: XX.X%  |  DSPs: XX.X%

Test App:     $TEST_APP → PASSED
              Instructions: XXXXX, Cycles: XXXXX, IPC: X.XXX
```

If timing is violated, emphasize this and suggest next steps (simplify logic, add pipeline stages, reduce NUM_CORES).

---

## Troubleshooting Reference

| Problem | Solution |
|---------|----------|
| `config.mk: No such file or directory` | Run `./configure --xlen=64 --tooldir=/opt` from repo root |
| `no such file: kernel/libvortex.a` | Run `make -C kernel` from repo root |
| `xbutil: command not found` | `source /opt/xilinx/xrt/setup.sh` |
| `v++: command not found` | `source /tools/Xilinx/Vitis/2024.1/settings64.sh` |
| Build out of memory | Add `MAX_JOBS=4` to the make command |
| Timing violation (WNS < 0) | Simplify design, add pipeline stages, or reduce NUM_CORES |
| `No devices found` | `xbutil examine` to check; may need `xbutil reset` |
| Build dir already exists | Use different PREFIX or delete old build dir |
| DUT synthesis errors | Fix RTL errors before attempting full build |
