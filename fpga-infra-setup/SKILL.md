---
name: fpga-infra-setup
description: End-to-end FPGA infrastructure for standalone RTL on Alveo U55C. Generates XRT-compatible wrapper, AXI4 control slave, Makefile, TCL packaging scripts, and host testbench around any RTL codebase, then builds and runs it on real FPGA hardware. Use when the user wants to get RTL running on FPGA, set up FPGA build infrastructure, create an XRT kernel from RTL, wrap RTL for Alveo, or build a hardware testbench. Also triggers on "FPGA infra", "XRT kernel from RTL", "build RTL on U55C", "package RTL for FPGA", or "run my Verilog on the board". Do NOT use for Vortex-specific FPGA builds (use vortex-fpga-build-and-test instead) or for RTL simulation-only workflows.
---

# FPGA Infrastructure Setup

Takes any RTL codebase and wraps it into a complete XRT kernel with build scripts and host testbench, targeting the Xilinx Alveo U55C at 300 MHz.

## Important: Gather Input First

If the user hasn't provided the RTL path, ask for it before doing anything else. You need:
- **RTL directory path** (required)
- **What the design computes** (helps generate a meaningful testbench)
- **Output directory** (default: sibling directory named after the design)

## Workflow

```
Analyze RTL → Generate Infrastructure → Build Host → Build XO → Build XCLBIN → Run Test
     ~5 min         ~10 min              ~5 sec     ~5 min     ~1-2 hours      ~10 sec
```

### Step 1: Analyze the RTL

Read all `.v`, `.sv`, `.vh`, `.svh` files in the user's directory to understand:
- Top-level module (the one not instantiated by others)
- I/O ports, parameters, data widths
- What computation the design performs
- Special requirements (clock domains, memory interfaces)

### Step 2: Generate Infrastructure

Create this directory structure — consult `references/templates.md` for proven file templates:

```
<output_dir>/
├── Makefile               # Orchestrates xo → xclbin → host targets
├── sources.txt            # RTL file list for Vivado (+incdir+, source files)
├── vitis.ini              # Vivado optimization settings
├── run.sh                 # One-shot build-and-test script (chmod +x)
├── rtl/
│   ├── <kernel_name>.v    # XRT top-level wrapper (must be .v, not .sv)
│   ├── <ctrl_name>.sv     # AXI4-Lite control register slave
│   └── <core_or_user>.sv  # Compute core (shim around user RTL, or user RTL directly)
├── scripts/
│   ├── gen_xo.tcl         # XO generation entry point (stable, no customization needed)
│   ├── package_kernel.tcl # IP packaging with register map (customize per design)
│   └── parse_vcs_list.tcl # sources.txt parser (stable, reusable utility)
└── host/
    └── host.cpp           # XRT host testbench using xrt::ip for register-level access
```

#### Critical design rules

These rules come from hard-won debugging — violating any of them causes subtle failures:

- **Top-level wrapper must be `.v` (Verilog)**. Vivado's IP packager silently mishandles SystemVerilog top modules. Use `.sv` freely for submodules.
- **`ap_done` must persist until next `ap_start`**. The host polls over PCIe with microsecond latency. A single-cycle pulse will be missed, causing a timeout.
- **AXI4-Lite read FSM needs 3 states** (ADDR → DATA → RESP). The DATA state registers the mux output. Skipping it causes timing failures at 300 MHz.
- **PATH must be appended after sourcing XRT**. XRT's `setup.sh` clobbers PATH — run `export PATH=$PATH:/usr/bin:/usr/local/bin:/bin` immediately after.

Consult `references/xrt-kernel-contract.md` for the full XRT port specification and register map layout.

#### Register map layout

Standard registers (0x00-0x0C) are fixed by XRT. Custom parameters start at 0x10:
```
0x00  AP_CTRL    [0]=ap_start(RW), [1]=ap_done(RO), [2]=ap_idle(RO), [3]=ap_ready(RO)
0x04  GIER       Global Interrupt Enable
0x08  IP_IER     IP Interrupt Enable
0x0C  IP_ISR     IP Interrupt Status (toggle-on-write)
0x10+ Custom     64-bit addresses (LO/HI pairs), 32-bit scalars
last  MEM_0      Memory bank association (ASSOCIATED_BUSIF = m_axi_mem_0)
```

The `package_kernel.tcl` register map must exactly match the RTL control slave — mismatches cause `check_integrity` to fail.

#### Host testbench pattern

Use `xrt::ip` (not `xrt::kernel`) because RTL kernels need direct register access:

```cpp
#include "experimental/xrt_device.h"
#include "experimental/xrt_bo.h"
#include "experimental/xrt_ip.h"

auto device = xrt::device(0);
auto uuid = device.load_xclbin(xclbin_path);
auto ip = xrt::ip(device, uuid, "<kernel_name>");

auto bo = xrt::bo(device, buf_size, 0);  // HBM bank 0
// ... initialize, sync to device, write registers, start, poll ap_done, verify
```

