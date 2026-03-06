# DUT Top Synthesis Fixes

## Summary

Two fixes are needed for the DUT `top` target (`make top` in `hw/syn/xilinx/dut/`) to pass Vivado synthesis. These are only needed for the `top` target (VX_afu_wrap), not `core` (VX_core_top).

## Fix 1: VX_bar_unit.sv Interface Port

### Problem

`hw/rtl/core/VX_bar_unit.sv` has an interface port declared with the `output` keyword:
```systemverilog
output VX_gbar_bus_if.master gbar_bus_if
```

The XRT build flow uses `gen_sources.sh` with `-P` (verilator preprocessing) and a sed step that strips `.master` and `.slave` from interface modport qualifiers. After stripping, Vivado sees:
```systemverilog
output VX_gbar_bus_if gbar_bus_if
```

Vivado cannot parse `output` with an interface type (interfaces don't have direction in Vivado's parser).

### Fix

Remove the `output` keyword from the port declaration:
```systemverilog
// Before (broken after sed strips .master):
output VX_gbar_bus_if.master gbar_bus_if

// After (works in both Verilator and Vivado):
VX_gbar_bus_if.master gbar_bus_if
```

This is safe because:
- The `.master` modport already specifies direction
- Verilator accepts both forms
- After sed strips `.master`, Vivado sees `VX_gbar_bus_if gbar_bus_if` which is valid

### Error if not fixed

The preprocessed file (in the build's `src/` directory) will have a different line number than the original. The error looks like:
```
ERROR: [Synth 8-36] 'master' is not declared [.../VX_bar_unit.sv:NN]
```
or if `.master` was already stripped by sed:
```
ERROR: [Synth 8-36] 'VX_gbar_bus_if' is not declared [.../VX_bar_unit.sv:NN]
```

## Fix 2: gen_sources.sh Interface File Ordering

### Problem

Vivado requires SystemVerilog files to be compiled in dependency order. Interface definitions (`*_if.sv`) must come after package definitions (`*_pkg.sv`) but before modules that use them.

The default `gen_sources.sh` may not enforce this ordering for all directories, causing Vivado to fail with "not declared" errors when a module references an interface that hasn't been compiled yet.

### Fix

In the copy-folder function of `gen_sources.sh` (the `-C` codepath), ensure files are collected in dependency order. The `find` command that collects `.sv` files should list them as:
1. `*_pkg.sv` first (packages)
2. `*_if.sv` second (interfaces)
3. All other `*.sv` last (modules)

For example, when building the file list in the copy-folder path:
```bash
# Collect in order: packages, then interfaces, then modules
find "$dir" -name '*_pkg.sv' | sort
find "$dir" -name '*_if.sv' | sort
find "$dir" -name '*.sv' ! -name '*_pkg.sv' ! -name '*_if.sv' | sort
```

This ordering ensures Vivado's single-pass elaboration sees definitions before uses.

### When is this needed?

- Only for Vivado synthesis (DUT or full XRT build)
- Verilator handles dependency ordering automatically
- The `core` DUT target may work without this fix if all interfaces are defined in the same directory as their consumers
