# FPGA Hang: Wrong BRAM Inference Pattern in VX_async_ram_patch.sv

## Summary

An FPGA execution hang (AP_DONE never asserts, test stuck at "wait for completion") was caused by `hw/rtl/libs/VX_async_ram_patch.sv` using a non-standard Write-First RAM pattern that Vivado cannot properly infer as Block RAM. The bug is invisible in RTL simulation (Verilator) and only manifests on real FPGA hardware.

## Symptoms

- FPGA bitstream builds successfully (no errors, timing MET)
- `demo` test hangs at "wait for completion" — never returns
- AP_DONE never asserts (VX_afu_wrap state machine stuck in STATE_RUN)
- RTLsim and SimX both PASS the same test — FPGA-only failure
- AXI-Lite control path works fine (dev_caps readable, AP_START written OK)

## Root Cause

The `SYNC_RAM_WF_BLOCK` macro in `VX_async_ram_patch.sv` determines how Write-First synchronous RAMs are synthesized. Vivado requires a very specific RTL pattern to infer Block RAM primitives.

### Broken pattern (our version)

Registers the read **data** and adds a hazard bypass mux:

```systemverilog
reg [DATAW-1:0] rdata_r;
reg [ADDRW-1:0] raddr_r;
always @(posedge clk) begin
    rdata_r <= ram[__ra_n];     // register DATA from RAM
    raddr_r <= __ra_n;
end
wire is_rdw_hazard = __we && (__wa == raddr_r);
assign __d = is_rdw_hazard ? wdata : rdata_r;  // bypass mux
```

### Correct pattern (upstream)

Registers only the **address**, reads combinationally from RAM array:

```systemverilog
`RAM_ATTRIBUTES `RW_RAM_CHECK reg [DATAW-1:0] ram [0:SIZE-1];
reg [ADDRW-1:0] raddr_r;
always @(posedge clk) begin
    raddr_r <= __ra;            // register ADDRESS only
end
assign __d = ram[raddr_r];     // combinational read from RAM
```

Key differences:
1. **Address vs data registration**: Xilinx BRAM inference requires `assign out = ram[registered_addr]`
2. **`RW_RAM_CHECK` attribute**: Tells Vivado how to handle read-during-write conflicts in BRAM
3. **No bypass mux**: The standard pattern relies on BRAM primitive's built-in write-first behavior

### Why it breaks only on FPGA

Verilator simulates behavioral RTL — both patterns produce identical functional results in simulation. On real hardware, when Vivado can't match the pattern to a BRAM primitive, it may:
- Use distributed RAM (LUT-based) with different timing characteristics
- Synthesize incorrect read-during-write behavior
- Produce a design that appears correct in post-synthesis simulation but fails at runtime

## How to Fix

Copy the upstream version of `VX_async_ram_patch.sv` from a known-working build:

```bash
# Backup first
cp hw/rtl/libs/VX_async_ram_patch.sv hw/rtl/libs/VX_async_ram_patch.sv.bak

# Copy upstream working version
cp /path/to/upstream/vortex/hw/rtl/libs/VX_async_ram_patch.sv hw/rtl/libs/VX_async_ram_patch.sv
```

Verify with RTLsim first (quick sanity check):
```bash
./ci/blackbox.sh --driver=rtlsim --app=demo
```

Then rebuild the FPGA bitstream.

## How to Detect This Class of Bug

1. **Compare with upstream**: `diff hw/rtl/libs/VX_async_ram_patch.sv /path/to/upstream/version`
2. **Check CRITICAL warnings**: Vivado synthesis log shows multi-driven net warnings on `rdata[N]` — these hint at BRAM inference issues
3. **Check Vivado BRAM inference**: In the synthesis log, search for "Inferred BRAM" or "distributed RAM" — if RAMs that should be BRAM are inferred as distributed, suspect this issue
4. **Symptom pattern**: Build succeeds + timing MET + RTLsim PASS + FPGA hangs = likely a synthesis-vs-simulation mismatch, often in RAM inference

## Prevention

- Never modify `VX_async_ram_patch.sv` RAM macros without checking against Xilinx UG901 (Vivado Synthesis Guide) RAM inference templates
- After any RAM-related RTL changes, verify BRAM inference in the Vivado synthesis report before committing to a full build
- The DUT quick synthesis (`make core` or `make top`) catches synthesis errors but NOT incorrect BRAM inference — you need to check the synthesis log manually

## Timeline

- **Build**: build_tcu_1c (first attempt) — timing MET, demo hangs
- **Build**: build_tcu_1c_v2 — same hang, confirmed not a one-off
- **Root cause found**: Compared VX_async_ram_patch.sv with upstream working build
- **Build**: build_tcu_1c_v3 (with fix) — demo PASSED, sgemm_tcu PASSED