### Step 3: Build (sequential, with validation gates)

Source the environment first — every build command needs this:
```bash
source /opt/xilinx/xrt/setup.sh
export PATH=$PATH:/usr/bin:/usr/local/bin:/bin
source /tools/Xilinx/Vivado/2024.1/settings64.sh
source /tools/Xilinx/Vitis/2024.1/settings64.sh
```

**3a. Build host** (~seconds)
```bash
make host
```
Validates that XRT headers/libs are found. If this fails, check `XRT_INC` and `XRT_LIB` paths in the Makefile.

**3b. Build XO** (~5-10 min)
```bash
make xo
```
Packages RTL into `.xo` via Vivado batch mode. Verify the output contains:
```
check_integrity: Integrity check passed.
```
If integrity check fails, the register map in `package_kernel.tcl` doesn't match the RTL, or bus interfaces aren't associated with `ap_clk`.

**3c. Build XCLBIN** (~1-2 hours)

This is synthesis + place + route. It takes a long time, so run it in tmux to survive network disconnects:
```bash
tmux new -s fpga_build
source /opt/xilinx/xrt/setup.sh && export PATH=$PATH:/usr/bin:/usr/local/bin:/bin
source /tools/Xilinx/Vivado/2024.1/settings64.sh && source /tools/Xilinx/Vitis/2024.1/settings64.sh
make xclbin 2>&1 | tee xclbin_build.log
# Ctrl+B, D to detach; tmux attach -t fpga_build to reconnect
```

After completion, verify timing met:
```bash
grep -A7 "Design Timing Summary" build_hw/_x/reports/link/imp/impl_1_hw_bb_locked_timing_summary_routed.rpt
```
WNS (Worst Negative Slack) must be >= 0. Negative WNS means timing violations — the design may produce incorrect results on hardware.

### Step 4: Run FPGA Test

```bash
./host/<test_binary> build_hw/<kernel_name>.xclbin
```

Expected: output ends with `PASSED!` and exit code 0.

## Example: Vector Add

**User provides**: `rtl/` directory with a combinational adder module
**Skill generates**: XRT wrapper that reads A[i] and B[i] from HBM via AXI4, computes C[i]=A[i]+B[i] using 16 parallel 32-bit adders (512-bit bus), writes back
**Host testbench**: Initializes A[i]=i, B[i]=2*i, verifies C[i]=3*i for 1024 elements
**Result**: `PASSED! All 1024 elements correct.` in ~0.2 ms kernel time

A working reference implementation lives at `00_workspace/99_fpge_example/` in this repository.

## Troubleshooting

### Kernel times out (ap_done never asserts)
- **Cause**: `ap_done` is a single-cycle pulse, or FSM gets stuck
- **Fix**: Ensure `ap_done` stays high in the DONE/IDLE state until cleared by the next `ap_start`. Check that all FSM transitions have proper AXI handshake conditions (e.g., `arvalid && arready` before deasserting).

### XO integrity check fails
- **Cause**: Register map in `package_kernel.tcl` doesn't match RTL, or bus interfaces not associated with clock
- **Fix**: Verify `ipx::associate_bus_interfaces -busif s_axi_ctrl -clock ap_clk` and `ipx::associate_bus_interfaces -busif m_axi_mem_0 -clock ap_clk` are both present. Check that every register offset in TCL matches the RTL control slave.

### Host compilation fails with missing headers
- **Cause**: XRT include path wrong
- **Fix**: Verify `/opt/xilinx/xrt/include/experimental/xrt_device.h` exists. Check that `source /opt/xilinx/xrt/setup.sh` was run before `make host`.

### XCLBIN build fails with timing violation (WNS < 0)
- **Cause**: Design too complex for 300 MHz, or long combinational paths
- **Fix**: Add pipeline registers in critical paths. For simple designs this shouldn't happen — check for accidentally wide multipliers or deep logic chains.

### Data mismatches (FPGA test FAILED)
- **Cause**: AXI addressing error, wrong byte offset calculation, or data width mismatch
- **Fix**: Verify `BEAT_BYTES = AXI_DATA_WIDTH / 8` (64 for 512-bit bus). Check that address offsets increment by `BEAT_BYTES`, not by element count. Ensure `awsize/arsize = 3'b110` (log2 of 64 bytes).

## Prerequisites

Verify before starting — if any are missing, inform the user:
- **XRT**: `/opt/xilinx/xrt` (provides `xrt::device`, `xrt::bo`, `xrt::ip`)
- **Vivado 2024.1**: `/tools/Xilinx/Vivado/2024.1` (IP packaging into .xo)
- **Vitis 2024.1**: `/tools/Xilinx/Vitis/2024.1` (v++ linker for .xclbin)
- **Platform**: `xilinx_u55c_gen3x16_xdma_3_202210_1` (Alveo U55C shell)
